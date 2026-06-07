from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import User
from app.schemas.capstone import CapstoneSubmitRequest, ReviewActionRequest
from app.services.certificate import certificate_service

router = APIRouter()
certifications_router = APIRouter()


class CertificationApplyRequest(BaseModel):
    """Request body for L1 certification application."""

    level_id: int = Field(..., ge=1, description="Certification level ID")


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


# ── M2: 证书详情查询端点 ──────────────────────────────────────────────────


@router.get("/{cert_number}")
def get_certificate_detail(
    cert_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """查询证书详情和签名信息。"""
    from app.models.certification import Certificate, CertificationLevel

    cert = db.query(Certificate).filter(Certificate.cert_number == cert_number).first()

    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"证书 {cert_number} 不存在",
        )

    # Fetch level name
    level = db.query(CertificationLevel).filter(CertificationLevel.id == cert.level_id).first()
    level_name = level.name if level else None

    return {
        "id": cert.id,
        "cert_number": cert.cert_number,
        "user_id": cert.user_id,
        "level_id": cert.level_id,
        "level_name": level_name,
        "issue_date": cert.issue_date.isoformat() if cert.issue_date else None,
        "cert_metadata": cert.cert_metadata,
        "signature": cert.signature,
        "is_valid": cert.is_valid,
        "created_at": cert.created_at.isoformat() if cert.created_at else None,
    }


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


# ── M1: L1 认证申请端点 ───────────────────────────────────────────────────


@certifications_router.post("/apply")
def apply_l1_certification(
    request: CertificationApplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """L1 认证申请 — 自动评定必修课程和平均分。"""

    result = certificate_service.auto_evaluate_l1(
        db=db, user_id=current_user.id, level_id=request.level_id
    )

    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("reason", "Certification level not found"),
        )

    return result
