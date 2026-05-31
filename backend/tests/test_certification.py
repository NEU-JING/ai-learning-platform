"""Test Certification module — T16, T17, T18.

T16: Database tables
- AC30: certification_levels table
- AC31: certification_applications table
- AC32: certificates table
- AC33: capstone_submissions table
- AC34-AC37: Foreign key relationships

T17: L1 auto evaluation
- AC30: auto_evaluate_l1 service

T18: L2 Capstone review
- AC31: Capstone submit + AI review + human review flow
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


# ── T18: L2 Capstone Review ───────────────────────────────────────────────────


class TestCapstoneSubmitService:
    """T18: AC31 — submit_capstone service method."""

    def test_submit_capstone_creates_record(self, test_db, test_user):
        """Submit capstone → creates CapstoneSubmission with status='submitted'."""
        from app.models.certification import CapstoneSubmission, CertificationLevel
        from app.services.certificate import certificate_service

        user_id = test_user["user"]["id"]

        # Create L2 level
        level = CertificationLevel(
            name="L2 AI Engineer",
            description="L2 certification",
            required_courses=[],
            min_average_score=75.0,
            order=2,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        result = certificate_service.submit_capstone(
            db=test_db,
            user_id=user_id,
            level_id=level.id,
            title="My Capstone Project",
            description="An awesome AI project",
            repository_url="https://github.com/user/capstone",
            submission_data={"framework": "PyTorch", "dataset": "ImageNet"},
        )

        assert result["status"] == "submitted"
        assert "id" in result
        assert result["title"] == "My Capstone Project"
        assert result["level_id"] == level.id

        # Verify DB record
        submission = test_db.query(CapstoneSubmission).filter_by(id=result["id"]).first()
        assert submission is not None
        assert submission.status == "submitted"
        assert submission.title == "My Capstone Project"
        assert submission.repository_url == "https://github.com/user/capstone"
        assert submission.submission_data == {"framework": "PyTorch", "dataset": "ImageNet"}

    def test_submit_capstone_level_not_found(self, test_db, test_user):
        """Submit to non-existent level → raises ValueError."""
        from app.services.certificate import certificate_service

        with pytest.raises(ValueError, match="not found"):
            certificate_service.submit_capstone(
                db=test_db,
                user_id=test_user["user"]["id"],
                level_id=999,
                title="Project",
                description="Desc",
                repository_url="https://github.com/user/proj",
                submission_data={},
            )

    def test_submit_capstone_missing_title(self, test_db, test_user):
        """Submit with empty title → raises ValueError."""
        from app.models.certification import CertificationLevel
        from app.services.certificate import certificate_service

        level = CertificationLevel(
            name="L2 AI Engineer",
            description="L2",
            required_courses=[],
            min_average_score=75.0,
            order=2,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        with pytest.raises(ValueError, match="title"):
            certificate_service.submit_capstone(
                db=test_db,
                user_id=test_user["user"]["id"],
                level_id=level.id,
                title="",
                description="Desc",
                repository_url="https://github.com/user/proj",
                submission_data={},
            )


class TestCapstoneAIReviewService:
    """T18: AC31 — ai_review_capstone service method."""

    def test_ai_review_updates_submission(self, test_db, test_user):
        """AI review → updates status to 'reviewing' then back, sets ai_review JSON."""
        from app.models.certification import CapstoneSubmission, CertificationLevel
        from app.services.certificate import certificate_service

        user_id = test_user["user"]["id"]

        level = CertificationLevel(
            name="L2 AI Engineer",
            description="L2",
            required_courses=[],
            min_average_score=75.0,
            order=2,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        # Create submission
        sub = CapstoneSubmission(
            user_id=user_id,
            level_id=level.id,
            title="Capstone Project",
            description="An AI project",
            repository_url="https://github.com/user/proj",
            submission_data={"framework": "PyTorch"},
            status="submitted",
        )
        test_db.add(sub)
        test_db.commit()

        result = certificate_service.ai_review_capstone(test_db, sub.id)

        assert result["status"] == "reviewed"
        assert "ai_review" in result

        # Check AI review content
        ai_review = result["ai_review"]
        assert "quality_score" in ai_review
        assert "complexity_score" in ai_review
        assert "completeness_score" in ai_review
        assert "summary" in ai_review
        assert 0 <= ai_review["quality_score"] <= 100
        assert 0 <= ai_review["complexity_score"] <= 100
        assert 0 <= ai_review["completeness_score"] <= 100

        # DB should be updated
        submission_db = test_db.query(CapstoneSubmission).filter_by(id=sub.id).first()
        assert submission_db.ai_review is not None
        assert submission_db.ai_review["quality_score"] == ai_review["quality_score"]

    def test_ai_review_submission_not_found(self, test_db, test_user):
        """AI review non-existent submission → raises ValueError."""
        from app.services.certificate import certificate_service

        with pytest.raises(ValueError, match="not found"):
            certificate_service.ai_review_capstone(test_db, 99999)

    def test_ai_review_already_reviewed_returns_existing(self, test_db, test_user):
        """AI review on already-reviewed submission → returns existing review."""
        from app.models.certification import CapstoneSubmission, CertificationLevel
        from app.services.certificate import certificate_service

        user_id = test_user["user"]["id"]

        level = CertificationLevel(
            name="L2 AI Engineer",
            description="L2",
            required_courses=[],
            min_average_score=75.0,
            order=2,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        existing_review = {
            "quality_score": 85,
            "complexity_score": 75,
            "completeness_score": 90,
            "summary": "Already reviewed",
        }

        sub = CapstoneSubmission(
            user_id=user_id,
            level_id=level.id,
            title="Capstone Project",
            description="An AI project",
            repository_url="https://github.com/user/proj",
            submission_data={},
            status="submitted",
            ai_review=existing_review,
        )
        test_db.add(sub)
        test_db.commit()

        result = certificate_service.ai_review_capstone(test_db, sub.id)

        assert result["ai_review"] == existing_review


class TestCapstoneApproveRejectService:
    """T18: AC31 — approve_capstone and reject_capstone service methods."""

    def test_approve_capstone_sets_status(self, test_db, test_user, test_user_other):
        """Approve → status='approved', reviewer info set."""
        from app.models.certification import CapstoneSubmission, CertificationLevel
        from app.services.certificate import certificate_service

        user_id = test_user["user"]["id"]
        reviewer_id = test_user_other["id"]

        level = CertificationLevel(
            name="L2 AI Engineer",
            description="L2",
            required_courses=[],
            min_average_score=75.0,
            order=2,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        sub = CapstoneSubmission(
            user_id=user_id,
            level_id=level.id,
            title="Capstone Project",
            description="An AI project",
            repository_url="https://github.com/user/proj",
            submission_data={},
            status="submitted",
        )
        test_db.add(sub)
        test_db.commit()

        result = certificate_service.approve_capstone(test_db, sub.id, reviewer_id, "Great work!")

        assert result["status"] == "approved"
        assert result["reviewer_id"] == reviewer_id
        assert result["reviewer_notes"] == "Great work!"

        # DB verification
        submission_db = test_db.query(CapstoneSubmission).filter_by(id=sub.id).first()
        assert submission_db.status == "approved"
        assert submission_db.reviewer_id == reviewer_id
        assert submission_db.reviewer_notes == "Great work!"

    def test_reject_capstone_sets_status(self, test_db, test_user, test_user_other):
        """Reject → status='rejected', reviewer info set."""
        from app.models.certification import CapstoneSubmission, CertificationLevel
        from app.services.certificate import certificate_service

        user_id = test_user["user"]["id"]
        reviewer_id = test_user_other["id"]

        level = CertificationLevel(
            name="L2 AI Engineer",
            description="L2",
            required_courses=[],
            min_average_score=75.0,
            order=2,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        sub = CapstoneSubmission(
            user_id=user_id,
            level_id=level.id,
            title="Capstone Project",
            description="An AI project",
            repository_url="https://github.com/user/proj",
            submission_data={},
            status="submitted",
        )
        test_db.add(sub)
        test_db.commit()

        result = certificate_service.reject_capstone(
            test_db, sub.id, reviewer_id, "Needs improvement"
        )

        assert result["status"] == "rejected"
        assert result["reviewer_id"] == reviewer_id
        assert result["reviewer_notes"] == "Needs improvement"

        # DB verification
        submission_db = test_db.query(CapstoneSubmission).filter_by(id=sub.id).first()
        assert submission_db.status == "rejected"
        assert submission_db.reviewer_id == reviewer_id

    def test_approve_capstone_not_found(self, test_db, test_user, test_user_other):
        """Approve non-existent submission → raises ValueError."""
        from app.services.certificate import certificate_service

        with pytest.raises(ValueError, match="not found"):
            certificate_service.approve_capstone(test_db, 99999, test_user_other["id"], "notes")

    def test_reject_already_approved_raises(self, test_db, test_user, test_user_other):
        """Reject already-approved submission → raises ValueError."""
        from app.models.certification import CapstoneSubmission, CertificationLevel
        from app.services.certificate import certificate_service

        user_id = test_user["user"]["id"]

        level = CertificationLevel(
            name="L2 AI Engineer",
            description="L2",
            required_courses=[],
            min_average_score=75.0,
            order=2,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()

        sub = CapstoneSubmission(
            user_id=user_id,
            level_id=level.id,
            title="Capstone Project",
            description="An AI project",
            repository_url="https://github.com/user/proj",
            submission_data={},
            status="approved",
        )
        test_db.add(sub)
        test_db.commit()

        with pytest.raises(ValueError, match="already been approved"):
            certificate_service.reject_capstone(test_db, sub.id, test_user_other["id"], "Too late")


class TestCapstoneAPI:
    """T18: AC31 — Capstone API endpoints via TestClient."""

    def _create_level(self, test_db, name="L2 AI Engineer", order=2):
        from app.models.certification import CertificationLevel

        level = CertificationLevel(
            name=name,
            description="L2 certification",
            required_courses=[],
            min_average_score=75.0,
            order=order,
            is_active=True,
        )
        test_db.add(level)
        test_db.commit()
        test_db.refresh(level)
        return level

    def test_submit_capstone_api(self, client, test_db, auth_headers):
        """POST /api/v1/capstone/submit → 200 with submission data."""
        level = self._create_level(test_db)

        response = client.post(
            "/api/v1/certificates/capstone/submit",
            json={
                "level_id": level.id,
                "title": "My Capstone Project",
                "description": "An AI project",
                "repository_url": "https://github.com/user/proj",
                "submission_data": {"framework": "PyTorch"},
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "submitted"
        assert data["title"] == "My Capstone Project"
        assert data["level_id"] == level.id

    def test_submit_capstone_api_missing_title(self, client, test_db, auth_headers):
        """POST /api/v1/capstone/submit with empty title → 422."""
        level = self._create_level(test_db)

        response = client.post(
            "/api/v1/certificates/capstone/submit",
            json={
                "level_id": level.id,
                "title": "",
                "description": "An AI project",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_submit_capstone_api_level_not_found(self, client, auth_headers):
        """POST /api/v1/capstone/submit with non-existent level → 404."""
        response = client.post(
            "/api/v1/certificates/capstone/submit",
            json={
                "level_id": 999,
                "title": "My Project",
                "description": "Desc",
            },
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_capstone_review_api(self, client, test_db, auth_headers, test_user):
        """GET /api/v1/capstone/review/{id} → 200 with submission details."""
        from app.models.certification import CapstoneSubmission

        level = self._create_level(test_db)
        user_id = test_user["user"]["id"]

        sub = CapstoneSubmission(
            user_id=user_id,
            level_id=level.id,
            title="My Capstone",
            description="Desc",
            repository_url="https://github.com/user/proj",
            submission_data={},
            status="submitted",
        )
        test_db.add(sub)
        test_db.commit()
        test_db.refresh(sub)

        response = client.get(
            f"/api/v1/certificates/capstone/review/{sub.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sub.id
        assert data["title"] == "My Capstone"
        assert data["status"] == "submitted"

    def test_get_capstone_review_not_found(self, client, auth_headers):
        """GET /api/v1/capstone/review/{id} → 404 for non-existent."""
        response = client.get(
            "/api/v1/certificates/capstone/review/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_approve_capstone_api(self, client, test_db, auth_headers_other, test_user):
        """POST /api/v1/capstone/review/{id}/approve → 200 with approved status."""
        from app.models.certification import CapstoneSubmission

        level = self._create_level(test_db)
        user_id = test_user["user"]["id"]

        sub = CapstoneSubmission(
            user_id=user_id,
            level_id=level.id,
            title="My Capstone",
            description="Desc",
            submission_data={},
            status="submitted",
        )
        test_db.add(sub)
        test_db.commit()
        test_db.refresh(sub)

        response = client.post(
            f"/api/v1/certificates/capstone/review/{sub.id}/approve",
            json={"notes": "Excellent work!"},
            headers=auth_headers_other,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert "reviewer_notes" in data

    def test_reject_capstone_api(self, client, test_db, auth_headers_other, test_user):
        """POST /api/v1/capstone/review/{id}/reject → 200 with rejected status."""
        from app.models.certification import CapstoneSubmission

        level = self._create_level(test_db)
        user_id = test_user["user"]["id"]

        sub = CapstoneSubmission(
            user_id=user_id,
            level_id=level.id,
            title="My Capstone",
            description="Desc",
            submission_data={},
            status="submitted",
        )
        test_db.add(sub)
        test_db.commit()
        test_db.refresh(sub)

        response = client.post(
            f"/api/v1/certificates/capstone/review/{sub.id}/reject",
            json={"notes": "Needs improvement"},
            headers=auth_headers_other,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"

    def test_ai_review_api(self, client, test_db, auth_headers, test_user):
        """POST /api/v1/capstone/review/{id}/ai-review → triggers AI review."""
        from app.models.certification import CapstoneSubmission

        level = self._create_level(test_db)
        user_id = test_user["user"]["id"]

        sub = CapstoneSubmission(
            user_id=user_id,
            level_id=level.id,
            title="My Capstone",
            description="Desc",
            repository_url="https://github.com/user/proj",
            submission_data={"framework": "PyTorch"},
            status="submitted",
        )
        test_db.add(sub)
        test_db.commit()
        test_db.refresh(sub)

        response = client.post(
            f"/api/v1/certificates/capstone/review/{sub.id}/ai-review",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reviewed"
        assert "ai_review" in data
        assert "quality_score" in data["ai_review"]
        assert "complexity_score" in data["ai_review"]
        assert "completeness_score" in data["ai_review"]
        assert 0 <= data["ai_review"]["quality_score"] <= 100

    def test_ai_review_api_not_found(self, client, auth_headers):
        """POST /api/v1/capstone/review/{id}/ai-review → 404 for non-existent."""
        response = client.post(
            "/api/v1/certificates/capstone/review/99999/ai-review",
            headers=auth_headers,
        )

        assert response.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# T19: AC37 — ECDSA Certificate Signature
# ══════════════════════════════════════════════════════════════════════════════


class TestECDSACertificateSignature:
    """T19: AC37 — ECDSA-SHA256 digital signature for certificate anti-counterfeiting."""

    def test_certificate_signature_produces_valid_signature(self):
        """Sign certificate data → returns a non-empty base64 signature string."""
        from app.services.certificate import certificate_service

        cert_data = {
            "cert_number": "CERT-TEST-001",
            "user_id": 42,
            "level_id": 1,
            "issue_date": "2026-01-15T10:00:00Z",
        }

        signature = certificate_service.sign_certificate(cert_data)

        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) > 20  # ECDSA signature should be substantial

    def test_certificate_verification_returns_true_for_valid_signature(self):
        """Sign then verify → returns True for intact data."""
        from app.services.certificate import certificate_service

        cert_data = {
            "cert_number": "CERT-TEST-002",
            "user_id": 42,
            "level_id": 2,
            "issue_date": "2026-02-20T12:00:00Z",
        }

        signature = certificate_service.sign_certificate(cert_data)
        is_valid = certificate_service.verify_certificate_signature(
            signature=signature,
            cert_data=cert_data,
        )

        assert is_valid is True

    def test_certificate_tamper_detection_returns_false(self):
        """Modify signed data → verification returns False (tamper detected)."""
        from app.services.certificate import certificate_service

        original_data = {
            "cert_number": "CERT-TEST-003",
            "user_id": 42,
            "level_id": 3,
            "issue_date": "2026-03-25T14:00:00Z",
        }

        signature = certificate_service.sign_certificate(original_data)

        # Tamper: change user_id
        tampered_data = {
            **original_data,
            "user_id": 999,
        }
        is_valid_tampered = certificate_service.verify_certificate_signature(
            signature=signature,
            cert_data=tampered_data,
        )

        assert is_valid_tampered is False, "Tampered user_id should fail verification"

        # Tamper: change cert_number
        tampered_data2 = {
            **original_data,
            "cert_number": "FAKE-CERT-999",
        }
        is_valid_tampered2 = certificate_service.verify_certificate_signature(
            signature=signature,
            cert_data=tampered_data2,
        )

        assert is_valid_tampered2 is False, "Tampered cert_number should fail verification"

        # Tamper: change issue_date
        tampered_data3 = {
            **original_data,
            "issue_date": "2025-01-01T00:00:00Z",
        }
        is_valid_tampered3 = certificate_service.verify_certificate_signature(
            signature=signature,
            cert_data=tampered_data3,
        )

        assert is_valid_tampered3 is False, "Tampered issue_date should fail verification"

    def test_ecdsa_key_is_persistent(self):
        """The signing key is persistent — signatures from same key both verify.

        ECDSA uses random nonces, so signature strings differ even for identical
        data. The correct test for key persistence is that both signatures
        verify against the same public key.
        """
        from app.services.certificate import certificate_service

        cert_data = {
            "cert_number": "CERT-TEST-004",
            "user_id": 1,
            "level_id": 1,
            "issue_date": "2026-01-01T00:00:00Z",
        }

        sig1 = certificate_service.sign_certificate(cert_data)
        sig2 = certificate_service.sign_certificate(cert_data)

        # Signatures may differ (random nonces), but both must verify
        assert certificate_service.verify_certificate_signature(
            signature=sig1, cert_data=cert_data
        ), "First signature should verify"
        assert certificate_service.verify_certificate_signature(
            signature=sig2, cert_data=cert_data
        ), "Second signature should verify"

    def test_different_data_produces_different_signature(self):
        """Different certificate data → different signatures."""
        from app.services.certificate import certificate_service

        data1 = {
            "cert_number": "CERT-A",
            "user_id": 1,
            "level_id": 1,
            "issue_date": "2026-01-01T00:00:00Z",
        }
        data2 = {
            "cert_number": "CERT-B",
            "user_id": 2,
            "level_id": 2,
            "issue_date": "2026-06-01T00:00:00Z",
        }

        sig1 = certificate_service.sign_certificate(data1)
        sig2 = certificate_service.sign_certificate(data2)

        assert sig1 != sig2, "Different data should produce different signatures"
