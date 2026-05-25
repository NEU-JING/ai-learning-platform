# AI学习平台 - Agent 全栈开发工程师课程设计方案

> 基于 DeepSeek Agent 全栈开发工程师职位需求设计
> 版本: 1.0
> 创建日期: 2026-04-26

---

## 一、课程设计背景

### 1.1 目标岗位分析

**DeepSeek Agent 全栈开发工程师** 职位核心能力要求：

| 能力维度 | 具体要求 | 课程覆盖 |
|---------|---------|---------|
| **编程语言** | Python、Rust、JS/TS | Python✅、Rust🆕、TS🆕 |
| **前端开发** | 独立完成前端功能 | 🆕 新增5天课程 |
| **容器技术** | Docker、K8s运维经验 | 基础✅、进阶🆕 |
| **AI工具** | Claude Code/Cursor原理与二开 | 🆕 新增3天课程 |
| **RL基础** | 集成到RL基础设施 | 🆕 新增5天课程 |
| **Agent协议** | MCP、Tool Use、Function Calling | 基础⚠️、进阶🆕 |
| **评测平台** | 轨迹查看、调试分析工具 | 🆕 新增5天课程 |
| **安全竞赛** | CTF经验（加分项） | 🆕 新增3天选修 |

### 1.2 学习者画像

- **背景**: 10年Java + 数仓开发经验
- **优势**: 编程思维成熟、数据处理经验丰富、SQL能力强
- **目标**: 转型为 Agent 全栈开发工程师
- **时间**: 21周/147天（原14周扩展）
- **投入**: 每日1-2小时

---

## 二、课程路径总览

### 2.1 完整学习路线图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Agent 全栈开发工程师培养路径                          │
│                              (21周 / 147天)                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Phase 1: Python for AI (2周/14天) [Day 1-14]
├── 保持现有内容
└── 目标: Python基础 + NumPy/Pandas

Phase 2: 数学基础 (1周/7天) [Day 15-21]
├── 保持现有内容
└── 目标: 线性代数/概率论/微积分

Phase 3: 机器学习 (4周/28天) [Day 22-49]
├── 保持现有内容
└── 目标: ML算法 + Scikit-Learn

Phase 4: 深度学习 (2周/14天) [Day 50-63]
├── 保持现有内容
└── 目标: PyTorch + CNN/RNN

Phase 5: LLM大模型扩展 (5周/35天) [Day 64-98] ⭐扩展
├── Day 64-70: LLM基础与Prompt Engineering [已有]
├── Day 71-75: LangChain与RAG架构 [已有]
├── Day 76-78: Fine-tuning与模型部署 [已有]
├── Day 79-81: LLM项目实战 [已有]
├── Day 82-84: Multi-Agent系统 [已有]
│
├── 🆕 Day 85-87: AI编程工具原理与应用 (3天)
│   ├── 85: Claude Code/Cursor架构解析
│   ├── 86: 构建Mini Code Assistant
│   └── 87: Prompt Engineering进阶
│
├── 🆕 Day 88-92: 强化学习基础 (5天)
│   ├── 88: RL核心概念 (MDP/Q-Learning)
│   ├── 89: Policy Gradient与Actor-Critic
│   ├── 90: PPO算法与RLHF
│   ├── 91: Agent训练环境搭建
│   └── 92: LLM Agent与RL结合
│
├── 🆕 Day 93-96: Agent交互协议深度 (4天)
│   ├── 93: Function Calling深入
│   ├── 94: MCP协议规范详解
│   ├── 95: MCP Server开发实战
│   └── 96: Agent轨迹追踪与调试
│
└── 🆕 Day 97-98: Agent评测平台设计 (2天)
    ├── 97: 评测指标体系
    └── 98: 轨迹数据模型

