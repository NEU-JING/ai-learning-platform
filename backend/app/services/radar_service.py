"""Radar skill update service — T7.

Skill update algorithm with time decay weight calculation.

AC覆盖:
- AC9: 自动汇总多源数据（实验完成后更新技能）
- AC10: 90天半衰期时间衰减权重算法
"""

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models import UserSkillScore
from app.models.radar import SkillDimension, SkillEvent, UserSkillSnapshot

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_HALF_LIFE_DAYS = 90
DEFAULT_MIN_WEIGHT = 0.1
DEFAULT_MAX_IMPACT_PER_LAB = 10.0  # Each lab affects score by max 10%

# Lab type to dimension mapping
LAB_DIMENSION_MAPPING: dict[str, list[str]] = {
    "python_basics": ["coding_thinking"],
    "ml_algorithm": ["algorithm_understanding", "coding_thinking"],
    "dl_fundamentals": ["algorithm_understanding", "system_design"],
    "llm_prompt": ["ai_collaboration", "prompt_engineering"],
    "system_design": ["system_design", "engineering_practice"],
    "ai_application": ["ai_application", "problem_solving"],
    "data_analysis": ["data_analysis", "research_depth"],
    "ai_strategy": ["ai_strategy", "problem_solving"],
    "coding_harness": ["ai_collaboration", "engineering_practice"],
}

# Default dimension for unknown lab types
DEFAULT_DIMENSION = "coding_thinking"

# Path type to dimension highlighting mapping (T8)
PATH_HIGHLIGHT_MAPPING: dict[str, list[str]] = {
    "ai-engineer": ["coding_thinking", "system_design", "engineering_practice"],
    "ai-researcher": ["algorithm_understanding", "research_depth", "data_analysis"],
    "ai-applier": ["ai_application", "prompt_engineering", "ai_collaboration"],
    "ai-manager": ["problem_solving", "ai_collaboration", "ai_application"],
}

# Path type display names
PATH_TYPE_NAMES: dict[str, str] = {
    "ai-engineer": "AI工程师路径",
    "ai-researcher": "AI专家路径",
    "ai-applier": "AI应用者路径",
    "ai-manager": "AI管理者路径",
}


