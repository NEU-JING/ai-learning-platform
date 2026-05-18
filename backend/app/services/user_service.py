from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db: Session, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email, username=user_data.username, password_hash=hashed_password
        )
        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
        except IntegrityError:
            db.rollback()
            raise ValueError("邮箱或用户名已存在")
        return db_user

    @staticmethod
    def update(db: Session, user: User, user_data: UserUpdate) -> User:
        if user_data.username:
            user.username = user_data.username
        if user_data.avatar_url:
            user.avatar_url = user_data.avatar_url
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        user = UserService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


user_service = UserService()
