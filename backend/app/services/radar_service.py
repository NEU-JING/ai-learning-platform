"""Radar skill update service — T7.

Skill update algorithm with time decay weight calculation.

AC覆盖:
- AC9: 自动汇总多源数据（实验完成后更新技能）
- AC10: 90天半衰期时间衰减权重算法
"""

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models import UserSkillScore
from app.models.radar import SkillDimension, SkillEvent

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
    ) -> float:
        """Calculate time decay weight for an event.

        AC10: Time decay calculation with 90-day half-life.
        Formula: weight = 0.5 ^ (days_passed / half_life_days)

        Args:
            event_date: The date of the event
            half_life_days: Number of days for weight to decay to 50%
            min_weight: Minimum weight to prevent events from having zero impact

        Returns:
            The decay weight, clamped to min_weight
        """
        now = datetime.now(timezone.utc)

        # Ensure event_date has timezone info
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=timezone.utc)

        days_passed = (now - event_date).days

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
    ) -> float:
        """Calculate weighted dimension score based on skill events.

        AC10: Uses time decay weighting to prioritize recent events.

        Args:
            user_id: The user's ID
            dimension_id: The dimension's ID
            db: Database session
            limit: Maximum number of events to consider

        Returns:
            The calculated dimension score (0-100)
        """
        events = (
            db.query(SkillEvent)
            .filter(
                SkillEvent.user_id == user_id,
                SkillEvent.dimension_id == dimension_id,
                SkillEvent.score_impact.isnot(None),
            )
            .order_by(desc(SkillEvent.created_at))
            .limit(limit)
            .all()
        )

        if not events:
            return 0.0

        weighted_sum = 0.0
        weight_sum = 0.0

        for event in events:
            weight = SkillUpdateService.calculate_time_decay_weight(event.created_at)
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
        percentile = (below_count + 0.5 * equal_count) / total * 100

        return min(max(percentile, 0.0), 100.0)
