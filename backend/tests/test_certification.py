"""Test Certification module database tables — T16.

Tests the existence and structure of Certification tables:
- certification_levels: 认证级别定义表
- certification_applications: 用户认证申请表
- certificates: 已颁发证书表
- capstone_submissions: 顶点项目提交表

AC覆盖:
- AC30: certification_levels table
- AC31: certification_applications table
- AC32: certificates table
- AC33: capstone_submissions table
- AC34-AC37: Foreign key relationships
"""

import pytest
from sqlalchemy import inspect


class TestCertificationTablesExist:
    """RED phase test: Verify certification tables are created in database."""

    def test_certification_levels_table_exists(self, test_db):
        """AC30: certification_levels table should exist with required columns."""
        inspector = inspect(test_db.bind)
        tables = inspector.get_table_names()
        assert "certification_levels" in tables, "certification_levels table should exist"

        columns = {col["name"] for col in inspector.get_columns("certification_levels")}
        required_columns = {
            "id",
            "name",
            "description",
            "required_courses",
            "min_average_score",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        }
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_certification_applications_table_exists(self, test_db):
        """AC31: certification_applications table should exist with required columns."""
        inspector = inspect(test_db.bind)
        tables = inspector.get_table_names()
        assert (
            "certification_applications" in tables
        ), "certification_applications table should exist"

        columns = {col["name"] for col in inspector.get_columns("certification_applications")}
        required_columns = {
            "id",
            "user_id",
            "level_id",
            "status",
            "evaluation_data",
            "evaluator_notes",
            "created_at",
            "updated_at",
        }
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_certificates_table_exists(self, test_db):
        """AC32: certificates table should exist with required columns."""
        inspector = inspect(test_db.bind)
        tables = inspector.get_table_names()
        assert "certificates" in tables, "certificates table should exist"

        columns = {col["name"] for col in inspector.get_columns("certificates")}
        required_columns = {
            "id",
            "user_id",
            "level_id",
            "cert_number",
            "issue_date",
            "cert_metadata",
            "signature",
            "is_valid",
            "created_at",
        }
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_capstone_submissions_table_exists(self, test_db):
        """AC33: capstone_submissions table should exist with required columns."""
        inspector = inspect(test_db.bind)
        tables = inspector.get_table_names()
        assert "capstone_submissions" in tables, "capstone_submissions table should exist"

        columns = {col["name"] for col in inspector.get_columns("capstone_submissions")}
        required_columns = {
            "id",
            "user_id",
            "level_id",
            "title",
            "description",
            "repository_url",
            "submission_data",
            "status",
            "ai_review",
            "reviewer_id",
            "reviewer_notes",
            "created_at",
            "updated_at",
        }
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_certification_applications_fk(self, test_db):
        """AC34: certification_applications should have FK to users and certification_levels."""
        inspector = inspect(test_db.bind)
        fks = inspector.get_foreign_keys("certification_applications")
        fk_tables = {fk["referred_table"] for fk in fks}
        assert "users" in fk_tables, "Should have FK to users"
        assert "certification_levels" in fk_tables, "Should have FK to certification_levels"

    def test_certificates_fk(self, test_db):
        """AC35: certificates should have FK to users and certification_levels."""
        inspector = inspect(test_db.bind)
        fks = inspector.get_foreign_keys("certificates")
        fk_tables = {fk["referred_table"] for fk in fks}
        assert "users" in fk_tables, "Should have FK to users"
        assert "certification_levels" in fk_tables, "Should have FK to certification_levels"

    def test_capstone_submissions_fk(self, test_db):
        """AC36: capstone_submissions should have FK to users, certification_levels, and users (reviewer)."""
        inspector = inspect(test_db.bind)
        fks = inspector.get_foreign_keys("capstone_submissions")
        fk_tables = {fk["referred_table"] for fk in fks}
        assert "users" in fk_tables, "Should have FK to users"
        assert "certification_levels" in fk_tables, "Should have FK to certification_levels"
        # reviewer_id should also reference users
        fk_columns = {fk["constrained_columns"][0]: fk["referred_table"] for fk in fks}
        assert fk_columns.get("reviewer_id") == "users", "reviewer_id should have FK to users"

    def test_certificates_cert_number_unique(self, test_db):
        """AC37: cert_number should be unique."""
        from sqlalchemy.exc import IntegrityError

        from app.models.certification import Certificate, CertificationLevel

        # Create a level first
        level = CertificationLevel(
            name="L1 Beginner",
            description="Beginner level",
            required_courses=[],
            min_average_score=70.0,
            order=1,
            is_active=True,
        )
        test_db.add(level)
        test_db.flush()

        cert1 = Certificate(
            user_id=1,
            level_id=level.id,
            cert_number="CERT-001",
            is_valid=True,
        )
        test_db.add(cert1)
        test_db.flush()

        cert2 = Certificate(
            user_id=1,
            level_id=level.id,
            cert_number="CERT-001",  # duplicate
            is_valid=True,
        )
        test_db.add(cert2)
        with pytest.raises(IntegrityError):
            test_db.flush()
        test_db.rollback()


