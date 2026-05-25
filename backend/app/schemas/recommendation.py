"""Recommendation schemas — request/response models for the recommendation API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ContinueLearningResponse(BaseModel):
    """User's last learning position (continue-learning card)."""

    course_id: int
    course_title: str
    course_cover: Optional[str] = Field(None, description="课程封面图 URL")
    chapter_id: int
    chapter_title: str
    progress_pct: float = Field(..., description="该课程完成百分比 0-100")
    last_accessed_at: Optional[str] = Field(None, description="ISO 格式时间戳")


class RecommendationItem(BaseModel):
    """A single recommended chapter."""

    chapter_id: int
    title: str
    course_id: int
    course_title: str
    course_cover: Optional[str] = Field(None, description="课程封面图 URL")
    score: float = Field(..., description="推荐分数 0-1")
    reason: str = Field(..., description="推荐理由（中文）")
    reason_detail: str = Field(default="", description="推荐详细说明")
    component_scores: Optional[dict] = Field(None, description="各维度分数明细")
    recommendation_type: Optional[str] = Field(
        None, description="推荐类型: next_chapter / reinforcement / review / retry"
    )


class PostLabRecommendationItem(RecommendationItem):
    """Extended recommendation item with recommendation_type for post-lab context."""

    recommendation_type: str = Field(..., description="推荐类型")


class LearningCoachResponse(BaseModel):
    """AI learning coach advice for Dashboard display."""

    weekly_hours: float = Field(..., description="本周学习时长（小时）")
    hours_trend: str = Field(..., description="与上周对比趋势，如 '+2.0', '-1.5'")
    weakest_dimension: Optional[str] = Field(None, description="最弱技能维度标识")
    weakest_score: float = Field(default=0.0, description="最弱维度分数 0-100")
    streak_days: int = Field(default=0, description="连续学习天数")
    advice: str = Field(..., description="个性化学习建议（中文）")
    recommended_chapters: list[RecommendationItem] = Field(
        default_factory=list, description="推荐学习的章节列表"
    )


class DailyRecommendationsResponse(BaseModel):
    """Wrapper for daily recommendations list."""

    recommendations: list[RecommendationItem] = Field(
        default_factory=list, description="今日推荐章节列表"
    )
    total_incomplete: int = Field(default=0, description="未完成章节总数")


class PostLabRecommendationsResponse(BaseModel):
    """Wrapper for post-lab recommendations."""

    lab_id: int
    passed: Optional[bool] = Field(None, description="实验是否通过")
    recommendations: list[PostLabRecommendationItem] = Field(
        default_factory=list, description="实验后推荐列表"
    )
