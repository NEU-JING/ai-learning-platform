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

## 🔥 P1 - 课程内容优化（Agent全栈工程师方向）

基于 DeepSeek Agent 全栈开发工程师职位需求分析，新增以下课程内容优化任务。

### O11: AI编程工具原理课程 [待开始]
**状态**: pending
**优先级**: P1
**负责人**: main
**目标日期**: 2026-05-15
**对应职位要求**: 熟悉 Claude Code、Cursor 原理，有相关二次开发经验

**目标**: 开发AI编程工具原理与应用课程模块

**子任务**:
- [ ] O11.1 课程内容编写 - Claude Code架构解析
  - 文件: `content/day85_claude_code_architecture.md`
  - 内容: Agent Loop实现、上下文管理、API调用链分析
  - 验收: 包含原理讲解 + 代码示例 + 实践任务

- [ ] O11.2 课程内容编写 - Cursor与Copilot对比
  - 文件: `content/day86_ai_tools_comparison.md`
  - 内容: 各工具System Prompt设计、代码补全机制对比
  - 验收: 提供详细的架构对比表格和流程图

- [ ] O11.3 实验环境搭建 - Mini Code Assistant
  - 文件: `labs/lab_mini_code_assistant/`
  - 内容: AST解析基础、RAG代码检索、多轮对话管理
  - 验收: 学生能独立完成极简代码问答Agent开发

- [ ] O11.4 Prompt模板库建设
  - 文件: `content/resources/prompt_templates/`
  - 内容: 代码审查、代码解释、文档生成Prompt模板
  - 验收: 提供10+可用的Prompt模板及效果评估

- [ ] O11.5 前端实验界面开发
  - 文件: `frontend/src/labs/AICodingAssistant.js`
  - 功能: 在线Prompt编辑、代码对比、效果评估
  - 验收: 支持实时编辑和效果测试

**交付物**:
- 3天完整课程内容（理论+实践）
- Mini Code Assistant实验项目
- Prompt模板库（10+模板）
- 在线实验界面

---

### O12: 强化学习基础课程 [待开始]
**状态**: pending
**优先级**: P1
**负责人**: main
**目标日期**: 2026-05-22
**对应职位要求**: 集成到RL基础设施，参与Agent能力工程化

**目标**: 开发强化学习基础课程，覆盖RL到RLHF完整流程

**子任务**:
- [ ] O12.1 课程内容编写 - RL核心概念
  - 文件: `content/day88_rl_fundamentals.md`
  - 内容: MDP、Q-Learning、SARSA、策略梯度
  - 验收: 包含数学公式、Python实现、可视化展示

- [ ] O12.2 课程内容编写 - PPO与Actor-Critic
  - 文件: `content/day89_ppo_actor_critic.md`
  - 内容: PPO算法原理、Actor-Critic架构、TRPO简介
  - 验收: 提供算法伪代码和PyTorch实现

- [ ] O12.3 课程内容编写 - RLHF与LLM训练
  - 文件: `content/day90_rlhf_llm.md`
  - 内容: Reward Model设计、RLHF流程、PPO在LLM中的应用
  - 验收: 包含HuggingFace TRL库实践示例

- [ ] O12.4 课程内容编写 - LLM Agent与RL结合
  - 文件: `content/day91_llm_agent_rl.md`
  - 内容: Tool Learning训练、反馈机制、Agent能力增强
  - 验收: 提供完整的RL Agent训练代码示例

- [ ] O12.5 实验环境配置 - Gym/Gymnasium
  - 文件: `sandbox/gym_environment/`
  - 内容: 预装gym、gymnasium、stable-baselines3
  - 验收: 支持CartPole等经典环境训练

- [ ] O12.6 实验案例开发
  - 文件: `labs/lab_rl_cartpole/`、`labs/lab_rlhf/`
  - 内容: CartPole训练、PPO实现简化版、RLHF流程模拟
  - 验收: 学生能在30分钟内完成基础实验

**交付物**:
- 5天完整RL课程内容
- 3个交互式实验环境
- RL与LLM结合实战案例
- 可视化训练过程工具

---

### O13: Agent交互协议深度课程 [待开始]
**状态**: pending
**优先级**: P1
**负责人**: main
**目标日期**: 2026-05-29
**对应职位要求**: 熟悉Agent交互协议与规范（MCP、Tool Use、Function Calling）

**目标**: 深入讲解MCP协议，开发相关实验

**子任务**:
- [ ] O13.1 课程内容编写 - Function Calling深入
  - 文件: `content/day93_function_calling_deep.md`
  - 内容: OpenAI/Claude Function Calling对比、Schema设计、错误处理
  - 验收: 包含多种工具调用链设计模式

- [ ] O13.2 课程内容编写 - MCP协议规范
  - 文件: `content/day94_mcp_protocol.md`
  - 内容: MCP架构、Server/Client设计、工具发现机制
  - 验收: 提供MCP协议中文版解读

- [ ] O13.3 实验项目 - MCP Server开发
  - 文件: `labs/lab_mcp_server/`
  - 内容: 实现天气查询、文件操作、数据库查询MCP Server
  - 验收: 提供完整的Server模板和测试用例

