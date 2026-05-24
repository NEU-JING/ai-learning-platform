"""Integration tests for public profile feature (Task-5).

Covers the full lifecycle and all 12 ACs from spec.md:
  - AC1:  Full visibility — visitor sees all data
  - AC2:  Partial visibility — hidden dimensions return null
  - AC3:  First-time enable — auto-set all dimensions
  - AC4:  Adjust visibility → preview → copy link
  - AC5:  All dimensions hidden — still shows username
  - AC6:  Nonexistent user → 404
  - AC7:  Profile not enabled → 403
  - AC8:  Zero labs / zero certs — empty state
  - AC9:  Large dataset — labs_total reflects full count
  - AC10: OG tags present for public profile
  - AC11: Close profile → previously shared link returns 403
  - AC12: Concurrent access consistency

Security:
  - Un-enabled profile data cannot be probed via API
  - Disabled user returns 404 (not 403, no user existence leak)

Full lifecycle:
  Enable → Visit → Adjust visibility → Preview → Share → Close → Access fails
"""

import threading


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


def _make_user(
    test_db,
    username="intuser",
    email="int@example.com",
    is_active=True,
    avatar_url=None,
    with_auth=False,
):
    """Create a user. Returns (user_obj, auth_headers) if with_auth=True, else user_obj only."""
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
    if with_auth:
        token = create_access_token(data={"sub": user.id})
        return user, {"Authorization": f"Bearer {token}"}
    return user


def _enable_profile(test_db, user, **overrides):
    """Create UserProfile with is_public=True. Returns profile obj."""
    defaults = dict(
        user_id=user.id,
        is_public=True,
        show_basic_info=True,
        show_skill_radar=True,
        show_labs=True,
        show_certificates=True,
        display_name=user.username,
        bio="Integration bio",
    )
    defaults.update(overrides)
    profile = UserProfile(**defaults)
    test_db.add(profile)
    test_db.commit()
    test_db.refresh(profile)
    return profile


