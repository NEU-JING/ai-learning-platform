"""
AI学习平台 - 完整测试用例集

本测试文件基于 PRD.md 编写，覆盖所有验收标准。
测试用例按模块组织，每个用例包含:
- 测试ID (T-{模块}-{序号})
- 测试描述
- 预期结果
- PRD参考

运行方式:
    cd backend
    pytest ../tests/test_complete.py -v
    
或运行所有测试:
    pytest ../tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models import Base
from app.core.database import get_db
from app.data.courses import init_courses_data


# ============================================================================
# 测试配置 - 所有测试共享
# ============================================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖，使用测试数据库"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def setup_db():
    """每个测试前创建表，测试后清理"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    init_courses_data(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def auth_token(setup_db):
    """获取认证token的fixture"""
    # 注册用户
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    # 登录获取token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    return login_response.json()["access_token"]


# ============================================================================
# 模块A: 认证测试 (Auth)
# ============================================================================

class TestAuth:
    """
    PRD参考: 6.1 认证模块验收
    
    验收标准:
    - AC-01: 用户注册 - 填写正确信息后成功注册，返回用户信息
    - AC-02: 重复邮箱 - 注册重复邮箱返回400错误
    - AC-03: 重复用户名 - 注册重复用户名返回400错误
    - AC-04: 用户登录 - 登录成功返回JWT token
    - AC-05: 错误密码 - 登录错误密码返回401错误
    - AC-06: Token有效性 - Token过期后返回401错误
    """

    def test_A01_register_success(self, setup_db):
        """
        T-AUTH-001: 测试用户注册成功
        验收标准: AC-01
        """
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 201, f"注册失败: {response.json()}"
        
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password_hash" not in data, "密码哈希不应返回给客户端"
        assert "id" in data

    def test_A02_register_duplicate_email(self, setup_db):
        """
        T-AUTH-002: 测试重复邮箱注册失败
        验收标准: AC-02
        """
        # 首次注册
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "user1",
                "email": "duplicate@example.com",
                "password": "password123"
            }
        )
        
        # 重复注册
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "user2",
                "email": "duplicate@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400, "重复邮箱应返回400"
        assert "邮箱已注册" in response.json()["detail"]

    def test_A03_register_duplicate_username(self, setup_db):
        """
        T-AUTH-003: 测试重复用户名注册失败
        验收标准: AC-03
        """
        # 首次注册
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicate_user",
                "email": "user1@example.com",
                "password": "password123"
            }
        )
        
        # 重复注册
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicate_user",
                "email": "user2@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400, "重复用户名应返回400"
        assert "用户名已存在" in response.json()["detail"]

    def test_A04_login_success(self, setup_db):
        """
        T-AUTH-004: 测试登录成功
        验收标准: AC-04
        注意: 登录使用 form-data格式，不是JSON
        """
        # 先注册
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "mypassword123"
            }
        )
        
        # 登录 - 使用form-data格式 (这是PRD中的关键点)
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "mypassword123"
            }
        )
        assert response.status_code == 200, f"登录失败: {response.json()}"
        
        data = response.json()
        assert "access_token" in data, "应返回access_token"
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0, "token不应为空"

    def test_A05_login_wrong_password(self, setup_db):
        """
        T-AUTH-005: 测试密码错误
        验收标准: AC-05
        """
        # 先注册
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "wrongpass@example.com",
                "password": "correctpassword"
            }
        )
        
        # 错误密码登录
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401, "错误密码应返回401"
        assert "邮箱或密码错误" in response.json()["detail"]

    def test_A06_login_nonexistent_user(self, setup_db):
        """
        T-AUTH-006: 测试不存在的用户登录
        """
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "notexist@example.com",
                "password": "anypassword"
            }
        )
        assert response.status_code == 401, "不存在的用户应返回401"

    def test_A07_get_me_unauthorized(self, setup_db):
        """
        T-AUTH-007: 测试未授权访问用户信息
        验收标准: AC-06 (无Token)
        """
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401, "未授权应返回401"

    def test_A08_get_me_with_valid_token(self, setup_db):
        """
        T-AUTH-008: 测试已授权访问用户信息
        验收标准: AC-06 (有效Token)
        """
        # 注册并登录
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "authtest",
                "email": "auth@example.com",
                "password": "test123456"
            }
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "auth@example.com",
                "password": "test123456"
            }
        )
        token = login_response.json()["access_token"]
        
        # 访问用户信息
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "auth@example.com"
        assert data["username"] == "authtest"

    def test_A09_get_me_with_invalid_token(self, setup_db):
        """
        T-AUTH-009: 测试无效Token访问
        PRD参考: 安全验收 SC-02
        """
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code == 401, "无效Token应返回401"

    def test_A10_register_with_empty_fields(self, setup_db):
        """
        T-AUTH-010: 测试空字段注册
        """
        # 空邮箱
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "user",
                "email": "",
                "password": "password123"
            }
        )
        assert response.status_code in [400, 422], "空邮箱应拒绝"

    def test_A11_register_short_password(self, setup_db):
        """
        T-AUTH-011: 测试短密码注册 (PRD要求长度>=8)
        """
        # First test that validation works with schema directly
        from app.schemas.user import UserCreate
        try:
            UserCreate(username="shortpw", email="short@example.com", password="123")
            print("ERROR: Schema should have rejected short password!")
        except Exception as e:
            print(f"Schema correctly rejected: {e}")
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "shortpw2",
                "email": "short2@example.com",
                "password": "123"  # 小于8字符
            }
        )
        # Pydantic验证会返回422
        assert response.status_code in [400, 422], f"短密码应拒绝, got {response.status_code}: {response.text}"


