# AI学习平台 - 架构设计文档

## 一、项目概述

### 1.1 项目目标
建设一个完整的AI学习平台，提供从入门到AI团队Leader的完整培养路径。

### 1.2 核心功能
1. **课程体系**：分阶段学习路径（入门→进阶→精通→领导力）
2. **在线实验**：浏览器内直接编写和运行Python代码
3. **实战项目**：AI Agent团队协作开发案例
4. **能力认证**：学习证书与能力评估

### 1.3 目标用户
- AI初学者（零基础入门）
- 进阶开发者（掌握LangChain等框架）
- 技术管理者（培养AI团队Leadership）

---

## 二、技术架构

### 2.1 技术栈选择

```
前端层:
├── React 18 + TypeScript
├── Tailwind CSS (样式)
├── Monaco Editor (代码编辑器)
├── React Query (数据获取)
└── Zustand (状态管理)

后端层:
├── Python 3.11 + FastAPI
├── SQLAlchemy (ORM)
├── PostgreSQL (主数据库)
├── Redis (缓存 + 会话)
├── Celery (异步任务)
└── Docker (代码沙箱)

基础设施:
├── Docker Compose (开发/部署)
├── Nginx (反向代理)
└── GitHub Actions (CI/CD)
```

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ 课程学习 │  │ 在线实验 │  │ 社区讨论 │  │ 个人中心 │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Nginx     │
                    │  (反向代理)  │
                    └──────┬──────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                        API Gateway                          │
│                     (FastAPI + JWT)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐  ┌────────▼────────┐  ┌──────▼──────┐
│   业务服务    │  │    实验服务      │  │   文件服务   │
│  - 用户管理   │  │  - 代码执行      │  │  - 上传下载  │
│  - 课程管理   │  │  - 沙箱管理      │  │  - 资源管理  │
│  - 学习进度   │  │  - 结果返回      │  │              │
└───────┬──────┘  └────────┬────────┘  └──────┬──────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      数据层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │    MinIO     │      │
│  │  (主数据库)   │  │   (缓存)     │  │  (对象存储)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    代码执行沙箱                              │
│              (Docker容器 + 资源限制)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、数据库设计

### 3.1 核心实体

```sql
-- 用户表
users
├── id (PK)
├── email (unique)
├── username
├── password_hash
├── avatar_url
├── role (student/teacher/admin)
├── created_at
└── updated_at

-- 课程表
courses
├── id (PK)
├── title
├── description
├── cover_image
├── level (beginner/intermediate/advanced/expert)
├── category_id (FK)
├── instructor_id (FK)
├── duration_hours
├── is_published
├── created_at
└── updated_at

-- 课程章节表
chapters
├── id (PK)
├── course_id (FK)
├── title
├── content (markdown)
├── order_index
├── type (video/text/code/lab)
├── video_url
├── duration_minutes
└── created_at

-- 实验环境表
labs
├── id (PK)
├── chapter_id (FK)
├── title
├── description
├── starter_code
├── solution_code
├── test_cases (JSON)
├── requirements (依赖包)
├── time_limit_seconds
├── memory_limit_mb
└── created_at

-- 学习进度表
learning_progress
├── id (PK)
├── user_id (FK)
├── chapter_id (FK)
├── status (not_started/in_progress/completed)
├── completed_at
├── last_accessed_at
└── created_at

-- 实验提交记录
lab_submissions
├── id (PK)
├── user_id (FK)
├── lab_id (FK)
├── code
├── output
├── status (pending/running/success/failed)
├── execution_time_ms
├── created_at
└── updated_at

-- 讨论区表
discussions
├── id (PK)
├── user_id (FK)
├── course_id (FK)
├── chapter_id (FK, nullable)
├── title
├── content
├── is_pinned
├── view_count
├── created_at
└── updated_at
```

---

## 四、安全设计

### 4.1 代码执行安全

1. **容器隔离**：每个代码执行在独立Docker容器
2. **资源限制**：
   - CPU: 0.5核
   - 内存: 256MB
   - 执行时间: 30秒
   - 网络: 禁止外网访问
3. **危险代码检测**：
   - 黑名单关键字（os.system, subprocess, eval等）
   - 文件系统访问限制（只读挂载）
