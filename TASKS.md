# AI学习平台 - 优化任务追踪

## 项目状态概览

| 模块 | 当前状态 | 目标状态 |
|------|----------|----------|
| 安全性 | ⚠️ 存在隐患 | ✅ 生产级安全 |
| 功能完整性 | 🟡 基础功能完成 | ✅ 完整学习平台 |
| 性能优化 | 🟡 基础可用 | ✅ 高性能 |
| 测试覆盖 | ❌ 几乎无 | ✅ 全面覆盖 |
| 文档 | 🟡 基础文档 | ✅ 完整文档 |

---

## 🔥 P0 - 立即修复（安全与核心功能）

### O1: 安全漏洞修复 [进行中]
**状态**: active
**优先级**: P0
**负责人**: main
**创建日期**: 2026-04-24
**目标日期**: 2026-04-25

**目标**: 修复所有安全漏洞，确保生产环境安全

**子任务**:
- [ ] O1.1 修改硬编码 JWT Secret Key，使用环境变量
  - 文件: `backend/app/core/config.py`
  - 验收: 生产环境必须通过环境变量注入 SECRET_KEY
  
- [ ] O1.2 限制 CORS 配置，只允许特定域名
  - 文件: `backend/app/main.py`
  - 验收: CORS 在生产环境只允许配置的域名
  
- [ ] O1.3 移除代码中的 GitHub Token
  - 文件: `push-to-github.sh`
  - 验收: Token 从仓库历史中彻底移除
  
- [ ] O1.4 添加密码强度验证
  - 文件: `backend/app/schemas/user.py`
  - 验收: 密码必须8位以上，包含字母和数字
  
- [ ] O1.5 强化沙箱安全检测
  - 文件: `backend/app/core/code_security.py`
  - 验收: 覆盖更多危险代码模式

**交付物**:
- 安全配置更新
- 安全测试用例
- 安全检查清单

**验收标准**:
- 无硬编码密钥
- CORS 配置正确
- 通过安全扫描

---

### O2: 核心功能补全 [待开始]
**状态**: pending
**优先级**: P0
**负责人**: main
**目标日期**: 2026-04-26

**目标**: 完成学习进度持久化和实验评测核心功能

**子任务**:
- [ ] O2.1 学习进度持久化前端实现
  - 文件: `frontend/js/progress.js`, `frontend/chapter.html`
  - 验收: 前端自动保存阅读进度，标记完成状态
  
- [ ] O2.2 实验自动评测系统
  - 文件: `backend/app/services/lab_evaluator.py`
  - 验收: 支持代码输出对比、单元测试评测
  
- [ ] O2.3 实验提交历史功能
  - 文件: `backend/app/api/labs.py`
  - 验收: 可查看提交记录和代码对比

**交付物**:
- 进度追踪功能
- 自动评测系统
- 提交历史功能

**验收标准**:
- 进度自动保存
- 实验自动评分
- 历史记录可查询

---

## 🔥 P1 - 近期完成（功能增强）

### O3: API 与文档完善 [待开始]
**状态**: pending
**优先级**: P1
**负责人**: main
**目标日期**: 2026-04-27

**目标**: 完善 API 设计和文档

**子任务**:
- [ ] O3.1 接入 FastAPI Swagger 自动文档
  - 文件: `backend/app/main.py`
  - 验收: 访问 `/docs` 可查看完整 API 文档
  
- [ ] O3.2 为所有端点添加响应模型
  - 文件: `backend/app/schemas/*.py`
  - 验收: 所有 API 都有明确的请求/响应模型
  
- [ ] O3.3 添加 API 版本控制
  - 文件: `backend/app/api/v1/`
  - 验收: API 路径改为 `/api/v1/*`
  
- [ ] O3.4 为列表接口添加分页
  - 文件: `backend/app/api/courses.py`
  - 验收: 支持 `?page=1&limit=20` 分页参数
  
