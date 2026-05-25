"""Analytics event schemas — request/response models for the event ingestion API."""

from datetime import datetime

from pydantic import BaseModel, Field


class AnalyticsEventCreate(BaseModel):
    """Single event payload from the frontend tracking SDK.

    The `user_id` field is optional — when the user is authenticated,
    the API fills it from the JWT token. Anonymous users can omit it.
    """

    event: str  # event type: page_view, chapter_start, chapter_complete, lab_submit, etc.
    properties: dict = Field(default_factory=dict)  # flexible payload
    session_id: str = ""  # browser session UUID
    timestamp: datetime | None = None  # client-side timestamp
    user_id: int | None = None  # authenticated user (filled by API if missing)


class AnalyticsEventBatch(BaseModel):
    """Batch of events sent by the frontend SDK (typically every 5-10 events)."""

    events: list[AnalyticsEventCreate]


class AnalyticsEventResponse(BaseModel):
    """Response returned after event ingestion (202 Accepted)."""

    accepted: int  # number of events accepted
    rejected: int = 0  # number of events rejected
