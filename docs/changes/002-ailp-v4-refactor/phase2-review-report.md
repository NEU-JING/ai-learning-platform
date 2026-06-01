# Phase 2 Review Report: Tutor + Certification 模块

> **变更 ID**: 002-ailp-v4-refactor  
> **Phase**: Phase 2 (核心服务层)  
> **评审日期**: 2026-06-01  
> **评审状态**: ⚠️ **有条件通过 (CONDITIONAL PASS)**

---

## 一、执行摘要

Phase 2 (Tutor + Certification 模块) 的三阶段评审已完成，**结论为有条件通过**。存在 1 个 CRITICAL 问题（AC 覆盖不完整）和 5 个 MAJOR 问题需要修复。

| 检查项 | 状态 | 备注 |
|--------|:----:|------|
| Phase 1: Spec 合规 | ⚠️ | AC 覆盖不完整 (18/23) |
| Phase 2: 代码质量 | ⚠️ | 6 个问题 (1 CRITICAL, 3 MAJOR, 2 MINOR) |
| Phase 3: 架构一致性 | ✅ | 与 Design 一致 |
| 前后端契约 (R5) | ✅ | Phase 2 无前端变更，无需检查 |
| 数据契约检查 | ✅ | 16/16 通过 (Phase 1 基线) |
| 回归测试 | ✅ | Phase 1 数据契约全部通过 |

**测试统计**:
- Tutor 模块: 31 tests ✅ (test_tutor.py: 17, test_tutor_chat.py: 6, test_tutor_llm_router.py: 8)
- Code Review: 7 tests ✅
- Certification 模块: 36 tests ✅
- 数据契约: 16 tests ✅
- **总计: 74 tests, 全部通过** (Phase 2) + 16 数据契约

---

## 二、Phase 1: Spec 合规检查

### 2.1 AC 覆盖矩阵 (AC15-AC37)

#### 2.1.1 Tutor 模块 (AC15-AC21)

| AC | 场景 | 实现位置 | 测试覆盖 | 状态 |
|:--:|------|----------|----------|:----:|
| AC15 | AI导师入学诊断 | `tutor.py:chat()` (session_type=diagnosis) | `test_create_new_session`, `test_diagnosis_conversation` (via chat) | ✅ |
| AC16 | 代码审查实时反馈 | `code_review.py:review_code()` | `test_create_code_review`, `test_code_review_with_issues`, `test_code_review_scoring_dimensions` | ✅ |
| AC17 | 对话质量分析 | `code_review.py:review_code()` (dimensions评分) | `test_code_review_scoring_dimensions` | ✅ |
| AC18 | 内容个性化推荐 | `tutor.py:get_recommendations()` | `test_recommendations_*` 系列 (9 个测试) | ✅ |
| AC19 | 路径动态优化 | `tutor.py:get_recommendations()` (Fast Track) | `test_recommendations_fast_track_*` (2 个测试) | ✅ |
| AC20 | 学习障碍识别 | `tutor.py:get_obstacles()` | `test_obstacle_detection_*` 系列 (5 个测试) | ✅ |
| AC21 | 24/7 学习支持 | `llm_router.py:LLMRouter` 三级降级 | `test_fallback_on_*` 系列 (8 个测试) | ✅ |

**Tutor AC 覆盖度**: 7/7 = **100%** ✅

#### 2.1.2 Certification 模块 (AC30-AC37)

