# Agent Development PRD — AI Learning Platform

> Version: 1.0 | Date: 2026-05-13
> Purpose: 指导AI Agent完成编码任务，每个功能点有精确的输入/输出/验收标准
> 遵循: DEVELOPMENT_HARNESS.md 中定义的全流程规范

---

## 0. Agent开发须知

**在开始任何编码任务前，必须阅读**：
1. `DEVELOPMENT_HARNESS.md` — 分支策略、commit规范、测试要求、代码风格
2. `AGENTS.md` — 项目架构、已知quirks、API端点
3. 本文档 — 具体要做什么、验收标准、依赖关系

**开发纪律**：
- 一个任务一个分支 `feature/TASK-{id}-{desc}`
- 代码必须通过 black + flake8
- 新代码必须有测试，当前阶段覆盖率门禁 ≥40%
- 数据库变更必须有 Alembic 迁移（upgrade + downgrade）
- commit格式: `feat(api): add xxx` / `fix(sandbox): handle xxx`

---

## 1. 当前代码现状（Agent必须了解的事实）

| 事实 | 影响 |
|------|------|
| 所有ORM模型在 `models/__init__.py` 单文件（155行） | 新增模型在该文件追加，后续重构为独立文件 |
| Service层用静态方法类模式 `class UserService:` | 新Service遵循相同模式 |
| 登录端点接受JSON（非标准OAuth2PasswordRequestForm） | 测试时用JSON发送login请求 |
| 无Alembic，用 `init_db()` 在startup时create_all | 新表定义后需在init_db中注册 |
| 测试无conftest.py，每个文件自建SQLite内存库 | **必须创建conftest.py**，新测试共享fixtures |
| API路径当前是 `/api/auth/*`，不是 `/api/v1/auth/*` | O3任务会改版，在此之前用现有路径 |
| 前端是Vanilla HTML/JS，无构建步骤 | 前端改动直接编辑HTML/JS文件 |

---

## 2. 任务清单（按优先级排序）

### TASK-001: 安全漏洞修复（P0）

> 来源: TASKS.md O1，状态=进行中但子任务全未完成

**TASK-001-1: JWT Secret Key 环境变量化**

- **文件**: `backend/app/core/config.py`
- **当前**: SECRET_KEY 有硬编码默认值
- **目标**: 生产环境必须通过环境变量注入，无默认值则启动报错
- **实现**:
  ```python
  # config.py 中
  SECRET_KEY: str  # 移除默认值，pydantic-settings会在缺少时抛ValidationError
  
  # 新增校验：如果DEBUG=False且SECRET_KEY为空，抛出明确错误
  @model_validator(mode='after')
  def validate_production_config(self):
      if not self.DEBUG and (not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-here"):
          raise ValueError("SECRET_KEY must be set in production")
      return self
  ```
- **测试**:
  - `test_config_missing_secret_key_in_prod_raises_error`: 设置DEBUG=False, SECRET_KEY=""，断言ValidationError
  - `test_config_default_secret_key_in_dev_ok`: 设置DEBUG=True，断言不报错
- **验收标准**:
  - [ ] 生产环境启动时，SECRET_KEY未设置则启动失败
  - [ ] 开发环境有合理的默认值或从.env读取
  - [ ] .env.example 已更新，标注SECRET_KEY为必填

**TASK-001-2: CORS 生产环境限制**

- **文件**: `backend/app/main.py`
- **当前**: `allow_origins=["*"]`
- **目标**: 生产环境只允许配置的域名
- **实现**:
  ```python
  # config.py 新增
  CORS_ORIGINS: str = "*"  # 逗号分隔的域名列表
  
  # main.py 修改
  allow_origins=settings.CORS_ORIGINS.split(","),
  ```
- **测试**:
  - `test_cors_wildcard_in_dev`: DEBUG=True时CORS允许*
  - `test_cors_restricted_in_prod`: DEBUG=False时CORS只允许配置域名
- **验收标准**:
  - [ ] 生产环境CORS不允许`*`
  - [ ] 可通过CORS_ORIGINS环境变量配置允许的域名
  - [ ] .env.example 已更新

**TASK-001-3: 密码强度验证**

- **文件**: `backend/app/schemas/user.py`
- **当前**: 仅校验长度≥8
- **目标**: 必须包含字母+数字，长度8-128
- **实现**:
  ```python
  # schemas/user.py
  password: str = Field(
      ..., min_length=8, max_length=128,
      pattern=r"^(?=.*[A-Za-z])(?=.*\d).+$",
      description="Password must contain both letters and numbers"
  )
  ```
