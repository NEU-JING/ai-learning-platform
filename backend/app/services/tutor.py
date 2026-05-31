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

    async def get_recommendations(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Generate personalized learning recommendations.

        T14: Analyzes user skill scores to find weak dimensions
        and recommends courses/practices to improve.

        AC18: 内容个性化推荐 — based on weakest dimensions
        AC19: 路径动态优化 — fast track suggestion if user is exceeding
        """
        from app.models import UserSkillScore
        from app.models.path import UserPath
        from app.models.radar import SkillDimension

        # Get user's skill scores
        user_scores = db.query(UserSkillScore).filter(UserSkillScore.user_id == user_id).all()

        # Build dimension lookup
        dimensions = {d.slug: d for d in db.query(SkillDimension).all()}

        recommendations = []
        based_on_parts = []

        if user_scores:
            # Sort by score ascending — weakest first
            sorted_scores = sorted(user_scores, key=lambda s: s.score)

            # Identify weak dimensions (score < 50)
            weak_scores = [s for s in sorted_scores if s.score < 50]
            # Also include borderline (50-60)
            borderline_scores = [s for s in sorted_scores if 50 <= s.score < 60]

            # Determine what to base the analysis on
            if weak_scores:
                weak_names = []
                for ws in weak_scores[:3]:
                    dim = dimensions.get(ws.dimension)
                    weak_names.append(dim.name if dim else ws.dimension)
                based_on_parts.append("、".join(weak_names) + " 维度薄弱")
            else:
                based_on_parts.append("整体技能水平")

            # Generate course recommendations for each weak dimension
            for ws in weak_scores[:3]:
                dim = dimensions.get(ws.dimension)
                dim_name = dim.name if dim else ws.dimension

                recommendations.append(
                    {
                        "type": "course",
                        "title": f"{dim_name}强化课程",
                        "reason": f"补强{dim_name}基础，提升综合能力",
                        "priority": "high" if ws.score < 30 else "medium",
                        "estimated_time": "4小时",
                    }
                )

            # Generate practice recommendations
            for ws in weak_scores[:2]:
                dim = dimensions.get(ws.dimension)
                dim_name = dim.name if dim else ws.dimension

                recommendations.append(
                    {
                        "type": "practice",
                        "title": f"{dim_name}专项练习",
                        "reason": "针对性练习巩固薄弱环节",
                        "priority": "high" if ws.score < 30 else "medium",
                    }
                )

            # Handle borderline dimensions
            for bs in borderline_scores[:2]:
                dim = dimensions.get(bs.dimension)
                dim_name = dim.name if dim else bs.dimension

                recommendations.append(
                    {
                        "type": "practice",
                        "title": f"{dim_name}进阶训练",
                        "reason": f"提升{dim_name}至优秀水平",
                        "priority": "low",
                    }
                )

        # If no scores at all, give default recommendations
        if not user_scores:
            based_on_parts.append("初始评估阶段")
            recommendations.extend(
                [
                    {
                        "type": "course",
                        "title": "Python 编程基础",
                        "reason": "建立扎实的编程基础",
                        "priority": "high",
                        "estimated_time": "4小时",
                    },
                    {
                        "type": "course",
                        "title": "AI 数学直觉",
                        "reason": "培养算法和数据思维",
                        "priority": "medium",
                        "estimated_time": "4小时",
                    },
                    {
                        "type": "practice",
                        "title": "编程思维练习题",
                        "reason": "动手实践巩固所学",
                        "priority": "high",
                    },
                    {
                        "type": "practice",
                        "title": "算法基础练习",
                        "reason": "培养问题解决能力",
                        "priority": "medium",
                    },
                ]
            )

        # AC19: Check for Fast Track eligibility
        user_path = (
            db.query(UserPath)
            .filter(UserPath.user_id == user_id, UserPath.status == "active")
            .first()
        )

        if user_path:
            progress_pct = user_path.progress_percent or 0
            if progress_pct >= 80:
                # User is highly active, suggest fast track
                recommendations.append(
                    {
                        "type": "course",
                        "title": "Fast Track 加速模式",
                        "reason": "你已连续完成大量任务，建议切换至加速模式跳过已掌握内容",
                        "priority": "high",
                        "estimated_time": "预计节省 2 周",
                    }
                )

        # Deduplicate recommendations while preserving order
        seen = set()
        unique_recs = []
        for rec in recommendations:
            key = (rec["type"], rec["title"])
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)

        return {
            "based_on": "、".join(based_on_parts) if based_on_parts else "学习数据分析",
            "recommendations": unique_recs,
        }

    async def get_obstacles(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Detect learning obstacles by comparing per-lab time vs peer average.

        T15 / AC20: 学习障碍识别 — 用户在某Lab停留超过平均时长3倍时，
        主动询问是否需要帮助。

        Algorithm:
        1. For each lab the user has LearningProgress for, compute time_spent
           (completed_at - created_at, or last_accessed_at - created_at)
        2. For each lab, compute the average time_spent across all other users
        3. If user_time / average_time > 3.0, flag as obstacle
        4. Return list of obstacles with tutor messages
        """
        from app.models import Lab, LearningProgress

        # Get all lab progress for this user (excluding not_started)
        user_progress = (
            db.query(LearningProgress)
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.status != "not_started",
            )
            .all()
        )

        if not user_progress:
            return {"has_obstacles": False, "obstacles": []}

        obstacles = []
        OBSTACLE_RATIO_THRESHOLD = 3.0  # AC20: >3x average → obstacle

        for up in user_progress:
            # Compute user's time spent on this lab
            end_time = up.completed_at or up.last_accessed_at
            if not end_time or not up.created_at:
                continue

            user_time_seconds = (end_time - up.created_at).total_seconds()
            if user_time_seconds <= 0:
                continue

            # Get the lab info via chapter
            lab = db.query(Lab).filter(Lab.chapter_id == up.chapter_id).first()
            if not lab:
                continue

            # Compute average time across all OTHER users for this lab
            other_progress = (
                db.query(LearningProgress)
                .filter(
                    LearningProgress.chapter_id == up.chapter_id,
                    LearningProgress.user_id != user_id,
                    LearningProgress.status != "not_started",
                )
                .all()
            )

            if not other_progress:
                # No peers to compare against — skip
                continue

            other_times = []
            for op in other_progress:
                op_end = op.completed_at or op.last_accessed_at
                if op_end and op.created_at:
                    seconds = (op_end - op.created_at).total_seconds()
                    if seconds > 0:
                        other_times.append(seconds)

            if not other_times:
                continue

            average_seconds = sum(other_times) / len(other_times)
            if average_seconds <= 0:
                continue

            ratio = user_time_seconds / average_seconds

            if ratio >= OBSTACLE_RATIO_THRESHOLD:
                # Format times for display
                user_time_str = self._format_duration(user_time_seconds)
                avg_time_str = self._format_duration(average_seconds)

                tutor_message = (
                    f"是否需要帮助？其他同学在此Lab的平均用时{avg_time_str}。"
                    f"我可以为你提供分步指导。"
                )

                obstacles.append(
                    {
                        "lab_id": lab.id,
                        "lab_name": lab.title,
                        "type": "time_exceeded",
                        "data": {
                            "user_time": user_time_str,
                            "average_time": avg_time_str,
                            "ratio": round(ratio, 2),
                        },
                        "tutor_message": tutor_message,
                    }
                )

        # Check for existing obstacle records and avoid duplicates
        # Sort obstacles by ratio descending (most severe first)
        obstacles.sort(key=lambda o: o["data"]["ratio"], reverse=True)

        return {
            "has_obstacles": len(obstacles) > 0,
            "obstacles": obstacles,
        }

    @staticmethod
    def _format_duration(total_seconds: float) -> str:
        """Format a duration in seconds to a human-readable string."""
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        if hours > 0 and minutes > 0:
            return f"{hours}小时{minutes}分钟"
        elif hours > 0:
            return f"{hours}小时"
        elif minutes > 0:
            return f"{minutes}分钟"
        else:
            return "不到1分钟"