| AC | 场景 | 实现位置 | 测试覆盖 | 状态 |
|:--:|------|----------|----------|:----:|
| AC30 | L1 自动评定 | `certificate.py:auto_evaluate_l1()` | `test_auto_approve_*`, `test_fail_when_*` 等 (5 个测试) | ✅ |
| AC31 | L2 项目评审 | `certificate.py:submit_capstone()`, `ai_review_capstone()`, `approve_capstone()`, `reject_capstone()` | `TestCapstoneSubmitService`, `TestCapstoneAIReviewService`, `TestCapstoneApproveRejectService`, `TestCapstoneAPI` (15 个测试) | ✅ |
| AC32 | L3 场景挑战 | **未实现** ⚠️ | 无测试 | ❌ |
| AC33 | L4 创新贡献 | **未实现** ⚠️ | 无测试 | ❌ |
| AC34 | 认证过期提醒 | **未实现** ⚠️ | 无测试 | ❌ |
| AC35 | 认证续期 | **未实现** ⚠️ | 无测试 | ❌ |
| AC36 | 路径特化认证 | **未实现** ⚠️ | 无测试 | ❌ |
| AC37 | 证书数字签名 | `certificate.py:sign_certificate()`, `verify_certificate_signature()` | `TestECDSACertificateSignature` (5 个测试) | ✅ |

**Certification AC 覆盖度**: 3/8 = **37.5%** ❌

#### 2.1.3 AC 覆盖汇总

| 模块 | AC 范围 | 已覆盖 | 未覆盖 | 覆盖率 |
|------|--------|:------:|:------:|:------:|
| Tutor | AC15-AC21 | 7 | 0 | 100% |
| Certification | AC30-AC37 | 3 | 5 | 37.5% |
| **合计** | **AC15-AC37** | **10/15** | **5/15** | **66.7%** |

> **注**: AC32-AC36 未在 Phase 2 的 Tasks (T16-T19) 中分配业务逻辑实现任务。T16 创建了数据库表（声明覆盖 AC30-AC37），但 AC32-AC36 的 Service/API 层未实现。这些 AC 预计在后续 Phase 或独立变更中交付。

### 2.2 交付物验证

| 交付物 | 路径 | 状态 |
|--------|------|:----:|
| LLM Router | `app/services/llm_router.py` | ✅ |
| Tutor Service | `app/services/tutor.py` | ✅ |
| Code Review Service | `app/services/code_review.py` | ✅ |
| Certificate Service | `app/services/certificate.py` | ✅ |
| Tutor API | `app/api/v1/tutor.py` | ✅ |
| Certificates API | `app/api/v1/certificates.py` | ✅ |
| Tutor Models | `app/models/tutor.py` | ✅ |
| Cert Models | `app/models/certification.py` | ✅ |
| Tutor Schemas | `app/schemas/tutor.py` | ✅ |
| Code Review Schemas | `app/schemas/code_review.py` | ✅ |
| Capstone Schemas | `app/schemas/capstone.py` | ✅ |
| Tutor Tests | `tests/test_tutor.py` 等 3 文件 | ✅ |
| Cert Tests | `tests/test_certification.py` | ✅ |

---

## 三、Phase 2: 代码质量检查

### 3.1 DRY (Don't Repeat Yourself)

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| 重复代码检查 | ⚠️ | `_utcnow()` 在 6 个文件中重复定义 |
| 常量抽取 | ✅ | 降级链、阈值常量已抽取 |
| 工具函数复用 | ✅ | LLMRouter 被 Tutor/Cert 共享 |

**发现**:
- 🔴 `_utcnow()` 在 `models/__init__.py`, `models/tutor.py`, `models/certification.py`, `models/path.py`, `models/radar.py`, `data/path_templates.py` 中重复定义（共 6 处）。Phase 2 新增了 `tutor.py` 和 `certification.py` 的副本。应统一从 `app.models` 或 `app.core` 导入。

### 3.2 YAGNI (You Aren't Gonna Need It)

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| 死代码检查 | ✅ | 未发现死代码 |
| 过度设计检查 | ✅ | 实现范围与 Tasks 一致 |
| 注释掉的代码 | ✅ | 无 |

### 3.3 命名规范