- **测试**:
  - `test_register_password_no_number_fails`: 纯字母密码→422
  - `test_register_password_no_letter_fails`: 纯数字密码→422
  - `test_register_password_valid_succeeds`: 字母+数字→200
  - `test_register_password_too_short_fails`: 7位→422
- **验收标准**:
  - [ ] 密码必须同时包含字母和数字
  - [ ] 长度8-128
  - [ ] 错误消息清晰说明规则

**TASK-001-4: 强化沙箱安全检测**

- **文件**: `backend/app/core/code_security.py`
- **当前**: 已有基础黑名单
- **目标**: 增加以下检测模式
- **新增检测**:
  ```python
  # 新增危险模式
  DANGEROUS_PATTERNS = [
      # 现有的...
      # 新增：
      r"__import__\s*\(",           # 动态import
      r"importlib",                 # importlib模块
      r"sys\.(modules|path)",       # sys模块操作
      r"os\.environ",               # 环境变量读取
      r"subprocess",                # 已有，确保覆盖所有变体
      r"pickle\.loads?",            # 反序列化
      r"marshal\.loads?",           # marshal反序列化
      r"ctypes",                    # FFI调用
      r"socket\b",                  # 网络socket
      r"http\.(client|server)",     # HTTP客户端/服务端
      r"urllib",                    # URL请求
      r"requests\b",                # requests库
      r"pathlib",                   # 文件路径操作
      r"shutil",                    # 文件操作
      r"tempfile",                  # 临时文件
  ]
  ```
- **测试**:
  - 对每个新增pattern编写测试：`test_block_importlib`, `test_block_pickle_loads` 等
  - `test_bypass_attempt_with_string_concat`: `__imp` + `ort__('os')` 应被检测
  - `test_bypass_attempt_with_eval`: `eval('__im'+'port__("os")')` 应被检测
- **验收标准**:
  - [ ] 新增pattern全部有对应测试
  - [ ] 已知的绕过手段被覆盖
  - [ ] 合法代码（如 `import math`）不被误拦截

---

### TASK-002: 核心功能补全（P0）

> 来源: TASKS.md O2

**TASK-002-1: 学习进度持久化前端实现**

- **文件**: `frontend/js/progress.js`, `frontend/chapter.html`
- **当前**: 前端无进度保存逻辑
- **目标**: 自动保存阅读进度，标记完成状态
- **实现**:
  ```javascript
  // progress.js
  class ProgressManager {
      constructor() {
          this.apiBase = '/api';
          this.token = localStorage.getItem('token');
      }
      
      // 进入章节时调用：标记为in_progress
      async markInProgress(chapterId) { ... }
      
      // 滚动到底部或点击"完成"按钮：标记为completed
      async markCompleted(chapterId) { ... }
      
      // 加载章节时：恢复进度状态，滚动到上次位置
      async loadProgress(chapterId) { ... }
  }
  ```
- **验收标准**:
  - [ ] 打开章节自动标记in_progress
  - [ ] 滚动到80%以上自动标记completed（可配置阈值）
  - [ ] 重新打开章节恢复到上次阅读位置
  - [ ] 章节列表页显示完成状态（✓/进行中/未开始）

**TASK-002-2: 实验自动评测系统**

- **文件**: `backend/app/services/grader.py`（已存在，需扩展）
- **当前**: grader.py有基础结构，但不完整
- **目标**: 支持两种评测模式
- **评测模式一：输出对比**
  ```python
  # lab.test_cases 中定义期望输出
  # 执行学生代码，对比stdout
  # 支持模糊匹配（忽略空白、浮点精度）
  ```
- **评测模式二：单元测试**
  ```python
  # lab.test_cases 中定义pytest表达式
  # 在沙箱中运行 pytest，收集结果
  # 返回 pass/fail + 错误信息
  ```
- **API变更**:
  ```
  POST /api/labs/{lab_id}/submit
  Request: { "code": "..." }
  Response: {
      "submission_id": 1,
      "status": "success" | "failed" | "error",
      "output": "...",
      "test_results": [
          { "name": "test_add", "passed": true },
          { "name": "test_subtract", "passed": false, "message": "..." }
      ],
      "score": 80  // 百分比
  }
  ```
