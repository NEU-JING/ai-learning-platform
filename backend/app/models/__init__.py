from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    role = Column(String(20), default="student")  # student, teacher, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    progress = relationship("LearningProgress", back_populates="user")
    submissions = relationship("LabSubmission", back_populates="user")
    discussions = relationship("Discussion", back_populates="user")
    comments = relationship("Comment", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    cover_image = Column(String(500), nullable=True)
    level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    category = Column(String(50), nullable=False)  # python, math, ml, dl, langchain, agent, leadership
    duration_hours = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    chapters = relationship("Chapter", back_populates="course", order_by="Chapter.order_index")
    discussions = relationship("Discussion", back_populates="course", order_by="Discussion.is_pinned.desc(), Discussion.created_at.desc()")

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # Markdown格式
    order_index = Column(Integer, default=0)
    chapter_type = Column(String(20), default="text")  # text, code, lab, video
    duration_minutes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    course = relationship("Course", back_populates="chapters")
    lab = relationship("Lab", back_populates="chapter", uselist=False)
    progress = relationship("LearningProgress", back_populates="chapter")

class Lab(Base):
    __tablename__ = "labs"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    starter_code = Column(Text, nullable=True)
    solution_code = Column(Text, nullable=True)
    test_cases = Column(JSON, default=list)
    requirements = Column(Text, nullable=True)  # pip requirements
    hints = Column(JSON, default=list)
    time_limit_seconds = Column(Integer, default=30)
    memory_limit_mb = Column(Integer, default=256)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    chapter = relationship("Chapter", back_populates="lab")
    submissions = relationship("LabSubmission", back_populates="lab")

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed
    completed_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="progress")
    chapter = relationship("Chapter", back_populates="progress")

class LabSubmission(Base):
    __tablename__ = "lab_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    code = Column(Text, nullable=False)
    output = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, running, success, failed
    execution_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="submissions")
    lab = relationship("Lab", back_populates="submissions")


class Discussion(Base):
    __tablename__ = "discussions"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="discussions")
    course = relationship("Course", back_populates="discussions")
    comments = relationship("Comment", back_populates="discussion", order_by="Comment.created_at.desc()", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    is_solution = Column(Boolean, default=False)  # 是否被标记为解决方案
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # 回复评论
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="comments")
    discussion = relationship("Discussion", back_populates="comments")
    parent = relationship("Comment", remote_side="Comment.id", back_populates="replies")
    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")