def _make_course_with_lab(test_db, title="Test Course", level="beginner"):
    """Create course + chapter + lab. Returns dict."""
    course = Course(
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
        title=f"Ch-{title}",
        content="# c",
        order_index=1,
        chapter_type="lab",
        duration_minutes=30,
    )
    test_db.add(chapter)
    test_db.flush()

    lab = Lab(
        chapter_id=chapter.id,
        title=f"Lab-{title}",
        description="d",
        starter_code="# s",
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


SETTINGS_URL = "/api/v1/profile/me/settings"
BATCH_URL = "/api/v1/profile/me/settings/batch"
PUBLIC_URL = "/api/v1/profile/{username}"


# ════════════════════════════════════════════════════════════════════════════
# AC1: Full visibility — visitor sees complete data
# ════════════════════════════════════════════════════════════════════════════


class TestAC1FullVisibility:
    """AC1: All dimensions visible → visitor sees complete profile."""

    def test_visitor_sees_all_data_without_login(self, client, test_db):
        user = _make_user(test_db, username="ac1user", avatar_url="https://img.test/ac1.png")
        _enable_profile(test_db, user, display_name="AC1张三", bio="专注CV方向的AI工程师")
        d = _make_course_with_lab(test_db, title="Python L2", level="intermediate")

        # Add passed lab
        sub = LabSubmission(
            user_id=user.id,
            lab_id=d["lab"].id,
            code="pass",
            status="passed",
            score=95.0,
            passed=True,
        )
        test_db.add(sub)

        # Complete course for certificate
        lp = LearningProgress(
            user_id=user.id,
            chapter_id=d["chapter"].id,
            status="completed",
        )
        test_db.add(lp)
        test_db.commit()

        # Access as anonymous visitor (no auth headers)
        resp = client.get(PUBLIC_URL.format(username="ac1user"))
        assert resp.status_code == 200
        data = resp.json()

        # Basic info
        assert data["username"] == "ac1user"
        assert data["display_name"] == "AC1张三"
        assert data["bio"] == "专注CV方向的AI工程师"
        assert data["avatar_url"] == "https://img.test/ac1.png"
        assert data["is_public"] is True

        # All visibility flags true
        vis = data["visibility"]
        assert all(
            vis[k] is True
            for k in ["show_basic_info", "show_skill_radar", "show_labs", "show_certificates"]
        )

        # Skill radar present
        assert data["skill_radar"] is not None
        assert "skills" in data["skill_radar"]

        # Labs present
        assert data["labs"] is not None
        assert len(data["labs"]) >= 1
        assert data["labs_total"] >= 1

        # Certificates present
        assert data["certificates"] is not None
        assert len(data["certificates"]) >= 1


# ════════════════════════════════════════════════════════════════════════════
# AC2: Partial visibility — hidden dimensions excluded
# ════════════════════════════════════════════════════════════════════════════


class TestAC2PartialVisibility:
    """AC2: Some dimensions hidden → hidden fields null, others normal."""

    def test_labs_and_certs_hidden_but_basic_info_and_radar_shown(self, client, test_db):
        user = _make_user(test_db, username="ac2lisi", avatar_url="https://img.test/lisi.png")
        _enable_profile(
            test_db, user, display_name="李四", show_labs=False, show_certificates=False
        )

        resp = client.get(PUBLIC_URL.format(username="ac2lisi"))
        assert resp.status_code == 200
        data = resp.json()

        # Visible dimensions
        assert data["display_name"] == "李四"
        assert data["avatar_url"] == "https://img.test/lisi.png"
        assert data["skill_radar"] is not None

        # Hidden dimensions
        assert data["labs"] is None
        assert data["labs_total"] is None
        assert data["certificates"] is None


# ════════════════════════════════════════════════════════════════════════════
# AC3: First-time enable — all dimensions auto-set to true
# ════════════════════════════════════════════════════════════════════════════


class TestAC3FirstTimeEnable:
    """AC3: User enables profile for the first time → all dimensions auto true."""

    def test_first_enable_auto_sets_all_dimensions(self, client, test_db):
        user, headers = _make_user(test_db, username="ac3wangwu", with_auth=True)

        # Before enable — defaults all false
        resp = client.get(SETTINGS_URL, headers=headers)
        assert resp.json()["is_public"] is False

        # Enable
        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["is_public"] is True
        assert data["show_basic_info"] is True
        assert data["show_skill_radar"] is True
        assert data["show_labs"] is True
        assert data["show_certificates"] is True
        assert data["profile_url"] is not None
        assert "ac3wangwu" in data["profile_url"]

    def test_display_name_defaults_to_username(self, client, test_db):
        user, headers = _make_user(test_db, username="ac3named", with_auth=True)
        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["display_name"] is not None


# ════════════════════════════════════════════════════════════════════════════
# AC4: Adjust visibility → preview → share (copy link)
# ════════════════════════════════════════════════════════════════════════════


class TestAC4AdjustAndPreview:
    """AC4: User adjusts visibility, previews, and shares."""

    def test_hide_basic_info_then_visit_matches_preview(self, client, test_db):
        user, headers = _make_user(
            test_db, username="ac4zhaoliu", avatar_url="https://img.test/zl.png", with_auth=True
        )
        _enable_profile(test_db, user, display_name="赵六", bio="AC4 bio")

        # Hide basic_info
        resp = client.put(SETTINGS_URL, json={"show_basic_info": False}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["show_basic_info"] is False
        assert resp.json()["is_public"] is True  # is_public unchanged

        # "Preview" = visit public profile (same data visitor sees)
        resp = client.get(PUBLIC_URL.format(username="ac4zhaoliu"))
        assert resp.status_code == 200
        data = resp.json()

        # basic_info hidden → display_name/bio/avatar_url all null
        assert data["display_name"] is None
        assert data["bio"] is None
        assert data["avatar_url"] is None
        # Other fields still visible
        assert data["username"] == "ac4zhaoliu"
        assert data["skill_radar"] is not None

    def test_profile_url_available_for_copy(self, client, test_db):
        user, headers = _make_user(test_db, username="ac4copy", with_auth=True)
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        resp = client.get(SETTINGS_URL, headers=headers)
        data = resp.json()
        assert data["profile_url"] is not None
        assert "ac4copy" in data["profile_url"]


# ════════════════════════════════════════════════════════════════════════════
# AC5: All dimensions hidden — profile still loads with username only
# ════════════════════════════════════════════════════════════════════════════


class TestAC5AllDimensionsHidden:
    """AC5: All dimensions hidden → only username + AILP branding."""

    def test_all_hidden_still_returns_200_with_username(self, client, test_db):
        user = _make_user(test_db, username="ac5sunqi")
        _enable_profile(
            test_db,
            user,
            show_basic_info=False,
            show_skill_radar=False,
            show_labs=False,
            show_certificates=False,
        )

        resp = client.get(PUBLIC_URL.format(username="ac5sunqi"))
        assert resp.status_code == 200
        data = resp.json()

        # Username always visible
        assert data["username"] == "ac5sunqi"
        assert data["is_public"] is True

        # All content hidden
        assert data["display_name"] is None
        assert data["bio"] is None
        assert data["avatar_url"] is None
        assert data["skill_radar"] is None
        assert data["labs"] is None
        assert data["labs_total"] is None
        assert data["certificates"] is None

    def test_no_not_enabled_message_when_all_hidden(self, client, test_db):
        """AC5 explicitly states: no '尚未公开' message when profile IS enabled
        but all dimensions are hidden."""
        user = _make_user(test_db, username="ac5nohint")
        _enable_profile(
            test_db,
            user,
            show_basic_info=False,
            show_skill_radar=False,
            show_labs=False,
            show_certificates=False,
        )

        resp = client.get(PUBLIC_URL.format(username="ac5nohint"))
        assert resp.status_code == 200  # Not 403


# ════════════════════════════════════════════════════════════════════════════
# AC6: Nonexistent user → 404
# ════════════════════════════════════════════════════════════════════════════


class TestAC6NonexistentUser:
    """AC6: Username does not exist → 404 with proper message."""

    def test_nonexistent_returns_404(self, client, test_db):
        resp = client.get(PUBLIC_URL.format(username="nonexistent999"))
        assert resp.status_code == 404
        assert "该用户不存在" in resp.json()["detail"]


# ════════════════════════════════════════════════════════════════════════════
# AC7: Profile not enabled → 403
# ════════════════════════════════════════════════════════════════════════════


class TestAC7ProfileNotEnabled:
    """AC7: User exists but profile not enabled → 403."""

    def test_never_enabled_returns_403(self, client, test_db):
        user = _make_user(test_db, username="ac7zhouba")
        # No UserProfile created

        resp = client.get(PUBLIC_URL.format(username="ac7zhouba"))
        assert resp.status_code == 403
        assert "该用户尚未公开能力主页" in resp.json()["detail"]

    def test_disabled_profile_returns_403(self, client, test_db):
        user = _make_user(test_db, username="ac7disabled")
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

        resp = client.get(PUBLIC_URL.format(username="ac7disabled"))
        assert resp.status_code == 403
        assert "该用户尚未公开能力主页" in resp.json()["detail"]


# ════════════════════════════════════════════════════════════════════════════
# AC8: Zero labs / zero certs — empty state display
# ════════════════════════════════════════════════════════════════════════════


class TestAC8ZeroData:
    """AC8: User with no labs/certs sees empty state."""

    def test_zero_labs_shows_empty_list(self, client, test_db):
        user = _make_user(test_db, username="ac8wujiu")
        _enable_profile(test_db, user)

        resp = client.get(PUBLIC_URL.format(username="ac8wujiu"))
        assert resp.status_code == 200
        data = resp.json()

        assert data["labs"] == []
        assert data["labs_total"] == 0
        assert data["certificates"] == []

    def test_zero_data_radar_shows_initial_scores(self, client, test_db):
        user = _make_user(test_db, username="ac8radar")
        _enable_profile(test_db, user)

        resp = client.get(PUBLIC_URL.format(username="ac8radar"))
        data = resp.json()

        # Radar should be present with initial (0) scores, not null
        assert data["skill_radar"] is not None
        assert data["skill_radar"]["overall_score"] == 0.0


# ════════════════════════════════════════════════════════════════════════════
# AC9: Large dataset — labs_total reflects full count
# ════════════════════════════════════════════════════════════════════════════


class TestAC9LargeDataset:
    """AC9: User with many labs — labs_total accurate, data complete."""

    def test_labs_total_matches_passed_submissions(self, client, test_db):
        user = _make_user(test_db, username="ac9dataking")
        _enable_profile(test_db, user)

        # Create 10 labs (enough to test count, 200 would be too slow for unit test)
        for i in range(10):
            d = _make_course_with_lab(test_db, title=f"Course-{i}")
            sub = LabSubmission(
                user_id=user.id,
                lab_id=d["lab"].id,
                code="pass",
                status="passed",
                score=80.0 + i,
                passed=True,
            )
            test_db.add(sub)
        test_db.commit()

        resp = client.get(PUBLIC_URL.format(username="ac9dataking"))
        assert resp.status_code == 200
        data = resp.json()

        assert data["labs_total"] == 10
        assert len(data["labs"]) == 10

    def test_labs_ordered_by_completed_at_desc(self, client, test_db):
        user = _make_user(test_db, username="ac9order")
        _enable_profile(test_db, user)

        from datetime import datetime, timedelta, timezone

        for i in range(3):
            d = _make_course_with_lab(test_db, title=f"Order-Course-{i}")
            ts = datetime.now(timezone.utc) - timedelta(days=2 - i)
            sub = LabSubmission(
                user_id=user.id,
                lab_id=d["lab"].id,
                code="pass",
                status="passed",
                score=80.0,
                passed=True,
                created_at=ts,
            )
            test_db.add(sub)
        test_db.commit()

        resp = client.get(PUBLIC_URL.format(username="ac9order"))
        data = resp.json()
        labs = data["labs"]
        # Most recent first
        for j in range(len(labs) - 1):
            assert labs[j]["completed_at"] >= labs[j + 1]["completed_at"]


# ════════════════════════════════════════════════════════════════════════════
# AC10: OG tags — social media preview (tested in test_profile_frontend.py)
# ════════════════════════════════════════════════════════════════════════════


class TestAC10OGTags:
    """AC10: OG meta tags present for public profile (API-level check)."""

    def test_public_profile_response_contains_username_for_og(self, client, test_db):
        user = _make_user(test_db, username="ac10og", avatar_url="https://img.test/og.png")
        _enable_profile(test_db, user, display_name="OG用户", bio="OG简介")

        resp = client.get(PUBLIC_URL.format(username="ac10og"))
        data = resp.json()

        # Data needed for OG tags: display_name, bio, skill_radar
        assert data["display_name"] == "OG用户"
        assert data["bio"] == "OG简介"
        assert data["skill_radar"] is not None


# ════════════════════════════════════════════════════════════════════════════
# AC11: Close profile → previously shared link returns 403
# ════════════════════════════════════════════════════════════════════════════


class TestAC11CloseProfileLinkInvalidated:
    """AC11: User closes profile → old link shows 403."""

    def test_close_then_visit_returns_403(self, client, test_db):
        user, headers = _make_user(test_db, username="ac11close", with_auth=True)

        # Step 1: Enable profile
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)

        # Step 2: Verify accessible
        resp = client.get(PUBLIC_URL.format(username="ac11close"))
        assert resp.status_code == 200

        # Step 3: Close profile
        resp = client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["is_public"] is False

        # Step 4: Old link now returns 403
        resp = client.get(PUBLIC_URL.format(username="ac11close"))
        assert resp.status_code == 403
        assert "该用户尚未公开能力主页" in resp.json()["detail"]

    def test_url_persists_after_close_and_reopen(self, client, test_db):
        """BR7: URL stays the same after close/reopen cycle."""
        user, headers = _make_user(test_db, username="ac11url", with_auth=True)

        # Enable
        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        url_before = resp.json()["profile_url"]

        # Close
        client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)

        # Re-enable
        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        url_after = resp.json()["profile_url"]

        assert url_before == url_after

    def test_reopen_resets_all_dimensions_to_visible(self, client, test_db):
        """BR5: Re-enabling resets all dimensions to true."""
        user, headers = _make_user(test_db, username="ac11reopen", with_auth=True)

        # Enable
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        # Close
        client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)
        # Re-enable
        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        data = resp.json()

        assert data["is_public"] is True
        assert data["show_basic_info"] is True
        assert data["show_skill_radar"] is True
        assert data["show_labs"] is True
        assert data["show_certificates"] is True


