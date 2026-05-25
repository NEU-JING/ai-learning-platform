# AILP SDD 工作流改进报告

> 基于「公开能力主页」试点（001-public-profile）全流程复盘
> 覆盖：SDD V2.0 → V2.1 演进、6 轮 CI 修复、E2E 从 3 条冒烟到 12 AC 全覆盖的完整历程

---

## 一、当前存在的问题分析

### 1.1 流程设计层面

| # | 问题 | 根因 | 改进意见 |
|---|------|------|---------|
| P1 | **文档结构混乱**：PRD/Spec/Design 最初混在一个目录，无清晰层次 | SDD 概念在设计时未映射到目录结构 | 已修复：`docs/changes/XXX-name/{prd,spec,design,tasks}.md`。需固化到 `ailp-sdd-workflow` skill |
| P2 | **Spec 含技术设计泄漏**：BA Agent 产出的 spec.md 描述了 API 端点和技术方案 | 缺少 Spec Linter 的内容净化检查 | `ailp-spec-linter` 增加**技术词汇检测规则**（如"API 端点""数据库表""Redis"等出现在 Spec 中即告警） |
| P3 | **缺少 PRD 阶段**：最初流程从 Spec 开始，跳过了 Why+What | SDD V1 只定义了 Spec→Design→Code | 已在 V2.0 修复：PRD(PO)→Spec(BA)→Design(Architect)。需确保 `ailp-flow-level` 不会被 Quick Flow 跳过 PRD |
| P4 | **User Confirmation Gates 缺失**：最初 PRD/Spec 产出后没有用户确认点，直接推进 | 流程设计中"用户"角色被隐含为"需求提供者"而非"门禁决策者" | 已在 V2.1 修复：PRD→👤确认→Spec→👤确认→Design。需在 `ailp-sdd-workflow` 中强制标记门禁不可跳过 |
| P5 | **Tasks 首次拆分按技术层次而非业务场景**：第一次是"数据库层→API层→前端层" | Architect Agent 默认按技术栈分层，未被告知业务场景优先原则 | 在 `ailp-sdd-workflow` skill 的 Tasks 阶段说明中增加**强制规则**：每个 Task 必须是可独立上线的业务场景，禁止按技术层次拆分 |
| P6 | **Brainstorming 在错误阶段**：最初设计放在 Spec 阶段（探索替代方案时混入了行为定义） | 角色边界不清——BA Agent 做了 Architect 的事 | 已在 V2.0 修复：Brainstorming 移到 Design 阶段。需在角色定义中明确**禁止跨阶段行为** |

### 1.2 代码交付层面

| # | 问题 | 根因 | 改进意见 |
|---|------|------|---------|
| P7 | **本地未 format 就 push**：black/isort/ruff 在 CI 挂了 6 轮，每轮修复一个新问题 | 没有 pre-commit hook，完全依赖 CI 反馈 | **P0: 添加 pre-commit hook**（见 §4.3） |
| P8 | **ruff auto-fix 误删 `import pytest`**：ruff `--fix` 删了"未使用的 import"，但后续代码通过 `pytest.mark.skipif` 又需要它 | 自动修复无人审查 diff | **post-coding-review Phase 1 增加 `git diff --staged` 审查步骤** |
| P9 | **E2E 测试依赖本地 DB 状态**：测试用户（e2e_public 等）在本地 DB 中有数据，CI 全新 SQLite 中没有 | E2E 编写时假设测试数据已存在，未设计种子机制 | **P0: 创建 E2E Authoring Skill**（见 §4.2） |
| P10 | **AC12 并发测试在 SQLite 失败但未标记 skip**：SQLite 不支持并发读写，但测试没有 `skipif` | 测试编写者未考虑 CI 环境差异（CI parity 未声明） | 在 AGENTS.md 增加 **CI Parity Rule**：所有测试必须在 SQLite 和 PostgreSQL 双环境通过（或显式 skipif） |
| P11 | **QA 报告声称 E2E 全覆盖，实际只有 3 条冒烟**：QA Agent 只验证了单元测试列表，未逐条核对 AC 与 E2E 用例的映射 | QA skill 缺少 E2E-AC 覆盖矩阵检查 | **QA skill 增强**：增加 `_verify_e2e_ac_coverage()` 步骤（见 §4.2） |
| P12 | **CRITICAL 遗漏（埋点/可观测性）**：Reviewer 发现了 Design 文档要求的埋点事件 + 审计日志未实现 | Coder Agent 只关注功能实现，忽略了非功能需求（NFR） | 在 `tasks.md` 模板中增加 **NFR Checklist**，Coder 在每个 Task 完成时必须勾选 |
| P13 | **直接 push main 不触发 CI**：`e2e-smoke.yml` 是 `pull_request` trigger，push 到 main 不会执行 | AGENTS.md 缺少 push 前检查清单和 CI trigger 说明 | 在 AGENTS.md 增加 **Push 前检查清单**（见 §4.1） |

