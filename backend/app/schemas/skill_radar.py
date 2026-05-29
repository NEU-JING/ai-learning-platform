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
