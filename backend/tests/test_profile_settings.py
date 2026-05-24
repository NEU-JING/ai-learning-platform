"""Tests for public profile settings API (Task-1).

Covers:
  - First-time enable (no UserProfile -> create, is_public=true, all dimensions true)
  - Close profile (is_public true->false, dimension settings preserved)
  - Re-enable profile (is_public true again, all dimensions true again)
  - Modify dimension toggles without affecting is_public
  - show_all / hide_all batch operations
  - Batch operations return 400 when profile not enabled
  - display_name empty string -> null
  - bio exceeds 200 chars validation
"""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token, get_password_hash
from app.models import User

# ── helpers ──────────────────────────────────────────────────────────────────


def _make_user(test_db, username="profileuser", email="profile@example.com"):
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


class TestGetSettings:
    """GET /api/v1/profile/me/settings"""

    def test_no_profile_returns_defaults(self, client, test_db):
        """When no UserProfile record exists, all fields default to false."""
        user, headers = _make_user(test_db)
        resp = client.get(SETTINGS_URL, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_public"] is False
        assert data["show_basic_info"] is False
        assert data["show_skill_radar"] is False
        assert data["show_labs"] is False
        assert data["show_certificates"] is False
        assert data["display_name"] is None
        assert data["bio"] is None

    def test_unauthenticated_returns_401(self, client, test_db):
        resp = client.get(SETTINGS_URL)
        assert resp.status_code == 401


class TestFirstTimeEnable:
    """First-time enable: no UserProfile -> create with is_public=true,
    all four dimensions auto-set to true (BR5)."""

    def test_first_enable_creates_profile_with_all_dimensions(self, client, test_db):
        user, headers = _make_user(test_db)

        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        # BR5: is_public false->true auto-sets all dimensions to true
        assert data["is_public"] is True
        assert data["show_basic_info"] is True
        assert data["show_skill_radar"] is True
        assert data["show_labs"] is True
        assert data["show_certificates"] is True
        assert data["profile_url"] is not None

    def test_first_enable_sets_display_name_to_username(self, client, test_db):
        """When display_name is null and user enables profile, display_name
        defaults to username (Design flow 2, step 3)."""
        user, headers = _make_user(test_db, username="zhangsan")

        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        # display_name should be populated; schema returns it
        assert data["display_name"] is not None


class TestCloseProfile:
    """Close profile: is_public true->false, dimension settings preserved."""

    def test_close_preserves_dimensions(self, client, test_db):
        user, headers = _make_user(test_db)

        # Enable first
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        # Close
        resp = client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["is_public"] is False
        # Dimensions should still be true (preserved from enable)
        assert data["show_basic_info"] is True
        assert data["show_skill_radar"] is True
        assert data["show_labs"] is True
        assert data["show_certificates"] is True


class TestReEnableProfile:
    """Re-enable: is_public false->true again, all dimensions set to true again."""

    def test_re_enable_resets_all_dimensions_to_true(self, client, test_db):
        user, headers = _make_user(test_db)

        # Enable
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        # Close
        client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)
        # Modify some dimensions while closed (to test they get reset)
        client.put(SETTINGS_URL, json={"show_basic_info": False}, headers=headers)

        # Re-enable
        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["is_public"] is True
        # BR5: all dimensions reset to true on re-enable
        assert data["show_basic_info"] is True
        assert data["show_skill_radar"] is True
        assert data["show_labs"] is True
        assert data["show_certificates"] is True


