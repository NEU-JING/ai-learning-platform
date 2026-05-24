"""Tests for public profile data API (Task-2).

Covers:
  - Full visibility: returns complete data (display_name, bio, avatar_url, skill_radar, labs, certificates)
  - Partial visibility: hidden fields return null/[], other fields normal
  - User not found: 404 + "该用户不存在"
  - UserProfile not exists (never configured): 403 + "该用户尚未公开能力主页"
  - is_public=false: 403
  - Zero labs zero certificates: labs=[], certificates=[], radar returns 0 scores
  - Deleted/disabled user (is_active=false): 404 (BR9)
"""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token, get_password_hash
from app.models import (
    Chapter,
    Course,
    Lab,
    LabSubmission,
    LearningProgress,
    User,
)
from app.models.user_profile import UserProfile


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_user(test_db, username="publicuser", email="public@example.com",
               is_active=True, avatar_url=None):
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
    """Create a UserProfile with is_public=True. Returns the profile obj."""
    defaults = dict(
        user_id=user.id,
        is_public=True,
        show_basic_info=True,
        show_skill_radar=True,
        show_labs=True,
        show_certificates=True,
        display_name=user.username,
        bio="Test bio",
    )
    defaults.update(overrides)
    profile = UserProfile(**defaults)
    test_db.add(profile)
    test_db.commit()
    test_db.refresh(profile)
    return profile


def _make_course_with_lab(test_db, title="Python Basics", level="beginner",
                          course_id=None):
    """Create a course + chapter + lab. Returns dict with all three."""
    course = Course(
        id=course_id,
        title=title,
        description="desc",
        level=level,
        category="python",
        duration_hours=10,
        is_published=True,
        order_index=1,
    )
    test_db.add(course)
    test_db.flush()

    chapter = Chapter(
        course_id=course.id,
        title=f"Chapter of {title}",
        content="# content",
        order_index=1,
        chapter_type="lab",
        duration_minutes=30,
    )
    test_db.add(chapter)
    test_db.flush()

    lab = Lab(
        chapter_id=chapter.id,
        title=f"Lab for {title}",
        description="desc",
        starter_code="# code",
        solution_code="pass",
        test_cases=[],
        hints=[],
        time_limit_seconds=30,
        memory_limit_mb=256,
    )
    test_db.add(lab)
    test_db.commit()
    test_db.refresh(course)
    test_db.refresh(chapter)
    test_db.refresh(lab)

    return {"course": course, "chapter": chapter, "lab": lab}


PUBLIC_URL = "/api/v1/profile/{username}"


# ── Test classes ─────────────────────────────────────────────────────────────

class TestFullVisibility:
    """All dimensions visible → returns complete data."""

    def test_returns_complete_data(self, client, test_db):
        user = _make_user(test_db, username="fullvis", avatar_url="https://img.test/avatar.png")
        _enable_profile(test_db, user, display_name="Full User", bio="My bio")
        data_dict = _make_course_with_lab(test_db, title="Python Basics", level="beginner")

        # Add a passed lab submission
        sub = LabSubmission(
            user_id=user.id,
            lab_id=data_dict["lab"].id,
            code="pass",
            status="passed",
            score=95.0,
            passed=True,
        )
        test_db.add(sub)

        # Mark chapter as completed
        lp = LearningProgress(
            user_id=user.id,
            chapter_id=data_dict["chapter"].id,
            status="completed",
        )
        test_db.add(lp)
        test_db.commit()

        resp = client.get(PUBLIC_URL.format(username="fullvis"))
        assert resp.status_code == 200
        data = resp.json()

        # Basic info visible
        assert data["username"] == "fullvis"
        assert data["display_name"] == "Full User"
        assert data["bio"] == "My bio"
        assert data["avatar_url"] == "https://img.test/avatar.png"
        assert data["is_public"] is True

        # Visibility flags
        vis = data["visibility"]
        assert vis["show_basic_info"] is True
        assert vis["show_skill_radar"] is True
        assert vis["show_labs"] is True
        assert vis["show_certificates"] is True

        # Skill radar present (not null)
        assert data["skill_radar"] is not None
        assert "skills" in data["skill_radar"]
        assert "overall_score" in data["skill_radar"]

        # Labs present
        assert data["labs"] is not None
        assert len(data["labs"]) >= 1
        lab_item = data["labs"][0]
        assert lab_item["lab_id"] == data_dict["lab"].id
        assert lab_item["score"] == 95.0
        assert lab_item["lab_title"] == data_dict["lab"].title
        assert lab_item["course_title"] == data_dict["course"].title

        # Labs total
        assert data["labs_total"] is not None
        assert data["labs_total"] >= 1

        # Certificates present (course completed → certificate generated)
        assert data["certificates"] is not None
        assert len(data["certificates"]) >= 1
        cert_item = data["certificates"][0]
        assert cert_item["course_title"] == "Python Basics"
        assert cert_item["level"] == "beginner"
        assert cert_item["level_label"] == "入门认证"
        assert "cert_id" in cert_item
        assert "verify_url" in cert_item