- [ ] O13.4 课程内容编写 - Agent轨迹追踪
  - 文件: `content/day96_agent_tracing.md`
  - 内容: 执行过程记录、状态序列化、调试回放
  - 验收: 提供轨迹数据结构设计方案

- [ ] O13.5 MCP工具市场界面
  - 文件: `frontend/src/labs/MCPToolsMarket.js`
  - 功能: MCP工具浏览、安装、测试
  - 验收: 支持工具注册和在线测试

**交付物**:
- 4天MCP协议课程内容
- 可运行的MCP Server模板（3个）
- 轨迹追踪工具原型
- MCP工具市场界面

---

### O14: Rust编程基础课程 [待开始]
**状态**: pending
**优先级**: P1
**负责人**: main
**目标日期**: 2026-06-05
**对应职位要求**: 熟悉Rust，具备扎实的编程功底

**目标**: 从零开始教授Rust编程，侧重AI服务开发

**子任务**:
- [ ] O14.1 课程内容编写 - Rust基础语法
  - 文件: `content/day109_rust_basics.md`
  - 内容: Rust与Java对比、所有权系统、基础语法
  - 验收: Java开发者友好，提供对比表格

- [ ] O14.2 课程内容编写 - 所有权与生命周期
  - 文件: `content/day110_rust_ownership.md`
  - 内容: 借用检查、生命周期、智能指针
  - 验收: 包含常见编译错误及解决方案

- [ ] O14.3 课程内容编写 - Rust异步编程
  - 文件: `content/day111_rust_async.md`
  - 内容: Tokio运行时、async/await、并发模式
  - 验收: 提供HTTP服务示例代码

- [ ] O14.4 课程内容编写 - PyO3与Python互调
  - 文件: `content/day112_pyo3_integration.md`
  - 内容: PyO3基础、扩展模块开发、性能对比
  - 验收: 提供完整的Python扩展示例

- [ ] O14.5 课程内容编写 - Rust AI服务开发
  - 文件: `content/day113_rust_ai_service.md`
  - 内容: Candle框架、ONNX Runtime、推理优化
  - 验收: 提供文本分类服务完整代码

- [ ] O14.6 在线Rust编译环境
  - 文件: `sandbox/rust_environment/`
  - 内容: Rust工具链、Cargo包管理、常用库预装
  - 验收: 支持代码编写、编译、运行

**交付物**:
- 5天Rust编程课程
- 在线Rust编译环境
- Rust AI服务模板
- PyO3扩展示例

---

### O15: 前端技术栈课程 [待开始]
**状态**: pending
**优先级**: P1
**负责人**: main
**目标日期**: 2026-06-12
**对应职位要求**: 具备前端开发经验，熟练掌握TypeScript

**目标**: 补充前端开发课程，支持AI应用界面开发

**子任务**:
- [ ] O15.1 课程内容编写 - TypeScript基础
  - 文件: `content/day114_typescript_basics.md`
  - 内容: TS与Java对比、类型系统、泛型
  - 验收: 提供从Java到TS的迁移指南

- [ ] O15.2 课程内容编写 - React组件开发
  - 文件: `content/day115_react_components.md`
  - 内容: React基础、Hooks、组件通信
  - 验收: 提供AI对话组件完整代码

- [ ] O15.3 课程内容编写 - 数据可视化
  - 文件: `content/day116_data_visualization.md`
  - 内容: ECharts、D3.js简介、时序数据可视化
  - 验收: 提供Agent轨迹可视化示例

- [ ] O15.4 课程内容编写 - AI应用前端框架
  - 文件: `content/day117_ai_frontend_frameworks.md`
  - 内容: Streamlit、Next.js、Gradio对比
  - 验收: 提供快速原型开发指南

- [ ] O15.5 TypeScript实验环境
  - 文件: `sandbox/typescript_environment/`
  - 内容: Node.js、TypeScript编译器、React模板
  - 验收: 支持TS/React代码在线编辑和预览

**交付物**:
- 5天前端技术课程
- TypeScript/React在线环境
- 可视化组件库
- AI应用快速开发模板

---

### O16: Agent评测与可视化课程 [待开始]
**状态**: pending
**优先级**: P1
**负责人**: main
**目标日期**: 2026-06-19
**对应职位要求**: 有Agent评测平台、轨迹回放或可视化工具开发经验

**目标**: 开发完整的Agent评测平台课程

**子任务**:
- [ ] O16.1 课程内容编写 - 评测指标体系
  - 文件: `content/day119_evaluation_metrics.md`
  - 内容: 任务完成率、步骤效率、Token成本、工具准确性
  - 验收: 提供可量化的评测框架

- [ ] O16.2 课程内容编写 - 轨迹数据模型
  - 文件: `content/day120_trajectory_data_model.md`
  - 内容: Step/Action/Observation设计、序列化、存储
  - 验收: 提供JSON Schema定义

- [ ] O16.3 实验项目 - 评测平台后端
  - 文件: `labs/lab_eval_platform_backend/`
  - 内容: 批量评测执行、结果聚合、排行榜
  - 验收: 提供FastAPI后端模板

