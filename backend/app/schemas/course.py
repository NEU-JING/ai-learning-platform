from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

# ── Chapter ──────────────────────────────────────────────


class ChapterBase(BaseModel):
    title: str
    content: str
    order_index: int
    chapter_type: str = "text"
    duration_minutes: int = 0


class ChapterCreate(ChapterBase):
    course_id: int


class ChapterResponse(ChapterBase):
    id: int
    course_id: int
    created_at: datetime
    has_lab: bool = False
    lab: Optional["LabPublicResponse"] = None

    model_config = ConfigDict(from_attributes=True)


# ── Lab (public — no solution_code / test_cases) ─────────


class LabPublicBase(BaseModel):
    """Fields safe to expose to the frontend."""

    title: str
    description: Optional[str] = None
    starter_code: Optional[str] = None
    hints: List[str] = []
    time_limit_seconds: int = 30
    memory_limit_mb: int = 256

    @field_validator("hints", mode="before")
    @classmethod
    def parse_hints(cls, v):
        # SQLite stores JSON as string; deserialize if needed
        if isinstance(v, str):
            import json

            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            return [v] if v else []
        if v is None:
            return []
        return v


class LabPublicResponse(LabPublicBase):
    """Returned by all API endpoints — NEVER exposes solution_code or test_cases."""

    id: int
    chapter_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Lab (internal — includes sensitive fields) ───────────


class LabBase(LabPublicBase):
    """Full lab definition including sensitive fields — for internal use only."""

    solution_code: Optional[str] = None
    test_cases: List[dict] = []
    requirements: Optional[str] = None

    @field_validator("test_cases", mode="before")
    @classmethod
    def parse_test_cases(cls, v):
        # SQLite stores JSON as string; deserialize if needed
        if isinstance(v, str):
            import json

            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            return []
        if v is None:
            return []
        return v


class LabCreate(LabBase):
    chapter_id: int


class LabResponse(LabBase):
    """Full lab — only used internally by services, NEVER in API response_model."""

    id: int
    chapter_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Course ────────────────────────────────────────────────


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    level: str
    category: str
    duration_hours: int = 0
    is_published: bool = False


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    level: Optional[str] = None
    category: Optional[str] = None
    duration_hours: Optional[int] = None
    is_published: Optional[bool] = None


class CourseResponse(CourseBase):
    id: int
    order_index: int
    created_at: datetime
    updated_at: datetime
    chapters: List[ChapterResponse] = []

    model_config = ConfigDict(from_attributes=True)


class CourseListResponse(CourseBase):
    id: int
    order_index: int
    chapters_count: int = 0
    labs_count: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ── LabSubmission ────────────────────────────────────────


class LabSubmissionCreate(BaseModel):
    code: str


class LabSubmissionResponse(BaseModel):
    id: int
    user_id: int
    lab_id: int
    code: str
    output: Optional[str] = None
    status: str
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    score: Optional[float] = None
    passed: Optional[bool] = None
    test_results: Optional[list] = None
    feedback: Optional[str] = None
    created_at: datetime

    @field_validator("test_results", mode="before")
    @classmethod
    def parse_test_results(cls, v):
        if isinstance(v, str):
            import json

            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            return None
        return v

    model_config = ConfigDict(from_attributes=True)


# ── Code Execution ───────────────────────────────────────


class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: Optional[int] = 30


class CodeExecutionResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: int
