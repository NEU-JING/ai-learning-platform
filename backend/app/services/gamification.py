"""Gamification service — XP / 等级 / 徽章 / 每日挑战 (Phase 4 F1).

设计原则：
- 先查后插保证幂等（不盲依赖唯一约束 + rollback，避免影响外部事务）
- 只增不减：不扣 XP、不降级
- 证据来自行为，全自动
"""

import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    DailyChallenge,
    DailyChallengeAttempt,
    UserBadge,
    UserXp,
    XpEvent,
)

# 每累计 LEVEL_XP 点 XP 升一级
LEVEL_XP = 100

# 各行为 XP 奖励（点数）
LAB_XP = 20  # 单个 Lab 通过


def _get_or_create_user_xp(db: Session, user_id: int) -> UserXp:
    row = db.query(UserXp).filter(UserXp.user_id == user_id).first()
    if row is None:
        row = UserXp(user_id=user_id, total_xp=0, level=1)
        db.add(row)
    return row


def _level_for(total_xp: int) -> int:
    return total_xp // LEVEL_XP + 1


def award_xp(
    db: Session,
    user_id: int,
    action: str,
    ref_type: str,
    ref_id: int,
    xp: int,
) -> dict:
    """发放 XP（幂等：同一 user+action+ref 只计一次）。返回 {awarded, level_ups}。"""
    exists = (
        db.query(XpEvent)
        .filter_by(user_id=user_id, action=action, ref_type=ref_type, ref_id=ref_id)
        .first()
    )
    if exists is not None:
        return {"awarded": False, "level_ups": []}

    row = _get_or_create_user_xp(db, user_id)
    old_level = row.level
    row.total_xp += xp
    new_level = _level_for(row.total_xp)
    row.level = new_level

    db.add(XpEvent(user_id=user_id, action=action, ref_type=ref_type, ref_id=ref_id, xp=xp))
    try:
        db.flush()
    except IntegrityError:
        # 并发下另一请求已插入同一幂等事件 → 不双发、不抛 500
        db.rollback()
        return {"awarded": False, "level_ups": []}

    level_ups = list(range(old_level + 1, new_level + 1)) if new_level > old_level else []
    db.commit()
    return {"awarded": True, "level_ups": level_ups}


def award_badge(db: Session, user_id: int, badge_code: str, ref_id: int | None = None) -> bool:
    """发放徽章（幂等）。返回是否本次新发放。"""
    exists = db.query(UserBadge).filter_by(user_id=user_id, badge_code=badge_code).first()
    if exists is not None:
        return False
    db.add(UserBadge(user_id=user_id, badge_code=badge_code, ref_id=ref_id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return False
    return True


def submit_daily_challenge(db: Session, user_id: int, challenge_id: int, passed: bool) -> dict:
    """提交每日挑战（upsert 打卡记录）。通过则发双倍 XP（幂等）。

    幂等语义：同一用户+挑战 首次通过发 XP，重复提交不再发。
    失败后重试通过 → 视为首次通过，正常发放（不因之前失败错过双倍奖）。
    """
    challenge = db.query(DailyChallenge).filter(DailyChallenge.id == challenge_id).first()
    if challenge is None:
        return {"xp_awarded": 0, "status": "not_found"}

    attempt = (
        db.query(DailyChallengeAttempt)
        .filter_by(user_id=user_id, challenge_id=challenge_id)
        .first()
    )
    if attempt is None:
        attempt = DailyChallengeAttempt(user_id=user_id, challenge_id=challenge_id, passed=False)
        db.add(attempt)
    elif attempt.passed:
        # 已通过过：幂等，不重复发
        return {"xp_awarded": 0, "status": "already_submitted"}

    attempt.passed = passed
    db.commit()

    if not passed:
        return {"xp_awarded": 0, "status": "failed"}

    # 首次通过 → 双倍 XP（award_xp 唯一约束保证重试/并发不双发）
    result = award_xp(
        db, user_id, "daily_challenge", "daily_challenge", challenge_id, xp=challenge.xp_reward * 2
    )
    return {
        "xp_awarded": challenge.xp_reward * 2 if result["awarded"] else 0,
        "status": "passed",
    }


def _get_daily_streak(db: Session, user_id: int) -> int:
    """从今天起算的连续通过天数。今天未通过则 streak=0。"""
    rows = (
        db.query(DailyChallengeAttempt, DailyChallenge.date)
        .join(DailyChallenge, DailyChallengeAttempt.challenge_id == DailyChallenge.id)
        .filter(
            DailyChallengeAttempt.user_id == user_id,
            DailyChallengeAttempt.passed.is_(True),
        )
        .all()
    )
    passed_dates = {date_ for _, date_ in rows}
    today = datetime.date.today()
    streak = 0
    day = today
    while day in passed_dates:
        streak += 1
        day = day - datetime.timedelta(days=1)
    return streak


def get_user_gamification(db: Session, user_id: int) -> dict:
    """汇总用户游戏化状态，供前端展示。"""
    xp_row = db.query(UserXp).filter(UserXp.user_id == user_id).first()
    badges = [b.badge_code for b in db.query(UserBadge).filter(UserBadge.user_id == user_id).all()]
    return {
        "total_xp": xp_row.total_xp if xp_row else 0,
        "level": xp_row.level if xp_row else 1,
        "badges": badges,
        "daily_streak": _get_daily_streak(db, user_id),
    }
