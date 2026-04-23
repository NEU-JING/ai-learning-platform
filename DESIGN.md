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

```
Path 1: AI入门 (4周)
├── Week 1: Python基础
├── Week 2: 数学基础（线性代数/概率论）
├── Week 3: 机器学习基础
└── Week 4: 深度学习入门

Path 2: AI框架精通 (6周)
├── Week 1-2: LangChain基础与进阶
├── Week 3-4: AI Agent开发
├── Week 5: RAG系统构建
└── Week 6: 项目实战

Path 3: AI团队Leader (4周)
├── Week 1: AI项目管理
├── Week 2: 团队协作与代码审查
├── Week 3: AI系统架构设计
└── Week 4: 技术决策与风险管理
```

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