class TestPartialVisibility:
    """Some dimensions hidden → hidden fields return null/[], others normal."""

    def test_basic_info_hidden(self, client, test_db):
        user = _make_user(test_db, username="partial1")
        _enable_profile(test_db, user, show_basic_info=False, display_name="Hidden", bio="Hidden bio")

        resp = client.get(PUBLIC_URL.format(username="partial1"))
        assert resp.status_code == 200
        data = resp.json()

        # Basic info fields should be null
        assert data["display_name"] is None
        assert data["bio"] is None
        assert data["avatar_url"] is None

        # Other fields still present
        assert data["username"] == "partial1"
        assert data["skill_radar"] is not None
        assert data["labs"] is not None

    def test_skill_radar_hidden(self, client, test_db):
        user = _make_user(test_db, username="partial2")
        _enable_profile(test_db, user, show_skill_radar=False)

        resp = client.get(PUBLIC_URL.format(username="partial2"))
        assert resp.status_code == 200
        data = resp.json()

        assert data["skill_radar"] is None
        # Other fields still present
        assert data["display_name"] is not None

    def test_labs_hidden(self, client, test_db):
        user = _make_user(test_db, username="partial3")
        _enable_profile(test_db, user, show_labs=False)

        resp = client.get(PUBLIC_URL.format(username="partial3"))
        assert resp.status_code == 200
        data = resp.json()

        assert data["labs"] is None
        assert data["labs_total"] is None

    def test_certificates_hidden(self, client, test_db):
        user = _make_user(test_db, username="partial4")
        _enable_profile(test_db, user, show_certificates=False)

        resp = client.get(PUBLIC_URL.format(username="partial4"))
        assert resp.status_code == 200
        data = resp.json()

        assert data["certificates"] is None

    def test_all_dimensions_hidden_but_is_public(self, client, test_db):
        """AC5: All dimensions hidden, only username visible."""
        user = _make_user(test_db, username="allhidden")
        _enable_profile(
            test_db, user,
            show_basic_info=False,
            show_skill_radar=False,
            show_labs=False,
            show_certificates=False,
        )

        resp = client.get(PUBLIC_URL.format(username="allhidden"))
        assert resp.status_code == 200
        data = resp.json()

        assert data["username"] == "allhidden"
        assert data["display_name"] is None
        assert data["bio"] is None
        assert data["avatar_url"] is None
        assert data["skill_radar"] is None
        assert data["labs"] is None
        assert data["labs_total"] is None
        assert data["certificates"] is None


class TestUserNotFound:
    """Username does not exist → 404."""

    def test_nonexistent_username_returns_404(self, client, test_db):
        resp = client.get(PUBLIC_URL.format(username="ghost_user"))
        assert resp.status_code == 404
        assert "该用户不存在" in resp.json()["detail"]


class TestNoProfileRecord:
    """User exists but never configured UserProfile → 403."""

    def test_no_profile_returns_403(self, client, test_db):
        user = _make_user(test_db, username="noprofile")
        # No UserProfile created

        resp = client.get(PUBLIC_URL.format(username="noprofile"))
        assert resp.status_code == 403
        assert "该用户尚未公开能力主页" in resp.json()["detail"]


class TestProfileNotPublic:
    """User has UserProfile but is_public=false → 403."""

    def test_is_public_false_returns_403(self, client, test_db):
        user = _make_user(test_db, username="private1")
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

        resp = client.get(PUBLIC_URL.format(username="private1"))
        assert resp.status_code == 403
        assert "该用户尚未公开能力主页" in resp.json()["detail"]


class TestZeroLabsZeroCertificates:
    """User has public profile but zero lab submissions and zero completed courses."""

    def test_empty_labs_and_certs(self, client, test_db):
        user = _make_user(test_db, username="empty1")
        _enable_profile(test_db, user)

        resp = client.get(PUBLIC_URL.format(username="empty1"))
        assert resp.status_code == 200
        data = resp.json()

        # Labs should be empty list
        assert data["labs"] == []
        assert data["labs_total"] == 0

        # Certificates should be empty list
        assert data["certificates"] == []

        # Skill radar should have 0 scores
        assert data["skill_radar"] is not None
        radar = data["skill_radar"]
        assert radar["overall_score"] == 0.0


