"""Path module schemas — Request/Response models for learning paths."""

from typing import List, Optional

from pydantic import BaseModel, Field


class DiagnosisRequest(BaseModel):
    """入学诊断请求.

    POST /api/v1/paths/diagnosis
    """

    target_role: str = Field(
        ..., description="目标角色: ai-researcher, ai-engineer, ai-applier, ai-manager"
    )
    experience_years: int = Field(..., ge=0, le=50, description="编程经验年数")
    python_level: str = Field(..., description="Python 水平: beginner, intermediate, advanced")
    math_level: str = Field(..., description="数学水平: beginner, intermediate, advanced")
    current_job: str = Field(..., description="当前职业")
    time_commitment: str = Field(..., description="时间投入: full_time, part_time")
    goal_timeline: str = Field(..., description="目标时间线: 3_months, 6_months, 1_year")


class DiagnosisInfo(BaseModel):
    """诊断结果详情."""

    can_skip_phase1: bool = Field(..., description="能否跳过 Phase 1")
    start_from: int = Field(..., ge=1, le=6, description="从哪个阶段开始")
    weak_areas: List[str] = Field(default_factory=list, description="薄弱领域列表")
    reasoning: str = Field(..., description="诊断理由说明")


class DiagnosisResponse(BaseModel):
    """入学诊断响应.

    200 OK
    """

    recommended_template: str = Field(..., description="推荐的路径模板 slug")
    recommended_mode: str = Field(..., description="推荐的模式: standard, fast_track")
    diagnosis: DiagnosisInfo = Field(..., description="详细诊断结果")
    estimated_duration_weeks: int = Field(..., description="预计学习周期（周）")
    preview_path: Optional[dict] = Field(None, description="路径预览数据")


class PathTemplateResponse(BaseModel):
    """路径模板响应."""

    slug: str
    name: str
    description: Optional[str]
    duration_weeks: int
    target_role: str
    required_courses_count: int
    elective_courses_count: int
    capstone_count: int


class PathTemplateListResponse(BaseModel):
    """路径模板列表响应."""

    templates: List[PathTemplateResponse]


class UserPathCreateRequest(BaseModel):
    """创建用户路径请求.

    POST /api/v1/paths
    """

    template_slug: str = Field(..., description="路径模板 slug")
    mode: str = Field(default="standard", description="学习模式: standard, fast_track")
    diagnosis_id: Optional[int] = Field(None, description="关联的诊断结果 ID")


class PathProgressSummary(BaseModel):
    """路径进度摘要."""

    percent: float
    completed_courses: int
    in_progress_courses: int
    total_courses: int


class MilestoneProgress(BaseModel):
    """里程碑进度."""

    order: int
    name: str
    status: str
    completed_at: Optional[str] = None
    progress: Optional[int] = None


class PathProgressResponse(BaseModel):
    """路径进度响应.

    GET /api/v1/paths/{id}/progress
    """

    path_id: int
    status: str
    progress: PathProgressSummary
    milestones: List[MilestoneProgress]
    estimated_remaining_days: int
    ahead_behind_schedule: str  # ahead, on_track, behind


class UserPathCreateResponse(BaseModel):
    """创建用户路径响应."""

    path_id: int
    template: dict
    status: str
    start_date: Optional[str]
    target_end_date: Optional[str]
    progress: PathProgressSummary
    next_course: Optional[dict]


class SkillGapItem(BaseModel):
    """技能缺口项."""

    dimension: str = Field(..., description="技能维度: python, math, ml, dl, etc.")
    pass_rate: float = Field(..., ge=0.0, le=100.0, description="实验通过率 %")
    status: str = Field(..., description="状态: weak, normal, strong")


class SkillGapRecommendation(BaseModel):
    """技能补强建议."""

    dimension: str
    priority: str = Field(..., description="优先级: high, medium, low")
    recommended_actions: List[str] = Field(default_factory=list)
    estimated_hours: int = Field(default=0, description="建议学习时长（小时）")


class SkillGapResponse(BaseModel):
    """技能缺口诊断响应.

    GET /api/v1/paths/{id}/gaps
    """

    path_id: int
    weak_skills: List[SkillGapItem]
    recommendations: List[SkillGapRecommendation]
    summary: dict = Field(..., description="诊断摘要")
