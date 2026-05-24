"""Analytics service — event ingestion with optional Redis Streams publishing."""

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.analytics import AnalyticsEventCreate

logger = logging.getLogger(__name__)

# ── Redis Streams helpers (lazy-connect with graceful degradation) ──────────

_redis_client = None
_redis_unavailable = False


def _get_redis():
    """Return a Redis client or None if unavailable."""
    global _redis_client, _redis_unavailable

    if _redis_unavailable:
        return None
    if _redis_client is not None:
        return _redis_client

    try:
        import redis

        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        _redis_client.ping()
        logger.info("Redis connected for analytics Streams")
        return _redis_client
    except Exception as exc:
        logger.warning("Redis unavailable for analytics Streams: %s", exc)
        _redis_unavailable = True
        _redis_client = None
        return None


def _publish_to_stream(events: list[dict]) -> None:
    """Publish events to the analytics:events Redis Stream.

    Failures are silently swallowed — Redis is best-effort only.
    """
    r = _get_redis()
    if r is None:
        return

    try:
        for event_data in events:
            r.xadd("analytics:events", event_data, maxlen=100000)
    except Exception as exc:
        logger.debug("Redis Stream publish failed (non-blocking): %s", exc)


# ── Service ──────────────────────────────────────────────────────────────────


class AnalyticsService:
    """Analytics event ingestion and querying."""

    @staticmethod
    def ingest_events(
        db: Session,
        events: list[AnalyticsEventCreate],
        user_id: int | None = None,
        request_info: dict | None = None,
    ) -> int:
        """Bulk-insert events into the DB and optionally publish to Redis Streams.

        Args:
            db: Database session.
            events: List of AnalyticsEventCreate payloads from the client.
            user_id: Authenticated user ID (fills missing user_id in events).
            request_info: Dict with optional 'user_agent', 'ip_address', 'path'.

        Returns:
            Number of events accepted.
        """
        if not events:
            return 0

        request_info = request_info or {}
        now = datetime.now(timezone.utc)
        rows = []

        for evt in events:
            # Resolve user_id: auth token takes precedence over body
            resolved_user_id = user_id or evt.user_id
            # Use client timestamp if provided, otherwise server time
            ts = evt.timestamp.replace(tzinfo=timezone.utc) if evt.timestamp else now
            # Path: prefer request path, fall back to properties
            path = request_info.get("path") or evt.properties.get("path")

            row = {
                "user_id": resolved_user_id,
                "event_type": evt.event,
                "event_data": evt.properties,
                "session_id": evt.session_id or "",
                "path": str(path)[:500] if path else None,
                "referrer": request_info.get("referrer"),
                "user_agent": (request_info.get("user_agent") or "")[:500],
                "ip_address": request_info.get("ip_address"),
                "created_at": ts,
            }
            rows.append(row)

        # Bulk insert for performance (avoids N individual INSERTs)
        db.execute(
            AnalyticsService._bulk_insert_stmt(),
            rows,
        )
        db.commit()

        # Best-effort Redis Streams publishing (non-blocking)
        try:
            _publish_to_stream(rows)
        except Exception:
            pass  # DB write succeeded — never fail a request over Redis

        return len(rows)

    @staticmethod
    def _bulk_insert_stmt():
        """Return a reusable bulk-insert statement for analytics_events."""
        from sqlalchemy import insert

        from app.models import AnalyticsEvent

        return insert(AnalyticsEvent)

    @staticmethod
    def query_events(
        db: Session,
        event_type: str = None,
        user_id: int = None,
        days: int = 7,
    ) -> list:
        """Query historical events with optional filters.

        Args:
            db: Database session.
            event_type: Filter by event type (e.g. 'page_view').
            user_id: Filter by user ID.
            days: Look back this many days (default 7).

        Returns:
            List of AnalyticsEvent ORM instances.
        """
        from datetime import timedelta

        from app.models import AnalyticsEvent

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        q = db.query(AnalyticsEvent).filter(AnalyticsEvent.created_at >= cutoff)

        if event_type:
            q = q.filter(AnalyticsEvent.event_type == event_type)
        if user_id:
            q = q.filter(AnalyticsEvent.user_id == user_id)

        return q.order_by(AnalyticsEvent.created_at.desc()).limit(1000).all()
