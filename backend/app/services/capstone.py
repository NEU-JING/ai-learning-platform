"""Capstone chain service — 任务链（渐进小任务）(Phase 4 F2).

- 渐进小任务 + 即时自动评分（复用 CodeGrader）
- 证据卡自动生成（零整理、零人工评审）
- 链完成 → 发 XP + 徽章 + 触发 L1 判定
"""

from sqlalchemy.orm import Session

from app.models import (
    Badge,
    CapstoneAttempt,
    CapstoneChain,
    CapstoneTask,
    XpEvent,
)
from app.services import gamification as gm
from app.services.grader import CodeGrader


def list_chains(db: Session, only_active: bool = True) -> list[dict]:
    query = db.query(CapstoneChain)
    if only_active:
        query = query.filter(CapstoneChain.is_active.is_(True))
    return [
        {"id": c.id, "code": c.code, "title": c.title, "description": c.description,
         "skill_tags": c.skill_tags or []}
        for c in query.all()
    ]


def get_chain(db: Session, chain_id: int) -> CapstoneChain | None:
    return db.query(CapstoneChain).filter(CapstoneChain.id == chain_id).first()


def get_tasks(db: Session, chain_id: int) -> list[dict]:
    tasks = (
        db.query(CapstoneTask)
        .filter(CapstoneTask.chain_id == chain_id)
        .order_by(CapstoneTask.seq)
        .all()
    )
    return [
        {"id": t.id, "seq": t.seq, "title": t.title, "scenario": t.scenario,
         "test_cases": t.test_cases or []}
        for t in tasks
    ]


def _is_task_passed(db: Session, user_id: int, task_id: int) -> bool:
    a = (
        db.query(CapstoneAttempt)
        .filter_by(user_id=user_id, task_id=task_id)
        .first()
    )
    return a is not None and bool(a.passed)


def get_next_task(db: Session, user_id: int, chain_id: int) -> dict | None:
    """返回用户当前应做的下一任务（seq 最小未通过）。"""
    tasks = get_tasks(db, chain_id)
    for t in tasks:
        if not _is_task_passed(db, user_id, t["id"]):
            return t
    return None  # 链已完成


def submit_task(
    db: Session,
    user_id: int,
    task_id: int,
    code: str,
    timeout: int = 30,
) -> dict:
    """提交任务：自动评分 → 写 attempt → 通过则发 XP + 检查链完成。"""
    task = db.query(CapstoneTask).filter(CapstoneTask.id == task_id).first()
    if task is None:
        return {"status": "not_found"}
    chain = get_chain(db, task.chain_id)
    if chain is None or not chain.is_active:
        return {"status": "chain_inactive"}

    # 幂等：已通过不重复评分/发 XP
    already = (
        db.query(CapstoneAttempt)
        .filter_by(user_id=user_id, task_id=task_id)
        .first()
    )
    if already is not None and already.passed:
        return {"status": "already_passed"}

    # 自动评分（mockable：测试注入）
    grading = _grade(db, user_id, task, code, timeout)
    passed = bool(grading["passed"]) and float(grading["score"]) >= float(task.pass_threshold)

    attempt = already or CapstoneAttempt(
        user_id=user_id, task_id=task_id, started_at=_now()
    )
    attempt.status = "completed" if passed else "failed"
    attempt.score = float(grading["score"])
    attempt.passed = passed
    attempt.output = str(grading.get("feedback", ""))
    db.add(attempt)
    db.commit()

    result = {"status": "passed" if passed else "failed", "task_id": task_id}
    if not passed:
        result["feedback"] = grading.get("feedback", "")
        return result

    # 通过 → 发任务 XP
    xp_res = gm.award_xp(db, user_id, "task_passed", "capstone_task", task_id, xp=task.xp_reward)
    result["xp_awarded"] = task.xp_reward if xp_res["awarded"] else 0

    # 链是否全完成
    if get_next_task(db, user_id, task.chain_id) is None:
        chain = get_chain(db, task.chain_id)
        cxp = gm.award_xp(db, user_id, "chain_completed", "capstone_chain", chain.id, xp=chain.xp_reward)
        result["chain_completed"] = True
        result["chain_xp"] = chain.xp_reward if cxp["awarded"] else 0
        gm.award_badge(db, user_id, "chain_complete", ref_id=chain.id)

    return result


def _grade(db: Session, user_id: int, task: CapstoneTask, code: str, timeout: int) -> dict:
    """评分入口 — 默认走 CodeGrader，测试可 patch。"""
    return CodeGrader.grade_in_sandbox(code, task.test_cases, timeout=timeout)


def get_evidence_card(db: Session, user_id: int, chain_id: int) -> dict | None:
    """证据卡：聚合各任务分值/结果/耗时/时间戳。零整理，自动生成。"""
    chain = get_chain(db, chain_id)
    if chain is None:
        return None
    tasks = get_tasks(db, chain_id)
    attempts = {
        t["id"]: db.query(CapstoneAttempt)
        .filter_by(user_id=user_id, task_id=t["id"])
        .first()
        for t in tasks
    }
    items = []
    all_passed = True
    for t in tasks:
        a = attempts[t["id"]]
        passed = a is not None and bool(a.passed)
        if not passed:
            all_passed = False
        items.append(
            {
                "seq": t["seq"],
                "title": t["title"],
                "score": (a.score if a else None),
                "passed": passed,
                "output": (a.output if a else None),
                "completed_at": (a.completed_at.isoformat() if a and a.completed_at else None),
            }
        )
    return {
        "chain_id": chain.id,
        "title": chain.title,
        "complete": all_passed,
        "tasks": items,
        "generated_at": _now().isoformat(),
    }


def _now():
    import datetime

    return datetime.datetime.utcnow()