"""Gamification & Capstone chain API tests (Phase 4 F1/F2)."""

import datetime

from app.core.security import create_access_token, get_password_hash
from app.models import CapstoneChain, CapstoneTask, DailyChallenge, User


def _auth_user(test_db, username="gamapi"):
    user = User(username=username, email=f"{username}@x.com",
                password_hash=get_password_hash("Pass1234"), role="student", is_active=True)
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    token = create_access_token(data={"sub": user.id})
    return {"Authorization": f"Bearer {token}"}


class TestGamificationAPI:
    def test_me_returns_default_summary(self, client, test_db):
        headers = _auth_user(test_db)
        resp = client.get("/api/v1/gamification/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_xp"] == 0
        assert data["level"] == 1
        assert data["daily_streak"] == 0
        assert data["badges"] == []

    def test_me_requires_auth(self, client, test_db):
        resp = client.get("/api/v1/gamification/me")
        assert resp.status_code in (401, 403)

    def test_today_challenge_found_seeded(self, client, test_db):
        """启动 seed 后，今日挑战必然存在（题库自动填充）。"""
        headers = _auth_user(test_db)
        resp = client.get("/api/v1/gamification/daily-challenge/today", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["task"]  # 非空
        assert resp.json()["xp_reward"] > 0


class TestCapstoneAPI:
    def test_list_chains(self, client, test_db):
        headers = _auth_user(test_db)
        chain = CapstoneChain(code="c1", title="链1", xp_reward=50, is_active=True)
        test_db.add(chain)
        test_db.commit()
        resp = client.get("/api/v1/capstone/chains", headers=headers)
        assert resp.status_code == 200
        assert resp.json()[0]["title"] == "链1"