### 1.3 Agent 协作层面

| # | 问题 | 根因 | 改进意见 |
|---|------|------|---------|
| P14 | **模型路由不稳定**：Coder Agent 用 flash 模型导致代码质量波动，复杂任务用错模型 | `model-router` skill 只定义了调研/编码/股票场景，缺少编码场景子任务的模型选择规则 | **细化 model-router**：编码场景下 Tasks → Implement 必须用 pro/GLM 模型，Review/QA 用 pro |
| P15 | **委派 Agent 输入不完整**：QA Agent 收到的上下文缺少 E2E 文件路径列表，导致只检查了单元测试 | `delegate_task` context 字段由人工填写，容易遗漏 | 在 `ailp-sdd-workflow` 中定义**每个阶段的委派上下文模板**（文件列表、前置产物路径） |
| P16 | **单并发限制下任务积压**：千帆模型限并发 1，多 Task 排队导致总耗时线性叠加 | 架构约束（千帆 API 限制），无法绕过 | 非千帆阶段（PRD/Spec/Design）用对话模型并行产出；千帆仅用于 Implement 阶段 |

---

## 二、多角色 Agent 定义

### 2.1 当前定义（AGENTS.md）

| 角色 | Agent | 输入 | 输出 |
|------|-------|------|------|
| 需求分析 | PM Agent | 用户需求 + CONSTITUTION | spec.md → **错误：实际是 PRD** |
| 技术设计 | Architect Agent | spec.md + 代码结构 | plan.md + tasks.md |
| 编码实现 | Coder Agent | tasks.md + plan.md | 代码 + 测试 |
| 代码审查 | Reviewer Agent | 代码 diff + spec.md | 评审报告 |
| 质量保证 | QA Agent | 代码 + spec.md | QA 报告 |

**问题**：
1. 缺少 **PO Agent**（PRD 产出者）——PM Agent 被错误地指向 spec.md
2. 缺少 **BA Agent**（Spec 产出者）——行为定义环节无人负责
3. 角色与 SDD 阶段不对齐——PM→PRD、BA→Spec、Architect→Design 的映射未体现
4. 缺少各角色的**禁止行为清单**（如 BA 不能写技术方案）

### 2.2 修正后的角色定义

| 阶段 | 角色 | 模型 | 职责 | 禁止行为 |
|------|------|------|------|---------|
| **PRD** | **PO Agent** | Flash | Why + What + 用户故事 + 成功指标 | ❌ 不能写任何技术方案、API 设计、数据库表 |
| **Spec** | **BA Agent** | Flash/Pro | 行为契约：Given-When-Then AC + 业务规则 + 错误文案 | ❌ 不能写任何技术实现、API 端点、数据模型 |
| **Design** | **Architect Agent** | Pro/GLM | 技术方案对比（Brainstorming ≥2 方案）+ 推荐方案 + 接口定义 + 数据模型 + 安全审计 | ❌ 不能修改 AC 或业务规则 |
| **Tasks** | **Architect Agent** | Pro/GLM | 按业务场景拆分 Task + 估时 + 依赖关系 | ❌ 不能按技术层次拆分（如"数据库层→API层→前端"） |
| **Implement** | **Coder Agent** | GLM | TDD：测试→实现→重构，每个 Task 独立可上线 | ❌ 不能跳过测试直接写实现 |
| **Review** | **Reviewer Agent** | Pro | 三阶段：自动化→独立审查→回归 | ❌ 不能只检查代码风格，必须对照 Design 和 NFR |
| **QA** | **QA Agent** | Pro | E2E 运行 + AC 覆盖矩阵 + 环境差异标记 | ❌ 不能只在本地跑测试；必须验证 CI 通过 |
| **验收** | **用户（人）** | — | 需求/设计/代码三级分类打回 | — |

