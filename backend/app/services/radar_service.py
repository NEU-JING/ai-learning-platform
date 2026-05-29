"""Radar skill update service — T7.

Skill update algorithm with time decay weight calculation.

AC覆盖:
- AC9: 自动汇总多源数据（实验完成后更新技能）
- AC10: 90天半衰期时间衰减权重算法
"""

import logging
from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy import desc
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
