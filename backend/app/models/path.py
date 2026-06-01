"""Path module models — Learning path templates and user path instances."""

from sqlalchemy import (
    JSON,
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
from sqlalchemy.orm import relationship

from app.models import Base, _utcnow


class PathTemplate(Base):
    """路径模板（系统预定义）— 定义学习路径的基本结构."""

    __tablename__ = "path_templates"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(
        String(32), unique=True, nullable=False, index=True
    )  # ai-researcher, ai-engineer, etc.
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    duration_weeks = Column(Integer, nullable=False)  # 20, 14, 8, 6
    target_role = Column(String(32), nullable=False)  # AI专家, AI工程师, AI应用者, AI管理者
    required_courses = Column(JSON, nullable=False, default=list)  # [course_id1, course_id2, ...]
    elective_courses = Column(JSON, nullable=True, default=list)  # 可选课程
    capstone_count = Column(Integer, default=2)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    user_paths = relationship("UserPath", back_populates="template")
    milestones = relationship("PathMilestone", back_populates="template")

    def __repr__(self):
        return f"<PathTemplate({self.slug}: {self.name})>"


class UserPath(Base):
    """用户路径实例 — 用户实际参与的学习路径."""

    __tablename__ = "user_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("path_templates.id"), nullable=True)
    status = Column(String(16), default="active")  # active, completed, paused, switched
    start_date = Column(Date, nullable=True)
    target_end_date = Column(Date, nullable=True)  # 预计完成日期
    actual_end_date = Column(Date, nullable=True)
    mode = Column(String(16), default="standard")  # standard, fast_track
    diagnosis_result = Column(
        JSON, nullable=True
    )  # 入学诊断结果 {skip_phase1: true, start_from: 2}
    progress_percent = Column(Float, default=0.00)
    current_milestone = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    user = relationship("User")
    template = relationship("PathTemplate", back_populates="user_paths")
    courses = relationship("PathCourse", back_populates="path", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserPath(user={self.user_id}, template={self.template_id}, status={self.status})>"


class PathCourse(Base):
    """路径课程关联 — 记录用户在路径中的课程状态."""

    __tablename__ = "path_courses"
    __table_args__ = (UniqueConstraint("path_id", "course_id", name="uq_path_course"),)

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("user_paths.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    sequence_order = Column(Integer, nullable=False)  # 在路径中的顺序
    status = Column(String(16), default="pending")  # pending, in_progress, completed, skipped
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # relationships
    path = relationship("UserPath", back_populates="courses")
    course = relationship("Course")

    def __repr__(self):
        return f"<PathCourse(path={self.path_id}, course={self.course_id}, status={self.status})>"


class PathMilestone(Base):
    """里程碑定义 — 路径中的关键节点."""

    __tablename__ = "path_milestones"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("path_templates.id"), nullable=True)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, nullable=False)
    required_courses = Column(JSON, nullable=True)  # 完成这些课程即达成里程碑
    reward_badge = Column(String(32), nullable=True)

    # relationships
    template = relationship("PathTemplate", back_populates="milestones")

    def __repr__(self):
        return f"<PathMilestone({self.name}, order={self.sequence_order})>"


class SkillGapDiagnosis(Base):
    """能力缺口诊断记录 — 用户的技能缺口分析."""

    __tablename__ = "skill_gap_diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    path_id = Column(Integer, ForeignKey("user_paths.id"), nullable=True)
    weak_dimensions = Column(JSON, nullable=True)  # ["algorithm_understanding", "linear_algebra"]
    recommended_courses = Column(JSON, nullable=True)  # 推荐的补强课程
    diagnosed_at = Column(DateTime, default=_utcnow)

    # relationships
    user = relationship("User")
    path = relationship("UserPath")

    def __repr__(self):
        return f"<SkillGapDiagnosis(user={self.user_id}, path={self.path_id})>"
