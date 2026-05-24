"""Tests for profile analytics events and observability logging (CRITICAL-1).

Covers:
  - profile_enabled event: is_public false→true
  - profile_disabled event: is_public true→false
  - privacy_toggle event: dimension visibility change
  - profile_batch_action event: show_all / hide_all
  - profile_view event + log: GET public profile (with viewer IP)
  - profile_404 / profile_403 observability logs
  - profile_settings_update observability log
  - AnalyticsEvent records created in DB
"""

from unittest.mock import patch


from app.core.security import create_access_token, get_password_hash
from app.models import AnalyticsEvent, User
from app.models.user_profile import UserProfile

# ── helpers ──────────────────────────────────────────────────────────────────


def _make_user(test_db, username="analyticsuser", email="analytics@example.com"):
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
PUBLIC_URL = "/api/v1/profile/{username}"


def _get_profile_events(test_db, event_type: str) -> list[AnalyticsEvent]:
    """Query AnalyticsEvent records for profile-related events."""
    return test_db.query(AnalyticsEvent).filter(AnalyticsEvent.event_type == event_type).all()


# ── Analytics event tests (DB records) ──────────────────────────────────────


class TestProfileEnabledEvent:
    """profile_enabled event when is_public transitions false→true."""

    def test_first_enable_creates_profile_enabled_event(self, client, test_db):
        user, headers = _make_user(test_db, username="en1")
        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        assert resp.status_code == 200

        events = _get_profile_events(test_db, "profile_enabled")
        assert len(events) >= 1
        evt = events[-1]
        assert evt.event_data.get("username") == "en1"

    def test_re_enable_creates_profile_enabled_event(self, client, test_db):
        user, headers = _make_user(test_db, username="reen1")
        # Enable
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        # Disable
        client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)
        # Re-enable
        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        assert resp.status_code == 200

        events = _get_profile_events(test_db, "profile_enabled")
        # Should have 2 profile_enabled events (first + re-enable)
        assert len(events) >= 2


class TestProfileDisabledEvent:
    """profile_disabled event when is_public transitions true→false."""

    def test_disable_creates_profile_disabled_event(self, client, test_db):
        user, headers = _make_user(test_db, username="dis1")
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        resp = client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)
        assert resp.status_code == 200

        events = _get_profile_events(test_db, "profile_disabled")
        assert len(events) >= 1
        evt = events[-1]
        assert evt.event_data.get("username") == "dis1"


class TestPrivacyToggleEvent:
    """privacy_toggle event when a dimension visibility changes."""

    def test_toggle_dimension_creates_privacy_toggle_event(self, client, test_db):
        user, headers = _make_user(test_db, username="tog1")
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        # Toggle one dimension off
        resp = client.put(SETTINGS_URL, json={"show_basic_info": False}, headers=headers)
        assert resp.status_code == 200

        events = _get_profile_events(test_db, "privacy_toggle")
        assert len(events) >= 1
        evt = events[-1]
        assert "show_basic_info" in evt.event_data.get("changed_dimensions", [])

    def test_toggle_multiple_dimensions(self, client, test_db):
        user, headers = _make_user(test_db, username="tog2")
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        resp = client.put(
            SETTINGS_URL,
            json={"show_basic_info": False, "show_labs": False},
            headers=headers,
        )
        assert resp.status_code == 200

        events = _get_profile_events(test_db, "privacy_toggle")
        assert len(events) >= 1
        evt = events[-1]
        dims = evt.event_data.get("changed_dimensions", [])
        assert "show_basic_info" in dims
        assert "show_labs" in dims


class TestProfileBatchActionEvent:
    """profile_batch_action event on show_all / hide_all."""

    def test_show_all_creates_batch_event(self, client, test_db):
        user, headers = _make_user(test_db, username="batch1")
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        resp = client.post(BATCH_URL, json={"action": "show_all"}, headers=headers)
        assert resp.status_code == 200

        events = _get_profile_events(test_db, "profile_batch_action")
        assert len(events) >= 1
        evt = events[-1]
        assert evt.event_data.get("action") == "show_all"

    def test_hide_all_creates_batch_event(self, client, test_db):
        user, headers = _make_user(test_db, username="batch2")
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        resp = client.post(BATCH_URL, json={"action": "hide_all"}, headers=headers)
        assert resp.status_code == 200

        events = _get_profile_events(test_db, "profile_batch_action")
        assert len(events) >= 1
        evt = events[-1]
        assert evt.event_data.get("action") == "hide_all"


