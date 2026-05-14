from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User, LearningProgress, Course, Chapter
from app.schemas.progress import (
    ProgressUpdate,
    ProgressResponse,
    CourseProgressResponse,
    LearningStatsResponse,
)

router = APIRouter()


@router.get("/", response_model=List[ProgressResponse])
def get_my_progress(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's learning progress."""
    query = db.query(LearningProgress).filter(LearningProgress.user_id == current_user.id)

    if course_id:
        chapters = db.query(Chapter.id).filter(Chapter.course_id == course_id).subquery()
        query = query.filter(LearningProgress.chapter_id.in_(chapters))

    progress_list = query.all()

    return [
        {
            "id": p.id,
            "chapter_id": p.chapter_id,
            "status": p.status,
            "completed_at": p.completed_at,
            "last_accessed_at": p.last_accessed_at,
            "created_at": p.created_at,
        }
        for p in progress_list
    ]


@router.get("/courses/{course_id}", response_model=CourseProgressResponse)
def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get progress statistics for a specific course."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")

    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).all()
    total_chapters = len(chapters)

    if total_chapters == 0:
        return CourseProgressResponse(
            course_id=course_id,
            course_title=course.title,
            total_chapters=0,
            completed_chapters=0,
            in_progress_chapters=0,
            progress_percentage=0.0,
            is_completed=False,
        )

    chapter_ids = [c.id for c in chapters]
    progress_records = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.chapter_id.in_(chapter_ids),
    ).all()

    completed = sum(1 for p in progress_records if p.status == "completed")
    in_progress = sum(1 for p in progress_records if p.status == "in_progress")
    progress_percentage = round((completed / total_chapters) * 100, 2)

    return CourseProgressResponse(
        course_id=course_id,
        course_title=course.title,
        total_chapters=total_chapters,
        completed_chapters=completed,
        in_progress_chapters=in_progress,
        progress_percentage=progress_percentage,
        is_completed=completed == total_chapters,
    )


@router.post("/chapters/{chapter_id}", response_model=ProgressResponse)
def update_progress(
    chapter_id: int,
    progress_data: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update chapter learning progress (body-based, unified endpoint)."""
    # Validate chapter exists
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")

    # Validate status value
    if progress_data.status not in ("not_started", "in_progress", "completed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的进度状态，允许: not_started, in_progress, completed",
        )

    # Find or create progress record
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.chapter_id == chapter_id,
    ).first()

    now = datetime.now(timezone.utc)

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
            completed_at=now if progress_data.status == "completed" else None,
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
        "created_at": progress.created_at,
    }


@router.get("/stats/summary", response_model=LearningStatsResponse)
def get_learning_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get learning statistics summary."""
    progress_list = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).all()

    total = len(progress_list)
    completed = sum(1 for p in progress_list if p.status == "completed")
    in_progress = sum(1 for p in progress_list if p.status == "in_progress")
    not_started = total - completed - in_progress

    total_duration_minutes = sum(
        p.chapter.duration_minutes for p in progress_list if p.chapter and p.status == "completed"
    )

    completed_courses = set()
    for p in progress_list:
        if p.status == "completed" and p.chapter and p.chapter.course_id:
            completed_courses.add(p.chapter.course_id)

    return LearningStatsResponse(
        total_chapters_accessed=total,
        completed_chapters=completed,
        in_progress_chapters=in_progress,
        not_started_chapters=not_started,
        total_learning_minutes=total_duration_minutes,
        completed_courses=len(completed_courses),
    )


@router.get("/learning-path", response_model=List[dict])
def get_learning_path(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get full learning path with per-course progress."""
    courses = (
        db.query(Course).filter(Course.is_published == True).order_by(Course.order_index).all()
    )

    result = []
    for course in courses:
        chapters = db.query(Chapter).filter(Chapter.course_id == course.id).all()
        chapter_ids = [c.id for c in chapters]

        if chapter_ids:
            completed_count = (
                db.query(LearningProgress)
                .filter(
                    LearningProgress.user_id == current_user.id,
                    LearningProgress.chapter_id.in_(chapter_ids),
                    LearningProgress.status == "completed",
                )
                .count()
            )
            progress_pct = round((completed_count / len(chapters)) * 100, 2) if chapters else 0.0
        else:
            progress_pct = 0.0

        result.append(
            {
                "course_id": course.id,
                "course_title": course.title,
                "level": course.level,
                "description": course.description,
                "duration_hours": course.duration_hours,
                "progress_percentage": progress_pct,
                "total_chapters": len(chapters),
            }
        )

    return result
