"""Profile schemas — single source of truth (Constitution 1.2).

Task-1: settings-related schemas.

"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

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