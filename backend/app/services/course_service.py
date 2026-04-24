from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Course, Chapter, LearningProgress


class CourseService:
    @staticmethod
    def list_courses(
        db: Session, 
        level: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Course]:
        query = db.query(Course).filter(Course.is_published == True)
        
        if level:
            query = query.filter(Course.level == level)
        if category:
            query = query.filter(Course.category == category)
        
        return query.order_by(Course.order_index).all()
    
    @staticmethod
    def get_course(db: Session, course_id: int) -> Optional[Course]:
        return db.query(Course).filter(
            Course.id == course_id,
            Course.is_published == True
        ).first()
    
    @staticmethod
    def get_chapters(db: Session, course_id: int) -> List[Chapter]:
        return db.query(Chapter).filter(
            Chapter.course_id == course_id
        ).order_by(Chapter.order_index).all()
    
    @staticmethod
    def get_chapter(db: Session, chapter_id: int) -> Optional[Chapter]:
        return db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
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


course_service = CourseService()
