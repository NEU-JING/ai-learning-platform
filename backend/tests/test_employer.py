"""Employer module tests — TDD: AC45-AC49.

Test strategies (RED → GREEN → REFACTOR):
E1: Tables exist
E2: Certificate verification HTML page (AC45)
E3: Digital signature verify API key auth (AC46)
E4: Rate limiting middleware (AC48)
E5: Authorization code query (AC49)
E6: Full coverage
"""

import pytest
from sqlalchemy import inspect


class TestEmployerTables:
    """E1: Verify employer-related tables exist."""

    def test_employers_table_exists(self, test_db):
        """Verify employers table is created."""
        inspector = inspect(test_db.bind)
        tables = inspector.get_table_names()
        assert "employers" in tables, f"employers table missing from {tables}"

    def test_verification_codes_table_exists(self, test_db):
        """Verify verification_codes table is created."""
        inspector = inspect(test_db.bind)
        tables = inspector.get_table_names()
        assert "verification_codes" in tables, f"verification_codes table missing from {tables}"

    def test_employer_api_logs_table_exists(self, test_db):
        """Verify employer_api_logs table is created."""
        inspector = inspect(test_db.bind)
        tables = inspector.get_table_names()
        assert "employer_api_logs" in tables, f"employer_api_logs table missing from {tables}"

    def test_employer_table_columns(self, test_db):
        """Verify employers table has expected columns."""
        inspector = inspect(test_db.bind)
        columns = {c["name"]: c for c in inspector.get_columns("employers")}
        expected = [
            "id", "company_name", "contact_email", "api_key",
            "rate_limit", "tier", "is_active", "created_at"
        ]
        for col in expected:
            assert col in columns, f"employers missing column: {col}"

    def test_verification_codes_columns(self, test_db):
        """Verify verification_codes table has expected columns."""
        inspector = inspect(test_db.bind)
        columns = {c["name"]: c for c in inspector.get_columns("verification_codes")}
        expected = [
            "id", "user_id", "code", "permissions",
            "expires_at", "used_by", "used_at", "created_at"
        ]
        for col in expected:
            assert col in columns, f"verification_codes missing column: {col}"

    def test_employer_api_logs_columns(self, test_db):
        """Verify employer_api_logs table has expected columns."""
        inspector = inspect(test_db.bind)
        columns = {c["name"]: c for c in inspector.get_columns("employer_api_logs")}
        expected = [
            "id", "employer_id", "endpoint", "status_code",
            "response_time_ms", "created_at"
        ]
        for col in expected:
            assert col in columns, f"employer_api_logs missing column: {col}"

    def test_employer_crud(self, test_db):
        """Verify we can create and query an employer record."""
        from app.models.employer import Employer

        emp = Employer(
            company_name="Test Corp",
            contact_email="test@corp.com",
            api_key="test-api-key-123",
            rate_limit=1000,
            tier="basic",
            is_active=True,
        )
        test_db.add(emp)
        test_db.commit()
        test_db.refresh(emp)

        assert emp.id is not None
        assert emp.company_name == "Test Corp"
        assert emp.api_key == "test-api-key-123"

        # Query back
        found = test_db.query(Employer).filter(Employer.api_key == "test-api-key-123").first()
        assert found is not None
        assert found.id == emp.id

    def test_verification_code_crud(self, test_db):
        """Verify we can create and query a verification_code record."""
        from app.models.employer import VerificationCode
        from datetime import datetime, timezone, timedelta

        vc = VerificationCode(
            user_id=1,
            code="X7B9K2M1",
            permissions={"certifications": True, "skill_summary": True, "lab_history": False},
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        test_db.add(vc)
        test_db.commit()
        test_db.refresh(vc)

        assert vc.id is not None
        assert vc.code == "X7B9K2M1"
        assert vc.permissions == {"certifications": True, "skill_summary": True, "lab_history": False}

    def test_employer_api_log_crud(self, test_db):
        """Verify we can create and query an API log record."""
        from app.models.employer import EmployerApiLog

        log = EmployerApiLog(
            employer_id=1,
            endpoint="/api/v1/employer/verify",
            status_code=200,
            response_time_ms=45,
        )
        test_db.add(log)
        test_db.commit()
        test_db.refresh(log)

        assert log.id is not None
        assert log.endpoint == "/api/v1/employer/verify"
        assert log.status_code == 200
