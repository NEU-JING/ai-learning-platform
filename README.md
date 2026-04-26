# AI学习平台

> 从入门到Agent全栈开发工程师的完整学习路径
> 
> 原课程: 14周/98天 | 扩展课程: 21周/147天 | 目标岗位: DeepSeek Agent全栈开发工程师

## 🎯 项目概述

AI学习平台是一个系统化的在线学习系统，提供：
- 📚 **完整课程体系**：Python基础 → LangChain框架 → AI Agent开发 → 团队领导力
- 💻 **在线实验环境**：浏览器内直接编写和运行Python代码
- 🔐 **安全沙箱**：代码执行环境完全隔离
- 📊 **学习进度追踪**：实时记录学习进度和完成情况

## 🚀 快速开始

### 1. 环境要求
- Python 3.9+
- 无需额外安装数据库（使用SQLite）

### 2. 启动后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 启动服务
python app/main.py
```

后端服务将运行在 http://localhost:8000

### 3. 启动前端
```bash
# 直接用浏览器打开 frontend/index.html
# 或使用简单的HTTP服务器
cd frontend
python -m http.server 3000
```

前端将运行在 http://localhost:3000

### 4. 访问系统
打开浏览器访问 http://localhost:3000

## 📁 项目结构

```
ai-learning-platform/
├── backend/                # FastAPI后端
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── data/          # 内置课程数据
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # 数据验证
│   │   ├── services/      # 业务逻辑
│   │   └── main.py        # 应用入口
│   └── requirements.txt
├── frontend/              # 前端页面
│   └── index.html         # 单页应用
└── README.md
```

## 📚 课程内容

### 原课程路径 (14周/98天)

#### Phase 1: Python for AI（2周/14天）
- Day 1-14: Python基础 → NumPy → Pandas

#### Phase 2: 数学基础（1周/7天）
- Day 15-21: 线性代数/概率论/微积分

#### Phase 3: 机器学习（4周/28天）
- Day 22-49: 监督学习/无监督学习/模型优化

#### Phase 4: 深度学习（2周/14天）
- Day 50-63: PyTorch/CNN/RNN

#### Phase 5: LLM大模型（3周/21天）
- Day 64-84: Transformer/LangChain/RAG/Fine-tuning

#### Phase 6: AI工程化（2周/14天）
- Day 85-98: MLOps/Docker/特征平台

### 扩展课程: Agent全栈开发工程师 (21周/147天)

基于 [DeepSeek Agent全栈开发工程师](docs/CURRICULUM_DESIGN_AGENT_FULLSTACK.md) 职位需求设计

#### Phase 5+: LLM Agent深度专题（扩展至5周/35天）
- Day 85-87: 🆕 AI编程工具原理 (Claude Code/Cursor二开)
- Day 88-92: 🆕 强化学习基础 (RLHF/Agent训练)
- Day 93-96: 🆕 Agent交互协议 (MCP/Function Calling)
- Day 97-98: 🆕 Agent评测平台设计

#### Phase 6+: AI工程化扩展（扩展至5周/35天）
- Day 107-108: 🆕 Docker/K8s进阶 (GPU容器/Operator)
- Day 109-113: 🆕 Rust编程基础 (PyO3/AI服务)
- Day 114-118: 🆕 前端技术栈 (TypeScript/React/可视化)
- Day 119-123: 🆕 Agent评测与可视化平台
- Day 124-126: 🆕 CTF安全基础 (选修)

#### Phase 7: 综合实战项目（3周/21天）
- Week 1: 需求分析与架构设计
- Week 2: 核心功能实现 (评测平台全栈开发)
- Week 3: 部署与优化 (Docker/K8s/Rust)

## 🔐 安全特性

- ✅ JWT认证
- ✅ 密码加密存储
- ✅ 代码执行沙箱（禁止危险操作）
- ✅ 执行超时限制（30秒）
- ✅ 资源限制（256MB内存）

## 🛠️ API文档

启动后端后访问：http://localhost:8000/docs

### 主要API

**认证**
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录

**课程**
- `GET /api/v1/courses/` - 课程列表
- `GET /api/v1/courses/{id}` - 课程详情
- `GET /api/v1/courses/{id}/chapters` - 章节列表
- `POST /api/v1/courses/chapters/{id}/progress` - 更新进度

**实验**
- `POST /api/v1/courses/labs/{id}/submit` - 提交代码

## 📝 开发计划

### 平台功能开发
- [x] 架构设计
- [x] 数据库模型
- [x] 用户认证
- [x] 课程管理
- [x] 代码执行沙箱
- [x] 前端页面
- [x] 社区讨论功能
- [ ] 代码编辑器增强（Monaco Editor）
- [ ] 实验自动评测
- [ ] 学习证书系统

### Agent全栈工程师课程内容开发
- [ ] AI编程工具原理课程 (Day 85-87)
- [ ] 强化学习基础课程 (Day 88-92)
- [ ] Agent交互协议深度课程 (Day 93-96)
- [ ] Rust编程基础课程 (Day 109-113)
- [ ] 前端技术栈课程 (Day 114-118)
- [ ] Agent评测与可视化课程 (Day 119-123)
- [ ] CTF安全基础课程 (Day 124-126)
- [ ] Docker/K8s进阶课程 (Day 107-108)
- [ ] 综合实战项目 (Agent评测平台)

### 实验环境扩展
- [ ] Rust在线编译环境
- [ ] TypeScript/React在线环境
- [ ] 强化学习实验环境 (Gym)
- [ ] MCP协议实验环境

## 🤝 贡献

欢迎提交Issue和PR！

## 📄 License

MIT License