- **测试**:
  - `test_grader_output_match`: 输出完全匹配→pass
  - `test_grader_output_fuzzy`: 忽略空白→pass
  - `test_grader_unit_test`: pytest表达式执行→pass/fail
  - `test_grader_partial_score`: 部分通过→score=66
- **验收标准**:
  - [ ] 提交代码后返回评测结果
  - [ ] 支持输出对比和单元测试两种模式
  - [ ] 返回分数（百分比）
  - [ ] Lab模型的test_cases字段格式有文档说明

**TASK-002-3: 实验提交历史**

- **文件**: `backend/app/api/v1/labs.py`
- **当前**: 只能提交，不能查看历史
- **目标**: 可查看提交记录列表和代码对比
- **API变更**:
  ```
  GET /api/labs/{lab_id}/submissions
  Response: [
      { "id": 1, "code": "...", "status": "success", "score": 80, "created_at": "..." },
      { "id": 2, "code": "...", "status": "failed", "score": 40, "created_at": "..." }
  ]
  ```
- **测试**:
  - `test_list_submissions`: 提交2次→列表返回2条
  - `test_submissions_only_own`: 用户A看不到用户B的提交
  - `test_submissions_ordered_by_time`: 最新提交排前面
- **验收标准**:
  - [ ] 可查看某实验的所有提交记录
  - [ ] 只能看到自己的提交
  - [ ] 按时间倒序排列

---

### TASK-003: 测试基础设施（P0 — 阻塞其他所有测试）

**TASK-003-1: 创建 conftest.py + 共享fixtures**

- **文件**: `tests/conftest.py`
- **目标**: 所有测试共享以下fixtures
- **实现**:
  ```python
  import pytest
  from fastapi.testclient import TestClient
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker
  from sqlalchemy.pool import StaticPool
  
  from app.core.database import Base, get_db
  from app.main import app
  
  SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
  
  @pytest.fixture(scope="function")
  def db_engine():
      engine = create_engine(
          SQLALCHEMY_DATABASE_URL,
          connect_args={"check_same_thread": False},
          poolclass=StaticPool,
      )
      Base.metadata.create_all(bind=engine)
      yield engine
      Base.metadata.drop_all(bind=engine)
  
  @pytest.fixture(scope="function")
  def db_session(db_engine):
      TestingSessionLocal = sessionmaker(bind=db_engine)
      session = TestingSessionLocal()
      yield session
      session.close()
  
  @pytest.fixture(scope="function")
  def client(db_session):
      def override_get_db():
          yield db_session
      app.dependency_overrides[get_db] = override_get_db
      with TestClient(app) as c:
          yield c
      app.dependency_overrides.clear()
  
  @pytest.fixture(scope="function")
  def test_user(client):
      response = client.post("/api/auth/register", json={
          "email": "test@example.com",
          "username": "testuser",
          "password": "Test1234"
      })
      return response.json()
  
  @pytest.fixture(scope="function")
  def auth_headers(client, test_user):
      response = client.post("/api/auth/login", json={
          "email": "test@example.com",
          "password": "Test1234"
      })
      token = response.json()["access_token"]
      return {"Authorization": f"Bearer {token}"}
  ```
- **验收标准**:
  - [ ] conftest.py创建完成
  - [ ] 现有4个测试文件可使用共享fixtures（无需重复定义）
  - [ ] `pytest tests/ -v` 全部通过

**TASK-003-2: 迁移现有测试使用conftest fixtures**

- **文件**: `tests/test_auth.py`, `tests/test_courses.py`, `tests/test_code_execution.py`, `tests/test_complete.py`
- **目标**: 删除各文件中重复的db/client/用户创建逻辑，改用conftest fixtures
- **验收标准**:
  - [ ] 无重复的fixture定义
  - [ ] 所有测试通过
  - [ ] 测试文件代码量减少>30%

---

### TASK-004: API完善（P1）

**TASK-004-1: 列表接口分页**

- **文件**: `backend/app/api/v1/courses.py`（及其他列表接口）
- **当前**: 返回全部数据
- **目标**: 支持 `?page=1&limit=20` 分页
- **实现**:
  ```python
  # schemas/pagination.py (新建)
  class PaginationParams(BaseModel):
      page: int = Field(default=1, ge=1)
      limit: int = Field(default=20, ge=1, le=100)
  
  class PaginatedResponse(BaseModel, Generic[T]):
      items: list[T]
      total: int
      page: int
      limit: int
      pages: int  # ceil(total/limit)
  
  # courses.py 修改
  @router.get("/courses")
  def list_courses(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
      total = db.query(func.count(Course.id)).scalar()
      courses = db.query(Course).offset((page-1)*limit).limit(limit).all()
      return {"items": courses, "total": total, "page": page, "limit": limit, "pages": (total+limit-1)//limit}
  ```
