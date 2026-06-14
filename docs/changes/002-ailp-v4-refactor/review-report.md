# Phase 3 代码评审报告 — Sandbox + Profile + Employer

> **变更 ID**: 002-ailp-v4-refactor  
> **评审日期**: 2026-06-14  
> **评审范围**: Phase 3 (AC38-AC49): Sandbox Module, Profile Module, Employer Module  
> **评审方法**: 三阶段独立评审 (Spec 合规 → 代码质量 → 架构一致性)  
> **代码量**: +1858 行，5 次提交

---

## 评审结论: 🔴 不通过

**理由**: 存在 2 个 CRITICAL 问题（AC46/AC48/AC49 缺少 API 集成测试、AC43 路径感知未实现）和 1 个 MAJOR 架构不一致问题（Profile 路由路径与 Design 不匹配），必须修复后重新评审。

---

## Phase 1: Spec 合规

### AC 覆盖矩阵

| AC | 场景 | 测试覆盖 | 实现深度 | 状态 |
|:--:|------|:---:|------|:---:|
| AC38 | 本地沙箱执行 | ✅ 6 测试 | 功能实现：subprocess 执行+自动评分+DB 持久化 | ✅ PASS |
| AC39 | 外部资源训练 | ✅ 3 测试 | 功能实现：provider 校验+job_id 生成+webhook_url | ✅ PASS |
| AC40 | 验证引擎审计 | ✅ 2 测试 | 功能实现：metrics 计算+audit_log+pass/fail | ✅ PASS |
| AC41 | 验证失败处理 | ✅ 1 测试 | 功能实现：epochs>0 AND loss<0.5 判定逻辑 | ✅ PASS |
| AC42 | 混合流程完成 | ✅ 3 测试 | 功能实现：layers_completed 记录+状态更新 | ✅ PASS |
| AC43 | 路径感知主页 | ❌ 0 测试 | **仅建表**：UserProfile 建表但 GET /profile/{username} 不执行路径感知高亮 | 🔴 CRITICAL |
| AC44 | 隐私控制 | ✅ 16 测试 | 功能实现：4 维度独立控制+show_all/hide_all+BR5 逻辑 | ✅ PASS |
| AC45 | 验证 URL+授权码 | ✅ 4 测试 | 功能实现：HTML 页面渲染+证书信息+吊销状态 | ✅ PASS |
| AC46 | 数字签名验证 API | ❌ 0 测试 | **仅建路由**：端点存在但无 API 级集成测试（无 API Key auth 测试） | 🔴 CRITICAL |
| AC47 | 审计日志完整记录 | ❌ 0 测试 | **仅表存在**：log_api_call 被调用但无测试验证日志写入 | 🟡 MAJOR |
| AC48 | 雇主 API 限流 | ❌ 0 测试 | **功能实现**：in-memory RateLimiter 存在但无集成测试验证 429 | 🔴 CRITICAL |
| AC49 | 授权码验证机制 | ❌ 0 测试 | **仅建路由**：端点存在但无集成测试（无 API Key+code 组合测试） | 🔴 CRITICAL |

### AC 深度检查

#### AC38 — Layer A 本地执行 ✅
- **建表**: execution_requests 表完整（14 列）
- **功能**: `SandboxService.execute_layer_a()` → subprocess 执行 → 自动评分（CodeGrader）→ DB 持久化
- **验证**: 6 个测试覆盖正常执行、错误执行、自动评分、未授权、DB 记录、缺字段 422

#### AC39 — Layer B 外部资源 ✅
- **建表**: external_executions 表完整（8 列）
- **功能**: `SandboxService.submit_external()` → provider 白名单校验 → UUID job_id → webhook_url
- **验证**: 3 测试覆盖 kaggle 提交、未授权、未知 provider

#### AC40-AC41 — Layer C 验证引擎 ✅
- **建表**: verification_tasks 表完整（9 列）
- **功能**: `SandboxService.verify_model()` → JSON 解析 training_log → 计算 metrics → pass/fail
- **验证**: 2 测试覆盖正常验证和失败处理

