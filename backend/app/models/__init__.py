from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base — replaces deprecated declarative_base()."""


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    role = Column(String(20), default="student", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
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
    level = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    duration_hours = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    chapters = relationship("Chapter", back_populates="course", order_by="Chapter.order_index")
    discussions = relationship(
        "Discussion",
        back_populates="course",
        order_by="Discussion.is_pinned.desc(), Discussion.created_at.desc()",
    )

    @property
    def chapters_count(self):
        return len(self.chapters) if self.chapters else 0

    @property
    def labs_count(self):
        """Count labs across all chapters in this course."""
        if not self.chapters:
            return 0
        return sum(1 for ch in self.chapters if ch.lab is not None)


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    order_index = Column(Integer, default=0)
    chapter_type = Column(String(20), default="text")
    duration_minutes = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
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
    requirements = Column(Text, nullable=True)
    hints = Column(JSON, default=list)
    time_limit_seconds = Column(Integer, default=30)
    memory_limit_mb = Column(Integer, default=256)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    chapter = relationship("Chapter", back_populates="lab")
    submissions = relationship("LabSubmission", back_populates="lab")


class LearningProgress(Base):
    __tablename__ = "learning_progress"
    __table_args__ = (UniqueConstraint("user_id", "chapter_id", name="uq_user_chapter_progress"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    status = Column(String(20), default="not_started")
    completed_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, default=_utcnow)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    user = relationship("User", back_populates="progress")
    chapter = relationship("Chapter", back_populates="progress")


class LabSubmission(Base):
    __tablename__ = "lab_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    code = Column(Text, nullable=False)
    output = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    execution_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    # Grading fields (T2 addition)
    score = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=True)
    test_results = Column(JSON, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
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
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    user = relationship("User", back_populates="discussions")
    course = relationship("Course", back_populates="discussions")
    comments = relationship(
        "Comment",
        back_populates="discussion",
        order_by="Comment.created_at.desc()",
        cascade="all, delete-orphan",
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    is_solution = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    user = relationship("User", back_populates="comments")
    discussion = relationship("Discussion", back_populates="comments")
    parent = relationship("Comment", remote_side="Comment.id", back_populates="replies")
    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")
    likes = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")


class DiscussionLike(Base):
    __tablename__ = "discussion_likes"
    __table_args__ = (UniqueConstraint("user_id", "discussion_id", name="uq_user_discussion_like"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    discussion_id = Column(Integer, ForeignKey("discussions.id"), nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    user = relationship("User")
    discussion = relationship("Discussion")


class CommentLike(Base):
    __tablename__ = "comment_likes"
    __table_args__ = (UniqueConstraint("user_id", "comment_id", name="uq_user_comment_like"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    user = relationship("User")
    comment = relationship("Comment", back_populates="likes")


class AnalyticsEvent(Base):
    """User behavior tracking — lightweight event log."""

    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable for anonymous
    event_type = Column(String(50), nullable=False, index=True)  # page_view, chapter_start, etc.
    event_data = Column(JSON, nullable=True)  # flexible payload
    path = Column(String(500), nullable=True)  # URL path
    referrer = Column(String(500), nullable=True)  # previous page
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    session_id = Column(String(64), nullable=True, index=True)  # browser session
    created_at = Column(DateTime, default=_utcnow, index=True)

    # relationships
    user = relationship("User")


# ── V3: User Profile & Learning Paths ──────────────────────────────────────────


class UserSettings(Base):
    """用户画像设置 — 每个用户一条记录，存储学习路径偏好和背景信息。"""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    learning_path = Column(
        String(50), nullable=True
    )  # ai_expert / ai_engineer / ai_practitioner / ai_manager
    background_language = Column(String(50), nullable=True)  # java / python / javascript / other
    background_industry = Column(
        String(50), nullable=True
    )  # finance / internet / manufacturing / other
    ai_experience_level = Column(String(20), nullable=True)  # beginner / concept_aware / api_user
    assessment_completed = Column(Boolean, default=False)
    assessment_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    user = relationship("User")


class UserSkillScore(Base):
    """用户技能雷达评分 — 多维度 0-100 分。"""

    __tablename__ = "user_skill_scores"
    __table_args__ = (UniqueConstraint("user_id", "dimension", name="uq_user_skill_dimension"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dimension = Column(
        String(30), nullable=False
    )  # python / math / ml / dl / llm / engineering / coding_harness / ai_application / ai_strategy
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    user = relationship("User")


class UserAchievement(Base):
    """用户成就/徽章 — 每个用户可拥有多个成就。"""

    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_type", name="uq_user_achievement_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_type = Column(
        String(50), nullable=False
    )  # streak_7 / first_lab_pass / all_labs_phase1 / speed_demon / perfect_score
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    earned_at = Column(DateTime, default=_utcnow)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    user = relationship("User")


class LearningPath(Base):
    """学习路径定义 — 多路径课程体系的路径元数据。"""

    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(
        String(30), unique=True, index=True, nullable=False
    )  # ai_expert / ai_engineer / ai_practitioner / ai_manager
    title = Column(String(100), nullable=False)
    subtitle = Column(String(200), nullable=True)
    description = Column(Text, nullable=False)
    target_role = Column(String(100), nullable=False)
    estimated_weeks = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    modules = relationship("LearningPathModule", back_populates="learning_path")


class LearningPathModule(Base):
    """路径-课程模块关联 — 多对多桥接表，定义每条路径包含哪些课程。"""

    __tablename__ = "learning_path_modules"
    __table_args__ = (UniqueConstraint("path_id", "course_id", name="uq_path_course"),)

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(String(30), ForeignKey("learning_paths.path_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    requirement = Column(String(20), default="required")  # required / recommended / optional
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    learning_path = relationship("LearningPath", back_populates="modules")
    course = relationship("Course")


from app.models.user_profile import UserProfile  # noqa: E402, F401 — V4: public profile settings

__all__ = [
    "Base",
    "User",
    "Course",
    "Chapter",
    "Lab",
    "LearningProgress",
    "LabSubmission",
    "Discussion",
    "Comment",
    "DiscussionLike",
    "CommentLike",
    "AnalyticsEvent",
    # V3 additions
    "UserSettings",
    "UserSkillScore",
    "UserAchievement",
    "LearningPath",
    "LearningPathModule",
    # V4 additions
    "UserProfile",
]
