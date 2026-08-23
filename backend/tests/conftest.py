"""Shared test fixtures for the AI Learning Platform test suite."""

import os

# 标识测试库为 SQLite：AC12 并发测试按项目意图在 SQLite 下 skip（仅 PostgreSQL 保证并发一致性）
os.environ.setdefault("DATABASE_URL", "sqlite://")
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models import JobSkillRequirement  # noqa: F401 — T10: Gap analysis
from app.models import PathTemplate  # noqa: F401 — Ensure path tables are registered
from app.models import SkillDimension  # noqa: F401 — T6: Radar tables
from app.models import UserSkillSnapshot  # noqa: F401 — T9: Radar snapshots
from app.models import Base, Chapter, Course, Lab, User

# SDD: CI-only marker support — auto-skip locally, run only in CI
# Requires: pytest.ini with "ci_only" marker registered


def pytest_configure(config):
    config.addinivalue_line("markers", "ci_only: tests that require CI environment resources")


def pytest_collection_modifyitems(config, items):
    if os.environ.get("CI", "").lower() not in ("true", "1"):
        skip_ci_only = pytest.mark.skip(reason="CI-only test, skipped locally")
        for item in items:
            if "ci_only" in item.keywords:
                item.add_marker(skip_ci_only)


# End SDD: CI-only

# In-memory SQLite shared across all connections via StaticPool.
# Without StaticPool, each SQLite connection gets its own empty DB.
_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


@pytest.fixture(scope="function")
def test_db():
    """Fresh database per test function."""
    Base.metadata.create_all(bind=_test_engine)
    db = _TestSessionLocal()
    try:
        # Seed path templates for tests
        from app.data.path_templates import seed_all_path_data
        from app.data.skill_dimensions import seed_skill_dimensions

        seed_all_path_data(db)
        # T6: Seed skill dimensions
        seed_skill_dimensions(db)
        yield db
    finally:
        db.expire_all()  # Clear session identity map before drop
        db.close()
        Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture(scope="function")
def client(test_db):
    """TestClient with DB override + lifespan bypassed.

    - init_db patched to no-op (tables already created on test_engine)
    - SessionLocal patched so lifespan seeding uses test DB too
    - get_db overridden to yield the test session
    """

    def _override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    # Patch both database.SessionLocal AND the module-level imports in main.py
    # so lifespan seeding writes to the same test DB
    with (
        patch("app.core.database.init_db"),
        patch("app.core.database.SessionLocal", _TestSessionLocal),
        patch("app.main.SessionLocal", _TestSessionLocal),
        patch("app.main._assert_data_contract"),
        patch.dict(os.environ, {"DISABLE_DOCKER_SANDBOX": "1"}),
    ):
        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(test_db):
    """Create a test user directly in DB. Returns {user, token}."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        password_hash=get_password_hash("TestPass123"),
        role="student",
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    token = create_access_token(data={"sub": user.id})

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
        },
        "token": token,
    }


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Authorization headers for the test user."""
    return {"Authorization": f"Bearer {test_user['token']}"}


@pytest.fixture(scope="function")
def test_user_other(test_db):
    """Create another test user for cross-user authorization tests."""
    from datetime import datetime, timedelta

    from jose import jwt

    from app.core.config import settings

    user = User(
        email="other@example.com",
        username="otheruser",
        password_hash=get_password_hash("testpassword"),
        role="student",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Generate JWT token
    token = jwt.encode(
        {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(minutes=30),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "token": token,
    }


@pytest.fixture(scope="function")
def auth_headers_other(test_user_other):
    """Authorization headers for the other test user."""
    return {"Authorization": f"Bearer {test_user_other['token']}"}


@pytest.fixture(scope="function")
def test_course(test_db):
    """Create a course + chapter + lab for testing."""
    course = Course(
        title="Python for AI",
        description="Learn Python basics",
        level="beginner",
        category="python",
        duration_hours=14,
        is_published=True,
        order_index=1,
    )
    test_db.add(course)
    test_db.flush()

    chapter = Chapter(
        course_id=course.id,
        title="Hello World",
        content="# Hello World\n\nPrint your first line of code.",
        order_index=1,
        chapter_type="lab",
        duration_minutes=30,
    )
    test_db.add(chapter)
    test_db.flush()

    lab = Lab(
        chapter_id=chapter.id,
        title="Hello World Lab",
        description="Write a hello world function",
        starter_code="# Write your code here\n",
        solution_code='def hello():\n    return "hello world"',
        test_cases=[
            {
                "name": "test_hello",
                "type": "output_match",
                "function": "hello",
                "args": [],
                "expected": "hello world",
            },
        ],
        hints=["Use def to define a function", "Use return to return a value"],
        time_limit_seconds=30,
        memory_limit_mb=256,
    )
    test_db.add(lab)
    test_db.commit()
    test_db.refresh(course)
    test_db.refresh(chapter)
    test_db.refresh(lab)

    return {"course": course, "chapter": chapter, "lab": lab}


@pytest.fixture(scope="function")
def test_lab(test_course):
    """Shorthand fixture that returns the lab portion of test_course."""
    return {
        "course": test_course["course"],
        "chapter": test_course["chapter"],
        "lab": test_course["lab"],
    }