class TestDimensionToggle:
    """Modifying dimension toggles should not affect is_public."""

    def test_toggle_dimension_does_not_change_is_public(self, client, test_db):
        user, headers = _make_user(test_db)

        # Enable profile
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        # Turn off one dimension
        resp = client.put(SETTINGS_URL, json={"show_basic_info": False}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["is_public"] is True  # unchanged
        assert data["show_basic_info"] is False

    def test_toggle_multiple_dimensions(self, client, test_db):
        user, headers = _make_user(test_db)

        # Enable profile
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        # Turn off two dimensions at once
        resp = client.put(
            SETTINGS_URL,
            json={"show_basic_info": False, "show_labs": False},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()

        assert data["is_public"] is True
        assert data["show_basic_info"] is False
        assert data["show_skill_radar"] is True  # unchanged
        assert data["show_labs"] is False
        assert data["show_certificates"] is True  # unchanged


class TestBatchOperations:
    """show_all / hide_all batch operations."""

    def test_show_all(self, client, test_db):
        user, headers = _make_user(test_db)

        # Enable first
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        # Hide some dimensions
        client.put(
            SETTINGS_URL,
            json={"show_basic_info": False, "show_labs": False},
            headers=headers,
        )

        # show_all
        resp = client.post(BATCH_URL, json={"action": "show_all"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["is_public"] is True
        assert data["show_basic_info"] is True
        assert data["show_skill_radar"] is True
        assert data["show_labs"] is True
        assert data["show_certificates"] is True

    def test_hide_all(self, client, test_db):
        user, headers = _make_user(test_db)

        # Enable first
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        # hide_all
        resp = client.post(BATCH_URL, json={"action": "hide_all"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["is_public"] is True  # is_public stays true
        assert data["show_basic_info"] is False
        assert data["show_skill_radar"] is False
        assert data["show_labs"] is False
        assert data["show_certificates"] is False

    def test_batch_without_profile_returns_400(self, client, test_db):
        """No UserProfile record -> batch operations return 400."""
        user, headers = _make_user(test_db)

        resp = client.post(BATCH_URL, json={"action": "show_all"}, headers=headers)
        assert resp.status_code == 400
        assert "主页未开启" in resp.json()["detail"]

    def test_batch_with_closed_profile_returns_400(self, client, test_db):
        """is_public=false -> batch operations return 400."""
        user, headers = _make_user(test_db)

        # Enable then close
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)

        resp = client.post(BATCH_URL, json={"action": "show_all"}, headers=headers)
        assert resp.status_code == 400

    def test_invalid_action_returns_422(self, client, test_db):
        user, headers = _make_user(test_db)

        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        resp = client.post(BATCH_URL, json={"action": "invalid"}, headers=headers)
        assert resp.status_code == 422


class TestDisplayNameAndBioValidation:
    """display_name empty string -> null, bio max 200 chars."""

    def test_display_name_empty_string_becomes_null(self, client, test_db):
        user, headers = _make_user(test_db)

        resp = client.put(
            SETTINGS_URL,
            json={"is_public": True, "display_name": "   "},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["display_name"] is None

    def test_display_name_strips_to_null(self, client, test_db):
        user, headers = _make_user(test_db)

        resp = client.put(
            SETTINGS_URL,
            json={"display_name": "  "},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["display_name"] is None

    def test_bio_exceeds_200_chars_returns_422(self, client, test_db):
        user, headers = _make_user(test_db)

        long_bio = "a" * 201
        resp = client.put(
            SETTINGS_URL,
            json={"bio": long_bio},
            headers=headers,
        )
        assert resp.status_code == 422

    def test_bio_exactly_200_chars_ok(self, client, test_db):
        user, headers = _make_user(test_db)

        bio = "a" * 200
        resp = client.put(
            SETTINGS_URL,
            json={"bio": bio},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["bio"] == bio

    def test_display_name_max_50_chars(self, client, test_db):
        user, headers = _make_user(test_db)

        long_name = "a" * 51
        resp = client.put(
            SETTINGS_URL,
            json={"display_name": long_name},
            headers=headers,
        )
        assert resp.status_code == 422


class TestProfileUrl:
    """profile_url is always returned in settings responses."""

    def test_profile_url_present(self, client, test_db):
        user, headers = _make_user(test_db, username="testurl")

        resp = client.get(SETTINGS_URL, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "profile_url" in data
        assert "testurl" in data["profile_url"]

    def test_avatar_url_in_response(self, client, test_db):
        """avatar_url comes from User model if set."""
        user, headers = _make_user(test_db)
        # Update user avatar
        from app.models import User as UserModel

        db_user = test_db.query(UserModel).filter(UserModel.id == user.id).first()
        db_user.avatar_url = "https://example.com/avatar.png"
        test_db.commit()

        resp = client.get(SETTINGS_URL, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["avatar_url"] == "https://example.com/avatar.png"
