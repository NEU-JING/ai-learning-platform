from math import ceil
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import User
from app.schemas.course import (
    ChapterResponse,
    CourseListResponse,
    CourseResponse,
    LabPublicResponse,
)
from app.schemas.pagination import PaginatedResponse
from app.services.course_service import course_service

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CourseListResponse])
def list_courses(
    level: Optional[str] = None,
    category: Optional[str] = None,
    page: Optional[int] = Query(None, ge=1, description="Page number (1-indexed)"),
    per_page: Optional[int] = Query(None, ge=1, le=100, description="Items per page (max 100)"),
    db: Session = Depends(get_db),
):
    """List published courses.

    Always returns a PaginatedResponse. When `page` is omitted, returns all
    items in a single page (backward compatible wrapper).
    """
    courses, total = course_service.list_courses(
        db, level=level, category=category, page=page, per_page=per_page
    )

    if page is not None:
        _per_page = min(per_page or 20, 100)
        _pages = ceil(total / _per_page) if total > 0 else 0
        return {
            "items": courses,
            "total": total,
            "page": page,
            "per_page": _per_page,
            "pages": _pages,
        }

    # Backward compatible: wrap all items in PaginatedResponse with page=None
    return {
        "items": courses,
        "total": total,
        "page": None,
        "per_page": None,
        "pages": None,
    }


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get course detail with chapters."""
    course = course_service.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    return course


@router.get("/{course_id}/chapters", response_model=List[ChapterResponse])
def list_chapters(course_id: int, db: Session = Depends(get_db)):
    """List chapters of a course."""
    return course_service.get_chapters(db, course_id)


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """Get chapter detail."""
    chapter = course_service.get_chapter(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")
    return chapter


@router.get("/chapters/{chapter_id}/lab", response_model=Optional[LabPublicResponse])
def get_chapter_lab(chapter_id: int, db: Session = Depends(get_db)):
    """Get the lab associated with a chapter (public view, no solution)."""
    return course_service.get_chapter_lab(db, chapter_id)