Phase 6: AI工程化扩展 (5周/35天) [Day 99-133] ⭐扩展
├── Day 99-101: MLOps与MLflow [已有]
├── Day 102-104: 特征平台 [已有]
├── Day 105-106: A/B测试 [已有]
│
├── 🆕 Day 107-108: Docker/K8s进阶 (扩展2天)
│   ├── 107: Dockerfile多阶段构建 + GPU容器
│   └── 108: K8s Operator开发与模型部署
│
├── 🆕 Day 109-113: Rust编程基础 (5天)
│   ├── 109: Rust基础语法 (对比Java)
│   ├── 110: 所有权与生命周期
│   ├── 111: 异步编程与Tokio
│   ├── 112: PyO3与Python互调
│   └── 113: Rust AI服务开发 (Candle)
│
├── 🆕 Day 114-118: 前端技术栈 (5天)
│   ├── 114: TypeScript基础 (对比Java)
│   ├── 115: React组件开发
│   ├── 116: 数据可视化 (ECharts/D3.js)
│   ├── 117: AI应用前端框架 (Streamlit/Next.js)
│   └── 118: 前端实战练习
│
├── 🆕 Day 119-123: Agent评测与可视化 (5天)
│   ├── 119: 评测指标体系
│   ├── 120: 轨迹数据模型
│   ├── 121: 评测平台后端开发
│   ├── 122: 轨迹可视化前端
│   └── 123: LangSmith/Phoenix集成
│
└── 🆕 Day 124-126: CTF安全基础 (3天,选修)
    ├── 124: Web安全基础
    ├── 125: AI安全攻防
    └── 126: CTF实战练习

Phase 7: 综合实战项目 (3周/21天) [Day 127-147]
├── Week 1 (127-133): 需求分析与架构设计
│   ├── 项目选题: Agent评测平台全栈开发
│   ├── 技术选型: Python + Rust + TS + Docker/K8s
│   └── 架构设计: 微服务架构设计
│
├── Week 2 (134-140): 核心功能实现
│   ├── 后端: FastAPI + SQLModel
│   ├── 评测引擎: 异步任务队列 (Celery)
│   ├── 前端: React + TypeScript
│   └── 可视化: D3.js轨迹展示
│
└── Week 3 (141-147): 部署与优化
    ├── Docker化: 多阶段构建
    ├── K8s部署: Operator + Helm
    ├── 性能优化: Rust核心模块
    └── 项目文档与演示
```

---

## 三、新增课程模块详细设计

### 3.1 模块A: AI编程工具原理与应用 (Day 85-87)

#### 学习目标
- 理解Claude Code、Cursor、Copilot的核心架构
- 能够进行二次开发和自定义扩展
- 掌握高质量Prompt编写能力

#### 课程内容

**Day 85: Claude Code/Cursor架构解析**

| 时间 | 内容 | 形式 | 产出 |
|------|------|------|------|
| 30min | 课程介绍与工具概览 | 视频 | 工具对比表 |
| 45min | Claude Code Agent Loop实现机制 | 图文+代码 | 流程图 |
| 30min | Cursor上下文管理与Codebase理解 | 图文 | 架构图 |
| 15min | 休息 | - | - |
| 30min | Copilot代码补全与预测模型 | 图文 | 原理笔记 |
| 30min | 【实验】分析Claude Code API调用链 | 动手 | 分析报告 |

**核心知识点**:
```
Claude Code 架构:
├── 输入层
│   ├── 用户Query解析
│   ├── Codebase索引 (RAG)
│   └── 上下文窗口管理
├── 推理层
│   ├── System Prompt工程
│   ├── 多轮对话状态机
│   └── 工具调用决策
└── 输出层
    ├── 代码生成策略
    ├── 编辑建议格式化
    └── 用户确认循环
