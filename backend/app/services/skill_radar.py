"""Skill radar service — multi-dimensional skill scoring engine.

Calculates scores across 9 skill dimensions using lab pass rates,
chapter completion rates, and learning activity frequency.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import (
    AnalyticsEvent,
    Chapter,
    Course,
    Lab,
    LabSubmission,
    LearningProgress,
    UserSkillScore,
)

logger = logging.getLogger(__name__)

# ── Skill dimension definitions ───────────────────────────────────────────────
# Each dimension maps to: (Chinese label, list of course IDs)
SKILL_DIMENSIONS: dict[str, tuple[str, list[int]]] = {
    "python": ("Python基础", [5, 6]),  # Phase 1,2
    "math": ("AI数学直觉", [6]),  # Phase 2
    "ml": ("机器学习", [7]),  # Phase 3
    "dl": ("深度学习", [8]),  # Phase 4
    "llm": ("LLM大模型", [9]),  # Phase 5
    "engineering": ("AI工程化", [10]),  # Phase 6
    "coding_harness": ("AI辅助开发", []),  # 新模块，暂无course_id
    "ai_application": ("AI应用实战", []),  # 新模块
    "ai_strategy": ("AI产品与策略", []),  # 新模块
}

# Weights for each sub-component of the skill score
WEIGHT_LAB_PASS = 0.60
WEIGHT_CHAPTER_COMPLETION = 0.25
WEIGHT_ACTIVITY = 0.15

# Activity bonus constants (mapped to 0-100 scale for the weighted formula)
ACTIVITY_BONUS_7D = 100.0
ACTIVITY_BONUS_30D = 50.0
ACTIVITY_BONUS_NONE = 0.0


class SkillRadarService:
    """Computes and persists multi-dimensional skill scores for users."""

    # ── Public API ──────────────────────────────────────────────────────────

    @staticmethod
    def calculate_skill_score(user_id: int, dimension: str, db: Session) -> float:
        """Compute a single dimension's skill score (0-100).

        Scoring rules:
          1. Lab pass rate (weight 60%): best-score-per-lab average across
             labs in the dimension's associated courses.
          2. Chapter completion rate (weight 25%): completed / total chapters
             in the dimension's associated courses.
          3. Activity bonus (weight 15%): based on recent learning events
             - Last 7 days  → 100 (full 15 points)
             - Last 30 days → 50  (7.5 points)
             - No activity   → 0

        Returns a float in [0, 100].
        """
        dim_info = SKILL_DIMENSIONS.get(dimension)
        if dim_info is None:
            logger.warning("Unknown skill dimension: %s", dimension)
            return 0.0

        _label, course_ids = dim_info

        # Dimensions with no courses get activity-only scores
        if not course_ids:
            activity_score = SkillRadarService._compute_activity_score(user_id, db)
            return round(WEIGHT_ACTIVITY * activity_score, 1)

        lab_pass_rate = SkillRadarService._compute_lab_pass_rate(user_id, course_ids, db)
        chapter_completion_rate = SkillRadarService._compute_chapter_completion_rate(
            user_id, course_ids, db
        )
        activity_score = SkillRadarService._compute_activity_score(user_id, db)

        score = (
            WEIGHT_LAB_PASS * lab_pass_rate
            + WEIGHT_CHAPTER_COMPLETION * chapter_completion_rate
            + WEIGHT_ACTIVITY * activity_score
        )

        return round(min(score, 100.0), 1)

    @staticmethod
    def get_skill_radar(user_id: int, db: Session) -> dict:
        """Build the full skill radar payload for a user.

        Returns a dict matching the SkillRadarResponse schema:
        {
            "user_id": 1,
            "skills": {"python": {"score": 85, "label": "Python基础", "trend": "+15"}, ...},
            "overall_score": 45.2,
            "weakest": ["llm", "engineering"],
            "strongest": ["python", "math"],
            "updated_at": "ISO datetime"
        }
        """
        # Fetch previous scores for trend calculation
        prev_scores: dict[str, float] = {}
        prev_records = (
            db.query(UserSkillScore)
            .filter(UserSkillScore.user_id == user_id)
            .all()
        )
        for rec in prev_records:
            prev_scores[rec.dimension] = rec.score

        skills: dict = {}
        scores_list: list[tuple[str, float]] = []

        for dim_key, (label, _course_ids) in SKILL_DIMENSIONS.items():
            current_score = SkillRadarService.calculate_skill_score(user_id, dim_key, db)
            prev = prev_scores.get(dim_key)
            if prev is not None:
                diff = round(current_score - prev, 1)
                trend = f"+{diff}" if diff > 0 else str(diff) if diff < 0 else "0"
            else:
                trend = "0"

            skills[dim_key] = {
                "score": current_score,
                "label": label,
                "trend": trend,
            }
            scores_list.append((dim_key, current_score))

        # Sort by score for weakest/strongest
        sorted_dims = sorted(scores_list, key=lambda x: x[1])
        weakest = [d[0] for d in sorted_dims[:3]]
        strongest = [d[0] for d in sorted_dims[-3:]][::-1]  # descending

        # Overall score: equal-weighted average of all dimensions
        total = sum(s[1] for s in scores_list)
        overall = round(total / len(scores_list), 1) if scores_list else 0.0

        # Most recent update timestamp
        latest_updated = None
        if prev_records:
            latest_updated = max(
                (r.updated_at for r in prev_records),
                default=None,
            )

        return {
            "user_id": user_id,
            "skills": skills,
            "overall_score": overall,
            "weakest": weakest,
            "strongest": strongest,
            "updated_at": latest_updated,
        }

    @staticmethod
    def refresh_skill_scores(user_id: int, db: Session) -> int:
        """Recompute and persist all skill scores to user_skill_scores.

        Call this after lab passes / chapter completions to keep scores fresh.

        Returns the number of dimensions updated.
        """
        updated = 0
        now = datetime.now(timezone.utc)

        for dim_key in SKILL_DIMENSIONS:
            score = SkillRadarService.calculate_skill_score(user_id, dim_key, db)

            existing = (
                db.query(UserSkillScore)
                .filter(
                    UserSkillScore.user_id == user_id,
                    UserSkillScore.dimension == dim_key,
                )
                .first()
            )

            if existing:
                existing.score = score
                existing.updated_at = now
            else:
                new_score = UserSkillScore(
                    user_id=user_id,
                    dimension=dim_key,
                    score=score,
                    created_at=now,
                    updated_at=now,
                )
                db.add(new_score)

            updated += 1

        db.commit()
        logger.info("Refreshed %d skill scores for user %d", updated, user_id)
        return updated

    # ── Private helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _compute_lab_pass_rate(user_id: int, course_ids: list[int], db: Session) -> float:
        """Best-score-per-lab average (0-100) across all labs in the given courses."""
        # Find all labs in the given courses
        lab_ids = [
            row[0]
            for row in (
                db.query(Lab.id)
                .join(Chapter, Lab.chapter_id == Chapter.id)
                .filter(Chapter.course_id.in_(course_ids))
                .all()
            )
        ]

        total_labs = len(lab_ids)
        if total_labs == 0:
            return 0.0

        # Get all submissions for those labs by this user
        submissions = (
            db.query(LabSubmission)
            .filter(
                LabSubmission.user_id == user_id,
                LabSubmission.lab_id.in_(lab_ids),
                LabSubmission.score.isnot(None),
            )
            .all()
        )

        if not submissions:
            return 0.0

        # Group by lab_id, take best score per lab
        best_per_lab: dict[int, float] = {}
        for sub in submissions:
            if sub.lab_id not in best_per_lab or sub.score > best_per_lab[sub.lab_id]:
                best_per_lab[sub.lab_id] = sub.score

        # Average across all labs in the courses (including labs with no submissions)

        total_best = sum(best_per_lab.values())
        return round((total_best / total_labs), 1)

    @staticmethod
    def _compute_chapter_completion_rate(
        user_id: int, course_ids: list[int], db: Session
    ) -> float:
        """Completed / total chapters ratio (0-100) in the given courses."""
        # Total chapters in these courses
        total_chapters = (
            db.query(Chapter.id)
            .filter(Chapter.course_id.in_(course_ids))
            .count()
        )

        if total_chapters == 0:
            return 0.0

        # Completed chapters for this user
        completed = (
            db.query(LearningProgress)
            .join(Chapter, LearningProgress.chapter_id == Chapter.id)
            .filter(
                LearningProgress.user_id == user_id,
                Chapter.course_id.in_(course_ids),
                LearningProgress.status == "completed",
            )
            .count()
        )

        return round((completed / total_chapters) * 100, 1)

    @staticmethod
    def _compute_activity_score(user_id: int, db: Session) -> float:
        """Activity bonus based on recent analytics events.

        Returns 100, 50, or 0 based on learning activity in the last 7/30 days.
        """
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)

        # Check for any learning-related event in the last 7 days
        recent_7d = (
            db.query(AnalyticsEvent.id)
            .filter(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.created_at >= seven_days_ago,
            )
            .limit(1)
            .first()
        )

        if recent_7d:
            return ACTIVITY_BONUS_7D

        # Check for any learning-related event in the last 30 days
        recent_30d = (
            db.query(AnalyticsEvent.id)
            .filter(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.created_at >= thirty_days_ago,
            )
            .limit(1)
            .first()
        )

        if recent_30d:
            return ACTIVITY_BONUS_30D

        return ACTIVITY_BONUS_NONE
