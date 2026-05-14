# AI Learning Platform — Development Harness Specification

> Version: 1.0
> Date: 2026-05-13
> Scope: 从需求到上线的全生命周期开发规范
> Tech Stack: FastAPI + Vanilla HTML/JS + PostgreSQL + Redis + Docker

---

## 0. 为什么需要这份规范

本项目当前状态：
- 代码已有四层分层（api/core/models/services/schemas），但模型集中在单文件、Service用静态类模式
- CONTRIBUTING.md 声明了 black/flake8/mypy，但**零配置文件、零pre-commit hooks**
- 测试覆盖仅10%，无conftest.py，测试配置重复
- 无CI/CD流水线
- 无Alembic迁移，用`init_db()`暴力建表
- 部署靠手工shell脚本

本规范的目标：**建立可执行、可自动化的开发纪律，不是挂在墙上的文档。**

---

## 1. 分支策略

### 1.1 分支模型

```
main ────────────────────────────────────────── 生产分支，保护分支
  │
  ├── develop ─────────────────────────────── 开发集成分支
  │     │
  │     ├── feature/TASK-001-add-certificate-api
  │     ├── feature/TASK-002-progress-refactor
  │     ├── fix/TASK-003-sandbox-timeout-bug
  │     └── chore/TASK-004-alembic-migration
  │
  └── hotfix/TASK-005-prod-login-crash ────── 生产热修
```

### 1.2 命名规则

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能 | `feature/TASK-{id}-{short-desc}` | `feature/TASK-012-certificate-api` |
| 修复 | `fix/TASK-{id}-{short-desc}` | `fix/TASK-008-sandbox-timeout` |
| 杂项 | `chore/TASK-{id}-{short-desc}` | `chore/TASK-015-alembic-setup` |
| 热修 | `hotfix/TASK-{id}-{short-desc}` | `hotfix/TASK-003-prod-login-crash` |

**规则**：
- 短描述用小写kebab-case，不超过3个词
- 所有分支必须关联TASK ID
- 禁止直推`main`和`develop`（branch protection）

### 1.3 分支生命周期

```
创建分支 → 开发(≤5天) → 自测通过 → 提交PR → Code Review → 合并到develop → 删除分支
```

- 功能分支存活**不超过5个工作日**，超过需拆分
- 合并后**立即删除**分支

---

## 2. 需求阶段

### 2.1 需求文档规范

每个需求必须包含以下字段，记录在TASKS.md或Issue中：

```markdown
### TASK-{id}: {标题}

- **优先级**: P0/P1/P2/P3
- **类型**: feature | fix | refactor | chore
- **负责人**: @xxx
- **状态**: 待开始 | 进行中 | 待review | 已完成

**需求描述**：
{用1-3句话描述要做什么}

**验收标准**（必须可测试）：
- [ ] AC1: {具体可验证的条件}
- [ ] AC2: {具体可验证的条件}

**影响范围**：
- 后端: {涉及的api/service/model}
- 前端: {涉及的页面/组件}
- 数据库: {是否需要schema变更}

**关联**：
- 依赖: TASK-xxx
- 阻塞: TASK-xxx
```

### 2.2 需求评审检查清单

| 检查项 | 要求 |
|--------|------|
| 验收标准可测试 | 每条AC有明确的输入/输出/预期结果 |
| 影响范围已标注 | 后端/前端/数据库哪些模块受影响 |
| 非功能需求已考虑 | 性能、安全、兼容性是否有约束 |
| 无歧义 | 任何开发人员读完都能理解要做的事 |

**不通过则打回，不进入设计阶段。**

---

## 3. 设计阶段

### 3.1 设计文档模板

对于P0/P1需求，或涉及2个以上模块变更的需求，必须写设计文档：

```markdown
## DESIGN: TASK-{id} {标题}

### 1. 变更概述
{50字以内说明做什么}

### 2. 方案设计

#### 2.1 API变更
| 方法 | 路径 | 请求体 | 响应体 | 认证 |
|------|------|--------|--------|------|

#### 2.2 数据模型变更
{新增/修改/删除哪些表/字段，附Alembic迁移说明}

#### 2.3 核心逻辑
{关键业务流程，伪代码或流程图}

### 3. 替代方案
{列出至少1个备选方案及取舍原因}

### 4. 风险与约束
{已知风险、技术约束、性能影响}
```

