from typing import Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.code_security import check_code_security
from app.api.deps import get_current_active_user
from app.models import User, LabSubmission
from app.schemas.course import CodeExecutionRequest, CodeExecutionResponse, LabSubmissionResponse
from app.schemas.pagination import PaginatedResponse
from app.services.code_executor import execute_code_docker

router = APIRouter()


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Execute code in sandbox (no submission recorded)."""
    if request.language != "python":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="目前仅支持Python语言",
        )

    # Security check before execution
    is_safe, security_msg = check_code_security(request.code)
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"代码安全检查未通过: {security_msg}",
        )

    timeout = min(request.timeout or 30, 300)

    result = await execute_code_docker(request.code, timeout=timeout)

    return CodeExecutionResponse(
        success=result.get("success", False),
        output=result.get("output", ""),
        error=result.get("error"),
        execution_time_ms=result.get("execution_time_ms", 0),
    )


@router.get("/{lab_id}/submissions")
def get_lab_submissions(
    lab_id: int,
    page: Optional[int] = Query(None, ge=1, description="Page number (1-indexed)"),
    per_page: Optional[int] = Query(None, ge=1, le=100, description="Items per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user's submission history for a lab.

    When `page` is provided, returns a paginated response with metadata.
    When `page` is omitted, returns the full list (backward compatible).
    """
    base_query = db.query(LabSubmission).filter(
        LabSubmission.lab_id == lab_id,
        LabSubmission.user_id == current_user.id,
    )

    if page is not None:
        total = base_query.count()
        _per_page = min(per_page or 20, 100)
        offset = (page - 1) * _per_page
        submissions = (
            base_query.order_by(LabSubmission.created_at.desc())
            .offset(offset)
            .limit(_per_page)
            .all()
        )
        _pages = ceil(total / _per_page) if total > 0 else 0
        return {
            "items": submissions,
            "total": total,
            "page": page,
            "per_page": _per_page,
            "pages": _pages,
        }

    # Backward compatible: return plain list
    return base_query.order_by(LabSubmission.created_at.desc()).all()


@router.get("/submissions/{submission_id}", response_model=LabSubmissionResponse)
def get_submission_detail(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get submission detail."""
    submission = (
        db.query(LabSubmission)
        .filter(
            LabSubmission.id == submission_id,
            LabSubmission.user_id == current_user.id,
        )
        .first()
    )
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在",
        )
    return submission
