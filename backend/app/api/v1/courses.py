from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User
from app.schemas.course import (
    CourseResponse, CourseListResponse, 
    ChapterResponse, LabResponse, LabSubmissionCreate, LabSubmissionResponse
)
from app.services.course_service import course_service
from app.services.lab_service import lab_service

router = APIRouter()


@router.get("/", response_model=List[CourseListResponse])
def list_courses(
    level: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取课程列表"""
    courses = course_service.list_courses(db, level=level, category=category)
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """获取课程详情"""
    course = course_service.get_course(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    return course


@router.get("/{course_id}/chapters", response_model=List[ChapterResponse])
def list_chapters(course_id: int, db: Session = Depends(get_db)):
    """获取课程章节列表"""
    return course_service.get_chapters(db, course_id)


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """获取章节详情"""
    chapter = course_service.get_chapter(db, chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )
    return chapter


@router.get("/chapters/{chapter_id}/lab", response_model=Optional[LabResponse])
def get_chapter_lab(chapter_id: int, db: Session = Depends(get_db)):
    """获取章节的实验"""
    return course_service.get_chapter_lab(db, chapter_id)


@router.post("/labs/{lab_id}/submit", response_model=LabSubmissionResponse)
def submit_lab(
    lab_id: int,
    submission: LabSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """提交实验代码"""
    from app.models import Lab
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="实验不存在"
        )
    result = lab_service.submit_code(
        db=db,
        user_id=current_user.id,
        lab_id=lab_id,
        code=submission.code
    )
    return result


@router.get("/progress", response_model=List[dict])
def get_learning_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取学习进度"""
    return course_service.get_user_progress(db, current_user.id)


@router.post("/chapters/{chapter_id}/progress")
def update_chapter_progress(
    chapter_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新章节学习进度"""
    course_service.update_progress(
        db=db,
        user_id=current_user.id,
        chapter_id=chapter_id,
        status=status
    )
    return {"message": "进度已更新"}