P2/P3需求可不写独立设计文档，但PR描述中必须包含方案说明。

### 3.2 设计评审检查清单

| 检查项 | 要求 |
|--------|------|
| API设计符合RESTful | 资源命名、HTTP语义正确 |
| 数据模型有迁移方案 | 明确Alembic upgrade/downgrade |
| 不破坏现有接口 | 向后兼容或有版本策略 |
| 安全已考虑 | 认证/鉴权/输入校验/沙箱限制 |

---

## 4. 开发阶段

### 4.1 代码结构规范

```
backend/app/
├── api/v1/                    # 路由层：只做参数校验和调用Service
│   ├── {module}.py            # 一个模块一个文件
│   └── deps.py                # 共享依赖注入
├── core/                      # 基础设施层：配置、数据库、安全
├── models/                    # 数据模型层
│   ├── __init__.py            # 导出所有模型
│   ├── user.py                # 每个模型一个文件（新规范）
│   ├── course.py
│   └── ...
├── schemas/                   # Pydantic请求/响应模型
│   ├── {module}.py            # 与API模块一一对应
│   └── __init__.py
├── services/                  # 业务逻辑层
│   ├── {module}_service.py    # 与API模块一一对应
│   └── ...
└── data/                      # 种子数据
```

### 4.2 命名规范

| 类别 | 规范 | 正确 | 错误 |
|------|------|------|------|
| Python文件 | snake_case | `user_service.py` | `userService.py` |
| 类名 | PascalCase | `UserService` | `user_service` |
| 函数/方法 | snake_case | `get_user_by_id` | `getUserById` |
| 常量 | UPPER_SNAKE | `MAX_EXECUTION_TIME` | `maxExecutionTime` |
| API路径 | kebab-lower | `/api/v1/lab-submissions` | `/api/v1/labSubmissions` |
| 数据库列 | snake_case | `created_at` | `createdAt` |
| 环境变量 | UPPER_SNAKE | `DATABASE_URL` | `databaseUrl` |

### 4.3 代码风格强制执行

**工具链配置（必须存在）**：

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 100

