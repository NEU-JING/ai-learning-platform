"""
用户认证测试
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models import Base

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def setup_db():
    """每个测试前创建表，测试后删除"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAuth:
    """用户认证测试类"""

    def test_register_success(self, setup_db):
        """测试用户注册成功"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password_hash" not in data

    def test_register_duplicate_email(self, setup_db):
        """测试重复邮箱注册失败"""
        # 首次注册
        client.post(
            "/api/v1/auth/register",
            json={"username": "user1", "email": "test@example.com", "password": "password123"},
        )
        # 重复注册
        response = client.post(
            "/api/v1/auth/register",
            json={"username": "user2", "email": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 400
        assert "邮箱已注册" in response.json()["detail"]

    def test_login_success(self, setup_db):
        """测试登录成功"""
        # 先注册
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        # 登录
        response = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, setup_db):
        """测试密码错误"""
        # 先注册
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        # 错误密码登录
        response = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "邮箱或密码错误" in response.json()["detail"]

    def test_get_me_unauthorized(self, setup_db):
        """测试未授权访问"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_me_authorized(self, setup_db):
        """测试已授权访问用户信息"""
        # 注册
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        # 登录获取token
        login_response = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]

        # 访问用户信息
        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
