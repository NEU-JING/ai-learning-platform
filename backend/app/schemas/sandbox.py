"""Sandbox module Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ── Layer A: Execute ──────────────────────────────────────────────────────────


class ExecuteRequest(BaseModel):
    """AC38: Code execution request."""

    lab_id: Optional[int] = None
    code: str = Field(..., min_length=1, max_length=100000)
    language: str = Field(default="python", max_length=16)
    layer: str = Field(..., max_length=8)


class ExecuteResult(BaseModel):
    """Execution result from subprocess."""

    output: Optional[str] = None
    exit_code: Optional[int] = None
    execution_time_ms: Optional[int] = None
    error: Optional[str] = None


class ExecuteResponse(BaseModel):
    """AC38: Code execution response."""

    execution_id: int
    status: str
    result: Optional[ExecuteResult] = None
    score: Optional[float] = None
    passed: Optional[bool] = None
    feedback: Optional[str] = None


# ── Layer B: External Submit ──────────────────────────────────────────────────


class ExternalSubmitRequest(BaseModel):
    """AC39: External execution submission request."""

    lab_id: Optional[int] = None
    provider: str = Field(..., max_length=16)
    notebook_url: Optional[str] = Field(None, max_length=1024)
    expected_output: Optional[str] = Field(None, max_length=256)


class ExternalSubmitResponse(BaseModel):
    """AC39: External execution submission response."""

    submission_id: int
    status: str
    estimated_wait: Optional[str] = None
    webhook_url: Optional[str] = None


# ── Layer C: Verify ───────────────────────────────────────────────────────────


class VerifyRequest(BaseModel):
    """AC40-AC41: Verification request."""

    execution_request_id: int
    lab_id: Optional[int] = None
    model_url: Optional[str] = Field(None, max_length=1024)
    training_log: Optional[str] = None


class VerifyResponse(BaseModel):
    """AC40-AC41: Verification response."""

    verification_id: int
    status: str
    metrics: Optional[Dict[str, Any]] = None
    audit: Optional[Dict[str, Any]] = None


# ── S5: Hybrid Complete ──────────────────────────────────────────────────────


class CompleteRequest(BaseModel):
    """AC42: Hybrid flow completion request."""

    execution_request_id: int
    layers_completed: List[str] = Field(..., min_length=1)
    final_status: str = Field(default="completed", max_length=16)


class CompleteResponse(BaseModel):
    """AC42: Hybrid flow completion response."""

    status: str
    message: str


# ── S6: Provider ─────────────────────────────────────────────────────────────


class ProviderResponse(BaseModel):
    """Provider health check response."""

    id: int
    name: str
    layer: str
    is_healthy: bool
    last_health_check: Optional[datetime] = None
    failure_count: int

    model_config = {"from_attributes": True}
