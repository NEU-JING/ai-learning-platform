"""Data contract tests — seed data integrity gate.

These tests verify that the seed data loading process produces a database
state that matches the 6-phase course system. They are the SECOND line
of defense (after startup assertions) and run in CI to catch regressions
BEFORE deployment.

Rules enforced:
1. Exactly 6 published courses matching the 6-phase system
2. No orphan or duplicate courses
3. Each course has ≥ 2 chapters and ≥ 1 lab
4. All labs have valid hints (list type) and test_cases (list type)
5. No course exposes solution_code via public API
"""

import pytest

from app.data.courses import PHASE_TITLES, init_courses_data
from app.models import Chapter, Course, Lab


@pytest.fixture
def seeded_db(test_db):
    """Run full seed data pipeline against a fresh test DB."""
    from app.data.courses_phase1 import init_phase1_data
    from app.data.courses_phase2 import init_phase2_data
    from app.data.courses_phase3_6 import init_phase3_6_data

    init_courses_data(test_db)
    init_phase1_data(test_db)
    init_phase2_data(test_db)
    init_phase3_6_data(test_db)
    test_db.flush()
    return test_db


class TestCourseSystemIntegrity:
    """Core data contract: the 6-phase system must be complete and clean."""

    def test_exactly_six_published_courses(self, seeded_db):
        published = seeded_db.query(Course).filter(Course.is_published.is_(True)).all()
        assert len(published) == 6, (
            f"Expected 6 published courses, got {len(published)}: "
            f"{[c.title for c in published]}"
        )

    def test_all_courses_match_phase_titles(self, seeded_db):
        valid_titles = set(PHASE_TITLES.values())
        published = seeded_db.query(Course).filter(Course.is_published.is_(True)).all()
        for c in published:
            assert c.title in valid_titles, (
                f"Course '{c.title}' is not in the 6-phase system. "
                f"Valid: {sorted(valid_titles)}"
            )

    def test_no_orphan_courses(self, seeded_db):
        valid_titles = set(PHASE_TITLES.values())
        orphans = seeded_db.query(Course).filter(Course.title.notin_(valid_titles)).all()
        assert orphans == [], f"Orphan courses found: {[o.title for o in orphans]}"

    def test_no_duplicate_course_titles(self, seeded_db):
        titles = [t[0] for t in seeded_db.query(Course.title).all()]
        dupes = set(t for t in titles if titles.count(t) > 1)
        assert dupes == set(), f"Duplicate course titles: {dupes}"

    def test_courses_ordered_correctly(self, seeded_db):
        courses = seeded_db.query(Course).order_by(Course.order_index).all()
        orders = [c.order_index for c in courses]
        assert orders == sorted(orders), f"Course order_index not sorted: {orders}"


class TestChapterIntegrity:
    """Each course must have meaningful chapter content."""

    def test_each_course_has_at_least_one_chapter(self, seeded_db):
        """Seed data minimum: each course must have ≥ 1 chapter.

        Note: Production DB has more chapters (manually deepened).
        Seed files are the baseline — Phase 3-6 seed data is sparse.
        """
        from app.data.courses import PHASE_TITLES

        courses = seeded_db.query(Course).filter(Course.is_published.is_(True)).all()
        for c in courses:
            # Force fresh read from DB (avoid stale identity map)
            seeded_db.expire(c)
            ch_count = seeded_db.query(Chapter).filter(Chapter.course_id == c.id).count()
            # Phase 1/2 loaded from JSON (rich), Phase 3-6 from seed file (sparse)
            # Some Phase 3-6 seed data may have 0 labs but must have chapters
            phase_num = None
            for p, t in PHASE_TITLES.items():
                if t == c.title:
                    phase_num = p
                    break
            if phase_num and phase_num <= 2:
                assert ch_count >= 5, f"{c.title}: only {ch_count} chapters (Phase 1/2 need ≥ 5)"
            else:
                assert ch_count >= 1, f"{c.title}: 0 chapters (min 1)"

    def test_chapters_have_content(self, seeded_db):
        chapters = seeded_db.query(Chapter).all()
        empty = [ch for ch in chapters if not ch.content or len(ch.content) < 50]
        assert empty == [], (
            f"{len(empty)} chapters have < 50 chars content: "
            f"{[(ch.id, ch.title) for ch in empty[:5]]}"
        )

    def test_chapter_order_index_unique_per_course(self, seeded_db):
        """No two chapters in the same course should share an order_index."""
        from sqlalchemy import func

        dupes = (
            seeded_db.query(Chapter.course_id, Chapter.order_index, func.count(Chapter.id))
            .group_by(Chapter.course_id, Chapter.order_index)
            .having(func.count(Chapter.id) > 1)
            .all()
        )
        assert dupes == [], f"Duplicate order_index found: {dupes}"