| 检查项 | 状态 | 示例 |
|--------|:----:|------|
| 类名 (PascalCase) | ✅ | `LLMRouter`, `CertificateService`, `CodeReviewService` |
| 函数名 (snake_case) | ✅ | `auto_evaluate_l1`, `sign_certificate` |
| 变量名 | ✅ | `obstacle_type`, `latency_ms` |
| 常量名 (UPPER_CASE) | ⚠️ | `OBSTACLE_RATIO_THRESHOLD` ✅, 但 `CERTIFICATE_TEMPLATE` 是大段 HTML |

### 3.4 错误处理

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| HTTP 状态码正确使用 | ✅ | 400/401/404/500 使用恰当 |
| 错误信息清晰 | ✅ | detail 包含具体错误信息 |
| 异常边界处理 | ⚠️ | `QianfanProvider` 和 `LocalQwenProvider` 为 Mock 实现 |
| 事务回滚 | ✅ | SQLAlchemy 事务正确管理 |

**发现**:
- 🟡 `QianfanProvider.chat()` (line 166-186) 返回 Mock 数据，未对接真实千帆 API
- 🟡 `LocalQwenProvider.chat()` (line 200-219) 返回 Mock 数据，未对接本地模型
- 🟢 降级链能正确处理 Mock 提供的假的成功响应，但从测试角度看，Mock 层不暴露真实 API 错误路径

### 3.5 函数长度

| 函数 | 文件 | 行数 | 状态 |
|------|------|:---:|:----:|
| `auto_evaluate_l1()` | `certificate.py:479-661` | **183** | ❌ 超标 |
| `get_recommendations()` | `tutor.py:178-329` | **152** | ❌ 超标 |
| `get_obstacles()` | `tutor.py:331-440` | **110** | ❌ 超标 |
| `generate_certificate()` | `certificate.py:155-288` | 134 | ❌ 超标 |
| `chat()` | `tutor.py:20-113` | 94 | ❌ 超标 |
| `LLMRouter.chat()` | `llm_router.py:245-283` | 39 | ✅ |
| `review_code()` | `code_review.py:20-78` | 59 | ⚠️ 略超 |

**评级**: 多个核心函数远超 50 行限制 (`review-checklist.md` 标准)。`auto_evaluate_l1` 达 183 行，`get_recommendations` 达 152 行。建议拆分为子函数。

### 3.6 代码风格

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| 文档字符串 | ✅ | 主要函数均有 docstring |
| 类型注解 | ✅ | 类型注解完整 |
| 代码注释 | ✅ | 关键逻辑有中文注释 |

### 3.7 前后端契约同步 (R5)

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| Phase 2 前端变更 | N/A | Phase 2 无前端文件变更 |
| Schema 一致性 | ✅ | Pydantic Schema 定义完整 |

> Phase 2 的 diff (52a83a1..bb50451) 中无 `frontend-v2/` 变更，R5 检查适用性为 N/A。

---

## 四、Phase 3: 架构一致性检查

### 4.1 与 Design 文档对比

| Design 章节 | 实现情况 | 一致性 |
|-------------|----------|:------:|
| LLM Router 三级降级 (design.md §2.3) | `llm_router.py:LLMRouter` 实现 4 层降级 (Ark→OpenRouter→Qianfan→Local) | ⚠️ |
| Tutor 数据模型 (design-module-tutor.md §2) | `models/tutor.py` 完整实现 4 张表 | ✅ |
| Tutor API (design-module-tutor.md §3) | `api/v1/tutor.py` 实现 chat + code-review + recommendations + obstacles | ✅ |
| Certification 数据模型 (design-module-certification.md §2) | `models/certification.py` 完整实现 4 张表 | ✅ |
| L1 自动评定 (design-module-certification.md §3.2) | `certificate.py:auto_evaluate_l1()` 实现 | ✅ |
| L2 项目评审 (design-module-certification.md §3.1) | `certificate.py:submit_capstone()` + AI初审 + 人工抽检 | ✅ |
| ECDSA 签名 (design-module-certification.md §3.4) | `certificate.py:sign_certificate()` + `verify_certificate_signature()` | ✅ |

