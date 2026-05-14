"""API contract tests — verify response field names match frontend consumption.

This file is the single automated guardian of frontend-backend contract.
When modifying any Pydantic schema field name, you MUST update the
corresponding assertion here. A failing contract test = a broken frontend.

See DEVELOPMENT_HARNESS.md §5.6 for contract test specification.
See DEVELOPMENT_HARNESS.md §4.7.3 for the API contract registry.
"""

import pytest


class TestCourseListContract:
    """GET /api/v1/courses/ response contract.

    Frontend consumers: Home.js, Courses.js
    Key fields: chapters_count (not chapter_count)
    """

    def test_course_list_has_chapters_count(self, client, test_course):
        """Frontend Home.js/Courses.js consume chapters_count field."""
        resp = client.get("/api/v1/courses/")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert len(data["items"]) > 0
        # 🔑 Contract: field name must match frontend exactly
        assert "chapters_count" in data["items"][0], (
            "Frontend uses 'chapters_count', backend must return this field name. "
            "If you renamed this field, update frontend/src/views/Home.js and Courses.js too."
        )

    def test_course_list_has_required_fields(self, client, test_course):
        """Verify all fields consumed by frontend are present."""
        resp = client.get("/api/v1/courses/")
        data = resp.json()
        item = data["items"][0]
        required_fields = ["id", "title", "level", "category", "chapters_count", "is_published"]
        for field in required_fields:
            assert field in item, f"Missing field '{field}' in course list response"


class TestCourseDetailContract:
    """GET /api/v1/courses/{id} response contract.

    Frontend consumers: CourseDetail.js
    Key fields: chapters, order_index
    """

    def test_course_detail_has_chapters(self, client, test_course):
        """Frontend CourseDetail.js consumes chapters field."""
        course_id = test_course["course"].id
        resp = client.get(f"/api/v1/courses/{course_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert "chapters" in data, (
            "Frontend uses 'chapters', backend must return this field name."
        )

    def test_chapter_has_has_lab(self, client, test_course):
        """Frontend uses has_lab to show/hide lab entry."""
        course_id = test_course["course"].id
        resp = client.get(f"/api/v1/courses/{course_id}")
        data = resp.json()
        if len(data["chapters"]) > 0:
            assert "has_lab" in data["chapters"][0], (
                "Frontend uses 'has_lab' on chapter objects."
            )


class TestAuthContract:
    """Auth API response contracts.

    Key behavior: register returns UserResponse (no token), login returns TokenResponse.
    """

    def test_register_returns_user_no_token(self, client):
        """Register endpoint returns user info, NOT tokens — frontend must call login after register."""
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "email": "contract_test@example.com",
                "username": "contractuser",
                "password": "TestPass123",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" not in data, (
            "Register endpoint should NOT return access_token. "
            "Frontend expects to redirect to login after registration."
        )
        assert "username" in data
        assert "email" in data

    def test_login_returns_token_fields(self, client, test_user):
        """Login endpoint returns access_token and refresh_token."""
        resp = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["user"]["email"],
                "password": "TestPass123",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data, "Frontend uses access_token after login"
        assert "refresh_token" in data, "Frontend storage.js stores refresh_token"
        assert "token_type" in data

    def test_me_returns_user_fields(self, client, test_user):
        """GET /auth/me returns username and email consumed by frontend."""
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {test_user['token']}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "username" in data, "Frontend displays username from /auth/me"
        assert "email" in data


class TestPaginatedResponseContract:
    """Verify PaginatedResponse structure consistency per §4.8."""

    def test_list_without_page_returns_paginated_structure(self, client, test_course):
        """Without page param, API returns PaginatedResponse with page=None."""
        resp = client.get("/api/v1/courses/")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert data["page"] is None, "Without page param, page should be None"

    def test_list_with_page_returns_paginated_structure(self, client, test_course):
        """With page param, API returns PaginatedResponse with metadata."""
        resp = client.get("/api/v1/courses/?page=1&per_page=10")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert "pages" in data
