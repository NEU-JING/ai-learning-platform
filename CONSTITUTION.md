# AILP 项目宪法（Constitution）

> 本文件是 AILP 项目的最高准则。所有 AI Agent 在开始任何工作前必须读取。
> 违反本宪法的代码不得提交。本宪法本身可被修订，但修订必须经过人类确认。

---

## 一、架构原则

### 1.1 分层不可跨越
- `api/` → `services/` → `models/`。路由层只做参数校验和 Service 调用，不写业务逻辑。
- Service 层不直接操作 `Request` 对象，通过参数接收数据。
- Model 层不包含业务逻辑，仅定义数据结构。

### 1.2 Schema 是唯一真相源
- Pydantic schema 定义 = 前端消费的数据结构。字段名（含单复数）必须完全一致。
- 禁止前端自行"翻译"字段名（如 `chapters_count` → `chapter_count`）。
- 修改 Schema 字段名时，同一 commit 必须同步更新前端引用。

### 1.3 数据迁移必须可追溯
- 数据库 Schema 变更必须通过 Alembic 迁移脚本。
- 禁止手动改表结构（`ALTER TABLE`）。
- 迁移脚本必须可回滚（`downgrade()` 非空）。

### 1.4 前端 SPA 优先
- 新增页面默认使用 SPA 版本（`frontend/src/`）。
- 传统多页面版本（`frontend/js/`、`frontend/*.html`）仅维护，不新增。

---

## 二、质量原则

### 2.1 TDD 强制
- 先写测试，后写实现。流程：红（写失败测试）→ 绿（写最小实现）→ 重构。
- 新增 API 端点 = 新增契约测试。
- 无测试的代码不得合并。

### 2.2 前端修改必冒烟
- 修改 `frontend/` 下任何文件后，必须执行 Playwright 冒烟测试。
- 冒烟测试覆盖：`/`、`/#/courses`、`/#/login`、`/#/register`。
- 冒烟失败 = 阻塞提交，不论后端测试是否全绿。

### 2.3 数据契约不可违反
- 启动时 `_assert_data_contract(db)` 执行，违反则服务拒绝启动。
- 契约测试（`tests/test_data_contract.py`）在 CI 中强制运行。
- Phase 1/2 数据 `upsert`（JSON 为真相源），Phase 3-6 数据 `create_only`（DB 为真相源）。

### 2.4 代码评审强制
- 所有代码变更必须通过 post-coding-review 三阶段评审。
- Phase 1 自动化检查（lint/format/安全/测试）→ Phase 2 独立 Agent 审查 → Phase 3 回归验证。
- BLOCKER 或 CRITICAL 问题未修复 → 禁止提交。

---

## 三、安全原则

### 3.1 用户输入必校验
- 所有请求体通过 Pydantic schema 校验。
- 禁止信任前端传来的数据（即使是下拉选项也要服务端校验）。

### 3.2 SQL 必参数化
- 使用 SQLAlchemy ORM 或参数化查询。
- 禁止字符串拼接 SQL（含 f-string 构建 SQL）。

### 3.3 密钥不入代码
- API Key、Secret、Password 通过环境变量注入。
- `.env.example` 只包含模板，不包含真实值。
- 提交前自动扫描硬编码密钥（post-coding-review Phase 1）。

### 3.4 沙箱安全
- 沙箱内代码执行必须受白名单模块限制。
- 禁用网络访问、文件系统写权限（除指定目录）。
- 每次执行有资源限制（CPU 时间、内存、超时）。

---

## 四、AI 协作原则

### 4.1 没有 Spec 不写代码
- 新功能必须先写 spec.md，后写代码（Quick Flow 除外）。
- Spec 必须包含可测试的验收标准（Given-When-Then 格式）。
- Spec 必须通过 Constitution Check（与本宪法不冲突）。

### 4.2 Brainstorm 先于 Build
- 收到需求后先探索替代方案，不直接写代码。
- 至少考虑 2 种方案，有 trade-off 分析。
- Quick Flow 免除，Standard/Enhanced 强制执行。

### 4.3 从错误中学习
- 每次踩坑后更新 `QUIRKS.md`。
- 发现可复用的解决方案 → 创建或更新 Skill。
- 架构级发现 → 提议修订本宪法。

### 4.4 生产代码禁 Mock 数据
- 数据来源于数据库或种子文件，禁止硬编码演示数据。
- 演示/示例数据仅在测试代码中使用。

---

## 五、技术栈约束

| 层级 | 选择 | 约束 |
|------|------|------|
| 后端 | FastAPI + Python 3.11 | 禁止引入新的 Web 框架 |
| 前端 | Vite + React 18 | SPA 用 React，禁止引入 Vue/Angular |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） | Schema 兼容，Alembic 管理迁移 |
| 缓存 | Redis | 非必需功能可降级运行 |
| AI 推理 | Ollama 本地 | 不可用时降级，不阻塞核心功能 |
| 沙箱 | Docker（优先）/ Subprocess（回退） | 安全白名单必须生效 |

---

*本文档为 AILP 项目最高准则。修订需人类确认。最后更新：2026-05-21。*