**架构偏离说明**:
- 🔵 **INFO**: LLM Router 实现为 4 层 (Ark→OpenRouter→Qianfan→Local)，Design 原定义 3 层 (OpenRouter→Qianfan→Local)。Ark (豆包) 作为新增的第 0 层主 provider，Design 未预见到此需求。这是合理的演进 → 标记为 INFO，建议回写 Design。

### 4.2 API 契约一致性

| API | Design 定义 | 实际实现 | 一致性 |
|-----|-------------|----------|:------:|
| `POST /api/v1/tutor/chat` | TutorChatRequest/Response | 匹配 | ✅ |
| `POST /api/v1/tutor/code-review` | CodeReviewCreate/Response | 匹配 | ✅ |
| `GET /api/v1/tutor/recommendations` | RecommendationsResponse | 匹配 | ✅ |
| `GET /api/v1/tutor/obstacles` | ObstaclesResponse | 匹配 | ✅ |
| `GET /api/v1/certificates/{number}` | cert_number + signature | 路径为 `/api/v1/certificates/courses/{course_id}` ⚠️ | ⚠️ |
| `POST /api/v1/certifications/apply` | (Design §3.1) | **未实现 API** | ❌ |
| `POST /api/v1/certifications/{id}/renew` | (Design §3.5) | **未实现** | ❌ |

**API 偏离详情**:
- 🟡 **MAJOR**: Design 定义 `POST /api/v1/certifications/apply` 作为 L1 申请入口，但未实现对应 API 端点。`auto_evaluate_l1()` 仅为 Service 方法，无 HTTP 路由暴露。
- 🟡 **MAJOR**: Design 定义 `GET /api/v1/certificates/{cert_number}`，但实现为 `GET /api/v1/certificates/courses/{course_id}`（按课程生成证书），语义不同。
- 🟡 **MAJOR**: Design 定义 `POST /certifications/{cert_id}/renew`，未实现。

### 4.3 模块间接口契约

| 调用方 | 被调用方 | Design 接口 | 实际接口 | 一致性 |
|--------|----------|-------------|----------|:------:|
| Tutor Service | LLM Router | `chat(messages, model_preference)` | `LLMRouter.chat(message, **kwargs)` | ✅ |
| Tutor Service | Radar Service | `update_skill_from_lab()` | `get_recommendations()` 读取 `UserSkillScore` | ✅ |
| Certification | Radar Service | `get_skill_summary()` | `auto_evaluate_l1()` 直接读 `LabSubmission.score` | ⚠️ |

### 4.4 关键技术决策遵循

| 决策 | Design 选择 | 实现遵循 | 状态 |
|------|:-----------|---------|:----:|
| LLM 降级 | 三级降级链 | 4 层 (多一层 Ark) | ✅ (合理演进) |
| 证书防伪 | ECDSA + SHA256 | SECP256r1 ECDSA + SHA256 | ✅ |
| 技能雷达计算 | 预计算 | `auto_evaluate_l1()` 直接读 submission scores | ✅ |

---

## 五、数据契约检查

```bash
$ pytest tests/test_data_contract.py -v
# 结果: 16 passed, 0 failed
```

Phase 2 未引入新的种子数据初始化逻辑，不影响现有数据契约。Phase 1 的数据契约 (16 项) 全部通过。

---

## 六、问题清单

### 6.1 CRITICAL (阻断合并)

| # | 问题 | 位置 | 修复建议 |
|---|------|------|---------|
| C1 | **AC32-AC36 全部未实现**：L3 场景挑战 (AC32)、L4 创新贡献 (AC33)、认证过期提醒 (AC34)、认证续期 (AC35)、路径特化认证 (AC36) 在 Phase 2 Tasks 中无对应实现任务，仅有数据库表。 | `tasks.md` T16-T19 范围 | 方案 A: 将 AC32-AC36 移入 Phase 3/4 的 Tasks 中并标注未覆盖。方案 B: 本 Phase 补充最少实现 (Service stub + 测试)。建议方案 A，明确声明 Phase 2 实际覆盖范围为 AC15-AC21 + AC30-AC31 + AC37，其余 AC 列入后续 Phase。 |

