"""Code Review schemas.

T13: Code Review API
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CodeIssue(BaseModel):
    """Single code issue."""

    type: str = Field(..., description="Issue type: style, bug, performance, security")
    line: int = Field(..., description="Line number where issue occurs")
    message: str = Field(..., description="Issue description")
    suggestion: str = Field(..., description="Suggested fix")
    severity: str = Field("medium", description="Issue severity: low, medium, high, critical")


class CodeReviewDimensions(BaseModel):
    """Code review scoring dimensions (AC17)."""

    correctness: int = Field(..., ge=0, le=100, description="代码正确性")
    efficiency: int = Field(..., ge=0, le=100, description="执行效率")
    readability: int = Field(..., ge=0, le=100, description="可读性")
    style: int = Field(..., ge=0, le=100, description="代码风格")
    best_practices: int = Field(..., ge=0, le=100, description="最佳实践")


class CodeReviewCreate(BaseModel):
    """Schema for creating a code review."""

    lab_id: Optional[int] = Field(None, description="Associated lab ID")
    code_content: str = Field(..., description="Code to review")
    language: str = Field(..., description="Programming language")


class CodeReviewResponse(BaseModel):
    """Schema for code review response."""

    review_id: int
    user_id: int
    lab_id: Optional[int]
    code_content: str
    language: str
    issues: List[CodeIssue]
    overall_score: float = Field(..., ge=0, le=100)
    dimensions: CodeReviewDimensions
    summary: str
    reviewed_at: datetime

    model_config = {"from_attributes": True}


class CodeReviewListResponse(BaseModel):
    """Schema for list of code reviews."""

    reviews: List[CodeReviewResponse]
    total: int

    model_config = {"from_attributes": True}
