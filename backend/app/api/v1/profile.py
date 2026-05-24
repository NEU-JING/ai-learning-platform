"""Profile API routes — Task-1: settings, Task-2: public profile.

Endpoints:
  GET  /api/v1/profile/me/settings         — get current user's settings
  PUT  /api/v1/profile/me/settings         — update settings (BR5 logic)
  POST /api/v1/profile/me/settings/batch   — show_all / hide_all
  GET  /api/v1/profile/{username}          — public profile (anonymous access)
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
    PublicProfileResponse,
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


# ── Public profile (Task-2) ────────────────────────────────────────────────

@router.get("/{username}", response_model=PublicProfileResponse)
def get_public_profile(
    username: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get public profile data for a user. No auth required (anonymous access).

    Error responses:
      404: User does not exist or is inactive (BR9)
      403: User exists but has not enabled public profile
    """
    result = profile_service.get_public_profile(db, username,
                                                  request_info=_request_info(request))

    # Service returns error dict when access should be denied
    if "error" in result:
        code = result["error"]
        detail = result["detail"]
        if code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        elif code == 403:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    return result
