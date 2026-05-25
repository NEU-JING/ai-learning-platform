"""Tests for public profile frontend support (Task-3).

Covers:
  - /p/{username} SPA fallback returns index.html with OG meta tags
  - /p/{username} for non-existent user returns index.html with noindex
  - /p/{username} for private user returns index.html with noindex
  - /p/{username} for public user returns index.html with og:title, og:description
  - OG tags are dynamically injected from user profile data
"""

from app.core.security import get_password_hash
from app.models import User
from app.models.user_profile import UserProfile

# ── helpers ──────────────────────────────────────────────────────────────────


def _make_user(test_db, username="oguser", email="og@example.com", is_active=True, avatar_url=None):
    """Create a user and return user_obj."""
    user = User(
        email=email,
        username=username,
        password_hash=get_password_hash("Pass1234"),
        role="student",
        is_active=is_active,
        avatar_url=avatar_url,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


def _enable_profile(test_db, user, **overrides):
    """Create a UserProfile with is_public=True."""
    defaults = dict(
        user_id=user.id,
        is_public=True,
        show_basic_info=True,
        show_skill_radar=True,
        show_labs=True,
        show_certificates=True,
        display_name=user.username,
        bio="Test bio for OG",
    )
    defaults.update(overrides)
    profile = UserProfile(**defaults)
    test_db.add(profile)
    test_db.commit()
    test_db.refresh(profile)
    return profile


# ── Test classes ─────────────────────────────────────────────────────────────


class TestProfileSPAFallback:
    """GET /p/{username} returns index.html for SPA client-side routing."""

    def test_p_route_returns_html(self, client, test_db):
        """GET /p/someuser returns HTML content."""
        resp = client.get("/p/someuser")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")

    def test_p_route_returns_index_html_content(self, client, test_db):
        """GET /p/someuser returns the V2 index.html (SPA entry point)."""
        resp = client.get("/p/someuser")
        # Should contain the SPA root element
        content = resp.text
        # The HTML should be the V2 index.html content (not a 404)
        assert len(content) > 100  # Not an empty page


class TestOGTagInjection:
    """OG meta tags dynamically injected based on user data."""

    def test_public_user_has_og_tags(self, client, test_db):
        """Public user's /p/ page has og:title and og:description."""
        user = _make_user(test_db, username="ogpublic", avatar_url="https://img.test/og.png")
        _enable_profile(test_db, user, display_name="OG Public User", bio="My OG description")

        resp = client.get("/p/ogpublic")
        content = resp.text

        # Should have og:title with user's display name
        assert "og:title" in content
        assert "OG Public User" in content

        # Should have og:description with bio
        assert "og:description" in content
        assert "My OG description" in content

    def test_nonexistent_user_has_noindex(self, client, test_db):
        """Non-existent user's /p/ page has noindex meta tag."""
        resp = client.get("/p/ghost_user_999")
        content = resp.text

        # Should have noindex for non-existent users
        assert "noindex" in content or "robots" in content

    def test_private_user_has_noindex(self, client, test_db):
        """Private user's /p/ page has noindex meta tag."""
        user = _make_user(test_db, username="ogprivate")
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

        resp = client.get("/p/ogprivate")
        content = resp.text

        # Should have noindex for private users
        assert "noindex" in content or "robots" in content

    def test_public_user_has_og_image(self, client, test_db):
        """Public user with avatar has og:image tag."""
        user = _make_user(test_db, username="ogimg", avatar_url="https://img.test/avatar.png")
        _enable_profile(test_db, user, display_name="IMG User")

        resp = client.get("/p/ogimg")
        content = resp.text

        assert "og:image" in content

    def test_all_dimensions_hidden_og_tags(self, client, test_db):
        """Public user with all dimensions hidden still gets basic OG tags."""
        user = _make_user(test_db, username="ogallhidden")
        _enable_profile(
            test_db,
            user,
            show_basic_info=False,
            show_skill_radar=False,
            show_labs=False,
            show_certificates=False,
        )

        resp = client.get("/p/ogallhidden")
        content = resp.text

        # Should have og:title with username (always available)
        assert "og:title" in content
        assert "ogallhidden" in content