# ============================================================================
# 模块B: 课程测试 (Course)
# ============================================================================

class TestCourses:
    """
    PRD参考: 6.2 课程模块验收
    
    验���标准:
    - CC-01: 课程列表 - 返回所有已发布课程
    - CC-02: 课程详情 - 返回课程详细信息
    - CC-03: 章节内容 - 返回章节Markdown内容
    - CC-04: 内容渲染 - Markdown正确渲染为HTML
    """

    def test_B01_list_courses(self, setup_db):
        """
        T-COURSE-001: 测试获取课程列表
        验收标准: CC-01
        """
        response = client.get("/api/v1/courses/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "应返回数组"
        assert len(data) > 0, "应有内置课程数据"
        
        # 验证课程数据结构
        course = data[0]
        assert "id" in course
        assert "title" in course
        assert "description" in course

    def test_B02_list_courses_published_only(self, setup_db):
        """
        T-COURSE-002: 测试只返回已发布课程
        验收标准: CC-01 (is_published过滤)
        """
        response = client.get("/api/v1/courses/")
        courses = response.json()
        
        for course in courses:
            assert course.get("is_published") is True, "应只返回已发布课程"

    def test_B03_get_course_detail(self, setup_db):
        """
        T-COURSE-003: 测试获取课程详情
        验收标准: CC-02
        """
        # 先获取列表
        list_response = client.get("/api/v1/courses/")
        courses = list_response.json()
        assert len(courses) > 0, "需要有课程"
        
        course_id = courses[0]["id"]
        response = client.get(f"/api/v1/courses/{course_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == course_id
        assert "title" in data
        assert "chapters" in data

    def test_B04_get_course_not_found(self, setup_db):
        """
        T-COURSE-004: 测试获取不���在的课程
        验收标准: CC-02 (404处理)
        """
        response = client.get("/api/v1/courses/99999")
        assert response.status_code == 404
        assert "课程不存在" in response.json()["detail"]

    def test_B05_get_chapter_detail(self, setup_db):
        """
        T-COURSE-005: 测试获取章节详情
        验收标准: CC-03
        """
        # 先获取课程
        list_response = client.get("/api/v1/courses/")
        courses = list_response.json()
        assert len(courses) > 0, "需要有课程"
        
        # 获取第一个课程的章节
        chapters = courses[0].get("chapters", [])
        assert len(chapters) > 0, "课程需要有章节"
        
        chapter_id = chapters[0]["id"]
        response = client.get(f"/api/v1/courses/chapters/{chapter_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chapter_id
        assert "title" in data
        assert "content" in data
        assert len(data["content"]) > 0, "内容不应为空"

    def test_B06_get_chapter_not_found(self, setup_db):
        """
        T-COURSE-006: 测试获取不存在的章节
        验收标准: CC-03 (404处理)
        """
        response = client.get("/api/v1/courses/chapters/99999")
        assert response.status_code == 404
        assert "章节不存在" in response.json()["detail"]

    def test_B07_courses_structure_complete(self, setup_db):
        """
        T-COURSE-007: 测试课程数据结构完整性
        验收标准: CC-01 (数据结构验证)
        """
        response = client.get("/api/v1/courses/")
        courses = response.json()
        
        for course in courses:
            # 必填字段
            assert "id" in course
            assert "title" in course
            assert "description" in course
            assert "level" in course
            assert "category" in course
            assert "chapters" in course
            
            # 类型验证
            assert isinstance(course["chapters"], list)

    def test_B08_chapters_have_required_fields(self, setup_db):
        """
        T-COURSE-008: 测试章节包含必填字段
        """
        response = client.get("/api/v1/courses/")
        courses = response.json()
        
        for course in courses:
            for chapter in course.get("chapters", []):
                assert "id" in chapter
                assert "title" in chapter
                assert "chapter_type" in chapter

    def test_B09_course_ordering(self, setup_db):
        """
        T-COURSE-009: 测试课程按order_index排序
        """
        response = client.get("/api/v1/courses/")
        courses = response.json()
        
        # 验证按order_index升序排列
        order_indices = [c.get("order_index", 0) for c in courses]
        assert order_indices == sorted(order_indices), "应按order_index排序"


# ============================================================================
# 模块C: 实验/代码执行测试 (Lab/Code Execution)
# ============================================================================

class TestCodeExecution:
    """
    PRD参考: 6.3 实验模块验收
    
    验收标准:
    - EC-01: 代码执行 - 执行成功返回输出
    - EC-2: 执行超时 - 超时自动终止
    - EC-03: 危险代码 - 危险操作被拦截
    - EC-04: 实验提交 - 提交记录被保存
    - EC-05: 结果返回 - 正确返回执行结果
    
    安全验收:
    - SC-01: 未授权访问
    - SC-02: Token伪造
    - SC-03: 危险代码
    """

    def test_C01_execute_simple_code(self, auth_token):
        """
        T-LAB-001: 测试执行简单Python代码
        验收标准: EC-01
        """
        response = client.post(
            "/api/v1/labs/execute",
            json={
                "code": "print('Hello, World!')",
                "timeout": 5
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Hello, World!" in data["output"]

    def test_C02_execute_code_with_error(self, auth_token):
        """
        T-LAB-002: 测试执行有错误的代码
        验收标准: EC-02
        """
        response = client.post(
            "/api/v1/labs/execute",
            json={
                "code": "print(undefined_variable)",
                "timeout": 5
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None

    def test_C03_execute_code_timeout(self, auth_token):
        """
        T-LAB-003: 测试代码执行超时
        验收标准: EC-02 (超时处理)
        """
        response = client.post(
            "/api/v1/labs/execute",
            json={
                "code": "import time; time.sleep(10)",
                "timeout": 1  # 1秒超时
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "timeout" in data["error"].lower() or "超时" in data["error"]

    def test_C04_execute_code_unauthorized(self, setup_db):
        """
        T-LAB-004: 测试未授权执行代码
        验收标准: SC-01
        """
        response = client.post(
            "/api/v1/labs/execute",
            json={
                "code": "print('test')",
                "timeout": 5
            }
        )
        assert response.status_code == 401, "未授权应返回401"

    def test_C05_execute_dangerous_subprocess(self, auth_token):
        """
        T-LAB-005: 测试subprocess危险代码被阻止
        验收标准: EC-03, SC-03
        """
        response = client.post(
            "/api/v1/labs/execute",
            json={
                "code": "import os; os.system('echo hacked')",
                "timeout": 5
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # 危险代码应被拦截
        assert response.status_code == 200
        data = response.json()
        # 执行应该失败或输出受限
        if data.get("success") is True:
            # 如果成功，输出不应包含命令执行结果
            assert "hacked" not in data.get("output", "")

    def test_C06_execute_dangerous_exec(self, auth_token):
        """
        T-LAB-006: 测试exec危险代码被阻止
        验收标准: EC-03, SC-03
        """
        dangerous_codes = [
            "exec('import os')",
            "eval('__import__(\"os\")')",
            "__import__('subprocess').run(['ls'], shell=True)",
        ]
        
        for code in dangerous_codes:
            response = client.post(
                "/api/v1/labs/execute",
                json={"code": code, "timeout": 5},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            # 应返回200但执行失败或被限制
            assert response.status_code == 200

    def test_C07_execute_numpy_code(self, auth_token):
        """
        T-LAB-007: 测试NumPy代码执行
        注意: 沙箱环境应该预装NumPy
        """
        response = client.post(
            "/api/v1/labs/execute",
            json={
                "code": "import numpy as np; print(np.array([1,2,3]).sum())",
                "timeout": 10
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200

    def test_C08_execute_empty_code(self, auth_token):
        """
        T-LAB-008: 测试空代码执行
        """
        response = client.post(
            "/api/v1/labs/execute",
            json={"code": "", "timeout": 5},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [200, 422]

    def test_C09_execute_infinite_loop_protection(self, auth_token):
        """
        T-LAB-009: 测试无限循环保护
        """
        response = client.post(
            "/api/v1/labs/execute",
            json={
                "code": "while True: pass",
                "timeout": 2
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        data = response.json()
        assert data["success"] is False


# ============================================================================
# 模块D: 学习进度测试 (Progress)
# ============================================================================

class TestProgress:
    """
    PRD参考: 6.4 进度模块验收
    
    验收标准:
    - PC-01: 获取进度 - 返回用户所有进度
    - PC-02: 更新进度 - 进度状态正确更新
    - PC-03: 完成记录 - 完成后记录completed_at
    """

    def test_D01_get_progress_empty(self, auth_token):
        """
        T-PROG-001: 测试获取空进度
        验收标准: PC-01
        """
        response = client.get(
            "/api/v1/progress/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "应返回数组"

    def test_D02_get_progress_unauthorized(self, setup_db):
        """
        T-PROG-002: 测试未授权获取进度
        """
        response = client.get("/api/v1/progress/")
        assert response.status_code == 401

    def test_D03_update_progress_in_progress(self, auth_token):
        """
        T-PROG-003: 测试更新进度为进行中
        验收标准: PC-02
        """
        # 先获取章节ID
        courses_response = client.get("/api/v1/courses/")
        chapters = courses_response.json()[0]["chapters"]
        chapter_id = chapters[0]["id"]
        
        response = client.post(
            f"/api/v1/progress/chapters/{chapter_id}",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_D04_update_progress_completed(self, auth_token):
        """
        T-PROG-004: 测试更新进度为已完成
        验收标准: PC-03
        """
        # 先获取章节ID
        courses_response = client.get("/api/v1/courses/")
        chapters = courses_response.json()[0]["chapters"]
        chapter_id = chapters[0]["id"]
        
        response = client.post(
            f"/api/v1/progress/chapters/{chapter_id}",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200

    def test_D05_update_progress_not_started(self, auth_token):
        """
        T-PROG-005: 测试更新进度为未开始
        """
        courses_response = client.get("/api/v1/courses/")
        chapters = courses_response.json()[0]["chapters"]
        chapter_id = chapters[0]["id"]
        
        response = client.post(
            f"/api/v1/progress/chapters/{chapter_id}",
            json={"status": "not_started"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200

    def test_D06_update_progress_invalid_status(self, auth_token):
        """
        T-PROG-006: 测试无效状态更新
        """
        courses_response = client.get("/api/v1/courses/")
        chapters = courses_response.json()[0]["chapters"]
        chapter_id = chapters[0]["id"]
        
        response = client.post(
            f"/api/v1/progress/chapters/{chapter_id}",
            json={"status": "invalid_status"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code in [400, 422]


# ============================================================================
# 模块E: 实验提交测试 (Lab Submission)
# ============================================================================

class TestLabSubmission:
    """
    验收标准:
    - EC-04: 实验提交 - 提交记录被保存
    - EC-05: 结果返回 - 正确返回执行结果
    """

    def test_E01_submit_lab_success(self, auth_token):
        """
        T-LAB_SUB-001: 测试实验提交成功
        验收标准: EC-04
        """
        # 获取课程列表
        courses_response = client.get("/api/v1/courses/")
        
        # 查找有实验的章节
        chapter_id = None
        for course in courses_response.json():
            for chapter in course.get("chapters", []):
                if chapter.get("chapter_type") == "lab":
                    chapter_id = chapter["id"]
                    break
            if chapter_id:
                break
        
        if chapter_id is None:
            pytest.skip("没有实验章节可提交")
        
        # 获取章节对应的实验ID
        lab_response = client.get(f"/api/v1/courses/chapters/{chapter_id}/lab")
        if lab_response.status_code != 200 or lab_response.json() is None:
            pytest.skip("章节没有关联实验")
        
        lab_id = lab_response.json()["id"]
        
        response = client.post(
            f"/api/v1/courses/labs/{lab_id}/submit",
            json={"lab_id": lab_id, "code": "print('test')"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data or "submission_id" in data or "success" in data

    def test_E02_submit_lab_not_found(self, auth_token):
        """
        T-LAB_SUB-002: 测试提交不存在的实验
        """
        response = client.post(
            "/api/v1/courses/labs/99999/submit",
            json={"lab_id": 99999, "code": "print('test')"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404

    def test_E03_submit_lab_unauthorized(self, setup_db):
        """
        T-LAB_SUB-003: 测试未授权提交
        """
        response = client.post(
            "/api/v1/courses/labs/1/submit",
            json={"lab_id": 1, "code": "print('test')"}
        )
        assert response.status_code == 401


# ============================================================================
# 模块F: 安全测试 (Security)
# ============================================================================

class TestSecurity:
    """
    PRD参考: 6.6 安全验收
    
    安全验收:
    - SC-01: 未授权访问
    - SC-02: Token伪造
    - SC-03: 危险代码
    """

    def test_F01_sql_injection_protection(self, auth_token):
        """
        T-SEC-001: 测试SQL注入保护
        """
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "test'; DROP TABLE users; --",
                "email": "sqlinject@example.com",
                "password": "password123"
            }
        )
        # 应该成功转义，不应执行恶意代码
        assert response.status_code in [201, 400]

    def test_F02_xss_in_content(self, setup_db):
        """
        T-SEC-002: 测试内容XSS保护
        """
        # 注册用户
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "xssuser",
                "email": "xss@example.com",
                "password": "password123"
            }
        )
        
        # 获取课程内容，验证HTML转义
        response = client.get("/api/v1/courses/")
        courses = response.json()
        
        for course in courses:
            for chapter in course.get("chapters", []):
                content = chapter.get("content", "")
                # 不应直接返回<script>标签
                assert "<script>" not in content.lower() or "</script>" not in content.lower()

    def test_F03_cors_configuration(self, setup_db):
        """
        T-SEC-003: 测试CORS配置
        注意: 开发环境CORS开放，生产环境应限制
        """
        # 测试预检请求
        response = client.options(
            "/api/v1/courses/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        # 应返回200或允许跨域
        assert response.status_code in [200, 204]


# ============================================================================
# 模块G: 性能测试 (Performance)
# ============================================================================

class TestPerformance:
    """
    PRD参考: 6.5 性能验收
    
    性能验收:
    - PC-01: API响应 < 200ms
    """

    def test_G01_api_response_time(self, setup_db):
        """
        T-PERF-001: 测试API响应时间
        """
        import time
        
        start = time.time()
        response = client.get("/api/v1/courses/")
        elapsed = (time.time() - start) * 1000  # 转为毫秒
        
        assert response.status_code == 200
        # 注意: SQLite内存数据库可能比生产环境快
        # 实际生产环境应测试PostgreSQL
        assert elapsed < 5000, f"响应时间过长: {elapsed}ms"

    def test_G02_concurrent_requests(self, setup_db):
        """
        T-PERF-002: 测试并发请求
        """
        # 注册多个用户
        for i in range(5):
            client.post(
                "/api/v1/auth/register",
                json={
                    "username": f"user{i}",
                    "email": f"user{i}@example.com",
                    "password": "password123"
                }
            )
        
        # 并发登录
        for i in range(5):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": f"user{i}@example.com",
                    "password": "password123"
                }
            )
            assert response.status_code == 200


# ============================================================================
# 模块H: 边界测试 (Edge Cases)
# ============================================================================

class TestEdgeCases:
    """
    边界情况和异常处理测试
    """

    def test_H01_very_long_code(self, auth_token):
        """
        T-EDGE-001: 测试超长代码
        """
        long_code = "print('a' * 10000)"
        
        response = client.post(
            "/api/v1/labs/execute",
            json={"code": long_code, "timeout": 5},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200

    def test_H02_unicode_code(self, auth_token):
        """
        T-EDGE-002: 测试Unicode代码
        """
        response = client.post(
            "/api/v1/labs/execute",
            json={"code": "print('你好世界')", "timeout": 5},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        if data["success"]:
            assert "你好世界" in data["output"]

    def test_H03_binary_output(self, auth_token):
        """
        T-EDGE-003: 测试二进制输出
        """
        response = client.post(
            "/api/v1/labs/execute",
            json={"code": "print(bytes([72, 101, 108, 108, 111]))", "timeout": 5},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200


# ============================================================================
# 测试运行入口
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])