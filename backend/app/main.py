import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import (
    analytics,
    auth,
    certificates,
    courses,
    discussions,
    labs,
    profile,
    progress,
    recommendations,
    skills,
)
from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.data.courses import PHASE_TITLES, init_courses_data
from app.data.courses_phase1 import init_phase1_data
from app.data.courses_phase2 import init_phase2_data
from app.data.courses_phase3_6 import init_phase3_6_data
from app.data.learning_paths import init_learning_paths


def _assert_data_contract(db):
    """Data contract assertion — fail-fast if seed data is corrupt.

    This is the FIRST line of defense: the server refuses to start
    if the database does not match the expected 6-phase course system.

    Philosophy: a crashed server is better than a server serving wrong data.
    """
    from app.models import Chapter, Course

    errors = []

    # 1. Exactly 6 published courses
    published = db.query(Course).filter(Course.is_published).all()
    if len(published) != 6:
        errors.append(f"Expected 6 published courses, got {len(published)}")

    # 2. All published courses must belong to our 6-phase system
    valid_titles = set(PHASE_TITLES.values())
    for c in published:
        if c.title not in valid_titles:
            errors.append(f"Unknown published course: '{c.title}' (valid: {sorted(valid_titles)})")

    # 3. Each course must have ≥ 1 chapter (seed data minimum)
    for c in published:
        ch_count = db.query(Chapter).filter(Chapter.course_id == c.id).count()
        if ch_count < 1:
            errors.append(f"{c.title}: 0 chapters (minimum 1)")

    # 4. Each course must have ≥ 0 labs (seed data has 0 labs; labs come from manual deepening)
    # No minimum lab check — labs are added post-seed via content deepening,
    # not required at initial deployment. Contract tests enforce lab presence separately.

    # 5. No duplicate titles
    all_titles = db.query(Course.title).all()
    title_list = [t[0] for t in all_titles]
    if len(title_list) != len(set(title_list)):
        dupes = [t for t in title_list if title_list.count(t) > 1]
        errors.append(f"Duplicate course titles: {set(dupes)}")

    # 6. No orphan courses (courses not in our system)
    orphans = db.query(Course).filter(Course.title.notin_(valid_titles)).all()
    if orphans:
        errors.append(f"Orphan courses: {[o.title for o in orphans]}")

    if errors:
        print("❌ 数据契约校验失败:")
        for e in errors:
            print(f"   • {e}")
        msg = f"Data contract violated: {len(errors)} error(s). Server refused to start."
        raise RuntimeError(msg)


def _format_size(size_bytes: int) -> str:
    """格式化字节大小为人类可读格式"""
    if size_bytes == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时确保数据库schema就绪
    # V1.0: Use Alembic migration as primary schema management
    # Fallback to init_db() only if Alembic is not available (e.g. tests)
    try:
        from alembic import command as alembic_command
        from alembic.config import Config as AlembicConfig

        alembic_cfg = AlembicConfig(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        alembic_command.upgrade(alembic_cfg, "head")
    except Exception:
        # Fallback for test/dev environments without Alembic setup
        init_db()
    db = SessionLocal()
    try:
        # Step 1: Create course shells + clean up orphan courses
        init_courses_data(db)
        # Step 1b: Initialize learning paths (multi-path curriculum)
        init_learning_paths(db)
        # Step 2: Load Phase 1/2 from high-quality JSON files
        init_phase1_data(db)
        init_phase2_data(db)
        # Step 3: Load Phase 3-6 from extended data
        init_phase3_6_data(db)
        # Step 4: Invalidate all course caches after seed data refresh
        from app.core.cache import cache_manager

        try:
            cache_manager.delete_pattern("courses:*")
        except Exception:
            pass
        # Step 5: Assert data contract — refuse to start if violated
        _assert_data_contract(db)
    finally:
        db.close()
    print("✅ 数据库初始化完成（数据契约校验通过）")

    # 检查沙箱镜像（同步检查，不阻塞启动）
    # Docker 构建在后台进行，不影响应用启动
    try:
        from app.services.code_executor import get_sandbox_image_info

        print("🔍 正在检查 Docker 沙箱镜像...")
        image_info = get_sandbox_image_info()

        if os.environ.get("DISABLE_DOCKER_SANDBOX") == "1":
            print("ℹ️ Docker 沙箱已禁用（DISABLE_DOCKER_SANDBOX=1），使用本地回退模式")
        elif not image_info["docker_available"]:
            print("⚠️ Docker 不可用，代码执行将使用本地回退模式")
        elif image_info["image_exists"]:
            print(f"✅ 沙箱镜像已存在: {image_info['image_tag']}")
        else:
            print("⏳ 沙箱镜像未找到，将在后台异步构建")
            # 在后台启动镜像构建任务（不等待完成）
            asyncio.create_task(_build_sandbox_image_async())
    except Exception as e:
        print(f"⚠️ 沙箱镜像检查失败: {e}")
        print("   代码执行将使用本地回退模式")

    yield
    # 关闭时的清理
    print("👋 应用关闭")


async def _build_sandbox_image_async():
    """后台异步构建沙箱镜像"""
    try:
        from app.services.code_executor import ensure_sandbox_image

        success = await ensure_sandbox_image()
        if success:
            print("✅ 沙箱镜像后台构建完成")
        else:
            print("⚠️ 沙箱镜像构建失败，代码执行将使用本地回退模式")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"❌ 沙箱镜像后台构建异常: {e}")
        print("   代码执行将使用本地回退模式")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI学习平台 - 从入门到AI团队Leader",
    version=settings.VERSION,
    lifespan=lifespan,
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
# 静态文件服务配置
STATIC_DIR = os.getenv("STATIC_DIR", "../frontend")
STATIC_DIR_V2 = os.getenv("STATIC_DIR_V2", "../frontend-v2/dist")
# Force absolute path to avoid cwd issues
STATIC_DIR = os.path.abspath(STATIC_DIR)
STATIC_DIR_V2 = os.path.abspath(STATIC_DIR_V2)
SERVE_STATIC = True  # Always serve static files in this deployment