#### AC42 — 混合流程 ✅
- **功能**: `complete_hybrid_flow()` → layers_completed 记录+状态标记
- **验证**: 3 测试覆盖正常完成、未授权、不存在请求

#### AC43 — 路径感知主页 🔴
- **建表**: UserProfile 模型存在 5 新字段（privacy_settings, custom_title, theme, view_count, last_synced_at）
- **功能缺失**: 
  - `profile_service.get_public_profile()` 调用 `SkillRadarService.get_skill_radar()` 时**未传递 path_type 参数**
  - Design 要求: "突出显示'工程实现'和'系统设计'维度，隐藏'研究深度'"
  - radar_service 虽有 path_type 支持但 profile 路由未使用
- **Spec 对应**: "突出显示'工程实现'和'系统设计'维度，淡化'研究深度'" — 未实现

#### AC44 — 隐私控制 ✅
- **功能**: 4 维度独立 toggles + BR5 逻辑（is_public false→true 自动开启全部）+ batch 操作
- **验证**: 16 测试覆盖首次启用、关闭、重新启用、维度切换、batch 操作、display_name 校验、bio 长度限制

#### AC45 — 验证页面 ✅
- **功能**: `GET /verify/{cert_number}` → HTML 响应 → 证书等级/持有者/日期/实验数/签名/吊销状态
- **验证**: 4 测试覆盖 HTML 返回、内容校验、不存在证书、吊销状态

#### AC46 — 数字签名验证 🔴
- **路由存在**: `POST /api/v1/employer/verify` + `get_api_key_employer` 依赖注入
- **测试缺失**: 无 API 级测试；无法验证 X-API-Key header 认证流程、ECDSA 签名验证端到端行为

#### AC47 — 审计日志 🟡
- **表存在**: employer_api_logs 表完整
- **代码调用**: `log_api_call()` 在 verify 和 query 端点被调用
- **测试缺失**: 无测试验证 API 调用后在 employer_api_logs 中生成记录
- **风险**: log_api_call 的 `except Exception: db.rollback()` 静默吞掉所有错误

#### AC48 — 限流 🔴
- **代码存在**: `RateLimiter` 类实现 in-memory 计数器 + `get_api_key_employer` 依赖注入
- **测试缺失**: 无测试验证第 1001 次请求返回 429 + `X-RateLimit-Remaining: 0` 头

#### AC49 — 授权码查询 🔴
- **路由存在**: `POST /api/v1/employer/query`
- **测试缺失**: 无测试验证授权码过期、权限过滤（certifications/skill_summary/lab_history）、未授权字段返回

### Out of Scope 合规 ✅

检查 Spec §7 的 5 项 Out of Scope：
- ❌ 自建 GPU 集群 — 未实现 ✅
- ❌ 免费 LLM API — 未实现 ✅
- ❌ K8s 实训环境 — 未实现 ✅
- ❌ 招聘平台 — 未实现 ✅
- ❌ "找到工作"承诺 — 未实现 ✅

---

## Phase 2: 代码质量

### Lint 检查 (ruff check . --select=E,W,F)

| 文件 | 行号 | 问题 | 严重度 |
|------|:---:|------|:---:|
| `app/api/v1/employer.py` | 11 | F401: `fastapi.status` imported but unused | MINOR |
| `app/services/employer.py` | 11 | F401: `time` imported but unused | MINOR |
| `app/models/sandbox.py` | 3 | F401: `sqlalchemy.Float` imported but unused | MINOR |
| `app/api/v1/employer.py` | 79 | E501: Line too long (105 > 100) | MINOR |
| `app/models/employer.py` | 86 | E501: Line too long (103 > 100) | MINOR |
| `app/models/sandbox.py` | 1 | E501: Line too long (109 > 100) | MINOR |

**总计**: 0 ERROR, 0 WARNING, 3 unused imports, 3 line-too-long

### 函数长度检查

