"""Shared test fixtures for the AI Learning Platform test suite."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.core.database import get_db
from app.main import app
from app.models import User, Course, Chapter, Lab, LearningProgress
from app.core.security import get_password_hash, create_access_token

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
    with patch("app.core.database.init_db"), \
         patch("app.core.database.SessionLocal", _TestSessionLocal), \
         patch("app.main.SessionLocal", _TestSessionLocal), \
         patch("app.main._assert_data_contract"):
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
