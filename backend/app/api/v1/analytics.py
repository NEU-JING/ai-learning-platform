"""
Analytics API — lightweight event tracking.
No auth required for event ingestion (supports anonymous).
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_optional_current_user  # nullable auth
from app.core.database import get_db
from app.models import AnalyticsEvent

router = APIRouter()


class EventPayload(BaseModel):
    event_type: (
        str  # page_view, chapter_start, chapter_complete, lab_submit, lab_pass, exercise_attempt
    )
    event_data: Optional[dict[str, Any]] = None
    path: Optional[str] = None
    referrer: Optional[str] = None
    session_id: Optional[str] = None


class BatchEventPayload(BaseModel):
    events: list[EventPayload]


@router.post("/events")
def track_event(
    payload: EventPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """Track a single analytics event."""
    event = AnalyticsEvent(
        user_id=current_user.id if current_user else None,
        event_type=payload.event_type,
        event_data=payload.event_data,
        path=payload.path,
        referrer=payload.referrer,
        session_id=payload.session_id,
        user_agent=request.headers.get("user-agent", "")[:500],
        ip_address=request.client.host if request.client else None,
    )
    db.add(event)
    db.commit()
    return {"status": "ok"}


@router.post("/events/batch")
def track_events_batch(
    payload: BatchEventPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """Track multiple analytics events (for batching from frontend)."""
    user_agent = request.headers.get("user-agent", "")[:500]
    ip_address = request.client.host if request.client else None
    user_id = current_user.id if current_user else None

    events = []
    for p in payload.events[:50]:  # cap at 50 per batch
        events.append(
            AnalyticsEvent(
                user_id=user_id,
                event_type=p.event_type,
                event_data=p.event_data,
                path=p.path,
                referrer=p.referrer,
                session_id=p.session_id,
                user_agent=user_agent,
                ip_address=ip_address,
            )
        )
    db.add_all(events)
    db.commit()
    return {"status": "ok", "count": len(events)}


@router.get("/events/summary")
def get_events_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """Get event counts by type for current user."""
    if not current_user:
        return {"events": []}

    from sqlalchemy import func

    results = (
        db.query(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id))
        .filter(AnalyticsEvent.user_id == current_user.id)
        .group_by(AnalyticsEvent.event_type)
        .all()
    )
    return {"events": [{"type": r[0], "count": r[1]} for r in results]}