4. **内容安全**：
   - 输入过滤（XSS防护）
   - SQL注入防护（参数化查询）

### 4.2 用户认证安全

1. JWT Token认证（Access Token + Refresh Token）
2. 密码加密（bcrypt）
3. 登录失败限制（防暴力破解）
4. HTTPS强制

---

## 五、课程体系设计

### 5.1 学习路径

#### 原课程路径（14周/98天）
```
Path 1: AI入门 (2周/14天)
├── Day 1-14: Python for AI

Path 2: 数学基础 (1周/7天)
├── Day 15-21: 线性代数/概率论/微积分

Path 3: 机器学习 (4周/28天)
├── Day 22-49: 监督学习/无监督学习/模型优化

Path 4: 深度学习 (2周/14天)
├── Day 50-63: PyTorch/CNN/RNN

Path 5: LLM大模型 (3周/21天)
├── Day 64-84: Transformer/LangChain/RAG/Fine-tuning

Path 6: AI工程化 (2周/14天)
├── Day 85-98: MLOps/Docker/特征平台
```

#### 新增课程路径：Agent 全栈开发工程师（扩展至 21周/147天）
**目标岗位**: DeepSeek Agent 全栈开发工程师

```
Path 5+: LLM Agent 深度专题（扩展至5周/35天）
├── Day 64-70: LLM基础与Prompt Engineering [已有]
├── Day 71-75: LangChain与RAG架构 [已有]
├── Day 76-78: Fine-tuning与模型部署 [已有]
├── Day 79-81: LLM项目实战 [已有]
├── Day 82-84: Multi-Agent系统 [已有]
├── 🆕 Day 85-87: AI编程工具原理与应用（新增3天）
│   ├── Claude Code/Cursor架构解析
│   ├── Prompt Engineering进阶
│   └── AI编程助手二次开发
├── 🆕 Day 88-92: 强化学习基础（新增5天）
│   ├── MDP与Q-Learning
│   ├── Policy Gradient与Actor-Critic
│   ├── PPO算法与RLHF
│   ├── Agent训练环境搭建
│   └── LLM Agent与RL结合
├── 🆕 Day 93-96: Agent交互协议深度（新增4天）
│   ├── Function Calling与Tool Use
│   ├── MCP协议详解
│   ├── MCP Server开发实战
│   └── Agent轨迹追踪与调试
└── 🆕 Day 97-98: Agent评测平台设计（新增2天）
    ├── 评测指标体系
    └── 轨迹数据结构

Path 6+: AI工程化扩展（扩展至5周/35天）
├── Day 99-101: MLOps与MLflow [已有]
├── Day 102-104: 特征平台 [已有]
├── Day 105-106: A/B测试 [已有]
├── 🆕 Day 107-108: Docker/K8s进阶（扩展2天）
│   ├── Dockerfile多阶段构建
│   ├── GPU容器配置
│   ├── K8s Operator开发
│   └── 模型服务部署
├── 🆕 Day 109-113: Rust编程基础（新增5天）
│   ├── Rust语法与所有权系统
│   ├── 生命周期与借用检查
│   ├── 异步编程与Tokio
│   ├── PyO3: Python与Rust互调
│   └── Rust高性能AI服务开发
├── 🆕 Day 114-118: 前端技术栈（新增5天）
│   ├── TypeScript基础（对比Java）
│   ├── React组件开发
│   ├── 可视化工具开发(D3.js/ECharts)
│   └── AI应用前端框架(Streamlit/Next.js)
├── 🆕 Day 119-123: Agent评测与可视化（新增5天）
│   ├── Agent评测指标体系
│   ├── 轨迹数据结构设计
│   ├── 评测平台后端开发
│   ├── 轨迹可视化前端开发
│   └── LangSmith/Phoenix集成
└── 🆕 Day 124-126: CTF安全基础（新增3天，选修）
    ├── Web安全基础
    ├── AI安全攻防
    └── Prompt Injection实战

Path 7: 综合实战项目（3周/21天）
├── Week 1: Agent评测平台开发
│   ├── 需求分析与技术选型
│   ├── 架构设计
│   └── 数据库设计
├── Week 2: 核心功能实现
│   ├── 轨迹采集与存储
│   ├── 可视化调试界面
│   └── 评测执行引擎
└── Week 3: 部署与优化
    ├── Docker化部署
    ├── K8s编排
    └── 性能优化
```

