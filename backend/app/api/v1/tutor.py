"""Tutor API routes.

T12: Tutor Chat API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas.tutor import (
    SessionMessagesResponse,
    TutorChatRequest,
    TutorChatResponse,
)
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
