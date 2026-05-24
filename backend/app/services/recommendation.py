"""Recommendation Engine — V3 personalized learning content recommendations.

Core algorithm:
  Score = 0.35 × weakness + 0.20 × freshness + 0.25 × path_priority
        + 0.10 × collaborative + 0.10 × time_decay

Handles cold-start gracefully: new users with no data get sensible defaults.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    AnalyticsEvent,
    Chapter,
    Course,
    Lab,
    LabSubmission,
    LearningPathModule,
    LearningProgress,
    UserSettings,
)
from app.services.skill_radar import SKILL_DIMENSIONS, SkillRadarService

logger = logging.getLogger(__name__)

# ── Scoring weights ──────────────────────────────────────────────────────────
W_WEAKNESS = 0.35
W_FRESHNESS = 0.20
W_PATH_PRIORITY = 0.25
W_COLLABORATIVE = 0.10
W_TIME_DECAY = 0.10

# Path requirement → numeric priority score
_REQUIREMENT_SCORE = {
    "required": 1.0,
    "recommended": 0.5,
    "optional": 0.2,
}

# Chapter-related analytics event types
_CHAPTER_EVENT_TYPES = {"chapter_view", "chapter_start", "chapter_complete"}


class RecommendationService:
    """Personalized learning recommendation engine.

    All public methods are @staticmethod and receive a SQLAlchemy Session.
    Designed for defence-in-depth: every method handles missing data gracefully.
    """

    # ── Public API ──────────────────────────────────────────────────────────

    @staticmethod
    def get_continue_learning(user_id: int, db: Session) -> dict | None:
        """Return the last position the user left off.

        Returns a dict with course_id, course_title, chapter_id, chapter_title,
        progress_pct, and last_accessed_at — or None for a brand-new user.
        """
        last_progress = (
            db.query(LearningProgress)
            .filter(LearningProgress.user_id == user_id)
            .order_by(LearningProgress.last_accessed_at.desc())
            .first()
        )

        if not last_progress:
            return None

        chapter = last_progress.chapter
        if not chapter:
            return None

        course = chapter.course
        if not course:
            return None

        # Compute progress percentage for the course
        total_chapters = (
            db.query(func.count(Chapter.id)).filter(Chapter.course_id == course.id).scalar()
        ) or 0

        completed = (
            db.query(func.count(LearningProgress.id))
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.status == "completed",
                LearningProgress.chapter_id.in_(
                    db.query(Chapter.id).filter(Chapter.course_id == course.id)
                ),
            )
            .scalar()
        ) or 0

        progress_pct = round((completed / total_chapters) * 100, 1) if total_chapters > 0 else 0

        last_accessed = last_progress.last_accessed_at
        return {
            "course_id": course.id,
            "course_title": course.title,
            "course_cover": course.cover_image,
            "chapter_id": chapter.id,
            "chapter_title": chapter.title,
            "progress_pct": progress_pct,
            "last_accessed_at": last_accessed.isoformat() if last_accessed else None,
        }

    @staticmethod
    def get_daily_recommendations(
        user_id: int,
        db: Session,
        limit: int = 3,
    ) -> list[dict]:
        """Return top-N recommended chapters for today.

        Scores every uncompleted chapter via compute_recommendation_score()
        and returns the highest-ranked ones with human-readable reasons.
        """
        # Collect IDs of already-completed chapters
        completed_ids = {
            row[0]
            for row in db.query(LearningProgress.chapter_id)
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.status == "completed",
            )
            .all()
        }

        # Fetch all published chapters
        all_chapters = (
            db.query(Chapter)
            .join(Course, Chapter.course_id == Course.id)
            .filter(Course.is_published == True)  # noqa: E712
            .all()
        )

        incomplete = [ch for ch in all_chapters if ch.id not in completed_ids]

        if not incomplete:
            return []

        # Score and sort
        scored: list[dict] = []
        for ch in incomplete:
            score = RecommendationService.compute_recommendation_score(user_id, ch.id, db)
            explanation = RecommendationService._explain_recommendation(user_id, ch.id, db)
            scored.append(
                {
                    "chapter_id": ch.id,
                    "title": ch.title,
                    "course_id": ch.course_id,
                    "course_title": ch.course.title if ch.course else "",
                    "course_cover": ch.course.cover_image if ch.course else None,
                    "score": round(score, 4),
                    "reason": explanation["primary_reason"],
                    "reason_detail": explanation["detail"],
                    "component_scores": explanation["scores"],
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    @staticmethod
    def get_post_lab_recommendations(
        user_id: int,
        lab_id: int,
        db: Session,
    ) -> list[dict]:
        """Generate recommendations after a lab attempt.

        - Passed  → recommend next chapter + optional reinforcement
        - Failed  → recommend review chapters + retry suggestion
        """
        latest_sub = (
            db.query(LabSubmission)
            .filter(
                LabSubmission.user_id == user_id,
                LabSubmission.lab_id == lab_id,
            )
            .order_by(LabSubmission.created_at.desc())
            .first()
        )

        if not latest_sub:
            return []

        lab = db.query(Lab).filter(Lab.id == lab_id).first()
        if not lab:
            return []

        chapter = lab.chapter
        if not chapter:
            return []

        course = chapter.course
        recommendations: list[dict] = []

        if latest_sub.passed:
            # ── Passed: next chapter + reinforcement ──
            next_chapter = (
                db.query(Chapter)
                .filter(
                    Chapter.course_id == chapter.course_id,
                    Chapter.order_index > chapter.order_index,
                )
                .order_by(Chapter.order_index)
                .first()
            )

            if next_chapter:
                recommendations.append(
                    {
                        "chapter_id": next_chapter.id,
                        "title": next_chapter.title,
                        "course_id": next_chapter.course_id,
                        "course_title": course.title if course else "",
                        "course_cover": course.cover_image if course else None,
                        "reason": "继续下一章",
                        "reason_detail": "实验通过！继续学习同一课程的下一章节",
                        "score": 1.0,
                        "recommendation_type": "next_chapter",
                    }
                )

            # Reinforcement: top daily rec from weakest area
            daily_recs = RecommendationService.get_daily_recommendations(user_id, db, limit=1)
            for rec in daily_recs:
                rec["recommendation_type"] = "reinforcement"
                rec["reason"] = "强化练习"
                rec["reason_detail"] = "薄弱项强化推荐"
                recommendations.append(rec)
        else:
            # ── Failed: review + retry ──
            if course:
                same_course_chapters = (
                    db.query(Chapter)
                    .filter(
                        Chapter.course_id == course.id,
                        Chapter.id != chapter.id,
                    )
                    .order_by(Chapter.order_index)
                    .limit(2)
                    .all()
                )
                for ch in same_course_chapters:
                    recommendations.append(
                        {
                            "chapter_id": ch.id,
                            "title": ch.title,
                            "course_id": ch.course_id,
                            "course_title": course.title,
                            "course_cover": course.cover_image,
                            "reason": "建议复习",
                            "reason_detail": "实验未通过，建议复习相关章节后再尝试",
                            "score": 0.9,
                            "recommendation_type": "review",
                        }
                    )

            # Retry entry
            recommendations.append(
                {
                    "chapter_id": chapter.id,
                    "title": f"重试: {chapter.title}",
                    "course_id": chapter.course_id,
                    "course_title": course.title if course else "",
                    "course_cover": course.cover_image if course else None,
                    "reason": "重新挑战",
                    "reason_detail": "复习后重新挑战本实验",
                    "score": 0.8,
                    "recommendation_type": "retry",
                }
            )

        return recommendations

    @staticmethod
    def get_learning_coach_advice(user_id: int, db: Session) -> dict:
        """AI learning coach advice for the Dashboard widget.

        Returns weekly hours, streak, weakest dimension, personalized advice
        text, and recommended chapters.
        """
        radar = SkillRadarService.get_skill_radar(user_id, db)

        weakest_dims = radar.get("weakest", [])
        weakest_dim: str | None = weakest_dims[0] if weakest_dims else None
        weakest_score: float = 0.0

        if weakest_dim and weakest_dim in radar.get("skills", {}):
            weakest_score = float(
                radar["skills"][weakest_dim].get("score", 0)
                if isinstance(radar["skills"][weakest_dim], dict)
                else 0
            )

        weekly_hours, hours_trend = RecommendationService._compute_weekly_hours(user_id, db)
        streak_days = RecommendationService._compute_streak(user_id, db)
        advice = RecommendationService._generate_advice_text(weakest_dim, weakest_score, radar)
        recommended = RecommendationService.get_daily_recommendations(user_id, db, limit=3)

        return {
            "weekly_hours": weekly_hours,
            "hours_trend": hours_trend,
            "weakest_dimension": weakest_dim,
            "weakest_score": weakest_score,
            "streak_days": streak_days,
            "advice": advice,
            "recommended_chapters": recommended,
        }

    @staticmethod
    def compute_recommendation_score(
        user_id: int,
        chapter_id: int,
        db: Session,
    ) -> float:
        """Core algorithm — compute the recommendation score for one chapter.

        Returns a float in [0, 1] (higher = more recommended).
        """
        weakness = RecommendationService._compute_weakness(user_id, chapter_id, db)
        freshness = RecommendationService._compute_freshness(user_id, chapter_id, db)
        path_priority = RecommendationService._compute_path_priority(user_id, chapter_id, db)
        collaborative = RecommendationService._compute_collaborative(user_id, chapter_id, db)
        time_decay = RecommendationService._compute_time_decay(user_id, chapter_id, db)

        return (
            W_WEAKNESS * weakness
            + W_FRESHNESS * freshness
            + W_PATH_PRIORITY * path_priority
            + W_COLLABORATIVE * collaborative
            + W_TIME_DECAY * time_decay
        )

    # ── Private: score components ───────────────────────────────────────────

    @staticmethod
    def _compute_weakness(user_id: int, chapter_id: int, db: Session) -> float:
        """Weakness score 0-1.  Higher = chapter belongs to a weaker skill area.

        weakness = (100 - skill_score) / 100, averaged across dimensions the
        chapter's course maps to.
        """
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            return 0.5

        dims = RecommendationService._get_course_dimensions(chapter.course_id)
        if not dims:
            return 0.5  # neutral for chapters outside the 6-phase system

        total = 0.0
        for dim in dims:
            score = SkillRadarService.calculate_skill_score(user_id, dim, db)
            total += (100.0 - score) / 100.0

        return round(total / len(dims), 4)

    @staticmethod
    def _compute_freshness(user_id: int, chapter_id: int, db: Session) -> float:
        """Content freshness 0-1.  Higher = user hasn't seen this chapter much.

        Never visited → 1.0
        Visited n times → 1 / (1 + n)
        """
        # Query chapter-related analytics events for this user, then filter in
        # Python to avoid SQL-dialect-specific JSON extraction issues.
        raw_events = (
            db.query(AnalyticsEvent.event_data)
            .filter(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.event_type.in_(_CHAPTER_EVENT_TYPES),
            )
            .all()
        )

        visit_count = 0
        target = str(chapter_id)
        for (event_data,) in raw_events:
            if not event_data:
                continue
            chapter_val = event_data.get("chapter_id") if isinstance(event_data, dict) else None
            if chapter_val is not None and str(chapter_val) == target:
                visit_count += 1

        if visit_count == 0:
            return 1.0
        return round(1.0 / (1.0 + visit_count), 4)

    @staticmethod
    def _compute_path_priority(user_id: int, chapter_id: int, db: Session) -> float:
        """Path priority 0-1 based on the user's learning path.

        Looks up the chapter's course in learning_path_modules for the user's
        active learning_path.  Courses not in the path get 0.1 baseline.
        """
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

        if not user_settings or not user_settings.learning_path:
            return 0.5  # no path configured → neutral

        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            return 0.0

        module = (
            db.query(LearningPathModule)
            .filter(
                LearningPathModule.path_id == user_settings.learning_path,
                LearningPathModule.course_id == chapter.course_id,
            )
            .first()
        )

        if not module:
            return 0.1  # course not in user's path

        return _REQUIREMENT_SCORE.get(module.requirement, 0.1)

    @staticmethod
    def _compute_collaborative(user_id: int, chapter_id: int, db: Session) -> float:
        """Collaborative-filtering score 0-1.

        Finds similar users (same path + industry + language) and returns the
        fraction who have completed at least one chapter in this course.
        """
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if not user_settings:
            return 0.0

        # Build similarity filters
        filters = []
        if user_settings.learning_path:
            filters.append(UserSettings.learning_path == user_settings.learning_path)
        if user_settings.background_industry:
            filters.append(UserSettings.background_industry == user_settings.background_industry)
        if user_settings.background_language:
            filters.append(UserSettings.background_language == user_settings.background_language)

        if not filters:
            return 0.0

        # Find similar users (cap at 50 to keep it lightweight)
        similar_rows = (
            db.query(UserSettings.user_id)
            .filter(UserSettings.user_id != user_id, *filters)
            .limit(50)
            .all()
        )
        similar_ids = [row[0] for row in similar_rows]

        if not similar_ids:
            return 0.0

        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            return 0.0

        # Count how many similar users completed ≥1 chapter in this course
        similar_with_completion = (
            db.query(func.count(func.distinct(LearningProgress.user_id)))
            .join(Chapter, LearningProgress.chapter_id == Chapter.id)
            .filter(
                LearningProgress.user_id.in_(similar_ids),
                Chapter.course_id == chapter.course_id,
                LearningProgress.status == "completed",
            )
            .scalar()
        ) or 0

        return round(similar_with_completion / len(similar_ids), 4)

    @staticmethod
    def _compute_time_decay(user_id: int, chapter_id: int, db: Session) -> float:
        """Time-decay factor 0-1.  Higher = longer since last access.

        decay = 1 / (1 + days_since_last_access)
        Never accessed → 1.0 (no decay).
        """
        progress = (
            db.query(LearningProgress)
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.chapter_id == chapter_id,
            )
            .first()
        )

        if not progress or not progress.last_accessed_at:
            return 1.0

        now = datetime.now(timezone.utc)
        last = progress.last_accessed_at
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)

        days = max((now - last).days, 0)
        return round(1.0 / (1.0 + days), 4)

    # ── Private: helpers ────────────────────────────────────────────────────

    @staticmethod
    def _get_course_dimensions(course_id: int) -> list[str]:
        """Return skill-dimension keys that a course maps to."""
        dims: list[str] = []
        for dim_key, (_label, course_ids) in SKILL_DIMENSIONS.items():
            if course_id in course_ids:
                dims.append(dim_key)
        return dims

    @staticmethod
    def _explain_recommendation(
        user_id: int,
        chapter_id: int,
        db: Session,
    ) -> dict:
        """Produce a human-readable explanation for why a chapter is recommended."""
        weakness = RecommendationService._compute_weakness(user_id, chapter_id, db)
        freshness = RecommendationService._compute_freshness(user_id, chapter_id, db)
        path_priority = RecommendationService._compute_path_priority(user_id, chapter_id, db)

        weighted = {
            "薄弱项加强": W_WEAKNESS * weakness,
            "新内容": W_FRESHNESS * freshness,
            "路径必修": W_PATH_PRIORITY * path_priority,
        }

        primary = max(weighted, key=weighted.get)  # type: ignore[arg-type]

        detail_map = {
            "薄弱项加强": f"该章节所属技能维度薄弱（薄弱度 {weakness:.0%}），建议重点学习",
            "新内容": "你尚未学习过该章节，新内容值得探索",
            "路径必修": f"该章节属于你学习路径中的{'必修' if path_priority >= 1.0 else '推荐'}内容",
        }

        return {
            "primary_reason": primary,
            "detail": detail_map.get(primary, ""),
            "scores": {
                "weakness": round(weakness, 4),
                "freshness": round(freshness, 4),
                "path_priority": round(path_priority, 4),
            },
        }

    @staticmethod
    def _compute_weekly_hours(user_id: int, db: Session) -> tuple[float, str]:
        """Estimate weekly learning hours and trend from analytics events.

        Each learning event ≈ 10 minutes (coarse estimate).
        """
        now = datetime.now(timezone.utc)
        this_week_start = now - timedelta(days=now.weekday())
        this_week_start = this_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        last_week_start = this_week_start - timedelta(days=7)

        def _count_learning_events(start: datetime, end: datetime) -> int:
            return (
                db.query(func.count(AnalyticsEvent.id))
                .filter(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.created_at >= start,
                    AnalyticsEvent.created_at < end,
                    AnalyticsEvent.event_type.in_(
                        {"chapter_view", "chapter_start", "chapter_complete", "lab_submit"}
                    ),
                )
                .scalar()
            ) or 0

        this_week_events = _count_learning_events(this_week_start, now)
        last_week_events = _count_learning_events(last_week_start, this_week_start)

        # ~10 minutes per event → hours
        this_week = round(this_week_events * 10 / 60, 1)
        last_week = round(last_week_events * 10 / 60, 1)

        if last_week > 0:
            diff = this_week - last_week
            trend = f"+{diff:.1f}" if diff >= 0 else f"{diff:.1f}"
        else:
            trend = "0.0"

        return this_week, trend

    @staticmethod
    def _compute_streak(user_id: int, db: Session) -> int:
        """Count consecutive days with learning activity (backwards from today)."""
        now = datetime.now(timezone.utc)

        rows = (
            db.query(AnalyticsEvent.created_at)
            .filter(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.event_type.in_(
                    {"chapter_view", "chapter_start", "chapter_complete", "lab_submit"}
                ),
            )
            .order_by(AnalyticsEvent.created_at.desc())
            .limit(365)
            .all()
        )

        if not rows:
            return 0

        active_dates: set = set()
        for (ts,) in rows:
            if ts.tzinfo is not None:
                active_dates.add(ts.date())
            else:
                active_dates.add(ts.replace(tzinfo=timezone.utc).date())

        today = now.date()
        streak = 0
        cursor = today
        if cursor not in active_dates:
            cursor = today - timedelta(days=1)

        while cursor in active_dates:
            streak += 1
            cursor -= timedelta(days=1)

        return streak

    @staticmethod
    def _generate_advice_text(
        weakest_dim: str | None,
        weakest_score: float,
        radar: dict,
    ) -> str:
        """Generate personalized Chinese-language coaching advice."""
        _DIM_LABEL: dict[str, str] = {
            "python": "Python 基础",
            "math": "AI 数学直觉",
            "ml": "机器学习",
            "dl": "深度学习",
            "llm": "LLM 大模型",
            "engineering": "AI 工程化",
            "coding_harness": "AI 辅助开发",
            "ai_application": "AI 应用实战",
            "ai_strategy": "AI 产品与策略",
        }

        if not weakest_dim:
            return "欢迎开始 AI 学习之旅！建议从 Python 基础课程入手，打好编程基础。"

        label = _DIM_LABEL.get(weakest_dim, weakest_dim)

        if weakest_score < 30:
            return (
                f"你的 {label} 部分严重不足（仅 {weakest_score} 分），"
                f"建议本周集中精力打好该领域基础。"
            )
        if weakest_score < 60:
            return (
                f"你的 {label} 部分评分偏低（{weakest_score} 分），" f"建议本周重点复习相关章节。"
            )
        if weakest_score < 80:
            return (
                f"你的 {label} 尚有提升空间（{weakest_score} 分），"
                f"适当安排复习可以帮助你更全面地掌握技能。"
            )

        # 80+ — find next-weakest dimension
        skills = radar.get("skills", {})
        sorted_dims = sorted(
            [(k, v.get("score", 0) if isinstance(v, dict) else 0) for k, v in skills.items()],
            key=lambda x: x[1],
        )
        if len(sorted_dims) > 1:
            next_dim, next_score = sorted_dims[1]
            next_label = _DIM_LABEL.get(next_dim, next_dim)
            return (
                f"你的 {label} 已经很好（{weakest_score} 分），"
                f"可以多关注 {next_label}（{next_score} 分）方面的提升。"
            )

        return "你的学习进展良好，各项技能均衡发展，继续保持！"
