# AI学习平台 — 架构设计文档

> **Version: 2.0 | Date: 2026-05-13**
> 替代: 原DESIGN.md (v1.0)
> **本文档定位**: 编码agent的"施工蓝图"，读完此文档+PRD_v2.md，应能写出正确可运行的代码
> **与PRD_v2的关系**: PRD回答"做什么"，本文档回答"怎么做"

---

## 〇、阅读指引

本文档的每个设计决策都基于 **代码现状** 而非理想状态。如果你是编码agent：

1. **先读§1** 了解项目全貌
2. **§3 数据库** 和 **§4 API** 是最核心的参考资料，修改代码前必读
3. **§5 业务逻辑** 给出精确的方法签名和流程，照着实现
4. **§6 安全** 中的红色标记(🚨)是已知漏洞，MVP阶段必须修复
5. **§8 任务拆解** 是你的工作清单，按依赖顺序执行
6. **§9 约束与红线** 是不可违反的规则，违反即为bug

---

## 一、项目概述

### 1.1 一句话

浏览器内"学→练→测→证"全链路的AI全栈工程师培养平台。

### 1.2 MVP目标

一个零基础用户，能在30分钟内完成：注册 → 选课 → 学完第一章 → 完成第一个实验 → 看到自己的进度。

### 1.3 当前状态

| 维度 | 现状 | MVP要求 | 差距 |
|------|------|---------|------|
| 用户系统 | 注册/登录/JWT | ✅ 已有 | token刷新未实现 |
| 课程系统 | 6阶段60章43实验 | ✅ 已有 | 无 |
| 实验系统 | 代码编辑+执行+提交 | ⚠️ 部分可用 | 评测未接入、安全漏洞 |
| 进度系统 | 章节进度追踪 | ⚠️ 部分可用 | 两个重叠端点需合并 |
| 证书系统 | 基础实现 | ❌ MVP不需要 | P2再做 |
| 讨论区 | 基础CRUD | ❌ MVP不需要 | P1再做 |
| 安全 | 多个已知漏洞 | 🚨 必须修复 | 5个高危 |
| 测试 | 78个测试（含16项数据契约） | ≥40% | 有提升 |
| 数据库 | SQLite硬编码 | 需支持PostgreSQL | 配置BUG |
| 前端 | Vanilla JS SPA | ✅ 可用 | 缺Toast/Loading |
| 数据契约 | 三道防线（启动断言+契约测试+init行为声明） | ✅ 已有 | 无 |

### 1.4 技术栈（实际，非幻想）

```
后端: Python 3.11 + FastAPI + SQLAlchemy + SQLite(开发) / PostgreSQL(生产)
缓存: Redis (已配置但未使用)
前端: Vanilla HTML/JS + ES Modules (无构建步骤)
沙箱: Docker容器 (有本地subprocess回退)
部署: Docker Compose + Nginx
```

**⚠️ 注意**: 原DESIGN.md写的React+TypeScript+MinIO+Celery都是**未实现的幻想**，不要参考。代码现实是Vanilla JS。

---

## 二、技术架构

### 2.1 系统架构图（实际部署）

```
┌─────────────────────────────────────────────┐
│                 Nginx                         │
│          (反向代理 + 静态文件)                │
└──────────┬──────────────────┬────────────────┘
           │                  │
    /api/* │                  │ /static/*
           ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│   FastAPI 后端    │  │   前端静态文件    │
│                  │  │  (Vanilla JS)    │
│  ┌────────────┐ │  └──────────────────┘
│  │ Auth 模块   │ │
│  │ Course 模块 │ │
│  │ Lab 模块    │ │
│  │ Progress 模块│ │
│  └────────────┘ │
└───────┬──────────┘
        │
   ┌────┼────────┐
   │    │        │
   ▼    ▼        ▼
SQLite  Redis  Docker
(开发)  (缓存)  (沙箱)
```

### 2.2 项目目录结构（实际，非幻想）

```
ai-learning-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI应用入口、路由注册、中间件
│   │   ├── core/
│   │   │   ├── config.py           # Settings(BaseSettings)，所有配置项
│   │   │   ├── database.py         # 引擎、SessionLocal、get_db()、init_db()
│   │   │   ├── security.py         # JWT创建/验证、密码哈希
│   │   │   └── code_security.py    # 代码安全检查（AST+正则）
│   │   ├── models/
│   │   │   └── __init__.py         # ⚠️ 所有ORM模型在单文件中（8个模型）
│   │   ├── schemas/
│   │   │   ├── __init__.py         # ⚠️ 重复定义，与子模块不一致
│   │   │   ├── user.py             # UserCreate/UserResponse/Token
│   │   │   ├── course.py           # Course/Lab/Chapter/Submission相关schema
│   │   │   ├── progress.py         # Progress/LearningStats相关schema
│   │   │   └── discussion.py       # Discussion/Comment相关schema
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py         # /api/v1/auth — 注册/登录/当前用户
│   │   │       ├── courses.py      # /api/v1/courses — 课程+章节+进度
│   │   │       ├── labs.py         # /api/v1/labs — 执行+提交历史
│   │   │       ├── progress.py     # /api/v1/progress — 进度+统计
│   │   │       ├── certificates.py # /api/v1/certificates — 证书
│   │   │       └── discussions.py  # /api/v1 — 讨论区
│   │   ├── services/
│   │   │   ├── user_service.py     # UserService (静态方法类)
│   │   │   ├── course_service.py   # CourseService (静态方法类)
│   │   │   ├── lab_service.py      # LabService (静态方法类)
│   │   │   ├── code_executor.py    # Docker沙箱+本地回退
│   │   │   ├── grader.py           # 代码评测
│   │   │   ├── certificate.py      # 证书生成/验证
│   │   │   └── discussion_service.py # DiscussionService
│   │   └── data/
│   │       ├── courses.py            # PHASE_TITLES + 课程壳 + 孤例清理
│   │       ├── courses_phase1.py     # Phase 1 加载器（upsert, JSON为真相源）
│   │       ├── courses_phase2.py     # Phase 2 加载器（upsert, JSON为真相源）
│   │       ├── courses_phase3_6.py   # Phase 3-6 加载器（create_only, DB为真相源）
│   │       ├── courses_extended_fixed.py  # Phase 3-6 种子数据
│   │       ├── phase1/               # Phase 1 JSON内容（10章2实验）
│   │       ├── phase2/               # Phase 2 JSON内容（10章2实验）
│   │       └── phase3/               # Phase 3 内容草稿
│   ├── tests/                      # 78个测试（含16项数据契约测试）
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/                        # 新版SPA
│   │   ├── main.js                 # 入口
│   │   ├── config/env.js           # 环境配置
│   │   ├── core/
│   │   │   ├── router.js           # Hash路由
│   │   │   └── store.js            # Proxy响应式Store
│   │   ├── services/
│   │   │   ├── api.js              # APIClient + API模块
│   │   │   ├── auth.js             # Token管理
│   │   │   ├── autoSave.js         # 自动保存
│   │   │   └── theme.js            # 主题
│   │   ├── views/                  # 页面组件
│   │   └── components/             # UI组件
│   ├── css/
│   ├── js/                         # 旧版JS（保留兼容）
│   ├── spa.html / index.html       # SPA入口
│   └── *.html                      # 旧版页面
├── sandbox/
│   ├── Dockerfile                  # 沙箱镜像
│   └── runner.py                   # 沙箱内代码执行器
├── docker-compose.yml
├── nginx.conf
├── PRD_v2.md                       # 产品需求文档
├── DESIGN.md                       # 本文档
├── DEVELOPMENT_HARNESS.md          # 开发流程规范
└── README.md
```

