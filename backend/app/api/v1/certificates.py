from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import User
from app.schemas.capstone import CapstoneSubmitRequest, ReviewActionRequest
from app.services.certificate import certificate_service

router = APIRouter()


@router.get("/courses/{course_id}")
def generate_certificate(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    生成课程完成证书
    """
    result = certificate_service.generate_certificate(
        db=db, user_id=current_user.id, course_id=course_id
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程或用户信息不存在")

    if not result.get("verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message", "无法生成证书")
        )

    return result


@router.get("/verify/{cert_id}")
def verify_certificate(
    cert_id: str,
    db: Session = Depends(get_db),
):
    """
    验证证书真伪 — with ECDSA signature verification
    """
    return certificate_service.verify_certificate(cert_id, db=db)


# ── T18: L2 Capstone Review Endpoints ─────────────────────────────────────


@router.post("/capstone/submit")
def submit_capstone(
    request: CapstoneSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AC31: 提交 L2 顶点项目用于评审。"""

    try:
        result = certificate_service.submit_capstone(
            db=db,
            user_id=current_user.id,
            level_id=request.level_id,
            title=request.title,
            description=request.description,
            repository_url=request.repository_url,
            submission_data=request.submission_data,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND if "not found" in str(e) else status.HTTP_400_BAD_REQUEST
            ),
            detail=str(e),
        )


@router.get("/capstone/review/{submission_id}")
def get_capstone_review(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AC31: 获取 Capstone 提交详情。"""
    from app.models.certification import CapstoneSubmission

    submission = db.query(CapstoneSubmission).filter(CapstoneSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Capstone submission not found"
        )

    return {
        "id": submission.id,
        "user_id": submission.user_id,
        "level_id": submission.level_id,
        "title": submission.title,
        "description": submission.description,
        "repository_url": submission.repository_url,
        "submission_data": submission.submission_data,
        "status": submission.status,
        "ai_review": submission.ai_review,
        "reviewer_id": submission.reviewer_id,
        "reviewer_notes": submission.reviewer_notes,
        "created_at": submission.created_at.isoformat() if submission.created_at else None,
        "updated_at": submission.updated_at.isoformat() if submission.updated_at else None,
    }


@router.post("/capstone/review/{submission_id}/ai-review")
def trigger_ai_review(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AC31: 触发 AI 初审。"""
    try:
        result = certificate_service.ai_review_capstone(db, submission_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/capstone/review/{submission_id}/approve")
def approve_capstone(
    submission_id: int,
    request: ReviewActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AC31: 人工审核 — 批准 Capstone 提交。"""

    try:
        result = certificate_service.approve_capstone(
            db, submission_id, current_user.id, request.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/capstone/review/{submission_id}/reject")
def reject_capstone(
    submission_id: int,
    request: ReviewActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AC31: 人工审核 — 拒绝 Capstone 提交。"""

    try:
        result = certificate_service.reject_capstone(
            db, submission_id, current_user.id, request.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
