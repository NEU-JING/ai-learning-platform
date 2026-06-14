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


# ──────────────────────────────────────────────────────────────────────────────
# E2: Certificate verification HTML page (AC45)
# ──────────────────────────────────────────────────────────────────────────────


class TestCertificateVerificationPage:
    """E2: GET /verify/{cert_number} — AC45, renders public HTML verification page."""

    def _seed_cert(self, test_db):
        """Helper: create a certificate + user for verification page tests."""
        from app.models import User
        from app.models.certification import Certificate, CertificationLevel

        # Create user
        user = User(
            email="holder@example.com",
            username="certificate_holder",
            password_hash="hash",
            role="student",
            is_active=True,
        )
        test_db.add(user)
        test_db.flush()

        # Create level
        level = CertificationLevel(
            name="L2 AI Engineer",
            description="Level 2 certification",
            min_average_score=80.0,
            order=2,
            is_active=True,
        )
        test_db.add(level)
        test_db.flush()

        # Create certificate
        cert = Certificate(
            user_id=user.id,
            level_id=level.id,
            cert_number="AILP-L2-ABCD-1234",
            issue_date=__import__("datetime").datetime(2026, 5, 1),
            cert_metadata={
                "holder_name": "张三",
                "completed_labs": 45,
                "avg_score": 85.5,
            },
            signature="MEUCIQTestSignature123",
            is_valid=True,
        )
        test_db.add(cert)
        test_db.commit()
        test_db.refresh(cert)
        return cert, user, level

    def test_verify_page_returns_html(self, client, test_db):
        """AC45: GET /verify/{cert_number} returns HTML page (not JSON)."""
        cert, _, _ = self._seed_cert(test_db)

        response = client.get(f"/verify/{cert.cert_number}")
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type, f"Expected HTML, got {content_type}"

    def test_verify_page_contains_cert_info(self, client, test_db):
        """AC45: HTML page shows certificate holder, level, dates."""
        cert, _, _ = self._seed_cert(test_db)

        response = client.get(f"/verify/{cert.cert_number}")
        assert response.status_code == 200
        html = response.text

        # Check that key info is in the HTML
        assert "AILP-L2-ABCD-1234" in html
        assert "张三" in html
        assert "L2 AI Engineer" in html or "L2" in html
        assert "2026" in html  # issue date

    def test_verify_page_nonexistent_cert(self, client, test_db):
        """AC45: Non-existent cert number returns 404 page."""
        response = client.get("/verify/FAKE-CERT-0000")
        assert response.status_code == 404

    def test_verify_page_revoked_cert(self, client, test_db):
        """AC45: Revoked certificate shows invalid status."""
        cert, _, _ = self._seed_cert(test_db)

        # Revoke the cert
        from app.models.certification import Certificate
        test_db.query(Certificate).filter(
            Certificate.id == cert.id
        ).update({"is_valid": False})
        test_db.commit()

        response = client.get(f"/verify/{cert.cert_number}")
        assert response.status_code == 200
        html = response.text
        # Should indicate the certificate is invalid/revoked
        assert any(
            word in html.lower()
            for word in ["revoked", "invalid", "无效", "吊销", "失效"]
        ), f"HTML should indicate revoked status, got: {html[:500]}"
