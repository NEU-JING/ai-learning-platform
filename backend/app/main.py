from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from contextlib import asynccontextmanager
import os
import asyncio

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.data.courses import init_courses_data
from app.data.courses_phase1 import init_phase1_data
from app.data.courses_phase2 import init_phase2_data
from app.api.v1 import auth, courses, labs, progress, certificates, discussions


def _format_size(size_bytes: int) -> str:
    """格式化字节大小为人类可读格式"""
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时确保数据库schema就绪
    # 开发环境: init_db() 创建缺失表 (Alembic未跑时的fallback)
    # 生产环境: 应使用 `alembic upgrade head` 管理迁移
    init_db()
    db = SessionLocal()
    try:
        init_courses_data(db)
        init_phase1_data(db)
        init_phase2_data(db)
    finally:
        db.close()
    print("✅ 数据库初始化完成")
    
    # 异步检查沙箱镜像（不阻塞启动）
    async def check_sandbox_image():
        """后台检查沙箱镜像，避免阻塞启动"""
        try:
            from app.services.code_executor import get_sandbox_image_info, ensure_sandbox_image
            
            print("🔍 正在检查 Docker 沙箱镜像...")
            image_info = get_sandbox_image_info()
            
            if not image_info['docker_available']:
                print("⚠️ Docker 不可用，代码执行将使用本地回退模式")
                print("   如需使用 Docker 沙箱，请确保 Docker 服务已启动")
                return
            
            if image_info['image_exists']:
                print(f"✅ 沙箱镜像已存在: {image_info['image_tag']}")
                print(f"   镜像版本: {image_info['image_details']['labels'].get('sandbox.version', 'unknown')}")
                print(f"   镜像大小: {_format_size(image_info['image_details'].get('size', 0))}")
            else:
                print(f"⏳ 沙箱镜像未找到，正在后台构建: {image_info['image_tag']}")
                # 异步构建镜像，不等待完成
                asyncio.create_task(_build_sandbox_image_async())
        except Exception as e:
            print(f"⚠️ 沙箱镜像检查失败: {e}")
            print("   代码执行将使用本地回退模式")
    
    async def _build_sandbox_image_async():
        """后台异步构建沙箱镜像"""
        try:
            from app.services.code_executor import ensure_sandbox_image
            
            success = await ensure_sandbox_image()
            if success:
                print("✅ 沙箱镜像后台构建完成")
            else:
                print("⚠️ 沙箱镜像构建失败，代码执行将使用本地回退模式")
        except Exception as e:
            print(f"❌ 沙箱镜像后台构建异常: {e}")
    
    # 启动后台检查任务
    asyncio.create_task(check_sandbox_image())
    
    yield
    # 关闭时的清理
    print("👋 应用关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI学习平台 - 从入门到AI团队Leader",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS配置 - 从配置文件中读取
# 开发环境: 允许localhost:3000
# 生产环境: 通过环境变量CORS_ORIGINS配置，例如: "https://example.com,https://app.example.com"
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
    max_age=600,  # 预检请求缓存10分钟
)

# 静态文件服务配置
# 生产环境: 前端文件挂载到容器中，由后端同时提供API和静态文件服务
STATIC_DIR = os.getenv("STATIC_DIR", "../frontend")
# Force absolute path to avoid cwd issues
STATIC_DIR = os.path.abspath(STATIC_DIR)
SERVE_STATIC = True  # Always serve static files in this deployment

if SERVE_STATIC and os.path.exists(STATIC_DIR):
    # 挂载静态文件目录
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    print(f"✅ 静态文件服务已启用: {STATIC_DIR}")


