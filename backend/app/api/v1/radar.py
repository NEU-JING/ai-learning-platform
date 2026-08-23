"""Radar API — GET /api/v1/radar with path specialization.

T8: Radar query with path type highlighting.
T9: Snapshot and comparison endpoints for AC12.

AC覆盖:
- AC8: GET /api/v1/radar 端点
- AC11: 路径特化高亮
- AC14: percentile 和 confidence 返回
- AC12: 快照和对比功能
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import User
from app.schemas.skill_radar import (
    RadarComparisonResponse,
    RadarGapAnalysisResponse,
    RadarSnapshotCreate,
    RadarSnapshotResponse,
    SkillTrendPoint,
)
from app.services.radar_service import RadarService, SnapshotService, get_skill_trend

router = APIRouter()


@router.get("/radar")
def get_radar(
    path_type: Optional[str] = Query(
        None,
        description=(
            "Path type for specialization highlighting. "
            "Options: ai-engineer, ai-researcher, ai-applier, ai-manager"
        ),
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


@router.post("/radar/snapshots", response_model=RadarSnapshotResponse, status_code=201)
def create_snapshot(
    data: RadarSnapshotCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建当前技能快照。

    AC12: 保存当前技能状态，用于后续对比。

    Args:
        data: 快照创建请求，包含可选的名称和路径ID

    Returns:
        创建的快照信息，包含ID、名称、日期和分数
    """
    # Validate name length
    if data.name and len(data.name) > 64:
        raise HTTPException(
            status_code=400,
            detail="Snapshot name must be at most 64 characters",
        )

    snapshot = SnapshotService.create_snapshot(
        user_id=current_user.id,
        name=data.name,
        path_id=data.path_id,
        db=db,
    )

    return {
        "snapshot_id": snapshot.id,
        "name": snapshot.snapshot_name,
        "snapshot_date": snapshot.created_at.isoformat() if snapshot.created_at else None,
        "scores": snapshot.scores,
    }


@router.get("/radar/compare", response_model=RadarComparisonResponse)
def compare_snapshot(
    snapshot_id: int = Query(..., description="快照ID用于对比"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """对比当前技能与历史快照。

    AC12: 显示当前技能与历史快照的差异和趋势。

    Args:
        snapshot_id: 要对比的历史快照ID

    Returns:
        包含当前分数、历史分数、对比结果和评估的响应
    """
    if snapshot_id is None:
        raise HTTPException(
            status_code=400,
            detail="snapshot_id is required",
        )

    result = SnapshotService.compare_with_snapshot(
        user_id=current_user.id,
        snapshot_id=snapshot_id,
        db=db,
    )

    return result


@router.get("/radar/gap-analysis", response_model=RadarGapAnalysisResponse)
def gap_analysis(
    target_job: str = Query(..., description="目标岗位名称，如 ai-engineer"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """分析当前技能与目标岗位要求的差距。

    AC13: 返回技能差距分析，包含当前分数、要求分数、差距值和推荐课程。

    Args:
        target_job: 目标岗位名称，如 'ai-engineer'

    Returns:
        包含差距列表、整体准备度和预计弥补天数的响应
    """
    from app.services.radar_service import GapAnalysisService

    result = GapAnalysisService.analyze_gaps(
        user_id=current_user.id,
        target_job=target_job,
        db=db,
    )

    return result


@router.get("/radar/trend", response_model=list[SkillTrendPoint])
def get_trend(
    weeks: int = Query(8, ge=1, le=52, description="返回的周数，默认 8"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """技能成长趋势 — Phase 4 F6。

    按周聚合各维度分数（截至每周末），数据源 = SkillEvent（行为自动记录，
    零手动打点）。成长曲线由浏览器/前端可视化。
    """
    return get_skill_trend(db, current_user.id, weeks=weeks)