class TestProfileViewEvent:
    """profile_view event when public profile is accessed."""

    def test_public_profile_view_creates_event(self, client, test_db):
        user, headers = _make_user(test_db, username="view1")
        # Enable profile
        profile = UserProfile(
            user_id=user.id,
            is_public=True,
            show_basic_info=True,
            show_skill_radar=True,
            show_labs=True,
            show_certificates=True,
            display_name="View1",
            bio="bio",
        )
        test_db.add(profile)
        test_db.commit()

        resp = client.get(PUBLIC_URL.format(username="view1"))
        assert resp.status_code == 200

        events = _get_profile_events(test_db, "profile_view")
        assert len(events) >= 1
        evt = events[-1]
        assert evt.event_data.get("viewed_username") == "view1"
        # profile_view events have no user_id (anonymous viewer)
        assert evt.user_id is None


# ── Observability logging tests ─────────────────────────────────────────────


class TestObservabilityLogs:
    """Verify structured log messages are emitted at the right times.

    Uses direct logger mock because FastAPI TestClient may run in a
    different thread where caplog cannot capture records reliably.
    """

    def test_profile_settings_update_log(self, client, test_db):
        user, headers = _make_user(test_db, username="log1")
        with patch("app.services.profile_service.logger") as mock_logger:
            client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        log_messages = [str(c) for c in mock_logger.info.call_args_list]
        assert any("profile_settings_update" in m for m in log_messages)
        assert any("profile_enabled" in m for m in log_messages)

    def test_profile_view_log_with_ip(self, client, test_db):
        user, headers = _make_user(test_db, username="logview1")
        profile = UserProfile(
            user_id=user.id,
            is_public=True,
            show_basic_info=True,
            show_skill_radar=True,
            show_labs=True,
            show_certificates=True,
        )
        test_db.add(profile)
        test_db.commit()

        with patch("app.services.profile_service.logger") as mock_logger:
            client.get(PUBLIC_URL.format(username="logview1"))

        log_messages = [str(c) for c in mock_logger.info.call_args_list]
        assert any("profile_view" in m for m in log_messages)

    def test_profile_404_log(self, client, test_db):
        with patch("app.services.profile_service.logger") as mock_logger:
            resp = client.get(PUBLIC_URL.format(username="ghost_404"))
        assert resp.status_code == 404

        log_messages = [str(c) for c in mock_logger.info.call_args_list]
        assert any("profile_404" in m for m in log_messages)

    def test_profile_403_no_profile_log(self, client, test_db):
        user, headers = _make_user(test_db, username="log403")
        # User exists but no UserProfile

        with patch("app.services.profile_service.logger") as mock_logger:
            resp = client.get(PUBLIC_URL.format(username="log403"))
        assert resp.status_code == 403

        log_messages = [str(c) for c in mock_logger.info.call_args_list]
        assert any("profile_403" in m for m in log_messages)

    def test_profile_403_not_public_log(self, client, test_db):
        user, headers = _make_user(test_db, username="log403b")
        profile = UserProfile(
            user_id=user.id,
            is_public=False,
            show_basic_info=True,
            show_skill_radar=True,
            show_labs=True,
            show_certificates=True,
        )
        test_db.add(profile)
        test_db.commit()

        with patch("app.services.profile_service.logger") as mock_logger:
            resp = client.get(PUBLIC_URL.format(username="log403b"))
        assert resp.status_code == 403

        log_messages = [str(c) for c in mock_logger.info.call_args_list]
        assert any("profile_403" in m for m in log_messages)

    def test_profile_disabled_log(self, client, test_db):
        user, headers = _make_user(test_db, username="logdis1")
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        with patch("app.services.profile_service.logger") as mock_logger:
            client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)

        log_messages = [str(c) for c in mock_logger.info.call_args_list]
        assert any("profile_disabled" in m for m in log_messages)

    def test_privacy_toggle_log(self, client, test_db):
        user, headers = _make_user(test_db, username="logtog1")
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        with patch("app.services.profile_service.logger") as mock_logger:
            client.put(SETTINGS_URL, json={"show_basic_info": False}, headers=headers)

        log_messages = [str(c) for c in mock_logger.info.call_args_list]
        assert any("privacy_toggle" in m for m in log_messages)

    def test_batch_action_log(self, client, test_db):
        user, headers = _make_user(test_db, username="logbatch1")
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        with patch("app.services.profile_service.logger") as mock_logger:
            client.post(BATCH_URL, json={"action": "hide_all"}, headers=headers)

        log_messages = [str(c) for c in mock_logger.info.call_args_list]
        assert any("profile_batch_action" in m for m in log_messages)


class TestAnalyticsEventResilience:
    """Analytics emission should never break the main flow."""

    def test_emit_failure_does_not_break_update(self, client, test_db):
        user, headers = _make_user(test_db, username="resilient1")
        with patch(
            "app.services.profile_service.AnalyticsService.ingest_events",
            side_effect=Exception("DB connection lost"),
        ):
            resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
            # Main flow should still succeed
            assert resp.status_code == 200
            assert resp.json()["is_public"] is True
