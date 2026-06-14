"""Profile service — business logic for public profile settings and data.

Key business rules:
  BR1: No UserProfile record = profile never enabled (privacy by default)
  BR5: is_public false→true auto-sets all four dimensions to true
  BR9: is_active=false user treated as non-existent
  Closing profile preserves dimension settings; re-enabling resets all to true
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import (
    Chapter,
    Course,
    LabSubmission,
    LearningProgress,
    User,
    UserSettings,
)
from app.models.profile_cache import ProfileCache
from app.models.user_profile import UserProfile
from app.schemas.analytics import AnalyticsEventCreate
from app.schemas.profile import ProfileSettingsUpdate
from app.services.analytics_service import AnalyticsService
from app.services.skill_radar import SkillRadarService

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
            db=db, user_id=user_id, username=username,
            is_now_public=profile.is_public, was_public=was_public,
            prev_dimensions=prev_dimensions, profile=profile,
            update_data=update_data, request_info=request_info,
        )

        return self.get_settings(db, user_id, username, avatar_url)

    def _emit_settings_events(
        self, db: Session, user_id: int, username: str,
        is_now_public: bool, was_public: bool,
        prev_dimensions: dict, profile: UserProfile,
        update_data: dict, request_info: dict | None,
    ) -> None:
        """Emit analytics events for settings changes (MAJOR fix: extracted from update_settings)."""
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

    # ── Public profile (Task-2) ────────────────────────────────────────────

    def get_public_profile(
        self, db: Session, username: str, request_info: dict | None = None
    ) -> dict:
        """Get public profile data for a given username.

        Returns dict on success, or raises an appropriate exception.
        Flow:
          1. Query User by username → not found or is_active=false → 404
          2. Query UserProfile by user_id → not found → 403
          3. Check is_public → false → 403
          4. Aggregate data and apply visibility
        """
        # Step 1: Find user
        user = db.query(User).filter(User.username == username).first()
        if user is None or not user.is_active:
            logger.info("profile_404 username=%s reason=not_found_or_inactive", username)
            return {"error": 404, "detail": "该用户不存在"}

        # Step 2: Find profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if profile is None:
            logger.info("profile_403 username=%s reason=no_profile_record", username)
            return {"error": 403, "detail": "该用户尚未公开能力主页"}

        # Step 3: Check is_public
        if not profile.is_public:
            logger.info("profile_403 username=%s reason=not_public", username)
            return {"error": 403, "detail": "该用户尚未公开能力主页"}

        # Step 4: Build response with full data, then apply visibility
        # AC43: Determine path_type for dimension highlighting
        path_type = None
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
        if user_settings and user_settings.learning_path:
            path_type = user_settings.learning_path

        response = {
            "username": user.username,
            "display_name": profile.display_name or user.username,
            "bio": profile.bio,
            "avatar_url": user.avatar_url,
            "is_public": profile.is_public,
            "visibility": {
                "show_basic_info": profile.show_basic_info,
                "show_skill_radar": profile.show_skill_radar,
                "show_labs": profile.show_labs,
                "show_certificates": profile.show_certificates,
            },
            "skill_radar": SkillRadarService.get_skill_radar(user.id, db, path_type=path_type),
            "labs": self._get_labs(db, user.id),
            "labs_total": 0,  # will be set below
            "certificates": self._get_certificates(db, user.id),
        }
        response["labs_total"] = len(response["labs"])

        # Apply visibility filtering
        response = self._apply_visibility(response, profile)

        # ── Analytics: profile_view (anonymous viewer, viewer IP from request_info) ──
        self._emit_event(
            db,
            "profile_view",
            user_id=None,
            properties={"viewed_username": username, "viewed_user_id": user.id},
            request_info=request_info,
        )
        # Observability log with anonymous viewer context

        # ── Cache: write to ProfileCache for 5 minutes ──
        try:
            existing_cache = (
                db.query(ProfileCache)
                .filter(ProfileCache.cache_key == f"public_profile:{username}")
                .first()
            )
            cache_entry = existing_cache or ProfileCache(
                user_id=user.id, cache_key=f"public_profile:{username}"
            )
            cache_entry.cached_data = response
            cache_entry.expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            if not existing_cache:
                db.add(cache_entry)
            db.commit()
        except Exception:
            logger.warning("profile_cache_write_failed username=%s", username, exc_info=True)

        return response

    @staticmethod
    def _apply_visibility(response: dict, profile: UserProfile) -> dict:
        """Enforce visibility rules at Service layer — never rely on frontend hiding.

        Per Design flow 3: hidden dimensions return null/[] instead of real data.
        """
        if not profile.show_basic_info:
            response["display_name"] = None
            response["bio"] = None
            response["avatar_url"] = None
        if not profile.show_skill_radar:
            response["skill_radar"] = None
        if not profile.show_labs:
            response["labs"] = None
            response["labs_total"] = None
        if not profile.show_certificates:
            response["certificates"] = None
        return response

    @staticmethod
    def _get_labs(db: Session, user_id: int) -> list[dict]:
        """Get passed lab submissions for a user.

        Rules:
          - Only passed submissions (passed=True)
          - Best score per lab (highest score)
          - Ordered by completed_at (created_at) DESC
        """
        # Query all passed submissions for this user
        submissions = (
            db.query(LabSubmission)
            .filter(
                LabSubmission.user_id == user_id,
                LabSubmission.passed.is_(True),
                LabSubmission.score.isnot(None),
            )
            .all()
        )

        if not submissions:
            return []

        # Group by lab_id, keep best score per lab
        best_per_lab: dict[int, LabSubmission] = {}
        for sub in submissions:
            if sub.lab_id not in best_per_lab or sub.score > best_per_lab[sub.lab_id].score:
                best_per_lab[sub.lab_id] = sub

        # Build response items with lab and course info
        result = []
        for lab_id, sub in best_per_lab.items():
            lab = sub.lab
            if lab is None:
                continue
            chapter = lab.chapter
            course = chapter.course if chapter else None

            result.append(
                {
                    "lab_id": lab.id,
                    "lab_title": lab.title,
                    "course_title": course.title if course else "未知课程",
                    "score": sub.score,
                    "completed_at": sub.created_at,
                }
            )

        # Sort by completed_at DESC
        result.sort(
            key=lambda x: x["completed_at"] or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return result

    @staticmethod
    def _get_certificates(db: Session, user_id: int) -> list[dict]:
        """Get completed courses for a user as certificate entries.

        Rules:
          - A course is "completed" when ALL its chapters have
            LearningProgress status='completed'
          - cert_id format: AI-{course_id}-{user_id}-{date}
          - verify_url: /api/v1/certificates/verify/{cert_id}

        Uses a single JOIN query to avoid N+1 per-course lookups.
        """
        from sqlalchemy import func

        # Single query: get course_id, total chapters, and completed count per course
        rows = (
            db.query(
                Course.id,
                Course.title,
                Course.level,
                func.count(Chapter.id.distinct()).label("total_chapters"),
                func.count(LearningProgress.id.distinct()).label("completed_count"),
            )
            .outerjoin(Chapter, Chapter.course_id == Course.id)
            .outerjoin(
                LearningProgress,
                (LearningProgress.chapter_id == Chapter.id)
                & (LearningProgress.user_id == user_id)
                & (LearningProgress.status == "completed"),
            )
            .group_by(Course.id)
            .all()
        )

        now = datetime.now(timezone.utc)
        result = []
        for row in rows:
            course_id, title, level, total_chapters, completed_count = row
            if total_chapters == 0 or completed_count < total_chapters:
                continue

            cert_id = f"AI-{course_id}-{user_id}-{now.strftime('%Y%m%d')}"
            level_label = _LEVEL_LABELS.get(level, "学习认证")
            verify_url = f"/api/v1/certificates/verify/{cert_id}"

            result.append(
                {
                    "cert_id": cert_id,
                    "course_title": title,
                    "level": level,
                    "level_label": level_label,
                    "issue_date": now,
                    "verify_url": verify_url,
                }
            )

        return result


# Module-level singleton (stateless, safe to share)
profile_service = ProfileService()
