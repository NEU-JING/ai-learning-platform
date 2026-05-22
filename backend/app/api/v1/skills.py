"""Skills API — skill radar visualization and score refresh."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import User
from app.schemas.skill_radar import SkillRadarResponse, SkillRefreshResponse
from app.services.skill_radar import SkillRadarService

router = APIRouter()


@router.get("/radar", response_model=SkillRadarResponse)
def get_skill_radar(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的技能雷达数据。

    返回9个维度的评分、趋势、综合分、强弱项分析。
    """
    data = SkillRadarService.get_skill_radar(current_user.id, db)
    return SkillRadarResponse(**data)


@router.post("/refresh", response_model=SkillRefreshResponse)
def refresh_skills(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """强制刷新技能评分。

    重新计算所有维度的技能分数并持久化到 user_skill_scores 表。
    通常在实验完成后自动调用，也可手动触发。
    """
    updated = SkillRadarService.refresh_skill_scores(current_user.id, db)
    return SkillRefreshResponse(
        user_id=current_user.id,
        updated_dimensions=updated,
        message="技能评分已刷新",
    )