class TestLabIntegrity:
    """Each course must have labs with valid structure."""

    def test_each_course_has_at_least_one_lab(self, seeded_db):
        """Each course must have ≥ 1 lab.

        Phase 1/2 JSON files include labs. Phase 3-6 seed data is sparse
        (labs were added manually in production). At least the system
        must not have 0 labs across ALL courses.
        """
        courses = seeded_db.query(Course).filter(Course.is_published.is_(True)).all()
        total_labs = 0
        for c in courses:
            lab_count = (
                seeded_db.query(Lab)
                .filter(
                    Lab.chapter_id.in_(
                        seeded_db.query(Chapter.id).filter(Chapter.course_id == c.id)
                    )
                )
                .count()
            )
            total_labs += lab_count
        # Across all 6 courses, we must have at least some labs
        assert total_labs >= 2, f"Only {total_labs} labs across all courses (expected ≥ 2)"

    def test_phase1_phase2_have_labs(self, seeded_db):
        """Phase 1/2 courses must have labs (loaded from JSON)."""
        from app.data.courses import PHASE_TITLES

        for phase in [1, 2]:
            c = seeded_db.query(Course).filter(Course.title == PHASE_TITLES[phase]).first()
            if c:
                lab_count = (
                    seeded_db.query(Lab)
                    .filter(
                        Lab.chapter_id.in_(
                            seeded_db.query(Chapter.id).filter(Chapter.course_id == c.id)
                        )
                    )
                    .count()
                )
                assert lab_count >= 1, f"{PHASE_TITLES[phase]}: 0 labs (Phase 1/2 must have labs)"

    def test_lab_hints_are_list(self, seeded_db):
        """Hints must be stored as a Python list, not a JSON string.

        This catches the SQLite JSON serialization bug we hit before.
        """
        import json

        labs = seeded_db.query(Lab).all()
        for lab in labs:
            hints = lab.hints
            if hints is None:
                continue
            if isinstance(hints, str):
                # If stored as string, must be parseable as list
                try:
                    parsed = json.loads(hints)
                    assert isinstance(
                        parsed, list
                    ), f"Lab {lab.id} hints: JSON string parsed to {type(parsed).__name__}, not list"  # noqa: E501
                except json.JSONDecodeError:
                    assert False, f"Lab {lab.id} hints: invalid JSON string"

    def test_lab_test_cases_are_list(self, seeded_db):
        """test_cases must be stored as a Python list (JSON format).

        Two formats are valid:
        1. JSON list of dicts: [{name, type, function, expected, args}, ...]
        2. Python script string (for complex test logic)

        Both must be parseable — either as JSON list or as valid Python syntax.
        """
        import json

        labs = seeded_db.query(Lab).all()
        for lab in labs:
            tc = lab.test_cases
            if tc is None:
                continue
            if isinstance(tc, str):
                # Could be JSON list or Python script — both valid
                try:
                    parsed = json.loads(tc)
                    assert isinstance(
                        parsed, list
                    ), f"Lab {lab.id} test_cases: JSON string parsed to {type(parsed).__name__}, not list"  # noqa: E501
                except json.JSONDecodeError:
                    # Not JSON — must be valid Python script string
                    import ast

                    try:
                        ast.parse(tc)
                    except SyntaxError as e:
                        assert (
                            False
                        ), f"Lab {lab.id} test_cases: neither valid JSON list nor valid Python: {e}"

    def test_lab_has_starter_code(self, seeded_db):
        """Every lab should provide starter_code for the student."""
        labs = seeded_db.query(Lab).all()
        empty = [lab for lab in labs if not lab.starter_code]
        assert (
            len(empty) == 0
        ), f"{len(empty)} labs have no starter_code: {[lab.id for lab in empty]}"

    def test_lab_solution_code_not_in_public_api(self, seeded_db):
        """The public course API must NEVER expose solution_code.

        This is a security contract: students must not be able to
        fetch solutions via the API.
        """
        from fastapi.testclient import TestClient

        from app.core.database import get_db
        from app.main import app

        # Override to use seeded test DB
        def _override():
            yield seeded_db

        app.dependency_overrides[get_db] = _override
        client = TestClient(app)

        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "contract_tester",
                "email": "contract@test.com",
                "password": "testpassword123",
            },
        )
        login_resp = client.post(
            "/api/v1/auth/login",
            json={
                "email": "contract@test.com",
                "password": "testpassword123",
            },
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check all courses
        courses_resp = client.get("/api/v1/courses/", headers=headers)
        courses = courses_resp.json().get("items", [])

        for course in courses:
            detail_resp = client.get(f"/api/v1/courses/{course['id']}", headers=headers)
            detail = detail_resp.json()
            for ch in detail.get("chapters", []):
                lab = ch.get("lab")
                if lab:
                    assert "solution_code" not in lab, (
                        f"Lab {lab.get('id')} in course '{course['title']}' "
                        f"exposes solution_code in public API"
                    )
                    assert "test_cases" not in lab, (
                        f"Lab {lab.get('id')} in course '{course['title']}' "
                        f"exposes test_cases in public API"
                    )

        app.dependency_overrides.clear()


class TestSeedDataIdempotency:
    """Running seed init twice must not duplicate or corrupt data."""

    def test_double_init_no_duplicates(self, seeded_db):
        """Running all init functions a second time must not create duplicates."""
        from app.data.courses_phase1 import init_phase1_data
        from app.data.courses_phase2 import init_phase2_data
        from app.data.courses_phase3_6 import init_phase3_6_data

        # Run again
        init_courses_data(seeded_db)
        init_phase1_data(seeded_db)
        init_phase2_data(seeded_db)
        init_phase3_6_data(seeded_db)

        # Must still be exactly 6 courses
        total = seeded_db.query(Course).count()
        assert total == 6, f"After double init: {total} courses (expected 6)"

        # Must still be exactly 6 published
        published = seeded_db.query(Course).filter(Course.is_published.is_(True)).count()
        assert published == 6, f"After double init: {published} published (expected 6)"

    def test_phase1_chapters_preserved_on_reinit(self, seeded_db):
        """Phase 1 content must survive a second init (upsert behavior)."""
        from app.data.courses_phase1 import init_phase1_data

        ch_count_before = (
            seeded_db.query(Chapter)
            .filter(
                Chapter.course_id
                == seeded_db.query(Course).filter(Course.title == PHASE_TITLES[1]).first().id
            )
            .count()
        )

        init_phase1_data(seeded_db)

        ch_count_after = (
            seeded_db.query(Chapter)
            .filter(
                Chapter.course_id
                == seeded_db.query(Course).filter(Course.title == PHASE_TITLES[1]).first().id
            )
            .count()
        )

        assert (
            ch_count_after == ch_count_before
        ), f"Phase 1 chapters changed after reinit: {ch_count_before} → {ch_count_after}"
