"""Gamification service tests — XP 幂等 / 升级 / 徽章 / streak (Phase 4)."""

import datetime

import pytest

from app.models import (
    Badge,
    DailyChallenge,
    User,
    UserBadge,
    UserXp,
    XpEvent,
)
from app.services import gamification as gm


def _make_user(db, username="gamer1"):
    user = User(username=username, email=f"{username}@test.com", password_hash="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestAwardXp:
    def test_award_xp_creates_event_and_updates_total(self, test_db):
        user = _make_user(test_db)
        result = gm.award_xp(test_db, user.id, "lab_passed", "lab", 101, xp=10)
        assert result["awarded"] is True
        assert result["level_ups"] == []
        events = test_db.query(XpEvent).filter_by(user_id=user.id).all()
        assert len(events) == 1
        assert events[0].xp == 10
        row = test_db.query(UserXp).filter_by(user_id=user.id).first()
        assert row.total_xp == 10
        assert row.level == 1

    def test_award_xp_is_idempotent(self, test_db):
        """同一行为只计一次 XP（幂等）。"""
        user = _make_user(test_db)
        gm.award_xp(test_db, user.id, "lab_passed", "lab", 101, xp=10)
        second = gm.award_xp(test_db, user.id, "lab_passed", "lab", 101, xp=10)
        assert second["awarded"] is False
        events = test_db.query(XpEvent).filter_by(user_id=user.id).count()
        assert events == 1
        assert test_db.query(UserXp).filter_by(user_id=user.id).first().total_xp == 10

    def test_level_up_crosses_threshold(self, test_db):
        """累计 XP 跨越等级门槛 → 升级。"""
        user = _make_user(test_db)
        # 假设 level 2 门槛 = 100 XP
        gm.award_xp(test_db, user.id, "task_passed", "task", 1, xp=60)
        result = gm.award_xp(test_db, user.id, "task_passed", "task", 2, xp=60)
        assert result["level_ups"] == [2]  # total=120 → 升到 2 级
        row = test_db.query(UserXp).filter_by(user_id=user.id).first()
        assert row.level == 2


class TestBadgeAward:
    def test_award_badge_once(self, test_db):
        user = _make_user(test_db)
        badge = Badge(code="first_lab", name="首个实验", icon="🏅", criteria={"type": "first_lab"})
        test_db.add(badge)
        test_db.commit()
        assert gm.award_badge(test_db, user.id, "first_lab", ref_id=101) is True
        assert gm.award_badge(test_db, user.id, "first_lab", ref_id=101) is False  # 幂等
        granted = test_db.query(UserBadge).filter_by(user_id=user.id).count()
        assert granted == 1


class TestDailyChallenge:
    def test_streak_counts_consecutive_passed_days(self, test_db):
        """今天+昨天挑战都通过 → 连续 2 天。"""
        user = _make_user(test_db)
        today = datetime.date.today()
        c_today = DailyChallenge(date=today, task="今天", xp_reward=20)
        c_yesterday = DailyChallenge(date=today - datetime.timedelta(days=1),
                                     task="昨天", xp_reward=20)
        test_db.add_all([c_today, c_yesterday])
        test_db.commit()
        gm.submit_daily_challenge(test_db, user.id, c_today.id, passed=True)
        gm.submit_daily_challenge(test_db, user.id, c_yesterday.id, passed=True)
        summary = gm.get_user_gamification(test_db, user.id)
        assert summary["daily_streak"] == 2

    def test_streak_resets_on_gap(self, test_db):
        """今天通过、前天通过、昨天未通过 → 中间断档 → streak=1（只算今天的连续）。"""
        user = _make_user(test_db)
        today = datetime.date.today()
        c_today = DailyChallenge(date=today, task="今天", xp_reward=20)
        c_2days_ago = DailyChallenge(date=today - datetime.timedelta(days=2),
                                     task="前天", xp_reward=20)
        test_db.add_all([c_today, c_2days_ago])
        test_db.commit()
        gm.submit_daily_challenge(test_db, user.id, c_today.id, passed=True)
        gm.submit_daily_challenge(test_db, user.id, c_2days_ago.id, passed=True)
        summary = gm.get_user_gamification(test_db, user.id)
        assert summary["daily_streak"] == 1  # 昨天断档，从今天往前只连续到今天

    def test_submit_passed_sends_double_xp(self, test_db):
        """每日挑战通过 → 双倍 XP（reward*2），幂等。"""
        user = _make_user(test_db)
        today = datetime.date.today()
        c = DailyChallenge(date=today, task="双倍", xp_reward=20, is_active=True)
        test_db.add(c)
        test_db.commit()
        r = gm.submit_daily_challenge(test_db, user.id, c.id, passed=True)
        assert r["xp_awarded"] == 40  # 20*2
        events = test_db.query(XpEvent).filter_by(user_id=user.id).count()
        assert events == 1
        r2 = gm.submit_daily_challenge(test_db, user.id, c.id, passed=True)
        assert r2["xp_awarded"] == 0  # 幂等，不重复发


class TestGamificationSummary:
    def test_summary_structure(self, test_db):
        user = _make_user(test_db)
        gm.award_xp(test_db, user.id, "lab_passed", "lab", 1, xp=10)
        gm.award_badge(test_db, user.id, "first_lab", ref_id=1)
        summary = gm.get_user_gamification(test_db, user.id)
        assert summary["total_xp"] == 10
        assert summary["level"] == 1
        assert summary["badges"] == ["first_lab"]
        assert "daily_streak" in summary

class TestDailyChallengeRetry:
    def test_failed_then_retry_passed_awards_xp(self, test_db):
        """首次失败、重试通过 → 正常发双倍 XP；重复通过不再发。"""
        user = _make_user(test_db)
        today = datetime.date.today()
        c = DailyChallenge(date=today, task="重试", xp_reward=20)
        test_db.add(c)
        test_db.commit()
        gm.submit_daily_challenge(test_db, user.id, c.id, passed=False)
        assert test_db.query(XpEvent).count() == 0
        r = gm.submit_daily_challenge(test_db, user.id, c.id, passed=True)
        assert r["xp_awarded"] == 40
        r2 = gm.submit_daily_challenge(test_db, user.id, c.id, passed=True)
        assert r2["xp_awarded"] == 0
        assert test_db.query(XpEvent).count() == 1