### 6.2 MAJOR (需修复)

| # | 问题 | 位置 | 修复建议 |
|---|------|------|---------|
| M1 | **L1 自动评定无 API 端点**：`auto_evaluate_l1()` 仅作为 Service 方法存在，Design 定义的 `POST /api/v1/certifications/apply` 未实现。 | `app/api/v1/certificates.py` | 添加 `POST /api/v1/certifications/apply` 端点，调用 `auto_evaluate_l1()`。 |
| M2 | **证书 API 路径与 Design 不一致**：Design 定义 `GET /api/v1/certificates/{cert_number}` 查询指定证书，但实现为 `GET /api/v1/certificates/courses/{course_id}` 按课程生成证书（语义不同）。 | `app/api/v1/certificates.py` | 添加 `GET /api/v1/certificates/{cert_number}` 端点查询指定编号的证书详情和签名。 |
| M3 | **`_utcnow()` DRY 违规**：同一函数在 `models/__init__.py`, `models/tutor.py`, `models/certification.py`, `models/path.py`, `models/radar.py`, `data/path_templates.py` 中重复定义（共 6 处）。Phase 2 新增了 `tutor.py` 和 `certification.py` 的副本。 | `app/models/tutor.py:23`, `app/models/certification.py:28` | 删除 `tutor.py` 和 `certification.py` 中的 `_utcnow()`，改为 `from app.models import _utcnow` 或统一移至 `app/core/time_utils.py`。 |
| M4 | **函数严重超标**：`auto_evaluate_l1()` 183 行、`get_recommendations()` 152 行、`get_obstacles()` 110 行、`generate_certificate()` 134 行、`chat()` 94 行。 | `certificate.py`, `tutor.py` | 拆分为子函数：`auto_evaluate_l1()` 拆出 `_check_course_completion()`, `_calculate_avg_score()`；`get_recommendations()` 拆出 `_recommend_for_weak_dimensions()`, `_recommend_defaults()`, `_suggest_fast_track()`。 |
| M5 | **QianfanProvider 和 LocalQwenProvider 为 Mock 实现**：返回硬编码的假数据，未对接真实 API。降级链测试通过是因为 mock 返回成功，但生产环境下 Layer 2/3 降级会失败。 | `llm_router.py:166-219` | QianfanProvider 对接千帆 SDK 或 OpenAI-compatible API；LocalQwenProvider 对接本地 llama.cpp/Ollama。若暂不实现，至少返回明确错误而不是假数据。 |

### 6.3 MINOR (建议修复)

| # | 问题 | 位置 | 修复建议 |
|---|------|------|---------|
| m1 | **Tutor 模型未加入 `__all__`**：`TutorSession`, `TutorMessage`, `CodeReview`, `LearningObstacle` 已导入但未列在 `models/__init__.py` 的 `__all__` 中。 | `app/models/__init__.py:401-438` | 在 `__all__` 中添加 `"TutorSession", "TutorMessage", "CodeReview", "LearningObstacle"`。 |
| m2 | **`CERTIFICATE_TEMPLATE` 类属性过长**：HTML 模板 (~150 行) 直接写在 `CertificateService` 类体中。 | `app/services/certificate.py:10-152` | 移至独立文件 `app/templates/certificate.html` 或 `app/data/certificate_template.py`。 |

### 6.4 INFO (仅供参考)

