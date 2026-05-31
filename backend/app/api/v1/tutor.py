"""Tutor API routes.

T12: Tutor Chat API
T13: Code Review API
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas.code_review import (
    CodeReviewCreate,
    CodeReviewListResponse,
    CodeReviewResponse,
)
from app.schemas.tutor import (
    SessionMessagesResponse,
    TutorChatRequest,
    TutorChatResponse,
)
from app.services.code_review import CodeReviewService
from app.services.tutor import TutorService

router = APIRouter(prefix="/tutor", tags=["Tutor"])


@router.post("/chat", response_model=TutorChatResponse)
async def tutor_chat(
    request: TutorChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """AI tutor chat endpoint.

    - Create new session or continue existing one
    - Returns AI response within 5 seconds (AC15)
    """
    try:
        service = TutorService()
        result = await service.chat(
            db=db,
            user_id=current_user.id,
            session_type=request.session_type,
            message=request.message,
            session_id=request.session_id,
            context_id=request.context_id,
            context_type=request.context_type,
            attachments=request.attachments,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI tutor error: {str(e)}",
        )


@router.get("/sessions/{session_id}/messages", response_model=SessionMessagesResponse)
async def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all messages for a tutor session."""
    try:
        service = TutorService()
        messages = service.get_session_messages(db, session_id, current_user.id)
        return {
            "session_id": session_id,
            "messages": messages,
            "total": len(messages),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/code-review", response_model=CodeReviewResponse)
async def create_code_review(
    request: CodeReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a code review (AC16, AC17).

    Analyzes code and returns:
    - List of issues with suggestions
    - Scoring across 5 dimensions
    - Overall score and summary
    """
    try:
        service = CodeReviewService()
        result = await service.review_code(
            db=db,
            user_id=current_user.id,
            code_content=request.code_content,
            language=request.language,
            lab_id=request.lab_id,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code review error: {str(e)}",
        )


@router.get("/code-review/{review_id}", response_model=CodeReviewResponse)
async def get_code_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific code review."""
    service = CodeReviewService()
    review = service.get_review(db, review_id, current_user.id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Code review not found",
        )

    return {
        "review_id": review.id,
        "user_id": review.user_id,
        "lab_id": review.lab_id,
        "code_content": review.code_content,
        "language": review.language,
        "issues": review.issues or [],
        "overall_score": float(review.overall_score) if review.overall_score else 70.0,
        "dimensions": review.dimensions or service._default_dimensions(),
        "summary": review.summary or "",
        "reviewed_at": review.reviewed_at.isoformat(),
    }


@router.get("/code-reviews", response_model=CodeReviewListResponse)
async def get_user_code_reviews(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get user's code review history."""
    service = CodeReviewService()
    reviews = service.get_user_reviews(db, current_user.id, skip, limit)

    return {
        "reviews": [
            {
                "review_id": r.id,
                "user_id": r.user_id,
                "lab_id": r.lab_id,
                "code_content": r.code_content,
                "language": r.language,
                "issues": r.issues or [],
                "overall_score": float(r.overall_score) if r.overall_score else 70.0,
                "dimensions": r.dimensions or service._default_dimensions(),
                "summary": r.summary or "",
                "reviewed_at": r.reviewed_at.isoformat(),
            }
            for r in reviews
        ],
        "total": len(reviews),
    }
