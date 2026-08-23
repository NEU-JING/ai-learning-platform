"""Skill trend tests — 技能成长趋势 (Phase 4 F6)."""

import datetime

from app.core.security import create_access_token, get_password_hash
from app.models import SkillDimension, SkillEvent, User
from app.services.radar_service import get_skill_trend

NOW = datetime.datetime.utcnow()


def _make_user(db, username="trend1"):
    u = User(username=username, email=f"{username}@test.com", password_hash="x")
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _make_dim(db, slug):
    d = SkillDimension(slug=slug, name=slug, category="hard")
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def _add_event(db, user_id, dim_id, impact, days_ago):
    db.add(
        SkillEvent(
            user_id=user_id,
            dimension_id=dim_id,
            event_type="lab_completed",
            score_impact=impact,
            created_at=NOW - datetime.timedelta(days=days_ago),
        )
    )


class TestSkillTrend:
    def test_trend_returns_weeks_ascending(self, test_db):
        user = _make_user(test_db)
        dim = _make_dim(test_db, "python")
        _add_event(test_db, user.id, dim.id, 10, 14)
        _add_event(test_db, user.id, dim.id, 20, 7)
        _add_event(test_db, user.id, dim.id, 30, 0)
        test_db.commit()
        trend = get_skill_trend(test_db, user.id, weeks=3)
        assert len(trend) == 3
        periods = [t["period"] for t in trend]
        assert periods == sorted(periods)  # 时间升序

    def test_growth_signal_recent_gt_oldest(self, test_db):
        """最近一周桶的分数应高于最早桶（成长信号）。"""
        user = _make_user(test_db)
        dim = _make_dim(test_db, "python")
        _add_event(test_db, user.id, dim.id, 10, 14)
        _add_event(test_db, user.id, dim.id, 30, 0)
        test_db.commit()
        trend = get_skill_trend(test_db, user.id, weeks=3)
        assert trend[-1]["dimensions"]["python"] >= trend[0]["dimensions"]["python"]

    def test_empty_user_returns_empty_or_zero(self, test_db):
        user = _make_user(test_db)
        _make_dim(test_db, "python")
        trend = get_skill_trend(test_db, user.id, weeks=3)
        # 无事件：早期桶分数 0，趋势存在但全 0 或空
        for t in trend:
            assert all(v == 0 for v in t["dimensions"].values())

    def test_multiple_dimensions(self, test_db):
        user = _make_user(test_db)
        d1 = _make_dim(test_db, "python")
        d2 = _make_dim(test_db, "math")
        _add_event(test_db, user.id, d1.id, 50, 0)
        _add_event(test_db, user.id, d2.id, 40, 0)
        test_db.commit()
        trend = get_skill_trend(test_db, user.id, weeks=1)
        assert "python" in trend[-1]["dimensions"]
        assert "math" in trend[-1]["dimensions"]


class TestSkillTrendAPI:
    def test_requires_auth(self, client, test_db):
        resp = client.get("/api/v1/radar/trend")
        assert resp.status_code in (401, 403)

    def test_returns_trend_with_auth(self, client, test_db):
        u = User(
            username="trendapi",
            email="trendapi@t.com",
            password_hash=get_password_hash("Pass1234"),
            is_active=True,
        )
        test_db.add(u)
        d = SkillDimension(slug="python", name="Python", category="hard")
        test_db.add(d)
        test_db.commit()
        test_db.refresh(u)
        test_db.refresh(d)
        _add_event(test_db, u.id, d.id, 40, 0)
        test_db.commit()
        token = create_access_token(data={"sub": u.id})
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/api/v1/radar/trend?weeks=2", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert "python" in data[-1]["dimensions"]
