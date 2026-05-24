"""Profile schemas — single source of truth (Constitution 1.2).

Task-1: settings-related schemas.
Task-2: public profile response schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# ── Public profile page response (Task-2) ───────────────────────────────────


class ProfileLabItem(BaseModel):
    """Single lab entry on public profile."""

    lab_id: int
    lab_title: str
    course_title: str
    score: float
    completed_at: Optional[datetime] = None


class ProfileCertificateItem(BaseModel):
    """Single certificate entry on public profile."""

    cert_id: str
    course_title: str
    level: str
    level_label: str
    issue_date: datetime
    verify_url: str


class ProfileVisibility(BaseModel):
    """Visibility flags for profile modules."""

    show_basic_info: bool
    show_skill_radar: bool
    show_labs: bool
    show_certificates: bool


class PublicProfileResponse(BaseModel):
    """Response for GET /api/v1/profile/{username} — public view."""

    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_public: bool
    visibility: ProfileVisibility
    skill_radar: Optional[dict] = None  # SkillRadarResponse subset, null if hidden
    labs: Optional[list[ProfileLabItem]] = None
    labs_total: Optional[int] = None
    certificates: Optional[list[ProfileCertificateItem]] = None


# ── Settings (authenticated user) ──────────────────────────────────────────


class ProfileSettingsResponse(BaseModel):
    """Response for GET/PUT /api/v1/profile/me/settings."""

    is_public: bool = False
    show_basic_info: bool = False
    show_skill_radar: bool = False
    show_labs: bool = False
    show_certificates: bool = False
    profile_url: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfileSettingsUpdate(BaseModel):
    """Request body for PUT /api/v1/profile/me/settings."""

    is_public: Optional[bool] = None
    show_basic_info: Optional[bool] = None
    show_skill_radar: Optional[bool] = None
    show_labs: Optional[bool] = None
    show_certificates: Optional[bool] = None
    display_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=200)

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: Optional[str]) -> Optional[str]:
        """Empty/whitespace-only string → null."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v


class ProfileBatchAction(BaseModel):
    """Request body for POST /api/v1/profile/me/settings/batch."""

    action: str  # "show_all" | "hide_all"

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ("show_all", "hide_all"):
            raise ValueError("action must be 'show_all' or 'hide_all'")
        return v