if SERVE_STATIC and os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    print(f"✅ 旧版静态文件: {STATIC_DIR}")

# V2 作为主前端——assets 和 index.html 都从 dist 目录服务
if SERVE_STATIC and os.path.exists(STATIC_DIR_V2):
    app.mount(
        "/assets", StaticFiles(directory=os.path.join(STATIC_DIR_V2, "assets")), name="v2-assets"
    )
    app.mount(
        "/v2/assets",
        StaticFiles(directory=os.path.join(STATIC_DIR_V2, "assets")),
        name="v2-assets-legacy",
    )
    print(f"✅ V2前端 (dist): {STATIC_DIR_V2}")


# 注册API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["课程"])
app.include_router(labs.router, prefix="/api/v1/labs", tags=["实验"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["学习进度"])
app.include_router(certificates.router, prefix="/api/v1/certificates", tags=["证书"])
app.include_router(discussions.router, prefix="/api/v1", tags=["讨论区"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["数据分析"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["技能雷达"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["公开主页"])
app.include_router(recommendations.router, prefix="/api/v1", tags=["个性化推荐"])


@app.get("/", response_class=HTMLResponse)
def root():
    """首页 - V2 React SPA"""
    # 优先 V2
    v2_index = os.path.join(STATIC_DIR_V2, "index.html")
    if os.path.exists(v2_index):
        return FileResponse(v2_index)
    # 回退旧版
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse(content="<h1>AI Learning Platform</h1><p>Frontend not found</p>")


@app.get("/p/{full_path:path}", response_class=HTMLResponse)
async def public_profile_spa(full_path: str, request: Request):
    """SPA fallback for public profile pages /p/{username}."""
    # Serve static assets (js/css/png/...) under /p/ directly
    static_ext = (
        ".js",
        ".mjs",
        ".css",
        ".map",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".json",
        ".webp",
    )
    if full_path and any(full_path.endswith(e) for e in static_ext):
        file_path = os.path.normpath(os.path.join(STATIC_DIR, full_path))
        if file_path.startswith(os.path.abspath(STATIC_DIR)) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return HTMLResponse(content="Not Found", status_code=404)

    # Extract username from path
    username = full_path.strip("/")
    if not username or "/" in username:
        index_file = os.path.join(STATIC_DIR, "spa.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return HTMLResponse(content="<h1>Not Found</h1>", status_code=404)

    # Try to fetch user profile data for OG tag injection
    og_tags = _build_og_tags(username)

    # Read the SPA template and inject OG tags
    spa_file = os.path.join(STATIC_DIR, "spa.html")
    if not os.path.exists(spa_file):
        index_file = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_file):
            spa_file = index_file
        else:
            return HTMLResponse(content="<h1>Frontend not found</h1>")

    with open(spa_file, "r", encoding="utf-8") as f:
        html = f.read()

    # Inject OG tags before </head>
    if og_tags:
        html = html.replace("</head>", f"{og_tags}\n</head>")

    return HTMLResponse(content=html)


def _build_og_tags(username: str) -> str:
    """Build OG meta tags by querying user profile data.

    Returns HTML string of <meta> tags to inject into <head>.
    For non-existent/private users, returns noindex tag.
    """
    from app.models import User
    from app.models.user_profile import UserProfile

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()

        # Non-existent or inactive user → noindex
        if user is None or not user.is_active:
            return '<meta name="robots" content="noindex, nofollow">'

        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

        # No profile or not public → noindex
        if profile is None or not profile.is_public:
            return '<meta name="robots" content="noindex, nofollow">'

        # Public user → inject OG tags
        display_name = profile.display_name or user.username
        bio = profile.bio or f"{display_name}的AILP能力主页"
        avatar_url = user.avatar_url or ""

        tags = [
            f'<meta property="og:title" content="{_html_escape(display_name)} - AILP能力主页">',
            f'<meta property="og:description" content="{_html_escape(bio)}">',
            '<meta property="og:type" content="profile">',
            f'<meta property="og:url" content="/p/{_html_escape(username)}">',
        ]

        if avatar_url:
            tags.append(f'<meta property="og:image" content="{_html_escape(avatar_url)}">')

        # Always include profile username
        tags.append(f'<meta property="profile:username" content="{_html_escape(username)}">')

        # Update page title
        tags.append(f"<title>{_html_escape(display_name)} - AILP能力主页</title>")

        return "\n    ".join(tags)
    except Exception:
        # On any error, return noindex (fail safe)
        return '<meta name="robots" content="noindex, nofollow">'
    finally:
        db.close()


def _html_escape(s: str) -> str:
    """Minimal HTML escaping for attribute values."""
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


@app.get("/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "frontend_v2": os.path.exists(STATIC_DIR_V2),
    }


@app.get("/v2", response_class=HTMLResponse)
@app.get("/v2/", response_class=HTMLResponse)
def v2_index():
    """V2 React前端入口"""
    index_file = os.path.join(STATIC_DIR_V2, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse(
        content="<h1>V2 Frontend not built</h1><p>Run: cd frontend-v2 && npm run build</p>"
    )


@app.get("/v2/{full_path:path}", response_class=HTMLResponse)
async def v2_spa_fallback(full_path: str):
    """V2 SPA fallback — all /v2/* routes return index.html for client-side routing"""
    # If it's an asset file, serve it directly
    asset_file = os.path.normpath(os.path.join(STATIC_DIR_V2, full_path))
    if asset_file.startswith(os.path.abspath(STATIC_DIR_V2)) and os.path.isfile(asset_file):
        return FileResponse(asset_file)
    # Otherwise return index.html for SPA routing
    index_file = os.path.join(STATIC_DIR_V2, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse(content="<h1>V2 Frontend not built</h1>")


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
    - /v2/* - V2前端（由独立路由处理）
    """
    # DEBUG: log what the catch-all sees
    import sys

    print(f"[DEBUG catch-all] full_path='{full_path}'", file=sys.stderr)
    # V2 routes are handled by their own route handlers — never fall through here
    if full_path == "v2/" or full_path == "v2":
        # /v2/ and /v2 with trailing slash — serve V2 index directly
        index_file = os.path.join(STATIC_DIR_V2, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
    if full_path.startswith("v2/"):
        # /v2/* SPA routes — serve V2 index for client-side routing
        asset_path = full_path[3:]  # strip "v2/"
        asset_file = os.path.normpath(os.path.join(STATIC_DIR_V2, asset_path))
        if asset_file.startswith(os.path.abspath(STATIC_DIR_V2)) and os.path.isfile(asset_file):
            return FileResponse(asset_file)
        index_file = os.path.join(STATIC_DIR_V2, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
    # --- Static file serving (js/css/images/src/etc.) ---
    # Before falling back to SPA/HTML, check if the path maps to a real file
    # under STATIC_DIR. This handles relative paths like js/api.js, css/style.css,
    # src/main.js that HTML pages reference without the /static/ prefix.
    static_extensions = (
        ".js",
        ".mjs",
        ".css",
        ".map",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".json",
        ".webp",
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
    excluded_paths = ["/api/", "/docs", "/redoc", "/openapi.json", "/static/", "/health"]

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
        status_code=200,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