- **测试**:
  - `test_courses_pagination_default`: 不传参数→返回第1页20条
  - `test_courses_pagination_page2`: page=2→返回正确的偏移数据
  - `test_courses_pagination_limit`: limit=5→返回5条
  - `test_courses_pagination_invalid_page`: page=0→422
  - `test_courses_pagination_invalid_limit`: limit=0→422
- **验收标准**:
  - [ ] 课程列表支持分页
  - [ ] 讨论列表支持分页
  - [ ] 返回total/pages元数据

**TASK-004-2: 为所有端点添加响应模型**

- **文件**: `backend/app/api/v1/*.py`
- **当前**: 部分端点缺 `response_model`
- **目标**: 所有端点有明确的response_model
- **验收标准**:
  - [ ] `GET /docs` 显示所有端点的响应Schema
  - [ ] 响应格式与response_model一致

**TASK-004-3: 更新 API.md**

- **文件**: `API.md`
- **目标**: 文档与实现一致
- **验收标准**:
  - [ ] 每个端点的请求/响应格式已更新
  - [ ] 新增端点（讨论区、证书等）已记录

---

### TASK-005: 前端体验优化（P1）

**TASK-005-1: Toast通知系统**

- **文件**: `frontend/js/app.js`, `frontend/css/style.css`
- **实现**:
  ```javascript
  // 全局Toast函数
  function showToast(message, type = 'info', duration = 3000) {
      // type: success | error | warning | info
      // 自动3秒后消失，error类型需手动关闭
  }
  ```
- **验收标准**:
  - [ ] 登录成功→green toast
  - [ ] 登录失败→red toast
  - [ ] 代码执行成功→green toast
  - [ ] 代码执行失败→red toast
  - [ ] Toast不遮挡关键操作区域

**TASK-005-2: 全局Loading指示器**

- **文件**: `frontend/js/app.js`
- **验收标准**:
  - [ ] API请求时显示loading
  - [ ] 请求完成（成功或失败）隐藏loading
  - [ ] 超过3秒的请求显示"加载较慢"提示

**TASK-005-3: 错误重试机制**

- **文件**: `frontend/js/api.js`（新建或从app.js抽离）
- **验收标准**:
  - [ ] 网络错误自动重试3次，间隔1s/2s/4s
  - [ ] 重试期间显示"重试中..."
  - [ ] 3次后仍失败显示"网络异常，请稍后重试"

**TASK-005-4: 面包屑导航**

- **文件**: `frontend/course.html`, `frontend/chapter.html`
- **验收标准**:
  - [ ] 课程详情页：首页 > 课程名
  - [ ] 章节页：首页 > 课程名 > 章节名
  - [ ] 每级可点击跳转

**TASK-005-5: 移动端响应式**

- **文件**: `frontend/css/style.css`
- **验收标准**:
  - [ ] 375px宽度下课程列表正常显示
  - [ ] 代码编辑区在手机上可操作（Monaco Editor降级为textarea）
  - [ ] 导航栏在手机上折叠为汉堡菜单

---

### TASK-006: 性能优化（P1）

**TASK-006-1: Redis缓存课程数据**

- **文件**: `backend/app/services/course_service.py`
- **目标**: 课程列表和详情走Redis缓存
- **实现**:
  ```python
  class CourseService:
      CACHE_PREFIX = "course"
      CACHE_TTL = 300  # 5分钟
      
      @staticmethod
      def get_courses(db: Session, redis_client: Redis) -> list[Course]:
          cache_key = f"{CourseService.CACHE_PREFIX}:list"
          cached = redis_client.get(cache_key)
          if cached:
              return json.loads(cached)
          courses = db.query(Course).filter(Course.is_published).order_by(Course.order_index).all()
          redis_client.setex(cache_key, CourseService.CACHE_TTL, json.dumps([c.to_dict() for c in courses]))
          return courses
      
      @staticmethod
      def invalidate_cache(redis_client: Redis):
          # 课程变更时调用
          for key in redis_client.scan_iter(f"{CourseService.CACHE_PREFIX}:*"):
              redis_client.delete(key)
  ```
