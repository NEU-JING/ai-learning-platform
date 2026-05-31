"""Tests for Tutor Chat API (T12).

AC15: AI 导师对话 (< 5s 响应)
AC21: LLM Router 集成
"""

import pytest


class TestTutorChatAPI:
    """Test Tutor Chat API endpoints."""

    @pytest.mark.asyncio
    async def test_create_new_session(self, client, auth_headers):
        """Test creating a new tutor session."""
        response = client.post(
            "/api/v1/tutor/chat",
            json={
                "session_type": "diagnosis",
                "message": "我想学习 Python",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_type"] == "diagnosis"
        assert "response" in data
        assert "content" in data["response"]

    @pytest.mark.asyncio
    async def test_continue_existing_session(self, client, auth_headers):
        """Test continuing an existing session."""
        # First message
        response1 = client.post(
            "/api/v1/tutor/chat",
            json={"session_type": "qa", "message": "什么是 Python？"},
            headers=auth_headers,
        )
        assert response1.status_code == 200
        session_id = response1.json()["session_id"]

        # Continue session
        response2 = client.post(
            "/api/v1/tutor/chat",
            json={
                "session_id": session_id,
                "message": "它有什么特点？",
            },
            headers=auth_headers,
        )

        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_response_time_under_5s(self, client, auth_headers):
        """Test response time is under 5 seconds (AC15)."""
        import time

        start = time.time()
        response = client.post(
            "/api/v1/tutor/chat",
            json={"session_type": "qa", "message": "Hello"},
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 5.0, f"Response took {elapsed}s, expected < 5s"

    @pytest.mark.asyncio
    async def test_code_review_session(self, client, auth_headers):
        """Test code review session type."""
        response = client.post(
            "/api/v1/tutor/chat",
            json={
                "session_type": "code_review",
                "context_id": 1,  # lab_id
                "message": "请检查这段代码",
                "attachments": [
                    {
                        "type": "code",
                        "content": "def foo(): pass",
                        "language": "python",
                    }
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_type"] == "code_review"

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client):
        """Test unauthorized access is rejected."""
        response = client.post(
            "/api/v1/tutor/chat",
            json={"session_type": "qa", "message": "Hello"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_session_message_history(self, client, auth_headers):
        """Test message history is stored correctly."""
        # Send multiple messages
        session_id = None
        messages = ["你好", "我想学 Python", "推荐一些课程"]

        for msg in messages:
            response = client.post(
                "/api/v1/tutor/chat",
                json={
                    "session_id": session_id,
                    "session_type": "qa",
                    "message": msg,
                },
                headers=auth_headers,
            )
            assert response.status_code == 200
            if session_id is None:
                session_id = response.json()["session_id"]

        # Verify history
        response = client.get(
            f"/api/v1/tutor/sessions/{session_id}/messages",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Should have user messages + AI responses
        assert len(data["messages"]) >= len(messages) * 2