# 注册API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["课程"])
app.include_router(labs.router, prefix="/api/v1/labs", tags=["实验"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["学习进度"])
app.include_router(certificates.router, prefix="/api/v1/certificates", tags=["证书"])
app.include_router(discussions.router, prefix="/api/v1", tags=["讨论区"])


@app.get("/", response_class=HTMLResponse)
def root():
    """首页 - 返回SPA应用"""
    spa_file = os.path.join(STATIC_DIR, "spa.html")
    if os.path.exists(spa_file):
        return FileResponse(spa_file)
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse(content="<h1>AI Learning Platform</h1><p>Frontend not found</p>")


@app.get("/health")
def health_check():
    """健康检查端点 - 用于负载均衡器和监控"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": os.getenv("ENVIRONMENT", "development")
    }


# SPA路由回退处理
# 捕获所有非API路径，返回spa.html用于前端路由处理
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_fallback(request: Request, full_path: str):
    """
    SPA路由回退处理
    
    所有未匹配的静态路径都将返回spa.html，由前端路由处理。
    排除的路径:
    - /api/* - API路由
    - /docs, /redoc, /openapi.json - API文档
    - /static/* - 静态文件
    """
    # --- Static file serving (js/css/images/src/etc.) ---
    # Before falling back to SPA/HTML, check if the path maps to a real file
    # under STATIC_DIR. This handles relative paths like js/api.js, css/style.css,
    # src/main.js that HTML pages reference without the /static/ prefix.
    static_extensions = (
        ".js", ".mjs", ".css", ".map", ".png", ".jpg", ".jpeg", ".gif",
        ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".json", ".webp",
    )
    if full_path and any(full_path.endswith(ext) for ext in static_extensions):
        file_path = os.path.normpath(os.path.join(STATIC_DIR, full_path))
        # Security: ensure we don't escape STATIC_DIR
        if file_path.startswith(os.path.abspath(STATIC_DIR)) and os.path.isfile(file_path):
            response = FileResponse(file_path)
            # Prevent aggressive caching of JS/CSS during development
            if any(full_path.endswith(ext) for ext in (".js", ".mjs", ".css", ".map")):
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            return response
        # File not found under STATIC_DIR — don't fall through to HTML fallback
        return HTMLResponse(content="Not Found", status_code=404)

    # --- Direct file match (html, ico, etc.) ---
    # If the path directly corresponds to a file under STATIC_DIR, serve it.
    # This ensures /login.html returns the actual login.html, not a SPA fallback.
    if full_path:
        direct_file = os.path.normpath(os.path.join(STATIC_DIR, full_path))
        if direct_file.startswith(os.path.abspath(STATIC_DIR)) and os.path.isfile(direct_file):
            return FileResponse(direct_file)

    # 排除API和文档路径
    excluded_paths = [
        "/api/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/static/",
        "/health"
    ]
    
    # 检查是否是排除路径
    for excluded in excluded_paths:
        if full_path.startswith(excluded.lstrip("/")) or full_path == excluded.lstrip("/"):
            return HTMLResponse(content="Not Found", status_code=404)
    
    # 尝试返回具体的HTML文件 (bare paths like /login → login.html)
    page_mapping = {
        "": "index.html",
        "index": "index.html",
        "login": "login.html",
        "register": "register.html",
        "course": "course.html",
        "chapter": "chapter.html",
        "lab": "lab.html",
        "courses": "index.html",
        "dashboard": "index.html",
        "profile": "index.html",
        "certificates": "index.html",
    }
    
    # 获取请求路径的第一部分
    path_first = full_path.split("/")[0] if full_path else ""
    
    # 如果存在具体页面，返回对应页面
    if path_first in page_mapping:
        page_file = os.path.join(STATIC_DIR, page_mapping[path_first])
        if os.path.exists(page_file):
            return FileResponse(page_file)
    
    # SPA路由回退 (only for unknown paths without file extension)
    spa_file = os.path.join(STATIC_DIR, "spa.html")
    if os.path.exists(spa_file):
        return FileResponse(spa_file)
    
    # 如果连spa.html都没有，返回index.html
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    
    # 最后的回退
    return HTMLResponse(
        content="""<!DOCTYPE html>
<html>
<head><title>AI Learning Platform</title></head>
<body>
    <h1>AI Learning Platform</h1>
    <p>Frontend files not found. Please build the frontend or check STATIC_DIR configuration.</p>
    <p>API Documentation: <a href="/docs">/docs</a></p>
</body>
</html>""",
        status_code=200
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