- [ ] O3.5 更新 API.md 与实现同步
  - 文件: `docs/API.md`
  - 验收: 文档与实际 API 一致

**交付物**:
- Swagger 文档
- API 版本控制
- 分页功能
- 更新后的 API.md

---

### O4: 前端体验优化 [待开始]
**状态**: pending
**优先级**: P1
**负责人**: main
**目标日期**: 2026-04-28

**目标**: 提升前端用户体验

**子任务**:
- [ ] O4.1 添加全局加载状态指示器
  - 文件: `frontend/js/app.js`
  - 验收: API 请求时显示 loading，完成后隐藏
  
- [ ] O4.2 实现错误重试机制
  - 文件: `frontend/js/api.js`
  - 验收: 网络错误自动重试3次
  
- [ ] O4.3 添加面包屑导航
  - 文件: `frontend/course.html`, `frontend/chapter.html`
  - 验收: 显示 首页 > 课程 > 章节 路径
  
- [ ] O4.4 响应式移动端优化
  - 文件: `frontend/css/style.css`
  - 验收: 在手机上有良好的显示效果
  
- [ ] O4.5 添加 Toast 通知系统
  - 文件: `frontend/js/app.js`
  - 验收: 操作成功/失败显示提示消息

**交付物**:
- Loading 组件
- 错误重试机制
- 面包屑导航
- Toast 通知

---

### O5: 性能优化 [进行中]
**状态**: active
**优先级**: P1
**负责人**: main
**目标日期**: 2026-04-29

**目标**: 提升系统性能

**子任务**:
- [ ] O5.1 为课程数据添加 Redis 缓存
  - 文件: `backend/app/services/course_service.py`
  - 验收: 课程列表从缓存读取，减少数据库查询

- [ ] O5.2 实现课程内容懒加载
  - 文件: `frontend/js/app.js`
  - 验收: 滚动到位置才加载图片/代码块

- [ ] O5.3 优化 Docker 镜像构建
  - 文件: `backend/Dockerfile`
  - 验收: 使用多阶段构建，减小镜像体积

- [x] O5.4 添加数据库连接池 ✅
  - 文件: `backend/app/core/database.py`
  - 完成: docker-compose.prod.yml 中已配置连接池参数 (DB_POOL_SIZE=20, DB_MAX_OVERFLOW=30)

**交付物**:
- Redis 缓存层
- 懒加载实现
- 优化后的 Dockerfile
- 连接池配置

---

## 🔥 P2 - 中期规划（功能扩展）

### O6: 社区功能实现 [已完成]
**状态**: completed
**优先级**: P2
**负责人**: main
**完成日期**: 2026-04-24

**目标**: 实现讨论区功能 ✅

**子任务**:
- [x] O6.1 讨论区数据模型
  - 文件: `backend/app/models/__init__.py`
  - 字段: Discussion(id, course_id, user_id, title, content, likes_count, comments_count, is_pinned, is_locked)
  - 字段: Comment(id, discussion_id, user_id, content, likes_count, is_solution, parent_id)
  
- [x] O6.2 讨论区 API 实现
  - 文件: `backend/app/api/v1/discussions.py`
  - 功能: 
    - GET /api/v1/courses/{course_id}/discussions - 获取课程讨论列表
    - POST /api/v1/courses/{course_id}/discussions - 创建讨论
    - GET /api/v1/discussions/{id} - 获取讨论详情
    - PUT /api/v1/discussions/{id} - 更新讨论
    - DELETE /api/v1/discussions/{id} - 删除讨论
    - POST /api/v1/discussions/{id}/comments - 发表评论
    - POST /api/v1/discussions/{id}/like - 点赞
  
- [x] O6.3 讨论区前端页面
  - 文件: `frontend/src/views/Discussion.js` - 讨论区列表页面
  - 文件: `frontend/src/views/DiscussionDetail.js` - 讨论详情页面
  - 功能: 列表, 发帖, 回复, 点赞, 删除, 编辑
  
