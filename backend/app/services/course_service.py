from sqlalchemy.orm import Session
from app.models import Course


def get_all_courses(db: Session) -> list:
    return db.query(Course).filter(Course.is_published == True).order_by(Course.order_index).all()


def get_course_detail(db: Session, course_id: int) -> Course:
    return db.query(Course).filter(Course.id == course_id, Course.is_published == True).first()