"""Debug CI failure - replicate test_auth + test_certification + test_code_review sequence."""

import os
from unittest.mock import AsyncMock, patch

os.environ["DATABASE_URL"] = "sqlite:///./test_ci_debug.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-ci-at-least-32-characters-long"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["DISABLE_DOCKER_SANDBOX"] = "1"

# Force complete reimport
import sys

# Remove cached modules
for mod in list(sys.modules.keys()):
    if "app" in mod and "app.main" in mod:
        del sys.modules[mod]

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models import User
from app.services.llm_router import LLMRouter

# Setup fresh engine
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed data
from app.data.path_templates import seed_all_path_data
from app.data.skill_dimensions import seed_skill_dimensions

db = TestSessionLocal()
try:
    seed_all_path_data(db)
    seed_skill_dimensions(db)
    db.commit()

    # Create user
    user = User(
        email="testuser@example.com",
        username="testuser",
        password_hash=get_password_hash("TestPass123"),
        role="student",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.id})
    headers = {"Authorization": f"Bearer {token}"}

    # Override dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with (
        patch("app.core.database.init_db"),
        patch("app.core.database.SessionLocal"),
        patch("app.main.SessionLocal"),
        patch("app.main._assert_data_contract"),
        patch.object(LLMRouter, "chat", new_callable=AsyncMock) as mock_llm,
    ):

        mock_llm.return_value = {
            "content": '{"issues": [], "dimensions": {"correctness": 80, "efficiency": 75, "readability": 70, "style": 60, "best_practices": 75}, "overall_score": 72.0, "summary": "Mock review"}',
            "model": "mock",
            "tokens": 10,
            "provider": "mock",
        }

        with TestClient(app) as c:
            # Step 1: Test L1 Certification Apply (as test_certification.py would)
            print("=== 1. L1 Certification Apply ===")
            r1 = c.post(
                "/api/v1/certifications/apply",
                json={"level_id": 1},
                headers=headers,
            )
            print(f"Status: {r1.status_code}")
            if r1.status_code != 200:
                print(f"Body: {r1.text[:500]}")
            else:
                data = r1.json()
                print(f"OK: level={data.get('level_id')}, status={data.get('status')}")

            # Step 2: Test Code Review
            print("\n=== 2. Code Review ===")
            r2 = c.post(
                "/api/v1/tutor/code-review",
                json={
                    "lab_id": 1,
                    "code_content": "def add(a, b):\n    return a + b",
                    "language": "python",
                },
                headers=headers,
            )
            print(f"Status: {r2.status_code}")
            if r2.status_code != 200:
                print(f"Body: {r2.text[:2000]}")
            else:
                data = r2.json()
                print(f"OK: review_id={data.get('review_id')}, score={data.get('overall_score')}")

finally:
    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)
    print("\nDone")
