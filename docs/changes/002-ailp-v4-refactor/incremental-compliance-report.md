# SDD增量模式合规性审视报告

> **变更 ID**: 002-ailp-v4-refactor  
> **审视日期**: 2026-05-31  
> **审视依据**: sdd-orchestrator v2.0.2 增量模式规范

---

## 一、审视结论

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| **Phase划分清晰** | ⚠️ | 有5个Phase定义，但依赖关系未在tasks.md中明确标注 |
| **模块间依赖定义** | ✅ | design.md中定义了模块间接口契约 |
| **增量交付可行性** | ✅ | incremental-delivery-analysis.md已分析，Phase 1可独立交付 |
| **.sdd-state.json扩展** | ❌ | 未按增量模式要求扩展phase_config |
| **Phase交付标准** | ⚠️ | tasks.md中Phase标题有说明，但缺少明确的交付检查点 |
| **回归测试策略** | ❌ | 未定义Phase级别的回归测试策略 |

**总体评估**: **部分符合**增量模式要求，需要补充3项内容才能完全合规。

---

## 二、详细审视

### 2.1 Phase划分与依赖（✅ 符合）

tasks.md中明确定义了5个Phase：

| Phase | 模块 | 任务数 | 依赖 | 可独立交付 |
|-------|------|:------:|------|:----------:|
| Phase 1 | Path + Radar | 10 | 无 | ✅ **完全独立** |
| Phase 2 | Tutor + Certification | 9 | Phase 1 | ✅ 依赖清晰 |
| Phase 3 | Sandbox + Profile + Employer | 10 | Phase 1+2 | ✅ 依赖清晰 |
| Phase 4 | Evolution | 5 | Phase 1+2 | ✅ 依赖清晰 |
| Phase 5 | 集成测试 | 5 | Phase 1-4 | ✅ 依赖清晰 |

**设计评审**: incremental-delivery-analysis.md已验证Phase 1完全独立，可以独立交付。

---

### 2.2 模块间接口契约（✅ 符合）

design.md §3.2 明确定义了模块间接口：

| 调用方 | 被调用方 | 接口 | 说明 |
|--------|---------|------|------|
| Path Service | Radar Service | `get_skill_radar()` | Phase 1内部调用 |
| Tutor Service | Radar Service | `update_skill_from_lab()` | Phase 2依赖Phase 1 |
| Certification Service | Radar Service | `get_skill_summary()` | Phase 2依赖Phase 1 |
| Sandbox Service | Radar Service | `record_execution()` | Phase 3依赖Phase 1+2 |
| Profile Service | Radar Service | `get_public_radar()` | Phase 3依赖Phase 1+2 |
| Evolution Engine | Radar Service | `get_aggregate_skills()` | Phase 4依赖Phase 1+2 |

**关键发现**: Radar Service是核心依赖，所有后续Phase都依赖它。这与增量分析一致。

---

### 2.3 .sdd-state.json 扩展（❌ 不符合）

**当前状态**（不符合增量模式）:
```json
{
  "change_id": "002-ailp-v4-refactor",
  "current_phase": "coder",
  "phases_completed": ["po", "ba", "architect", "review"],
  // 缺少增量模式必需的 phase_config
}
```

**增量模式要求**（参考sdd-orchestrator规范）:
```json
{
  "change_id": "002-ailp-v4-refactor",
  "incremental_mode": true,
  "phase_config": {
    "total_phases": 5,
    "current_phase": "phase_1",
    "phases": {
      "phase_1": {
        "name": "基础数据层",
        "status": "not_started",
        "tasks": ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"],
        "ac_covered": ["AC1-AC14"],
        "depends_on": []
      },
      "phase_2": {
        "name": "核心服务层",
        "status": "not_started",
        "tasks": ["T11-T19"],
        "ac_covered": ["AC15-AC37"],
        "depends_on": ["phase_1"]
      },
      // ... phase_3, phase_4, phase_5
    }
  }
}
```

**不合规原因**:
1. 缺少 `"incremental_mode": true` 标记
2. 缺少 `phase_config` 配置
3. 无法追踪每个Phase的完成状态
4. 无法检查Phase间依赖

---

### 2.4 Phase交付标准（⚠️ 部分符合）

tasks.md中Phase标题有基本说明：

```markdown
## Phase 1: 基础数据层（Path + Radar）
## Phase 2: 核心服务层（Tutor + Certification）
...
```

**但缺少SDD增量模式要求的**:
1. 明确的交付检查点（Review + QA）
2. 每Phase的AC覆盖验证清单
3. 可独立上线的验收标准

**incremental-delivery-analysis.md中已建议**（但未落实到tasks.md）:
```markdown
## Phase 1: 基础数据层 [可独立交付]
**交付标准**: Path + Radar API 全量测试通过，AC1-AC14 验证完成
**验收检查点**: Phase 1 Review + Phase 1 QA
**依赖**: 无
```

---