### 2.3 委派协议

每个 Agent 委派时必须提供：
```yaml
delegate_context:
  role: "Coder Agent"
  inputs:
    - spec.md        # 行为契约
    - design.md      # 技术方案
    - tasks.md       # 当前 Task 描述
    - CONSTITUTION.md # 项目宪法
    - QUIRKS.md      # 已知陷阱
  task_id: "T3"      # 当前执行的 Task 编号
  output_paths:       # 预期产出文件清单
    - backend/app/...
    - backend/tests/...
  nfr_checklist:      # 非功能需求检查清单
    - 埋点事件
    - 审计日志
    - 性能要求
```

---

## 三、Agent 协同工作流方案

### 3.1 当前流程（SDD V2.1，已落地）

```
PRD(PO) → 👤确认 → Spec(BA) → 👤确认 → Design(Architect) → Tasks → Implement(TDD) → Review(三阶段) → QA → 👤验收 → 归档
                                    ↑ Brainstorming ↑
```

**试点验证结果**：流程骨架正确，8 阶段走通，001-public-profile 成功交付。

### 3.2 暴露的缺口与修正

| 缺口 | 当前状态 | 修正方案 |
|------|---------|---------|
| **Pre-push Gate** | 不存在 | 新增 pre-commit hook：black + isort + ruff（仅变更文件），pre-push hook：全量 pytest |
| **E2E 门禁** | CI 只在 PR 时跑 smoke | E2E CI 已升级为全量 12 AC；补充 `e2e-smoke.yml` push trigger（除 PR 外，push 到 feature 分支也触发） |
| **Implementation 检查点** | 无 | 每个 Task 完成后，Coder 必须输出 Task Completion Report（测试数、AC 覆盖、NFR Checklist 勾选状态） |
| **QA-AC 覆盖强制验证** | QA Agent 跳过 | QA skill 增加 `_verify_e2e_ac_coverage()`：逐条读取 spec.md 的 AC，在 E2E 文件中搜索对应用例，输出缺失列表 |
| **熔断后决策模板** | QA 5 轮失败后无结构化输出 | `ailp-qa-circuit-breaker` 补充熔断报告模板：失败分类（需求/设计/代码/环境）+ 每类建议动作 |
| **归档门禁** | 缺少 | 新增归档条件：CI 全绿 + E2E CI 全绿 + QA 报告已生成 + 用户验收通过 |

### 3.3 角色交接协议

每个阶段产出后，向下游 Agent 传递**交接包**：

```
交棒方 → 产物文件 + 交接清单 → 接棒方
```

| 交接 | 产物 | 交接清单 |
|------|------|---------|
| PO → BA | prd.md | 用户故事清单、成功指标、非目标声明 |
| BA → Architect | spec.md | AC 清单（含编号）、业务规则清单（BR1-BRn）、错误文案清单 |
| Architect → Coder | design.md + tasks.md | 当前 Task 描述、依赖关系、文件清单、NFR Checklist |
| Coder → Reviewer | 代码 diff + Task Completion Report | 测试数、AC 覆盖状态、NFR 勾选 |
| Reviewer → QA | 代码 diff + 评审报告 | CRITICAL/WARNING/INFO 分级、修复建议 |
| QA → 用户 | qa-report.md + AC 覆盖矩阵 | 通过/失败/跳过分类、环境差异标记、E2E 运行记录 |

---

## 四、Harness 工程方案

### 4.1 Rules（规则层）

**4.1.1 当前 Rules（AGENTS.md + CONSTITUTION.md）**

| 规则 | 来源 | 状态 |
|------|------|------|
| 没有 Spec 不写代码 | AGENTS.md 红线 #0 | ✅ 已执行 |
| 编码前 Brainstorming | AGENTS.md 红线 #1 | ✅ 已执行 |
| TDD 强制 | AGENTS.md 红线 #2 | ✅ 已执行 |
| 编码后必须评审 | AGENTS.md 红线 #3 | ✅ 已执行 |
| 前后端契约同步 | AGENTS.md 红线 #4 | ✅ 已执行 |
| 前端修改必冒烟 | AGENTS.md 红线 #5 | ⚠️ 冒烟仅 3 条，已升级为全量 E2E |
| 数据契约不可违反 | AGENTS.md 红线 #6 | ✅ 已执行 |
| 分层不可跨越 | CONSTITUTION 1.1 | ✅ 已执行 |
| Schema 是唯一真相源 | CONSTITUTION 1.2 | ✅ 已执行 |