| 文件 | 函数 | 行数 | 状态 |
|------|------|:---:|:---:|
| `sandbox.py` | `_execute_code_sync` | 79 行 | ❌ >50 |
| `sandbox.py` | `execute_layer_a` | 86 行 | ❌ >50 |
| `sandbox.py` | `verify_model` | 62 行 | ❌ >50 |
| `employer.py` | `render_verify_page` | 112 行 | ❌ >50 (含 HTML 模板) |
| `employer.py` | `query_by_code` | 70 行 | ❌ >50 |
| `profile_service.py` | `_get_certificates` | 52 行 | ⚠️ 接近上限 |
| `profile_service.py` | `update_settings` | 88 行 | ❌ >50 |

**结论**: `sandbox.py` 的函数需要拆分，特别是 `_execute_code_sync`（模板生成+执行+解析混合）和 `render_verify_page`（业务逻辑+HTML 模板混合）。

### DRY / YAGNI

| 问题 | 位置 | 严重度 |
|------|------|:---:|
| `verify_signature` 第 299 行 `__import__("datetime").timedelta(days=730)` — 内联动态导入，应使用标准 `from datetime import timedelta` | `employer.py:299` | MINOR |
| `_execute_code_sync` 包装模板硬编码在函数体内（约 40 行），应提取为模块级常量或单独函数 | `sandbox.py:31-67` | MINOR |
| `render_verify_page` 和 `_error_html` 中 HTML 模板嵌入在 f-string 中，CSS 重复 | `employer.py:151-253` | MINOR |

### 命名

| 问题 | 位置 | 严重度 |
|------|------|:---:|
| `profile_service.py` 中 `_get_certificates` 实际返回的是"已完成的课程"而非正式的 `Certificate` ORM 记录，名称有误导性 | `profile_service.py:382` | MINOR |
| `query_by_code` 接受的参数名是 `verification_code` 但函数名用 `by_code` 不够明确 | `employer.py:309` | INFO |
| 模块级变量 `rate_limiter`（小写）是 `RateLimiter` 实例，按惯例应为 `_rate_limiter` 标记为模块私有 | `employer.py:57` | INFO |

### 错误处理

| 问题 | 位置 | 严重度 |
|------|------|:---:|
| `log_api_call` 在 `except Exception` 中静默吞掉所有异常(`db.rollback()`)，不记录日志，可能导致审计日志静默丢失 | `employer.py:97-109` | 🟡 MAJOR |
| `_execute_code_sync` 使用 `exec()` 执行用户代码 — 虽然有子进程隔离但不能完全消除风险，建议添加更明确的文档注释 | `sandbox.py:42` | INFO |
| `render_verify_page` 的 `cert.cert_metadata.get(...)` 链式访问若 `cert_metadata` 为 None 会抛 AttributeError | `employer.py:137-138` | 已处理 ✅ |

### LLM 依赖检查

本 Phase 未引入 LLM 调用。沙箱 execution 通过 subprocess 实现，验证引擎为纯计算逻辑。无需 mock LLM。

### 性能问题

| 问题 | 位置 | 严重度 |
|------|------|:---:|
| **N+1 查询**: `_get_certificates` 查询全部 Course（1 次），对每个 Course 分别查 Chapter（N 次）和 LearningProgress（N 次）。在 6 门课程场景下可接受，但随课程增长线性恶化。建议用 JOIN 一次性查询 | `profile_service.py:392-410` | 🟡 MAJOR |
| `RateLimiter` 使用 `defaultdict(dict)` 纯内存存储，无过期清理机制 — 运行时内存会持续增长（每小时一个 key） | `employer.py:30-31` | 🟡 MAJOR |
| `query_by_code` 中按需导入 `Certificate`、`UserSkillScore`、`LabSubmission`（lazy import in function body）增加了首次调用的延迟 | `employer.py:340-367` | MINOR |

---

## Phase 3: 架构一致性

### 模块划分

