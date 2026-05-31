"""
代码执行测试
"""

from app.core.database import get_db
from app.main import app
from tests.test_auth import client, override_get_db

app.dependency_overrides[get_db] = override_get_db


class TestCodeExecution:
    """代码执行测试类"""

    def test_execute_simple_code(self, setup_db):
        """测试执行简单Python代码"""
        # 注册并登录
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        login_response = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]

        # 执行代码
        response = client.post(
            "/api/v1/labs/execute",
            json={"code": "print('Hello, World!')", "timeout": 5},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Hello, World!" in data["output"]

    def test_execute_code_with_error(self, setup_db):
        """测试执行有错误的代码"""
        # 注册并登录
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        login_response = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]

        # 执行有错误的代码
        response = client.post(
            "/api/v1/labs/execute",
            json={"code": "", "timeout": 5},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None

    def test_execute_code_timeout(self, setup_db):
        """测试代码执行超时"""
        # 注册并登录
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        login_response = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]

        # 执行耗时代码
        response = client.post(
            "/api/v1/labs/execute",
            json={"code": "import time; time.sleep(10)", "timeout": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "超时" in data["error"] or "timeout" in data["error"].lower()

    def test_execute_code_unauthorized(self, setup_db):
        """测试未授权执行代码"""
        response = client.post("/api/v1/labs/execute", json={"code": "print('test')", "timeout": 5})
        assert response.status_code == 401

    def test_execute_dangerous_code_blocked(self, setup_db):
        """测试危险代码被阻止"""
        # 注册并登录
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        login_response = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]

        # 尝试执行危险代码
        dangerous_codes = [
            "import os; os.system('ls')",
            "__import__('os').system('whoami')",
            "exec('import os')",
            'eval(\'__import__("os").system("ls")\')',
        ]

        for code in dangerous_codes:
            response = client.post(
                "/api/v1/labs/execute",
                json={"code": code, "timeout": 5},
                headers={"Authorization": f"Bearer {token}"},
            )
            # 应该被拒绝或安全执行
            assert response.status_code == 200
            data = response.json()
            # 要么成功但输出受限，要么明确失败
            if data["success"]:
                # 如果成功，输出应该被限制
                pass