```

**Day 86: 构建Mini Code Assistant**

| 时间 | 内容 | 形式 | 产出 |
|------|------|------|------|
| 30min | AST抽象语法树基础 | 图文+代码 | AST可视化 |
| 45min | RAG驱动的代码检索 | 图文+代码 | 检索实现 |
| 30min | 多轮对话上下文管理 | 图文 | 状态机设计 |
| 15min | 休息 | - | - |
| 60min | 【实验】实现极简代码问答Agent | 动手 | 可运行原型 |

**实验任务**: 构建一个能理解代码库并回答问题的Mini Agent
```python
# 实验框架
class MiniCodeAssistant:
    def __init__(self, codebase_path):
        self.index = self._build_code_index(codebase_path)
        self.conversation_history = []
    
    def answer(self, query: str) -> str:
        # 1. 检索相关代码片段
        # 2. 构建Prompt
        # 3. 调用LLM
        # 4. 更新历史
        pass
```

**Day 87: Prompt Engineering进阶**

| 时间 | 内容 | 形式 | 产出 |
|------|------|------|------|
| 30min | System Prompt设计模式 | 图文 | 模板库 |
| 30min | Few-shot代码示例优化 | 图文+代码 | 示例集 |
| 30min | Chain-of-Thought编程 | 图文 | 流程图 |
| 15min | 休息 | - | - |
| 45min | 【实验】设计代码审查Prompt | 动手 | Prompt模板 |

**Prompt模板库示例**:
```yaml
code_review:
  system: |
    你是一位资深代码审查员，擅长发现代码中的问题。
    审查维度: 1)安全性 2)性能 3)可读性 4)规范性
  template: |
    请审查以下代码:
    ```{language}
    {code}
    ```
    请以JSON格式输出审查结果...

code_explanation:
  system: |
    你是一位技术文档专家，擅长解释复杂代码。
  template: |
    请解释以下代码的功能和工作原理...