| Design 模块 | 实现文件 | 一致性 |
|------|------|:---:|
| `design-module-sandbox.md` | `models/sandbox.py` + `services/sandbox.py` + `api/v1/sandbox.py` + `schemas/sandbox.py` | ✅ |
| `design-module-profile.md` | `models/user_profile.py` + `models/profile_cache.py` + `services/profile_service.py` + `api/v1/profile.py` | ✅ |
| `design-module-employer.md` | `models/employer.py` + `services/employer.py` + `api/v1/employer.py` + `schemas/employer.py` | ✅ |

### API 接口定义对比

| Design 定义 | 实现 | 状态 |
|------|------|:---:|
| `POST /api/v1/sandbox/execute` | `POST /api/v1/sandbox/execute` | ✅ 一致 |
| `POST /api/v1/sandbox/external/submit` | `POST /api/v1/sandbox/external/submit` | ✅ 一致 |
| `POST /api/v1/sandbox/verify` | `POST /api/v1/sandbox/verify` | ✅ 一致 |
| `GET /p/{username}` 或 `GET /api/v1/profiles/{username}` | `GET /api/v1/profile/{username}` | 🟡 不一致 (Design 用复数 `profiles`，实现用单数 `profile`) |
| `PUT /api/v1/profile/privacy` | `PUT /api/v1/profile/me/settings` | 🔴 路由路径完全不一致 |
| `GET /verify/{cert_number}` | `GET /verify/{cert_number}` | ✅ 一致 |
| `POST /api/v1/employer/verify` | `POST /api/v1/employer/verify` | ✅ 一致 |
| `POST /api/v1/employer/query` | `POST /api/v1/employer/query` | ✅ 一致 |

### 数据模型对比

| Design 表 | 实现模型 | 差异 |
|------|------|------|
| `execution_requests` | `ExecutionRequest` | ✅ 一致 |
| `external_executions` | `ExternalExecution` | ✅ 一致 |
| `verification_tasks` | `VerificationTask` | ✅ 一致 |
| `sandbox_providers` | `SandboxProvider` | ✅ 一致 |
| `user_profiles` | `UserProfile` | ✅ + 额外字段（show_basic_info 等 4 个布尔维度替代 JSONB privacy_settings 作为主要维度控制，privacy_settings JSONB 存在但未被服务层使用） |
| `profile_cache` | `ProfileCache` | ✅ 一致 |
| `employers` | `Employer` | ✅ 一致 |
| `verification_codes` | `VerificationCode` | ✅ 一致 |
| `employer_api_logs` | `EmployerApiLog` | ✅ 一致 |

### 数据流对比

| Design 流程 | 实现 | 状态 |
|------|------|:---:|
| User Request → CDN (1h) → Redis (30m) → DB | 未实现 CDN/Redis 缓存层。ProfileCache 表存在但无实际缓存读写逻辑 | 🟡 MAJOR |
| Layer A: 本地进程 2核4G | subprocess.run() 无资源限制（无 cgroup/Docker） | 🟡 MAJOR |
| Rate Limit: Redis INCR + EXPIRE | in-memory defaultdict，非 Redis | 🟡 MAJOR |

---

## 问题汇总

### 🔴 CRITICAL (阻塞提交)

| # | 问题 | AC | 位置 | 修复建议 |
|:--:|------|:--:|------|------|
| C1 | AC46 缺少 API 级集成测试（X-API-Key 认证 + ECDSA 签名验证端到端） | AC46 | `tests/test_employer.py` | 新增测试类 `TestSignatureVerifyAPI`，覆盖：有效签名→200、无效签名→400、无 API Key→401、错误 API Key→403 |
| C2 | AC48 缺少限流集成测试（第 1001 次请求应返回 429） | AC48 | `tests/test_employer.py` | 新增测试 `test_rate_limit_429`，循环调用 1001 次后验证 429 + X-RateLimit-Remaining 头 |
| C3 | AC49 缺少授权码查询集成测试 | AC49 | `tests/test_employer.py` | 新增测试类 `TestAuthCodeQuery`，覆盖：有效码→200、过期码→400、权限过滤、未授权字段 |
| C4 | AC43 路径感知主页未实现 — profile API 未传递 path_type 给雷达服务 | AC43 | `profile_service.py:283` | 在 `get_public_profile` 中查询用户路径类型，传递给 `SkillRadarService.get_skill_radar(user.id, db, path_type=...)` |

