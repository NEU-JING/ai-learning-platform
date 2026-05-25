"""UserProfile model — public profile visibility settings.

1:1 with users table. Record does NOT exist = user never enabled public profile (BR1).
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import Base, _utcnow


class UserProfile(Base):
    """Public profile settings — at most one record per user."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Master switch
    is_public = Column(Boolean, default=False, nullable=False)

    # Per-dimension visibility (BR4: independent control)
    show_basic_info = Column(Boolean, default=False, nullable=False)
    show_skill_radar = Column(Boolean, default=False, nullable=False)
    show_labs = Column(Boolean, default=False, nullable=False)
    show_certificates = Column(Boolean, default=False, nullable=False)

    # Display info (decoupled from User auth data)
    display_name = Column(String(50), nullable=True)  # null → fall back to username
    bio = Column(String(200), nullable=True)  # one-line intro

    # Timestamps
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    user = relationship("User", backref="profile")