### 2.3 请求处理流程

```
浏览器 → Nginx(:80)
         ├── /api/* → FastAPI(:8000)
         │           ├── JWT验证(需认证的端点)
         │           ├── Service层业务逻辑
         │           ├── SQLAlchemy ORM操作
         │           └── 返回JSON响应
         └── /* → 静态文件(前端)

代码执行流程:
POST /api/v1/labs/execute
  → LabService.validate_code() [简单关键字检查]
  → code_executor.execute_code_docker()
      → validate_code() [大小/超时校验]
      → check_code_security() [AST+正则安全检查]
      → check_docker_available() → Docker或本地回退
      → _run_in_container() / execute_code_subprocess_fallback()
  → 返回 {success, output, error, execution_time_ms}
```

---

## 三、数据库设计

### 3.1 设计原则

- **MVP阶段不拆分模型文件**：现有8个模型在`models/__init__.py`单文件中，MVP阶段维持现状
- **新增字段用Alembic迁移**：禁止再使用`init_db()`暴力建表
- **PostgreSQL兼容**：所有字段类型必须同时兼容SQLite和PostgreSQL

### 3.2 核心表定义（MVP阶段现有+需修改）

#### users 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, autoincrement | |
| email | String(255) | UNIQUE, NOT NULL, INDEX | 登录凭证 |
| username | String(100) | UNIQUE, NOT NULL, INDEX | 显示名称 |
| password_hash | String(255) | NOT NULL | bcrypt |
| avatar_url | String(500) | nullable | 头像URL |
| role | String(20) | NOT NULL, default="student" | student/teacher/admin |
| is_active | Boolean | default=True | 账号状态 |
| created_at | DateTime | default=utcnow | |
| updated_at | DateTime | default=utcnow, onupdate=utcnow | |

**MVP修改**: 无。表结构不变。

#### courses 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, autoincrement | |
| title | String(200) | NOT NULL | |
| description | Text | nullable | |
| cover_image | String(500) | nullable | |
| level | String(20) | NOT NULL | beginner/intermediate/advanced/expert |
| category | String(50) | NOT NULL | python/math/ml/dl/llm/engineering |
| duration_hours | Integer | default=0 | |
| is_published | Boolean | default=False | |
| order_index | Integer | default=0 | 学习路径排序 |
| created_at | DateTime | default=utcnow | |
| updated_at | DateTime | default=utcnow, onupdate=utcnow | |

**MVP修改**: 无。

#### chapters 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, autoincrement | |
| course_id | Integer | FK(courses.id), NOT NULL | |
| title | String(200) | NOT NULL | |
| content | Text | NOT NULL | Markdown内容 |
| order_index | Integer | default=0 | |
| chapter_type | String(20) | default="text" | text/code/lab/video |
| duration_minutes | Integer | default=0 | |
| created_at | DateTime | default=utcnow | |

**MVP修改**: 无。

#### labs 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, autoincrement | |
| chapter_id | Integer | FK(chapters.id), UNIQUE, NOT NULL | 1对1关系 |
| title | String(200) | NOT NULL | |
| description | Text | nullable | |
| starter_code | Text | nullable | 初始代码 |
| solution_code | Text | nullable | 🚨 不应返回前端 |
| test_cases | JSON | default=[] | 评测用例 |
| requirements | Text | nullable | 依赖包 |
| hints | JSON | default=[] | 提示列表 |
| time_limit_seconds | Integer | default=30 | |
| memory_limit_mb | Integer | default=256 | |
| created_at | DateTime | default=utcnow | |

**MVP修改**: 无表结构变化。schema层修复：`LabResponse` 不返回 `solution_code`。

#### learning_progress 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, autoincrement | |
| user_id | Integer | FK(users.id), NOT NULL | |
| chapter_id | Integer | FK(chapters.id), NOT NULL | |
| status | String(20) | default="not_started" | not_started/in_progress/completed |
| completed_at | DateTime | nullable | |
| last_accessed_at | DateTime | default=utcnow | |
| created_at | DateTime | default=utcnow | |

**MVP修改**: 新增 UNIQUE约束 `(user_id, chapter_id)`，防止重复记录。

#### lab_submissions 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, autoincrement | |
| user_id | Integer | FK(users.id), NOT NULL | |
| lab_id | Integer | FK(labs.id), NOT NULL | |
| code | Text | NOT NULL | 用户提交的代码 |
| output | Text | nullable | 执行输出 |
| status | String(20) | default="pending" | pending/running/success/failed |
| execution_time_ms | Integer | nullable | |
| error_message | Text | nullable | |
| created_at | DateTime | default=utcnow | |
| updated_at | DateTime | default=utcnow, onupdate=utcnow | |

**🚨 MVP必须修改**: 新增以下字段以支持评测：

| 新字段 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| score | Float | nullable, default=None | 0-100分 |
| passed | Boolean | nullable, default=None | 是否通过 |
| test_results | JSON | nullable, default=None | 逐条测试结果 |
| feedback | Text | nullable, default=None | 评测反馈文本 |

**迁移SQL**:
```sql
ALTER TABLE lab_submissions ADD COLUMN score FLOAT;
ALTER TABLE lab_submissions ADD COLUMN passed BOOLEAN;
ALTER TABLE lab_submissions ADD COLUMN test_results JSON;
ALTER TABLE lab_submissions ADD COLUMN feedback TEXT;
```

### 3.3 MVP阶段暂不使用的表

以下表已存在但MVP阶段**不重点投入**，维持现状即可：

| 表 | 状态 | 说明 |
|----|------|------|
| discussions | 保留 | P1阶段再打磨 |
| comments | 保留 | P1阶段再打磨 |

### 3.4 数据库迁移策略

**现状**: 无Alembic，使用`init_db()`暴力`create_all`。

**MVP迁移方案**:
1. 引入Alembic（参考DEVELOPMENT_HARNESS.md §6）
2. 初始化：`alembic init alembic`，基于当前模型生成初始migration
3. 后续所有schema变更必须通过`alembic revision --autogenerate`
4. 禁止修改`init_db()`，保留作为开发环境fallback

**PostgreSQL切换**:
- 修复`database.py`：读取`settings.DATABASE_URL`而非硬编码SQLite
- SQLAlchemy引擎创建时根据URL自动选择方言
- `connect_args={"check_same_thread": False}` 仅在SQLite时需要