### 🟡 MAJOR (建议修复，不阻塞)

| # | 问题 | 位置 | 修复建议 |
|:--:|------|------|------|
| M1 | Profile 路由路径与 Design 不一致：`/api/v1/profile/me/settings` vs Design 的 `/api/v1/profile/privacy` | `api/v1/profile.py` | 统一使用 Design 定义的路径或更新 Design 文档 |
| M2 | 缺少 CDN/Redis 缓存实现 — ProfileCache 表存在但无缓存读写服务 | `services/` | 实现 `ProfileCacheService` 或标记为后续 Phase |
| M3 | `_get_certificates` N+1 查询：逐 Course 查询 Chapter 和 LearningProgress | `profile_service.py:392-410` | 使用 JOIN 一次性查询，或用 `selectinload` |
| M4 | `RateLimiter` 无限增长内存 — 无过期清理机制 | `employer.py:30-31` | 使用 TTL 字典或定期清理旧 hour 条目 |
| M5 | `log_api_call` 静默吞掉异常（不记录日志），审计日志可能静默丢失 | `employer.py:97-109` | 至少添加 `logger.exception("Failed to log API call")` |
| M6 | AC47 审计日志无独立测试验证 | `tests/test_employer.py` | 在签名验证/查询测试后验证 `employer_api_logs` 中有对应记录 |
| M7 | Sandbox Layer A 无资源限制（无 cgroup/内存限制），与 Design "2核4G" 不符 | `services/sandbox.py` | 添加 resource.setrlimit 或标记为"开发阶段简化实现" |

### 🔵 MINOR (记录，不阻塞)

| # | 问题 | 位置 |
|:--:|------|------|
| m1 | `_execute_code_sync` 79 行，`execute_layer_a` 86 行: 超 50 行限制 | `sandbox.py` |
| m2 | `render_verify_page` 112 行: 业务逻辑与 HTML 模板混合 | `employer.py` |
| m3 | 3 个 unused imports (F401): `fastapi.status`, `time`, `sqlalchemy.Float` | 多文件 |
| m4 | 3 个 line-too-long (E501) | 多文件 |
| m5 | `verify_signature` 使用 `__import__("datetime")` 动态导入 | `employer.py:299` |
| m6 | `rate_limiter` 应为 `_rate_limiter`（模块私有） | `employer.py:57` |

---

## 统计

| 指标 | 值 |
|------|:--:|
| CRITICAL | 4 |
| MAJOR | 7 |
| MINOR | 6 |
| 总测试 | 70 passed, 0 failed |
| Lint (E/W/F) | 3 unused imports + 3 line-too-long |
| 函数 >50 行 | 5 个 |

---

## 修复优先级

1. **P0 — 阻塞**: 补充 AC46/AC48/AC49 API 集成测试 (C1-C3)
2. **P0 — 阻塞**: 实现 AC43 路径感知主页 (C4) 或与 PO 确认降级
3. **P1**: 修复 M1 路由不一致 + M3 N+1 查询
4. **P2**: 修复 M4 内存泄漏 + M5 错误处理
5. **P3**: 清理 lint 问题 (m1-m6)

---

## CODER_FIX 备注 (2026-06-14)

### M1 路由路径不一致 — 暂不修改

Design 要求 PUT /api/v1/profile/privacy，当前实现为 PUT /api/v1/profile/me/settings。
路由修改会破坏前端已有调用（frontend JS 已引用 /me/settings）。
建议后续 Phase 统一前端迁移后再修改路由，或保持现有路径并更新 Design 文档。

---

*评审人: Hermes Agent (独立评审，无变更上下文)*  
*评审工具: ruff check + pytest + 手动代码审查*
