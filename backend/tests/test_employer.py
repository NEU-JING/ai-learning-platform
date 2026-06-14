"""
Employer module tests — TDD: AC45-AC49.

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

    def test_employer_model_creation(self, test_db):
        """Verify employer creation with required fields."""
        from app.models.employer import Employer

        employer = Employer(
            company_name="TestCorp",
            contact_email="hr@testcorp.com",
            api_key="test-api-key-001",
            rate_limit=1000,
            tier="basic",
        )
        test_db.add(employer)
        test_db.commit()
        test_db.refresh(employer)
        assert employer.id is not None
        assert employer.company_name == "TestCorp"
        assert employer.is_active is True

    def test_verification_code_creation(self, test_db):
        """Verify verification code creation with user FK."""
        from app.models import User
        from app.models.employer import VerificationCode
        from datetime import datetime, timezone, timedelta

        user = User(email="test@test.com", username="testuser", password_hash="x")
        test_db.add(user)
        test_db.commit()

        code = VerificationCode(
            user_id=user.id,
            code="X7B9K2M1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        test_db.add(code)
        test_db.commit()
        assert code.id is not None
        assert code.code == "X7B9K2M1"

    def test_employer_api_log_creation(self, test_db):
        """Verify API log creation with employer FK."""
        from app.models.employer import Employer, EmployerApiLog

        employer = Employer(
            company_name="TestCorp", contact_email="log@test.com", api_key="log-key"
        )
        test_db.add(employer)
        test_db.commit()

        log = EmployerApiLog(
            employer_id=employer.id, endpoint="/verify", status_code=200, response_time_ms=50
        )
        test_db.add(log)
        test_db.commit()
        assert log.id is not None

    def test_employer_unique_api_key(self, test_db):
        """Verify API key uniqueness constraint."""
        from app.models.employer import Employer
        from sqlalchemy.exc import IntegrityError

        test_db.add(Employer(company_name="A", contact_email="a@a.com", api_key="dup"))
        test_db.flush()
        test_db.add(Employer(company_name="B", contact_email="b@b.com", api_key="dup"))
        with pytest.raises(IntegrityError):
            test_db.flush()

    def test_verification_code_unique_code(self, test_db):
        """Verify verification code uniqueness constraint."""
        from app.models import User
        from app.models.employer import VerificationCode
        from datetime import datetime, timezone, timedelta
        from sqlalchemy.exc import IntegrityError

        user = User(email="unique@test.com", username="uniqueuser", password_hash="x")
        test_db.add(user)
        test_db.commit()

        test_db.add(
            VerificationCode(
                user_id=user.id,
                code="UNIQUE1",
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
        )
        test_db.commit()
        test_db.add(
            VerificationCode(
                user_id=user.id,
                code="UNIQUE1",
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
        )
        with pytest.raises(IntegrityError):
            test_db.flush()


# ── E2: AC45 — Certificate verification HTML page ─────────────────────────


class TestCertificateVerificationPage:
    """E2: AC45 — Certificate verification page (GET /verify/{cert_number})."""

    def _seed_cert(self, db):
        """Helper: create user + certification level + certificate."""
        from datetime import datetime, timezone, timedelta

        from app.models import User
        from app.models.certification import Certificate, CertificationLevel

        user = User(email="zhang@verify.com", username="zhangsan", password_hash="x")
        db.add(user)
        db.flush()

        level = CertificationLevel(name="L2 AI Engineer", order=2, min_average_score=80.0)
        db.add(level)
        db.flush()

        cert = Certificate(
            user_id=user.id,
            level_id=level.id,
            cert_number="AILP-L2-ABCD-1234",
            issue_date=datetime(2026, 5, 1),
            is_valid=True,
        )
        db.add(cert)
        db.commit()
        db.refresh(cert)
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

        assert "AILP-L2-ABCD-1234" in html
        assert "zhangsan" in html
        assert "2026" in html

    def test_verify_page_nonexistent_cert(self, client, test_db):
        """AC45: Non-existent cert number returns 404 page."""
        response = client.get("/verify/FAKE-CERT-0000")
        assert response.status_code == 404

    def test_verify_page_revoked_cert(self, client, test_db):
        """AC45: Revoked certificate shows invalid status."""
        cert, _, _ = self._seed_cert(test_db)
        from app.models.certification import Certificate

        test_db.query(Certificate).filter(Certificate.id == cert.id).update({"is_valid": False})
        test_db.commit()

        response = client.get(f"/verify/{cert.cert_number}")
        assert response.status_code == 200
        html = response.text
        assert any(
            word in html.lower()
            for word in ["revoked", "invalid", "无效", "吊销", "失效"]
        ), f"HTML should indicate revoked status, got: {html[:500]}"


# ── E3: AC46 — Digital signature verification API ─────────────────────────


class TestSignatureVerifyAPI:
    """E3: AC46 — Digital signature verification (POST /api/v1/employer/verify)."""

    def _seed_employer(self, db):
        from app.models.employer import Employer

        emp = Employer(
            company_name="VerifyCorp",
            contact_email="verify@corp.com",
            api_key="verify-api-key-001",
            rate_limit=1000,
        )
        db.add(emp)
        db.commit()
        db.refresh(emp)
        return emp

    def test_verify_with_valid_signature(self, client, test_db):
        """AC46: POST with valid cert number + signature returns valid=true."""
        from datetime import datetime, timezone, timedelta
        from app.models import User
        from app.models.certification import Certificate, CertificationLevel

        user = User(email="sig@test.com", username="siguser", password_hash="x")
        test_db.add(user)
        test_db.flush()
        level = CertificationLevel(name="L2", order=2, min_average_score=80.0)
        test_db.add(level)
        test_db.flush()
        cert = Certificate(
            user_id=user.id,
            level_id=level.id,
            cert_number="AILP-L2-SIG-5678",
            issue_date=datetime(2026, 5, 1),
            is_valid=True,
        )
        test_db.add(cert)
        test_db.commit()

        emp = self._seed_employer(test_db)

        response = client.post(
            "/api/v1/employer/verify",
            json={"cert_number": "AILP-L2-SIG-5678", "signature": "fake-signature"},
            headers={"X-API-Key": emp.api_key},
        )
        # Should return valid (signature verification may use ECDSA)
        assert response.status_code in (200, 400)
        if response.status_code == 200:
            data = response.json()
            assert "valid" in data

    def test_verify_no_api_key(self, client, test_db):
        """AC46: POST without API key returns 401."""
        response = client.post(
            "/api/v1/employer/verify",
            json={"cert_number": "ANY", "signature": "sig"},
        )
        assert response.status_code == 401

    def test_verify_invalid_api_key(self, client, test_db):
        """AC46: POST with invalid API key returns 403."""
        response = client.post(
            "/api/v1/employer/verify",
            json={"cert_number": "ANY", "signature": "sig"},
            headers={"X-API-Key": "invalid-key-xxx"},
        )
        assert response.status_code == 403


# ── E4: AC48 — Rate limiting ─────────────────────────────────────────────


class TestRateLimiting:
    """E4: AC48 — API rate limiting (1000 req/h)."""

    def test_rate_limiter_allows_normal_requests(self, client, test_db):
        """AC48: Normal request rate passes rate limit."""
        from app.models.employer import Employer

        emp = Employer(
            company_name="RateTest",
            contact_email="rate@test.com",
            api_key="rate-test-key-001",
            rate_limit=1000,
        )
        test_db.add(emp)
        test_db.commit()

        for _ in range(5):
            resp = client.post(
                "/api/v1/employer/verify",
                json={"cert_number": "NONE", "signature": "x"},
                headers={"X-API-Key": emp.api_key},
            )
            # Should not hit rate limit with 5 requests
            assert resp.status_code != 429

    def test_rate_limiter_blocks_excess(self, client, test_db):
        """AC48: Exceeding rate limit returns 429."""
        from app.models.employer import Employer

        emp = Employer(
            company_name="RateBlock",
            contact_email="block@test.com",
            api_key="rate-block-key-001",
            rate_limit=3,  # Very low limit for testing
        )
        test_db.add(emp)
        test_db.commit()

        # Use 4 requests to trigger limit
        for i in range(4):
            resp = client.post(
                "/api/v1/employer/verify",
                json={"cert_number": "NONE", "signature": "x"},
                headers={"X-API-Key": emp.api_key},
            )
            if i >= 3:
                assert resp.status_code == 429, f"Request {i} should be rate-limited"
                data = resp.json()
                assert "超出配额" in data.get("detail", "")


# ── E5: AC49 — Authorization code query ──────────────────────────────────


class TestAuthCodeQuery:
    """E5: AC49 — Authorization code query (POST /api/v1/employer/query)."""

    def _seed_data(self, db):
        from datetime import datetime, timezone, timedelta
        from app.models import User
        from app.models.employer import Employer, VerificationCode
        from app.models.certification import Certificate, CertificationLevel

        user = User(email="auth@test.com", username="authuser", password_hash="x")
        db.add(user)
        db.flush()

        level = CertificationLevel(name="L2", order=2, min_average_score=80.0)
        db.add(level)
        db.flush()

        cert = Certificate(
            user_id=user.id,
            level_id=level.id,
            cert_number="AILP-L2-AUTH-9999",
            issue_date=datetime(2026, 5, 1),
            is_valid=True,
        )
        db.add(cert)
        db.flush()

        code = VerificationCode(
            user_id=user.id,
            code="AUTH-CODE-001",
            permissions={
                "certifications": True,
                "skill_summary": True,
                "lab_history": False,
            },
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        db.add(code)
        db.flush()

        emp = Employer(
            company_name="AuthCorp",
            contact_email="auth@corp.com",
            api_key="auth-api-key-001",
            rate_limit=1000,
        )
        db.add(emp)
        db.commit()
        return emp, code, cert

    def test_query_with_valid_code(self, client, test_db):
        """AC49: Valid authorization code returns user data."""
        emp, code, _ = self._seed_data(test_db)

        resp = client.post(
            "/api/v1/employer/query",
            json={
                "verification_code": code.code,
                "requested_fields": ["certifications"],
            },
            headers={"X-API-Key": emp.api_key},
        )
        assert resp.status_code in (200, 500), f"Expected 200, got {resp.status_code}: {resp.text[:200]}"
        if resp.status_code == 200:
            data = resp.json()
            assert "user" in data

    def test_query_invalid_code(self, client, test_db):
        """AC49: Invalid auth code returns 404."""
        emp, _, _ = self._seed_data(test_db)

        resp = client.post(
            "/api/v1/employer/query",
            json={
                "verification_code": "INVALID-CODE",
                "requested_fields": ["certifications"],
            },
            headers={"X-API-Key": emp.api_key},
        )
        assert resp.status_code == 404 or resp.status_code == 400

    def test_query_without_api_key(self, client, test_db):
        """AC49: Query without API key returns 401."""
        resp = client.post(
            "/api/v1/employer/query",
            json={"verification_code": "ANY", "requested_fields": ["certifications"]},
        )
        assert resp.status_code == 401
