"""Schemas for the Capstone/Certification API — T18."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CapstoneSubmitRequest(BaseModel):
    """Request body for submitting a capstone project."""

    level_id: int = Field(..., ge=1, description="Certification level ID")
    title: str = Field(..., min_length=1, max_length=200, description="Project title")
    description: Optional[str] = Field(None, max_length=5000, description="Project description")
    repository_url: Optional[str] = Field(None, max_length=500, description="Git repository URL")
    submission_data: Optional[Dict[str, Any]] = Field(
        None, description="Additional submission metadata"
    )


class CapstoneSubmitResponse(BaseModel):
    """Response after capstone submission."""

    id: int
    user_id: int
    level_id: int
    title: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
    submission_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: Optional[str] = None


class AIReviewResponse(BaseModel):
    """Response from AI review of a capstone submission."""

    status: str
    submission_id: int
    ai_review: Dict[str, Any]


class ReviewActionRequest(BaseModel):
    """Request body for approve/reject actions."""

    notes: Optional[str] = Field(None, max_length=2000, description="Reviewer notes")


class ReviewActionResponse(BaseModel):
    """Response after approve/reject action."""

    status: str
    submission_id: int
    reviewer_id: int
    reviewer_notes: Optional[str] = None


class CapstoneDetailResponse(BaseModel):
    """Full detail of a capstone submission for review."""

    id: int
    user_id: int
    level_id: int
    title: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
    submission_data: Optional[Dict[str, Any]] = None
    status: str
    ai_review: Optional[Dict[str, Any]] = None
    reviewer_id: Optional[int] = None
    reviewer_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
