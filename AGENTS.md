# AGENTS.md — AILP 开发指引（Harness 感知版）

> 本文件是所有 AI Agent 在本项目开发时必须遵循的入口文件。
> 详细规范见 DEVELOPMENT_HARNESS.md 和 DESIGN.md。

## ⚠️ 开始任何工作前

1. **读取 CONSTITUTION.md** — 项目最高准则，不可违反
2. **读取 QUIRKS.md** — 已知陷阱，搜索是否已有相同问题
3. 如需新功能，按 SDD 流程执行（见 `docs/AILP-DEVELOPMENT-FLOW.md`）

## 🔄 标准开发流程（SDD V2.0）

```
完整流程：PRD → 👤确认 → Spec → 👤确认 → Design → Tasks → Implement → Review → QA → 👤验收 → 归档

关键门禁：
  · PRD 完成后 → 👤 用户确认（方向性决策）
  · Spec 完成后 → 👤 用户确认（行为契约）
  · QA 通过后 → 👤 人工验收（需求/设计/代码三级分类打回）
  · QA 失败 ≤4 轮 → 自动返回 Coder 修复
  · QA 第 5 轮仍失败 → 👤 熔断，等待用户决策
```

详见 `docs/AILP-DEVELOPMENT-FLOW.md`。

## 🤖 多 Agent 协作角色

| 角色 | Agent | 输入 | 输出 |
|------|-------|------|------|
| 需求分析 | PM Agent | 用户需求 + CONSTITUTION | spec.md |
| 技术设计 | Architect Agent | spec.md + 代码结构 | plan.md + tasks.md |
| 编码实现 | Coder Agent | tasks.md + plan.md | 代码 + 测试 |
| 代码审查 | Reviewer Agent | 代码 diff + spec.md | 评审报告 |
| 质量保证 | QA Agent | 代码 + spec.md | QA 报告 |

**委派 Agent 时必须提供**：spec.md + plan.md + tasks.md + CONSTITUTION.md

## 🚨 红线规则（违反即 Block）

### 0. 没有 Spec 不写代码（Quick Flow 除外）
- 新功能必须先 /specify，产出 spec.md
- Spec 必须通过 ailp-spec-linter 检查
- Spec 必须通过 AI Spec Reviewer（Standard/Enhanced）

### 1. 编码前 Brainstorming（Standard/Enhanced）
- 收到需求后先探索替代方案，不直接写代码
- 详见 `skill_view(name='ailp-brainstorming')`

### 2. TDD 强制
- 先写测试，后写实现。红 → 绿 → 重构
- 每个 task 都按此循环执行

### 3. 编码后必须评审
- post-coding-review 三阶段评审
- Phase 1 自动化 → Phase 2 独立 Agent → Phase 3 回归
- 详见 `skill_view(name='post-coding-review')`

### 4. 前后端契约同步
- 后端 Pydantic schema 字段名 = 前端消费字段名
- 修改 schema → 同一 commit 同步前端引用
- 新增 API → 契约测试覆盖

### 5. 前端修改必冒烟
- 修改 frontend/ 文件 → Playwright 冒烟测试
- 冒烟失败 = 阻塞提交

### 6. 数据契约不可违反
- 启动断言 `_assert_data_contract(db)`
- 契约测试 16 项 CI 门禁
- Phase 1/2 upsert，Phase 3-6 create_only

## 📁 文档结构

```
docs/
├── specs/       ← /specify 产出，按功能名命名
├── plans/       ← /plan 产出
├── tasks/       ← /tasks 产出
├── design-notes/← brainstorming 产物
└── learnings/   ← Stop Hook 学习日志

模板文件：docs/{specs,plans,tasks}/_TEMPLATE.md
```

## 🔧 快速启动

```bash
cd backend
source /tmp/ailp-venv/bin/activate
SERVE_STATIC=True uvicorn app.main:app --host 0.0.0.0 --port 8000
pytest tests/ -v                                    # 全量测试
pytest tests/test_data_contract.py -v               # 契约测试
```

- venv: `/tmp/ailp-venv` (Python 3.11)
- 前端: 静态文件由后端 `SERVE_STATIC=True` 直接服务
- 数据库: MVP 用 SQLite，Schema 兼容 PostgreSQL

## 项目结构

```
backend/app/
├── api/v1/          # 路由层：参数校验 → Service 调用
├── core/            # 配置、数据库、安全、缓存
├── models/          # SQLAlchemy ORM
├── schemas/         # Pydantic（唯一真相源）
├── services/        # 业务逻辑
└── data/            # 种子数据（6 阶段课程体系）
frontend/
├── src/             # SPA 版（优先）
├── js/              # 传统版（维护）
└── *.html
sandbox/
├── Dockerfile
└── runner.py
```