---

## 四、API设计

### 4.1 通用约定

| 项目 | 规范 |
|------|------|
| URL前缀 | `/api/v1` |
| 认证方式 | `Authorization: Bearer ***` |
| Content-Type | `application/json` |
| 分页参数 | `?page=1&per_page=20`（MVP后实现） |
| 时间格式 | ISO 8601: `2026-05-13T10:30:00Z` |
| 错误响应 | `{"detail": "错误描述"}` |

### 4.1.1 API契约红线 🚨

> **根因**：前后端独立演化，字段名不一致是最常见的bug来源。以下规则是强制红线，违反即视为bug。

1. **后端Pydantic schema的字段名 = 前端消费的字段名**，必须完全一致（包括单复数）
2. **禁止前端自行翻译字段名**（如后端返回`chapters_count`，前端不得写成`chapter_count`）
3. **修改schema字段名时**，必须在同一commit中同步修改前端代码，并执行`grep -rn "old_field_name" frontend/`确认无遗漏
4. **新增API端点时**，必须在DEVELOPMENT_HARNESS.md §4.7.3 API契约注册表中登记
5. **response_model必须与函数实际返回类型一致**，禁止声明`List[T]`但返回`dict`
6. **Pydantic schema是唯一真相源**，DESIGN.md中的API示例json以schema为准

### 4.2 认证 API — `/api/v1/auth`

#### POST /api/v1/auth/register

注册新用户。

**请求体**:
```json
{
  "email": "user@example.com",
  "username": "learner01",
  "password": "MyPass123"
}
```

**验证规则**:
- `email`: 合法邮箱格式 (EmailStr)
- `username`: 3-20字符，字母/数字/下划线/中文
- `password`: ≥8字符，必须包含字母+数字

**成功响应** `201 Created`:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "learner01",
  "role": "student",
  "avatar_url": null,
  "is_active": true,
  "created_at": "2026-05-13T10:30:00Z"
}
```

**错误响应**:
- `400 Bad Request` — 邮箱/用户名已存在
- `422 Unprocessable Entity` — 输入验证失败

**实现文件**: `api/v1/auth.py` → `UserService.create()`

---

#### POST /api/v1/auth/login

用户登录，获取token。

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "MyPass123"
}
```

**⚠️ 重要**: 当前实现接受**JSON body**（非OAuth2PasswordRequestForm）。MVP阶段保持JSON方式，不改动。

**成功响应** `200 OK`:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Token规格**:
- Access Token: HS256签名，30分钟过期，payload `{"sub": user_id, "exp": ...}`
- Refresh Token: HS256签名，7天过期，payload `{"sub": user_id, "type": "refresh", "exp": ...}`

**错误响应**:
- `401 Unauthorized` — 邮箱或密码错误

**实现文件**: `api/v1/auth.py` → `UserService.authenticate()` → `create_access_token()` + `create_refresh_token()`

---

#### GET /api/v1/auth/me

获取当前用户信息。

**认证**: 必需