```

---

### 3.2 模块B: 强化学习基础 (Day 88-92)

#### 学习目标
- 理解RL基础原理和核心算法
- 能够将LLM Agent与强化学习结合
- 了解RLHF在LLM训练中的应用

#### 前置知识
- PyTorch基础
- 概率论基础
- Python编程

#### 课程内容

**Day 88: RL核心概念**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | MDP马尔可夫决策过程 | 图文+数学 |
| 30min | Q-Learning算法 | 图文+伪代码 |
| 30min | SARSA算法对比 | 图文 |
| 15min | 休息 | - |
| 30min | 【理论】策略梯度方法 | 图文+数学 |
| 15min | 【实验】Gym环境CartPole训练 | 代码 |

**Day 89: PPO与Actor-Critic**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | Actor-Critic架构详解 | 图文 |
| 30min | PPO算法原理 | 图文+伪代码 |
| 30min | TRPO简介与对比 | 图文 |
| 15min | 休息 | - |
| 30min | 【实验】PPO实现简化版 | 代码 |
| 15min | 【练习】超参数调优实验 | 动手 |

**Day 90: RLHF与LLM训练**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | RLHF整体流程介绍 | 图文 |
| 30min | Reward Model设计 | 图文+代码 |
| 30min | PPO在LLM中的应用 | 图文 |
| 15min | 休息 | - |
| 45min | 【实验】使用TRL库进行RLHF | 代码 |

**Day 91: Agent训练环境搭建**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | Gym/Gymnasium环境介绍 | 图文 |
| 30min | 自定义环境开发 | 代码 |
| 30min | Reward设计最佳实践 | 图文 |
| 15min | 休息 | - |
| 45min | 【实验】创建简单的Agent训练环境 | 动手 |

**Day 92: LLM Agent与RL结合**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | Tool Learning训练方法 | 图文 |
| 30min | 反馈机制设计 | 图文 |
| 30min | RL在Agent能力增强中的应用 | 案例 |
| 15min | 休息 | - |
| 45min | 【项目】使用RL优化Agent工具选择 | 实战 |

---

### 3.3 模块C: Agent交互协议深度 (Day 93-96)

#### 学习目标
- 深入理解Function Calling和Tool Use
- 掌握MCP协议规范
- 能够开发MCP Server和Client

#### 课程内容

**Day 93: Function Calling深入**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | OpenAI Function Calling规范 | 图文 |
| 30min | Claude Tool Use机制对比 | 对比表 |
| 30min | 工具描述Schema设计 | 图文+代码 |
| 15min | 休息 | - |
| 45min | 【实验】设计多工具调用链 | 动手 |

**Day 94: MCP协议规范详解**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | Model Context Protocol介绍 | 图文 |
| 30min | Server/Client架构设计 | 架构图 |
| 30min | 工具发现与动态注册 | 图文+代码 |
| 15min | 休息 | - |
| 45min | 【实验】实现MCP Client | 代码 |

**Day 95: MCP Server开发实战**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | MCP Server开发流程 | 图文 |
| 60min | 【实验】实现天气查询MCP Server | 动手 |
| 15min | 休息 | - |
| 45min | 【实验】实现文件操作MCP工具集 | 动手 |

**Day 96: Agent轨迹追踪与调试**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | 执行过程记录设计 | 图文 |
| 30min | 中间状态保存与恢复 | 代码 |
| 30min | 调试与回放机制 | 图文 |
| 15min | 休息 | - |
| 45min | 【项目】实现Agent执行轨迹记录器 | 实战 |

---

### 3.4 模块D: Rust编程基础 (Day 109-113)

#### 学习目标
- 掌握Rust基础语法和核心概念
- 理解所有权系统和生命周期
- 能够使用Rust开发高性能AI服务
- 掌握PyO3与Python的互调

#### 课程内容

**Day 109: Rust基础语法 (对比Java)**

| 时间 | 内容 | 形式 | Java对比 |
|------|------|------|---------|
| 30min | Rust安装与工具链 | 动手 | cargo vs maven |
| 30min | 变量与数据类型 | 代码 | let vs 类型声明 |
| 30min | 控制流与函数 | 代码 | 相似但有差异 |
| 15min | 休息 | - | - |
| 45min | 【实验】Rust编写基础算法 | 动手 | 排序/搜索 |

**Rust vs Java 对比表**:
```
特性            Rust                    Java
─────────────────────────────────────────────────────
类型系统        静态+强类型+类型推断     静态+强类型
内存管理        编译期所有权检查         GC垃圾回收
并发安全        编译期保证               运行时检查
包管理          Cargo                    Maven/Gradle
错误处理        Result<T,E>              Exception
泛型            单态化                   类型擦除
```

**Day 110: 所有权与生命周期**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | 所有权系统详解 | 图文+代码 |
| 30min | 借用与引用规则 | 图文+代码 |
| 30min | 生命周期标注 | 图文+代码 |
| 15min | 休息 | - |
| 45min | 【实验】实现链表数据结构 | 动手 |

**Day 111: 异步编程与Tokio**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | Tokio运行时介绍 | 图文 |
| 30min | async/await语法 | 代码 |
| 30min | 并发与并行模式 | 图文 |
| 15min | 休息 | - |
| 45min | 【实验】实现异步HTTP客户端 | 动手 |

**Day 112: PyO3与Python互调**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | PyO3基础介绍 | 图文 |
| 30min | 编写Python扩展模块 | 代码 |
| 30min | 性能对比测试 | 实验 |
| 15min | 休息 | - |
| 45min | 【实验】用Rust重写Python计算密集型模块 | 动手 |

**Day 113: Rust AI服务开发**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | Candle轻量级ML框架 | 图文 |
| 30min | ONNX Runtime集成 | 代码 |
| 30min | 高性能推理服务设计 | 图文 |
| 15min | 休息 | - |
| 45min | 【项目】Rust实现文本分类服务 | 实战 |

---

### 3.5 模块E: 前端技术栈 (Day 114-118)

#### 学习目标
- 掌握TypeScript基础
- 能够使用React开发组件
- 能够开发数据可视化界面
- 掌握AI应用前端框架

#### 课程内容

**Day 114: TypeScript基础 (对比Java)**

| 时间 | 内容 | 形式 | Java对比 |
|------|------|------|---------|
| 30min | TS环境配置 | 动手 | 配置对比 |
| 30min | 类型系统与接口 | 代码 | interface vs class |
| 30min | 泛型与类型推断 | 代码 | 相似但有差异 |
| 15min | 休息 | - | - |
| 45min | 【实验】重构JS代码为TS | 动手 |

**Day 115: React组件开发**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | React基础概念 | 图文 |
| 30min | Hooks与状态管理 | 代码 |
| 30min | 组件通信与复用 | 代码 |
| 15min | 休息 | - |
| 45min | 【实验】开发AI对话组件 | 动手 |

**Day 116: 数据可视化**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | ECharts基础 | 图文+代码 |
| 30min | D3.js简介 | 图文 |
| 30min | 时序数据可视化 | 代码 |
| 15min | 休息 | - |
| 45min | 【实验】开发Agent轨迹可视化图表 | 动手 |

**Day 117: AI应用前端框架**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | Streamlit快速原型 | 代码 |
| 30min | Next.js全栈开发 | 图文 |
| 30min | Gradio对比 | 图文 |
| 15min | 休息 | - |
| 45min | 【实验】部署AI应用界面 | 动手 |

---

### 3.6 模块F: Agent评测与可视化 (Day 119-123)

#### 学习目标
- 设计Agent评测指标体系
- 掌握轨迹数据模型设计
- 能够开发评测平台后端
- 能够开发可视化前端

#### 课程内容

**Day 119: 评测指标体系**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | 任务完成率指标 | 图文 |
| 30min | 步骤效率指标 | 图文 |
| 30min | Token成本指标 | 图文 |
| 15min | 休息 | - |
| 45min | 【设计】设计评测指标框架 | 动手 |

**评测指标框架**:
```python
class EvaluationMetrics:
    """Agent评测指标体系"""
    
    # 任务级指标
    task_completion_rate: float  # 任务完成率
    success_rate: float          # 成功率
    
    # 步骤级指标
    step_efficiency: float       # 步骤效率
    tool_accuracy: float         # 工具使用准确性
    
    # 成本指标
    token_usage: int             # Token使用量
    cost_efficiency: float       # 成本效率
    
    # 时间指标
    execution_time: float        # 执行时间
    latency_avg: float           # 平均延迟
