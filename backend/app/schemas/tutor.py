"""Tutor module schemas.

T12: Tutor Chat API
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TutorMessageBase(BaseModel):
    """Base TutorMessage schema."""

    role: str = Field(..., description="Message role: user, assistant, system")
    content: str = Field(..., description="Message content")
    message_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata (code snippets, etc.)"
    )


class TutorMessageCreate(TutorMessageBase):
    """Schema for creating a tutor message."""

    pass


class TutorMessageResponse(TutorMessageBase):
    """Schema for tutor message response."""

    id: int
    session_id: int
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    latency_ms: Optional[int] = None
    provider: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TutorSessionBase(BaseModel):
    """Base TutorSession schema."""

    session_type: str = Field(
        ..., description="Session type: diagnosis, code_review, qa, recommendation"
    )
    context_id: Optional[int] = Field(None, description="Related lab_id, course_id, etc.")
    context_type: Optional[str] = Field(None, description="Context type: lab, course, chapter")


class TutorSessionCreate(TutorSessionBase):
    """Schema for creating a tutor session."""

    message: str = Field(..., description="Initial user message")
    attachments: Optional[List[Dict[str, Any]]] = Field(
        None, description="Attachments (code snippets, etc.)"
    )


class TutorSessionResponse(BaseModel):
    """Schema for tutor session response."""

    session_id: int
    session_type: str
    status: str
    message_count: int
    response: Dict[str, Any]  # LLM response
    created_at: datetime

    model_config = {"from_attributes": True}


class TutorChatRequest(BaseModel):
    """Schema for tutor chat request."""

    session_id: Optional[int] = Field(None, description="Existing session ID")
    session_type: Optional[str] = Field(
        None, description="Session type: diagnosis, code_review, qa, recommendation"
    )
    context_id: Optional[int] = Field(None, description="Related lab_id, course_id, etc.")
    context_type: Optional[str] = Field(None, description="Context type: lab, course, chapter")
    message: str = Field(..., description="User message")
    attachments: Optional[List[Dict[str, Any]]] = Field(
        None, description="Attachments (code snippets, etc.)"
    )


class TutorChatResponse(BaseModel):
    """Schema for tutor chat response."""

    session_id: int
    session_type: str
    status: str
    message_count: int
    response: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionMessagesResponse(BaseModel):
    """Schema for session messages list."""

    session_id: int
    messages: List[TutorMessageResponse]
    total: int

    model_config = {"from_attributes": True}


# ── T14: Recommendations ────────────────────────────────────────────────────


class RecommendationItem(BaseModel):
    """Single recommendation item — course or practice."""

    type: str = Field(..., description="Recommendation type: course, practice")
    title: str = Field(..., description="Recommendation title")
    reason: str = Field(..., description="Why this is recommended")
    priority: str = Field("medium", description="Priority: high, medium, low")
    estimated_time: Optional[str] = Field(None, description="Estimated completion time")


class RecommendationsResponse(BaseModel):
    """Response for personalized tutor recommendations."""

    based_on: str = Field(..., description="Basis for the recommendations")
    recommendations: List[RecommendationItem] = Field(
        ..., description="List of personalized recommendations"
    )


# ── T15: Obstacle Detection ──────────────────────────────────────────────────


class ObstacleData(BaseModel):
    """Data payload for a single obstacle detection."""

    user_time: str = Field(..., description="User's time spent (human readable)")
    average_time: str = Field(..., description="Average time across all users (human readable)")
    ratio: float = Field(..., description="Ratio of user time to average time")


class ObstacleItem(BaseModel):
    """Single learning obstacle."""

    lab_id: int = Field(..., description="Lab ID where obstacle was detected")
    lab_name: str = Field(..., description="Lab name")
    type: str = Field(..., description="Obstacle type: time_exceeded, multiple_failures, stuck")
    data: ObstacleData = Field(..., description="Detection data")
    tutor_message: str = Field(..., description="AI tutor intervention message")


class ObstaclesResponse(BaseModel):
    """Response for learning obstacle detection."""

    has_obstacles: bool = Field(..., description="Whether any obstacles were detected")
    obstacles: List[ObstacleItem] = Field(
        default_factory=list, description="List of detected obstacles"
    )
