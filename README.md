# AI学习平台

> 浏览器内"学→练→测→证"全链路的AI全栈工程师培养平台

## 📖 文档索引

**所有开发文档以本表为准。归档文档在 `docs/archive/`，仅供参考历史。**

| 文档 | 用途 | 何时阅读 |
|------|------|---------|
| **[PRD.md](PRD.md)** | 产品需求：做什么、为谁做、做到什么程度 | 需要理解产品目标时 |
| **[DESIGN.md](DESIGN.md)** | 架构设计：怎么做（编码agent的施工蓝图） | **编码前必读**，最核心的参考文档 |
| **[DEVELOPMENT_HARNESS.md](DEVELOPMENT_HARNESS.md)** | 开发流程：分支策略/代码风格/测试/CI/PR | 提交代码前 |
| **[README.md](README.md)** | 项目概览+快速启动（本文档） | 首次接触项目时 |

**⚠️ 归档文档**（`docs/archive/`目录）：PRD_v1、AGENT_PRD、AGENTS、TASKS、API、DEPLOYMENT、SECURITY等旧版文档，**不要参考**，已被上述文档替代。

---

## 🎯 项目概述

AI学习平台提供：
- 📚 **课程学习**：从Python基础到Agent全栈的结构化学习路径
- 💻 **在线实验**：浏览器内编写和运行Python代码，零环境配置
- ✅ **自动评测**：代码提交后自动评分，立即知道对不对
- 📊 **学习追踪**：进度可视，跨设备同步
- 🏆 **能力认证**：完成课程获得可验证证书（P2）

**北极星指标**：完成首个实验的用户比例

---

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Docker（沙箱执行需要）

### 启动后端
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

后端运行在 http://localhost:8000，API文档：http://localhost:8000/docs

### 启动前端
```bash
cd frontend
python -m http.server 3000
```

前端运行在 http://localhost:3000

### Docker Compose（推荐）
```bash
docker-compose up --build
```

---

## 📁 项目结构

```
ai-learning-platform/
├── PRD.md                      # 产品需求文档
├── DESIGN.md                   # 架构设计文档（核心）
├── DEVELOPMENT_HARNESS.md      # 开发流程规范
├── README.md                   # 本文档
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI入口
│   │   ├── core/               # 配置/数据库/安全/代码安全
│   │   ├── models/             # ORM模型
│   │   ├── schemas/            # Pydantic验证
│   │   ├── api/v1/             # API路由
│   │   ├── services/           # 业务逻辑
│   │   └── data/courses/       # 内置课程数据
│   ├── tests/                  # 测试
│   └── requirements.txt
├── frontend/
│   ├── src/                    # SPA（Vanilla JS + ES Modules）
│   │   ├── core/               # Router + Store
│   │   ├── services/           # API客户端 + 认证
│   │   ├── views/              # 页面组件
│   │   └── components/         # UI组件
│   ├── css/                    # 样式
│   └── spa.html                # SPA入口
├── sandbox/
│   ├── Dockerfile              # 沙箱镜像
│   └── runner.py               # 沙箱内代码执行器
├── docs/
│   ├── archive/                # 归档的旧版文档
│   └── CURRICULUM_DESIGN_*.md  # 课程设计文档
├── docker-compose.yml
└── nginx.conf
```

---

## 🛠️ API概览

| 模块 | 端点前缀 | 说明 |
|------|---------|------|
| 认证 | `/api/v1/auth` | 注册/登录/当前用户 |
| 课程 | `/api/v1/courses` | 课程列表/详情/章节 |
| 实验 | `/api/v1/labs` | 代码执行/提交评测/历史 |
| 进度 | `/api/v1/progress` | 学习进度/统计 |

详细API设计见 [DESIGN.md §4](DESIGN.md#四api设计)

---

## 🔐 安全特性

- ✅ JWT认证（Access + Refresh Token）
- ✅ 密码bcrypt加密
- ✅ 代码安全检查（AST分析+正则匹配）
- ✅ Docker沙箱隔离（CPU/内存/网络/超时限制）
- ✅ 输入验证（Pydantic）

已知安全问题和修复计划见 [DESIGN.md §6](DESIGN.md#六安全设计)

---

## 📝 MVP开发状态

详见 [DESIGN.md §8](DESIGN.md#八开发任务拆解)

| 任务 | 说明 | 状态 |
|------|------|------|
| T1 | 安全与基础设施修复 | 🔲 待开始 |
| T2 | 评测系统安全重构 | 🔲 待开始 |
| T3 | 进度API统一 | 🔲 待开始 |
| T4 | 前端基础增强 | 🔲 待开始 |
| T5 | 评测系统集成前端 | 🔲 待开始 |
| T6 | 测试基础设施建设 | 🔲 待开始 |
| T7 | 端到端验证 | 🔲 待开始 |

---

## 📄 License

MIT License
