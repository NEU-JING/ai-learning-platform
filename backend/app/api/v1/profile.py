"""Profile API routes — Task-1: settings.

Endpoints:
  GET  /api/v1/profile/me/settings         — get current user's settings
  PUT  /api/v1/profile/me/settings         — update settings (BR5 logic)
  POST /api/v1/profile/me/settings/batch   — show_all / hide_all
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.profile import (
    ProfileBatchAction,
    ProfileSettingsResponse,
    ProfileSettingsUpdate,
)
from app.services.profile_service import profile_service

router = APIRouter()


def _request_info(request: Request) -> dict:
    """Extract request metadata for analytics/observability."""
    return {
        "user_agent": request.headers.get("user-agent", ""),
        "ip_address": request.client.host if request.client else None,
        "path": request.url.path,
        "referrer": request.headers.get("referer"),
    }


# ── Settings (Task-1) ──────────────────────────────────────────────────────


@router.get("/me/settings", response_model=ProfileSettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's profile settings."""
    return profile_service.get_settings(
        db,
        user_id=current_user.id,
        username=current_user.username,
        avatar_url=current_user.avatar_url,
    )


@router.put("/me/settings", response_model=ProfileSettingsResponse)
def update_settings(
    body: ProfileSettingsUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile settings. BR5: is_public false→true auto-enables all dimensions."""
    return profile_service.update_settings(
        db,
        user_id=current_user.id,
        username=current_user.username,
        data=body,
        avatar_url=current_user.avatar_url,
        request_info=_request_info(request),
    )


@router.post("/me/settings/batch", response_model=ProfileSettingsResponse)
def batch_action(
    body: ProfileBatchAction,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Batch operation: show_all or hide_all. Returns 400 if profile not enabled."""
    result = profile_service.batch_action(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action=body.action,
        avatar_url=current_user.avatar_url,
        request_info=_request_info(request),
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="主页未开启，无法调整可见性",
        )

    return result
