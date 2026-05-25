# AILP 开发流程规范 V2.1

> 版本：V2.1
> 日期：2026-05-24
> 变更：新增 Phase 8 人工验收门禁

---

## 一、流程总览

```
用户需求
    │
    ▼
┌─────────────────┐
│ 流程级别判定      │  Quick / Standard / Enhanced
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 1: PRD     │  PO Agent
│ · 背景/目标      │  产出: changes/NNN-xxx/prd.md
│ · 用户/功能点    │
│ · 非目标/指标    │
│ · UI/UX（可选）  │
└────────┬────────┘
         │
         ▼
   ┌─────────────┐
   │ 👤 PRD 确认   │  ← 门禁 1：方向性决策
   └──────┬──────┘
          │ ✅
          ▼
┌─────────────────┐
│ Phase 2: Spec    │  BA Agent
│ · 验收场景       │  产出: changes/NNN-xxx/spec.md
│ · 业务规则       │
│ · 边界/错误/非功能│
└────────┬────────┘
         │
         ▼
   ┌─────────────┐
   │ 👤 Spec 确认  │  ← 门禁 2：行为契约
   └──────┬──────┘
          │ ✅
          ▼
┌─────────────────┐
│ Phase 3: Design  │  Architect Agent
│ · Brainstorming  │  产出: changes/NNN-xxx/design.md
│ · 接口/模型/选型 │
│ · 流程/前端/安全 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 4: Tasks   │  Architect Agent
│ · 按业务场景拆分 │  产出: changes/NNN-xxx/tasks.md
│ · 最小可部署单元 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 5: Implement│ Coder Agent (TDD)
│ · 逐任务实现     │  产出: 代码 + 单元测试
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 6: Review  │  Reviewer Agent
│ · 7维度评审      │  产出: 评审报告
│ · 分级自动修复   │
└────────┬────────┘
         │ ✅
         ▼
┌─────────────────┐
│ Phase 7: QA      │  QA Agent
│ · 集成/E2E测试   │  产出: QA 报告
│ · AC 覆盖验证    │
└────┬───┬─────┬───┘
     │   │     │
     │   │     └── ✅ 通过 → Phase 8
     │   │
     │   └── ❌ 失败 → 返回 Phase 5 (Coder 修复)
     │              │
     │              ├── 第 1-4 轮：自动循环
     │              │
     │              └── 第 5 轮仍失败：
     │                   👤 熔断，等待用户决策
     │
     ▼
┌─────────────────┐
│ Phase 8: 👤验收  │  ← ★ 门禁 3：人工最终确认
│                  │
│ · 用户验证       │
│   功能实现是否   │
│   符合预期       │
│                  │
│ 发现问题 → 分类  │
│ · 需求问题 → P1  │  ← 打回 PRD 阶段
│ · 设计问题 → P3  │  ← 打回 Design 阶段
│ · 代码问题 → P5  │  ← 打回 Implement 阶段
└────────┬────────┘
         │ ✅ 确认无误
         ▼
┌─────────────────┐
│ Phase 9: 归档    │
│ · 合入 current/  │
│ · 移至 archive/  │
│ · Stop Hook 学习 │
└─────────────────┘
```

---

## 二、门禁汇总

| 门禁 | 位置 | 确认人 | 通过后 | 不通过 |
|:---:|------|:---:|------|------|
| **门禁 1** | PRD 完成后 | 👤 用户 | → Spec | 修改 PRD |
| **门禁 2** | Spec 完成后 | 👤 用户 | → Design | 修改 Spec |
| **门禁 3** | QA 通过后 | 👤 用户 | → 归档 | 分析问题分类打回 |
| **熔断** | QA 5 轮失败 | 👤 用户 | — | 等待决策 |

---

## 三、门禁 3 详细规则

### 触发时机

Phase 7 QA 通过后，Agent 通知用户进行人工验收。

### 通知格式

```
【验收通知】

功能：[功能名称]
变更目录：changes/NNN-xxx/
测试：XXX/XXX 全绿
AC 覆盖：12/12
QA 报告：changes/NNN-xxx/qa-report.md

请验证功能实现是否符合预期。如有问题请反馈，我会分析问题类型后打回对应阶段修复。
```

### 用户反馈分类

用户反馈问题后，Agent 分析问题类型并执行对应操作：

| 问题类型 | 判断标准 | 打回阶段 | 修复路径 |
|:---:|------|:---:|------|
| **需求问题** | 功能逻辑与预期不符、缺少功能点、不应有的行为 | **Phase 1 PRD** | 修改 PRD → Spec → Design → Tasks → Implement → Review → QA → 验收 |
| **设计问题** | 功能对但交互不对、性能不达标、架构不合理 | **Phase 3 Design** | 修改 Design → Tasks → Implement → Review → QA → 验收 |
| **代码问题** | 功能对但实现有 bug、边界条件未处理、样式问题 | **Phase 5 Implement** | 修改代码 → Review → QA → 验收 |

### Agent 分类逻辑

```
收到用户反馈
    │
    ├── "功能不对"/"缺功能"/"不该这样" → 需求问题 → 打回 P1
    │
    ├── "交互不好"/"太慢"/"架构有问题" → 设计问题 → 打回 P3
    │
    └── "报错了"/"显示不对"/"边界没处理" → 代码问题 → 打回 P5
```

不确定分类时，向用户确认：「这个问题属于——A.需求层面（功能不符合预期）B.设计层面（实现方式不对）C.代码层面（有 bug）？」

### 用户确认

```
用户回复 "确认，没问题，可以归档" → Phase 9 归档
```

---

## 四、Phase 9 归档

```
✅ 用户确认
    │
    ▼
1. 合并变更到 current/
   · 将 changes/NNN-xxx/spec.md 合并到 current/spec.md
   · 将 changes/NNN-xxx/design.md 合并到 current/design.md

2. 归档变更目录
   · mv changes/NNN-xxx/ → archive/NNN-xxx/

3. Stop Hook 触发
   · 记录本次经验教训到 QUIRKS.md
   · 如有新陷阱，更新 Skills

4. 清理
   · 删除 .qa-rounds（如有）
   · Git commit 标注变更完成
```

---

## 五、QA 修复循环规则

```
QA 报告发现问题
    │
    ▼
Coder Agent 修复（第 N 轮）
    │
    ▼
Reviewer Agent 审查
    │
    ├── ❌ 仍有 BLOCKER → 返回 Coder（Review 内部最多 2 轮）
    │
    └── ✅ 通过 → QA Agent
                  │
                  ├── ✅ 通过 → Phase 8 验收
                  │
                  └── ❌ 失败
                        │
                        ├── 第 1-4 轮：自动返回 Coder
                        │
                        └── 第 5 轮：熔断
                              👤 通知用户决策
```

---

## 六、目录结构

```
docs/
├── current/                        # 当前生产版本
│   ├── spec.md
│   └── design.md
│
├── changes/                        # 进行中的变更
│   └── NNN-feature-name/
│       ├── prd.md
│       ├── spec.md
│       ├── design.md
│       ├── tasks.md
│       ├── qa-report.md
│       ├── ac-coverage.md
│       └── .qa-rounds
│
├── archive/                        # 已完成的变更
│
└── templates/                      # 文档模板
```

---

*本文档为 AILP 开发流程 V2.1。V2.1 新增：Phase 8 人工验收门禁（需求/设计/代码三级分类打回）。*
