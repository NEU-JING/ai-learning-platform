"""Redis cache manager with graceful degradation."""

import json
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Singleton Redis cache manager.

    All methods silently degrade when Redis is unavailable — they return
    None / perform no action instead of raising errors.
    """

    _instance: Optional["CacheManager"] = None

    def __new__(cls) -> "CacheManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._redis = None
            cls._instance._unavailable = False
        return cls._instance

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_redis(self):
        """Return a Redis client, or None if Redis is unavailable."""
        if self._unavailable:
            return None

        if self._redis is not None:
            return self._redis

        try:
            import redis

            self._redis = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            # Verify connectivity
            self._redis.ping()
            logger.info("Redis cache connected")
            return self._redis
        except Exception as exc:
            logger.warning("Redis unavailable — caching disabled: %s", exc)
            self._unavailable = True
            self._redis = None
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[str]:
        """Retrieve a cached value by key. Returns None on miss or error."""
        try:
            r = self._get_redis()
            if r is None:
                return None
            value = r.get(key)
            return value
        except Exception as exc:
            logger.debug("Cache GET error for %s: %s", key, exc)
            return None

    def set(self, key: str, value: str, ttl: int = 300) -> None:
        """Store a value in cache with TTL (seconds, default 300 = 5 min)."""
        try:
            r = self._get_redis()
            if r is None:
                return
            r.setex(key, ttl, value)
        except Exception as exc:
            logger.debug("Cache SET error for %s: %s", key, exc)

    def delete(self, key: str) -> None:
        """Delete a single cache key."""
        try:
            r = self._get_redis()
            if r is None:
                return
            r.delete(key)
        except Exception as exc:
            logger.debug("Cache DELETE error for %s: %s", key, exc)

    def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching a pattern (e.g. 'courses:*')."""
        try:
            r = self._get_redis()
            if r is None:
                return
            keys = r.keys(pattern)
            if keys:
                r.delete(*keys)
        except Exception as exc:
            logger.debug("Cache DELETE_PATTERN error for %s: %s", pattern, exc)


# Module-level singleton
cache_manager = CacheManager()