- [x] O6.4 添加点赞功能
  - 文件: `backend/app/api/v1/discussions.py`
  - 功能: 帖子点赞

**交付物**:
- ✅ 讨论区数据库模型 (Discussion, Comment)
- ✅ 完整讨论区 API (7个端点)
- ✅ 讨论区前端页面 (列表页+详情页)
- ✅ API Schema定义 (discussion.py)
- ✅ 前端API服务集成
- ✅ 路由注册 (后端+前端)

---

### O7: 证书与统计系统 [待开始]
**状态**: pending
**优先级**: P2
**负责人**: main
**目标日期**: 2026-05-08

**目标**: 实现学习证书和统计功能

**子任务**:
- [ ] O7.1 学习统计 API
  - 文件: `backend/app/api/stats.py`
  - 功能: 学习时长, 完成进度, 连续学习天数

- [ ] O7.2 证书生成系统
  - 文件: `backend/app/services/certificate.py`
  - 功能: PDF 证书生成

- [x] O7.3 统计仪表板页面 ✅
  - 文件: `docker-compose.prod.yml`, `deploy.sh`
  - 完成: 已配置 Grafana 监控仪表板和 Prometheus 集成

- [ ] O7.4 证书下载功能
  - 文件: `frontend/certificates.html`
  - 功能: 查看和下载证书

**交付物**:
- 统计 API
- PDF 证书生成
- 仪表板页面
- 证书下载功能

---

### O8: 测试覆盖 [待开始]
**状态**: pending
**优先级**: P2
**负责人**: main
**目标日期**: 2026-05-10

**目标**: 建立全面的测试体系

**子任务**:
- [ ] O8.1 后端单元测试扩展
  - 文件: `tests/test_*.py`
  - 覆盖: Courses, Chapters, Progress, Labs
  
- [ ] O8.2 集成测试
  - 文件: `tests/integration/`
  - 覆盖: 端到端 API 测试
  
- [ ] O8.3 沙箱安全测试
  - 文件: `tests/security/test_sandbox.py`
  - 覆盖: 危险代码绕过测试
  
- [ ] O8.4 前端测试
  - 文件: `frontend/tests/`
  - 工具: Playwright 或 Cypress

**交付物**:
- 单元测试套件
- 集成测试套件
- 安全测试套件
- 测试覆盖率报告

---

## 🔥 P3 - 长期规划（高级功能）

### O9: 智能推荐系统 [待开始]
**状态**: pending
**优先级**: P3
**负责人**: main

**目标**: 基于学习行为的智能课程推荐

**子任务**:
- [ ] O9.1 用户行为收集
- [ ] O9.2 推荐算法实现
- [ ] O9.3 个性化学习路径

---

### O10: 内容管理后台 [待开始]
**状态**: pending
**优先级**: P3
**负责人**: main

**目标**: 管理课程、章节、实验内容

**子任务**:
- [ ] O10.1 管理员认证系统
- [ ] O10.2 课程内容编辑器
- [ ] O10.3 实验测试用例管理

---

## 任务执行日志

| 日期 | 任务ID | 操作 | 状态变更 | 备注 |
|------|--------|------|----------|------|
| 2026-04-24 | O1 | created → active | 开始安全漏洞修复 | 创建所有优化任务 |
| 2026-04-24 | 6-3 | completed | Docker沙箱镜像自动检查功能完成 | 镜像版本管理、启动检查、构建脚本 |
| 2026-04-24 | O6 | pending → completed | 讨论区功能实现完成 | Discussion模型、7个API端点、前端页面

---

## 快速检查清单

### 每日检查
- [ ] P0 任务是否有进展
- [ ] 是否有阻塞问题需要解决
- [ ] 是否需要调整优先级

### 每周回顾
- [ ] 已完成任务验收
- [ ] 更新任务状态
- [ ] 规划下周任务