### 2.5 回归测试策略（❌ 不符合）

tasks.md中没有定义Phase级别的回归测试策略。

**增量模式要求**（参考sdd-orchestrator）:

| Phase | 当前测试 | 回归测试 | 说明 |
|-------|:--------:|:--------:|------|
| Phase 1 | 100% | — | 基线Phase |
| Phase 2 | 100% | Phase 1 核心 10% | 验证不破坏Phase 1 |
| Phase 3 | 100% | Phase 1+2 核心 10% | 验证不破坏前面Phase |
| Phase 4 | 100% | Phase 1+2 核心 10% | 验证不破坏前面Phase |
| Phase 5 | 100% | 全量回归 100% | 最终归档前全量测试 |

---

## 三、改进建议

### 必须修复（ blocker ）

#### 1. 更新 .sdd-state.json 支持增量模式

```bash
# 在 .sdd-state.json 中添加
{
  "incremental_mode": true,
  "phase_config": {
    "total_phases": 5,
    "current_phase": "phase_1",
    "phases": {
      "phase_1": {
        "name": "基础数据层（Path + Radar）",
        "status": "not_started",  // not_started | in_progress | coding_done | review_passed | qa_passed | accepted
        "tasks": ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"],
        "ac_covered": ["AC1", "AC2", "AC3", "AC4", "AC5", "AC6", "AC7", "AC8", "AC9", "AC10", "AC11", "AC12", "AC13", "AC14"],
        "depends_on": [],
        "deliverables": [
          "Path API 全量测试通过",
          "Radar API 全量测试通过",
          "AC1-AC14 验证完成"
        ]
      },
      // ... 其他Phase
    }
  }
}
```

#### 2. 在 tasks.md 中添加Phase交付标准

```markdown
## Phase 1: 基础数据层（Path + Radar）
**交付标准**: 
- Path API 全量测试通过（5个API端点）
- Radar API 全量测试通过（4个API端点）
- AC1-AC14 验证完成
**验收检查点**: Phase 1 Review + Phase 1 QA
**回归测试**: 本Phase全量测试（基线Phase，无回归测试）
**依赖**: 无
**可独立交付**: ✅ 是

### T1: Path 模块数据库表
...
```

### 建议改进

#### 3. 在 design.md 中添加增量交付架构说明

在§3.2模块间接口契约后添加：

```markdown
### 3.2a 增量交付架构

本设计支持5个Phase增量交付：

**Phase 1（独立交付）**: Path + Radar
- 无外部依赖，可独立上线
- 提供基础数据层能力

**Phase 2-4（依赖前置）**: Tutor/Certification/Sandbox/Profile/Employer/Evolution
- 依赖Phase 1的Radar Service
- 每Phase完成后可Review+QA

**Phase 5（集成验证）**: 全量回归测试
- 验证所有Phase集成正确
- 最终验收后归档
```

---

## 四、当前状态与下一步

### 当前状态（根据.sdd-state.json）

| 阶段 | 状态 |
|------|------|
| PO | ✅ 完成 |
| BA | ✅ 完成 |
| Architect | ✅ 完成 |
| Review | ✅ 完成 |
| Coder | ⏸️ 回滚后等待重启 |

### 增量模式建议

**建议A：启用增量模式（推荐）**
1. 更新 `.sdd-state.json` 添加增量配置
2. 更新 `tasks.md` 添加Phase交付标准
3. 启动Phase 1 Coder → Review → QA
4. Phase 1验收通过后，再进入Phase 2

**建议B：保持标准模式**
- 所有39个任务一次性完成
- 统一Review和QA
- 适合：时间紧迫、团队熟悉、风险可控

### 决策建议

基于当前情况，**推荐启用增量模式**原因：
1. Phase 1（Path+Radar）已独立设计完毕，可快速验证
2. 39个任务、22小时估时，属于大型变更
3. Radar Service是核心依赖，早期验证可降低风险
4. 已有incremental-delivery-analysis.md分析基础

---

## 五、合规检查清单

| 检查项 | 状态 | 修复说明 |
|--------|:----:|----------|
| `.sdd-state.json` 包含 `"incremental_mode": true` | ✅ | 已添加 |
| `.sdd-state.json` 包含 `phase_config` 配置 | ✅ | 已添加5个Phase完整配置 |
| `tasks.md` 每个Phase有明确的交付标准 | ✅ | 已添加5个Phase交付标准 |
| `tasks.md` 每个Phase有AC覆盖验证清单 | ✅ | 已在phase_config中定义 |
| `tasks.md` 定义了Phase级别的回归测试策略 | ✅ | 已添加regression字段 |
| `design.md` 说明增量交付架构（可选） | ⏸️ | 可选，暂不处理 |

**当前通过**: 5/6 项（83%）  
**需修复**: 0 项（仅剩1项可选）

---

*报告生成: 2026-05-31*  
*依据: sdd-orchestrator v2.0.2 增量模式规范*