class EventListener:
    """Simple event listener for skill update events."""

    def __init__(self):
        self._handlers: dict[str, list[Callable[[Any], None]]] = {}

    def on(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """Register an event handler."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug("Registered handler for event: %s", event_type)

    def off(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """Unregister an event handler."""
        if event_type in self._handlers:
            self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler]

    def emit(self, event_type: str, event_data: Any) -> None:
        """Emit an event to all registered handlers."""
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event_data)
            except Exception as e:
                logger.error("Error in event handler for %s: %s", event_type, e)

    def once(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """Register a one-time event handler."""

        def wrapper(event_data: Any) -> None:
            self.off(event_type, wrapper)
            handler(event_data)

        self.on(event_type, wrapper)


# Global event listener instance
_event_listener = EventListener()


def get_event_listener() -> EventListener:
    """Get the global event listener instance."""
    return _event_listener


class SkillUpdateService:
    """Service for updating skill scores based on learning events."""

    @staticmethod
    def calculate_time_decay_weight(
        event_date: datetime,
        half_life_days: int = DEFAULT_HALF_LIFE_DAYS,
        min_weight: float = DEFAULT_MIN_WEIGHT,
        reference: Optional[datetime] = None,
    ) -> float:
        """Calculate time decay weight for an event.

        AC10: Time decay calculation with 90-day half-life.
        Formula: weight = 0.5 ^ (days_passed / half_life_days)

        Args:
            event_date: The date of the event
            half_life_days: Number of days for weight to decay to 50%
            min_weight: Minimum weight to prevent events from having zero impact
            reference: Optional anchor time. When provided, decay is measured
                       relative to it (used by skill trend so each week bucket is
                       scored at its own cutoff, not vs real now). Defaults to now.

        Returns:
            The decay weight, clamped to min_weight
        """
        ref = reference if reference is not None else datetime.now(timezone.utc)
        if ref.tzinfo is None:
            ref = ref.replace(tzinfo=timezone.utc)

        # Ensure event_date has timezone info
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=timezone.utc)

        days_passed = (ref - event_date).days

        # Calculate weight using the formula: 0.5 ^ (days / half_life)
        weight = 0.5 ** (days_passed / half_life_days)

        # Clamp to minimum weight
        return max(weight, min_weight)

    @staticmethod
    def update_skill_from_lab(
        user_id: int,
        lab_result: dict[str, Any],
        db: Session,
    ) -> list[SkillEvent]:
        """Update skill scores when a user completes a lab.

        AC9: Automatically update skills based on lab completion.

        Args:
            user_id: The user's ID
            lab_result: Dictionary containing lab result data:
                - lab_id: ID of the lab
                - lab_type: Type of lab (e.g., 'python_basics')
                - score: Score achieved (0-100)
                - course_id: Associated course ID
                - chapter_id: Associated chapter ID
            db: Database session

        Returns:
            List of created SkillEvent records
        """
        lab_type = lab_result.get("lab_type", "")
        lab_score = lab_result.get("score", 0.0)
        lab_id = lab_result.get("lab_id")

        # Get affected dimensions for this lab type
        affected_slugs = LAB_DIMENSION_MAPPING.get(lab_type, [DEFAULT_DIMENSION])

        created_events = []

        for dim_slug in affected_slugs:
            dimension = db.query(SkillDimension).filter(SkillDimension.slug == dim_slug).first()

            if not dimension:
                logger.warning("Dimension not found: %s", dim_slug)
                continue

            # Calculate score impact (max 10% of lab score)
            score_impact = lab_score * 0.1

            # Create skill event
            event = SkillEvent(
                user_id=user_id,
                event_type="lab_completed",
                dimension_id=dimension.id,
                score_impact=score_impact,
                event_metadata={
                    "lab_id": lab_id,
                    "score": lab_score,
                    "lab_type": lab_type,
                    "course_id": lab_result.get("course_id"),
                    "chapter_id": lab_result.get("chapter_id"),
                },
            )

            db.add(event)
            created_events.append(event)

            logger.info(
                "Created skill event: user=%s, dimension=%s, impact=%s",
                user_id,
                dim_slug,
                score_impact,
            )

        db.commit()

        # Update the actual skill scores
        for event in created_events:
            SkillUpdateService._update_user_skill_score(user_id, event.dimension_id, db)

        # Emit event for any listeners
        _event_listener.emit(
            "lab_completed",
            {
                "user_id": user_id,
                "lab_result": lab_result,
                "events": [
                    {
                        "dimension_id": e.dimension_id,
                        "score_impact": e.score_impact,
                    }
                    for e in created_events
                ],
            },
        )

        return created_events

    @staticmethod
    def calculate_dimension_score(
        user_id: int,
        dimension_id: int,
        db: Session,
        limit: int = 100,
        as_of: Optional[datetime] = None,
    ) -> float:
        """Calculate weighted dimension score based on skill events.

        AC10: Uses time decay weighting to prioritize recent events.

        Args:
            user_id: The user's ID
            dimension_id: The dimension's ID
            db: Database session
            limit: Maximum number of events to consider
            as_of: Optional cutoff — only count events at or before this time
                   (used by skill trend: score as of end of a given week)

        Returns:
            The calculated dimension score (0-100)
        """
        query = db.query(SkillEvent).filter(
            SkillEvent.user_id == user_id,
            SkillEvent.dimension_id == dimension_id,
            SkillEvent.score_impact.isnot(None),
        )
        if as_of is not None:
            query = query.filter(SkillEvent.created_at <= as_of)
        events = query.order_by(desc(SkillEvent.created_at)).limit(limit).all()

        if not events:
            return 0.0

        weighted_sum = 0.0
        weight_sum = 0.0

        for event in events:
            weight = SkillUpdateService.calculate_time_decay_weight(
                event.created_at, reference=as_of
            )
            weighted_sum += event.score_impact * weight
            weight_sum += weight

        return weighted_sum / weight_sum if weight_sum > 0 else 0.0

    @staticmethod
    def _update_user_skill_score(
        user_id: int,
        dimension_id: int,
        db: Session,
    ) -> UserSkillScore:
        """Update user's skill score for a specific dimension.

        Args:
            user_id: The user's ID
            dimension_id: The dimension's ID
            db: Database session

        Returns:
            The updated or created UserSkillScore record
        """
        # Calculate new score
        new_score = SkillUpdateService.calculate_dimension_score(user_id, dimension_id, db)
        new_score = min(new_score, 100.0)  # Cap at 100

        # Check for existing score
        existing = (
            db.query(UserSkillScore)
            .filter(
                UserSkillScore.user_id == user_id,
                UserSkillScore.dimension == str(dimension_id),
            )
            .first()
        )

        now = datetime.now(timezone.utc)

        if existing:
            existing.score = new_score
            existing.updated_at = now
            logger.debug(
                "Updated skill score: user=%s, dimension=%s, score=%s",
                user_id,
                dimension_id,
                new_score,
            )
            return existing
        else:
            # Create new score record
            # Note: UserSkillScore.dimension stores dimension_id as string
            score_record = UserSkillScore(
                user_id=user_id,
                dimension=str(dimension_id),
                score=new_score,
                created_at=now,
                updated_at=now,
            )
            db.add(score_record)
            db.commit()
            logger.debug(
                "Created skill score: user=%s, dimension=%s, score=%s",
                user_id,
                dimension_id,
                new_score,
            )
            return score_record

    @staticmethod
    def register_lab_completion_listener(callback: Callable[[dict], None]) -> None:
        """Register a callback for lab completion events.

        Args:
            callback: Function to call when lab is completed
        """
        _event_listener.on("lab_completed", callback)

    @staticmethod
    def unregister_lab_completion_listener(callback: Callable[[dict], None]) -> None:
        """Unregister a lab completion listener.

        Args:
            callback: The callback to remove
        """
        _event_listener.off("lab_completed", callback)


class RadarService:
    """T8: Service for querying radar data with path specialization.

    AC覆盖:
    - AC7: 10维技能模型落地
    - AC8: GET /api/v1/radar 端点
    - AC11: 路径特化高亮
    - AC14: percentile 和 confidence 返回
    """

    # Minimum events for maximum confidence
    MAX_CONFIDENCE_EVENTS = 10

    @staticmethod
    def get_radar(
        user_id: int,
        db: Session,
        path_type: Optional[str] = None,
    ) -> dict:
        """Get radar data for a user with optional path specialization.

        Args:
            user_id: The user's ID
            db: Database session
            path_type: Optional path type for highlighting (e.g., 'ai-engineer')

        Returns:
            Dictionary containing 10-dimension radar data with percentile and confidence
        """
        # Get all skill dimensions
        dimensions = db.query(SkillDimension).order_by(SkillDimension.id).all()

        # Calculate dimension stats for percentile
        all_dimension_scores = RadarService._get_all_user_dimension_scores(db)

        # Build dimension details
        dimension_details = []
        total_score = 0.0

        # Get highlighted dimensions for the path type
        highlighted_slugs = set()
        if path_type and path_type in PATH_HIGHLIGHT_MAPPING:
            highlighted_slugs = set(PATH_HIGHLIGHT_MAPPING[path_type])

        for dim in dimensions:
            # Calculate score for this dimension
            score = SkillUpdateService.calculate_dimension_score(user_id, dim.id, db)

            # Calculate confidence based on event count
            confidence = RadarService._calculate_confidence(user_id, dim.id, db)

            # Calculate percentile
            percentile = RadarService._calculate_percentile(
                score, all_dimension_scores.get(dim.slug, [])
            )

            # Check if this dimension should be highlighted
            highlighted = dim.slug in highlighted_slugs

            dimension_details.append(
                {
                    "slug": dim.slug,
                    "name": dim.name,
                    "score": round(score, 1),
                    "percentile": round(percentile, 1),
                    "confidence": round(confidence, 2),
                    "category": dim.category,
                    "highlighted": highlighted,
                }
            )

            total_score += score

        # Calculate overall score
        overall_score = round(total_score / len(dimensions), 1) if dimensions else 0.0

        # Get latest update time
        latest_event = (
            db.query(SkillEvent)
            .filter(SkillEvent.user_id == user_id)
            .order_by(desc(SkillEvent.created_at))
            .first()
        )
        updated_at = latest_event.created_at if latest_event else None

        return {
            "user_id": user_id,
            "dimensions": dimension_details,
            "overall_score": overall_score,
            "path_type": path_type,
            "updated_at": updated_at.isoformat() if updated_at else None,
        }

    @staticmethod
    def _calculate_confidence(user_id: int, dimension_id: int, db: Session) -> float:
        """Calculate confidence score based on event count.

        Confidence increases with more data points, up to a maximum.

        Args:
            user_id: The user's ID
            dimension_id: The dimension's ID
            db: Database session

        Returns:
            Confidence value between 0 and 1
        """
        event_count = (
            db.query(func.count(SkillEvent.id))
            .filter(
                SkillEvent.user_id == user_id,
                SkillEvent.dimension_id == dimension_id,
            )
            .scalar()
        )

        # Confidence = min(event_count / MAX_CONFIDENCE_EVENTS, 1.0)
        confidence = min(event_count / RadarService.MAX_CONFIDENCE_EVENTS, 1.0)
        return max(confidence, 0.1)  # Minimum confidence of 0.1

    @staticmethod
    def _get_all_user_dimension_scores(db: Session) -> dict[str, list[float]]:
        """Get all dimension scores across all users for percentile calculation.

        Args:
            db: Database session

        Returns:
            Dictionary mapping dimension slug to list of all user scores
        """
        # Get all skill dimensions
        dimensions = db.query(SkillDimension).all()

        scores_by_dimension: dict[str, list[float]] = {}

        for dim in dimensions:
            # Query scores for this dimension
            # UserSkillScore.dimension stores dimension_id as string
            dim_id_str = str(dim.id)
            scores = (
                db.query(UserSkillScore.score).filter(UserSkillScore.dimension == dim_id_str).all()
            )
            scores_by_dimension[dim.slug] = [s[0] for s in scores]

        return scores_by_dimension

    @staticmethod
    def _calculate_percentile(score: float, all_scores: list[float]) -> float:
        """Calculate percentile rank for a score.

        Args:
            score: The user's score
            all_scores: List of all scores for this dimension

        Returns:
            Percentile rank (0-100)
        """
        if not all_scores:
            return 50.0  # Default to median if no data

        # Count how many scores are below the user's score
        below_count = sum(1 for s in all_scores if s < score)
        equal_count = sum(1 for s in all_scores if s == score)

        # Use "nearest rank" method for percentile calculation
        # Percentile = (below_count + 0.5 * equal_count) / total_count * 100
        total = len(all_scores)
        percentile = ((below_count + 0.5 * equal_count) / total) * 100 if total > 0 else 50.0

        return min(max(percentile, 0.0), 100.0)


class SnapshotService:
    """T9: Service for creating and comparing skill snapshots.

    AC覆盖:
    - AC12: 历史版本对比功能
    """

    @staticmethod
    def create_snapshot(
        user_id: int,
        name: Optional[str],
        path_id: Optional[int],
        db: Session,
    ) -> UserSkillSnapshot:
        """Create a new skill snapshot for the user.

        Args:
            user_id: The user's ID
            name: Optional name for the snapshot
            path_id: Optional associated path ID
            db: Database session

        Returns:
            The created UserSkillSnapshot record
        """
        from datetime import datetime, timezone

        # Get current radar data to capture scores
        radar_data = RadarService.get_radar(user_id, db)

        # Build scores dictionary from dimensions
        scores = {}
        for dim in radar_data.get("dimensions", []):
            scores[dim["slug"]] = dim["score"]

        # Generate default name if not provided
        if not name:
            now = datetime.now(timezone.utc)
            name = f"快照 {now.strftime('%Y-%m-%d %H:%M')}"

        # Create snapshot record
        snapshot = UserSkillSnapshot(
            user_id=user_id,
            snapshot_name=name,
            scores=scores,
            path_id=path_id,
        )

        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        return snapshot

    @staticmethod
    def compare_with_snapshot(
        user_id: int,
        snapshot_id: int,
        db: Session,
    ) -> dict:
        """Compare current skills with a historical snapshot.

        Args:
            user_id: The user's ID
            snapshot_id: The snapshot ID to compare with
            db: Database session

        Returns:
            Dictionary containing current scores, snapshot scores, comparison, and assessment

        Raises:
            HTTPException: 404 if snapshot not found, 403 if not owned by user
        """
        from fastapi import HTTPException

        # Get the snapshot
        snapshot = db.query(UserSkillSnapshot).filter_by(id=snapshot_id).first()

        if not snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")

        # Verify ownership
        if snapshot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this snapshot")

        # Get current radar data
        current_radar = RadarService.get_radar(user_id, db)
        current_scores = {d["slug"]: d["score"] for d in current_radar.get("dimensions", [])}

        # Get snapshot scores
        snapshot_scores = snapshot.scores or {}

        # Build comparison list
        comparison = []
        all_dimensions = set(current_scores.keys()) | set(snapshot_scores.keys())

        for dim_slug in all_dimensions:
            current = current_scores.get(dim_slug, 0.0)
            snap = snapshot_scores.get(dim_slug, 0.0)
            change = current - snap

            # Determine trend
            if change > 0.1:
                trend = "up"
            elif change < -0.1:
                trend = "down"
            else:
                trend = "flat"

            comparison.append(
                {
                    "dimension": dim_slug,
                    "current": round(current, 1),
                    "snapshot": round(snap, 1),
                    "change": round(change, 1),
                    "trend": trend,
                }
            )

        # Sort by dimension name for consistency
        comparison.sort(key=lambda x: x["dimension"])

        # Generate assessment
        assessment = SnapshotService._generate_assessment(comparison)

        return {
            "current": current_scores,
            "snapshot": snapshot_scores,
            "comparison": comparison,
            "assessment": assessment,
            "snapshot_info": {
                "name": snapshot.snapshot_name,
                "date": snapshot.created_at.isoformat() if snapshot.created_at else None,
            },
        }

    @staticmethod
    def _generate_assessment(comparison: list[dict]) -> str:
        """Generate an assessment text based on comparison results.

        Args:
            comparison: List of dimension comparison results

        Returns:
            Assessment text
        """
        if not comparison:
            return "暂无技能数据"

        # Count improvements and declines
        improvements = [c for c in comparison if c["trend"] == "up"]
        declines = [c for c in comparison if c["trend"] == "down"]

        # Find biggest improvements and declines
        improvements.sort(key=lambda x: x["change"], reverse=True)
        declines.sort(key=lambda x: x["change"])

        parts = []

        if improvements:
            top_improvement = improvements[0]
            parts.append(f"{top_improvement['dimension']}提升{top_improvement['change']:.1f}分")

        if declines:
            top_decline = declines[0]
            parts.append(f"{top_decline['dimension']}下降{abs(top_decline['change']):.1f}分")

        if not parts:
            return "技能水平保持稳定"

        return "，".join(parts) + "。继续加油！"


class GapAnalysisService:
    """T10: Service for analyzing skill gaps against job requirements.

    AC覆盖:
    - AC13: 差距分析，返回当前分数与目标岗位要求差距
    """

    # Days per skill point gap (estimated)
    DAYS_PER_POINT = 2

    # Priority thresholds
    HIGH_GAP_THRESHOLD = 20.0
    MEDIUM_GAP_THRESHOLD = 10.0

    @staticmethod
    def analyze_gaps(
        user_id: int,
        target_job: str,
        db: Session,
    ) -> dict:
        """Analyze skill gaps for a user against job requirements.

        Args:
            user_id: The user's ID
            target_job: Target job title (e.g., 'ai-engineer')
            db: Database session

        Returns:
            Dictionary containing gaps, overall_readiness, and estimated_gap_days

        Raises:
            HTTPException: 404 if job requirements not found
        """
        from fastapi import HTTPException

        from app.models.radar import JobSkillRequirement

        # Get job requirements
        job_req = (
            db.query(JobSkillRequirement)
            .filter(JobSkillRequirement.job_title == target_job)
            .first()
        )

        if not job_req:
            raise HTTPException(
                status_code=404,
                detail=f"Job requirements not found for: {target_job}",
            )

        # Get current user radar data
        radar_data = RadarService.get_radar(user_id, db)
        current_scores = {d["slug"]: d["score"] for d in radar_data.get("dimensions", [])}

        # Get required skills
        required_skills = job_req.required_skills or {}

        # Calculate gaps
        gaps = []
        total_gap = 0.0
        total_required = 0.0

        for dim_slug, required_score in required_skills.items():
            current_score = current_scores.get(dim_slug, 0.0)
            gap = max(0, required_score - current_score)

            if gap > 0:
                # Determine priority
                if gap >= GapAnalysisService.HIGH_GAP_THRESHOLD:
                    priority = "high"
                elif gap >= GapAnalysisService.MEDIUM_GAP_THRESHOLD:
                    priority = "medium"
                else:
                    priority = "low"

                # Get recommended courses (placeholder for now)
                recommended_courses = GapAnalysisService._get_recommended_courses(dim_slug)

                gaps.append(
                    {
                        "dimension": dim_slug,
                        "current_score": round(current_score, 1),
                        "required_score": required_score,
                        "gap": round(gap, 1),
                        "priority": priority,
                        "recommended_courses": recommended_courses,
                    }
                )

                total_gap += gap

            total_required += required_score

        # Calculate overall readiness
        if total_required > 0:
            overall_readiness = max(0, 100 - (total_gap / total_required * 100))
        else:
            overall_readiness = 100.0

        # Estimate gap days
        estimated_gap_days = int(total_gap * GapAnalysisService.DAYS_PER_POINT)

        # Sort gaps by priority (high first) then by gap size
        priority_order = {"high": 0, "medium": 1, "low": 2}
        gaps.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["gap"]))

        return {
            "target_job": target_job,
            "target_level": job_req.job_level,
            "gaps": gaps,
            "overall_readiness": round(overall_readiness, 1),
            "estimated_gap_days": estimated_gap_days,
        }

    @staticmethod
    def _get_recommended_courses(dim_slug: str) -> list[dict]:
        """Get recommended courses for a skill dimension.

        This is a placeholder implementation that returns generic recommendations.
        In production, this should query a course-to-skill mapping table.

        Args:
            dim_slug: Dimension slug

        Returns:
            List of recommended courses
        """
        # Simple mapping for demo purposes
        course_mapping = {
            "coding_thinking": [
                {"id": 1, "name": "Python编程基础", "relevance": 0.95},
                {"id": 2, "name": "算法与数据结构", "relevance": 0.85},
            ],
            "system_design": [
                {"id": 3, "name": "系统设计基础", "relevance": 0.95},
                {"id": 4, "name": "微服务架构实践", "relevance": 0.85},
            ],
            "algorithm_understanding": [
                {"id": 5, "name": "机器学习算法", "relevance": 0.95},
                {"id": 6, "name": "深度学习原理", "relevance": 0.90},
            ],
            "ai_application": [
                {"id": 7, "name": "AI应用开发", "relevance": 0.95},
                {"id": 8, "name": "提示词工程", "relevance": 0.80},
            ],
            "data_analysis": [
                {"id": 9, "name": "数据分析基础", "relevance": 0.95},
                {"id": 10, "name": "数据可视化", "relevance": 0.85},
            ],
        }

        return course_mapping.get(dim_slug, [])


def get_skill_trend(db: Session, user_id: int, weeks: int = 8) -> list[dict]:
    """技能成长趋势 — 按周聚合各维度分数（截至每周末）。

    Phase 4 F6: 数据源 = SkillEvent（行为自动记录，零手动打点）。
    每个时间桶分数 = 截至该周末所有事件的时间衰减加权（与当前雷达同模型，
    早期事件权重低，曲线反映真实成长而非瞬时波动）。
    """
    dims = db.query(SkillDimension).order_by(SkillDimension.id).all()
    today = date.today()
    trend: list[dict] = []
    for i in range(weeks - 1, -1, -1):
        monday = (today - timedelta(days=today.weekday())) - timedelta(weeks=i)
        end_dt = datetime.combine(monday + timedelta(days=7), datetime.min.time())
        # 该周截止（含该周全部事件）；衰减锚定 end_dt，避免早期桶被人为低估
        row: dict = {"period": monday.isoformat(), "dimensions": {}}
        for dim in dims:
            score = SkillUpdateService.calculate_dimension_score(user_id, dim.id, db, as_of=end_dt)
            row["dimensions"][dim.slug] = round(score, 1)
        trend.append(row)
    return trend