# ════════════════════════════════════════════════════════════════════════════
# AC12: Concurrent access consistency
# ════════════════════════════════════════════════════════════════════════════


class TestAC12ConcurrentAccess:
    """AC12: Multiple concurrent visitors see consistent data."""

    def test_concurrent_reads_return_same_data(self, client, test_db):
        user = _make_user(test_db, username="ac12concurrent")
        _enable_profile(test_db, user, display_name="并发测试", bio="AC12 bio")
        d = _make_course_with_lab(test_db, title="Concurrent Course")

        sub = LabSubmission(
            user_id=user.id,
            lab_id=d["lab"].id,
            code="pass",
            status="passed",
            score=88.0,
            passed=True,
        )
        test_db.add(sub)
        test_db.commit()

        url = PUBLIC_URL.format(username="ac12concurrent")
        results = []
        errors = []

        def fetch():
            try:
                resp = client.get(url)
                results.append((resp.status_code, resp.json()))
            except Exception as e:
                errors.append(str(e))

        # Simulate 20 concurrent visitors (enough for integration test;
        # real load test with 100 users is a perf test, not CI)
        threads = [threading.Thread(target=fetch) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert len(results) == 20

        # All responses should be 200
        for status_code, data in results:
            assert status_code == 200

        # All data should be identical (consistent view)
        first_data = results[0][1]
        for _, data in results[1:]:
            assert data["username"] == first_data["username"]
            assert data["display_name"] == first_data["display_name"]
            assert data["labs_total"] == first_data["labs_total"]


# ════════════════════════════════════════════════════════════════════════════
# Full lifecycle: Enable → Visit → Adjust → Preview → Share → Close → Fail
# ════════════════════════════════════════════════════════════════════════════


class TestFullLifecycle:
    """Complete lifecycle: enable → visit → adjust → preview → close → fail."""

    def test_complete_lifecycle_chain(self, client, test_db):
        user, headers = _make_user(
            test_db,
            username="lifecycle_user",
            avatar_url="https://img.test/life.png",
            with_auth=True,
        )

        # ── Step 1: Enable profile (AC3) ──
        resp = client.put(SETTINGS_URL, json={"is_public": True}, headers=headers)
        assert resp.status_code == 200
        settings = resp.json()
        assert settings["is_public"] is True
        assert all(
            settings[d] is True
            for d in ["show_basic_info", "show_skill_radar", "show_labs", "show_certificates"]
        )
        profile_url = settings["profile_url"]
        assert "lifecycle_user" in profile_url

        # ── Step 2: Visit as anonymous (AC1) ──
        resp = client.get(PUBLIC_URL.format(username="lifecycle_user"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "lifecycle_user"
        assert data["is_public"] is True

        # ── Step 3: Adjust visibility — hide labs (AC4) ──
        resp = client.put(SETTINGS_URL, json={"show_labs": False}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["show_labs"] is False
        assert resp.json()["is_public"] is True  # unchanged

        # ── Step 4: Preview — visit public profile (AC4 WYSIWYG) ──
        resp = client.get(PUBLIC_URL.format(username="lifecycle_user"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["labs"] is None  # hidden
        assert data["labs_total"] is None  # hidden
        assert data["skill_radar"] is not None  # still visible

        # ── Step 5: Share — verify profile_url accessible ──
        resp = client.get(SETTINGS_URL, headers=headers)
        assert "lifecycle_user" in resp.json()["profile_url"]

        # ── Step 6: Close profile (AC11) ──
        resp = client.put(SETTINGS_URL, json={"is_public": False}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["is_public"] is False

        # ── Step 7: Access fails — old link returns 403 ──
        resp = client.get(PUBLIC_URL.format(username="lifecycle_user"))
        assert resp.status_code == 403
        assert "该用户尚未公开能力主页" in resp.json()["detail"]


# ════════════════════════════════════════════════════════════════════════════
# Security: Data leakage prevention
# ════════════════════════════════════════════════════════════════════════════


class TestSecurityDataLeakage:
    """Security: Users without enabled profile cannot have data probed via API."""

    def test_no_profile_cannot_access_skill_radar_via_profile_api(self, client, test_db):
        """User with no profile → 403, no data leaked."""
        user = _make_user(test_db, username="sec_noprofile")
        # User has lab submissions but no profile
        d = _make_course_with_lab(test_db, title="Secret Course")
        sub = LabSubmission(
            user_id=user.id,
            lab_id=d["lab"].id,
            code="pass",
            status="passed",
            score=100.0,
            passed=True,
        )
        test_db.add(sub)
        test_db.commit()

        resp = client.get(PUBLIC_URL.format(username="sec_noprofile"))
        assert resp.status_code == 403
        # Response should not contain any user data
        body = resp.json()
        assert "skill_radar" not in body or body.get("skill_radar") is None
        assert "labs" not in body or body.get("labs") is None

    def test_disabled_profile_cannot_leak_data(self, client, test_db):
        """User with is_public=false → 403, no data leaked."""
        user = _make_user(test_db, username="sec_disabled")
        _enable_profile(test_db, user, is_public=False, display_name="Hidden Name")

        resp = client.get(PUBLIC_URL.format(username="sec_disabled"))
        assert resp.status_code == 403
        body = resp.json()
        # No personal data in response
        assert "display_name" not in body
        assert "bio" not in body

    def test_inactive_user_returns_404_not_403(self, client, test_db):
        """BR9: Disabled user returns 404, not 403 — prevents user existence leak."""
        user = _make_user(test_db, username="sec_inactive", is_active=False)
        _enable_profile(test_db, user)

        resp = client.get(PUBLIC_URL.format(username="sec_inactive"))
        assert resp.status_code == 404
        assert "该用户不存在" in resp.json()["detail"]

    def test_hidden_dimension_data_not_in_response(self, client, test_db):
        """When a dimension is hidden, its data must not appear in the response."""
        user = _make_user(
            test_db, username="sec_hidden_dim", avatar_url="https://img.test/secret.png"
        )
        _enable_profile(
            test_db,
            user,
            display_name="Secret Name",
            bio="Secret bio",
            show_basic_info=False,
            show_labs=False,
        )

        # Add data that should be hidden
        d = _make_course_with_lab(test_db, title="Hidden Lab")
        sub = LabSubmission(
            user_id=user.id,
            lab_id=d["lab"].id,
            code="pass",
            status="passed",
            score=99.0,
            passed=True,
        )
        test_db.add(sub)
        test_db.commit()

        resp = client.get(PUBLIC_URL.format(username="sec_hidden_dim"))
        assert resp.status_code == 200
        data = resp.json()

        # Hidden data must be null/None — no leakage
        assert data["display_name"] is None
        assert data["bio"] is None
        assert data["avatar_url"] is None
        assert data["labs"] is None
        assert data["labs_total"] is None

        # Visible data still present
        assert data["skill_radar"] is not None
        assert data["certificates"] is not None

    def test_anonymous_cannot_access_settings_endpoint(self, client, test_db):
        """Settings endpoint requires auth — anonymous gets 401."""
        resp = client.get(SETTINGS_URL)
        assert resp.status_code == 401

        resp = client.put(SETTINGS_URL, json={"is_public": True})
        assert resp.status_code == 401

    def test_user_cannot_modify_another_users_settings(self, client, test_db):
        """User A cannot change User B's settings."""
        user_a, headers_a = _make_user(
            test_db, username="userA", email="a@test.com", with_auth=True
        )
        user_b, headers_b = _make_user(
            test_db, username="userB", email="b@test.com", with_auth=True
        )

        # User B enables their profile
        client.put(SETTINGS_URL, json={"is_public": True}, headers=headers_b)

        # User A tries to use their own auth to modify — can only modify their own
        resp = client.put(SETTINGS_URL, json={"is_public": False}, headers=headers_a)
        assert resp.status_code == 200

        # User B's profile should still be enabled
        resp = client.get(SETTINGS_URL, headers=headers_b)
        assert resp.json()["is_public"] is True
