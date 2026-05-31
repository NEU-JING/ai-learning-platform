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