- **测试**:
  - `test_courses_cached_on_first_request`: 第1次查数据库，第2次命中缓存
  - `test_cache_invalidated_on_update`: 更新课程后缓存失效
- **验收标准**:
  - [ ] 课程列表走缓存
  - [ ] 课程详情走缓存
  - [ ] 数据变更时缓存失效

**TASK-006-2: Docker多阶段构建**

- **文件**: `backend/Dockerfile`
- **目标**: 减小镜像体积
- **验收标准**:
  - [ ] 镜像体积减少>40%
  - [ ] 构建时间减少>30%
  - [ ] 运行功能不受影响

---

### TASK-007: 证书与统计（P2）

**TASK-007-1: 学习统计API**

- **文件**: `backend/app/api/v1/stats.py`（新建）
- **API**:
  ```
  GET /api/v1/stats/me
  Auth: Required
  Response: {
      "total_study_days": 15,
      "consecutive_days": 3,
      "completed_chapters": 20,
      "total_chapters": 98,
      "completed_labs": 8,
      "total_labs": 15,
      "study_hours_this_week": 5.2
  }
  ```
- **测试**:
  - `test_stats_own_data`: 返回自己的统计数据
  - `test_stats_unauthenticated`: 未认证→401
  - `test_stats_consecutive_days`: 连续3天学习→consecutive_days=3
- **验收标准**:
  - [ ] API可用
  - [ ] 统计数据准确

**TASK-007-2: 证书生成**

- **文件**: `backend/app/services/certificate.py`（已存在，需完善）
- **目标**: 完成课程后生成PDF证书
- **实现**: 使用reportlab或weasyprint
- **API**:
  ```
  POST /api/v1/certificates/generate
  Body: { "course_id": 1 }
  Response: PDF文件下载
  
  GET /api/v1/certificates
  Response: [{ "id": 1, "course_title": "...", "issued_at": "..." }]
  ```
- **验收标准**:
  - [ ] 完成课程所有章节+实验后可申请证书
  - [ ] 证书包含：用户名、课程名、完成日期、平台签名
  - [ ] 未完成课程不能申请

---

### TASK-008: 开发基础设施（P0 — 优先级最高）

**TASK-008-1: pyproject.toml 配置**

- **文件**: `pyproject.toml`（新建）
- **内容**: black/isort/flake8/mypy/pytest完整配置（见DEVELOPMENT_HARNESS.md §4.3）
- **验收标准**:
  - [ ] `black --check backend/` 通过
  - [ ] `flake8 backend/` 通过
  - [ ] `mypy backend/app/` 通过

**TASK-008-2: pre-commit hooks**

- **文件**: `.pre-commit-config.yaml`（新建）
- **内容**: 见DEVELOPMENT_HARNESS.md §4.4
- **验收标准**:
  - [ ] `pre-commit run --all-files` 通过
  - [ ] git commit自动触发检查

**TASK-008-3: Alembic初始化**

- **文件**: `backend/alembic/`（新建）
- **步骤**:
  1. `cd backend && alembic init alembic`
  2. 编辑 `alembic/env.py`：导入Base.metadata，配置database_url
  3. `alembic revision --autogenerate -m "initial schema"` — 基于现有模型生成初始迁移
  4. 验证 `alembic upgrade head` + `alembic downgrade base` 可正常执行
- **验收标准**:
  - [ ] `alembic upgrade head` 创建所有表
  - [ ] `alembic downgrade base` 删除所有表
  - [ ] `init_db()` 保留为开发环境便利方法，但生产环境应使用alembic

**TASK-008-4: CI流水线**

- **文件**: `.github/workflows/ci.yml`（新建）
- **内容**: 见DEVELOPMENT_HARNESS.md §8.1
- **验收标准**:
  - [ ] push到develop/main触发CI
  - [ ] PR触发CI
  - [ ] lint + test全部通过

---

### TASK-009: 内容管理后台（P3）

> 低优先级，仅列出需求，不展开实现细节

- 管理员认证（区分admin角色）
- 课程CRUD
- 章节CRUD（Markdown编辑器）
- 实验测试用例管理
- 用户管理（列表/禁用/角色变更）

---

### TASK-010: 智能推荐（P3）

> 低优先级，仅列出需求

- 基于学习进度的课程推荐
- 基于实验表现的练习推荐
- 学习路径个性化

---

## 3. 任务依赖关系

