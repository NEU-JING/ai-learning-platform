"""Path API — Learning path endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import User
from app.schemas.path import (
    DiagnosisRequest,
    DiagnosisResponse,
    PathProgressResponse,
    SkillGapResponse,
    UserPathCreateRequest,
    UserPathCreateResponse,
)
from app.services.path_service import DiagnosisService, PathService

router = APIRouter()


@router.post("/diagnosis", response_model=DiagnosisResponse)
def create_diagnosis(
    request: DiagnosisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """入学诊断 — 根据用户背景推荐学习路径.

    AC1, AC2: 根据用户背景推荐路径和起点
    """
    # 验证 target_role 有效性
    valid_roles = ["ai-researcher", "ai-engineer", "ai-applier", "ai-manager"]
    if request.target_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target_role. Must be one of: {valid_roles}",
        )

    # 执行诊断
    result = DiagnosisService.diagnose(request)
    return result


@router.post("", response_model=UserPathCreateResponse, status_code=status.HTTP_201_CREATED)
def create_path(
    request: UserPathCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建学习路径 — 根据诊断结果或手动选择创建用户路径.

    AC1, AC5: 创建路径，支持 fast_track 模式
    """
    service = PathService(db)

    try:
        user_path = service.create_user_path(
            user_id=current_user.id,
            template_slug=request.template_slug,
            mode=request.mode,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # 构建响应
    return service.build_create_response(user_path)


@router.get("/{path_id}/progress", response_model=PathProgressResponse)
def get_path_progress(
    path_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取路径进度 — 返回进度详情、里程碑状态、预估剩余时间.

    AC3: 路径进度追踪
    """
    service = PathService(db)

    # 验证路径存在且属于当前用户
    user_path = service.get_user_path(path_id)
    if not user_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Path not found: {path_id}",
        )

    if user_path.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this path",
        )

    return service.get_progress(user_path)


@router.get("/{path_id}/gaps", response_model=SkillGapResponse)
def get_skill_gaps(
    path_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取能力缺口诊断 — 基于实验通过率识别薄弱技能.

    AC4: 实验通过率 < 60% 判定为薄弱
    """
    service = PathService(db)

    # 验证路径存在
    user_path = service.get_user_path(path_id)
    if not user_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Path not found: {path_id}",
        )

    # 验证权限
    if user_path.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this path",
        )

    return service.detect_skill_gaps(user_path)
