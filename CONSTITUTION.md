# CONSTITUTION.md — AILP（AI Learning Platform）

> 项目宪法：不可违背的核心原则。SDD 编排器在每个阶段检查合规性。

---

## 代码原则

1. **TDD 强制**：所有功能代码必须先写测试（R3，不可禁用）
2. **测试自包含**：测试不依赖预置数据或外部状态（R6，不可禁用）
3. **Pre-commit 强制**：push 前必须通过 format + lint（R8，不可禁用）
4. **编码后必须评审**：代码完成 + 单元测试后，提交前必须执行 post-coding-review 三阶段评审。未通过评审的代码禁止 commit。

---

## 架构原则

1. **简洁优先**：能用简单方案解决的不引入复杂方案（YAGNI）
2. **模块化**：backend/app/ 下分层清晰（api → services → models → schemas → data）
3. **Pydantic Schema 为唯一真相源**：前端字段名必须与后端 Schema 字段名完全一致（R5）

---

## 协作原则

1. **文档驱动**：先写 Spec，再写代码（R1）
2. **增量提交**：每 Task 一个 commit，可独立 review
3. **前后端契约同步**：修改 Schema 字段名时，同一 commit 必须同步前端引用
4. **Schema 变更影响评估**：修改 Pydantic 响应 Schema 时必须逐项确认变更类型、影响前端文件、是否 Breaking Change

---

## 项目特有约束

### AILP-001: 数据契约不可违反（CRITICAL）

- 启动断言 `_assert_data_contract(db)` 在 lifespan 中执行，违反则服务拒绝启动
- 契约测试 `tests/test_data_contract.py`（16 项断言）为 CI 门禁
- Phase 1/2 使用 `upsert`（JSON 为真相源），Phase 3-6 使用 `create_only`（DB 为真相源）
- 修改种子数据时，必须确保启动断言和契约测试全量通过

### AILP-002: Phase 3-6 数据保护（CRITICAL）

- `courses_phase3_6.py` 使用 `create_only` 行为，只创建不覆盖
- Phase 3-6 深度内容仅存在于 DB 中，不可被种子数据覆盖
- 修改 `backend/app/data/` 时，IRB（内部评审委员会）必须确认未破坏 create_only 逻辑

### AILP-003: 前端修改必冒烟

- 修改 `frontend/` 下任何文件后，必须执行前端冒烟测试
- 冒烟测试检查核心页面加载、控制台无 JS 异常、页面 title 正确
- 冒烟失败 = 前端损坏 = 阻塞提交

### AILP-004: response_model 一致性

- `response_model` 必须与函数实际返回类型严格一致
- 分页端点用 `PaginatedResponse[T]`，禁止声明 `List[T]` 后返回 dict
- 修改端点返回逻辑后必须 `pytest` 验证