class TestL1AutoEvaluation:
    """T17: AC30 — L1 自动评定: check required courses + average score threshold."""

    def test_auto_approve_when_all_courses_completed_and_score_above_threshold(
        self, test_db, test_user
    ):
        """User completes all required courses with high scores → auto-approved."""
        from app.models import Chapter, Course, Lab, LabSubmission, LearningProgress
        from app.models.certification import CertificationApplication, CertificationLevel
        from app.services.certificate import certificate_service

        user_id = test_user["user"]["id"]

        # Create 2 required courses
        course1 = Course(
            title="Course 1",
            description="C1",
            level="beginner",
            category="python",
            is_published=True,
        )
        course2 = Course(
            title="Course 2",
            description="C2",
            level="beginner",
            category="python",
            is_published=True,
        )
        test_db.add_all([course1, course2])
        test_db.flush()

        # Each course has 2 chapters, each with a lab
        for course in [course1, course2]:
            for i in range(2):
                chapter = Chapter(
                    course_id=course.id,
                    title=f"Ch {i+1}",
                    content="Content",
                    order_index=i,
                    chapter_type="lab",
                )
                test_db.add(chapter)
                test_db.flush()
                lab = Lab(
                    chapter_id=chapter.id,
                    title=f"Lab {i+1}",
                    description="Lab desc",
                    test_cases=[],
                )
                test_db.add(lab)
        test_db.flush()

        # Get all chapters and labs
        chapters = test_db.query(Chapter).all()
        labs = test_db.query(Lab).all()

        # Mark all chapters completed
        for ch in chapters:
            prog = LearningProgress(
                user_id=user_id,
                chapter_id=ch.id,
                status="completed",
            )
            test_db.add(prog)

        # Create lab submissions with high scores
        for lab in labs:
            sub = LabSubmission(
                user_id=user_id,
                lab_id=lab.id,
                code="print('hello')",
                status="passed",
                score=90.0,
                passed=True,
            )
            test_db.add(sub)

        # Create certification level L1 with required courses
        level = CertificationLevel(
            name="L1 AI Foundations",
            description="L1 certification",
            required_courses=[course1.id, course2.id],
            min_average_score=80.0,
            order=1,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        # Call auto_evaluate_l1
        result = certificate_service.auto_evaluate_l1(test_db, user_id, level.id)

        # Verify auto-approved
        assert result["status"] == "approved"
        assert result["all_completed"] is True
        assert result["avg_score"] >= level.min_average_score

        # Verify application record was created
        application = (
            test_db.query(CertificationApplication)
            .filter_by(user_id=user_id, level_id=level.id)
            .first()
        )
        assert application is not None
        assert application.status == "approved"
        assert application.evaluation_data is not None
        assert "avg_score" in application.evaluation_data
        assert "all_completed" in application.evaluation_data

    def test_fail_when_not_all_chapters_completed(self, test_db, test_user):
        """User hasn't completed all chapters → fail with reason."""
        from app.models import Chapter, Course, Lab, LearningProgress
        from app.models.certification import CertificationApplication, CertificationLevel
        from app.services.certificate import certificate_service

        user_id = test_user["user"]["id"]

        course = Course(
            title="Course 1",
            description="C1",
            level="beginner",
            category="python",
            is_published=True,
        )
        test_db.add(course)
        test_db.flush()

        # Create 2 chapters
        for i in range(2):
            chapter = Chapter(
                course_id=course.id,
                title=f"Ch {i+1}",
                content="Content",
                order_index=i,
                chapter_type="lab",
            )
            test_db.add(chapter)
            test_db.flush()
            lab = Lab(chapter_id=chapter.id, title=f"Lab {i+1}", description="Lab", test_cases=[])
            test_db.add(lab)

        chapters = test_db.query(Chapter).all()

        # Only complete first chapter
        prog = LearningProgress(
            user_id=user_id,
            chapter_id=chapters[0].id,
            status="completed",
        )
        test_db.add(prog)
        # Second chapter not completed

        level = CertificationLevel(
            name="L1 AI Foundations",
            description="L1 certification",
            required_courses=[course.id],
            min_average_score=70.0,
            order=1,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        result = certificate_service.auto_evaluate_l1(test_db, user_id, level.id)

        assert result["status"] == "failed"
        assert result["all_completed"] is False
        assert "completed" in result["reason"].lower()

        # No approved application should be created
        approved_app = (
            test_db.query(CertificationApplication)
            .filter_by(user_id=user_id, level_id=level.id, status="approved")
            .first()
        )
        assert approved_app is None

    def test_fail_when_average_score_below_threshold(self, test_db, test_user):
        """All courses completed but average score below threshold → fail."""
        from app.models import Chapter, Course, Lab, LabSubmission, LearningProgress
        from app.models.certification import CertificationApplication, CertificationLevel
        from app.services.certificate import certificate_service

        user_id = test_user["user"]["id"]

        course = Course(
            title="Course 1",
            description="C1",
            level="beginner",
            category="python",
            is_published=True,
        )
        test_db.add(course)
        test_db.flush()

        # 1 chapter with lab
        chapter = Chapter(
            course_id=course.id,
            title="Ch 1",
            content="Content",
            order_index=0,
            chapter_type="lab",
        )
        test_db.add(chapter)
        test_db.flush()
        lab = Lab(chapter_id=chapter.id, title="Lab 1", description="Lab", test_cases=[])
        test_db.add(lab)
        test_db.flush()

        # Complete the chapter
        prog = LearningProgress(
            user_id=user_id,
            chapter_id=chapter.id,
            status="completed",
        )
        test_db.add(prog)

        # Low score submission
        sub = LabSubmission(
            user_id=user_id,
            lab_id=lab.id,
            code="print('hello')",
            status="passed",
            score=55.0,
            passed=True,
        )
        test_db.add(sub)

        level = CertificationLevel(
            name="L1 AI Foundations",
            description="L1 certification",
            required_courses=[course.id],
            min_average_score=70.0,
            order=1,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        result = certificate_service.auto_evaluate_l1(test_db, user_id, level.id)

        assert result["status"] == "failed"
        assert result["all_completed"] is True
        assert result["avg_score"] < level.min_average_score
        assert (
            "score" in result["reason"].lower()
            or "平均分" in result["reason"]
            or "score" in result["reason"]
        )

        # No approved application
        approved_app = (
            test_db.query(CertificationApplication)
            .filter_by(user_id=user_id, level_id=level.id, status="approved")
            .first()
        )
        assert approved_app is None

    def test_fail_when_level_not_found(self, test_db, test_user):
        """Non-existent level → returns error."""
        from app.services.certificate import certificate_service

        result = certificate_service.auto_evaluate_l1(test_db, test_user["user"]["id"], 99999)
        assert result["status"] == "error"
        assert (
            "not found" in result["reason"].lower()
            or "not found" in result.get("message", "").lower()
        )

    def test_auto_evaluate_l1_with_no_required_courses(self, test_db, test_user):
        """Level with empty required_courses → auto-approved (trivially)."""
        from app.models.certification import CertificationApplication, CertificationLevel
        from app.services.certificate import certificate_service

        user_id = test_user["user"]["id"]

        level = CertificationLevel(
            name="L1 Empty",
            description="No required courses",
            required_courses=[],
            min_average_score=0.0,
            order=1,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        result = certificate_service.auto_evaluate_l1(test_db, user_id, level.id)

        assert result["status"] == "approved"
        assert result["all_completed"] is True
        assert result["avg_score"] == 0.0

        application = (
            test_db.query(CertificationApplication)
            .filter_by(user_id=user_id, level_id=level.id)
            .first()
        )
        assert application is not None
        assert application.status == "approved"
