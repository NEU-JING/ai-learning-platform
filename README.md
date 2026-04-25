
# AI学习平台

> 从Python基础到AI团队Leader的完整培养体系

## 项目概述

本项目是一个完整的AI学习平台，提供：

- 📚 **完整课程体系**：从Python基础到AI团队管理的完整路径
- 💻 **在线实验环境**：浏览器内直接编写和运行Python代码
- 🤖 **AI Agent实战**：LangChain、RAG等主流框架实战
- 👥 **团队协作**：模拟AI团队开发流程
- 🏆 **能力认证**：学习证书与能力评估

## 学习路径

### Phase 1: Python基础与AI工具链 (2周/14天)
- Python vs Java语法对比
- NumPy数值计算
- Pandas数据处理
- 可视化与效率优化
- **产出**：能够使用Python进行数据处理

### Phase 2: 数学基础 (1周/7天)
- 线性代数基础
- 概率论与统计
- 微积分与优化
- **产出**：理解AI所需的数学基础

### Phase 3: 机器学习 (4周/28天)
- Scikit-Learn框架
- 监督学习算法（回归、分类、集成）
- 无监督学习（聚类、降维）
- 模型评估与优化
- **产出**：能够独立完成ML项目

### Phase 4: 深度学习 (2周/14天)
- PyTorch基础
- CNN与RNN
- 训练技巧与工程化
- **产出**：能够构建神经网络

### Phase 5: LLM大模型 (3周/21天)
- Transformer架构
- BERT与GPT
- Prompt Engineering
- LangChain框架
- RAG系统构建
- **产出**：能够开发AI应用

### Phase 6: AI工程化 (2周/14天)
- 模型部署与服务化
- MLOps与监控
- AI系统架构设计
- **产出**：具备AI工程化能力

## 技术栈

### 后端
- Python 3.11 + FastAPI
- PostgreSQL + Redis
- Docker（代码沙箱）
- SQLAlchemy（ORM）

### 前端
- HTML5 + CSS3 + Vanilla JavaScript（简化方案）
- Monaco Editor（代码编辑）
- Marked.js（Markdown渲染）
- Highlight.js（代码高亮）

## 快速开始

### 方式一：Docker Compose（推荐）

```bash
cd ai-learning-platform
docker-compose up -d

# 访问 http://localhost:3000
```

### 方式二：本地开发

```bash
# 1. 启动数据库
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15
docker run -d -p 6379:6379 redis:7

# 2. 安装后端依赖
cd backend
pip install -r requirements.txt

# 3. 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. 访问前端（直接打开HTML文件或使用本地服务器）
cd ../frontend
python -m http.server 3000
# 访问 http://localhost:3000
```

## 项目结构

```
ai-learning-platform/
├── backend/              # FastAPI后端
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── models/      # 数据库模型
│   │   ├── services/    # 业务逻辑
│   │   └── data/        # 内置课程数据
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # HTML/JS前端
│   ├── index.html       # 课程列表
│   ├── course.html      # 课程详情
│   ├── chapter.html     # 章节内容
│   ├── lab.html         # 代码实验
│   ├── login.html       # 登录
│   ├── register.html    # 注册
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js
│       ├── auth.js
│       └── app.js
├── sandbox/              # 代码执行沙箱
│   ├── Dockerfile
│   └── runner.py
├── docker-compose.yml
└── nginx.conf
```

## 核心功能

### 1. 课程学习
- Markdown格式的课程内容
- 代码高亮和复制
- 学习进度追踪

### 2. 在线实验
- Monaco代码编辑器
- 实时代码执行
- 自动评测

### 3. 完整知识体系
所有课程内容内置在平台中，无需外部资源：
- Python编程
- 数学基础
- 机器学习
- 深度学习
- LangChain
- AI Agent开发
- 团队管理

## 开发计划

- [x] 架构设计
- [x] 数据库模型
- [x] 完整课程内容（14周98天）
- [x] 后端API实现
- [x] 前端界面开发
- [x] 代码执行沙箱
- [x] Docker部署配置
- [x] 测试与优化
- [x] 部署上线
- [x] 运维文档
- [x] API文档

**🎉 项目已完成100%！**

## 许可证

MIT License