class TestDisabledUser:
    """BR9: is_active=false → 404, same as user not found."""

    def test_inactive_user_returns_404(self, client, test_db):
        user = _make_user(test_db, username="disabled1", is_active=False)
        _enable_profile(test_db, user)

        resp = client.get(PUBLIC_URL.format(username="disabled1"))
        assert resp.status_code == 404
        assert "该用户不存在" in resp.json()["detail"]


class TestLabListOrdering:
    """Labs ordered by completed_at desc, best score per lab."""

    def test_labs_ordered_by_completed_at_desc(self, client, test_db):
        user = _make_user(test_db, username="ordered1")
        _enable_profile(test_db, user)

        d1 = _make_course_with_lab(test_db, title="Course A")
        d2 = _make_course_with_lab(test_db, title="Course B")

        # Submission for lab 1 (earlier)
        from datetime import datetime, timezone, timedelta
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        sub1 = LabSubmission(
            user_id=user.id,
            lab_id=d1["lab"].id,
            code="pass",
            status="passed",
            score=80.0,
            passed=True,
            created_at=yesterday,
        )
        test_db.add(sub1)

        # Submission for lab 2 (today)
        sub2 = LabSubmission(
            user_id=user.id,
            lab_id=d2["lab"].id,
            code="pass",
            status="passed",
            score=90.0,
            passed=True,
        )
        test_db.add(sub2)
        test_db.commit()

        resp = client.get(PUBLIC_URL.format(username="ordered1"))
        assert resp.status_code == 200
        data = resp.json()

        labs = data["labs"]
        assert len(labs) == 2
        # Most recent first
        assert labs[0]["lab_id"] == d2["lab"].id
        assert labs[1]["lab_id"] == d1["lab"].id

    def test_best_score_per_lab(self, client, test_db):
        """Multiple submissions for same lab → only best score shown."""
        user = _make_user(test_db, username="bestscore1")
        _enable_profile(test_db, user)

        d1 = _make_course_with_lab(test_db, title="Course X")

        # Lower score submission
        sub1 = LabSubmission(
            user_id=user.id,
            lab_id=d1["lab"].id,
            code="pass1",
            status="passed",
            score=60.0,
            passed=True,
        )
        test_db.add(sub1)

        # Higher score submission
        sub2 = LabSubmission(
            user_id=user.id,
            lab_id=d1["lab"].id,
            code="pass2",
            status="passed",
            score=95.0,
            passed=True,
        )
        test_db.add(sub2)
        test_db.commit()

        resp = client.get(PUBLIC_URL.format(username="bestscore1"))
        assert resp.status_code == 200
        data = resp.json()

        # Only one lab entry, with the best score
        assert len(data["labs"]) == 1
        assert data["labs"][0]["score"] == 95.0


class TestCertificateGeneration:
    """Certificates derived from completed courses."""

    def test_certificate_fields(self, client, test_db):
        user = _make_user(test_db, username="certuser")
        _enable_profile(test_db, user)
        d = _make_course_with_lab(test_db, title="Advanced ML", level="advanced")

        # Complete all chapters
        lp = LearningProgress(
            user_id=user.id,
            chapter_id=d["chapter"].id,
            status="completed",
        )
        test_db.add(lp)
        test_db.commit()

        resp = client.get(PUBLIC_URL.format(username="certuser"))
        assert resp.status_code == 200
        data = resp.json()

        certs = data["certificates"]
        assert len(certs) >= 1
        cert = certs[0]
        assert cert["course_title"] == "Advanced ML"
        assert cert["level"] == "advanced"
        assert cert["level_label"] == "高级认证"
        # cert_id format: AI-{course_id}-{user_id}-{date}
        assert cert["cert_id"].startswith("AI-")
        assert "/api/v1/certificates/verify/" in cert["verify_url"]

    def test_no_certificate_for_incomplete_course(self, client, test_db):
        user = _make_user(test_db, username="incomplete1")
        _enable_profile(test_db, user)
        d = _make_course_with_lab(test_db, title="Incomplete Course")

        # Mark only partial progress (not completed)
        lp = LearningProgress(
            user_id=user.id,
            chapter_id=d["chapter"].id,
            status="in_progress",
        )
        test_db.add(lp)
        test_db.commit()

        resp = client.get(PUBLIC_URL.format(username="incomplete1"))
        assert resp.status_code == 200
        data = resp.json()

        assert data["certificates"] == []
