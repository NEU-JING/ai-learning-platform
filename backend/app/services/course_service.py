import json
import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Course, Chapter, LearningProgress
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)


class CourseService:
    @staticmethod
    def list_courses(
        db: Session,
        level: Optional[str] = None,
        category: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Tuple[List[Course], int]:
        """List published courses.

        Args:
            page: 1-indexed page number. None → return all (no pagination).
            per_page: Items per page (max 100). None → return all.

        Returns:
            (courses_list, total_count)
        """
        # Build cache key
        cache_key = f"courses:list:{level or ''}:{category or ''}:{page or ''}:{per_page or ''}"

        # Try cache first
        cached = cache_manager.get(cache_key)
        if cached is not None:
            try:
                data = json.loads(cached)
                # Re-hydrate ORM objects from cached IDs
                course_ids = data.get("course_ids", [])
                total = data.get("total", 0)
                if course_ids:
                    courses = db.query(Course).filter(Course.id.in_(course_ids)).order_by(Course.order_index).all()
                    # Preserve order
                    id_order = {cid: idx for idx, cid in enumerate(course_ids)}
                    courses.sort(key=lambda c: id_order.get(c.id, 0))
                else:
                    courses = []
                return courses, total
            except (json.JSONDecodeError, KeyError):
                logger.debug("Cache decode error for %s, falling back to DB", cache_key)

        # Cache miss → query DB
        query = db.query(Course).filter(Course.is_published == True)

        if level:
            query = query.filter(Course.level == level)
        if category:
            query = query.filter(Course.category == category)

        total = query.count()

        if page is not None:
            _per_page = min(per_page or 20, 100)
            offset = (page - 1) * _per_page
            courses = query.order_by(Course.order_index).offset(offset).limit(_per_page).all()
        else:
            courses = query.order_by(Course.order_index).all()

        # Write to cache
        try:
            cache_data = json.dumps({
                "course_ids": [c.id for c in courses],
                "total": total,
            })
            cache_manager.set(cache_key, cache_data, ttl=300)
        except Exception:
            pass  # cache write failure is non-critical

        return courses, total

    @staticmethod
    def get_course(db: Session, course_id: int) -> Optional[Course]:
        cache_key = f"courses:detail:{course_id}"

        cached = cache_manager.get(cache_key)
        if cached is not None:
            try:
                data = json.loads(cached)
                course = db.query(Course).filter(Course.id == data["id"]).first()
                if course:
                    return course
            except (json.JSONDecodeError, KeyError):
                logger.debug("Cache decode error for %s, falling back to DB", cache_key)

        course = db.query(Course).filter(
            Course.id == course_id,
            Course.is_published == True
        ).first()

        if course:
            try:
                cache_manager.set(cache_key, json.dumps({"id": course.id}), ttl=300)
            except Exception:
                pass

        return course

    @staticmethod
    def get_chapters(db: Session, course_id: int) -> List[Chapter]:
        return db.query(Chapter).filter(
            Chapter.course_id == course_id
        ).order_by(Chapter.order_index).all()

    @staticmethod
    def get_chapter(db: Session, chapter_id: int) -> Optional[Chapter]:
        cache_key = f"chapters:detail:{chapter_id}"

        cached = cache_manager.get(cache_key)
        if cached is not None:
            try:
                data = json.loads(cached)
                chapter = db.query(Chapter).filter(Chapter.id == data["id"]).first()
                if chapter:
                    return chapter
            except (json.JSONDecodeError, KeyError):
                logger.debug("Cache decode error for %s, falling back to DB", cache_key)

        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()

        if chapter:
            try:
                cache_manager.set(cache_key, json.dumps({"id": chapter.id}), ttl=300)
            except Exception:
                pass

        return chapter

    @staticmethod
    def get_chapter_lab(db: Session, chapter_id: int):
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if chapter and chapter.lab:
            return chapter.lab
        return None

    @staticmethod
    def get_user_progress(db: Session, user_id: int) -> List[dict]:
        progress = db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id
        ).all()

        result = []
        for p in progress:
            result.append({
                "chapter_id": p.chapter_id,
                "status": p.status,
                "completed_at": p.completed_at,
                "last_accessed_at": p.last_accessed_at
            })
        return result

    @staticmethod
    def update_progress(
        db: Session,
        user_id: int,
        chapter_id: int,
        status: str
    ):
        from datetime import datetime

        progress = db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id,
            LearningProgress.chapter_id == chapter_id
        ).first()

        if progress:
            progress.status = status
            progress.last_accessed_at = datetime.utcnow()
            if status == "completed":
                progress.completed_at = datetime.utcnow()
        else:
            progress = LearningProgress(
                user_id=user_id,
                chapter_id=chapter_id,
                status=status
            )
            if status == "completed":
                progress.completed_at = datetime.utcnow()
            db.add(progress)

        db.commit()
        db.refresh(progress)
        return progress

    @staticmethod
    def invalidate_course_cache(course_id: Optional[int] = None) -> None:
        """Invalidate course-related caches after data mutations."""
        cache_manager.delete_pattern("courses:list:*")
        if course_id is not None:
            cache_manager.delete(f"courses:detail:{course_id}")
            cache_manager.delete_pattern("chapters:detail:*")


course_service = CourseService()