[tool.flake8]
max-line-length = 100
exclude = [".git", "__pycache__", "venv", "migrations"]
per-file-ignores = ["__init__.py:F401"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

### 4.4 Pre-commit Hooks（强制）

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
```

**安装**：`pre-commit install`（首次clone后必须执行）

### 4.5 Commit规范

格式：`<type>(<scope>): <subject>`

| Type | 含义 | 示例 |
|------|------|------|
| feat | 新功能 | `feat(api): add certificate endpoint` |
| fix | 修复 | `fix(sandbox): handle execution timeout` |
| refactor | 重构 | `refactor(models): split into per-model files` |
| test | 测试 | `test(auth): add registration edge cases` |
| docs | 文档 | `docs(api): update endpoint descriptions` |
| chore | 杂项 | `chore(ci): add GitHub Actions workflow` |

**规则**：
- subject不超过50字符
- 不加句号
- 用英文（与代码一致）
- 一个commit只做一件事

### 4.6 开发自检清单

每次提交前必须确认：

- [ ] `black --check .` 通过
- [ ] `flake8 .` 通过
- [ ] `pytest tests/ -v` 通过
- [ ] 新代码有对应的测试
- [ ] API变更有对应的schema更新
- [ ] 数据库变更有Alembic迁移脚本

---

## 5. 测试阶段

### 5.1 测试分层

```
┌─────────────────────────────┐
│     E2E Tests (5%)          │  关键用户流程
├─────────────────────────────┤
│   Integration Tests (25%)   │  API端点 + 数据库
├─────────────────────────────┤
│    Unit Tests (70%)         │  Service/函数/工具类
└─────────────────────────────┘
```

### 5.2 测试目录结构

```
tests/
├── conftest.py              # 全局fixtures：test_db, client, test_user
├── fixtures/                # 测试数据
│   ├── courses.json
│   └── users.json
├── unit/                    # 单元测试
│   ├── test_code_security.py
│   ├── test_user_service.py
│   └── test_grader.py
├── integration/             # 集成测试
│   ├── test_auth_api.py
│   ├── test_courses_api.py
│   ├── test_labs_api.py
│   ├── test_progress_api.py
│   └── test_certificates_api.py
└── e2e/                     # 端到端测试
    └── test_learning_flow.py
```

### 5.3 conftest.py 核心Fixtures

```python
# 必须提供以下fixtures，所有测试文件共享
@pytest.fixture(scope="function")
def test_db():
    """每个测试函数独立数据库（SQLite内存），测试结束自动清理"""

@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI TestClient，已注入test_db"""

@pytest.fixture(scope="function")
def test_user(client):
    """已注册的测试用户，返回{user, token}"""

@pytest.fixture(scope="function")
def admin_user(client):
    """管理员用户，返回{user, token}"""

@pytest.fixture(scope="function")
def test_course(test_db):
    """已创建的测试课程，含章节和实验"""
```

### 5.4 测试编写规范

**每个测试函数遵循 AAA 模式**：

```python
def test_register_duplicate_email(client):
    # Arrange
    client.post("/api/v1/auth/register", json={"email": "test@example.com", ...})

    # Act
    response = client.post("/api/v1/auth/register", json={"email": "test@example.com", ...})

    # Assert
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
```

**命名规范**：`test_{功能}_{场景}_{预期结果}`

```python
# Good
def test_login_wrong_password_returns_401(client, test_user):
def test_execute_code_timeout_returns_error(client, test_user):

# Bad
def test_login(client):
def test_code(client, test_user):
```

### 5.5 测试覆盖率要求

**三阶段爬坡策略**（从现状10%渐进到终态80%，不搞一刀切）：

| 阶段 | 时间窗口 | 整体门禁 | core/security | core/code_security | services/ | api/v1/ | models/ |
|------|---------|---------|---------------|-------------------|-----------|---------|---------|
| **阶段一：补骨架** | 第1个月 | ≥40% | ≥70% | ≥70% | ≥50% | ≥40% | ≥30% |
| **阶段二：填血肉** | 第2-3月 | ≥70% | ≥90% | ≥90% | ≥75% | ≥60% | ≥50% |
| **阶段三：打磨** | 第4月+ | ≥80% | ≥95% | ≥95% | ≥85% | ≥75% | ≥70% |

**为什么终态是80%而不是90%**：
- 剩余20%大多是边界场景、错误分支、第三方集成mock，投入产出比急速下降
- 那部分精力更值得投入**集成测试和E2E测试**——覆盖率数字不高但发现真实bug的能力更强
- 核心/安全模块单独要求95%，该严的地方严

**执行规则**：
- CI中 `--cov-fail-under` 的值随阶段切换更新
- 新PR必须满足当前阶段门禁，且**不低于该PR涉及模块的阶段要求**
- 阶段切换由团队确认整体达标后执行，不是按日历硬切

**执行**：`pytest --cov=app --cov-report=term-missing tests/`

### 5.6 PR测试门禁

PR合并前必须通过：

```
✅ pytest tests/ -v --cov=app --cov-fail-under=40  # 三阶段爬坡，随阶段更新
✅ black --check .
✅ flake8 .
✅ mypy app/
```

---

## 6. Code Review

### 6.1 PR模板

```markdown
## 变更描述
{1-3句话}

## 变更类型
- [ ] feat: 新功能
- [ ] fix: 修复
- [ ] refactor: 重构（无功能变更）
- [ ] test: 测试
- [ ] docs: 文档
- [ ] chore: 杂项

## 关联任务
Closes TASK-{id}

## 自检清单
- [ ] 代码风格检查通过（black + flake8）
- [ ] 新代码有对应测试
- [ ] 所有测试通过
- [ ] 数据库变更有Alembic迁移（upgrade + downgrade）
- [ ] API变更有schema文档更新
- [ ] 无硬编码密钥/密码

## 测试说明
{新增了哪些测试，覆盖了哪些场景}
```

### 6.2 Review检查清单

| 维度 | 检查项 |
|------|--------|
| **正确性** | 逻辑是否正确，边界条件是否处理 |
| **安全** | 输入校验、SQL注入、XSS、认证鉴权 |
| **性能** | N+1查询、大数据量场景、缓存策略 |
| **可维护** | 命名清晰、函数<50行、无重复代码 |
| **测试** | 新增代码有测试、覆盖边界和异常 |
| **文档** | API文档/README/DESIGN已同步更新 |

### 6.3 Review时效

- P0/P1任务的PR：**24小时内**必须完成review
- P2/P3任务的PR：**48小时内**
- 超48小时未review，发起人有权escalate

---

## 7. 数据库迁移

### 7.1 Alembic规范（新增要求）

**初始化**：
```bash
cd backend
alembic init alembic
# 编辑 alembic/env.py：引入Base.metadata，配置database_url
```

**每个schema变更必须生成迁移**：
```bash
# 自动生成
alembic revision --autogenerate -m "add certificate table"

# 手动编写（复杂变更）
alembic revision -m "migrate progress status enum"
```

**迁移脚本要求**：
- `upgrade()` 和 `downgrade()` **必须成对实现**
- 数据迁移（非schema变更）用单独的迁移脚本
- 迁移脚本一旦合并，**禁止修改**，只能新增逆向迁移

### 7.2 迁移流程

```
开发: alembic revision → 编写迁移 → 本地upgrade验证
测试: CI自动执行 alembic upgrade head
部署: deploy.sh中自动执行 alembic upgrade head（已有备份前提下）
```

---

## 8. CI/CD

### 8.1 CI流水线（GitHub Actions）

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports: ['5432:5432']
      redis:
        image: redis:7-alpine
        ports: ['6379:6379']

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install black flake8 mypy pytest pytest-cov

      - name: Black
        run: black --check backend/

      - name: Flake8
        run: flake8 backend/

      - name: Mypy
        run: mypy backend/app/

      - name: Tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: pytest tests/ -v --cov=backend/app --cov-fail-under=40  # 三阶段爬坡，随阶段更新
```

### 8.2 CD流水线

```
develop分支合并 → 自动部署到staging环境 → 手动验证 → 合并到main → 自动部署到生产
```

**部署检查门禁**：
1. 所有CI检查通过
2. staging环境冒烟测试通过
3. 至少1人approve（main分支保护）

---

## 9. 部署

### 9.1 部署前检查清单

| 检查项 | 要求 |
|--------|------|
| `.env` 非默认值 | SECRET_KEY / DB_PASSWORD / REDIS_PASSWORD 已修改 |
| 数据库备份 | `pg_dump` 备份完成，文件已验证 |
| 迁移脚本测试 | `alembic upgrade head` 在staging验证通过 |
| 回滚方案 | 有 `alembic downgrade` 路径 + Docker镜像回退方案 |
| 健康检查 | `/docs` 可访问，数据库连接正常 |

### 9.2 部署流程

```bash
# 1. 备份
./deploy.sh backup

# 2. 拉取代码
git pull origin main

# 3. 构建镜像
docker-compose -f docker-compose.prod.yml build --no-cache

# 4. 数据库迁移
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 5. 滚动重启
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend
# 等待健康检查通过后再重启frontend
docker-compose -f docker-compose.prod.yml up -d --no-deps --build frontend

# 6. 验证
curl -f http://localhost:8000/docs || (echo "FAIL" && docker-compose -f docker-compose.prod.yml logs backend)
```

### 9.3 回滚流程

```bash
# 1. 数据库回滚
docker-compose -f docker-compose.prod.yml run --rm backend alembic downgrade -1

# 2. 镜像回退
docker-compose -f docker-compose.prod.yml down
git checkout {previous-tag}
docker-compose -f docker-compose.prod.yml up -d

# 3. 数据库恢复（极端情况）
./deploy.sh backup  # 先备份当前状态
pg_restore -d {db_name} {backup_file}
```

---

## 10. 监控与告警

### 10.1 必须监控的指标

| 指标 | 告警阈值 | 检查方式 |
|------|---------|---------|
| API响应时间 | >500ms (P95) | Nginx access log / APM |
| 错误率 | >1% (5xx) | 日志聚合 |
| 数据库连接数 | >80% pool | SQLAlchemy pool status |
| 沙箱容器泄漏 | 运行中>10个 | Docker ps |
| 磁盘使用 | >85% | df -h |

### 10.2 日志规范

```python
import logging
logger = logging.getLogger(__name__)

# 级别使用
logger.debug("SQL query: %s", query)          # 开发调试
logger.info("User %s registered", user_id)    # 业务事件
logger.warning("Slow query: %dms", duration)  # 需要关注
logger.error("Sandbox execution failed: %s", e)  # 错误但系统可用
logger.critical("Database connection lost")      # 系统不可用
```

**禁止**：`print()` 用于生产日志；异常只 `logger.error(e)` 不带 traceback（用 `exc_info=True`）

---

## 11. 安全规范

### 11.1 开发安全检查清单

| 检查项 | 要求 |
|--------|------|
| 输入校验 | 所有API入参通过Pydantic schema校验 |
| SQL注入 | 禁止字符串拼接SQL，使用ORM参数化查询 |
| XSS | 前端渲染用户内容必须转义 |
| 认证 | 除公开API外，所有端点要求Bearer Token |
| 密钥管理 | 禁止代码中硬编码密钥，使用环境变量 |
| 沙箱安全 | 代码执行必须走安全检查（code_security.py） |
| CORS | 生产环境配置具体域名，禁止 `*` |

### 11.2 依赖安全

```bash
# 定期执行（建议每周）
pip install safety
safety check -r backend/requirements.txt

pip install pip-audit
pip-audit -r backend/requirements.txt
```

---

## 12. 全流程速查

```
需求阶段                    设计阶段                    开发阶段
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│ 1.写需求描述  │    →     │ 1.写设计文档  │    →     │ 1.创建分支    │
│ 2.定义验收标准│          │ 2.定义API+模型│          │ 2.编写代码    │
│ 3.标注影响范围│          │ 3.评估风险    │          │ 3.编写测试    │
│ 4.需求评审    │          │ 4.设计评审    │          │ 4.本地自检    │
└──────────────┘          └──────────────┘          └──────────────┘
                                                           │
测试阶段                    部署阶段                    ←────┘
┌──────────────┐          ┌──────────────┐
│ 1.单元测试    │    →     │ 1.合并到develop│
│ 2.集成测试    │          │ 2.CI自动检查   │
│ 3.覆盖率≥60% │          │ 3.部署staging  │
│ 4.PR提交     │          │ 4.冒烟测试     │
│ 5.Code Review│          │ 5.合并到main   │
│ 6.合并       │          │ 6.部署生产     │
└──────────────┘          └──────────────┘
```

---

## 附录A：快速初始化清单

新开发者clone项目后，依次执行：

```bash
# 1. 安装pre-commit hooks
pip install pre-commit
pre-commit install

# 2. 安装后端依赖
cd backend && pip install -r requirements.txt
pip install black flake8 isort mypy pytest pytest-cov

# 3. 启动开发环境
cd .. && docker-compose up -d

# 4. 运行测试确认环境OK
cd backend && pytest ../tests/ -v

# 5. 查看API文档
open http://localhost:8000/docs
```

## 附录B：工具链版本锁定

| 工具 | 版本 | 用途 |
|------|------|------|
| black | >=24.0 | 代码格式化 |
| isort | >=5.13 | import排序 |
| flake8 | >=7.0 | 代码检查 |
| mypy | >=1.8 | 类型检查 |
| pytest | >=8.0 | 测试框架 |
| pytest-cov | >=5.0 | 覆盖率 |
| pre-commit | >=3.6 | Git hooks |
| alembic | >=1.13 | 数据库迁移 |
| safety | >=3.0 | 依赖安全扫描 |

## 附录C：与现有文档的关系

| 本规范章节 | 替代/补充 | 现有文档 |
|-----------|----------|---------|
| §1 分支策略 | 替代 | CONTRIBUTING.md 中的分支规范 |
| §2-3 需求/设计 | 新增 | 无 |
| §4 开发规范 | 补充 | CONTRIBUTING.md 中的编码规范 |
| §5 测试 | 新增 | 无（run_tests.sh仅运行test_complete.py） |
| §6 Code Review | 替代 | CONTRIBUTING.md 中的PR流程 |
| §7 数据库迁移 | 新增 | 无（当前无Alembic） |
| §8 CI/CD | 新增 | 无（当前零CI/CD） |
| §9 部署 | 补充 | deploy.sh（保留，补充回滚流程） |
| §10-11 监控/安全 | 补充 | SECURITY.md（保留，补充开发安全） |