**4.1.2 需要新增的 Rules**

| # | 新规则 | 说明 |
|---|--------|------|
| **R7** | **Push 前必过 Pre-commit** | black + isort + ruff（变更文件），失败禁止 push |
| **R8** | **测试自包含原则** | 所有测试（单元/集成/E2E）必须在全新 DB 中独立运行，不依赖预置数据 |
| **R9** | **CI Parity Rule** | 所有测试必须在 SQLite 和 PostgreSQL 双环境通过；不支持的显式 `skipif` |
| **R10** | **E2E-AC 一一对应** | 每个 E2E 用例必须标注对应的 AC 编号；QA 阶段验证映射完整性 |
| **R11** | **Task Completion Report** | Coder 完成每个 Task 后必须输出结构化报告（测试数、AC 覆盖、NFR 勾选） |
| **R12** | **PR 不直接 push main** | 任何涉及 `.github/workflows/` 或新增功能的变更，必须走 PR 流程 |

### 4.2 Skills（技能层）

**4.2.1 现有 Skills（26 个，software-development 分类）**

核心流程 skills 已覆盖：`ailp-sdd-workflow`、`ailp-spec-linter`、`ailp-brainstorming`、`ailp-flow-level`、`post-coding-review`、`ailp-qa-circuit-breaker`、`frontend-backend-contract`、`code-execution-sandbox`

**4.2.2 需要创建/增强的 Skills**

| Skill | 动作 | 说明 |
|-------|------|------|
| **`e2e-authoring`** | 🆕 新建 | E2E 编写规范：种子数据自包含、AC 映射标注、CI 种子步骤、login flow 使用 page context API、禁止依赖本地 DB |
| **`post-coding-review`** | 🔧 增强 | Phase 1 增加 `git diff --staged` 审查 + format 检查（black/isort/ruff） |
| **`ailp-spec-linter`** | 🔧 增强 | 增加技术词汇检测规则（API 端点、数据库表、Redis 等关键词在 Spec 中出现时告警） |
| **`ailp-qa-circuit-breaker`** | 🔧 增强 | 增加 E2E-AC 覆盖矩阵验证 + 熔断报告模板 |
| **`model-router`** | 🔧 增强 | 增加编码场景子任务模型选择规则：Tasks/Implement → GLM，Review/QA → Pro |
| **`ailp-sdd-workflow`** | 🔧 增强 | 增加委派上下文模板、交接协议、Task Completion Report 模板 |
| **`git-workflow`** | 🆕 新建 | PR 流程 + pre-commit hook 配置 + push 前检查清单 |
| **`ci-parity`** | 🆕 新建 | SQLite/PostgreSQL 双环境测试策略 + `skipif` 标记规范 |

### 4.3 Hooks（钩子层）

**当前状态**：完全空白。项目无任何 Git hooks。

**落地方案**：

```bash
# .git/hooks/pre-commit（或 .pre-commit-config.yaml）
- black --check（变更文件）
- isort --check-only（变更文件）
- ruff check --select=E,W,F（变更文件）

# .git/hooks/pre-push
- cd backend && pytest tests/ -x -q  # 全量回归
```

使用 `pre-commit` 框架管理，配置写入 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        args: [--check]
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--check-only]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.1
    hooks:
      - id: ruff
        args: [--select, E,W,F]
