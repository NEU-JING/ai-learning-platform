"""Lab service — handles code submission, execution, and grading.

Redesigned for MVP:
- validate_code / execute_code REMOVED — use CodeSecurityChecker + code_executor
- submit_and_grade is the single entry point for lab submissions
- All code execution goes through code_executor (Docker sandbox)
"""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.code_security import check_code_security
from app.models import Lab, LabSubmission, LearningProgress
from app.services.code_executor import execute_code_docker
from app.services.grader import CodeGrader
from app.services.skill_radar import SkillRadarService


class LabService:
    @staticmethod
    def get_lab(db: Session, lab_id: int) -> Lab | None:
        """Get lab by ID (public view, no solution)."""
        return db.query(Lab).filter(Lab.id == lab_id).first()

    @staticmethod
    def submit_and_grade(
        db: Session,
        user_id: int,
        lab_id: int,
        code: str,
    ) -> LabSubmission:
        """Submit code, execute in sandbox, grade, and auto-update progress.

        Flow:
        1. Fetch Lab (with test_cases, time_limit)
        2. Security check via CodeSecurityChecker
        3. Execute code in Docker sandbox
        4. Grade in sandbox via CodeGrader
        5. Write LabSubmission with score/passed/test_results/feedback
        6. If passed → auto-mark chapter progress as completed
        7. Return LabSubmission
        """
        # 1. Fetch lab
        lab = db.query(Lab).filter(Lab.id == lab_id).first()
        if not lab:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")

        # 2. Security check
        is_safe, security_msg = check_code_security(code)
        if not is_safe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"代码安全检查未通过: {security_msg}",
            )

        # 3. Create submission record (status=running)
        submission = LabSubmission(
            user_id=user_id,
            lab_id=lab_id,
            code=code,
            status="running",
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # 4. Execute code in sandbox
        timeout = lab.time_limit_seconds or 30
        import asyncio

        try:
            exec_result = asyncio.get_event_loop().run_until_complete(
                execute_code_docker(code, timeout=timeout)
            )
        except RuntimeError:
            loop = asyncio.new_event_loop()
            exec_result = loop.run_until_complete(execute_code_docker(code, timeout=timeout))
            loop.close()

        # 5. Grade in sandbox
        test_cases = lab.test_cases or []
        grading_result = CodeGrader.grade_in_sandbox(code, test_cases, timeout=timeout)

        # 6. Update submission with all results
        submission.status = "success" if grading_result["passed"] else "failed"
        submission.output = exec_result.get("output", "")
        submission.error_message = exec_result.get("error")
        submission.execution_time_ms = exec_result.get("execution_time_ms")
        submission.score = grading_result["score"]
        submission.passed = grading_result["passed"]
        submission.test_results = grading_result["test_results"]
        submission.feedback = grading_result["feedback"]
        submission.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(submission)

        # 7. Auto-mark chapter progress as completed if passed
        if grading_result["passed"] and lab.chapter_id:
            progress = (
                db.query(LearningProgress)
                .filter(
                    LearningProgress.user_id == user_id,
                    LearningProgress.chapter_id == lab.chapter_id,
                )
                .first()
            )

            now = datetime.now(timezone.utc)
            if progress:
                progress.status = "completed"
                progress.completed_at = now
                progress.last_accessed_at = now
            else:
                progress = LearningProgress(
                    user_id=user_id,
                    chapter_id=lab.chapter_id,
                    status="completed",
                    completed_at=now,
                    last_accessed_at=now,
                )
                db.add(progress)
            db.commit()

        # 8. Auto-refresh skill radar scores when lab is passed
        if grading_result["passed"]:
            try:
                SkillRadarService.refresh_skill_scores(user_id, db)
            except Exception:
                pass  # Non-critical — don't fail the submission over scoring

        return submission


lab_service = LabService()
