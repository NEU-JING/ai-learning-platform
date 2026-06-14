"""Tests for Sandbox module database models (S1)."""

import pytest
from sqlalchemy import text

from app.models import (
    ExecutionRequest,
    ExternalExecution,
    SandboxProvider,
    VerificationTask,
)


class TestSandboxModels:
    """Verify all four sandbox tables exist with correct columns."""

    def test_execution_requests_table_exists(self, test_db):
        """S1: execution_requests table has expected columns."""
        result = test_db.execute(text("SELECT * FROM execution_requests LIMIT 0"))
        columns = {col[0] for col in result.cursor.description}
        expected = {
            "id", "user_id", "lab_id", "layer", "code", "language",
            "resources", "status", "result", "logs",
            "started_at", "completed_at", "created_at",
        }
        assert expected.issubset(columns), f"Missing: {expected - columns}"

    def test_external_executions_table_exists(self, test_db):
        """S1: external_executions table has expected columns."""
        result = test_db.execute(text("SELECT * FROM external_executions LIMIT 0"))
        columns = {col[0] for col in result.cursor.description}
        expected = {
            "id", "request_id", "provider", "external_job_id",
            "artifacts", "status", "submitted_at", "completed_at",
        }
        assert expected.issubset(columns), f"Missing: {expected - columns}"

    def test_verification_tasks_table_exists(self, test_db):
        """S1: verification_tasks table has expected columns."""
        result = test_db.execute(text("SELECT * FROM verification_tasks LIMIT 0"))
        columns = {col[0] for col in result.cursor.description}
        expected = {
            "id", "request_id", "model_url", "dataset",
            "metrics", "audit_log", "status", "passed", "verified_at",
        }
        assert expected.issubset(columns), f"Missing: {expected - columns}"

    def test_sandbox_providers_table_exists(self, test_db):
        """S1: sandbox_providers table has expected columns."""
        result = test_db.execute(text("SELECT * FROM sandbox_providers LIMIT 0"))
        columns = {col[0] for col in result.cursor.description}
        expected = {
            "id", "name", "layer", "is_healthy",
            "last_health_check", "failure_count", "config",
        }
        assert expected.issubset(columns), f"Missing: {expected - columns}"

    def test_create_execution_request(self, test_db, test_user):
        """S1: Can create and persist an execution request."""
        req = ExecutionRequest(
            user_id=test_user["user"]["id"],
            layer="A",
            code="print('hello')",
            language="python",
            status="pending",
        )
        test_db.add(req)
        test_db.commit()
        test_db.refresh(req)

        assert req.id is not None
        assert req.user_id == test_user["user"]["id"]
        assert req.layer == "A"
        assert req.code == "print('hello')"
        assert req.status == "pending"
        assert req.language == "python"
        assert req.created_at is not None

    def test_create_external_execution(self, test_db, test_user):
        """S1: Can create an external execution linked to a request."""
        req = ExecutionRequest(
            user_id=test_user["user"]["id"],
            layer="B",
            code="",
            status="pending",
        )
        test_db.add(req)
        test_db.commit()
        test_db.refresh(req)

        ext = ExternalExecution(
            request_id=req.id,
            provider="kaggle",
            external_job_id="kg-12345",
            status="queued",
        )
        test_db.add(ext)
        test_db.commit()
        test_db.refresh(ext)

        assert ext.id is not None
        assert ext.request_id == req.id
        assert ext.provider == "kaggle"
        assert ext.status == "queued"

    def test_create_verification_task(self, test_db, test_user):
        """S1: Can create a verification task linked to a request."""
        req = ExecutionRequest(
            user_id=test_user["user"]["id"],
            layer="C",
            code="",
            status="pending",
        )
        test_db.add(req)
        test_db.commit()
        test_db.refresh(req)

        vt = VerificationTask(
            request_id=req.id,
            model_url="https://example.com/model.pth",
            dataset="mnist",
            status="pending",
        )
        test_db.add(vt)
        test_db.commit()
        test_db.refresh(vt)

        assert vt.id is not None
        assert vt.request_id == req.id
        assert vt.model_url == "https://example.com/model.pth"
        assert vt.dataset == "mnist"
        assert vt.status == "pending"

    def test_create_sandbox_provider(self, test_db):
        """S1: Can create a sandbox provider record."""
        provider = SandboxProvider(
            name="local",
            layer="A",
            is_healthy=True,
            failure_count=0,
        )
        test_db.add(provider)
        test_db.commit()
        test_db.refresh(provider)

        assert provider.id is not None
        assert provider.name == "local"
        assert provider.layer == "A"
        assert provider.is_healthy is True
        assert provider.failure_count == 0

    def test_sandbox_provider_unique_name(self, test_db):
        """S1: Provider name must be unique."""
        p1 = SandboxProvider(name="kaggle", layer="B", is_healthy=True)
        test_db.add(p1)
        test_db.commit()

        p2 = SandboxProvider(name="kaggle", layer="B", is_healthy=True)
        test_db.add(p2)
        with pytest.raises(Exception):
            test_db.commit()
        test_db.rollback()

    def test_execution_request_defaults(self, test_db, test_user):
        """S1: Verify default values for execution request."""
        req = ExecutionRequest(
            user_id=test_user["user"]["id"],
            layer="A",
        )
        test_db.add(req)
        test_db.commit()
        test_db.refresh(req)

        assert req.status == "pending"
        assert req.language == "python"
        assert req.created_at is not None
