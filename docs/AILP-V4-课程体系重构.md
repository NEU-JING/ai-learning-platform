# AILP V4 — 课程体系重构：Learn Your Way × AI 工程化能力

> **版本**：V4.1（课程体系完整重构）
> **日期**：2026-05-21
> **前置**：AILP-V4-PRD-重构版、AILP-实训落地可行性分析
>
> **核心命题**：AI 时代最稀缺的能力不是「懂 AI 原理」，而是「能用 AI 把事做成」。AILP 的课程体系必须两条腿走路——**AI 原理（理解 AI）** + **AI 工程化（驾驭 AI）**。

---

## 目录

| 部分 | 内容 |
|:----:|------|
| **零** | [设计哲学——什么是 AI 工程化能力](#零设计哲学什么是-ai-工程化能力) |
| **一** | [能力阶梯——从 Vibe Coding 到 Harness Engineering](#一能力阶梯从-vibe-coding-到-harness-engineering) |
| **二** | [四路径课程矩阵](#二四路径课程矩阵) |
| **三** | [AI 工程化课程体系（核心新增）](#三ai-工程化课程体系核心新增) |
| **四** | [AI 原理课程体系（保留与强化）](#四ai-原理课程体系保留与强化) |
| **五** | [课程 × 认证映射](#五课程--认证映射) |
| **六** | [Learn Your Way 个性化实现](#六learn-your-way-个性化实现) |
| **七** | [实施路线图](#七实施路线图) |

---

## 零、设计哲学——什么是 AI 工程化能力

### 0.1 一个根本性的区分

```
AI 原理（Understanding AI）：           AI 工程化（Engineering with AI）：
─────────────────────────────────────────────────────────────────
"Transformer 的 Attention 怎么算？"       "怎么给 Claude Code 写 CLAUDE.md？"
"反向传播的链式法则是什么？"              "什么时候用 /compact 而不是新开对话？"
"梯度下降有哪些变体？"                    "怎么设计一个 MCP Server 让 AI 调你的 API？"
"BERT 和 GPT 架构有什么区别？"            "怎么组织 Skills 让 Agent 复用能力？"

教的是"AI 怎么工作"                       教的是"人怎么让 AI 更好地工作"
```

**两者都重要，但价值路径完全不同。**

| 维度 | AI 原理 | AI 工程化 |
|------|:---:|:---:|
| 学习目标 | 理解模型内部机制 | 提升人+AI 协作效率 |
| 核心能力 | 设计/训练/调优模型 | 设计 Prompt/Context/Harness |
| 产出物 | 训练好的模型 | 高效的 AI 工作流 |
| 验证方式 | 模型指标（准确率等） | 效率提升（任务完成时间/质量） |
| 受众 | ML Engineer / Researcher | 所有开发者 |

### 0.2 Claude Code 给我们的启示

调研 Claude Code 源码后，发现了 AI 工程化的**三层范式**：

```
                    ┌─────────────────────────────┐
                    │    Harness Engineering       │  ← 脚手架层
                    │    (CLAUDE.md + Hooks +      │     95 分
                    │     Permissions + SubAgents) │
                    ├─────────────────────────────┤
                    │    Context Engineering       │  ← 上下文层
                    │    (/compact + cache_control │     85 分
                    │     + 动态组装 + 状态压缩)    │
                    ├─────────────────────────────┤
                    │    Prompt Engineering        │  ← 提示词层
                    │    (静态7模块 + 动态11模块    │     70 分
                    │     + 6步组装流水线)          │
                    └─────────────────────────────┘

直接靠 Prompt Engineering 做到 70+ 分
加上 Context Engineering 推到 80-85 分
再加上 Harness Engineering 才能到 90-95 分
```

**AILP 的 AI 工程化课程，就是沿着这三层，从 70 分教到 95 分。**

### 0.3 Claude Code 静态 Prompt 7 模块（对应我们的课程设计）

Claude Code 的 System Prompt 静态层有 7 个核心模块，恰好构成 AI 工程化的基础能力谱：

| # | Claude Code 模块 | 对应 AILP 课程 | 能力类型 |
|:--:|------|------|:---:|
| 1 | 身份介绍 + 安全边界 | Prompt Engineering（角色设定） | 提示词工程 |
| 2 | 系统行为（输出规则/权限） | Context Engineering（约束设计） | 上下文工程 |
| 3 | 任务执行（编码风格/防过度工程） | Spec Coding（规范编写） | 规范工程 |
| 4 | 操作安全（可逆性评估） | Harness（安全护栏） | 脚手架工程 |
| 5 | 工具使用（优先专用工具） | MCP（工具协议） | 工具集成 |
| 6 | 语气风格（简洁/带行号引用） | Prompt Engineering（格式控制） | 提示词工程 |
| 7 | 输出效率（直奔主题） | Context Engineering（Token 预算） | 上下文工程 |

---

## 一、能力阶梯——从 Vibe Coding 到 Harness Engineering

### 1.1 四个成熟度级别

```
Level 1: AI 使用者（Vibe Coder）
  "帮我写一个排序函数"
  能力：会向 AI 提问，能得到答案
  局限：答案质量不可控，复杂任务经常跑偏
  覆盖：Vibe Coding 基础

Level 2: AI 协作者（Prompt Engineer + Context Engineer）
  "你是资深 Python 开发者。项目使用 FastAPI + SQLAlchemy。
   请为 User 模型生成 CRUD 端点，遵循项目现有的 
   Repository 模式（见 app/repositories/base.py）。
   要求：类型提示完整、异常处理完善、含单元测试。"
  能力：通过 Prompt 设计 + Context 注入，精确控制 AI 输出
  覆盖：Prompt Engineering + Context Engineering + Memory Management

Level 3: AI 系统构建者（Agent Designer + Tool Builder）
  "我设计了一个多 Agent 系统：
   - Architect Agent：分析需求，输出技术方案
   - Coder Agent：根据方案写代码
   - Reviewer Agent：审查代码质量
   它们通过 MCP 共享文件系统和 Git 工具。"
  能力：能设计 Agent 架构、搭建 MCP Server、编排多步骤工作流
  覆盖：Agent + MCP + Skills + Workflow + Knowledge Engineering

Level 4: AI 组织建设者（Harness Engineer）
  "我为团队搭建了 AI 开发体系：
   - 每个项目有 CLAUDE.md 定义规范
   - Hooks 强制执行 lint/format/type-check
   - Stop Hook 自动总结并更新约定
   - 多 Agent 并行开发 + CI/CD 自动验收"
  能力：能搭建和维护团队级 AI 工程化基础设施
  覆盖：Harness + Agentic Engineering + CI/CD for AI
```

### 1.2 每层需要学的具体技能

```
Level 1: Vibe Coding
  ├── 如何描述需求（自然语言 → 可执行指令）
  ├── 如何阅读 AI 生成的代码（不是自己写，是审计）
  └── 如何迭代改进（第一版不行 → 怎么改提示）

Level 2: Prompt + Context Engineering
  ├── Prompt 结构设计（角色 → 上下文 → 约束 → 格式）
  ├── Context Window 管理（/compact 机制、缓存策略）
  ├── 硬约束设计（<RULE> 标签、首尾强调）
  ├── 记忆管理（对话内记忆、跨会话记忆、向量存储）
  └── Spec Coding（需求 → 验收标准 → AI 实现）

Level 3: Agent + MCP + Workflow
  ├── Agent 架构设计（单 Agent → 多 Agent 协作）
  ├── MCP 协议（Client/Server、Tools/Resources/Prompts）
  ├── 工具设计（Function Calling Schema 最佳实践）
  ├── Workflow 编排（Sequential / Hierarchical / Graph-based）
  ├── Skills 设计（可复用的 AI 能力封装）
  └── Knowledge Engineering（RAG、知识图谱、规则库）

Level 4: Harness + Agentic Engineering
  ├── Harness 设计（CLAUDE.md + Hooks + Permissions）
  ├── Agentic Engineering（多 Agent 系统架构）
  ├── CI/CD for AI（自动化质量门禁）
  ├── 安全与治理（权限模型、审计日志、回滚机制）
  └── 团队级落地（规范制定、知识沉淀、持续演进）
```

---

## 二、四路径课程矩阵

### 2.1 路径总览

```
                    ┌──────────────────────────────────────────────────┐
                    │              AILP 学习路径矩阵 V4.1                │
                    │                                                   │
    目标角色        │  AI 专家      AI 工程师      AI 应用者     AI 管理者
                    │  (20周)       (14周)         (8周)         (6周)
  ─────────────────┼───────────────────────────────────────────────────
  ── AI 原理层 ──  │
  P1 Python基础    │    ● 必修        ● 必修        ● 必修        ○ 选学
  P2 AI数学直觉    │    ● 必修        ○ 选学        ○ 选学        ○ 选学
  P3 机器学习      │    ● 必修        ○ 选学        ○ 选学           —
  P4 深度学习      │    ● 必修           —             —             —
  P5 LLM原理       │    ● 必修        ○ 选学        ○ 选学        ○ 选学
  P6 AI工程原理    │    ● 必修        ● 必修        ○ 选学        ● 必修
  ─────────────────┼───────────────────────────────────────────────────
  ── AI 工程化层 ──│
  E1 Vibe Coding   │    ○ 选学        ● 必修        ● 必修        ● 必修
  E2 Prompt工程    │    ○ 选学        ● 必修        ● 必修        ○ 选学
  E3 Context工程   │    ○ 选学        ● 必修        ○ 选学        ○ 选学
  E4 记忆与知识    │    ○ 选学        ● 必修        ○ 选学           —
  E5 Spec Coding   │    ○ 选学        ● 必修        ○ 选学        ○ 选学
  E6 Skills & MCP  │    ○ 选学        ● 必修        ○ 选学           —
  E7 Agent设计     │    ○ 选学        ● 必修        ○ 选学           —
  E8 Workflow      │    ○ 选学        ● 必修        ○ 选学        ○ 选学
  E9 Harness       │    ● 必修        ● 必修        ○ 选学        ○ 选学
  E10 CI/CD for AI │    ● 必修        ● 必修           —          ○ 选学
  E11 Agentic Eng  │    ● 必修        ○ 选学           —             —
  ─────────────────┼───────────────────────────────────────────────────
  ── 管理与策略层 ──│
  M1 AI产品与策略  │    ○ 选学        ○ 选学        ○ 选学        ● 必修
  M2 AI安全与治理  │    ○ 选学        ○ 选学           —          ● 必修
  ─────────────────┼───────────────────────────────────────────────────
  预估周数          │    20周          14周           8周           6周
```

### 2.2 四条路径的核心差异

| | AI 专家 | AI 工程师 | AI 应用者 | AI 管理者 |
|------|:---:|:---:|:---:|:---:|
| **一句话** | 我能训练模型 | 我能让 AI 替我干活 | 我能用 AI 解决业务问题 | 我能管理 AI 项目 |
| **AI原理深度** | 深（全 6 阶段） | 中（4 阶段） | 浅（2 阶段） | 概念级（1 阶段） |
| **AI工程化深度** | 中（Harness+CI/CD） | **深（全部11模块）** | 浅（Vibe+Prompt） | 浅（Vibe+Strategy） |
| **核心产出** | 训练好的模型 | 高效的 AI 开发工作流 | AI 驱动的业务方案 | AI 落地策略 |
| **对标岗位** | ML Engineer | **AI Engineer / Harness Engineer** | AI-savvy PM/运营 | AI 技术负责人 |

**重点路径是「AI 工程师」**——这是市场最大空白、AILP 最差异化的定位。这个角色在 2026 年的招聘市场上被称为 "AI Engineer" 或 "Harness Engineer"——不是训练模型的人，而是**能让 AI 高效工作的人**。

---

## 三、AI 工程化课程体系（核心新增）

### 3.1 课程架构

```
┌────────────────────────────────────────────────────────────┐
│                  AI 工程化能力成长路径                        │
│                                                            │
│  Level 1: 个体效率                                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐             │
│  │ E1 Vibe   │  │ E2 Prompt    │  │ E3 Context│             │
│  │ Coding    │→ │ Engineering  │→ │ Engineering│            │
│  │ (1周)    │  │ (2周)        │  │ (2周)     │            │
│  └──────────┘  └──────────────┘  └──────────┘             │
│                                                            │
│  Level 2: 系统效率                                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐             │
│  │ E4 记忆与 │  │ E5 Spec      │  │ E6 Skills │             │
│  │ 知识工程  │→ │ Coding       │→ │ & MCP     │            │
│  │ (2周)    │  │ (1周)        │  │ (2周)     │            │
│  └──────────┘  └──────────────┘  └──────────┘             │
│                                                            │
│  Level 3: 系统构建                                          │
│  ┌──────────┐  ┌──────────────┐                            │
│  │ E7 Agent  │  │ E8 Workflow  │                            │
│  │ 设计      │→ │ 编排         │                            │
│  │ (2周)    │  │ (1周)        │                            │
│  └──────────┘  └──────────────┘                            │
│                                                            │
│  Level 4: 组织建设                                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐             │
│  │ E9 Harness│  │ E10 CI/CD    │  │ E11 Agentic│            │
│  │ Engineering│→│ for AI       │→ │ Engineering│           │
│  │ (2周)    │  │ (1周)        │  │ (2周)     │            │
│  └──────────┘  └──────────────┘  └──────────┘             │
│                                                            │
│  总计：AI 工程化路径 18 周（AI 工程师路径 E1-E11 全部必修）   │
└────────────────────────────────────────────────────────────┘
```

### 3.2 模块详细设计

---

#### E1: Vibe Coding——AI 辅助编程入门（1周）

**定位**：AI 工程化的第一级台阶。学会用自然语言让 AI 写代码。

**你学完能做什么**：
- 用 AI（Claude Code / Cursor / Copilot）生成代码片段和函数
- 阅读并理解 AI 生成的代码（不是盲目复制）
- 当 AI 生成的代码不对时，能描述问题并迭代改进

**课程内容**：

```
第 1 章：Vibe Coding 是什么、不是什么
  · AI 写代码 ≠ 不需要懂代码
  · Vibe Coding 的能力边界：什么时候好用、什么时候翻车
  · 案例对比：好的 Vibe vs 坏的 Vibe

第 2 章：从需求到代码的翻译
  · 如何描述功能需求（不要说"写个函数"，说清楚输入/输出/边界条件）
  · 实战：用自然语言生成 5 种不同场景的代码

第 3 章：阅读 AI 代码——审计而非复制
  · 常见 AI 代码问题模式（off-by-one、未处理边界、幻觉API）
  · 实战：审查 3 段 AI 生成的有 bug 代码

第 4 章：迭代改进
  · "不对，再试一次"是你最常用的 prompt
  · 如何让 AI 改进自己的代码（提供错误信息、约束条件）
  · 实战：给定一个不完善的 AI 生成代码，通过 3 轮对话修到可用
```

**实验设计**：

| 实验 | 类型 | 说明 |
|------|:---:|------|
| Lab 1: Vibe 生成 CRUD | 沙箱内 | 用自然语言生成 FastAPI CRUD，验证代码可运行 |
| Lab 2: 代码审计 | 沙箱内 | 给定 3 段 AI 生成代码，找出所有 bug |
| Lab 3: 迭代修复 | 沙箱内 | 初始代码有 5 个 bug，通过 AI 对话修到全部测试通过 |

**验证方式**：L1 认证——沙箱内完成实验，代码可执行 + 审计正确率 > 80%

---

#### E2: Prompt Engineering——提示词工程（2周）⭐

**定位**：从"随便问"到"精确控制"。基于 Claude Code 的 7 模块静态 Prompt 体系设计。

**参考来源**：Claude Code 系统提示词源码分析——静态 7 模块 + 动态 11+ 模块 + 6 步组装流水线。

**你学完能做什么**：
- 设计结构化的 System Prompt（不是一段话，是一个工程组件）
- 用 Role → Context → Constraint → Format 四段式控制 AI 输出
- 用 `<RULE>` 标签设计不可违背的硬约束
- 设计 Few-shot 示例让 AI 精确模仿格式

**课程内容**：

```
Week 1：Prompt 结构设计

第 1 章：Prompt 的工程化视角
  · 为什么"写一段好的提示词"是工程问题而非玄学
  · Prompt 的四段式结构：Role → Context → Constraint → Format
  · 案例拆解：Claude Code 的 System Prompt 为什么是 string[] 而非一个大字符串

第 2 章：角色设定（Role）
  · "你是一个资深的..."到底有没有用？什么时候有用？
  · Persona 设计的两个关键维度：能力边界 + 行为规范
  · 实战：为同一个任务设计 3 种不同 Persona，对比输出质量

第 3 章：约束设计（Constraint）
  · <RULE> 硬约束标签——Claude Code 的核心技巧
  · 首尾强调效应：关键约束放在 prompt 前 20% 或后 10% 区域
  · 否定式约束 vs 肯定式约束：不要说"不要"，要说"必须"
  · 实战：用 Rule-Block Template 生成代码，对比有无硬约束的差异

Week 2：Prompt 进阶技术

第 4 章：Few-shot 与格式控制
  · Few-shot 示例的数量、顺序、多样性对输出的影响
  · 格式控制：让 AI 输出精确的 JSON/YAML/代码块
  · 实战：设计 3-shot 示例，让 AI 生成符合项目风格的代码

第 5 章：Prompt 模板与可复用性
  · 从一次性 Prompt 到可复用的 Prompt 模板
  · 变量注入：{{ROLE}}、{{CONTEXT}}、{{CONSTRAINT}}
  · 实战：设计一个通用的「API 端点生成」Prompt 模板

第 6 章：Prompt 测试与迭代
  · 如何测试 Prompt 质量（A/B 对比、边界用例、对抗样本）
  · Prompt 版本管理（为什么需要 Git 管理 Prompt）
  · 实战：对自己的 Prompt 模板进行 10 个边界测试，记录通过率
```

**实验设计**：

| 实验 | 类型 | 说明 |
|------|:---:|------|
| Lab 1: 四段式 Prompt 设计 | 沙箱内 | 给定任务，设计 Role→Context→Constraint→Format Prompt |
| Lab 2: 硬约束实战 | 沙箱内 | 用 <RULE> 标签约束 AI 输出，验证约束生效 |
| Lab 3: Few-shot 格式控制 | 沙箱内 | 设计 3-shot 示例，验证输出格式精确匹配 |
| Lab 4: Prompt 测试套件 | 沙箱内 | 对自己的 Prompt 模板跑 10 个测试用例 |

**验证方式**：L2 认证——提交 Prompt 模板 + 测试报告，AI 审查 + 人工抽查

---

#### E3: Context Engineering——上下文工程（2周）⭐

**定位**：管理 AI 的"记忆"和"注意力"。Claude Code 最精妙的设计就在这一层。

**参考来源**：Claude Code 的 /compact 机制、cache_control 策略、动态 Prompt 组装。

**你学完能做什么**：
- 管理 Context Window——知道什么时候该压缩、什么时候该保留
- 设计 /compact 式的上下文压缩策略
- 区分「静态上下文」（缓存命中）和「动态上下文」（每次重算）
- 设计 CLAUDE.md 式的项目级上下文注入

**课程内容**：

```
Week 1：Context Window 管理

第 1 章：什么是 Context Engineering
  · Prompt Engineering 告诉你"怎么说"，Context Engineering 告诉你"给 AI 看什么"
  · Token 预算管理：不是 token 越多越好
  · Claude Code 的 3 板块模型：System(30%) + Messages(60%) + Tools(10%)

第 2 章：上下文压缩——/compact 机制深度解析
  · Claude Code /compact 的 6 段式压缩结构：
    Primary Request & Intent
    Problem Solving & Current Work
    Key Technical Concepts & API calls
    Files and Code Sections
    Errors and fixes
    Pending Tasks & Next Step
  · 这不是"文学式总结"，是"面向继续开发工作的状态压缩"
  · 实战：给定一段长对话，手动执行 /compact 压缩

第 3 章：缓存策略
  · cache_control: ephemeral——什么该缓存、什么不该
  · 静态 vs 动态分离：7 个静态模块可缓存，11+ 动态模块每次重算
  · 实战：分析自己项目的上下文，识别哪些可以缓存

Week 2：上下文设计

第 4 章：项目级上下文注入——CLAUDE.md 模式
  · 为什么 CLAUDE.md 是 Context Engineering 的最佳实践
  · 全局规范（根目录）+ 局部约定（子目录），自动叠加
  · 社区经验：60-120 行最优，200 行封顶
  · 实战：为自己的项目编写 CLAUDE.md

第 5 章：上下文优先级与降噪
  · 位置偏差：关键信息不在前 20% 或后 10% 区域 → 被忽略概率 ×3
  · 信息密度优化：去掉"谢谢""请"等礼貌用语（在 system prompt 里）
  · 工具输出的截断策略——不是全部给模型看
  · 实战：优化一个信息冗余的上下文，将 token 消耗降低 40%

第 6 章：上下文可观测性
  · 如何知道自己塞了多少 token（tokenizer 计数）
  · 上下文利用率分析——哪些信息被模型实际使用了
  · 实战：为自己的开发工作流建立上下文监控
```

**实验设计**：

| 实验 | 类型 | 说明 |
|------|:---:|------|
| Lab 1: /compact 压缩实战 | 沙箱内 | 给定长对话，执行结构化压缩，验证关键信息不丢失 |
| Lab 2: CLAUDE.md 编写 | 沙箱内 | 为开源项目编写 CLAUDE.md，AI 评分 |
| Lab 3: 上下文优化 | 沙箱内 | 优化冗余上下文，减少 40% token 同时保持输出质量 |
| Lab 4: 缓存策略设计 | 沙箱内 | 分析上下文，设计静态/动态分离方案 |

**验证方式**：L2 认证——提交 CLAUDE.md + 上下文优化报告 + 压缩测试

---

#### E4: 记忆与知识工程（2周）

**定位**：让 AI 记住该记住的，忘记该忘记的。

**你学完能做什么**：
- 区分三种记忆：对话内记忆、跨会话记忆、知识库记忆
- 设计向量存储（RAG）来扩展 AI 的"长期记忆"
- 用知识图谱组织领域知识，让 AI 理解实体关系
- 评估记忆质量——AI 是不是真的"记住"了

**课程内容**：

```
Week 1：记忆管理

第 1 章：AI 记忆的三个层次
  · Working Memory（对话内）：Context Window 内的历史
  · Episodic Memory（跨会话）：/compact 压缩的摘要
  · Semantic Memory（知识库）：RAG + 知识图谱
  · 每个层次的适用场景和局限

第 2 章：对话内记忆管理
  · 什么时候需要在 prompt 里重复关键信息
  · 结构化记忆：让 AI 在对话中维护 TODO、状态表
  · 实战：设计一个需要 AI 在多轮对话中记住复杂状态的任务

第 3 章：跨会话记忆——从 /compact 到持久化
  · 会话结束时的状态保存策略
  · 下一会话开始的上下文恢复
  · 实战：设计一个可跨会话接续的 Agent

Week 2：知识工程

第 4 章：RAG——检索增强生成
  · RAG 的原理：Embedding → 向量检索 → 上下文注入
  · Chunking 策略：大小、重叠、结构化
  · 检索质量评估：Recall、Precision、MRR

第 5 章：知识图谱与规则库
  · 什么时候 RAG 不够——需要结构化知识
  · 知识图谱构建：实体、关系、属性
  · 规则库：硬约束的集中管理

第 6 章：知识生命周期
  · 知识的新鲜度管理（何时更新、何时淘汰）
  · 知识冲突消解（多个来源的矛盾信息）
  · 实战：为一个领域构建知识库并评估质量
```

**实验设计**：

| 实验 | 类型 | 说明 |
|------|:---:|------|
| Lab 1: 多轮对话记忆 | 沙箱内 | 设计需要记忆的任务，验证 AI 在多轮后仍保持状态 |
| Lab 2: RAG Pipeline | 沙箱内 | 用 ChromaDB 搭建 RAG，评估检索质量 |
| Lab 3: 知识图谱 | 沙箱内 | 为 AILP 课程体系构建小规模知识图谱 |

**验证方式**：L2 认证——RAG Pipeline 检索准确率 > 0.7

---

#### E5: Spec Coding——规范驱动开发（1周）

**定位**：从"帮我写代码"升级到"按我的规范写代码"。让 AI 按照精确的需求和验收标准来工作。

**你学完能做什么**：
- 把模糊需求转化为精确 Spec（AI 能理解、能验证）
- 设计验收标准（Acceptance Criteria）让 AI 自检
- 用 Spec → AI 实现 → 自动测试的闭环工作流

**课程内容**：

```
第 1 章：为什么 Vibe Coding 不够
  · Vibe 的问题：改需求 = 重写 Prompt = 输出完全不同
  · Spec 的优势：需求稳定 → 输出稳定

第 2 章：Spec 的结构
  · 输入/输出定义（类型、格式、约束）
  · 行为描述（Given-When-Then）
  · 边界条件（正常/异常/边界值）

第 3 章：Spec → AI 实现 → 自动验证
  · 把 Spec 翻译为测试用例
  · AI 实现后自动跑测试 → 不通过就重来
  · 实战：为一个功能写 Spec → 让 AI 实现 → 验证
```

**实验**：沙箱内——给定需求，写 Spec → AI 生成代码 → 测试验证

**验证方式**：L2 认证——Spec 质量评分 + AI 生成代码的测试通过率

---

#### E6: Skills & MCP——能力封装与工具协议（2周）⭐⭐

**定位**：从"用 AI"到"给 AI 造工具"。这是 AI 工程化的质变点。

**参考来源**：Anthropic MCP 官方规范、Claude Code Skills 系统、Hermes Agent 的 Skills 机制。

**你学完能做什么**：
- 设计可复用的 Skill（封装一段 AI 能力和知识）
- 搭建 MCP Server（让 AI 能调用你的 API、数据库、文件系统）
- 设计 Tools 的 JSON Schema（Function Calling 最佳实践）
- 理解 MCP 三种能力：Tools（执行）/ Resources（读取）/ Prompts（模板）

**课程内容**：

```
Week 1：Skills 设计

第 1 章：什么是 Skill
  · Skill = 特定领域的知识 + 操作流程 + 约束规则
  · 对比：Prompt 模板 vs Skill——Skill 是"可执行的 Prompt 包"
  · Claude Code / Hermes 的 Skills 机制分析

第 2 章：Skill 的结构设计
  · 触发条件：什么时候激活这个 Skill
  · 知识注入：Skill 激活时给 AI 注入什么上下文
  · 操作步骤：AI 遵循的工作流
  · 约束规则：不可违反的红线
  · 实战：为自己的项目设计 3 个 Skills

第 3 章：Skill 的生命周期
  · 创建 → 测试 → 发布 → 更新 → 废弃
  · Skill 版本管理与兼容性
  · 实战：迭代改进自己的 Skill

Week 2：MCP

第 4 章：MCP 协议原理
  · MCP = AI 的 USB-C 接口——统一的外设连接标准
  · Client-Server 架构：Host → Client → Server
  · 三种能力：Tools（执行操作）、Resources（读取数据）、Prompts（模板）

第 5 章：搭建 MCP Server
  · Python SDK 实战：用 FastMCP 搭建你的第一个 Server
  · 暴露 Tools：定义 name、description、inputSchema
  · 暴露 Resources：URI 模式 + 内容类型
  · 实战：搭建一个「AILP 课程查询」MCP Server

第 6 章：MCP 安全与最佳实践
  · 权限控制：什么操作需要用户确认
  · 输入校验：永远不要信任 AI 传给 Tool 的参数
  · 错误处理：Tool 失败时返回什么
  · 实战：为 MCP Server 添加安全层
```

**实验设计**：

| 实验 | 类型 | 说明 |
|------|:---:|------|
| Lab 1: Skill 设计 | 沙箱内 | 为 3 个不同场景设计 Skills |
| Lab 2: MCP Server 基础 | 沙箱内 | 搭建一个暴露 Tools 的 MCP Server |
| Lab 3: MCP Server 进阶 | 沙箱内 | 添加 Resources + Prompts，完整 MCP Server |
| Lab 4: MCP 安全 | 沙箱内 | 为 Server 添加权限校验 + 输入验证 |

**验证方式**：L3 认证——提交完整 MCP Server 代码 + 安全审查报告

---

#### E7: Agent 设计（2周）⭐⭐

**定位**：让 AI 不只是回答问题，而是自主完成任务。

**参考来源**：LangGraph、CrewAI、AutoGen 三大框架的设计哲学对比。

**你学完能做什么**：
- 区分 4 种 Agent 模式：Router、Tool-Use、Planning、Multi-Agent
- 用 LangGraph 搭建有状态的 Agent 工作流
- 设计多 Agent 协作系统（分工 + 通信 + 协调）
- 调试 Agent——当 Agent "跑偏"时如何诊断和修复

**课程内容**：

```
Week 1：单 Agent 设计

第 1 章：Agent 是什么
  · Agent = LLM + 工具 + 记忆 + 规划
  · 4 种 Agent 模式对比：Router / Tool-Use / Planning / Multi-Agent
  · 什么时候不需要 Agent——简单的 Prompt 就够

第 2 章：LangGraph 入门
  · 图结构：Node（计算）+ Edge（流转）+ State（状态）
  · 循环支持——Agent 可以反思和重试
  · 实战：搭建一个 Tool-Use Agent（能搜索 + 能计算）

第 3 章：Agent 的状态管理
  · 显式状态 vs 隐式状态
  · 状态持久化——Agent 中断后能恢复
  · Human-in-the-Loop——关键步骤需要人类确认
  · 实战：设计一个需要人工审批的 Agent

Week 2：多 Agent 设计

第 4 章：多 Agent 协作模式
  · Sequential（顺序执行）：上一个输出 → 下一个输入
  · Hierarchical（层级调度）：Manager Agent 分配任务
  · Debate（辩论）：多个 Agent 讨论达成共识
  · 框架对比：CrewAI（角色驱动） vs AutoGen（对话驱动）

第 5 章：Agent 通信协议
  · Agent 之间如何传递信息（结构化消息 vs 自然语言）
  · 共享记忆——多 Agent 如何访问同一份上下文
  · 实战：搭建一个「Architect → Coder → Reviewer」三 Agent 系统

第 6 章：Agent 调试与评估
  · 常见 Agent 失败模式（无限循环、工具误用、状态丢失）
  · 可观测性——日志、追踪、可视化
  · 实战：诊断和修复一个"跑偏"的 Agent
```

**实验设计**：

| 实验 | 类型 | 说明 |
|------|:---:|------|
| Lab 1: Tool-Use Agent | 沙箱内 | 用 LangGraph 搭建搜索+计算 Agent |
| Lab 2: Human-in-the-Loop | 沙箱内 | 设计需要审批的 Agent 流程 |
| Lab 3: 多 Agent 协作 | 沙箱内 | 搭建 Architect→Coder→Reviewer 三 Agent 系统 |
| Lab 4: Agent 调试 | 沙箱内 | 给定一个"跑偏"的 Agent，诊断并修复 |

**验证方式**：L3 认证——提交多 Agent 系统代码 + 架构文档 + 调试报告

---

#### E8: Workflow 编排（1周）

**定位**：把多个 AI 操作串成可靠的生产流水线。

**你学完能做什么**：
- 设计 Sequential / Conditional / Parallel 三种工作流
- 用 DAG（有向无环图）编排复杂 AI Pipeline
- 实现错误重试、超时处理、结果缓存
- 监控工作流执行状态

**课程内容**：

```
第 1 章：Workflow 模式
  · Sequential（链式）：A → B → C
  · Conditional（分支）：if 条件 → A else → B
  · Parallel（并行）：同时执行 A 和 B，合并结果
  · Map-Reduce：拆分 → 并行处理 → 汇总

第 2 章：LangGraph 实现 Workflow
  · 条件边（ConditionalEdge）——动态路由
  · 并行节点——Fan-out / Fan-in
  · 状态管理——跨节点共享数据

第 3 章：Workflow 的可靠性
  · 重试策略（指数退避）
  · 超时与熔断
  · 结果缓存（相同输入不重复计算）
  · 实战：设计一个"文档处理"Workflow（读取→分段→翻译→校对→输出）
```

**实验**：沙箱内——搭建一个 5 步 Workflow，包含条件分支和错误重试

**验证方式**：L3 认证——Workflow 可靠性测试（100 次执行，成功率 > 95%）

---

#### E9: Harness Engineering——脚手架工程（2周）⭐⭐⭐

**定位**：AI 工程化的顶点。不是让 AI 更好，而是**构建让 AI 持续变好的系统**。

**参考来源**：Anthropic Harness 七层模型、Claude Code 的 CLAUDE.md + Hooks + Permissions。

**你学完能做什么**：
- 设计团队级的 AI 使用规范（CLAUDE.md 模式）
- 构建强制执行的安全护栏（Hooks）
- 实现 AI 的自我改进循环（Stop Hook）
- 搭建 AI 操作的审计和回滚体系

**课程内容**：

```
Week 1：Harness 基础

第 1 章：什么是 Harness
  · Harness = 围绕 AI 的一整套约束和脚手架
  · Anthropic 七层 Harness 模型：
    Layer 1: CLAUDE.md（约定注入）
    Layer 2: Hooks（强制执行）
    Layer 3: Permissions（权限控制）
    Layer 4: Skills（能力封装）
    Layer 5: MCP（工具集成）
    Layer 6: SubAgents（任务委派）
    Layer 7: Stop Hook（自我改进）

第 2 章：CLAUDE.md 设计
  · 全局规范 vs 局部约定
  · 什么该放进 CLAUDE.md：代码风格、项目结构、常用命令、禁止事项
  · 什么不该放：太长 → 降低模型性能
  · 实战：为 AILP 项目编写生产级 CLAUDE.md

第 3 章：Hooks 设计
  · Pre-hook（执行前检查）vs Post-hook（执行后验证）
  · Hooks vs CLAUDE.md 的区别：建议 vs 强制执行
  · 实战：设计 3 个 Hooks（lint 检查、类型校验、安全扫描）

Week 2：Harness 进阶

第 4 章：Stop Hook——AI 的自我进化
  · Anthropic 提出的反直觉用法：每次会话结束让 AI 自己总结改进
  · Stop Hook 的工作流：回顾 → 总结 → 更新 CLAUDE.md
  · 实战：实现一个 Stop Hook

第 5 章：权限与审计
  · 权限模型：什么操作 AI 可以自主执行、什么需要审批
  · 审计日志：记录每一次 AI 操作
  · 回滚机制：AI 改坏了怎么恢复
  · 实战：设计权限矩阵 + 实现审计日志

第 6 章：Harness 测试
  · 如何测试护栏是否有效
  · 对抗测试：故意让 AI 违规，验证 Hooks 拦截
  · 实战：对自己的 Harness 进行对抗测试
```

**实验设计**：

| 实验 | 类型 | 说明 |
|------|:---:|------|
| Lab 1: CLAUDE.md | 沙箱内 | 为 AILP 项目编写完整 CLAUDE.md |
| Lab 2: Hooks 系统 | 沙箱内 | 实现 3 个 Hooks（lint + type-check + security） |
| Lab 3: Stop Hook | 沙箱内 | 实现一个自我改进的 Stop Hook |
| Lab 4: 对抗测试 | 沙箱内 | 尝试突破自己的 Harness，验证防护有效 |

**验证方式**：L4 认证——提交完整 Harness 系统 + 对抗测试报告

---

#### E10: CI/CD for AI（1周）

**定位**：把 AI 开发纳入自动化流水线。

**你学完能做什么**：
- 设计 AI 代码的 CI 流水线（lint → type-check → test → security scan）
- 实现 Prompt 的 CI——Prompt 变更自动触发测试
- 搭建 AI Agent 的自动化验收

**课程内容**：

```
第 1 章：为什么 AI 代码也需要 CI/CD
  · AI 生成的代码同样需要 lint/type-check/test
  · 区别：测试用例可以由 AI 自动生成

第 2 章：Prompt CI
  · Prompt 变更 → 自动跑 Prompt 测试套件
  · Prompt 版本管理 + 回滚
  · 实战：搭建 Prompt CI Pipeline

第 3 章：Agent 验收自动化
  · Agent 的 E2E 测试框架
  · 性能回归检测
  · 实战：搭建 Agent 的自动化验收 Pipeline
```

**实验**：沙箱内——搭建 Prompt CI + Agent 验收 Pipeline

**验证方式**：L4 认证——CI 流水线能自动检测 Prompt 退化

---

#### E11: Agentic Engineering——多 Agent 系统工程（2周）⭐⭐

**定位**：组织多个 Agent 协同工作，构建 AI 驱动的开发体系。

**你学完能做什么**：
- 设计多 Agent 系统的架构（分工、通信、协调）
- 实现 Agent 委派——Manager Agent 把任务分包给 Worker Agent
- 评估多 Agent 系统的效率和可靠性
- 设计故障恢复机制

**课程内容**：

```
Week 1：多 Agent 架构

第 1 章：多 Agent 系统的设计空间
  · 集中式 vs 去中心化
  · 静态分工 vs 动态分配
  · Agent 的"技能"管理——什么 Agent 会什么

第 2 章：Agent 通信与委派
  · 任务分解：把大任务拆成子任务
  · 委派协议：Manager → Worker 的信息传递格式
  · 结果汇总：多个 Worker 的输出如何合并
  · 实战：搭建一个"多 Agent 代码审查系统"

第 3 章：多 Agent 的状态同步
  · 共享工作区（文件系统、Git）
  · 冲突检测与解决
  · 实战：3 个 Agent 同时修改同一项目的不同文件

Week 2：Agentic 系统的运维

第 4 章：监控与可观测性
  · 每个 Agent 的执行日志
  · 整体系统的吞吐量、延迟、成功率
  · 实战：搭建多 Agent 监控仪表盘

第 5 章：故障恢复
  · Agent 挂了怎么办（重试、降级、人工接管）
  · 部分失败 vs 全部失败的处理策略
  · 实战：设计一个能优雅降级的多 Agent 系统

第 6 章：Capstone——AI 驱动的完整项目
  · 综合运用 E1-E11 全部技能
  · 搭建完整的 Agentic 开发体系
  · 完成一个真实项目（从需求到部署）
```

**实验**：Capstone 项目——用 AI Agent 团队完成一个完整项目

**验证方式**：**L4 Harness Engineer 认证**——提交完整的 Agentic 系统 + Capstone 项目

---

### 3.3 模块间依赖关系

```
E1 Vibe Coding ──────┐
                      ├──→ E2 Prompt Engineering ──→ E3 Context Engineering
                      │                                        │
                      │                                        ▼
                      │                              E4 记忆与知识工程
                      │                                        │
                      ├──→ E5 Spec Coding ──────────→ E6 Skills & MCP
                      │                                        │
                      │                                        ▼
                      │                              E7 Agent 设计
                      │                                        │
                      │                                        ▼
                      │                              E8 Workflow 编排
                      │                                        │
                      └──────────────────────────────────────→ E9 Harness
                                                                   │
                                                                   ▼
                                                          E10 CI/CD for AI
                                                                   │
                                                                   ▼
                                                          E11 Agentic Eng
```

**学习路径**：E1 是入口，E2→E3→E4 逐层深入，E5 与 E2 同级可选，E6 之后进入系统构建层。E9-E11 是最终整合。

---

## 四、AI 原理课程体系（保留与强化）

### 4.1 保留的 6 阶段（与 V3 一致）

| 阶段 | 定位 | 核心内容 | 状态 |
|:----:|------|------|:---:|
| P1 | Python 基础 | 语法、数据结构、OOP、文件IO | ✅ 完成 |
| P2 | AI 数学直觉 | 线性代数、概率、梯度下降可视化 | ✅ 完成 |
| P3 | 机器学习 | sklearn、特征工程、模型评估 | ⚠️ 种子数据 |
| P4 | 深度学习 | PyTorch、CNN、Transformer | ⚠️ 种子数据 |
| P5 | LLM 原理 | Tokenization、Attention、微调 | ⚠️ 种子数据 |
| P6 | AI 工程原理 | 模型部署、MLOps、监控 | ⚠️ 种子数据 |

### 4.2 V4 强化调整

基于「Vibe Coding 对课程的影响」分析，AI 原理课程增加**审计和判断**导向：

| 阶段 | V3 内容 | V4 增加 |
|:----:|------|------|
| P1 Python | 教写代码 | **教审计 AI 生成的代码**——不是自己写，是判断 AI 写的对不对 |
| P2 数学 | 教公式推导 | **教判断模型是否合理的直觉**——看到 loss 曲线能判断问题 |
| P3 ML | 教 sklearn API | **教调优 AI 写的训练脚本**——AI 生成 Pipeline，你优化 |
| P4 DL | 教 PyTorch | **教评估 AI 生成的模型架构**——AI 选 ResNet，你判断是否合适 |
| P5 LLM | 教 Transformer | **教 Prompt 原理 + RAG/Agent 设计模式** |
| P6 工程 | 教部署 | **教 Spec → Pipeline → Agent 完整工作流** |

---

## 五、课程 × 认证映射

### 5.1 四级认证与课程的对应关系

| 认证等级 | 要求完成的课程 | 验证方式 |
|:---:|------|------|
| **L1 Practitioner** | P1 + P2 + E1 + 任一 E 模块 | 沙箱内完成结构化实验 |
| **L2 Engineer** | P1-P3 + E1-E6 | Capstone 项目（Spec → 实现 → 验证） |
| **L3 Senior** | P1-P6 + E1-E8 | 场景挑战 + 架构评审 + 3 领域项目 |
| **L4 Harness** | P1-P6 + E1-E11 | Agent-Driven 项目 + Harness 系统验收 |

### 5.2 企业岗位映射（增强版）

| 岗位 | 最低认证 | 推荐课程组合 |
|------|:---:|------|
| AI 应用开发（初级） | L1 | P1+P2+E1+E2 |
| **AI Engineer** | **L2** | **P1-P3 + E1-E6（全工程化核心）** |
| ML Engineer | L2 | P1-P6 + E1-E3（偏原理） |
| **Harness Engineer** | **L4** | **P1-P6 + E1-E11（全栈工程化）** |
| AI 技术负责人 | L3 | P1-P6 + E1-E9 + M1+M2 |
| AI-savvy PM | L1 | P1+E1+E2+M1 |

---

## 六、Learn Your Way 个性化实现

### 6.1 四个个性化维度

```
1. 角色驱动：选择你的目标角色 → 系统推荐对应路径
   "我想成为 AI Engineer" → P1-P3 + E1-E6 为核心

2. 背景适配：根据你的现有技能跳过已知内容
   "我已经会 Python" → 跳过 P1，从 P2/E1 开始
   "我是 Java 开发者" → P1 中的案例改为 Java 类比

3. 学习偏好：选择你的学习风格
   "我喜欢先理解原理再动手" → 先 P1-P3 再 E1-E6
   "我想直接动手做东西" → 先 E1-E3 再回头补 P3-P5

4. 节奏自适应：根据你的正确率动态调整
   某模块正确率 > 90% → 加速，跳过基础练习
   某模块正确率 < 60% → 推荐补充练习 + AI 教练介入
```

### 6.2 Onboarding 流程（增强）

```
Step 1: 角色选择
  "我主要想..." → AI专家 / AI工程师 / AI应用者 / AI管理者

Step 2: 背景收集
  编程语言 / 行业 / AI经验水平 / 学习风格偏好

Step 3: 初始技能评测（可选，推荐）
  · Python 基础（5 题）
  · AI 概念理解（5 题）
  · 工程化意识（5 题——"AI 生成的代码你会怎么审查？"）

Step 4: 个性化路径生成
  → 系统根据 1+2+3 生成推荐学习路径
  → "根据你的背景（Java开发 + 金融行业 + 零AI经验），
     建议从 E1 Vibe Coding 开始，同时学习 P1 Python基础（跳过已知内容）。
     预计 14 周达到 AI Engineer L2 认证。"
```

### 6.3 动态路径调整

```
学习过程中持续评估：

每完成一个模块 → 技能雷达更新
  → 如果某维度远超预期 → 推荐跳级
  → 如果某维度持续低迷 → 推荐补充模块

例：
  学员选的是"AI 应用者"路径
  → 但在 E2 Prompt Engineering 中正确率 95%
  → 系统推荐："你在 AI 工程化方面很有天赋，
     要不要考虑转向 AI 工程师路径？只需要多学 E4-E8。"
```

---

## 七、实施路线图

### 7.1 当前状态

| 模块 | 状态 | 说明 |
|------|:---:|------|
| P1-P2 | ✅ 完成 | 完整课程内容 + 实验 |
| P3-P6 | ⚠️ 种子数据 | 有骨架但需内容深化 |
| E1-E11 | ❌ 全新 | 需从零开发 |

### 7.2 Sprint 规划

| Sprint | 周期 | 交付内容 | 优先级 |
|:---:|------|------|:---:|
| **Sprint 5** | 2 周 | E1 Vibe Coding + E2 Prompt Engineering（前 3 章） | P0 |
| **Sprint 6** | 2 周 | E2 Prompt Engineering（后 3 章）+ E3 Context Engineering（前 3 章） | P0 |
| **Sprint 7** | 2 周 | E3 Context Engineering（后 3 章）+ E4 记忆与知识工程 | P0 |
| **Sprint 8** | 2 周 | E5 Spec Coding + E6 Skills & MCP | P1 |
| **Sprint 9** | 2 周 | E7 Agent 设计 + E8 Workflow | P1 |
| **Sprint 10** | 2 周 | E9 Harness + E10 CI/CD | P1 |
| **Sprint 11** | 3 周 | E11 Agentic Engineering + Capstone 项目 | P1 |
| **并行** | 持续 | P3-P6 内容深化（AI 原理课程内容填充） | P1 |

### 7.3 内容生产方式（Agent-First）

```
每个模块的生产流程：

Step 1: 大纲设计（人工 ⊗ AI）
  · 老师定义章节结构 + 核心知识点
  · AI 补全案例、练习、实验

Step 2: 内容生成（AI 主导）
  · AI 根据大纲生成全文 + 代码示例 + 测验
  · 参考 Claude Code 源码分析等调研材料

Step 3: 质量审查（AI + 人工）
  · 审查 AI 检查准确性、一致性、可读性
  · 老师对关键章节做最终确认

Step 4: 个性化变体（AI 并行）
  · 为金融/互联网/制造等行业生成行业案例变体
  · 为 Java/Python/JS 开发者生成语言适配版本

人工时间：每模块 0.5-1 天（关键节点确认）
AI 时间：每模块 1-2 天（并行生成）
```

---

## 附录 A：Claude Code 调研关键发现（课程设计参考）

### A.1 Claude Code System Prompt 7 静态模块

```
1. 身份介绍："You are Claude Code, Anthropic's official CLI..."
   → 对应课程 E2 Prompt Engineering - 角色设定

2. 系统行为：输出规则/权限模式/安全防护
   → 对应课程 E9 Harness - Permissions

3. 任务执行：编码风格/避免过度工程/安全编码
   → 对应课程 E5 Spec Coding

4. 操作安全：可逆性评估 + 高风险操作确认
   → 对应课程 E9 Harness - Hooks

5. 工具使用：优先专用工具，而非 Bash 命令
   → 对应课程 E6 MCP

6. 语气风格：简洁/无 emoji/带行号引用
   → 对应课程 E2 Prompt Engineering - 格式控制

7. 输出效率：直奔主题，拒绝废话
   → 对应课程 E3 Context Engineering - Token 预算
```

### A.2 Claude Code Context Engineering 核心机制

```
/compact 6 段式压缩：
  1. Primary Request and Intent
  2. Key Technical Concepts
  3. Files and Code Sections
  4. Errors and fixes
  5. Problem Solving
  6. All user messages (condensed)
  → 这不是"文学式总结"，是"面向继续开发的状态压缩"

缓存策略：
  system prompt 使用 cache_control: ephemeral
  静态 7 模块 → 缓存命中 → 零 token 消耗
  动态 11+ 模块 → 每次重算

Token 分配：
  System(30%) + Messages(60%) + Tools(10%)
```

### A.3 Harness 七层模型

```
Layer 7: Stop Hook    —— 会话结束 → 自动总结 → 更新 CLAUDE.md
Layer 6: SubAgents    —— 任务委派给子 Agent
Layer 5: MCP          —— 外部工具集成
Layer 4: Skills       —— 可复用能力封装
Layer 3: Permissions  —— 权限控制
Layer 2: Hooks        —— 强制执行（Pre/Post）
Layer 1: CLAUDE.md    —— 约定注入（全局+局部）
```

---

## 附录 B：关键课程内容来源

| 课程模块 | 主要参考来源 |
|------|------|
| E2 Prompt Engineering | Claude Code System Prompt 7 模块 + 6 步组装流水线 + Rule-Block Template |
| E3 Context Engineering | Claude Code /compact 机制 + cache_control + CLAUDE.md 模式 |
| E4 记忆与知识工程 | RAG + LangChain/LlamaIndex + 知识图谱 |
| E6 Skills & MCP | Anthropic MCP 规范 + Claude Code Skills + Hermes Skills |
| E7 Agent 设计 | LangGraph + CrewAI + AutoGen 三大框架对比 |
| E9 Harness | Anthropic Harness 七层模型 + CLAUDE.md + Hooks |
| E10 CI/CD for AI | Prompt CI + GitHub Actions + Agent 验收测试 |

---

*本文档为 AILP V4.1 课程体系完整重构。核心变化：新增 AI 工程化 11 模块（E1-E11），保留 AI 原理 6 阶段（P1-P6），两者构成互补的"理解 AI + 驾驭 AI"双轨体系。课程 → 认证 → 岗位三向对齐，Learn Your Way 实现角色/背景/风格/节奏四维个性化。*
