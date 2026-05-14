"""Tests for progress API endpoints."""


class TestProgress:
    def test_get_my_progress_empty(self, client, auth_headers):
        resp = client.get("/api/v1/progress/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_update_progress(self, client, auth_headers, test_course):
        chapter_id = test_course["chapter"].id
        resp = client.post(
            f"/api/v1/progress/chapters/{chapter_id}",
            json={"status": "completed"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    def test_update_progress_invalid_status(self, client, auth_headers, test_course):
        chapter_id = test_course["chapter"].id
        resp = client.post(
            f"/api/v1/progress/chapters/{chapter_id}",
            json={"status": "invalid_status"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_update_progress_chapter_not_found(self, client, auth_headers):
        resp = client.post(
            "/api/v1/progress/chapters/99999",
            json={"status": "completed"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_get_my_progress_after_update(self, client, auth_headers, test_course):
        chapter_id = test_course["chapter"].id
        # Update first
        client.post(
            f"/api/v1/progress/chapters/{chapter_id}",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        # Then fetch
        resp = client.get("/api/v1/progress/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["chapter_id"] == chapter_id

    def test_get_course_progress(self, client, auth_headers, test_course):
        course_id = test_course["course"].id
        resp = client.get(f"/api/v1/progress/courses/{course_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["course_id"] == course_id
        assert data["total_chapters"] >= 1

    def test_get_learning_stats(self, client, auth_headers):
        resp = client.get("/api/v1/progress/stats/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "completed_chapters" in data
        assert "total_learning_minutes" in data

    def test_progress_no_auth(self, client):
        resp = client.get("/api/v1/progress/")
        assert resp.status_code == 401

    def test_progress_unique_constraint(self, client, auth_headers, test_course):
        """Same user+chapter should not create duplicate progress records."""
        chapter_id = test_course["chapter"].id
        # First update
        resp1 = client.post(
            f"/api/v1/progress/chapters/{chapter_id}",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        assert resp1.status_code == 200
        # Second update (should update, not duplicate)
        resp2 = client.post(
            f"/api/v1/progress/chapters/{chapter_id}",
            json={"status": "completed"},
            headers=auth_headers,
        )
        assert resp2.status_code == 200

        # Verify only one record
        progress_resp = client.get("/api/v1/progress/", headers=auth_headers)
        progress_data = [p for p in progress_resp.json() if p["chapter_id"] == chapter_id]
        assert len(progress_data) == 1
        assert progress_data[0]["status"] == "completed"
