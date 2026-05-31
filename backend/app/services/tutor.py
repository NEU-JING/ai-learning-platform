"""Tutor service — AI tutoring logic.

T12: Tutor Chat API with LLM Router integration.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import TutorMessage, TutorSession
from app.services.llm_router import LLMRouter


class TutorService:
    """Service for AI tutor functionality."""

    def __init__(self):
        self.llm_router = LLMRouter()

    async def chat(
        self,
        db: Session,
        user_id: int,
        message: str,
        session_type: Optional[str] = None,
        session_id: Optional[int] = None,
        context_id: Optional[int] = None,
        context_type: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Process a chat message and return AI response.

        Args:
            db: Database session
            user_id: User ID
            message: User message
            session_type: Type of session (required for new sessions)
            session_id: Optional existing session ID
            context_id: Optional context (lab_id, course_id, etc.)
            context_type: Optional context type
            attachments: Optional attachments (code snippets, etc.)

        Returns:
            Dict with session info and AI response
        """
        # Get or create session
        if session_id:
            session = (
                db.query(TutorSession)
                .filter(TutorSession.id == session_id, TutorSession.user_id == user_id)
                .first()
            )
            if not session:
                raise ValueError("Session not found")
        else:
            if not session_type:
                raise ValueError("session_type is required for new sessions")
            session = TutorSession(
                user_id=user_id,
                session_type=session_type,
                context_id=context_id,
                context_type=context_type,
                status="active",
                message_count=0,
            )
            db.add(session)
            db.flush()

        # Store user message
        user_msg = TutorMessage(
            session_id=session.id,
            role="user",
            content=message,
            message_metadata={"attachments": attachments} if attachments else None,
        )
        db.add(user_msg)

        # Build conversation context
        conversation = self._build_conversation_context(db, session.id)

        # Call LLM with system prompt based on session type
        system_prompt = self._get_system_prompt(session_type)
        llm_response = await self.llm_router.chat(
            message,
            system_prompt=system_prompt,
            conversation=conversation,
        )

        # Store AI response
        ai_msg = TutorMessage(
            session_id=session.id,
            role="assistant",
            content=llm_response["content"],
            tokens_used=llm_response.get("tokens"),
            model=llm_response.get("model"),
            latency_ms=llm_response.get("latency_ms"),
            provider=llm_response.get("provider"),
        )
        db.add(ai_msg)

        # Update session
        session.message_count += 2  # user + assistant
        db.commit()
        db.refresh(session)

        return {
            "session_id": session.id,
            "session_type": session.session_type,
            "status": session.status,
            "message_count": session.message_count,
            "response": llm_response,
            "created_at": session.created_at.isoformat(),
        }

    def _build_conversation_context(self, db: Session, session_id: int) -> List[Dict[str, str]]:
        """Build conversation context from session history."""
        messages = (
            db.query(TutorMessage)
            .filter(TutorMessage.session_id == session_id)
            .order_by(TutorMessage.created_at.asc())
            .limit(20)  # Keep last 20 messages for context
            .all()
        )

        conversation = []
        for msg in messages:
            conversation.append({"role": msg.role, "content": msg.content})

        return conversation

    def _get_system_prompt(self, session_type: str) -> str:
        """Get system prompt based on session type."""
        prompts = {
            "diagnosis": """你是一位 AI 学习导师，正在对新学员进行入学诊断。
请通过对话了解学员的背景、目标和当前水平，以便推荐合适的学习路径。
保持友好、专业的态度，逐步引导学员表达。""",
            "code_review": """你是一位代码审查导师。请分析学员提供的代码，给出：
1. 代码中的问题和改进建议
2. 代码质量和风格评分
3. 具体的优化示例
请用中文回复，保持建设性和鼓励性。""",
            "qa": """你是一位 AI 学习助教。请回答学员关于课程、编程或 AI 的问题。
回答要：
1. 准确且易懂
2. 结合具体例子
3. 适当引导深入思考
请用中文回复。""",
            "recommendation": """你是一位学习规划导师。根据学员的情况，推荐合适的学习内容和路径。
考虑因素：
1. 学员的背景和目标
2. 当前技能水平
3. 时间和学习节奏
请给出具体、可操作的建议。""",
        }
        return prompts.get(session_type, prompts["qa"])

    def get_session_messages(
        self, db: Session, session_id: int, user_id: int
    ) -> List[TutorMessage]:
        """Get all messages for a session."""
        # Verify session belongs to user
        session = (
            db.query(TutorSession)
            .filter(TutorSession.id == session_id, TutorSession.user_id == user_id)
            .first()
        )

        if not session:
            raise ValueError("Session not found")

        return (
            db.query(TutorMessage)
            .filter(TutorMessage.session_id == session_id)
            .order_by(TutorMessage.created_at.asc())
            .all()
        )
