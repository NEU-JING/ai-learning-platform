"""
AI学习平台 - 主入口
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.database import get_db, init_db
from app.models import User, Course, Chapter, Lab, LearningProgress, LabSubmission
from app.schemas import (
    UserCreate, UserResponse, Token, 
    CourseResponse, ChapterResponse, LabResponse,
    CodeExecutionRequest, CodeExecutionResponse,
    ProgressUpdate, ProgressResponse
)
from app.services.code_executor import execute_code_sandbox
from app.services.course_service import get_all_courses, get_course_detail
from app.data.courses_extended import COURSES_DATA

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI学习平台API - 从入门到AI团队Leader"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 启动事件
@app.on_event("startup")
async def startup_event():
    # 初始化数据库
    init_db()
    # 初始化课程数据
    init_courses_data()

def init_courses_data():
    """初始化内置课程数据"""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        # 检查是否已有课程
        if db.query(Course).first():
            return
        
        for course_data in COURSES_DATA:
            course = Course(
                title=course_data["title"],
                description=course_data["description"],
                level=course_data["level"],
                category=course_data["category"],
                duration_hours=course_data["duration_hours"],
                order_index=course_data["order_index"],
                is_published=True
            )
            db.add(course)
            db.flush()  # 获取course.id
            
            # 添加章节
            for chapter_data in course_data.get("chapters", []):
                chapter = Chapter(
                    course_id=course.id,
                    title=chapter_data["title"],
                    content=chapter_data["content"],
                    chapter_type=chapter_data.get("chapter_type", "text"),
                    duration_minutes=chapter_data.get("duration_minutes", 60),
                    order_index=chapter_data.get("order_index", 0)
                )
                db.add(chapter)
                db.flush()
                
                # 添加实验（如果有）
                if "lab" in chapter_data:
                    lab_data = chapter_data["lab"]
                    lab = Lab(
                        chapter_id=chapter.id,
                        title=lab_data["title"],
                        description=lab_data.get("description", ""),
                        starter_code=lab_data.get("starter_code", ""),
                        solution_code=lab_data.get("solution_code", ""),
                        test_cases=lab_data.get("test_cases", []),
                        hints=lab_data.get("hints", [])
                    )
                    db.add(lab)
        
        db.commit()
        print("✅ 课程数据初始化完成")
    except Exception as e:
        print(f"❌ 课程数据初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

# 认证相关函数
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# ========== API路由 ==========

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "message": "欢迎使用AI学习平台！"
    }

# 用户认证
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="邮箱已注册")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    db_user = User(
        email=user.email,
        username=user.username,
        password_hash=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# 课程相关
@app.get("/api/courses", response_model=List[CourseResponse])
async def list_courses(db: Session = Depends(get_db)):
    """获取所有已发布课程"""
    courses = db.query(Course).filter(Course.is_published == True).order_by(Course.order_index).all()
    return courses

@app.get("/api/courses/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """获取课程详情"""
    course = db.query(Course).filter(Course.id == course_id, Course.is_published == True).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return course

@app.get("/api/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """获取章节详情"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return chapter

# 在线代码执行
@app.post("/api/code/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """执行Python代码"""
    result = await execute_code_sandbox(request.code, request.timeout)
    return result

# 实验提交
@app.post("/api/labs/{lab_id}/submit")
async def submit_lab(
    lab_id: int,
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交实验代码"""
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    # 执行代码
    result = await execute_code_sandbox(code, lab.time_limit_seconds)
    
    # 保存提交记录
    submission = LabSubmission(
        user_id=current_user.id,
        lab_id=lab_id,
        code=code,
        output=result.output,
        status="success" if result.success else "failed",
        execution_time_ms=result.execution_time_ms,
        error_message=result.error
    )
    db.add(submission)
    db.commit()
    
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time_ms": result.execution_time_ms,
        "submission_id": submission.id
    }

# 学习进度
@app.get("/api/progress", response_model=List[ProgressResponse])
async def get_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取用户学习进度"""
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).all()
    return progress

@app.post("/api/progress/{chapter_id}")
async def update_progress(
    chapter_id: int,
    update: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新学习进度"""
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.chapter_id == chapter_id
    ).first()
    
    if progress:
        progress.status = update.status
        if update.status == "completed":
            progress.completed_at = datetime.utcnow()
        progress.last_accessed_at = datetime.utcnow()
    else:
        progress = LearningProgress(
            user_id=current_user.id,
            chapter_id=chapter_id,
            status=update.status
        )
        db.add(progress)
    
    db.commit()
    return {"message": "进度更新成功"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
