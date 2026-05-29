"""Path API — Learning path endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import User
from app.schemas.path import (
    DiagnosisRequest,
    DiagnosisResponse,
)
from app.services.path_service import DiagnosisService

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
