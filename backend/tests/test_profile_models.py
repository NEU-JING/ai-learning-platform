"""Tests for profile module data models — PR1 (RED phase).

Covers:
  - UserProfile model has new design fields (privacy_settings, theme, view_count, etc.)
  - ProfileCache model can be created, queried, and has TTL expiry logic
  - ProfileCache stores/retrieves serialized profile data
"""

import json
from datetime import datetime, timedelta, timezone

from app.models import User
from app.models.user_profile import UserProfile


class TestUserProfileModelExtensions:
    """PR1: UserProfile should have new design fields."""

    def test_userprofile_has_privacy_settings_field(self, test_db):
        """UserProfile model should have privacy_settings JSONB column."""
        from sqlalchemy import inspect
        inspector = inspect(UserProfile)
        columns = {c.name: c for c in inspector.columns}
        assert "privacy_settings" in columns, "privacy_settings column missing"
        # Should be JSON type
        assert str(columns["privacy_settings"].type).lower() in ("json", "jsonb")

    def test_userprofile_has_theme_field(self, test_db):
        """UserProfile model should have theme column."""
        from sqlalchemy import inspect
        inspector = inspect(UserProfile)
        columns = {c.name: c for c in inspector.columns}
        assert "theme" in columns, "theme column missing"

    def test_userprofile_has_view_count_field(self, test_db):
        """UserProfile model should have view_count column."""
        from sqlalchemy import inspect
        inspector = inspect(UserProfile)
        columns = {c.name: c for c in inspector.columns}
        assert "view_count" in columns, "view_count column missing"

    def test_userprofile_has_last_synced_at_field(self, test_db):
        """UserProfile model should have last_synced_at column."""
        from sqlalchemy import inspect
        inspector = inspect(UserProfile)
        columns = {c.name: c for c in inspector.columns}
        assert "last_synced_at" in columns, "last_synced_at column missing"

    def test_userprofile_has_custom_title_field(self, test_db):
        """UserProfile model should have custom_title column."""
        from sqlalchemy import inspect
        inspector = inspect(UserProfile)
        columns = {c.name: c for c in inspector.columns}
        assert "custom_title" in columns, "custom_title column missing"

