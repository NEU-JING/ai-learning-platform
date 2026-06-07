"""Radar module models — 多维技能雷达系统.

T6: Radar 模块数据库表
- SkillDimension: 技能维度定义表
- SkillEvent: 技能事件日志表

注意：UserSkillScore 模型保留在 __init__.py 中，这里只做扩展
"""

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models import Base, _utcnow


class SkillDimension(Base):
    """技能维度定义 — 10维技能雷达的维度元数据."""

    __tablename__ = "skill_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(64), nullable=False)
    name_en = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(16), nullable=False)  # hard, soft, specialized
    weight_formula = Column(Text, nullable=True)  # 计算公式，如 "avg(lab_scores) * time_decay"
    max_score = Column(Float, default=100.0)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    events = relationship("SkillEvent", back_populates="dimension")

    def __repr__(self):
        return f"<SkillDimension({self.slug}: {self.name})>"


class SkillEvent(Base):
    """技能事件日志 — 用于重新计算技能分数."""

    __tablename__ = "skill_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(32), nullable=False)  # lab_completed, project_submitted, etc.
    dimension_id = Column(Integer, ForeignKey("skill_dimensions.id"), nullable=True)
    score_impact = Column(Float, nullable=True)  # 对分数的影响
    event_metadata = Column(JSON, nullable=True)  # 关联的lab_id, project_id等
    created_at = Column(DateTime, default=_utcnow, index=True)

    # relationships
    user = relationship("User")
    dimension = relationship("SkillDimension", back_populates="events")

    def __repr__(self):
        return f"<SkillEvent(user={self.user_id}, type={self.event_type})>"


class UserSkillSnapshot(Base):
    """用户技能分数历史快照 — 用于对比功能 (AC12)."""

    __tablename__ = "user_skill_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_name = Column(String(64), nullable=True)  # 用户自定义名称，如 "入职前"
    scores = Column(JSON, nullable=False)  # {dimension_slug: score, ...}
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    user = relationship("User")

    def __repr__(self):
        return f"<UserSkillSnapshot(user={self.user_id}, name={self.snapshot_name})>"


class JobSkillRequirement(Base):
    """目标岗位技能要求 — 用于差距分析 (AC13)."""

    __tablename__ = "job_skill_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(64), nullable=False, index=True)  # 岗位名称，如 "ai-engineer"
    job_level = Column(String(16), nullable=True)  # 级别: junior, mid, senior
    required_skills = Column(JSON, nullable=False)  # {dimension_slug: min_score, ...}
    source = Column(String(32), nullable=True)  # 来源: jd_analysis, manual
    created_at = Column(DateTime, default=_utcnow)

    def __repr__(self):
        return f"<JobSkillRequirement({self.job_title}: {self.job_level})>"
