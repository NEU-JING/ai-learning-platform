"""Test Radar skill update algorithm — T7.

Tests the time decay weight calculation and skill update from lab events.

AC覆盖:
- AC9: 自动汇总多源数据（实验完成后更新技能）
- AC10: 90天半衰期时间衰减权重算法
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.radar import SkillDimension, SkillEvent
from app.services.radar_service import SkillUpdateService


class TestTimeDecayCalculation:
    """RED phase test: Verify time decay weight calculation — AC10."""

    def test_time_decay_weight_same_day(self):
        """AC10: 当天事件的权重应该为1.0（不衰减）."""
        now = datetime.now(timezone.utc)
        weight = SkillUpdateService.calculate_time_decay_weight(now, half_life_days=90)
        assert weight == pytest.approx(1.0, rel=1e-3)

    def test_time_decay_weight_90_days(self):
        """AC10: 90天后权重应该为0.5（半衰期）."""
        now = datetime.now(timezone.utc)
        event_date = now - timedelta(days=90)
        weight = SkillUpdateService.calculate_time_decay_weight(event_date, half_life_days=90)
        assert weight == pytest.approx(0.5, rel=1e-3)

    def test_time_decay_weight_180_days(self):
        """AC10: 180天后权重应该为0.25（两个半衰期）."""
        now = datetime.now(timezone.utc)
        event_date = now - timedelta(days=180)
        weight = SkillUpdateService.calculate_time_decay_weight(event_date, half_life_days=90)
        assert weight == pytest.approx(0.25, rel=1e-3)

    def test_time_decay_weight_45_days(self):
        """AC10: 45天后权重应该约为0.707（sqrt(0.5)）."""
        now = datetime.now(timezone.utc)
        event_date = now - timedelta(days=45)
        weight = SkillUpdateService.calculate_time_decay_weight(event_date, half_life_days=90)
        expected = 0.5**0.5  # sqrt(0.5) ≈ 0.707
        assert weight == pytest.approx(expected, rel=1e-3)

    def test_time_decay_weight_minimum(self):
        """AC10: 权重应该有最小值0.1的保护."""
        now = datetime.now(timezone.utc)
        event_date = now - timedelta(days=1000)  # 很久以前的
        weight = SkillUpdateService.calculate_time_decay_weight(
            event_date, half_life_days=90, min_weight=0.1
        )
        assert weight >= 0.1

    def test_time_decay_weight_formula_correctness(self):
        """AC10: 验证公式 weight = 0.5 ^ (days / 90)."""
        now = datetime.now(timezone.utc)

        test_cases = [
            (0, 1.0),  # 0 days → 1.0
            (30, 0.5 ** (30 / 90)),  # 30 days
            (60, 0.5 ** (60 / 90)),  # 60 days
            (90, 0.5),  # 90 days → 0.5
            (270, 0.125),  # 270 days → 0.5^3
        ]

        for days, expected in test_cases:
            event_date = now - timedelta(days=days)
            weight = SkillUpdateService.calculate_time_decay_weight(event_date, half_life_days=90)
            assert weight == pytest.approx(expected, rel=1e-3), f"Failed for {days} days"


class TestSkillUpdateFromLab:
    """RED phase test: Verify skill update from lab completion — AC9."""

    def test_skill_update_from_lab_creates_event(self, test_db, test_user):
        """AC9: 实验完成后应该创建技能事件记录."""
        user_id = test_user["user"]["id"]
        lab_result = {
            "lab_id": 1,
            "lab_type": "python_basics",
            "score": 85.0,
            "course_id": 5,
            "chapter_id": 1,
        }

        SkillUpdateService.update_skill_from_lab(user_id, lab_result, test_db)

        # Verify event was created
        events = test_db.query(SkillEvent).filter_by(user_id=user_id).all()
        assert len(events) > 0

        # Verify event has correct structure
        event = events[0]
        assert event.event_type == "lab_completed"
        assert event.score_impact is not None
        assert event.user_id == user_id

    def test_skill_update_coding_thinking_dimension(self, test_db, test_user):
        """AC9: python基础实验应该更新coding_thinking维度."""
        user_id = test_user["user"]["id"]
        lab_result = {
            "lab_id": 1,
            "lab_type": "python_basics",
            "score": 90.0,
            "course_id": 5,
            "chapter_id": 1,
        }

        SkillUpdateService.update_skill_from_lab(user_id, lab_result, test_db)

        # Verify coding_thinking dimension event was created
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()
        assert dimension is not None

        event = (
            test_db.query(SkillEvent).filter_by(user_id=user_id, dimension_id=dimension.id).first()
        )
        assert event is not None
        assert event.event_type == "lab_completed"

    def test_skill_update_algorithm_dimension(self, test_db, test_user):
        """AC9: 机器学习实验应该更新algorithm_understanding维度."""
        user_id = test_user["user"]["id"]
        lab_result = {
            "lab_id": 2,
            "lab_type": "ml_algorithm",
            "score": 75.0,
            "course_id": 7,
            "chapter_id": 2,
        }

        SkillUpdateService.update_skill_from_lab(user_id, lab_result, test_db)

        # Verify algorithm_understanding dimension event was created
        dimension = test_db.query(SkillDimension).filter_by(slug="algorithm_understanding").first()
        assert dimension is not None

        event = (
            test_db.query(SkillEvent).filter_by(user_id=user_id, dimension_id=dimension.id).first()
        )
        assert event is not None
        assert event.event_type == "lab_completed"

    def test_skill_update_metadata_includes_lab_id(self, test_db, test_user):
        """AC9: 事件metadata应该包含lab_id和score."""
        user_id = test_user["user"]["id"]
        lab_result = {
            "lab_id": 42,
            "lab_type": "python_basics",
            "score": 88.0,
            "course_id": 5,
            "chapter_id": 1,
        }

        SkillUpdateService.update_skill_from_lab(user_id, lab_result, test_db)

        event = test_db.query(SkillEvent).filter_by(user_id=user_id).first()
        assert event is not None
        assert event.event_metadata is not None
        assert event.event_metadata.get("lab_id") == 42
        assert event.event_metadata.get("score") == 88.0

    def test_skill_update_score_impact_calculation(self, test_db, test_user):
        """AC9: 分数影响应该基于实验分数计算（最多10%）."""
        user_id = test_user["user"]["id"]
        lab_score = 80.0
        lab_result = {
            "lab_id": 1,
            "lab_type": "python_basics",
            "score": lab_score,
            "course_id": 5,
            "chapter_id": 1,
        }

        SkillUpdateService.update_skill_from_lab(user_id, lab_result, test_db)

        event = test_db.query(SkillEvent).filter_by(user_id=user_id).first()
        assert event is not None
        # Score impact = lab_score * 0.1 (max 10% impact per lab)
        expected_impact = lab_score * 0.1
        assert event.score_impact == pytest.approx(expected_impact, rel=1e-3)

    def test_skill_update_unknown_lab_type(self, test_db, test_user):
        """AC9: 未知的实验类型应该使用默认维度映射."""
        user_id = test_user["user"]["id"]
        lab_result = {
            "lab_id": 1,
            "lab_type": "unknown_type",
            "score": 80.0,
            "course_id": 5,
            "chapter_id": 1,
        }

        # Should not raise exception, may create event with generic dimension or skip
        result = SkillUpdateService.update_skill_from_lab(user_id, lab_result, test_db)
        # Result should indicate whether event was created
        assert isinstance(result, list)

    def test_skill_update_multiple_dimensions(self, test_db, test_user):
        """AC9: 某些实验类型应该影响多个维度."""
        user_id = test_user["user"]["id"]
        lab_result = {
            "lab_id": 3,
            "lab_type": "ml_algorithm",
            "score": 85.0,
            "course_id": 7,
            "chapter_id": 3,
        }

        SkillUpdateService.update_skill_from_lab(user_id, lab_result, test_db)

        # ml_algorithm should affect both algorithm_understanding and coding_thinking
        events = test_db.query(SkillEvent).filter_by(user_id=user_id).all()
        dimension_ids = [e.dimension_id for e in events]

        algo_dim = test_db.query(SkillDimension).filter_by(slug="algorithm_understanding").first()
        coding_dim = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        assert algo_dim.id in dimension_ids
        assert coding_dim.id in dimension_ids


class TestDimensionScoreCalculation:
    """Test weighted dimension score calculation with time decay."""

    def test_calculate_dimension_score_no_events(self, test_db, test_user):
        """没有事件时分数应该为0."""
        user_id = test_user["user"]["id"]
        dimension = test_db.query(SkillDimension).first()

        score = SkillUpdateService.calculate_dimension_score(user_id, dimension.id, test_db)
        assert score == 0.0

    def test_calculate_dimension_score_single_event(self, test_db, test_user):
        """单个事件的分数计算."""
        user_id = test_user["user"]["id"]
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        # Create a skill event
        event = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=80.0,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        score = SkillUpdateService.calculate_dimension_score(user_id, dimension.id, test_db)
        # Single event with full weight (1.0) should equal score_impact
        assert score == pytest.approx(80.0, rel=1e-3)

    def test_calculate_dimension_score_weighted_average(self, test_db, test_user):
        """多个事件的加权平均计算."""
        user_id = test_user["user"]["id"]
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        now = datetime.now(timezone.utc)

        # Create two events: one recent, one old
        recent_event = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=100.0,  # Higher score
            created_at=now,
        )
        old_event = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=50.0,  # Lower score
            created_at=now - timedelta(days=90),  # 90 days ago, weight = 0.5
        )
        test_db.add(recent_event)
        test_db.add(old_event)
        test_db.commit()

        score = SkillUpdateService.calculate_dimension_score(user_id, dimension.id, test_db)

        # Weighted average: (100 * 1.0 + 50 * 0.5) / (1.0 + 0.5) = 125 / 1.5 = 83.33
        expected = (100.0 * 1.0 + 50.0 * 0.5) / (1.0 + 0.5)
        assert score == pytest.approx(expected, rel=1e-3)

    def test_calculate_dimension_score_recent_events_weighted_more(self, test_db, test_user):
        """近期事件应该对分数有更大影响."""
        user_id = test_user["user"]["id"]
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        now = datetime.now(timezone.utc)

        # Create two events: one recent with lower score, one old with higher score
        recent_event = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=60.0,
            created_at=now,
        )
        old_event = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=100.0,
            created_at=now - timedelta(days=180),  # 180 days ago, weight = 0.25
        )
        test_db.add(recent_event)
        test_db.add(old_event)
        test_db.commit()

        score = SkillUpdateService.calculate_dimension_score(user_id, dimension.id, test_db)

        # Weighted average: (60 * 1.0 + 100 * 0.25) / (1.0 + 0.25) = 85 / 1.25 = 68
        # Recent low score should pull down the average
        expected = (60.0 * 1.0 + 100.0 * 0.25) / (1.0 + 0.25)
        assert score == pytest.approx(expected, rel=1e-3)
        # Score should be closer to recent score (60) than old score (100)
        assert score < 80  # Below average of 60 and 100


class TestEventListener:
    """Test event listener mechanism for skill updates."""

    def test_event_listener_registration(self):
        """事件监听器应该可以注册和监听."""
        from app.services.radar_service import EventListener

        listener = EventListener()
        callback_called = False

        def callback(event):
            nonlocal callback_called
            callback_called = True

        listener.on("lab_completed", callback)
        listener.emit("lab_completed", {"lab_id": 1})

        assert callback_called is True

    def test_event_listener_multiple_handlers(self):
        """同一事件可以有多个处理函数."""
        from app.services.radar_service import EventListener

        listener = EventListener()
        calls = []

        def handler1(event):
            calls.append("handler1")

        def handler2(event):
            calls.append("handler2")

        listener.on("lab_completed", handler1)
        listener.on("lab_completed", handler2)
        listener.emit("lab_completed", {"lab_id": 1})

        assert len(calls) == 2
        assert "handler1" in calls
        assert "handler2" in calls

    def test_event_listener_no_handlers(self):
        """没有处理函数的事件不应该报错."""
        from app.services.radar_service import EventListener

        listener = EventListener()
        # Should not raise
        listener.emit("unknown_event", {"data": 1})