```
TASK-008 (基础设施) ──── 无依赖，最先做
    │
    ├── TASK-003 (测试基础) ── 依赖 TASK-008-1 (pyproject.toml)
    │       │
    │       ├── TASK-001 (安全修复) ── 依赖 TASK-003-1 (conftest.py)
    │       ├── TASK-002 (核心功能) ── 依赖 TASK-003-1
    │       └── TASK-004 (API完善)  ── 依赖 TASK-003-1
    │
    ├── TASK-005 (前端优化) ── 无测试依赖，可并行
    │
    ├── TASK-006 (性能优化) ── 依赖 TASK-001-2 (CORS修复后再测缓存)
    │
    └── TASK-007 (证书统计) ── 依赖 TASK-002 (核心功能完成后)

TASK-009, TASK-010 ── 无前置依赖，按业务优先级排期
```

**推荐执行顺序**:

```
第一批（基础设施，1-2天）:
  TASK-008-1 → TASK-008-2 → TASK-008-3 → TASK-003-1 → TASK-003-2

第二批（安全+核心，3-5天）:
  TASK-001-1 → TASK-001-2 → TASK-001-3 → TASK-001-4
  TASK-002-1 → TASK-002-2 → TASK-002-3  （可与TASK-001并行）

第三批（API+前端，3-5天）:
  TASK-004-1 → TASK-004-2 → TASK-004-3
  TASK-005-1 → TASK-005-2 → TASK-005-3 → TASK-005-4 → TASK-005-5

第四批（性能+证书，3-5天）:
  TASK-006-1 → TASK-006-2
  TASK-007-1 → TASK-007-2

第五批（CI/CD，1天）:
  TASK-008-4
```

---

## 4. 数据模型变更汇总

### 新增表

无。现有模型已覆盖所有功能需求。

### 新增字段

| 表 | 字段 | 类型 | 说明 | 对应任务 |
|----|------|------|------|---------|
| labs | `test_cases` | JSON | 扩展test_cases格式，支持output_match和unit_test两种模式 | TASK-002-2 |
| users | 无变更 | — | — | — |

### test_cases JSON格式规范

```json
{
  "type": "output_match",  // 或 "unit_test"
  "cases": [
    // output_match模式
    {
      "input": "",           // stdin（可选）
      "expected_output": "Hello World",
      "fuzzy_match": false   // 是否忽略空白
    },
    // unit_test模式
    {
      "test_code": "assert add(1,2) == 3",
      "name": "test_add"
    }
  ],
  "passing_score": 100      // 及格分数（百分比）
}
```

---

## 5. 环境变量清单

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `SECRET_KEY` | 生产必填 | — | JWT签名密钥 |
| `DATABASE_URL` | 否 | sqlite:///./app.db | 数据库连接 |
| `REDIS_URL` | 否 | redis://localhost:6379 | Redis连接 |
| `CORS_ORIGINS` | 否 | `*` | 允许的CORS域名（逗号分隔） |
| `DEBUG` | 否 | `true` | 调试模式 |
| `SANDBOX_IMAGE_NAME` | 否 | ai-learning-sandbox | 沙箱Docker镜像 |
| `DB_POOL_SIZE` | 否 | 5 | 连接池大小 |
| `DB_MAX_OVERFLOW` | 否 | 10 | 连接池溢出 |

---

## 6. 现有API端点速查

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | /api/auth/register | No | 注册 |
| POST | /api/auth/login | No | 登录（JSON格式） |
| GET | /api/auth/me | Yes | 当前用户 |
| GET | /api/courses | No | 课程列表 |
| GET | /api/courses/{id} | No | 课程详情 |
| GET | /api/courses/{id}/chapters | No | 章节列表 |
| POST | /api/code/execute | Yes | 执行代码 |
| POST | /api/labs/{id}/submit | Yes | 提交实验 |
| GET | /api/progress | Yes | 学习进度 |
| POST | /api/progress/{chapter_id} | Yes | 更新进度 |
| GET | /api/courses/{id}/discussions | No | 讨论列表 |
| POST | /api/courses/{id}/discussions | Yes | 创建讨论 |
| GET | /api/discussions/{id} | No | 讨论详情 |
| POST | /api/discussions/{id}/comments | Yes | 评论 |
| POST | /api/discussions/{id}/like | Yes | 点赞 |

---

*本文档随任务完成持续更新。Agent完成某个TASK后，更新对应验收标准的checkbox。*