**成功响应** `200 OK`:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "learner01",
  "role": "student",
  "avatar_url": null,
  "is_active": true,
  "created_at": "2026-05-13T10:30:00Z"
}
```

**错误响应**:
- `401 Unauthorized` — token无效或过期

**实现文件**: `api/v1/auth.py` → `get_current_user()` 依赖注入

---

### 4.3 课程 API — `/api/v1/courses`

#### GET /api/v1/courses

获取已发布课程列表。

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| level | string | 否 | 按难度筛选: beginner/intermediate/advanced/expert |
| category | string | 否 | 按分类筛选: python/math/ml/dl/llm/engineering |

**认证**: 不需要

**成功响应** `200 OK`:
```json
[
  {
    "id": 1,
    "title": "Phase 1: Python快速通道",
    "description": "...",
    "cover_image": null,
    "level": "beginner",
    "category": "python",
    "duration_hours": 28,
    "is_published": true,
    "order_index": 1,
    "chapters_count": 14,
    "created_at": "2026-05-13T10:30:00Z"
  }
]
```

**⚠️ 注意**: 现有`CourseListResponse`不含`chapters_count`，MVP需在schema中新增此字段，在Service中通过`len(course.chapters)`计算。

**实现文件**: `api/v1/courses.py` → `CourseService.list_courses()`

---

#### GET /api/v1/courses/{course_id}

获取课程详情（含章节列表）。

**认证**: 不需要

**成功响应** `200 OK`:
```json
{
  "id": 1,
  "title": "Python for AI",
  "description": "...",
  "level": "beginner",
  "category": "python",
  "duration_hours": 14,
  "chapters": [
    {
      "id": 1,
      "title": "Python Basics",
      "order_index": 1,
      "chapter_type": "text",
      "duration_minutes": 30,
      "has_lab": true
    }
  ]
}
```

**⚠️ 注意**: 现有`ChapterResponse`不含`has_lab`，MVP需在schema中新增此字段，通过`chapter.lab is not None`计算。

**错误响应**:
- `404 Not Found` — 课程不存在或未发布

**实现文件**: `api/v1/courses.py` → `CourseService.get_course()`

---

#### GET /api/v1/courses/{course_id}/chapters

获取课程章节列表。

**认证**: 不需要

**成功响应** `200 OK`: `List[ChapterResponse]`

**实现文件**: `api/v1/courses.py` → `CourseService.get_chapters()`

---

#### GET /api/v1/courses/chapters/{chapter_id}

获取章节详情（含Markdown内容）。

**认证**: 不需要

**成功响应** `200 OK`:
```json
{
  "id": 1,
  "course_id": 1,
  "title": "Python Basics",
  "content": "# Python Basics\n\n...",
  "order_index": 1,
  "chapter_type": "text",
  "duration_minutes": 30,
  "lab": {
    "id": 1,
    "title": "Hello World",
    "description": "Write your first Python program",
    "starter_code": "# Write your code here\n",
    "hints": ["Use print() function"],
    "time_limit_seconds": 30,
    "memory_limit_mb": 256
  }
}
```

**🚨 安全修复**: 当前`LabResponse`暴露了`solution_code`和`test_cases`。MVP必须创建`LabPublicResponse`，排除这两个字段。

**错误响应**:
- `404 Not Found` — 章节不存在

**实现文件**: `api/v1/courses.py` → `CourseService.get_chapter()`

---

### 4.4 实验 API — `/api/v1/labs`

#### POST /api/v1/labs/execute

在沙箱中执行代码（不记录提交）。

**认证**: 必需

**请求体**:
```json
{
  "code": "print('hello world')",
  "language": "python",
  "timeout": 30
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| code | string | 是 | — | Python代码，≤100KB |
| language | string | 否 | "python" | MVP仅支持python |
| timeout | int | 否 | 30 | 超时秒数，≤300 |

**成功响应** `200 OK`:
```json
{
  "success": true,
  "output": "hello world\n",
  "error": null,
  "execution_time_ms": 120
}
```

**错误响应**:
- `400 Bad Request` — 代码安全检查未通过 `{"detail": "代码包含禁止的操作: os.system"}`
- `408 Request Timeout` — 执行超时 `{"detail": "代码执行超时(30秒)"}`
- `500 Internal Server Error` — 沙箱不可用

**执行流程（必须严格遵循）**:
```
1. 输入验证: code大小≤100KB, timeout≤300s
2. 安全检查: CodeSecurityChecker.check_code()
   - 不通过 → 直接返回400，不执行
3. 代码执行:
   a. 优先Docker容器: _run_in_container()
   b. Docker不可用 → 本地回退: execute_code_subprocess_fallback()
4. 结果格式化 → 返回CodeExecutionResponse
```

**🚨 关键修复**: 当前`LabService.validate_code()`是简单关键字匹配，与`CodeSecurityChecker`深度检查冲突。MVP必须统一使用`CodeSecurityChecker`，删除`LabService.validate_code()`。

**实现文件**: `api/v1/labs.py` → `code_executor.execute_code_docker()`

---

#### POST /api/v1/courses/labs/{lab_id}/submit

提交实验代码并自动评测。

**认证**: 必需

**请求体**:
```json
{
  "code": "def hello():\n    return 'hello world'"
}
```

**成功响应** `200 OK`:
```json
{
  "id": 42,
  "user_id": 1,
  "lab_id": 1,
  "code": "def hello():\n    return 'hello world'",
  "output": "hello world",
  "status": "success",
  "score": 85.0,
  "passed": true,
  "test_results": [
    {"name": "test_hello", "passed": true, "expected": "hello world", "actual": "hello world"},
    {"name": "test_type", "passed": true, "expected": "str", "actual": "str"}
  ],
  "feedback": "所有测试通过(2/2)。代码风格良好。",
  "execution_time_ms": 150,
  "error_message": null,
  "created_at": "2026-05-13T10:30:00Z"
}
```

**🚨 关键修改**: 当前提交端点调用`LabService.submit_code()`（不评测）。MVP必须改为调用`submit_with_grading()`（执行+评测），并确保：

1. 代码先经过安全检查和沙箱执行
2. 执行成功后，在沙箱内运行评测（禁止在主进程中`exec`用户代码）
3. 评测结果写入`lab_submissions`的新增字段（score/passed/test_results/feedback）
4. 若评测通过（passed=True），自动将关联章节进度标记为completed

**评测流程（必须严格遵循）**:
```
1. 安全检查: CodeSecurityChecker.check_code()
2. 沙箱执行: execute_code_docker(code, timeout)
3. 评测: CodeGrader.grade_submission(code, lab.test_cases, lab.solution_code)
   🚨 grade_submission中的run_test_case必须改为在沙箱中执行
   而非当前的exec(code)在主进程中执行
4. 写入LabSubmission记录（含score/passed/test_results/feedback）
5. 若passed=True → 自动更新LearningProgress.status="completed"
6. 返回LabSubmissionResponse
```

**错误响应**:
- `400 Bad Request` — 代码安全检查未通过
- `404 Not Found` — 实验不存在
- `408 Request Timeout` — 执行超时

**实现文件**: `api/v1/courses.py` → 新方法 `LabService.submit_and_grade()`

---

#### GET /api/v1/labs/{lab_id}/submissions

获取用户对某实验的提交历史。

**认证**: 必需

**成功响应** `200 OK`: `List[LabSubmissionResponse]`（按created_at降序）

**实现文件**: `api/v1/labs.py`

---

### 4.5 进度 API — `/api/v1/progress`

**⚠️ 重构说明**: 当前`/api/v1/courses/progress`和`/api/v1/progress/`功能重叠。MVP统一使用`/api/v1/progress`，删除`courses.py`中的进度端点。

#### GET /api/v1/progress

获取当前用户所有学习进度。

**认证**: 必需

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| course_id | int | 否 | 筛选特定课程 |

**成功响应** `200 OK`: `List[ProgressResponse]`

**实现文件**: `api/v1/progress.py`

---

#### GET /api/v1/progress/courses/{course_id}

获取特定课程的整体进度统计。

**认证**: 必需

**成功响应** `200 OK`:
```json
{
  "course_id": 1,
  "course_title": "Python for AI",
  "total_chapters": 14,
  "completed_chapters": 5,
  "in_progress_chapters": 2,
  "progress_percentage": 35.7,
  "is_completed": false
}
```

**实现文件**: `api/v1/progress.py`

---

#### POST /api/v1/progress/chapters/{chapter_id}

更新章节学习进度。

**认证**: 必需

**请求体**:
```json
{
  "status": "completed"
}
```

| status值 | 含义 |
|----------|------|
| not_started | 未开始 |
| in_progress | 学习中 |
| completed | 已完成 |

**成功响应** `200 OK`: `ProgressResponse`

**⚠️ 关键修复**: 当前`courses.py`中更新进度用**query参数**`?status=completed`，`progress.py`中用**body**。MVP统一用body方式（`ProgressUpdate` schema）。

**业务规则**:
- `status="completed"`时，自动设置`completed_at=now()`
- 已完成状态不可回退（前端可允许，后端不限制）
- 若该章节关联Lab且用户从未提交通过，是否允许标记completed？MVP允许（进度可手动标记），后续版本可加强

**实现文件**: `api/v1/progress.py` → `CourseService.update_progress()`

---

#### GET /api/v1/progress/stats/summary

获取学习统计摘要。

**认证**: 必需

**成功响应** `200 OK`:
```json
{
  "total_chapters_accessed": 10,
  "completed_chapters": 5,
  "in_progress_chapters": 3,
  "not_started_chapters": 2,
  "total_learning_minutes": 120,
  "completed_courses": 1
}
```

**实现文件**: `api/v1/progress.py`

---

### 4.6 MVP阶段不实现的API

以下端点已存在但MVP不投入，保持现状：

| 端点 | 模块 | 说明 |
|------|------|------|
| POST /api/v1/auth/refresh | auth | Token刷新，MVP后实现 |
| GET /api/v1/certificates/* | certificates | P2再实现 |
| POST /api/v1/courses/{id}/discussions | discussions | P1再实现 |
| GET /api/v1/courses/progress | courses | 删除，用/progress替代 |
| POST /api/v1/courses/chapters/{id}/progress | courses | 删除，用/progress/chapters/{id}替代 |

---

## 五、业务逻辑设计

### 5.1 Service层架构

当前所有Service都是**静态方法类**（无实例化、无注入）。MVP阶段维持此模式。

**调用模式**:
```python
# 在路由函数中
@router.post("/submit")
async def submit_lab(lab_id: int, data: LabSubmissionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    result = LabService.submit_and_grade(db, user.id, lab_id, data.code)
    return result
```

### 5.2 UserService

**文件**: `services/user_service.py`

| 方法 | 签名 | 说明 |
|------|------|------|
| get_by_email | `(db: Session, email: str) -> Optional[User]` | 按邮箱查询 |
| get_by_username | `(db: Session, username: str) -> Optional[User]` | 按用户名查询 |
| get_by_id | `(db: Session, user_id: int) -> Optional[User]` | 按ID查询 |
| create | `(db: Session, user_data: UserCreate) -> User` | 创建用户 |
| update | `(db: Session, user: User, user_data: UserUpdate) -> User` | 更新用户 |
| authenticate | `(db: Session, email: str, password: str) -> Optional[User]` | 认证 |

**MVP修改**: 无。方法签名和行为不变。

---

### 5.3 CourseService

**文件**: `services/course_service.py`

| 方法 | 签名 | 说明 |
|------|------|------|
| list_courses | `(db: Session, level: str = None, category: str = None) -> List[Course]` | 已发布课程列表 |
| get_course | `(db: Session, course_id: int) -> Optional[Course]` | 课程详情（仅已发布） |
| get_chapters | `(db: Session, course_id: int) -> List[Chapter]` | 章节列表（按order_index排序） |
| get_chapter | `(db: Session, chapter_id: int) -> Optional[Chapter]` | 章节详情 |
| get_chapter_lab | `(db: Session, chapter_id: int) -> Optional[Lab]` | 章节关联实验 |
| update_progress | `(db: Session, user_id: int, chapter_id: int, status: str) -> LearningProgress` | 更新进度 |

**MVP修改**:
- 删除`get_user_progress()`方法，其功能由`ProgressService`替代
- `update_progress()`增加completed_at自动设置

---

### 5.4 LabService（🚨 核心重构）

**文件**: `services/lab_service.py`

**现有方法（保留）**:

| 方法 | 签名 | 说明 |
|------|------|------|
| submit_code | `(db, user_id, lab_id, code) -> LabSubmission` | 仅执行，不评测 |
| submit_with_grading | `(db, user_id, lab_id, code) -> dict` | 执行+评测（🚨 需重写） |

**删除方法**:

| 方法 | 原因 |
|------|------|
| validate_code | 与CodeSecurityChecker重复且弱，删除 |
| execute_code | 与code_executor.py重复，删除 |

**新增方法**:

```python
@staticmethod
def submit_and_grade(db: Session, user_id: int, lab_id: int, code: str) -> LabSubmission:
    """
    提交代码并自动评测 — MVP核心方法
    
    流程:
    1. 查询Lab，获取test_cases和time_limit_seconds
    2. 安全检查: check_code_security(code) → 不通过则抛HTTPException(400)
    3. 沙箱执行: execute_code_docker(code, timeout=lab.time_limit_seconds)
    4. 创建LabSubmission记录，status="running"
    5. 评测: CodeGrader.grade_in_sandbox(code, lab.test_cases, timeout=lab.time_limit_seconds)
       ⚠️ 评测必须在沙箱中执行，禁止exec()在主进程
    6. 更新LabSubmission: score, passed, test_results, feedback, status
    7. 若passed=True: 自动更新LearningProgress(chapter_id=lab.chapter_id, status="completed")
    8. db.commit() → 返回LabSubmission
    
    异常:
    - Lab不存在 → HTTPException(404)
    - 安全检查未通过 → HTTPException(400, detail=安全报告)
    - 执行超时 → 更新status="failed", error_message="执行超时"
    """
```

---

### 5.5 CodeGrader（🚨 核心安全重构）

**文件**: `services/grader.py`

**🚨 严重漏洞**: 当前`run_test_case()`使用`exec(code, namespace)`在主进程中执行用户代码。攻击者可执行任意系统命令。

**MVP重构方案**: 评测代码也必须在Docker沙箱中执行。

```python
class CodeGrader:
    @staticmethod
    def grade_in_sandbox(code: str, test_cases: list, timeout: int = 30) -> dict:
        """
        在沙箱中执行评测
        
        流程:
        1. 语法检查: ast.parse(code) → 失败直接返回
        2. 构建评测代码: 将用户代码+测试用例拼接成一个完整脚本
           脚本模板:
           ```python
           {user_code}
           
           import json
           results = []
           for i, test in enumerate({test_cases_json}):
               try:
                   # 根据test类型执行不同评测
                   if test["type"] == "output_match":
                       output = eval(test["call"])
                       results.append({{"name": test["name"], "passed": str(output) == str(test["expected"]), "expected": str(test["expected"]), "actual": str(output)}})
                   elif test["type"] == "exception":
                       try:
                           eval(test["call"])
                           results.append({{"name": test["name"], "passed": False, "expected": test["expected"], "actual": "no exception"}})
                       except Exception:
                           results.append({{"name": test["name"], "passed": True, "expected": test["expected"], "actual": "exception raised"}})
               except Exception as e:
                   results.append({{"name": test["name"], "passed": False, "expected": str(test["expected"]), "actual": str(e)}})
           print("===RESULT_START===")
           print(json.dumps(results))
           print("===RESULT_END===")
           ```
        3. 调用 execute_code_docker(grading_code, timeout) 执行
        4. 解析输出中 ===RESULT_START=== 和 ===RESULT_END=== 之间的JSON
        5. 计算分数: passed_count / total_count * 100
        6. 生成反馈文本
        7. 返回 {score, passed, test_results, feedback}
        """
    
    @staticmethod
    def check_syntax(code: str) -> tuple[bool, Optional[str]]:
        """语法检查 — 保留，不在沙箱中"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"语法错误: 行{e.lineno}, {e.msg}"
    
    @staticmethod
    def generate_feedback(test_results: list, score: float) -> str:
        """生成评测反馈文本"""
        passed = sum(1 for t in test_results if t["passed"])
        total = len(test_results)
        lines = [f"测试通过: {passed}/{total}"]
        for t in test_results:
            status = "✅" if t["passed"] else "❌"
            lines.append(f"  {status} {t['name']}: 期望 '{t['expected']}', 实际 '{t.get('actual', 'N/A')}'")
        if score >= 80:
            lines.append("评测通过！")
        elif score >= 60:
            lines.append("部分通过，继续加油。")
        else:
            lines.append("未通过，请检查代码逻辑。")
        return "\n".join(lines)
```

**删除方法**:

| 方法 | 原因 |
|------|------|
| run_test_case | 🚨 在主进程中exec()，严重安全漏洞 |
| check_style | MVP阶段不需要代码风格检查 |

---

### 5.6 CodeExecutor

**文件**: `services/code_executor.py`

现有实现基本可用，MVP修改点：

1. **统一入口**: 所有代码执行（运行/评测）都通过`execute_code_docker()`
2. **结果解析标准化**: 输出格式统一为`===RESULT_START===\n{json}\n===RESULT_END===`
3. **错误处理增强**: 超时/内存溢出/安全违规 返回结构化错误

**方法签名（不变）**:
```python
async def execute_code_docker(code: str, timeout: int = 30) -> dict:
    """返回 {"success": bool, "output": str, "error": str|null, "execution_time_ms": int}"""

def check_code_security(code: str) -> tuple[bool, str]:
    """返回 (is_safe, error_message)"""

async def execute_code_subprocess_fallback(code: str, timeout: int = 30) -> dict:
    """Docker不可用时的本地回退"""
```

---

### 5.7 CodeSecurityChecker

**文件**: `core/code_security.py`

现有实现基本可用（AST分析+正则），MVP修复点：

1. **删除pathlib从ALLOWED_MODULES** — 与FORBIDDEN_MODULES矛盾
2. **修复正则误判** — `open\s*\(` 改为 `\bopen\s*\(`（单词边界）
3. **测试用例关键字豁免** — 评测代码中`assert`等关键字需要豁免

---

## 六、安全设计

### 6.1 🚨 MVP必须修复的安全漏洞

| # | 漏洞 | 影响 | 修复方案 | 优先级 |
|---|------|------|---------|--------|
| S1 | `grader.py`的`exec()`在主进程执行用户代码 | RCE远程代码执行 | 删除`run_test_case()`，评测改为沙箱执行 | P0 |
| S2 | `LabResponse`暴露`solution_code` | 答案泄露 | 创建`LabPublicResponse`，排除solution_code和test_cases | P0 |
| S3 | `LabService.validate_code()`弱检查绕过安全 | 安全检查形同虚设 | 统一使用`CodeSecurityChecker` | P0 |
| S4 | `database.py`硬编码SQLite URL | 生产环境数据安全 | 读取`settings.DATABASE_URL` | P0 |
| S5 | 证书验证不查数据库 | 证书可伪造 | P2再修（MVP不实现证书功能） | P2 |
| S6 | 讨论区点赞无防重 | 数据污染 | P1再修（MVP不重点投入讨论区） | P1 |

### 6.2 代码沙箱安全架构

```
用户提交代码
     │
     ▼
┌─────────────────────────────────────────┐
│ 1. 输入验证                              │
│    - 代码大小 ≤ 100KB                    │
│    - 超时设置 ≤ 300秒                    │
│    - 语言检查（仅python）                │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│ 2. 静态安全检查 (CodeSecurityChecker)    │
│    - AST分析: 禁止导入os/subprocess等    │
│    - 正则匹配: 禁止eval/exec/open等     │
│    - 属性检查: 禁止__import__等          │
│    不通过 → 返回400，不执行              │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│ 3. Docker沙箱执行                        │
│    - 独立容器，无网络(--network=none)     │
│    - CPU限制: 0.5核                     │
│    - 内存限制: 256MB                    │
│    - 超时强制终止                       │
│    - 只读文件系统                       │
│    - 执行完毕自动销毁容器               │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│ 4. 结果处理                              │
│    - 输出截断: ≤10000字符               │
│    - 超时检测                           │
│    - 错误信息脱敏(不含路径/环境变量)     │
└─────────────────────────────────────────┘
```

### 6.3 JWT认证安全

| 项目 | 当前 | MVP要求 |
|------|------|---------|
| Access Token过期 | 30分钟 | ✅ 保持 |
| Refresh Token过期 | 7天 | ✅ 保持 |
| Token刷新接口 | 未实现 | MVP后实现 |
| `datetime.utcnow()` | 🚨 已弃用 | 改为`datetime.now(timezone.utc)` |
| SECRET_KEY | 开发环境自动生成 | ✅ 保持，生产必须环境变量 |

---

## 七、前端设计

### 7.1 技术栈

**当前**: Vanilla HTML/JS + ES Modules，Hash路由，Proxy响应式Store

**MVP原则**: 维持Vanilla JS，不引入React/Vue。MVP后可考虑升级。

### 7.2 页面列表（MVP）

| 页面 | 路由 | 说明 | 状态 |
|------|------|------|------|
| 首页 | `/` | 平台介绍+推荐课程 | ✅ 已有 |
| 课程列表 | `/courses` | 按难度/分类展示 | ✅ 已有 |
| 课程详情 | `/courses/:id` | 章节大纲+开始学习 | ✅ 已有 |
| 章节阅读 | `/chapters/:id` | Markdown内容+代码块 | ✅ 已有 |
| 实验页 | `/labs/:id` | 代码编辑+执行+评测 | ⚠️ 需增强评测UI |
| 学习进度 | `/progress` | 进度统计 | ✅ 已有 |
| 登录 | `/login` | 邮箱+密码 | ✅ 已有 |
| 注册 | `/register` | 邮箱+用户名+密码 | ✅ 已有 |

**MVP不新增页面**。重点增强已有页面的交互体验。

### 7.3 实验页面增强（MVP重点）

当前实验页面只有"运行"按钮，缺少评测反馈。MVP增强：

```
┌─────────────────────────────────────────────────────┐
│ 实验标题: Hello World                                │
│ 描述: Write your first Python program                │
├─────────────────────┬───────────────────────────────┤
│                     │  评测结果                       │
│   代码编辑器        │  ┌──────────────────────┐      │
│   (Monaco/textarea) │  │ ✅ test_hello: 通过  │      │
│                     │  │ ✅ test_type: 通过   │      │
│                     │  │ 得分: 85/100         │      │
│                     │  │ 状态: 通过 🎉        │      │
│                     │  └──────────────────────┘      │
│                     │                                 │
│                     │  执行输出                       │
│                     │  ┌──────────────────────┐      │
│                     │  │ > hello world        │      │
│                     │  └──────────────────────┘      │
├─────────────────────┴───────────────────────────────┤
│ [▶ 运行]  [📤 提交评测]  [💡 提示]                    │
└─────────────────────────────────────────────────────┘
```

**关键交互**:
1. **"运行"按钮**: 调用`POST /labs/execute`，只执行不评测，结果展示在"执行输出"
2. **"提交评测"按钮**: 调用`POST /courses/labs/{id}/submit`，执行+评测，结果展示在"评测结果"
3. **"提示"按钮**: 按顺序展示`lab.hints`中的提示（先显示第1条，再点击显示第2条）
4. **评测通过后**: 章节进度自动标记为completed

### 7.4 前端通用组件增强（MVP）

| 组件 | 说明 | 优先级 |
|------|------|--------|
| Toast通知 | 操作成功/失败反馈，3秒自动消失 | P0 |
| Loading状态 | API请求期间显示加载动画 | P0 |
| 错误重试 | 网络异常时显示重试按钮 | P1 |
| 自动保存 | 实验代码自动保存到localStorage | P1 |

**Toast实现参考**:
```javascript
// 在前端services/api.js中统一处理
class APIClient {
  async request(url, options) {
    try {
      showLoading();
      const response = await fetch(url, options);
      if (!response.ok) {
        const error = await response.json();
        showToast(error.detail || '操作失败', 'error');
        throw error;
      }
      return response;
    } catch (e) {
      if (e.name === 'TypeError') {  // network error
        showToast('网络异常，请检查连接', 'error');
      }
      throw e;
    } finally {
      hideLoading();
    }
  }
}
```

### 7.5 Token管理修复

**🚨 当前问题**: 前端只存储`access_token`，忽略`refresh_token`，不验证token有效性。

**MVP修复方案**:
1. 登录时同时存储`access_token`和`refresh_token`到localStorage
2. 每次API请求前，检查access_token是否过期（解码JWT的exp字段）
3. 过期后跳转到登录页（MVP不实现refresh，直接重新登录）
4. 401响应统一跳转登录页

```javascript
// auth.js 修复
class AuthService {
  static setTokens(data) {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
  }
  
  static isTokenExpired() {
    const token = this.getAccessToken();
    if (!token) return true;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }
  
  static getAuthHeaders() {
    if (this.isTokenExpired()) {
      this.logout();
      window.location.hash = '#/login';
      return {};
    }
    return { Authorization: `Bearer ${this.getAccessToken()}` };
  }
}
```

---

## 八、开发任务拆解

### 8.1 MVP任务依赖图

```
T1: 安全修复(数据库+schema) ─────┐
                                 ├──→ T5: 评测系统集成 ──→ T7: 前端增强
T2: 评测系统重构(沙箱内评测) ────┘         │
                                           │
T3: 进度API统一 ──────────────────────────┘
                                           │
T4: 前端基础增强(Toast/Loading) ──────────┘
                                           ▼
                                    T6: 集成测试
                                           │
                                           ▼
                                    T7: 端到端验证
```

### 8.2 任务详情

#### T1: 安全与基础设施修复 [P0, 2天]

**目标**: 修复数据库硬编码和schema安全问题

**子任务**:
1. 修复`database.py`: 使用`settings.DATABASE_URL`而非硬编码
2. 修复`database.py`: SQLite时添加`connect_args`，PostgreSQL时不添加
3. 创建`LabPublicResponse` schema: 排除`solution_code`和`test_cases`
4. 更新`courses.py`和`labs.py`中返回Lab数据的端点，使用`LabPublicResponse`
5. 清理`schemas/__init__.py`中的重复schema定义
6. 修复`datetime.utcnow()` → `datetime.now(timezone.utc)`（全局替换）
7. 新增Alembic初始化和首个migration

**验证**:
- [ ] `settings.DATABASE_URL=postgresql://...` 时连接PostgreSQL正常
- [ ] `GET /api/v1/courses/chapters/{id}` 返回的Lab数据不含solution_code
- [ ] `alembic upgrade head` 执行成功
- [ ] 全局搜索`utcnow()`结果为0

**文件变更清单**:
```
MODIFY: backend/app/core/database.py
MODIFY: backend/app/schemas/course.py (新增LabPublicResponse)
MODIFY: backend/app/api/v1/courses.py (使用LabPublicResponse)
MODIFY: backend/app/api/v1/labs.py (使用LabPublicResponse)
MODIFY: backend/app/core/security.py (utcnow → now(timezone.utc))
MODIFY: backend/app/models/__init__.py (utcnow → now(timezone.utc))
CLEANUP: backend/app/schemas/__init__.py (删除重复定义)
CREATE: backend/alembic/ (初始化)
CREATE: backend/alembic/env.py
CREATE: backend/alembic/versions/001_initial.py
```

---

#### T2: 评测系统安全重构 [P0, 3天]

**目标**: 消除exec()主进程执行漏洞，评测改为沙箱执行

**子任务**:
1. 重写`grader.py`:
   - 删除`run_test_case()`（🚨 exec漏洞）
   - 删除`check_style()`（MVP不需要）
   - 新增`grade_in_sandbox()`: 在Docker沙箱中执行评测代码
   - 新增`generate_feedback()`: 生成评测反馈文本
   - 保留`check_syntax()`
2. 重写`lab_service.py`:
   - 删除`validate_code()`和`execute_code()`
   - 新增`submit_and_grade()`: 安全检查→沙箱执行→评测→写库
   - 重写`submit_with_grading()`: 调用`submit_and_grade()`
3. 新增`lab_submissions`表的score/passed/test_results/feedback字段
   - 创建Alembic migration: `002_add_grading_fields.py`
4. 更新`LabSubmissionResponse` schema: 新增score/passed/test_results/feedback字段
5. 修改`courses.py`的`POST /labs/{lab_id}/submit`: 调用`submit_and_grade()`替代`submit_code()`
6. 评测通过时自动更新章节进度为completed

**验证**:
- [ ] 提交恶意代码（如`import os; os.system('whoami')`）返回400
- [ ] 提交正确代码返回score+passed+test_results+feedback
- [ ] 全局搜索`exec(code` 结果为0（主进程无exec用户代码）
- [ ] 评测通过后章节进度自动变为completed
- [ ] 提交包含死循环的代码超时后返回正常错误（不死机）

**文件变更清单**:
```
REWRITE: backend/app/services/grader.py
REWRITE: backend/app/services/lab_service.py (大部分重写)
MODIFY: backend/app/models/__init__.py (LabSubmission新增4字段)
MODIFY: backend/app/schemas/course.py (LabSubmissionResponse新增4字段)
MODIFY: backend/app/api/v1/courses.py (submit端点改用submit_and_grade)
CREATE: backend/alembic/versions/002_add_grading_fields.py
```

---

#### T3: 进度API统一 [P0, 1天]

**目标**: 合并重叠的进度端点，统一使用/progress

**子任务**:
1. 删除`courses.py`中的`GET /progress`和`POST /chapters/{id}/progress`
2. 确认`progress.py`中的端点完整覆盖功能
3. 统一进度更新方式为body（`ProgressUpdate` schema），不用query参数
4. 添加`(user_id, chapter_id)`唯一约束到`learning_progress`
5. 更新前端`api.js`中的进度相关API调用

**验证**:
- [ ] `GET /api/v1/progress` 正常返回进度列表
- [ ] `POST /api/v1/progress/chapters/{id}` 用body方式更新进度
- [ ] 同一用户同一章节不会出现重复进度记录
- [ ] 前端进度页面功能正常

**文件变更清单**:
```
MODIFY: backend/app/api/v1/courses.py (删除2个进度端点)
MODIFY: backend/app/api/v1/progress.py (确认完整)
MODIFY: backend/app/models/__init__.py (LearningProgress唯一约束)
MODIFY: frontend/src/services/api.js (更新API调用)
```

---

#### T4: 前端基础增强 [P0, 2天]

**目标**: Toast/Loading/Token管理

**子任务**:
1. 实现Toast组件: 成功(绿)/失败(红)/警告(黄)，3秒自动消失
2. 实现Loading组件: API请求期间顶部进度条
3. 在`api.js`中统一集成Toast和Loading
4. 修复Token管理: 存储+过期检查+401跳转
5. 实验代码自动保存到localStorage（每30秒+失焦时）

**验证**:
- [ ] API请求失败时弹出红色Toast
- [ ] API请求期间显示Loading
- [ ] Token过期后自动跳转登录页
- [ ] 实验页刷新后代码不丢失

**文件变更清单**:
```
CREATE: frontend/src/components/Toast.js
CREATE: frontend/src/components/Loading.js
MODIFY: frontend/src/services/api.js (集成Toast/Loading)
MODIFY: frontend/src/services/auth.js (Token管理修复)
MODIFY: frontend/src/views/Lab.js (自动保存)
```

---

#### T5: 评测系统集成到前端 [P0, 2天]

**依赖**: T2完成

**目标**: 实验页面支持"运行"和"提交评测"两种操作

**子任务**:
1. 实验页面新增"提交评测"按钮，调用`POST /courses/labs/{id}/submit`
2. 评测结果展示区域: 分数/通过状态/逐条测试结果
3. 提示按钮: 按序展示`lab.hints`
4. 提交历史查看: 调用`GET /labs/{id}/submissions`
5. 评测通过后显示祝贺动画+自动更新进度

**验证**:
- [ ] "运行"只执行不评测，输出在"执行输出"区
- [ ] "提交评测"执行+评测，结果在"评测结果"区
- [ ] 评测通过后章节进度自动更新
- [ ] 提交历史可查看

**文件变更清单**:
```
MODIFY: frontend/src/views/Lab.js (大改)
MODIFY: frontend/src/services/api.js (新增submitAPI)
```

---

#### T6: 测试基础设施建设 [P0, 2天]

**目标**: 测试覆盖率从10%提升到40%

**子任务**:
1. 创建`conftest.py`: 测试数据库fixture、client fixture、测试用户fixture
2. 编写`test_auth.py`: 注册/登录/获取当前用户（正常+异常用例）
3. 编写`test_courses.py`: 课程列表/详情/章节（正常+异常用例）
4. 编写`test_labs.py`: 代码执行/提交评测（正常+安全+异常用例）
5. 编写`test_progress.py`: 进度查询/更新/统计
6. 编写`test_code_security.py`: 安全检查（合法代码+恶意代码）
7. 编写`test_grader.py`: 评测逻辑（语法检查+分数计算+反馈生成）

**测试重点（MVP安全关键路径）**:
```python
# 必须覆盖的安全测试用例
def test_submit_malicious_code_os_system():
    """提交import os; os.system('rm -rf /')应返回400"""
    
def test_submit_malicious_code_eval():
    """提交eval('__import__("os").system("whoami")')应返回400"""
    
def test_submit_infinite_loop():
    """提交while True: pass应超时返回错误"""
    
def test_lab_response_no_solution_code():
    """LabPublicResponse不应包含solution_code字段"""
    
def test_grader_no_exec_in_main_process():
    """验证评测不在主进程中exec用户代码"""
```

**验证**:
- [ ] `pytest --cov=app --cov-report=term-missing` 覆盖率≥40%
- [ ] 所有安全测试用例通过
- [ ] CI中`--cov-fail-under=40`不报错

**文件变更清单**:
```
CREATE: backend/tests/conftest.py
CREATE: backend/tests/test_auth.py
CREATE: backend/tests/test_courses.py
CREATE: backend/tests/test_labs.py
CREATE: backend/tests/test_progress.py
CREATE: backend/tests/test_code_security.py
CREATE: backend/tests/test_grader.py
```

---

#### T7: 端到端验证 [P0, 1天]

**依赖**: T1-T6全部完成

**目标**: 验证MVP完整流程

**验证清单**:
- [ ] 新用户注册成功
- [ ] 登录获取token
- [ ] 浏览课程列表
- [ ] 进入课程详情，看到章节和实验
- [ ] 阅读章节内容
- [ ] 进入实验，看到starter_code
- [ ] 点击"运行"，看到执行输出
- [ ] 点击"提示"，看到第1条提示
- [ ] 点击"提交评测"，看到分数和测试结果
- [ ] 评测通过后，进度页显示章节completed
- [ ] 刷新页面，进度不丢失
- [ ] Token过期后跳转登录页

---

## 九、约束与红线

### 9.1 代码约束

| # | 约束 | 原因 |
|---|------|------|
| R1 | **禁止在主进程中exec()用户代码** | 安全红线，违反即RCE |
| R2 | **禁止在API响应中返回solution_code** | 答案泄露 |
| R3 | **禁止硬编码数据库URL** | 环境不一致 |
| R4 | **禁止使用`datetime.utcnow()`** | 已弃用，用`datetime.now(timezone.utc)` |
| R5 | **禁止修改数据库schema而不创建Alembic migration** | 变更不可追溯 |
| R6 | **禁止在Service层直接返回HTTP响应** | Service返回业务对象，路由层负责HTTP |
| R7 | **所有新增API端点必须有response_model** | 自动文档+类型安全 |
| R8 | **所有新增API端点必须在测试中有对应用例** | 覆盖率保障 |

### 9.2 架构约束

| # | 约束 | 原因 |
|---|------|------|
| A1 | MVP阶段维持Vanilla JS前端 | 避免引入React增加复杂度 |
| A2 | MVP阶段维持静态方法类Service模式 | 不引入DI框架 |
| A3 | MVP阶段维持单文件models | 不拆分模型文件 |
| A4 | 代码执行只通过code_executor.py | 不再在Service中重复实现执行逻辑 |
| A5 | 安全检查只通过CodeSecurityChecker | 不再使用简单关键字匹配 |

### 9.3 不可做的事

| # | 禁止 | 原因 |
|---|------|------|
| N1 | 不要引入React/Vue/Angular | MVP阶段Vanilla JS够用 |
| N2 | 不要引入Celery/RabbitMQ | MVP阶段同步执行够用 |
| N3 | 不要引入MinIO/S3 | MVP阶段无需对象存储 |
| N4 | 不要实现证书PDF生成 | P2功能 |
| N5 | 不要实现讨论区增强 | P1功能 |
| N6 | 不要实现管理后台 | P3功能 |
| N7 | 不要修改课程内容 | 课程内容已100%完成 |
| N8 | 不要修改Docker沙箱的runner.py | 现有沙箱逻辑可用 |

---

## 十、与现有文档的关系

| 本文档章节 | 对应 | 其他文档 |
|-----------|------|---------|
| §1-2 概述+架构 | 替代 | 原DESIGN.md §1-2 |
| §3 数据库 | 替代 | 原DESIGN.md §3 |
| §4 API | 替代 | AGENTS.md §3（API端点） |
| §5 业务逻辑 | 替代 | 无（原有文档无此内容） |
| §6 安全 | 替代 | 原DESIGN.md §4 |
| §7 前端 | 替代 | 无（原有文档无此内容） |
| §8 任务拆解 | 替代 | 原DESIGN.md §6 + TASKS.md |
| §9 约束红线 | 新增 | 无 |
| 课程内容 | 不涉及 | 原DESIGN.md §5（已100%完成） |
| 开发流程 | 不涉及 | DEVELOPMENT_HARNESS.md |
| 产品定义 | 不涉及 | PRD_v2.md |

---

**文档版本**: 2.0
**创建日期**: 2026-05-13
**基于代码版本**: 当前main分支
**下一步**: 按§8任务拆解顺序执行MVP开发
