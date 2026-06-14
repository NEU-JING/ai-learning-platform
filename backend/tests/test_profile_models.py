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

    def test_userprofile_privacy_settings_default(self, test_db):
        """privacy_settings should default to standard visibility config."""
        user = User(
            email="pr1@test.com",
            username="pr1user",
            password_hash="hash",
            role="student",
            is_active=True,
        )
        test_db.add(user)
        test_db.commit()

        profile = UserProfile(
            user_id=user.id,
            is_public=False,
        )
        test_db.add(profile)
        test_db.commit()
        test_db.refresh(profile)

        assert profile.privacy_settings is not None
        # Default should contain standard keys
        ps = profile.privacy_settings
        assert "show_skill_radar" in ps
        assert "show_certifications" in ps
        assert "show_lab_history" in ps
        assert "show_ai_tutor_chats" in ps
        assert "allow_employer_view" in ps


class TestProfileCacheModel:
    """PR1: ProfileCache model for CDN/Redis caching layer."""

    def test_profile_cache_model_exists(self):
        """ProfileCache should be importable from app.models."""
        from app.models import ProfileCache
        assert ProfileCache is not None
        assert ProfileCache.__tablename__ == "profile_cache"

    def test_profile_cache_create_and_query(self, test_db):
        """ProfileCache can store and retrieve cached profile data."""
        from app.models import ProfileCache

        user = User(
            email="pr1cache@test.com",
            username="pr1cache",
            password_hash="hash",
            role="student",
            is_active=True,
        )
        test_db.add(user)
        test_db.commit()

        cache_data = {"username": "pr1cache", "display_name": "Test", "skill_radar": {}}
        entry = ProfileCache(
            user_id=user.id,
            cache_key="public_profile:pr1cache",
            cached_data=cache_data,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        test_db.add(entry)
        test_db.commit()
        test_db.refresh(entry)

        assert entry.id is not None
        assert entry.user_id == user.id
        assert entry.cache_key == "public_profile:pr1cache"
        assert entry.cached_data["username"] == "pr1cache"
        assert entry.expires_at is not None

        # Query back
        fetched = (
            test_db.query(ProfileCache)
            .filter(ProfileCache.cache_key == "public_profile:pr1cache")
            .first()
        )
        assert fetched is not None
        assert fetched.cached_data["display_name"] == "Test"

    def test_profile_cache_expires_at_column(self, test_db):
        """ProfileCache should support TTL via expires_at."""
        from app.models import ProfileCache

        user = User(
            email="pr1expire@test.com",
            username="pr1expire",
            password_hash="hash",
            role="student",
            is_active=True,
        )
        test_db.add(user)
        test_db.commit()

        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        entry = ProfileCache(
            user_id=user.id,
            cache_key="expired:key",
            cached_data={"test": True},
            expires_at=past_time,
        )
        test_db.add(entry)
        test_db.commit()

        # Query expired entries
        now = datetime.now(timezone.utc)
        expired = (
            test_db.query(ProfileCache)
            .filter(
                ProfileCache.cache_key == "expired:key",
                ProfileCache.expires_at < now,
            )
            .first()
        )
        assert expired is not None  # entry exists (expiry handled by cleanup)

    def test_profile_cache_unique_constraint(self, test_db):
        """ProfileCache should enforce unique (user_id, cache_key)."""
        from app.models import ProfileCache

        import pytest
        from sqlalchemy.exc import IntegrityError

        user = User(
            email="pr1uniq@test.com",
            username="pr1uniq",
            password_hash="hash",
            role="student",
            is_active=True,
        )
        test_db.add(user)
        test_db.commit()

        entry1 = ProfileCache(
            user_id=user.id,
            cache_key="same_key",
            cached_data={"v": 1},
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        test_db.add(entry1)
        test_db.commit()

        # Duplicate (same user_id, same cache_key) should fail
        entry2 = ProfileCache(
            user_id=user.id,
            cache_key="same_key",
            cached_data={"v": 2},
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        test_db.add(entry2)
        with pytest.raises(IntegrityError):
            test_db.commit()
        test_db.rollback()
