"""Code Review service.

T13: Code Review API with AI analysis.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import CodeReview
from app.services.llm_router import LLMRouter


class CodeReviewService:
    """Service for code review functionality."""

    def __init__(self):
        self.llm_router = LLMRouter()

    async def review_code(
        self,
        db: Session,
        user_id: int,
        code_content: str,
        language: str,
        lab_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Review code and return analysis.

        Args:
            db: Database session
            user_id: User ID
            code_content: Code to review
            language: Programming language
            lab_id: Optional associated lab ID

        Returns:
            Dict with review results
        """
        # Build prompt for code review
        system_prompt = self._get_code_review_prompt(language)

        # Call LLM for analysis
        llm_response = await self.llm_router.chat(
            f"请审查以下{language}代码:\n\n```{language}\n{code_content}\n```",
            system_prompt=system_prompt,
        )

        # Parse LLM response to extract structured data
        review_data = self._parse_review_response(llm_response["content"])

        # Save to database
        code_review = CodeReview(
            user_id=user_id,
            lab_id=lab_id,
            code_content=code_content,
            language=language,
            issues=review_data.get("issues", []),
            dimensions=review_data.get("dimensions", {}),
            overall_score=review_data.get("overall_score", 70.0),
            summary=review_data.get("summary", "代码审查完成"),
        )
        db.add(code_review)
        db.commit()
        db.refresh(code_review)

        return {
            "review_id": code_review.id,
            "user_id": code_review.user_id,
            "lab_id": code_review.lab_id,
            "code_content": code_content,
            "language": language,
            "issues": review_data.get("issues", []),
            "overall_score": review_data.get("overall_score", 70.0),
            "dimensions": review_data.get("dimensions", self._default_dimensions()),
            "summary": review_data.get("summary", "代码审查完成"),
            "reviewed_at": code_review.reviewed_at.isoformat(),
        }

    def get_review(self, db: Session, review_id: int, user_id: int) -> Optional[CodeReview]:
        """Get a specific code review."""
        return (
            db.query(CodeReview)
            .filter(CodeReview.id == review_id, CodeReview.user_id == user_id)
            .first()
        )

    def get_user_reviews(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[CodeReview]:
        """Get user's code review history."""
        return (
            db.query(CodeReview)
            .filter(CodeReview.user_id == user_id)
            .order_by(CodeReview.reviewed_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def _get_code_review_prompt(self, language: str) -> str:
        """Get system prompt for code review."""
        return f"""你是一位专业的{language}代码审查专家。请分析提供的代码并返回JSON格式的审查结果。

返回格式必须如下:
{{
    "issues": [
        {{
            "type": "style|bug|performance|security",
            "line": 行号,
            "message": "问题描述",
            "suggestion": "修复建议",
            "severity": "low|medium|high|critical"
        }}
    ],
    "dimensions": {{
        "correctness": 0-100,  // 代码正确性
        "efficiency": 0-100,   // 执行效率
        "readability": 0-100,  // 可读性
        "style": 0-100,        // 代码风格
        "best_practices": 0-100  // 最佳实践
    }},
    "overall_score": 0-100,  // 综合评分
    "summary": "总体评价和建议"
}}

评分标准:
- correctness: 代码是否能正确运行，有无逻辑错误
- efficiency: 时间/空间复杂度，算法选择
- readability: 命名、注释、代码结构清晰度
- style: 是否符合{language}代码规范
- best_practices: 设计模式、异常处理、边界情况等

请确保返回的是有效的JSON格式。"""

    def _parse_review_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response to extract review data."""
        import json
        import re

        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)

        try:
            data = json.loads(content)
            return {
                "issues": data.get("issues", []),
                "dimensions": data.get("dimensions", self._default_dimensions()),
                "overall_score": data.get("overall_score", 70.0),
                "summary": data.get("summary", "代码审查完成"),
            }
        except json.JSONDecodeError:
            # Fallback to default if parsing fails
            return {
                "issues": [],
                "dimensions": self._default_dimensions(),
                "overall_score": 70.0,
                "summary": content[:500] if content else "代码审查完成",
            }

    def _default_dimensions(self) -> Dict[str, int]:
        """Get default dimension scores."""
        return {
            "correctness": 70,
            "efficiency": 70,
            "readability": 70,
            "style": 70,
            "best_practices": 70,
        }
