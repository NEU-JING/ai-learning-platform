# AGENTS.md — AI Learning Platform 开发指引

> 本文件是所有 AI Agent 在本项目开发时必须遵循的入口文件。
> 详细规范见 DEVELOPMENT_HARNESS.md 和 DESIGN.md。

## 快速启动

```bash
cd backend
source /tmp/ailp-venv/bin/activate
SERVE_STATIC=True uvicorn app.main:app --host 0.0.0.0 --port 8000   # 启动后端
pytest tests/ -v                                                     # 跑测试（78个）
pytest tests/test_data_contract.py -v                                # 跑数据契约测试（16项）
```

- venv: `/tmp/ailp-venv` (Python 3.11)
- 前端: 静态文件由后端 `SERVE_STATIC=True` 直接服务
- 数据库: MVP用SQLite，Schema兼容PostgreSQL
- 服务器: 当前2核4G（推荐升级4核8G+80GB以支持Docker沙箱）

## 🚨 红线规则（违反即视为bug）

### 0. 编码后必须评审（post-coding-review skill）
- 编码agent完成代码+单元测试后，**提交前必须执行标准化评审**
- 评审流程：Phase 1 自动化检查 → Phase 2 独立评审 → Phase 3 复审验证
- 没有通过评审的代码**禁止commit**
- 详见 `skill_view(name='post-coding-review')`

### 1. 前后端契约同步（DEVELOPMENT_HARNESS.md §4.7）
- **后端Pydantic schema字段名 = 前端消费的字段名**，必须完全一致（包括单复数）
- 修改schema字段名时，**同一commit**中必须 `grep -rn "old_field_name" frontend/` 并同步更新
- 禁止前端自行"翻译"字段名（如 `chapters_count` → `chapter_count`）
- 新增API端点必须在 §4.7.3 API契约注册表中登记

### 2. response_model一致性（DEVELOPMENT_HARNESS.md §4.8）
- `response_model` 必须与函数实际返回类型严格一致
- 分页端点用 `PaginatedResponse[T]`，禁止声明 `List[T]` 后返回dict
- 修改端点返回逻辑后必须 `pytest` 验证——不一致会暴露为 `ResponseValidationError`

### 3. 契约测试必须覆盖（DEVELOPMENT_HARNESS.md §5.6）
- 新增/变更API端点 → 必须在 `tests/e2e/test_contract.py` 添加断言
- 契约测试失败 = 前后端不一致 = 禁止合并

### 4. Schema变更影响评估（DEVELOPMENT_HARNESS.md §4.7.2）
修改任何Pydantic响应schema时，必须逐项确认：
1. 变更类型：新增/修改字段名/修改类型/删除字段
2. 影响的前端文件路径
3. 前端已同步修改
4. 是否Breaking Change
5. 契约测试已更新

### 5. 🚨 修改前端文件后必须冒烟验证
- 修改 `frontend/` 下任何 JS/CSS/HTML 文件后，**必须执行前端冒烟测试**
- 冒烟测试命令：`npx playwright test tests/e2e/smoke.spec.js`
- 冒烟测试检查项：
  1. 核心页面正常加载（`/`、`/#/courses`、`/#/login`、`/#/register`）
  2. 页面加载后 **浏览器控制台无 `console.error` 或 JS 运行时异常**
  3. 页面 title 符合预期
- 冒烟失败 = 前端损坏 = **阻塞提交**，必须先修复

### 6. 数据契约不可违反 🚨
- **启动断言**：`_assert_data_contract(db)` 在lifespan中执行，违反则服务拒绝启动
- **契约测试**：`tests/test_data_contract.py` 16项断言，CI门禁
- **init行为**：Phase 1/2 用 `upsert`（JSON为真相源），Phase 3-6 用 `create_only`（DB为真相源）
- 修改种子数据时，必须确保 `_assert_data_contract()` 和 `test_data_contract.py` 通过

## 项目结构

```
backend/app/
├── api/v1/          # 路由层：只做参数校验和调用Service
├── core/            # 配置、数据库、安全、缓存
├── models/          # SQLAlchemy ORM模型
├── schemas/         # Pydantic请求/响应模型（唯一真相源）
├── services/        # 业务逻辑
└── data/            # 种子数据（6阶段课程体系）
    ├── courses.py            # PHASE_TITLES + 课程壳 + 孤例清理
    ├── courses_phase1.py     # Phase 1 (upsert, JSON为真相源)
    ├── courses_phase2.py     # Phase 2 (upsert, JSON为真相源)
    ├── courses_phase3_6.py   # Phase 3-6 (create_only, DB为真相源)
    ├── courses_extended_fixed.py  # Phase 3-6 种子数据
    ├── phase1/               # Phase 1 JSON内容
    └── phase2/               # Phase 2 JSON内容
frontend/
├── src/             # SPA版（ES Modules, Router, Store）
├── js/              # 传统版（多页面）
└── *.html           # 页面
sandbox/
├── Dockerfile       # Docker沙箱镜像
└── runner.py        # 沙箱内代码执行器
```

## 已知Quirk

- **JWT sub必须string**: python-jose按RFC 7519要求sub是string，传int导致decode返回None
- **bcrypt<5.0**: bcrypt 5.0+默认禁止>72字节密码
- **SQLite内存DB测试需StaticPool**: 普通`sqlite://`每个连接是独立空DB
- **登录用email**: UserLogin schema要求email字段，不是username
- **注册不返token**: 返回UserResponse，前端需走登录流程
- **课程列表返回PaginatedResponse**: 统一结构 `{items, total, page, ...}`，前端取 `.items`
- **courses_extended_fixed.py不可直接pop**: `init_phase3_6_data` 用 `copy.deepcopy()` 防止 `pop("chapters")` 破坏模块级数据
- **Phase 3-6 DB为真相源**: 种子文件 `courses_extended_fixed.py` 内容可能落后于DB中的手动深化数据，`create_only`行为保护DB内容
- **Redis缓存需手动清理**: 修改种子数据后可能需要 `redis-cli FLUSHDB`，lifespan中已有自动清理但Redis不可用时不报错

## 关键文档索引

| 文档 | 内容 |
|------|------|
| `DEVELOPMENT_HARNESS.md` | 全流程开发规范（分支、需求、设计、测试、CI） |
| `DESIGN.md` | 技术架构、数据库、API定义（含§4.1.1契约红线） |
| `PRD.md` | 产品需求定义 |
| `README.md` | 项目概览 |