### 5.2 新增课程模块设计

#### 模块A: AI编程工具原理与应用（3天）
**目标**: 理解Claude Code、Cursor等AI编程工具的原理，具备二次开发能力

**Day 1: AI编程工具架构解析**
- 课程内容:
  - Claude Code的Agent Loop实现机制
  - Cursor的上下文管理与Codebase理解
  - Copilot的代码补全与预测模型
  - AI编程工具的工作流程对比
- 实验任务:
  - 分析Claude Code的API调用链
  - 对比不同工具的System Prompt设计
- 产出物: 工具架构对比报告

**Day 2: 构建简单AI编程助手**
- 课程内容:
  - AST抽象语法树解析基础
  - RAG驱动的代码检索与理解
  - 多轮对话上下文管理
  - 代码生成与编辑策略
- 实验任务:
  - 使用Python构建一个极简代码问答Agent
  - 集成代码库向量检索
- 产出物: Mini Code Assistant原型

**Day 3: Prompt Engineering进阶**
- 课程内容:
  - System Prompt设计模式
  - Few-shot代码示例优化技巧
  - Chain-of-Thought编程方法
  - 代码审查Prompt设计
- 实验任务:
  - 设计代码审查Prompt模板
  - 实现代码解释与文档生成
- 产出物: Prompt模板库

#### 模块B: 强化学习基础（5天）
**目标**: 理解RL基础原理，能够将LLM Agent与强化学习结合

**Day 1-2: RL核心概念**
- MDP马尔可夫决策过程
- Q-Learning与SARSA算法
- 策略梯度方法（REINFORCE）
- Actor-Critic架构
- 实验: 使用Gym环境训练简单Agent

**Day 3-4: PPO与RLHF**
- 近端策略优化（PPO）原理
- LLM训练中的RLHF流程
- Reward Model设计
- 人类反馈数据收集
- 实验: 实现简化的RLHF流程

**Day 5: LLM Agent与RL结合**
- Tool Learning训练方法
- 反馈机制设计
- RL在Agent能力增强中的应用
- 实验: 使用RL优化Agent工具选择策略

#### 模块C: Agent交互协议深度（4天）
**目标**: 深入理解MCP、Tool Use等协议，能够开发标准化Agent系统

**Day 1: Function Calling深入**
- OpenAI Function Calling规范
- Claude Tool Use机制对比
- 工具描述Schema设计最佳实践
- 错误处理与重试策略
- 实验: 设计多工具调用链

**Day 2-3: MCP协议详解**
- Model Context Protocol规范解读
- Server/Client架构设计
- 工具发现与动态注册
- 工具链编排与依赖管理
- 实验: 实现一个MCP Server

**Day 4: Agent轨迹追踪**
- 执行过程记录与序列化
- 中间状态保存与恢复
- 调试与回放机制
- 实验: 实现Agent执行轨迹记录器

#### 模块D: Rust编程基础（5天）
**目标**: 掌握Rust基础，能够开发高性能AI服务

**Day 1: Rust基础语法**
- Rust与Java/Python对比
- 变量与数据类型
- 控制流与函数
- 所有权系统初探
- 实验: Rust编写Hello World与基础算法

**Day 2: 所有权与生命周期**
- 所有权转移与借用
- 生命周期标注
- 智能指针（Box/Rc/Arc）
- 实验: 实现链表数据结构

**Day 3: 异步编程**
- Tokio运行时
- async/await语法
- 并发与并行
- 实验: 实现异步HTTP客户端

**Day 4: Python与Rust互调**
- PyO3基础
- 编写Python扩展模块
- 性能对比测试
- 实验: 用Rust重写Python计算密集型模块

**Day 5: Rust AI服务开发**
- Candle轻量级ML框架
- ONNX Runtime集成
- 高性能推理服务
- 实验: Rust实现文本分类服务

#### 模块E: 前端技术栈（5天）
**目标**: 掌握前端开发基础，能够开发AI应用界面

**Day 1-2: TypeScript基础**
- TypeScript与Java对比
- 类型系统与接口
- 泛型与类型推断
- 实验: 重构JavaScript代码为TypeScript