```

**Day 120: 轨迹数据模型**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | Step/Action/Observation设计 | 图文 |
| 30min | 序列化方案选择 | 对比 |
| 30min | 版本兼容性设计 | 图文 |
| 15min | 休息 | - |
| 45min | 【设计】轨迹数据Schema | 动手 |

**轨迹数据Schema**:
```json
{
  "trajectory_id": "uuid",
  "agent_id": "string",
  "task_id": "string",
  "start_time": "timestamp",
  "end_time": "timestamp",
  "status": "success|failure|timeout",
  "steps": [
    {
      "step_id": "uuid",
      "timestamp": "timestamp",
      "action": {
        "type": "tool_call|llm_call|user_input",
        "tool_name": "string",
        "params": {},
        "thought": "string"
      },
      "observation": {
        "result": "string",
        "error": "string|null",
        "metadata": {}
      },
      "token_usage": {
        "input": 0,
        "output": 0
      },
      "latency_ms": 0
    }
  ],
  "metrics": {
    "total_steps": 0,
    "total_tokens": 0,
    "total_time_ms": 0
  }
}
```

**Day 121: 评测平台后端开发**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | 批量评测执行引擎设计 | 图文 |
| 30min | 结果聚合与分析 | 代码 |
| 30min | 排行榜系统 | 图文 |
| 15min | 休息 | - |
| 45min | 【实验】实现批量评测API | 动手 |

**Day 122: 轨迹可视化前端**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | 步骤流程图展示 | 代码 |
| 30min | 调试时间轴 | 代码 |
| 30min | 对比分析视图 | 图文 |
| 15min | 休息 | - |
| 45min | 【实验】开发轨迹可视化界面 | 动手 |

**Day 123: 平台集成**

| 时间 | 内容 | 形式 |
|------|------|------|
| 30min | LangSmith集成 | 图文+代码 |
| 30min | Phoenix集成 | 图文+代码 |
| 30min | 自定义指标上报 | 代码 |
| 15min | 休息 | - |
| 45min | 【项目】集成现有监控平台 | 实战 |

---

## 四、实验环境设计

### 4.1 在线实验环境架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        实验环境架构                              │
└─────────────────────────────────────────────────────────────────┘

用户浏览器
    │
    ▼
┌─────────────────┐
│  前端界面        │
│  - Monaco编辑器  │
│  - 终端模拟器    │
│  - 可视化组件    │
└────────┬────────┘
         │ WebSocket
         ▼
┌─────────────────┐     ┌─────────────────┐
│  API Gateway    │────▶│  实验管理器      │
│  (FastAPI)      │     │  - 任务调度      │
└────────┬────────┘     │  - 资源分配      │
         │              └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────────────┐
│              容器化实验环境                        │
│  ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │ Python沙箱  │ │  Rust沙箱   │ │ TS/Node沙箱│ │
│  │             │ │             │ │            │ │
│  │ • PyTorch   │ │ • Cargo     │ │ • Node.js  │ │
│  │ • NumPy     │ │ • PyO3      │ │ • TS编译器  │ │
│  │ • Gym       │ │ • Tokio     │ │ • React    │ │
│  └─────────────┘ └─────────────┘ └────────────┘ │
└─────────────────────────────────────────────────┘
```

