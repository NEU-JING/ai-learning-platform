"""
Analytics API — lightweight event tracking for the frontend SDK.

- POST /events    — ingest batch events (open to anonymous + authenticated users)
- GET /events/summary — per-user event counts (auth required)
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_optional_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.analytics import AnalyticsEventBatch, AnalyticsEventResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()

# Alias for clearer intent in analytics context
get_current_user_optional = get_optional_current_user


@router.post("/events", response_model=AnalyticsEventResponse, status_code=202)
def ingest_events(
    batch: AnalyticsEventBatch,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Ingest a batch of analytics events from the frontend tracking SDK.

    - Authenticated users: user_id is auto-filled from the JWT token.
    - Anonymous users: user_id falls back to the request body (or null).
    - Returns 202 Accepted — event processing is asynchronous.
    """
    request_info = {
        "user_agent": request.headers.get("user-agent", ""),
        "ip_address": request.client.host if request.client else None,
        "path": request.url.path,
        "referrer": request.headers.get("referer"),
    }

    accepted = AnalyticsService.ingest_events(
        db=db,
        events=batch.events,
        user_id=current_user.id if current_user else None,
        request_info=request_info,
    )

    return AnalyticsEventResponse(accepted=accepted, rejected=0)


@router.get("/events/summary")
def get_events_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    """Get event counts by type for the current user (or empty for anonymous)."""
    if not current_user:
        return {"events": []}

    from sqlalchemy import func

    from app.models import AnalyticsEvent

    results = (
        db.query(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id))
        .filter(AnalyticsEvent.user_id == current_user.id)
        .group_by(AnalyticsEvent.event_type)
        .all()
    )
    return {"events": [{"type": r[0], "count": r[1]} for r in results]}
