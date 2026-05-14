"""Tests for course and lab API endpoints."""


class TestCourseList:
    def test_list_courses(self, client, test_course):
        resp = client.get("/api/v1/courses/")
        assert resp.status_code == 200
        data = resp.json()
        # API now returns PaginatedResponse { items, total, page, ... }
        assert "items" in data
        assert data["total"] >= 1  # at least one published course exists

    def test_list_courses_filter_level(self, client, test_course):
        resp = client.get("/api/v1/courses/?level=beginner")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 1

    def test_list_courses_filter_category(self, client, test_course):
        resp = client.get("/api/v1/courses/?category=python")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 1

    def test_list_courses_no_match(self, client, test_course):
        resp = client.get("/api/v1/courses/?level=expert")
        # Unpublished or no match → empty items is fine
        assert resp.status_code == 200


class TestCourseListPagination:
    """Tests for the paginated course list endpoint."""

    def test_list_courses_paginated(self, client, test_course):
        resp = client.get("/api/v1/courses/?page=1&per_page=10")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "pages" in data
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["items"][0]["title"]  # just verify title exists

    def test_list_courses_paginated_default_per_page(self, client, test_course):
        resp = client.get("/api/v1/courses/?page=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["per_page"] == 20  # default

    def test_list_courses_paginated_with_filters(self, client, test_course):
        resp = client.get("/api/v1/courses/?page=1&per_page=10&level=beginner")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_list_courses_paginated_empty_page(self, client, test_course):
        resp = client.get("/api/v1/courses/?page=999")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] >= 1  # total is still the full count

    def test_list_courses_paginated_per_page_max(self, client, test_course):
        resp = client.get("/api/v1/courses/?page=1&per_page=200")
        # per_page > 100 should be rejected by Query(le=100)
        assert resp.status_code == 422

    def test_list_courses_no_page_returns_list(self, client, test_course):
        """Without page param, returns PaginatedResponse with page=None."""
        resp = client.get("/api/v1/courses/")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["page"] is None
        assert len(data["items"]) >= 1


class TestCourseDetail:
    def test_get_course(self, client, test_course):
        course_id = test_course["course"].id
        resp = client.get(f"/api/v1/courses/{course_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Python for AI"
        assert len(data["chapters"]) >= 1

    def test_get_course_not_found(self, client):
        resp = client.get("/api/v1/courses/99999")
        assert resp.status_code == 404


class TestChapterDetail:
    def test_get_chapter(self, client, test_course):
        chapter_id = test_course["chapter"].id
        resp = client.get(f"/api/v1/courses/chapters/{chapter_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Hello World"
        assert "lab" in data

    def test_get_chapter_not_found(self, client):
        resp = client.get("/api/v1/courses/chapters/99999")
        assert resp.status_code == 404


class TestLabPublic:
    def test_lab_no_solution_code_in_response(self, client, test_course):
        """SECURITY: LabPublicResponse must NOT contain solution_code."""
        chapter_id = test_course["chapter"].id
        resp = client.get(f"/api/v1/courses/chapters/{chapter_id}/lab")
        assert resp.status_code == 200
        data = resp.json()
        assert "solution_code" not in data
        assert "test_cases" not in data
        assert data["title"] == "Hello World Lab"


class TestLabSubmit:
    def test_submit_lab_security_blocked(self, client, auth_headers, test_course):
        """Submitting dangerous code should return 400."""
        lab_id = test_course["lab"].id
        resp = client.post(
            f"/api/v1/courses/labs/{lab_id}/submit",
            json={"code": "import os\nos.system('whoami')"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "安全检查" in resp.json()["detail"]

    def test_submit_lab_not_found(self, client, auth_headers):
        resp = client.post(
            "/api/v1/courses/labs/99999/submit",
            json={"code": "print('hello')"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_submit_lab_no_auth(self, client, test_course):
        lab_id = test_course["lab"].id
        resp = client.post(
            f"/api/v1/courses/labs/{lab_id}/submit",
            json={"code": "print('hello')"},
        )
        assert resp.status_code == 401


class TestCodeExecution:
    def test_execute_no_auth(self, client):
        resp = client.post(
            "/api/v1/labs/execute",
            json={"code": "print('hello')"},
        )
        assert resp.status_code == 401

    def test_execute_unsupported_language(self, client, auth_headers):
        resp = client.post(
            "/api/v1/labs/execute",
            json={"code": "print('hello')", "language": "rust"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_execute_dangerous_code_blocked(self, client, auth_headers):
        resp = client.post(
            "/api/v1/labs/execute",
            json={"code": "import subprocess\nsubprocess.run(['ls'])"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