```

**额外 Hook 建议**：

| Hook | 触发时机 | 作用 |
|------|---------|------|
| **post-commit** | commit 后 | 更新 QUIRKS.md（如果本次修复了陷阱） |
| **pre-push** | push 前 | 运行全量 pytest + E2E smoke（本地环境） |
| **CI post-merge** | merge 到 main 后 | 自动归档 `docs/changes/` → `docs/archive/`、更新 `current/` |

---

## 五、落地方案及计划

### 5.1 优先级矩阵

| 优先级 | 项目 | 预计耗时 | 依赖 | 预期收益 |
|--------|------|---------|------|---------|
| **P0** | Pre-commit hooks（black + isort + ruff） | 0.5h | 无 | 消灭 CI format 轮次 |
| **P0** | E2E Authoring Skill（`e2e-authoring`） | 1h | 无 | 后续所有 E2E 质量基准 |
| **P0** | AGENTS.md 补充（push 前清单 + CI parity + 测试自包含） | 0.5h | 无 | 新 Agent 入场的默认行为 |
| **P1** | post-coding-review 增强（format 检查 + diff 审查） | 0.5h | P0 hooks | 评审阶段自动拦截 format 问题 |
| **P1** | ailp-spec-linter 增强（技术词汇检测） | 0.5h | 无 | 阻止 Spec 泄漏技术实现 |
| **P1** | QA skill 增强（E2E-AC 覆盖验证） | 1h | P0 E2E skill | 消灭 QA 报告的 E2E 盲区 |
| **P2** | 角色定义修正（AGENTS.md 角色表更新） | 0.5h | 无 | 厘清 PO/BA/Architect 边界 |
| **P2** | ailp-sdd-workflow 增强（委派模板 + 交接协议） | 1h | P2 角色定义 | Agent 委派不再遗漏上下文 |
| **P2** | model-router 增强（编码子任务模型选择） | 0.5h | 无 | 减少模型选择错误导致的重做 |
| **P2** | Git hooks pre-push（pytest + E2E smoke） | 1h | P0 hooks | 本地即可发现 regression |
| **P3** | ci-parity skill（双环境测试策略） | 1h | 需 PostgreSQL CI 环境 | AC12 等并发测试不再 skip |
| **P3** | E2E CI push trigger 补充 | 0.5h | 无 | push 到 feature 分支也能触发 E2E |

### 5.2 分阶段执行计划

#### Sprint 1: Foundation（P0，共 2h）

```
目标：消灭最高频的流程浪费
产出：
  1. .pre-commit-config.yaml（black + isort + ruff）
  2. e2e-authoring skill（SKILL.md）
  3. AGENTS.md 补充（3 条新规则）
验证：
  - CI format 检查一次通过
  - 新 E2E 测试遵循自包含规范
```

#### Sprint 2: Defense（P1，共 3h）

```
目标：增强评审和 QA 的拦截能力
产出：
  1. post-coding-review Phase 1 增强
  2. ailp-spec-linter 技术词汇检测
  3. QA skill E2E-AC 覆盖验证
验证：
  - 模拟一个 Spec 泄漏技术词汇 → linter 告警
  - 模拟 E2E 缺少 AC 覆盖 → QA 报告列出缺失
```

#### Sprint 3: Orchestration（P2，共 3.5h）

```
目标：完善 Agent 协作机制
产出：
  1. AGENTS.md 角色定义更新
  2. ailp-sdd-workflow 委派模板
  3. model-router 编码子场景规则
  4. pre-push hooks
验证：
  - 委派 Coder Agent 时上下文完整（不再遗漏 E2E 文件路径）
  - pre-push 拦截未 format 代码
```

#### Sprint 4: Hardening（P3，共 1.5h）

```
目标：CI 环境健壮性
产出：
  1. ci-parity skill
  2. E2E CI push trigger
验证：
  - 所有测试在 CI 双环境通过
```

### 5.3 总估时：10h

---

## 六、附录：001-public-profile 试点全流程数据

| 指标 | 数据 |
|------|------|
| 试点变更目录 | `docs/changes/001-public-profile/` |
| SDD 阶段 | 8/8 全部执行 |
| PR 编号 | [#19](https://github.com/NEU-JING/ai-learning-platform/pull/19) |
| 后端测试 | 193/194 通过（AC12 SQLite skip） |
| 契约测试 | 16/16 通过 |
| E2E 测试 | 9 passed / 5 skipped / 1 skipped(SQLite) in CI |
| CI 修复轮次 | 6 轮（black→isort→ruff→seed→skipif→import） |
| 新增 Skills | 7 个（ailp-sdd-workflow 等） |
| 新增 Rules | 6 条红线（AGENTS.md） |
| 新增文档 | PRD / Spec / Design / Tasks / QA Report / AC 覆盖矩阵 |
| 发现并修复 Bug | 5 个（MIME 类型、重复 export、测试数据不对齐、display_name 隐藏规则、BR5 auto-enable 副作用） |
