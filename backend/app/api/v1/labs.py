from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User
from app.schemas.course import CodeExecutionRequest, CodeExecutionResponse, LabSubmissionResponse
from app.services.lab_service import lab_service

router = APIRouter()


@router.post("/execute", response_model=CodeExecutionResponse)
def execute_code(
    request: CodeExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    在沙箱中执行代码
    
    - **code**: 要执行的Python代码
    - **language**: 编程语言（目前仅支持python）
    - **timeout**: 超时时间（秒，默认30）
    """
    if request.language != "python":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="目前仅支持Python语言"
        )
    
    # 限制超时时间
    timeout = min(request.timeout or 30, 60)  # 最大60秒
    
    result = lab_service.execute_code(request.code, timeout)
    
    return CodeExecutionResponse(
        success=result["status"] == "success",
        output=result["output"],
        error=result["error"],
        execution_time_ms=result["execution_time_ms"]
    )


@router.get("/{lab_id}/submissions", response_model=list[LabSubmissionResponse])
def get_lab_submissions(
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的实验提交历史"""
    from app.models import LabSubmission
    
    submissions = db.query(LabSubmission).filter(
        LabSubmission.lab_id == lab_id,
        LabSubmission.user_id == current_user.id
    ).order_by(LabSubmission.created_at.desc()).all()
    
    return submissions


@router.get("/submissions/{submission_id}", response_model=LabSubmissionResponse)
def get_submission_detail(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取提交详情"""
    from app.models import LabSubmission
    
    submission = db.query(LabSubmission).filter(
        LabSubmission.id == submission_id,
        LabSubmission.user_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在"
        )
    
    return submission
