"""Radar API — GET /api/v1/radar with path specialization.

T8: Radar query with path type highlighting.

AC覆盖:
- AC8: GET /api/v1/radar 端点
- AC11: 路径特化高亮
- AC14: percentile 和 confidence 返回
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import User
from app.services.radar_service import RadarService

router = APIRouter()


@router.get("/radar")
def get_radar(
    path_type: Optional[str] = Query(
        None,
        description="Path type for specialization highlighting. Options: ai-engineer, ai-researcher, ai-applier, ai-manager",
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的技能雷达数据。

    返回10维技能雷达数据，支持路径特化高亮。

    Args:
        path_type: 可选的路径类型，用于高亮相关维度
            - ai-engineer: AI工程师路径
            - ai-researcher: AI专家路径
            - ai-applier: AI应用者路径
            - ai-manager: AI管理者路径

    Returns:
        包含10维技能数据、整体评分、路径高亮信息的响应
    """
    # Validate path_type if provided
    valid_path_types = ["ai-engineer", "ai-researcher", "ai-applier", "ai-manager"]
    if path_type is not None and path_type not in valid_path_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid path_type. Must be one of: {', '.join(valid_path_types)}",
        )

    data = RadarService.get_radar(user_id=current_user.id, db=db, path_type=path_type)

    return data
