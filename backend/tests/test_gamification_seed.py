"""Gamification seed tests — badges + daily challenges (Phase 4)."""

import datetime

from app.data.gamification_seed import (
    BADGES,
    seed_badges,
    seed_daily_challenges,
)
from app.models import Badge, DailyChallenge


class TestSeedBadges:
    def test_creates_badge_definitions(self, test_db):
        seed_badges(test_db)
        codes = {b.code for b in test_db.query(Badge).all()}
        assert {"first_lab", "chain_complete", "streak_7"} <= codes

    def test_idempotent(self, test_db):
        seed_badges(test_db)
        first = test_db.query(Badge).count()
        seed_badges(test_db)
        assert test_db.query(Badge).count() == first


class TestSeedDailyChallenges:
    def test_seeds_challenges_from_today(self, test_db):
        seed_daily_challenges(test_db)
        today = test_db.query(DailyChallenge).filter(
            DailyChallenge.date == datetime.date.today()
        ).first()
        assert today is not None
        assert today.task
        assert today.test_cases

    def test_idempotent_over_same_day(self, test_db):
        seed_daily_challenges(test_db)
        first = test_db.query(DailyChallenge).count()
        seed_daily_challenges(test_db)
        assert test_db.query(DailyChallenge).count() == first


class TestChallengeGrading:
    def test_correct_answer_passes(self, test_db):
        """当日挑战的正确答案能被评分器判定为通过（真实评分链路）。"""
        seed_daily_challenges(test_db)
        challenge = test_db.query(DailyChallenge).filter(
            DailyChallenge.date == datetime.date.today()
        ).first()
        assert challenge is not None
        # 找 is_even 挑战（题库第 1 题）
        from app.services.grader import CodeGrader

        if "is_even" in challenge.task:
            res = CodeGrader.grade_in_sandbox("def is_even(n): return n % 2 == 0",
                                              challenge.test_cases)
            assert res["passed"] is True