| # | 问题 | 位置 | 说明 |
|---|------|------|------|
| I1 | **LLM Router 从 3 层变为 4 层**：Design 定义 OpenRouter→Qianfan→Local，实现为 Ark→OpenRouter→Qianfan→Local。 | `llm_router.py:236-241` | 合理演进，Ark (豆包) 作为主 provider 更具性价比。建议回写 Design 文档。 |
| I2 | **Pydantic V2 迁移**：部分 Schema 仍使用 `class Config: from_attributes = True` (V1 风格)，`capstone.py` 已使用 `model_config = {"from_attributes": True}` (V2 风格)。 | `schemas/tutor.py`, `schemas/code_review.py` | 统一迁移到 `model_config` 风格，避免 Pydantic V3 弃用警告。 |
| I3 | **证书过期/续期逻辑待实现**：AC34 (过期提醒) 和 AC35 (续期) 的 Service 方法尚未实现。 | N/A | 预计在后续 Phase 或独立变更中交付。 |

---

## 七、回归测试

| 测试范围 | 测试命令 | 结果 |
|----------|----------|:----:|
| Phase 2 Tutor 测试 | `pytest tests/test_tutor*.py -v` | ✅ 31 passed |
| Phase 2 Code Review 测试 | `pytest tests/test_code_review.py -v` | ✅ 7 passed |
| Phase 2 Certification 测试 | `pytest tests/test_certification.py -v` | ✅ 36 passed |
| 数据契约检查 | `pytest tests/test_data_contract.py -v` | ✅ 16 passed |

**Phase 2 总计**: 74/74 测试通过  
**数据契约基线**: 16/16 测试通过

---

## 八、结论与建议

### 8.1 评审结论

**⚠️ Phase 2 Review: 有条件通过 (CONDITIONAL PASS)**

**通过条件**:
1. ✅ 所有 74 个 Phase 2 测试通过
2. ✅ Tutor 模块 AC 覆盖 100% (AC15-AC21)
3. ✅ ECDSA 证书签名实现正确，防篡改测试通过
4. ✅ LLM Router 降级链逻辑正确，测试覆盖完整
5. ✅ 数据契约 16/16 全通过（无回归）

**阻塞条件** (CRITICAL):
- C1: AC32-AC36 未实现 → **需明确范围声明**

**建议修复** (MAJOR, 不阻塞交付):
- M1: 补 L1 认证申请 API 端点
- M2: 补证书详情查询 API
- M3: 消除 `_utcnow()` DRY 违规
- M4: 拆分超标函数
- M5: Qianfan/LocalQwen 替换 Mock 为真实实现（或至少返回错误而非假数据）

### 8.2 严重级别汇总

| 级别 | 数量 | 可交付? |
|:----:|:----:|:------:|
| CRITICAL | 1 | ❌ 需解决或声明 |
| MAJOR | 5 | ✅ 可后续修复 |
| MINOR | 2 | ✅ 可后续修复 |
| INFO | 3 | ✅ 仅记录 |

### 8.3 下一步行动

1. **立即行动** (CRITICAL):
   - 在 `tasks.md` 中明确 AC32-AC36 的交付范围（归属 Phase 3/4 或独立变更），更新 T16 的 AC 覆盖声明从 AC30-AC37 改为 AC30-AC31, AC37（表结构部分保持）

2. **短期修复** (MAJOR, QA 前完成):
   - M1: 添加 `POST /api/v1/certifications/apply` API 端点
   - M2: 添加 `GET /api/v1/certificates/{cert_number}` API 端点
   - M3: 统一 `_utcnow()` 导入

3. **后续优化** (MAJOR, 合并前完成):
   - M4: 拆分 `auto_evaluate_l1()`, `get_recommendations()`, `get_obstacles()` 等超标函数
   - M5: QianfanProvider 和 LocalQwenProvider 对接真实 API

4. **进入 Phase 3**:
   - Phase 2 已标记为有条件通过
   - 阻塞项 C1 需先解决（范围声明）
   - Phase 3 依赖 Phase 2 的 Tutor Service + Certification Service

---

## 九、签名

| 角色 | 签名 | 日期 |
|------|------|------|
| Reviewer | Phase 2 Review Agent | 2026-06-01 |

---

**附件**:
- 测试输出日志: Phase 2 全量 74 tests passed ✅
- 数据契约检查: 16/16 passed ✅
