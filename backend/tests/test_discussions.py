"""Discussion API tests — covers CRUD, comments, and like-toggle (S6 fix)."""


class TestDiscussionCRUD:
    """Basic discussion create / list / get / update / delete."""

    def _register_and_login(self, client, suffix="disc"):
        client.post(
            "/api/v1/auth/register",
            json={
                "email": f"{suffix}@test.com",
                "username": f"user_{suffix}",
                "password": "Test123456",
            },
        )
        resp = client.post(
            "/api/v1/auth/login", json={"email": f"{suffix}@test.com", "password": "Test123456"}
        )
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_discussion(self, client, test_course):
        course_id = test_course["course"].id
        headers = self._register_and_login(client, "crt")
        resp = client.post(
            f"/api/v1/courses/{course_id}/discussions",
            json={"title": "Test Discussion", "content": "Hello world!"},
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test Discussion"
        assert data["likes_count"] == 0

    def test_list_discussions(self, client, test_course):
        course_id = test_course["course"].id
        headers = self._register_and_login(client, "lst")
        client.post(
            f"/api/v1/courses/{course_id}/discussions",
            json={"title": "List Test", "content": "content"},
            headers=headers,
        )
        resp = client.get(f"/api/v1/courses/{course_id}/discussions")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert "content_preview" in data[0]

    def test_get_discussion_detail(self, client, test_course):
        course_id = test_course["course"].id
        headers = self._register_and_login(client, "dtl")
        create = client.post(
            f"/api/v1/courses/{course_id}/discussions",
            json={"title": "Detail Test", "content": "Full content here"},
            headers=headers,
        )
        assert create.status_code == 201
        disc_id = create.json()["id"]
        resp = client.get(f"/api/v1/discussions/{disc_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["content"] == "Full content here"
        assert "comments" in data

    def test_update_discussion(self, client, test_course):
        course_id = test_course["course"].id
        headers = self._register_and_login(client, "upd")
        create = client.post(
            f"/api/v1/courses/{course_id}/discussions",
            json={"title": "Old Title", "content": "Old content"},
            headers=headers,
        )
        disc_id = create.json()["id"]
        resp = client.put(
            f"/api/v1/discussions/{disc_id}", json={"title": "New Title"}, headers=headers
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "New Title"

    def test_delete_discussion(self, client, test_course):
        course_id = test_course["course"].id
        headers = self._register_and_login(client, "del")
        create = client.post(
            f"/api/v1/courses/{course_id}/discussions",
            json={"title": "To Delete", "content": "bye"},
            headers=headers,
        )
        disc_id = create.json()["id"]
        resp = client.delete(f"/api/v1/discussions/{disc_id}", headers=headers)
        assert resp.status_code == 204

    def test_create_comment(self, client, test_course):
        course_id = test_course["course"].id
        headers = self._register_and_login(client, "cmt")
        create = client.post(
            f"/api/v1/courses/{course_id}/discussions",
            json={"title": "Comment Test", "content": "discuss"},
            headers=headers,
        )
        disc_id = create.json()["id"]
        resp = client.post(
            f"/api/v1/discussions/{disc_id}/comments",
            json={"content": "Great post!"},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["content"] == "Great post!"


class TestDiscussionLikeToggle:
    """Like toggle — prevent duplicate likes (S6 fix)."""

    def _register_and_login(self, client, suffix):
        client.post(
            "/api/v1/auth/register",
            json={
                "email": f"{suffix}@test.com",
                "username": f"user_{suffix}",
                "password": "Test123456",
            },
        )
        resp = client.post(
            "/api/v1/auth/login", json={"email": f"{suffix}@test.com", "password": "Test123456"}
        )
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_like_then_unlike(self, client, test_course):
        course_id = test_course["course"].id
        headers = self._register_and_login(client, "tgl1")
        create = client.post(
            f"/api/v1/courses/{course_id}/discussions",
            json={"title": "Like Toggle", "content": "test"},
            headers=headers,
        )
        disc_id = create.json()["id"]

        # Like
        resp1 = client.post(f"/api/v1/discussions/{disc_id}/like", headers=headers)
        assert resp1.json()["liked"] is True
        assert resp1.json()["likes_count"] == 1

        # Unlike (toggle)
        resp2 = client.post(f"/api/v1/discussions/{disc_id}/like", headers=headers)
        assert resp2.json()["liked"] is False
        assert resp2.json()["likes_count"] == 0

    def test_like_prevents_duplicate(self, client, test_course):
        """Same user liking twice toggles back to 0."""
        course_id = test_course["course"].id
        headers = self._register_and_login(client, "dup2")
        create = client.post(
            f"/api/v1/courses/{course_id}/discussions",
            json={"title": "Dup Like", "content": "test"},
            headers=headers,
        )
        disc_id = create.json()["id"]

        client.post(f"/api/v1/discussions/{disc_id}/like", headers=headers)
        resp = client.post(f"/api/v1/discussions/{disc_id}/like", headers=headers)
        assert resp.json()["likes_count"] == 0
        assert resp.json()["liked"] is False

    def test_two_users_like_count(self, client, test_course):
        """Two different users liking should count 2."""
        course_id = test_course["course"].id
        headers1 = self._register_and_login(client, "two1")
        create = client.post(
            f"/api/v1/courses/{course_id}/discussions",
            json={"title": "Two Likes", "content": "test"},
            headers=headers1,
        )
        disc_id = create.json()["id"]
        client.post(f"/api/v1/discussions/{disc_id}/like", headers=headers1)

        # User 2
        headers2 = self._register_and_login(client, "two2")
        r = client.post(f"/api/v1/discussions/{disc_id}/like", headers=headers2)
        assert r.json()["likes_count"] == 2
        assert r.json()["liked"] is True
