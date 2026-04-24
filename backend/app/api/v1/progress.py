from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User, LearningProgress, Course, Chapter
from app.schemas.progress import (
    ProgressCreate, 
    ProgressUpdate, 
    ProgressResponse,
    CourseProgressResponse,
    LearningStatsResponse
)
from app.services.course_service import course_service

router = APIRouter()


@router.get("/", response_model=List[ProgressResponse])
def get_my_progress(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的学习进度"""
    query = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    )
    
    if course_id:
        # 通过course_id筛选
        chapters = db.query(Chapter.id).filter(Chapter.course_id == course_id).subquery()
        query = query.filter(LearningProgress.chapter_id.in_(chapters))
    
    progress_list = query.all()
    
    result = []
    for p in progress_list:
        result.append({
            "id": p.id,
            "chapter_id": p.chapter_id,
            "status": p.status,
            "completed_at": p.completed_at,
            "last_accessed_at": p.last_accessed_at,
            "created_at": p.created_at
        })
    
    return result


@router.get("/courses/{course_id}", response_model=CourseProgressResponse)
def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取某课程的学习进度统计"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 获取课程所有章节
    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).all()
    total_chapters = len(chapters)
    
    if total_chapters == 0:
        return {
            "course_id": course_id,
            "course_title": course.title,
            "total_chapters": 0,
            "completed_chapters": 0,
            "in_progress_chapters": 0,
            "progress_percentage": 0,
            "is_completed": False
        }
    
    # 获取用户在该课程的进度
    chapter_ids = [c.id for c in chapters]
    progress_records = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.chapter_id.in_(chapter_ids)
    ).all()
    
    progress_map = {p.chapter_id: p for p in progress_records}
    
    completed = sum(1 for p in progress_records if p.status == "completed")
    in_progress = sum(1 for p in progress_records if p.status == "in_progress")
    
    progress_percentage = round((completed / total_chapters) * 100, 2)
    
    return {
        "course_id": course_id,
        "course_title": course.title,
        "total_chapters": total_chapters,
        "completed_chapters": completed,
        "in_progress_chapters": in_progress,
        "progress_percentage": progress_percentage,
        "is_completed": completed == total_chapters
    }


@router.post("/chapters/{chapter_id}", response_model=ProgressResponse)
def update_progress(
    chapter_id: int,
    progress_data: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新章节学习进度"""
    # 验证章节存在
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )
    
    # 查找或创建进度记录
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.chapter_id == chapter_id
    ).first()
    
    now = datetime.utcnow()
    
    if progress:
        progress.status = progress_data.status
        progress.last_accessed_at = now
        if progress_data.status == "completed":
            progress.completed_at = now
    else:
        progress = LearningProgress(
            user_id=current_user.id,
            chapter_id=chapter_id,
            status=progress_data.status,
            last_accessed_at=now,
            completed_at=now if progress_data.status == "completed" else None
        )
        db.add(progress)
    
    db.commit()
    db.refresh(progress)
    
    return {
        "id": progress.id,
        "chapter_id": progress.chapter_id,
        "status": progress.status,
        "completed_at": progress.completed_at,
        "last_accessed_at": progress.last_accessed_at,
        "created_at": progress.created_at
    }


@router.get("/stats/summary", response_model=LearningStatsResponse)
def get_learning_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取学习统计概览"""
    progress_list = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).all()
    
    total_chapters = len(progress_list)
    completed = sum(1 for p in progress_list if p.status == "completed")
    in_progress = sum(1 for p in progress_list if p.status == "in_progress")
    not_started = total_chapters - completed - in_progress
    
    # 计算总学习时长（根据完成章节数估算）
    total_duration_minutes = sum(
        p.chapter.duration_minutes for p in progress_list 
        if p.chapter and p.status == "completed"
    )
    
    # 获取已完成的课程数
    completed_courses = set()
    for p in progress_list:
        if p.status == "completed" and p.chapter and p.chapter.course_id:
            completed_courses.add(p.chapter.course_id)
    
    return {
        "total_chapters_accessed": total_chapters,
        "completed_chapters": completed,
        "in_progress_chapters": in_progress,
        "not_started_chapters": not_started,
        "total_learning_minutes": total_duration_minutes,
        "completed_courses": len(completed_courses)
    }


@router.get("/learning-path", response_model=List[dict])
def get_learning_path(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取完整学习路径及各阶段进度"""
    courses = db.query(Course).filter(
        Course.is_published == True
    ).order_by(Course.order_index).all()
    
    result = []
    for course in courses:
        # 计算每门课程的进度
        chapters = db.query(Chapter).filter(Chapter.course_id == course.id).all()
        chapter_ids = [c.id for c in chapters]
        
        if chapter_ids:
            completed_count = db.query(LearningProgress).filter(
                LearningProgress.user_id == current_user.id,
                LearningProgress.chapter_id.in_(chapter_ids),
                LearningProgress.status == "completed"
            ).count()
            
            progress_pct = round((completed_count / len(chapters)) * 100, 2) if chapters else 0
        else:
            progress_pct = 0
        
        result.append({
            "course_id": course.id,
            "course_title": course.title,
            "level": course.level,
            "description": course.description,
            "duration_hours": course.duration_hours,
            "progress_percentage": progress_pct,
            "total_chapters": len(chapters)
        })
    
    return result