- [ ] O16.4 实验项目 - 轨迹可视化前端
  - 文件: `labs/lab_trajectory_visualization/`
  - 内容: 步骤流程图、时间轴、对比分析
  - 验收: 提供React组件和D3.js可视化

- [ ] O16.5 课程内容编写 - LangSmith/Phoenix集成
  - 文件: `content/day123_observability_integration.md`
  - 内容: 现有平台使用、自定义指标上报
  - 验收: 提供集成代码示例

- [ ] O16.6 评测平台原型开发
  - 文件: `frontend/src/views/EvaluationPlatform.js`
  - 功能: 评测任务管理、结果展示、轨迹回放
  - 验收: 支持上传轨迹文件并可视化展示

**交付物**:
- 5天评测平台课程
- 完整评测平台原型（前后端）
- 轨迹可视化组件库
- LangSmith/Phoenix集成指南

---

### O17: CTF安全基础课程 [待开始]
**状态**: pending
**优先级**: P2
**负责人**: main
**目标日期**: 2026-06-26
**对应职位要求**: 参与过CTF竞赛（加分项）

**目标**: 开发CTF安全基础课程（选修）

**子任务**:
- [ ] O17.1 课程内容编写 - Web安全基础
  - 文件: `content/day124_web_security.md`
  - 内容: XSS、CSRF、SQL注入基础
  - 验收: 提供漏洞示例和防护措施

- [ ] O17.2 课程内容编写 - AI安全攻防
  - 文件: `content/day125_ai_security.md`
  - 内容: Prompt Injection、模型窃取、数据投毒
  - 验收: 提供攻防实战案例

- [ ] O17.3 CTF实验环境
  - 文件: `sandbox/ctf_environment/`
  - 内容: DVWA、AI安全靶场
  - 验收: 提供安全的练习环境

**交付物**:
- 3天CTF安全课程（选修）
- AI安全攻防实验
- CTF练习环境

---

### O18: 综合实战项目 - Agent评测平台 [待开始]
**状态**: pending
**优先级**: P1
**负责人**: main
**目标日期**: 2026-07-10
**对应职位要求**: 负责Agent评测平台搭建与可视化工具开发

**目标**: 开发完整的Agent评测平台作为综合项目

**子任务**:
- [ ] O18.1 项目需求文档
  - 文件: `projects/agent_eval_platform/PRD.md`
  - 内容: 功能需求、技术选型、架构设计
  - 验收: 通过设计评审

- [ ] O18.2 数据库设计
  - 文件: `projects/agent_eval_platform/database_schema.sql`
  - 内容: 评测任务、轨迹数据、用户模型
  - 验收: 包含完整ER图和建表语句

- [ ] O18.3 后端API开发
  - 文件: `projects/agent_eval_platform/backend/`
  - 内容: FastAPI项目、评测执行引擎、结果分析
  - 验收: 覆盖核心功能的API实现

- [ ] O18.4 前端界面开发
  - 文件: `projects/agent_eval_platform/frontend/`
  - 内容: React项目、可视化组件、用户界面
  - 验收: 支持轨迹上传、可视化、回放

- [ ] O18.5 Docker部署配置
  - 文件: `projects/agent_eval_platform/docker-compose.yml`
  - 内容: 完整的多容器部署配置
  - 验收: 一键启动完整系统

- [ ] O18.6 项目文档与教程
  - 文件: `projects/agent_eval_platform/README.md`
  - 内容: 部署指南、使用教程、API文档
  - 验收: 新用户能独立完成部署

**交付物**:
- 完整的Agent评测平台项目
- 前后端分离架构
- Docker一键部署
- 详细的项目文档

---

### O19: Docker/K8s进阶课程 [待开始]
**状态**: pending
**优先级**: P1
**负责人**: main
**目标日期**: 2026-07-03
**对应职位要求**: 熟悉Docker、Kubernetes，有容器化服务部署经验

**目标**: 扩展Docker/K8s课程内容，覆盖AI服务部署

**子任务**:
- [ ] O19.1 课程内容编写 - Dockerfile多阶段构建
  - 文件: `content/day107_docker_advanced.md`
  - 内容: 多阶段构建优化、镜像体积控制
  - 验收: 提供Python/Rust项目的Dockerfile示例

- [ ] O19.2 课程内容编写 - GPU容器配置
  - 文件: `content/day107_gpu_docker.md`
  - 内容: NVIDIA Docker、CUDA环境、GPU资源共享
  - 验收: 提供PyTorch GPU容器配置

- [ ] O19.3 课程内容编写 - K8s Operator开发
  - 文件: `content/day108_k8s_operator.md`
  - 内容: CRD定义、Controller实现、模型服务部署
  - 验收: 提供简化版Operator示例

- [ ] O19.4 实验环境 - K8s集群
  - 文件: `sandbox/k8s_environment/`
  - 内容: Kind/Minikube配置、Helm Chart
  - 验收: 本地可运行的K8s学习环境

**交付物**:
- 2天Docker/K8s进阶课程
- GPU容器配置指南
- K8s Operator示例
- 本地K8s实验环境

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

