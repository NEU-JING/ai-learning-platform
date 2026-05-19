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
        """创建用户，捕获数据库唯一约束冲突"""
        try:
            hashed_password = get_password_hash(user_data.password)
            db_user = User(
                email=user_data.email, username=user_data.username, password_hash=hashed_password
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            db.rollback()
            # 区分是邮箱还是用户名冲突
            error_str = str(e).lower()
            if "email" in error_str or "ix_users_email" in error_str:
                raise ValueError("该邮箱已被注册")
            elif "username" in error_str or "ix_users_username" in error_str:
                raise ValueError("该用户名已被使用")
            else:
                raise ValueError("用户信息已存在，请更换邮箱或用户名")

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