### 4.2 各模块实验环境配置

| 模块 | 环境需求 | 预装包/工具 | 资源限制 |
|------|---------|------------|---------|
| AI编程工具 | Python 3.11 | tree-sitter, openai, anthropic | 512MB, 60s |
| 强化学习 | Python 3.11 | gym, stable-baselines3, trl | 1GB, 120s |
| MCP协议 | Python 3.11 | mcp-sdk, fastapi, uvicorn | 512MB, 60s |
| Rust编程 | Rust 1.75+ | cargo, pyo3, tokio | 1GB, 120s |
| 前端开发 | Node 18+ | typescript, react, vite | 512MB, 60s |
| 评测平台 | Python 3.11 + Node 18 | fastapi, react, d3 | 1GB, 120s |

---

## 五、综合实战项目设计

### 5.1 项目概述

**项目名称**: Agent评测平台 (Agent Evaluation Platform)

**项目目标**: 构建一个完整的Agent评测平台，支持：
- 批量Agent评测任务执行
- 执行轨迹记录与存储
- 轨迹可视化与回放
- 评测指标分析与对比
- 排行榜系统

**技术栈**:
- 后端: Python + FastAPI + SQLModel + Celery
- 前端: TypeScript + React + D3.js
- 高性能模块: Rust (可选)
- 部署: Docker + Kubernetes

### 5.2 项目里程碑

**Week 1: 需求分析与架构设计 (Day 127-133)**

| 天数 | 任务 | 产出 |
|------|------|------|
| 127-128 | 需求文档编写 | PRD.md |
| 129-130 | 架构设计 | 架构图 + 技术选型 |
| 131 | 数据库设计 | ER图 + Schema |
| 132-133 | 接口设计 | API文档 |

**Week 2: 核心功能实现 (Day 134-140)**

| 天数 | 任务 | 产出 |
|------|------|------|
| 134-135 | 后端基础架构 | FastAPI项目搭建 |
| 136-137 | 评测执行引擎 | Celery任务队列 |
| 138 | 轨迹存储模块 | 数据库操作 |
| 139-140 | 前端基础框架 | React项目搭建 |

**Week 3: 功能完善与部署 (Day 141-147)**

