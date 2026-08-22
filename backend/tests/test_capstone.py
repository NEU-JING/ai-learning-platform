"""Capstone chain service tests — 任务链评分/进度/证据卡 (Phase 4 F2)."""

from unittest.mock import patch

from app.models import CapstoneAttempt, CapstoneChain, CapstoneTask, User, XpEvent
from app.services import capstone


def _make_user(db, username="chain1"):
    u = User(username=username, email=f"{username}@test.com", password_hash="x")
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _make_chain(db, code="ml-basics", cert_level_id=None):
    chain = CapstoneChain(code=code, title="ML 入门", description="三个渐进任务",
                          xp_reward=50, cert_level_id=cert_level_id)
    db.add(chain)
    db.commit()
    db.refresh(chain)
    for i, (title, tc) in enumerate(
        [("写函数", [{"test": "x"}]), ("修 bug", [{"test": "y"}]), ("跑模型", [{"test": "z"}])], start=1
    ):
        db.add(CapstoneTask(chain_id=chain.id, seq=i, title=title, scenario=f"任务{i}",
                            test_cases=tc, xp_reward=10))
    db.commit()
    return chain


class TestSubmitTask:
    def test_passed_task_records_attempt_and_xp(self, test_db):
        user = _make_user(test_db)
        chain = _make_chain(test_db)
        task = test_db.query(CapstoneTask).filter_by(chain_id=chain.id, seq=1).first()
        with patch("app.services.capstone._grade",
                   return_value={"passed": True, "score": 90.0, "test_results": [], "feedback": "OK"}):
            r = capstone.submit_task(test_db, user.id, task.id, "print('hi')")
        assert r["status"] == "passed"
        assert r["xp_awarded"] == 10
        a = test_db.query(CapstoneAttempt).filter_by(user_id=user.id, task_id=task.id).first()
        assert a.passed is True
        assert a.score == 90.0
        assert test_db.query(XpEvent).filter_by(user_id=user.id).count() == 1

    def test_submit_task_is_idempotent(self, test_db):
        user = _make_user(test_db)
        chain = _make_chain(test_db)
        task = test_db.query(CapstoneTask).filter_by(chain_id=chain.id, seq=1).first()
        with patch("app.services.capstone._grade",
                   return_value={"passed": True, "score": 100.0, "test_results": [], "feedback": "OK"}):
            capstone.submit_task(test_db, user.id, task.id, "code")
            r2 = capstone.submit_task(test_db, user.id, task.id, "code")
        assert r2["status"] == "already_passed"
        assert test_db.query(XpEvent).filter_by(user_id=user.id).count() == 1

    def test_failed_task_no_xp(self, test_db):
        user = _make_user(test_db)
        chain = _make_chain(test_db)
        task = test_db.query(CapstoneTask).filter_by(chain_id=chain.id, seq=1).first()
        with patch("app.services.capstone._grade",
                   return_value={"passed": False, "score": 30.0, "test_results": [], "feedback": "错"}):
            r = capstone.submit_task(test_db, user.id, task.id, "wrong")
        assert r["status"] == "failed"
        assert test_db.query(XpEvent).filter_by(user_id=user.id).count() == 0
        a = test_db.query(CapstoneAttempt).filter_by(user_id=user.id, task_id=task.id).first()
        assert a.passed is False

    def test_returns_feedback_on_failure(self, test_db):
        user = _make_user(test_db)
        chain = _make_chain(test_db)
        task = test_db.query(CapstoneTask).filter_by(chain_id=chain.id, seq=1).first()
        with patch("app.services.capstone._grade",
                   return_value={"passed": False, "score": 10.0, "test_results": [], "feedback": "语法错"}):
            r = capstone.submit_task(test_db, user.id, task.id, "bad(")
        assert r["feedback"] == "语法错"


class TestChainCompletion:
    def test_completing_all_tasks_triggers_chain_xp_and_evidence(self, test_db):
        user = _make_user(test_db)
        chain = _make_chain(test_db)
        tasks = test_db.query(CapstoneTask).filter_by(chain_id=chain.id).order_by(CapstoneTask.seq).all()
        with patch("app.services.capstone._grade",
                   return_value={"passed": True, "score": 100.0, "test_results": [], "feedback": "OK"}):
            last = None
            for t in tasks:
                last = capstone.submit_task(test_db, user.id, t.id, "code")
        assert last["chain_completed"] is True
        assert last["chain_xp"] == 50
        # 3 任务 + 链完成 = 4 条 XP 事件
        assert test_db.query(XpEvent).filter_by(user_id=user.id).count() == 4
        # 证据卡
        card = capstone.get_evidence_card(test_db, user.id, chain.id)
        assert card["complete"] is True
        assert len(card["tasks"]) == 3

    def test_get_next_task_unlocks_sequentially(self, test_db):
        user = _make_user(test_db)
        chain = _make_chain(test_db)
        nxt = capstone.get_next_task(test_db, user.id, chain.id)
        assert nxt["seq"] == 1
        tasks = test_db.query(CapstoneTask).filter_by(chain_id=chain.id).order_by(CapstoneTask.seq).all()
        with patch("app.services.capstone._grade",
                   return_value={"passed": True, "score": 100.0, "test_results": [], "feedback": "OK"}):
            capstone.submit_task(test_db, user.id, tasks[0].id, "code")
        nxt2 = capstone.get_next_task(test_db, user.id, chain.id)
        assert nxt2["seq"] == 2

class TestSequentialLock:
    def test_cannot_skip_to_later_task(self, test_db):
        """跳过前置任务直接提交后续任务 → 被拒绝（locked），不发 XP。"""
        user = _make_user(test_db)
        chain = _make_chain(test_db)
        task3 = test_db.query(CapstoneTask).filter_by(chain_id=chain.id, seq=3).first()
        with patch("app.services.capstone._grade",
                   return_value={"passed": True, "score": 100.0, "test_results": [], "feedback": "OK"}):
            r = capstone.submit_task(test_db, user.id, task3.id, "code")
        assert r["status"] == "locked"
        assert "前面" in r["feedback"]
        assert test_db.query(XpEvent).filter_by(user_id=user.id).count() == 0


class TestFirstTaskBoundary:
    def test_first_task_allowed_without_prev(self, test_db):
        """首任务(seq=1)无前置 → 可直接正常提交（reviewer 建议补的边界测试）。"""
        user = _make_user(test_db)
        chain = _make_chain(test_db)
        task1 = test_db.query(CapstoneTask).filter_by(chain_id=chain.id, seq=1).first()
        with patch("app.services.capstone._grade",
                   return_value={"passed": True, "score": 100.0, "test_results": [], "feedback": "OK"}):
            r = capstone.submit_task(test_db, user.id, task1.id, "code")
        assert r["status"] == "passed"
        assert r["xp_awarded"] == 10
