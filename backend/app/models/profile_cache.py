"""ProfileCache model — CDN / Redis cache entries for public profiles.

Each row stores a serialized version of a public profile page,
keyed by (user_id, cache_key). Expired entries are cleaned up
by a scheduled job or lazy eviction.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models import Base, _utcnow


class ProfileCache(Base):
    """Serialized cache for public profile pages (CDN origin / Redis fallback)."""

    __tablename__ = "profile_cache"
    __table_args__ = (UniqueConstraint("user_id", "cache_key", name="uq_user_cache_key"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cache_key = Column(String(64), nullable=False)  # e.g. "public_profile:username"
    cached_data = Column(JSON, nullable=True)  # serialized profile response
    expires_at = Column(DateTime, nullable=False)  # TTL expiry timestamp
    created_at = Column(DateTime, default=_utcnow)

    # Relationships
    user = relationship("User")
