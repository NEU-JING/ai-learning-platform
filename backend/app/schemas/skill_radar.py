"""Skill radar schemas — request/response models for the skill radar API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SkillDimensionScore(BaseModel):
    """Single dimension score in the radar."""

    score: float = Field(..., description="0–100 技能评分")
    label: str = Field(..., description="维度中文标签，如 Python基础")
    trend: str = Field(default="0", description="与上次评分的差值，如 '+15', '-5', '0'")


class SkillDimensionDetail(BaseModel):
    """Detailed dimension info with percentile and confidence."""

    slug: str = Field(..., description="维度标识，如 'coding_thinking'")
    name: str = Field(..., description="维度中文名称")
    score: float = Field(..., description="0-100 技能评分")
    percentile: float = Field(..., description="百分位数 0-100")
    confidence: float = Field(..., description="置信度 0-1，基于数据量")
    category: str = Field(..., description="类别: hard, soft, specialized")
    highlighted: bool = Field(default=False, description="是否被路径特化高亮")


class SkillRadarResponse(BaseModel):
    """Full skill radar response for a user."""

    user_id: int
    skills: dict[str, SkillDimensionScore] = Field(
        ..., description="各维度评分，key 为维度标识如 'python', 'math'"
    )
    overall_score: float = Field(..., description="加权平均综合评分 (0-100)")
    weakest: list[str] = Field(default_factory=list, description="最弱的3个维度标识")
    strongest: list[str] = Field(default_factory=list, description="最强的3个维度标识")
    updated_at: Optional[datetime] = Field(None, description="最近一次刷新时间")


class RadarQueryResponse(BaseModel):
    """T8: Radar query response with path specialization."""

    user_id: int
    dimensions: list[SkillDimensionDetail] = Field(..., description="10维技能数据")
    overall_score: float = Field(..., description="加权平均综合评分 (0-100)")
    path_type: Optional[str] = Field(None, description="当前路径类型")
    updated_at: Optional[datetime] = Field(None, description="最近一次刷新时间")


class SkillRefreshResponse(BaseModel):
    """Response after forcing a skill score refresh."""

    user_id: int
    updated_dimensions: int = Field(..., description="更新的维度数量")
    message: str = Field(default="技能评分已刷新")


# T9: Snapshot and Comparison schemas for AC12


class RadarSnapshotCreate(BaseModel):
    """Request to create a skill snapshot."""

    name: Optional[str] = Field(None, description="快照名称，如 '入职前'")
    path_id: Optional[int] = Field(None, description="关联的路径ID")


class RadarSnapshotResponse(BaseModel):
    """Response after creating a snapshot."""

    snapshot_id: int
    name: Optional[str] = Field(None, description="快照名称")
    snapshot_date: Optional[str] = Field(None, description="快照创建时间 ISO格式")
    scores: dict[str, float] = Field(..., description="各维度分数 {slug: score}")


class DimensionComparison(BaseModel):
    """Single dimension comparison result."""

    dimension: str = Field(..., description="维度标识符")
    current: float = Field(..., description="当前分数")
    snapshot: float = Field(..., description="快照分数")
    change: float = Field(..., description="变化值 (current - snapshot)")
    trend: str = Field(..., description="趋势: up, down, flat")


class SnapshotInfo(BaseModel):
    """Snapshot metadata in comparison response."""

    name: Optional[str] = Field(None, description="快照名称")
    date: Optional[str] = Field(None, description="快照创建日期")


class RadarComparisonResponse(BaseModel):
    """Response for radar snapshot comparison — AC12."""

    current: dict[str, float] = Field(..., description="当前各维度分数")
    snapshot: dict[str, float] = Field(..., description="快照各维度分数")
    comparison: list[DimensionComparison] = Field(..., description="各维度对比详情")
    assessment: str = Field(..., description="整体评估文本")
    snapshot_info: SnapshotInfo = Field(..., description="快照信息")


# T10: Gap Analysis schemas for AC13


class RecommendedCourse(BaseModel):
    """Recommended course for closing a skill gap."""

    id: int = Field(..., description="课程ID")
    name: str = Field(..., description="课程名称")
    relevance: float = Field(..., description="相关度 0-1")


class SkillGap(BaseModel):
    """Single skill gap item."""

    dimension: str = Field(..., description="维度标识符")
    current_score: float = Field(..., description="当前分数")
    required_score: float = Field(..., description="要求分数")
    gap: float = Field(..., description="差距值 (required - current)")
    priority: str = Field(..., description="优先级: high, medium, low")
    recommended_courses: list[RecommendedCourse] = Field(
        default_factory=list, description="推荐课程"
    )


class RadarGapAnalysisResponse(BaseModel):
    """Response for radar gap analysis — AC13."""

    target_job: str = Field(..., description="目标岗位")
    target_level: Optional[str] = Field(None, description="目标级别")
    gaps: list[SkillGap] = Field(..., description="技能差距列表")
    overall_readiness: float = Field(..., description="整体准备度 0-100")
    estimated_gap_days: int = Field(..., description="预计弥补差距所需天数")
