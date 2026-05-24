"""Tests for profile settings frontend page (Task-4).

Covers:
  - /#/profile/settings hash route renders ProfileSettingsPage
  - Unauthenticated user is redirected to /login
  - GET /api/v1/profile/me/settings returns onboarding state (all false)
  - PUT /api/v1/profile/me/settings with is_public=true enables profile
  - POST /api/v1/profile/me/settings/batch show_all/hide_all
  - profile_url in settings response contains username
  - Preview URL: /p/{username} is accessible
  - Navigation entry for "我的公开主页" exists
"""


from app.core.security import create_access_token, get_password_hash
from app.models import User

# ── helpers ──────────────────────────────────────────────────────────────────


def _make_user(test_db, username="settingsuser", email="settings@example.com"):
    """Create a user and return (user_obj, auth_headers)."""
    user = User(
        email=email,
        username=username,
        password_hash=get_password_hash("Pass1234"),
        role="student",
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    token = create_access_token(data={"sub": user.id})
    return user, {"Authorization": f"Bearer {token}"}


SETTINGS_URL = "/api/v1/profile/me/settings"
BATCH_URL = "/api/v1/profile/me/settings/batch"


# ── Test classes ─────────────────────────────────────────────────────────────


class TestSettingsPageRoute:
    """/#/profile/settings hash route should be accessible via SPA."""

    def test_profile_settings_hash_route_served(self, client, test_db):
        """The SPA index.html should be served for hash routes.
        The actual routing happens client-side, so we verify the
        entry point HTML is returned."""
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")


class TestSettingsAPIForFrontend:
    """API contract tests that the frontend settings page relies on."""

    def test_get_settings_default_state(self, client, test_db):
        """Frontend shows onboarding when all flags are false."""
        user, headers = _make_user(test_db)
        resp = client.get(SETTINGS_URL, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        # Frontend checks these to show onboarding card
        assert data["is_public"] is False
        assert data["show_basic_info"] is False
        assert data["show_skill_radar"] is False
        assert data["show_labs"] is False
        assert data["show_certificates"] is False

    def test_get_settings_unauthenticated(self, client, test_db):
        """Unauthenticated access to settings returns 401.
        Frontend should redirect to /login."""
        resp = client.get(SETTINGS_URL)
        assert resp.status_code == 401

    def test_enable_profile_one_click(self, client, test_db):
        """One-click enable: PUT is_public=true sets all dimensions true.
        Frontend then shows profile link + copy button."""
        user, headers = _make_user(test_db, username="quickstart")

        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        # All dimensions should be true after enable (BR5)
        assert data["is_public"] is True
        assert data["show_basic_info"] is True
        assert data["show_skill_radar"] is True
        assert data["show_labs"] is True
        assert data["show_certificates"] is True
        # profile_url must be present for copy link button
        assert "profile_url" in data
        assert "quickstart" in data["profile_url"]

    def test_settings_response_has_profile_url(self, client, test_db):
        """profile_url is needed for the copy link and preview buttons."""
        user, headers = _make_user(test_db, username="linktest")

        resp = client.get(SETTINGS_URL, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "profile_url" in data
        assert "linktest" in data["profile_url"]

    def test_settings_response_has_avatar_url(self, client, test_db):
        """avatar_url from User model is included for display."""
        user, headers = _make_user(test_db)
        from app.models import User as UserModel

        db_user = test_db.query(UserModel).filter(UserModel.id == user.id).first()
        db_user.avatar_url = "https://example.com/avatar.png"
        test_db.commit()

        resp = client.get(SETTINGS_URL, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["avatar_url"] == "https://example.com/avatar.png"

    def test_close_profile_frontend_warning(self, client, test_db):
        """Closing profile: is_public false, but settings still returned.
        Frontend shows '你的能力主页已关闭' warning."""
        user, headers = _make_user(test_db)

        # Enable
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        # Close
        resp = client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        # is_public is false -> frontend shows closure warning
        assert data["is_public"] is False
        # Dimensions preserved (for re-enable)
        assert data["show_basic_info"] is True

    def test_dimension_toggle_does_not_change_is_public(self, client, test_db):
        """Toggling individual dimensions keeps is_public unchanged."""
        user, headers = _make_user(test_db)

        # Enable
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        # Toggle one dimension off
        resp = client.put(
            SETTINGS_URL,
            json={"show_basic_info": False},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()

        assert data["is_public"] is True
        assert data["show_basic_info"] is False
        assert data["show_skill_radar"] is True

    def test_batch_show_all(self, client, test_db):
        """Frontend '一键开启全部' button calls batch show_all."""
        user, headers = _make_user(test_db)

        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        # Hide some
        client.put(
            SETTINGS_URL,
            json={"show_basic_info": False, "show_labs": False},
            headers=headers,
        )

        resp = client.post(BATCH_URL, json={"action": "show_all"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["show_basic_info"] is True
        assert data["show_skill_radar"] is True
        assert data["show_labs"] is True
        assert data["show_certificates"] is True

    def test_batch_hide_all(self, client, test_db):
        """Frontend '一键隐藏全部' button calls batch hide_all."""
        user, headers = _make_user(test_db)

        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        resp = client.post(BATCH_URL, json={"action": "hide_all"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        # is_public stays true, but all dimensions are hidden
        assert data["is_public"] is True
        assert data["show_basic_info"] is False
        assert data["show_skill_radar"] is False
        assert data["show_labs"] is False
        assert data["show_certificates"] is False

    def test_batch_without_enabled_profile_returns_400(self, client, test_db):
        """Batch operations fail when profile not enabled.
        Frontend should show error toast."""
        user, headers = _make_user(test_db)

        resp = client.post(BATCH_URL, json={"action": "show_all"}, headers=headers)
        assert resp.status_code == 400

    def test_re_enable_resets_dimensions(self, client, test_db):
        """Re-enabling after close resets all dimensions to true."""
        user, headers = _make_user(test_db)

        # Enable
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        # Close
        client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)
        # Hide some while closed
        client.put(
            SETTINGS_URL,
            json={"show_basic_info": False},
            headers=headers,
        )
        # Re-enable
        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        # All dimensions reset to true on re-enable
        assert data["is_public"] is True
        assert data["show_basic_info"] is True
        assert data["show_skill_radar"] is True
        assert data["show_labs"] is True
        assert data["show_certificates"] is True


class TestPreviewURL:
    """Preview button opens /p/{username} in new tab."""

    def test_preview_url_accessible(self, client, test_db):
        """After enabling profile, /p/{username} returns 200 HTML."""
        user, headers = _make_user(test_db, username="previewer")

        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        resp = client.get("/p/previewer")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")

    def test_preview_url_for_public_profile_has_og_tags(self, client, test_db):
        """Public profile /p/{username} has OG tags for social sharing."""
        user, headers = _make_user(test_db, username="ogpreview")

        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        resp = client.get("/p/ogpreview")
        content = resp.text
        assert "og:title" in content

    def test_preview_url_for_closed_profile(self, client, test_db):
        """Closed profile /p/{username} returns HTML (with noindex)."""
        user, headers = _make_user(test_db, username="closedprev")

        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)

        resp = client.get("/p/closedprev")
        assert resp.status_code == 200
        assert "noindex" in resp.text or "robots" in resp.text


class TestSettingsResponseSchema:
    """Ensure settings response schema matches what frontend expects."""

    def test_settings_response_fields(self, client, test_db):
        """Settings response contains all fields the frontend consumes."""
        user, headers = _make_user(test_db)

        resp = client.get(SETTINGS_URL, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        # Required fields for frontend rendering
        required_fields = [
            "is_public",
            "show_basic_info",
            "show_skill_radar",
            "show_labs",
            "show_certificates",
            "profile_url",
            "display_name",
            "bio",
            "avatar_url",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_update_settings_returns_same_schema(self, client, test_db):
        """PUT settings returns same schema as GET (frontend re-renders)."""
        user, headers = _make_user(test_db)

        resp = client.put(
            SETTINGS_URL,
            json={"is_public": True},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()

        required_fields = [
            "is_public",
            "show_basic_info",
            "show_skill_radar",
            "show_labs",
            "show_certificates",
            "profile_url",
            "display_name",
            "bio",
            "avatar_url",
        ]
        for field in required_fields:
            assert field in data, f"Missing field in PUT response: {field}"

    def test_batch_response_returns_same_schema(self, client, test_db):
        """Batch response returns same schema as GET (frontend re-renders)."""
        user, headers = _make_user(test_db)

        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        resp = client.post(BATCH_URL, json={"action": "hide_all"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        required_fields = [
            "is_public",
            "show_basic_info",
            "show_skill_radar",
            "show_labs",
            "show_certificates",
            "profile_url",
            "display_name",
            "bio",
            "avatar_url",
        ]
        for field in required_fields:
            assert field in data, f"Missing field in batch response: {field}"
