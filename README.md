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
- 📚 **课程学习**：6阶段体系（Python→数学→ML→DL→LLM→工程化），60章43实验
- 💻 **在线实验**：浏览器内编写和运行Python代码，零环境配置
- ✅ **自动评测**：代码提交后自动评分，立即知道对不对
- 📊 **学习追踪**：进度可视，跨设备同步
- 🏆 **能力认证**：完成课程获得可验证证书（P2）

**北极星指标**：完成首个实验的用户比例

---

## 🚀 快速开始

### 环境要求
- Python 3.11+
- 2核4G最低配置（推荐4核8G+80GB，Phase 3+实验需要更多RAM）
- Docker（生产环境沙箱执行需要；开发环境可用subprocess回退）

### 启动后端
```bash
cd backend
source /tmp/ailp-venv/bin/activate   # 或 python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
SERVE_STATIC=True uvicorn app.main:app --host 0.0.0.0 --port 8000
```

后端运行在 http://localhost:8000，API文档：http://localhost:8000/docs

> **注意**：`SERVE_STATIC=True` 让后端直接服务前端文件，无需单独启动前端。

### 启动前端（独立模式）
```bash
cd frontend
python -m http.server 3000
```

### Docker Compose（生产环境推荐）
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
├── AGENTS.md                   # AI Agent开发指引
├── README.md                   # 本文档
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI入口（含数据契约启动断言）
│   │   ├── core/               # 配置/数据库/安全/缓存
│   │   ├── models/             # ORM模型
│   │   ├── schemas/            # Pydantic验证
│   │   ├── api/v1/             # API路由
│   │   ├── services/           # 业务逻辑
│   │   └── data/               # 种子数据（6阶段课程体系）
│   │       ├── courses.py              # 课程壳定义 + PHASE_TITLES
│   │       ├── courses_phase1.py       # Phase 1 加载器（upsert）
│   │       ├── courses_phase2.py       # Phase 2 加载器（upsert）
│   │       ├── courses_phase3_6.py     # Phase 3-6 加载器（create_only）
│   │       ├── courses_extended_fixed.py  # Phase 3-6 种子数据
│   │       ├── phase1/                 # Phase 1 JSON内容
│   │       └── phase2/                 # Phase 2 JSON内容
│   ├── tests/                  # 测试（78个）
│   │   ├── test_data_contract.py   # 🚨 数据契约测试（16项）
│   │   ├── test_auth.py
│   │   ├── test_code_security.py
│   │   ├── test_courses.py
│   │   └── test_code_execution.py
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
│   ├── Dockerfile              # Docker沙箱镜像
│   └── runner.py               # 沙箱内代码执行器
├── docs/
│   ├── archive/                # 归档的旧版文档
│   └── OPERATIONS.md           # 运维手册
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
- ✅ 数据契约三道防线（启动断言+契约测试+init行为声明）

已知安全问题和修复计划见 [DESIGN.md §6](DESIGN.md#六安全设计)

---

## 🛡️ 数据契约三道防线

为防止数据不一致问题再次发生，系统实现了三道防线：

| 防线 | 机制 | 检查时机 |
|------|------|---------|
| 第一道 | `_assert_data_contract()` 启动断言 | 服务启动时，违反则拒绝启动 |
| 第二道 | `test_data_contract.py` 契约测试（16项） | CI/CD流水线 |
| 第三道 | init函数`behavior`参数声明 | 代码层约束 |

**契约规则**：6门发布课程、标题属于6阶段体系、无孤例/重复、每课≥1章、solution_code不可通过公开API获取。

---

## 📝 开发状态

| 模块 | 状态 | 说明 |
|------|------|------|
| 6阶段课程体系 | ✅ 已完成 | 60章43实验，6门课程全部发布 |
| 用户认证系统 | ✅ 已完成 | JWT注册/登录/刷新 |
| 代码执行沙箱 | ⚠️ 部分可用 | Docker模式需4核8G+服务器，当前subprocess回退 |
| 数据契约防护 | ✅ 已完成 | 三道防线，78测试全绿 |
| 前端SPA | ✅ 已完成 | Vanilla JS，后端SERVE_STATIC |
| 评测系统集成 | 🔲 待完善 | 评测逻辑存在但前端集成未完成 |
| Alembic迁移 | 🔲 待开始 | 仍用init_db()建表 |
| CI/CD流水线 | 🔲 待开始 | 无GitHub Actions |

---

## 📄 License

MIT License
