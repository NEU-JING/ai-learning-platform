# AI学习平台

> 从入门到AI团队Leader的完整学习路径

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

### Phase 1: Python for AI（入门）
- Day 1: Python快速上手
- Day 2: Python函数与类
- Day 3: NumPy基础
- Day 4: Pandas数据操作
- ...更多章节

### Phase 2: LangChain框架（进阶）
- LangChain基础概念
- Prompt模板与Chain
- Agent与工具调用
- Memory记忆管理

### Phase 3: AI Agent开发（高级）
- 多Agent协作架构
- RAG系统构建
- 自动化工作流
- 项目实战

### Phase 4: AI团队领导力（专家）
- AI项目管理
- 技术决策与架构设计
- 团队协作与代码审查
- 风险控制与质量保证

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

- [x] 架构设计
- [x] 数据库模型
- [x] 用户认证
- [x] 课程管理
- [x] 代码执行沙箱
- [x] 前端页面
- [ ] 代码编辑器增强（Monaco Editor）
- [ ] 实验自动评测
- [ ] 学习证书系统
- [ ] 社区讨论功能

## 🤝 贡献

欢迎提交Issue和PR！

## 📄 License

MIT License
