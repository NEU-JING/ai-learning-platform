"""Gamified learning database models — Phase 4.

Tables:
- xp_events:              XP 发放明细（幂等：UNIQUE(user_id, action, ref_type, ref_id)）
- user_xp:                用户累计 XP 与等级
- badges:                 徽章定义
- user_badges:            徽章发放记录（create_only）
- capstone_chains / capstone_tasks / capstone_attempts: 任务链（渐进小任务 + 评分）
- daily_challenges / daily_challenge_attempts: 每日挑战 + 打卡
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from app.models import Base, _utcnow


class XpEvent(Base):
    """单条 XP 发放记录 — 幂等依据。"""

    __tablename__ = "xp_events"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "action", "ref_type", "ref_id", name="uq_xp_events_once_per_action"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(
        String(50), nullable=False
    )  # lab_passed / task_passed / chain_completed / daily_challenge
    ref_type = Column(
        String(30), nullable=False
    )  # lab / capstone_task / capstone_chain / daily_challenge
    ref_id = Column(Integer, nullable=False)  # 关联对象 id
    xp = Column(Integer, nullable=False, default=1)  # 本次 XP 点数
    created_at = Column(DateTime, default=_utcnow)


class UserXp(Base):
    """用户累计 XP 与等级。"""

    __tablename__ = "user_xp"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    total_xp = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class Badge(Base):
    """徽章定义 — 触发条件以 JSON 描述。"""

    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(10), nullable=True)  # emoji
    criteria = Column(
        JSON, default=dict
    )  # {"type": "first_lab" | "chain_complete" | "streak_days", "value": N}
    is_active = Column(Boolean, default=True)


class UserBadge(Base):
    """徽章发放记录 — create_only。"""

    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_code", name="uq_user_badges_once"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_code = Column(String(50), nullable=False)
    awarded_at = Column(DateTime, default=_utcnow)
    ref_id = Column(Integer, nullable=True)  # 触发该徽章的关联对象


class CapstoneChain(Base):
    """任务链定义 — 一个主题下多个渐进小任务。"""

    __tablename__ = "capstone_chains"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    skill_tags = Column(JSON, default=list)  # ["numpy", "pandas", ...]
    xp_reward = Column(Integer, nullable=False, default=50)  # 链完成额外奖励 XP
    cert_level_id = Column(Integer, nullable=True, index=True)  # 关联认证等级（F3 触发）
    is_active = Column(Boolean, default=True)


class CapstoneTask(Base):
    """任务链内单个任务。"""

    __tablename__ = "capstone_tasks"
    __table_args__ = (UniqueConstraint("chain_id", "seq", name="uq_capstone_task_seq"),)

    id = Column(Integer, primary_key=True, index=True)
    chain_id = Column(Integer, ForeignKey("capstone_chains.id"), nullable=False, index=True)
    seq = Column(Integer, nullable=False)  # 1..N 顺序
    title = Column(String(200), nullable=False)
    scenario = Column(Text, nullable=False)  # 场景描述（讲"为什么做"）
    test_cases = Column(JSON, default=list)  # 评分测试用例（复用 CodeGrader）
    xp_reward = Column(Integer, nullable=False, default=10)  # 单任务通过 XP
    pass_threshold = Column(Float, nullable=False, default=70.0)


class CapstoneAttempt(Base):
    """任务提交/评分记录 — 沙箱执行结果即证据。"""

    __tablename__ = "capstone_attempts"
    __table_args__ = (UniqueConstraint("user_id", "task_id", name="uq_capstone_attempt_once"),)

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("capstone_tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(16), nullable=False, default="pending")  # pending/completed/failed
    score = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=True)
    output = Column(Text, nullable=True)  # 沙箱 stdout/结果证据
    started_at = Column(DateTime, default=_utcnow)
    completed_at = Column(DateTime, nullable=True)


class DailyChallenge(Base):
    """每日挑战定义 — 每天一个 10 分钟小任务。"""

    __tablename__ = "daily_challenges"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True)  # 某天一个挑战
    task = Column(Text, nullable=False)  # 任务描述
    test_cases = Column(JSON, default=list)
    xp_reward = Column(Integer, nullable=False, default=20)  # 双倍发放=reward*2
    is_active = Column(Boolean, default=True)


class DailyChallengeAttempt(Base):
    """每日挑战打卡记录 — 通过判定 streak。"""

    __tablename__ = "daily_challenge_attempts"
    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", name="uq_daily_challenge_attempt"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("daily_challenges.id"), nullable=False, index=True)
    passed = Column(Boolean, nullable=False, default=False)
    score = Column(Float, nullable=True)
    completed_at = Column(DateTime, default=_utcnow)
