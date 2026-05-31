"""Tests for Code Review API (T13).

AC16: 代码审查 (AI 分析代码)
AC17: 代码评分维度
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.services.llm_router import LLMRouter


class TestCodeReviewAPI:
    """Test Code Review API endpoints."""

    @pytest.mark.asyncio
    async def test_create_code_review(self, client, auth_headers):
        """Test creating a code review."""
        response = client.post(
            "/api/v1/tutor/code-review",
            json={
                "lab_id": 1,
                "code_content": "def add(a, b):\n    return a + b",
                "language": "python",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "review_id" in data
        assert data["language"] == "python"
        assert "issues" in data
        assert "overall_score" in data
        assert "summary" in data

    @pytest.mark.asyncio
    async def test_code_review_with_issues(self, client, auth_headers):
        """Test code review detects issues."""
        # Mock LLM to return issues
        mock_response = {
            "issues": [
                {
                    "type": "style",
                    "line": 2,
                    "message": "Use 'is' for None comparison",
                    "suggestion": "Change 'x == True' to 'x is True'",
                    "severity": "medium",
                }
            ],
            "dimensions": {
                "correctness": 80,
                "efficiency": 75,
                "readability": 70,
                "style": 60,
                "best_practices": 75,
            },
            "overall_score": 72.0,
            "summary": "Code has minor style issues",
        }
        
        with patch.object(
            LLMRouter, "chat", new_callable=AsyncMock
        ) as mock_chat:
            mock_chat.return_value = {
                "content": '{"issues": [{"type": "style", "line": 2, "message": "Use \'is\' for None comparison", "suggestion": "Change \'x == True\' to \'x is True\'", "severity": "medium"}], "dimensions": {"correctness": 80, "efficiency": 75, "readability": 70, "style": 60, "best_practices": 75}, "overall_score": 72.0, "summary": "Code has minor style issues"}',
                "model": "doubao",
                "tokens": 150,
                "provider": "ark",
            }
            
            response = client.post(
                "/api/v1/tutor/code-review",
                json={
                    "lab_id": 1,
                    "code_content": "def bad_code(x):\n    if x == True:\n        print('bad')\n    return x",
                    "language": "python",
                },
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["issues"]) > 0
            # Check issue structure
            for issue in data["issues"]:
                assert "type" in issue
                assert "line" in issue
                assert "message" in issue
                assert "suggestion" in issue

    @pytest.mark.asyncio
    async def test_code_review_scoring_dimensions(self, client, auth_headers):
        """Test code review includes scoring dimensions (AC17)."""
        response = client.post(
            "/api/v1/tutor/code-review",
            json={
                "lab_id": 1,
                "code_content": "def sum_list(nums):\n    total = 0\n    for n in nums:\n        total += n\n    return total",
                "language": "python",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        
        # AC17: 代码评分维度
        assert "dimensions" in data
        dimensions = data["dimensions"]
        assert "correctness" in dimensions  # 正确性
        assert "efficiency" in dimensions   # 效率
        assert "readability" in dimensions  # 可读性
        assert "style" in dimensions        # 代码风格
        assert "best_practices" in dimensions  # 最佳实践
        
        # All dimensions are 0-100
        for dim, score in dimensions.items():
            assert 0 <= score <= 100

    @pytest.mark.asyncio
    async def test_get_code_review(self, client, auth_headers):
        """Test retrieving a specific code review."""
        # First create a review
        create_response = client.post(
            "/api/v1/tutor/code-review",
            json={
                "lab_id": 1,
                "code_content": "def test(): pass",
                "language": "python",
            },
            headers=auth_headers,
        )
        review_id = create_response.json()["review_id"]

        # Get the review
        get_response = client.get(
            f"/api/v1/tutor/code-review/{review_id}",
            headers=auth_headers,
        )

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["review_id"] == review_id
        assert "code_content" in data
        assert "issues" in data

    @pytest.mark.asyncio
    async def test_get_user_code_reviews(self, client, auth_headers):
        """Test retrieving user's code review history."""
        # Create a few reviews
        for i in range(3):
            client.post(
                "/api/v1/tutor/code-review",
                json={
                    "lab_id": i + 1,
                    "code_content": f"def func_{i}(): pass",
                    "language": "python",
                },
                headers=auth_headers,
            )

        # Get list
        response = client.get(
            "/api/v1/tutor/code-reviews",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "reviews" in data
        assert len(data["reviews"]) >= 3
        assert "total" in data

    @pytest.mark.asyncio
    async def test_unauthorized_code_review(self, client):
        """Test unauthorized access is rejected."""
        response = client.post(
            "/api/v1/tutor/code-review",
            json={
                "lab_id": 1,
                "code_content": "def test(): pass",
                "language": "python",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_code_review_without_lab(self, client, auth_headers):
        """Test code review without lab context (general review)."""
        response = client.post(
            "/api/v1/tutor/code-review",
            json={
                "code_content": "def hello():\n    print('Hello World')",
                "language": "python",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "review_id" in data
        assert data["lab_id"] is None