| 天数 | 任务 | 产出 |
|------|------|------|
| 141-142 | 可视化组件 | 轨迹可视化 |
| 143 | 排行榜系统 | 排行功能 |
| 144-145 | Docker化 | Dockerfile + Compose |
| 146 | K8s部署 | Helm Chart |
| 147 | 文档与演示 | README + 演示视频 |

---

## 六、课程产出物清单

### 6.1 课程内容产出

| 模块 | 课程文档 | 实验项目 | 代码示例 |
|------|---------|---------|---------|
| AI编程工具 | 3篇 | 2个 | 10+ |
| 强化学习 | 5篇 | 3个 | 15+ |
| MCP协议 | 4篇 | 2个 | 8+ |
| Rust编程 | 5篇 | 5个 | 20+ |
| 前端开发 | 5篇 | 4个 | 12+ |
| 评测平台 | 5篇 | 3个 | 15+ |
| **总计** | **27篇** | **19个** | **80+** |

### 6.2 平台功能产出

- [ ] Rust在线编译环境
- [ ] TypeScript/React在线环境
- [ ] MCP工具市场界面
- [ ] 评测平台原型系统
- [ ] 轨迹可视化组件库
- [ ] Prompt模板库

---

## 七、实施计划

### 7.1 开发排期

| 任务 | 负责人 | 开始日期 | 结束日期 | 状态 |
|------|--------|---------|---------|------|
| O11: AI编程工具课程 | main | 2026-05-01 | 2026-05-15 | 待开始 |
| O12: 强化学习课程 | main | 2026-05-16 | 2026-05-22 | 待开始 |
| O13: MCP协议课程 | main | 2026-05-23 | 2026-05-29 | 待开始 |
| O14: Rust编程课程 | main | 2026-05-30 | 2026-06-05 | 待开始 |
| O15: 前端技术课程 | main | 2026-06-06 | 2026-06-12 | 待开始 |
| O16: 评测平台课程 | main | 2026-06-13 | 2026-06-19 | 待开始 |
| O17: CTF安全课程 | main | 2026-06-20 | 2026-06-26 | 待开始 |
| O18: 综合实战项目 | main | 2026-06-27 | 2026-07-10 | 待开始 |
| O19: Docker/K8s进阶 | main | 2026-07-01 | 2026-07-03 | 待开始 |

### 7.2 优先级排序

**P1 (立即开始)**:
1. O11: AI编程工具原理 (直接对应加分项)
2. O14: Rust编程基础 (核心技能要求)
3. O16: 评测平台课程 (核心职责要求)

**P2 (近期完成)**:
4. O12: 强化学习基础 (核心职责要求)
5. O15: 前端技术栈 (核心技能要求)
6. O13: MCP协议深度 (加分项)

**P3 (中期规划)**:
7. O18: 综合实战项目 (能力整合)
8. O19: Docker/K8s进阶 (技能扩展)
9. O17: CTF安全基础 (加分项,选修)

---

## 八、附录

### 8.1 参考资料

**AI编程工具**:
- Claude Code官方文档
- Cursor架构博客
- Copilot技术报告

**强化学习**:
- "Reinforcement Learning: An Introduction" (Sutton & Barto)
- Spinning Up in Deep RL (OpenAI)
- HuggingFace TRL文档

**MCP协议**:
- Model Context Protocol Specification
- Anthropic MCP SDK文档

**Rust**:
- "The Rust Programming Language" (官方)
- Rust by Example
- PyO3官方文档
- Candle GitHub仓库

**前端**:
- TypeScript官方文档
- React官方文档
- ECharts官方文档

### 8.2 相关任务关联

本课程设计与以下TASKS.md任务关联:
- O11-O19: 课程内容开发任务
- O2: 实验自动评测系统 (为评测平台课程提供基础)
- O6: 讨论区功能 (支持课程社区互动)
- O7: 统计系统 (支持学习数据分析)

---

**文档版本**: 1.0
**最后更新**: 2026-04-26
**作者**: AI Assistant
