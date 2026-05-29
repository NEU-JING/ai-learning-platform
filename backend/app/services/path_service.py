"""Path service — Business logic for learning paths."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.path import PathTemplate, UserPath
from app.schemas.path import DiagnosisInfo, DiagnosisRequest, DiagnosisResponse


class DiagnosisService:
    """入学诊断服务 — 根据用户背景推荐学习路径."""

    # 目标角色到模板 slug 的映射
    ROLE_TO_TEMPLATE = {
        "ai-researcher": "ai-researcher",
        "ai-engineer": "ai-engineer",
        "ai-applier": "ai-applier",
        "ai-manager": "ai-manager",
    }

    # 模板 slug 到基础周数的映射
    TEMPLATE_BASE_WEEKS = {
        "ai-researcher": 20,
        "ai-engineer": 14,
        "ai-applier": 8,
        "ai-manager": 6,
    }

    # Fast Track 模式的最小周数
    FAST_TRACK_MIN_WEEKS = 6

    @classmethod
    def diagnose(cls, request: DiagnosisRequest) -> DiagnosisResponse:
        """执行入学诊断.

        AC1: 根据目标角色推荐路径模板
        AC2: 检测是否可跳过 Phase 1
        """
        # 1. 确定推荐模板
        recommended_template = cls.ROLE_TO_TEMPLATE.get(request.target_role, "ai-engineer")

        # 2. 诊断算法：能否跳过 Phase 1
        can_skip_phase1 = cls._can_skip_phase1(
            python_level=request.python_level,
            experience_years=request.experience_years,
        )

        # 3. 检测薄弱领域
        weak_areas = cls._detect_weak_areas(
            math_level=request.math_level,
        )

        # 4. 确定学习模式
        mode = cls._determine_mode(
            goal_timeline=request.goal_timeline,
        )

        # 5. 计算预计学习周期
        estimated_weeks = cls._calculate_duration(
            template_slug=recommended_template,
            mode=mode,
            can_skip_phase1=can_skip_phase1,
        )

        # 6. 生成诊断理由
        reasoning = cls._generate_reasoning(
            python_level=request.python_level,
            experience_years=request.experience_years,
            math_level=request.math_level,
            can_skip_phase1=can_skip_phase1,
            weak_areas=weak_areas,
        )

        return DiagnosisResponse(
            recommended_template=recommended_template,
            recommended_mode=mode,
            diagnosis=DiagnosisInfo(
                can_skip_phase1=can_skip_phase1,
                start_from=2 if can_skip_phase1 else 1,
                weak_areas=weak_areas,
                reasoning=reasoning,
            ),
            estimated_duration_weeks=estimated_weeks,
            preview_path={},
        )

    @classmethod
    def _can_skip_phase1(cls, python_level: str, experience_years: int) -> bool:
        """判断能否跳过 Phase 1 (Python 基础).

        条件：Python 水平为 intermediate 或 advanced，且经验 >= 2 年
        """
        return python_level in ["intermediate", "advanced"] and experience_years >= 2

    @classmethod
    def _detect_weak_areas(cls, math_level: str) -> List[str]:
        """检测薄弱领域.

        当前规则：
        - math_level == beginner -> 线性代数需要补强
        """
        weak_areas = []
        if math_level == "beginner":
            weak_areas.append("linear_algebra")
        return weak_areas

    @classmethod
    def _determine_mode(cls, goal_timeline: str) -> str:
        """确定学习模式.

        - 3_months -> fast_track
        - 其他 -> standard
        """
        return "fast_track" if goal_timeline == "3_months" else "standard"

    @classmethod
    def _calculate_duration(
        cls,
        template_slug: str,
        mode: str,
        can_skip_phase1: bool,
    ) -> int:
        """计算预计学习周期."""
        base_weeks = cls.TEMPLATE_BASE_WEEKS.get(template_slug, 14)

        # Fast Track 模式：减少到 60% 但不少于最小周数
        if mode == "fast_track":
            fast_weeks = int(base_weeks * 0.6)
            base_weeks = max(fast_weeks, cls.FAST_TRACK_MIN_WEEKS)

        # 跳过 Phase 1：减少约 3 周
        if can_skip_phase1:
            base_weeks = max(base_weeks - 3, cls.FAST_TRACK_MIN_WEEKS)

        return base_weeks

    @classmethod
    def _generate_reasoning(
        cls,
        python_level: str,
        experience_years: int,
        math_level: str,
        can_skip_phase1: bool,
        weak_areas: List[str],
    ) -> str:
        """生成诊断理由."""
        parts = []

        if can_skip_phase1:
            parts.append(
                f"您有{experience_years}年编程经验且Python水平为{python_level}，可直接从Phase 2开始"
            )
        else:
            parts.append("建议您从Phase 1开始，巩固Python基础")

        if weak_areas:
            parts.append(f"但建议补充{weak_areas[0]}基础")

        return "，".join(parts)


class PathService:
    """路径服务 — 用户路径管理."""

    def __init__(self, db: Session):
        self.db = db

    def get_template_by_slug(self, slug: str) -> Optional[PathTemplate]:
        """根据 slug 获取路径模板."""
        return self.db.query(PathTemplate).filter(PathTemplate.slug == slug).first()

    def list_templates(self) -> List[PathTemplate]:
        """获取所有路径模板."""
        return self.db.query(PathTemplate).all()

    def create_user_path(
        self,
        user_id: int,
        template_slug: str,
        mode: str = "standard",
        diagnosis_result: Optional[dict] = None,
    ) -> UserPath:
        """为用户创建学习路径."""
        template = self.get_template_by_slug(template_slug)
        if not template:
            raise ValueError(f"Template not found: {template_slug}")

        # 检查是否已有 active 路径
        existing = (
            self.db.query(UserPath)
            .filter(UserPath.user_id == user_id, UserPath.status == "active")
            .first()
        )
        if existing:
            raise ValueError("User already has an active path")

        # 计算目标完成日期
        from datetime import date, timedelta

        duration_weeks = template.duration_weeks
        if mode == "fast_track":
            duration_weeks = max(int(duration_weeks * 0.6), DiagnosisService.FAST_TRACK_MIN_WEEKS)

        start_date = date.today()
        target_end_date = start_date + timedelta(weeks=duration_weeks)

        user_path = UserPath(
            user_id=user_id,
            template_id=template.id,
            status="active",
            mode=mode,
            start_date=start_date,
            target_end_date=target_end_date,
            diagnosis_result=diagnosis_result,
            progress_percent=0.0,
            current_milestone=0,
        )

        self.db.add(user_path)
        self.db.commit()
        self.db.refresh(user_path)

        return user_path
