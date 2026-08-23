"""Profile service — business logic for profile settings and data.

Key business rules:
  BR1: No UserProfile record = profile never enabled (privacy by default)
  BR5: is_public false→true auto-sets all four dimensions to true
  BR9: is_active=false user treated as non-existent
  Closing profile preserves dimension settings; re-enabling resets all to true
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.schemas.analytics import AnalyticsEventCreate
from app.schemas.profile import ProfileSettingsUpdate
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


# Dimensions that get auto-set when is_public transitions false→true
_DIMENSIONS = ("show_basic_info", "show_skill_radar", "show_labs", "show_certificates")

# Level label mapping for certificates
_LEVEL_LABELS = {
    "beginner": "入门认证",
    "intermediate": "进阶认证",
    "advanced": "高级认证",
    "expert": "专家认证",
}


def _build_profile_url(username: str) -> str:
    return f"ailp.com/p/{username}"


class ProfileService:
    """Stateless service — all methods receive db session explicitly."""

    # ── Analytics / observability helpers ──────────────────────────────────

    @staticmethod
    def _emit_event(
        db: Session,
        event_type: str,
        user_id: int | None = None,
        properties: dict | None = None,
        request_info: dict | None = None,
    ) -> None:
        """Emit a profile analytics event into DB (best-effort, never fails caller)."""
        try:
            evt = AnalyticsEventCreate(
                event=event_type,
                properties=properties or {},
            )
            AnalyticsService.ingest_events(
                db,
                events=[evt],
                user_id=user_id,
                request_info=request_info,
            )
        except Exception:
            logger.warning("Failed to emit analytics event %s", event_type, exc_info=True)

    # ── Settings (Task-1) ──────────────────────────────────────────────────

    def get_settings(
        self, db: Session, user_id: int, username: str, avatar_url: Optional[str] = None
    ) -> dict:
        """Return settings dict. If no UserProfile exists, return defaults."""
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        if profile is None:
            return {
                "is_public": False,
                "show_basic_info": False,
                "show_skill_radar": False,
                "show_labs": False,
                "show_certificates": False,
                "profile_url": _build_profile_url(username),
                "display_name": None,
                "bio": None,
                "avatar_url": avatar_url,
            }

        return {
            "is_public": profile.is_public,
            "show_basic_info": profile.show_basic_info,
            "show_skill_radar": profile.show_skill_radar,
            "show_labs": profile.show_labs,
            "show_certificates": profile.show_certificates,
            "profile_url": _build_profile_url(username),
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": avatar_url,
        }

    def update_settings(
        self,
        db: Session,
        user_id: int,
        username: str,
        data: ProfileSettingsUpdate,
        avatar_url: Optional[str] = None,
        request_info: dict | None = None,
    ) -> dict:
        """Update profile settings. Handles BR5 logic."""
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        is_new_record = profile is None
        if is_new_record:
            # First-time: create record
            profile = UserProfile(user_id=user_id)
            db.add(profile)
            db.flush()  # get the record into session

        # Track state transitions before applying changes
        was_public = profile.is_public

        # BR5: is_public false→true → auto-set all dimensions to true
        if data.is_public is True and not profile.is_public:
            for dim in _DIMENSIONS:
                setattr(profile, dim, True)

        # Track dimension changes before applying (for privacy_toggle event)
        prev_dimensions = {dim: getattr(profile, dim) for dim in _DIMENSIONS}

        # Apply incoming fields (only non-None)
        update_data = data.model_dump(exclude_unset=True)
        display_name_explicitly_set = "display_name" in update_data

        for field, value in update_data.items():
            setattr(profile, field, value)

        # Default display_name to username only on first creation when not explicitly set
        if is_new_record and not display_name_explicitly_set and profile.display_name is None:
            profile.display_name = username

        db.commit()
        db.refresh(profile)

        # ── Analytics events (MAJOR fix: extracted helper) ─────────────────
        self._emit_settings_events(
            db=db,
            user_id=user_id,
            username=username,
            is_now_public=profile.is_public,
            was_public=was_public,
            prev_dimensions=prev_dimensions,
            profile=profile,
            update_data=update_data,
            request_info=request_info,
        )

        return self.get_settings(db, user_id, username, avatar_url)

    def _emit_settings_events(
        self,
        db: Session,
        user_id: int,
        username: str,
        is_now_public: bool,
        was_public: bool,
        prev_dimensions: dict,
        profile: UserProfile,
        update_data: dict,
        request_info: dict | None,
    ) -> None:
        """Emit analytics events for settings changes (MAJOR fix: extracted from update_settings)."""  # noqa: E501
        # profile_enabled: is_public transitioned false→true
        if is_now_public and not was_public:
            self._emit_event(
                db,
                "profile_enabled",
                user_id=user_id,
                properties={"username": username},
                request_info=request_info,
            )
            logger.info("profile_enabled user_id=%s username=%s", user_id, username)

        # profile_disabled: is_public transitioned true→false
        if not is_now_public and was_public:
            self._emit_event(
                db,
                "profile_disabled",
                user_id=user_id,
                properties={"username": username},
                request_info=request_info,
            )
            logger.info("profile_disabled user_id=%s username=%s", user_id, username)

        # privacy_toggle: any dimension changed
        changed_dims = [
            dim for dim in _DIMENSIONS if getattr(profile, dim) != prev_dimensions.get(dim)
        ]
        if changed_dims:
            self._emit_event(
                db,
                "privacy_toggle",
                user_id=user_id,
                properties={"changed_dimensions": changed_dims, "username": username},
                request_info=request_info,
            )
            logger.info("privacy_toggle user_id=%s dimensions=%s", user_id, changed_dims)

        # profile_settings_update: observability log for any settings change
        logger.info(
            "profile_settings_update user_id=%s fields=%s", user_id, list(update_data.keys())
        )

    def batch_action(
        self,
        db: Session,
        user_id: int,
        username: str,
        action: str,
        avatar_url: Optional[str] = None,
        request_info: dict | None = None,
    ) -> dict:
        """Execute show_all or hide_all batch operation.

        Returns 400 if profile not enabled (no record or is_public=false).
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        if profile is None or not profile.is_public:
            return None  # Signal to API layer to return 400

        if action == "show_all":
            for dim in _DIMENSIONS:
                setattr(profile, dim, True)
        elif action == "hide_all":
            for dim in _DIMENSIONS:
                setattr(profile, dim, False)

        db.commit()
        db.refresh(profile)

        # ── Analytics event ──────────────────────────────────────────────
        self._emit_event(
            db,
            "profile_batch_action",
            user_id=user_id,
            properties={"action": action, "username": username},
            request_info=request_info,
        )
        logger.info("profile_batch_action user_id=%s action=%s", user_id, action)

        return self.get_settings(db, user_id, username, avatar_url)


profile_service = ProfileService()
