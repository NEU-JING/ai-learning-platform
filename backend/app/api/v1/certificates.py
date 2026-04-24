from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User
from app.services.certificate import certificate_service

router = APIRouter()


@router.get("/courses/{course_id}")
def generate_certificate(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成课程完成证书
    """
    result = certificate_service.generate_certificate(
        db=db,
        user_id=current_user.id,
        course_id=course_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程或用户信息不存在"
        )
    
    if not result.get("verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "无法生成证书")
        )
    
    return result


@router.get("/verify/{cert_id}")
def verify_certificate(cert_id: str):
    """
    验证证书真伪
    """
    return certificate_service.verify_certificate(cert_id)
