"""Tutor module models — AI tutoring sessions and messages.

T12: Tutor Chat API
"""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models import Base


def _utcnow():
    return datetime.now(timezone.utc)


class TutorSession(Base):
    """AI tutor conversation session."""

    __tablename__ = "tutor_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_type = Column(String(32), nullable=False)  # diagnosis, code_review, qa, recommendation
    context_id = Column(Integer, nullable=True)  # lab_id, course_id, etc.
    context_type = Column(String(32), nullable=True)  # lab, course, chapter
    status = Column(String(16), default="active")  # active, closed
    message_count = Column(Integer, default=0)
    effectiveness_score = Column(Numeric(3, 2), nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    closed_at = Column(DateTime, nullable=True)

    # relationships
    user = relationship("User", back_populates="tutor_sessions")
    messages = relationship("TutorMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TutorSession(id={self.id}, type={self.session_type}, user_id={self.user_id})>"


class TutorMessage(Base):
    """Message in a tutor session."""

    __tablename__ = "tutor_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String(16), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # code snippets, errors, etc.
    tokens_used = Column(Integer, nullable=True)
    model = Column(String(64), nullable=True)  # LLM model used
    latency_ms = Column(Integer, nullable=True)  # Response latency
    provider = Column(String(32), nullable=True)  # ark, openrouter, qianfan, etc.
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    session = relationship("TutorSession", back_populates="messages")

    def __repr__(self):
        return f"<TutorMessage(id={self.id}, role={self.role}, session_id={self.session_id})>"


class CodeReview(Base):
    """Code review record."""

    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(
        Integer,
        ForeignKey("tutor_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="SET NULL"), nullable=True)
    code_content = Column(Text, nullable=False)
    language = Column(String(16), nullable=False)  # python, javascript
    issues = Column(JSON, nullable=True)  # [{type, line, message, suggestion}]
    dimensions = Column(JSON, nullable=True)  # {correctness, efficiency, readability, style, best_practices}
    overall_score = Column(Numeric(5, 2), nullable=True)  # 0-100
    summary = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=_utcnow)

    # relationships
    user = relationship("User")
    lab = relationship("Lab")
    session = relationship("TutorSession")

    def __repr__(self):
        return f"<CodeReview(id={self.id}, user_id={self.user_id}, score={self.overall_score})>"


class LearningObstacle(Base):
    """Learning obstacle detection record."""

    __tablename__ = "learning_obstacles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="SET NULL"), nullable=True)
    obstacle_type = Column(String(32), nullable=True)  # time_exceeded, multiple_failures, stuck
    detection_data = Column(JSON, nullable=True)  # detection basis
    tutor_response = Column(Text, nullable=True)  # AI tutor response
    resolved = Column(Integer, default=0)  # 0=false, 1=true
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    user = relationship("User")
    lab = relationship("Lab")

    def __repr__(self):
        return (
            f"<LearningObstacle(id={self.id}, type={self.obstacle_type}, user_id={self.user_id})>"
        )