**Day 3: React组件开发**
- React基础概念
- Hooks与状态管理
- 组件通信与复用
- 实验: 开发可复用的AI对话组件

**Day 4: 数据可视化**
- ECharts基础
- D3.js简介
- 时序数据可视化
- 实验: 开发Agent轨迹可视化图表

**Day 5: AI应用前端框架**
- Streamlit快速原型
- Next.js全栈开发
- 部署与优化
- 实验: 部署一个AI应用界面

#### 模块F: Agent评测与可视化（5天）
**目标**: 能够搭建Agent评测平台，开发轨迹查看和调试工具

**Day 1: 评测指标体系**
- 任务完成率、步骤效率
- 工具使用准确性
- Token效率与成本控制
- 实验: 设计评测指标框架

**Day 2: 轨迹数据模型**
- Step/Action/Observation设计
- 序列化与存储方案
- 版本兼容性
- 实验: 设计轨迹数据Schema

**Day 3: 评测平台后端**
- 批量评测执行引擎
- 结果聚合与分析
- 排行榜系统
- 实验: 实现批量评测API

**Day 4: 可视化前端**
- 步骤流程图展示
- 调试时间轴
- 对比分析视图
- 实验: 开发轨迹可视化界面

**Day 5: 平台集成**
- LangSmith/Phoenix集成
- 自定义指标上报
- 告警与通知
- 实验: 集成现有监控平台

### 5.3 实验案例设计扩展

#### 新增实验类型

1. **AI编程工具实验**
   - 实验: 分析Claude Code的API调用序列
   - 实验: 设计代码审查Prompt并评估效果
   - 实验: 实现极简代码问答Agent

2. **强化学习实验**
   - 实验: Gym环境CartPole训练
   - 实验: 使用PPO优化简单游戏策略
   - 实验: LLM Agent工具选择的RL优化

3. **MCP协议实验**
   - 实验: 实现天气查询MCP Server
   - 实验: 开发文件操作MCP工具集
   - 实验: 实现Agent轨迹记录器

4. **Rust性能实验**
   - 实验: Rust vs Python矩阵运算性能对比
   - 实验: 用Rust实现高性能文本分类
   - 实验: PyO3扩展模块开发

5. **前端可视化实验**
   - 实验: 开发Agent步骤流程图组件
   - 实验: 实现实时对话界面
   - 实验: 构建评测结果仪表板

6. **综合项目实验**
   - 项目: Agent评测平台全栈开发
   - 项目: AI编程助手二次开发
   - 项目: MCP工具链生态建设

### 5.2 实验案例设计

1. **基础实验**：Python数据处理、NumPy/Pandas操作
2. **框架实验**：LangChain链式调用、Agent构建
3. **项目实验**：完整AI应用开发（从需求到部署）
4. **团队协作实验**：多人协作开发AI Agent系统

---

## 六、开发计划

### Phase 1: 基础框架 (Week 1)
- [x] 需求分析与架构设计
- [ ] 项目脚手架搭建
- [ ] 用户认证系统
- [ ] 基础页面布局

### Phase 2: 核心功能 (Week 2-3)
- [ ] 课程管理系统
- [ ] 在线代码编辑器
- [ ] 代码执行沙箱
- [ ] 学习进度追踪

### Phase 3: 内容建设 (Week 4-5)
- [ ] 课程内容录入
- [ ] 实验环境配置
- [ ] 测试案例编写

### Phase 4: 完善与交付 (Week 6)
- [ ] 安全测试
- [ ] 性能优化
- [ ] 文档编写
- [ ] 部署上线

---

## 七、项目结构

```
ai-learning-platform/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic模型
│   │   ├── services/          # 业务逻辑
│   │   └── utils/             # 工具函数
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 测试
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # 组件
│   │   ├── pages/             # 页面
│   │   ├── hooks/             # 自定义Hooks
│   │   ├── stores/            # 状态管理
│   │   ├── services/          # API服务
│   │   └── utils/             # 工具函数
│   ├── public/
│   └── package.json
├── sandbox/                    # 代码执行沙箱
│   ├── Dockerfile
│   ├── runner.py              # 代码执行脚本
│   └── security.py            # 安全检查
├── docker-compose.yml
├── nginx.conf
└── README.md
```

---

文档版本: 1.0
创建日期: 2026-04-11
作者: AI Assistant
