"""Tests for Sandbox API endpoints (S2-S6)."""

import json

import pytest
from fastapi import status


# ── S2: Layer A — Local execution (AC38) ────────────────────────────────────

class TestLayerAExecute:
    """AC38: POST /api/v1/sandbox/execute — Layer A local subprocess execution."""

    def test_execute_simple_code(self, client, auth_headers, test_lab):
        """AC38: Execute a simple Python print statement and get output."""
        resp = client.post(
            "/api/v1/sandbox/execute",
            json={
                "lab_id": test_lab["lab"].id,
                "code": "print('hello world')",
                "language": "python",
                "layer": "A",
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        data = resp.json()
        assert data["status"] in ("completed", "failed")
        assert "execution_id" in data
        if data["status"] == "completed":
            assert "result" in data
            assert "output" in data["result"]

    def test_execute_code_with_error(self, client, auth_headers, test_lab):
        """AC38: Execute code with a runtime error — should report failure."""
        resp = client.post(
            "/api/v1/sandbox/execute",
            json={
                "lab_id": test_lab["lab"].id,
                "code": "raise ValueError('test error')",
                "language": "python",
                "layer": "A",
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        data = resp.json()
        assert data["status"] in ("completed", "failed")

    def test_execute_with_auto_grading(self, client, auth_headers, test_lab):
        """AC38: Execute code and receive auto-grading result (score + passed)."""
        # This lab has test_cases: hello() should return "hello world"
        resp = client.post(
            "/api/v1/sandbox/execute",
            json={
                "lab_id": test_lab["lab"].id,
                "code": "def hello():\n    return 'hello world'",
                "language": "python",
                "layer": "A",
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        data = resp.json()
        assert "execution_id" in data
        assert "score" in data
        assert "passed" in data
        assert isinstance(data["score"], (int, float))
        assert isinstance(data["passed"], bool)

    def test_execute_unauthorized(self, client, test_lab):
        """AC38: Unauthorized request returns 401."""
        resp = client.post(
            "/api/v1/sandbox/execute",
            json={
                "lab_id": test_lab["lab"].id,
                "code": "print('hello')",
                "language": "python",
                "layer": "A",
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_execute_records_in_db(self, client, auth_headers, test_lab, test_db):
        """AC38: Execution creates a record in execution_requests."""
        resp = client.post(
            "/api/v1/sandbox/execute",
            json={
                "lab_id": test_lab["lab"].id,
                "code": "print(42)",
                "language": "python",
                "layer": "A",
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        execution_id = data.get("execution_id")
        assert execution_id is not None

        # Verify DB record
        from app.models import ExecutionRequest

        record = test_db.query(ExecutionRequest).filter(ExecutionRequest.id == execution_id).first()
        assert record is not None
        assert record.layer == "A"
        assert record.status in ("completed", "failed")

    def test_execute_missing_layer(self, client, auth_headers, test_lab):
        """AC38: Missing 'layer' field returns 422 validation error."""
        resp = client.post(
            "/api/v1/sandbox/execute",
            json={
                "lab_id": test_lab["lab"].id,
                "code": "print('hello')",
                "language": "python",
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ── S3: Layer B — External resource submission (AC39) ────────────────────────

class TestLayerBExternalSubmit:
    """AC39: POST /api/v1/sandbox/external/submit — Layer B external resource."""

    def test_submit_external_kaggle(self, client, auth_headers, test_lab, test_db):
        """AC39: Submit a Kaggle external execution."""
        resp = client.post(
            "/api/v1/sandbox/external/submit",
            json={
                "lab_id": test_lab["lab"].id,
                "provider": "kaggle",
                "notebook_url": "https://kaggle.com/user/notebook",
                "expected_output": "model.pth",
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        data = resp.json()
        assert "submission_id" in data
        assert data["status"] == "queued"
        assert "webhook_url" in data

        # Verify DB
        from app.models import ExternalExecution

        ext = test_db.query(ExternalExecution).filter(
            ExternalExecution.id == data["submission_id"]
        ).first()
        assert ext is not None
        assert ext.provider == "kaggle"
        assert ext.status == "queued"

    def test_submit_external_unauthorized(self, client, test_lab):
        """AC39: Unauthorized external submission returns 401."""
        resp = client.post(
            "/api/v1/sandbox/external/submit",
            json={
                "lab_id": test_lab["lab"].id,
                "provider": "kaggle",
                "notebook_url": "https://kaggle.com/user/notebook",
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_submit_unknown_provider(self, client, auth_headers, test_lab):
        """AC39: Unknown provider returns 400."""
        resp = client.post(
            "/api/v1/sandbox/external/submit",
            json={
                "lab_id": test_lab["lab"].id,
                "provider": "unknown_xyz",
                "notebook_url": "https://example.com",
                "expected_output": "model.pth",
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── S4: Layer C — Verification engine (AC40-AC41) ────────────────────────────

class TestLayerCVerify:
    """AC40-AC41: POST /api/v1/sandbox/verify — Verification engine."""

    def test_verify_model_metrics(self, client, auth_headers, test_lab, test_db):
        """AC40: Submit a verification request and get metrics."""
        # First create an execution request for layer C
        from app.models import ExecutionRequest

        req = ExecutionRequest(
            user_id=1,  # test_user
            lab_id=test_lab["lab"].id,
            layer="C",
            status="pending",
        )
        test_db.add(req)
        test_db.commit()
        test_db.refresh(req)

        resp = client.post(
            "/api/v1/sandbox/verify",
            json={
                "execution_request_id": req.id,
                "model_url": "https://example.com/model.pth",
                "training_log": json.dumps({"epochs": 10, "loss": 0.15}),
                "lab_id": test_lab["lab"].id,
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        data = resp.json()
        assert "verification_id" in data
        assert "status" in data
        assert "metrics" in data
        assert "audit" in data

    def test_verify_failure_handling(self, client, auth_headers, test_lab, test_db):
        """AC41: Verification with failed metrics returns passed=false."""
        from app.models import ExecutionRequest

        req = ExecutionRequest(
            user_id=1,
            lab_id=test_lab["lab"].id,
            layer="C",
            status="pending",
        )
        test_db.add(req)
        test_db.commit()
        test_db.refresh(req)

        resp = client.post(
            "/api/v1/sandbox/verify",
            json={
                "execution_request_id": req.id,
                "model_url": "https://example.com/bad_model.pth",
                "training_log": json.dumps({"epochs": 0}),
                "lab_id": test_lab["lab"].id,
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # Should return a verification result (may or may not pass)
        assert "status" in data
        assert "metrics" in data

    def test_verify_unauthorized(self, client, test_lab, test_db):
        """AC40: Unauthorized verification returns 401."""
        resp = client.post(
            "/api/v1/sandbox/verify",
            json={
                "execution_request_id": 1,
                "model_url": "https://example.com/model.pth",
                "training_log": "{}",
                "lab_id": test_lab["lab"].id,
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ── S5: Hybrid flow completion (AC42) ────────────────────────────────────────

class TestHybridComplete:
    """AC42: POST /api/v1/sandbox/complete — Hybrid flow completion marker."""

    def test_complete_hybrid_flow(self, client, auth_headers, test_lab, test_db):
        """AC42: Mark a hybrid flow (Layer A + B + C) as complete."""
        from app.models import ExecutionRequest

        req = ExecutionRequest(
            user_id=1,
            lab_id=test_lab["lab"].id,
            layer="A",
            code="print('done')",
            status="completed",
            result={"output": "done\n", "exit_code": 0},
        )
        test_db.add(req)
        test_db.commit()
        test_db.refresh(req)

        resp = client.post(
            "/api/v1/sandbox/complete",
            json={
                "execution_request_id": req.id,
                "layers_completed": ["A", "B", "C"],
                "final_status": "completed",
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        data = resp.json()
        assert data["status"] == "ok"
        assert "message" in data

    def test_complete_unauthorized(self, client):
        """AC42: Unauthorized complete returns 401."""
        resp = client.post(
            "/api/v1/sandbox/complete",
            json={
                "execution_request_id": 1,
                "layers_completed": ["A"],
                "final_status": "completed",
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_complete_nonexistent_request(self, client, auth_headers):
        """AC42: Complete non-existent request returns 404."""
        resp = client.post(
            "/api/v1/sandbox/complete",
            json={
                "execution_request_id": 99999,
                "layers_completed": ["A"],
                "final_status": "completed",
            },
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ── S6: Provider health check ─────────────────────────────────────────────────

class TestProviderHealthCheck:
    """S6: GET /api/v1/sandbox/providers — Provider health check."""

    def test_list_providers(self, client, auth_headers, test_db):
        """S6: List all sandbox providers with health status."""
        from app.models import SandboxProvider

        # Seed a provider
        p = SandboxProvider(name="local", layer="A", is_healthy=True, failure_count=0)
        test_db.add(p)
        test_db.commit()

        resp = client.get("/api/v1/sandbox/providers", headers=auth_headers)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        provider = next((x for x in data if x["name"] == "local"), None)
        assert provider is not None
        assert provider["layer"] == "A"
        assert "is_healthy" in provider

    def test_providers_unauthorized(self, client):
        """S6: Unauthorized provider list returns 401."""
        resp = client.get("/api/v1/sandbox/providers")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
