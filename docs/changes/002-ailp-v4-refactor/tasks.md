# Tasks: AILP V4 — AI 能力验证平台

> **变更 ID**: 002-ailp-v4-refactor  
> **前置文档**: design.md, design-module-*.md  
> **版本**: 1.0  
> **日期**: 2026-05-28  

---

## 执行约定

1. **工作目录**: `/root/workspace/ai-learning-platform/backend`
2. **每 Task 完成后**: commit，格式 `feat({模块}): T{编号} {描述}`
3. **验证方式**: `pytest tests/test_{模块}.py -v`
4. **AC 覆盖检查**: 每个 Task 标注覆盖的 AC 编号

---

## Task 执行顺序

```
Phase 1: 基础数据层（Path + Radar）→ [可独立交付]
T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8 → T9 → T10

Phase 2: 核心服务层（Tutor + Certification）→ [依赖Phase 1]
T11 → T12 → T13 → T14 → T15 → T16 → T17 → T18 → T19

Phase 3: 验证与执行（Sandbox + Profile + Employer）→ [依赖Phase 1+2]
T20 → T21 → T22 → T23 → T24 → T25 → T26 → T27 → T28 → T29

Phase 4: 演进引擎（Evolution）→ [依赖Phase 1+2]
T30 → T31 → T32 → T33 → T34

Phase 5: 集成测试 → [依赖Phase 1-4]
T35 → T36 → T37 → T38 → T39
```

---

## Phase 1: 基础数据层（Path + Radar）

> **交付标准**: Path API + Radar API 全量测试通过，AC1-AC14 验证完成  
> **验收检查点**: Phase 1 Review → Phase 1 QA → Phase 1 Accepted  
> **回归测试**: 本Phase全量测试（基线Phase，无回归测试）  
> **依赖**: 无  
> **可独立交付**: ✅ **是**

### T1: Path 模块数据库表
**估时**: 30m  
**依赖**: None  
**AC 覆盖**: AC1, AC3  

**步骤**:
1. 创建 `path_templates` 表 + 4路径种子数据
2. 创建 `user_paths`, `path_courses`, `path_milestones` 表
3. Commit: `feat(path): T1 create path tables`

**验证**:
```bash
pytest tests/test_path.py::test_tables_exist -v
```

---

### T2: Path 入学诊断 API
**估时**: 45m  
**依赖**: T1  
**AC 覆盖**: AC1, AC2  

**步骤**:
1. 实现 `POST /api/v1/paths/diagnosis`
2. 实现诊断算法（can_skip_phase1, weak_areas）
3. Commit: `feat(path): T2 diagnosis API`

**验证**:
```bash
pytest tests/test_path.py::test_diagnosis_recommend_path -v
pytest tests/test_path.py::test_diagnosis_skip_phase1 -v
```

---

### T3: Path 创建与进度 API
**估时**: 45m  
**依赖**: T2  
**AC 覆盖**: AC1, AC3, AC5  

**步骤**:
1. 实现 `POST /api/v1/paths`（支持 fast_track 模式）
2. 实现 `GET /api/v1/paths/{id}/progress`
3. Commit: `feat(path): T3 create and progress API`

**验证**:
```bash
pytest tests/test_path.py::test_create_path -v
pytest tests/test_path.py::test_path_progress -v
pytest tests/test_path.py::test_fast_track_mode -v
```

---

### T4: Path 能力缺口诊断
**估时**: 45m  
**依赖**: T3  
**AC 覆盖**: AC4  

**步骤**:
1. 实现缺口检测算法（基于实验通过率）
2. 实现 `GET /api/v1/paths/{id}/gaps`
3. Commit: `feat(path): T4 skill gap detection`

**验证**:
```bash
pytest tests/test_path.py::test_skill_gap_detection -v
```

---

### T5: Path 可视化数据 API
**估时**: 30m  
**依赖**: T3  
**AC 覆盖**: AC6  

**步骤**:
1. 实现 `GET /api/v1/paths/{id}/visualization`
2. 返回 nodes + edges 结构
3. Commit: `feat(path): T5 visualization API`

**验证**:
```bash
pytest tests/test_path.py::test_path_visualization -v
```

---

### T6: Radar 模块数据库表
**估时**: 30m  
**依赖**: None  
**AC 覆盖**: AC7, AC9  

**步骤**:
1. 创建 `skill_dimensions` 表 + 10维种子数据
2. 创建 `user_skill_scores`, `skill_events` 表
3. Commit: `feat(radar): T6 create radar tables`

**验证**:
```bash
pytest tests/test_radar.py::test_tables_exist -v
```

---

### T7: Radar 技能更新算法
**估时**: 45m  
**依赖**: T6  
**AC 覆盖**: AC9, AC10  

**步骤**:
1. 实现时间衰减权重计算（90天半衰期）
2. 实现实验完成事件监听
3. Commit: `feat(radar): T7 skill update with time decay`

**验证**:
```bash
pytest tests/test_radar.py::test_time_decay_calculation -v
pytest tests/test_radar.py::test_skill_update_from_lab -v
```

---

### T8: Radar 查询与路径特化
**估时**: 45m  
**依赖**: T7  
**AC 覆盖**: AC7, AC8, AC11, AC14  

**步骤**:
1. 实现 `GET /api/v1/radar`
2. 支持 `?path_type=ai-engineer` 路径特化
3. 返回 percentile 和 confidence
4. Commit: `feat(radar): T8 radar query with path specialization`

**验证**:
```bash
pytest tests/test_radar.py::test_radar_10_dimensions -v
pytest tests/test_radar.py::test_radar_path_specialization -v
```

---

### T9: Radar 历史对比与快照
**估时**: 45m  
**依赖**: T8  
**AC 覆盖**: AC12  

**步骤**:
1. 创建 `user_skill_snapshots` 表
2. 实现 `POST /api/v1/radar/snapshots`
3. 实现 `GET /api/v1/radar/compare`
4. Commit: `feat(radar): T9 snapshot and comparison`

**验证**:
```bash
pytest tests/test_radar.py::test_create_snapshot -v
pytest tests/test_radar.py::test_compare_snapshots -v
```

---

### T10: Radar 差距分析
**估时**: 30m  
**依赖**: T8  
**AC 覆盖**: AC13  

**步骤**:
1. 创建 `job_skill_requirements` 表
2. 实现 `GET /api/v1/radar/gap-analysis`
3. Commit: `feat(radar): T10 gap analysis`

**验证**:
```bash
pytest tests/test_radar.py::test_gap_analysis -v
```

---

## Phase 2: 核心服务层（Tutor + Certification）

> **交付标准**: Tutor API + Certification API 全量测试通过，AC15-AC31, AC37 验证完成（AC32-AC36 由 Phase 3/4 后续交付）  
> **验收检查点**: Phase 2 Review → Phase 2 QA → Phase 2 Accepted  
> **回归测试**: Phase 1 核心 10%（验证不破坏基线）  
> **依赖**: Phase 1（Radar Service）  
> **可独立交付**: ✅ **是**（依赖Phase 1已交付）

### T11: Tutor LLM Router 四级降级
**估时**: 45m  
**依赖**: None  
**AC 覆盖**: AC21  

**步骤**:
1. 实现 `LLMRouter` 类
2. 配置 豆包(Ark) → OpenRouter → 千帆 → 本地 Qwen-7B
3. 实现降级逻辑（timeout / rate limit / failure）
4. Commit: `feat(tutor): T11 LLM router with 4-layer fallback`

**验证**:
```bash
pytest tests/test_tutor.py::test_llm_router_fallback -v
```

---

### T12: Tutor 对话 API
**估时**: 30m  
**依赖**: T11  
**AC 覆盖**: AC15, AC21  

**步骤**:
1. 创建 `tutor_sessions`, `tutor_messages` 表
2. 实现 `POST /api/v1/tutor/chat`
3. Commit: `feat(tutor): T12 chat API`

**验证**:
```bash
pytest tests/test_tutor.py::test_chat_response_time -v
pytest tests/test_tutor.py::test_diagnosis_conversation -v
```

---

### T13: Tutor 代码审查
**估时**: 45m  
**依赖**: T12  
**AC 覆盖**: AC16, AC17  

**步骤**:
1. 创建 `code_reviews` 表
2. 实现 `POST /api/v1/tutor/code-review`
3. 实现代码分析（issues, score, summary）
4. Commit: `feat(tutor): T13 code review`

**验证**:
```bash
pytest tests/test_tutor.py::test_code_review_structure -v
```

---

### T14: Tutor 个性化推荐
**估时**: 30m  
**依赖**: T13  
**AC 覆盖**: AC18, AC19  

**步骤**:
1. 实现 `GET /api/v1/tutor/recommendations`
2. 基于薄弱维度推荐课程
3. Commit: `feat(tutor): T14 recommendations`

**验证**:
```bash
pytest tests/test_tutor.py::test_recommendations -v
```

---

### T15: Tutor 学习障碍检测
**估时**: 30m  
**依赖**: T12  
**AC 覆盖**: AC20  

**步骤**:
1. 创建 `learning_obstacles` 表
2. 实现障碍检测算法（time_exceeded > 3x average）
3. 实现 `GET /api/v1/tutor/obstacles`
4. Commit: `feat(tutor): T15 obstacle detection`

**验证**:
```bash
pytest tests/test_tutor.py::test_obstacle_detection -v
```

---

### T16: Certification 数据库表
**估时**: 30m  
**依赖**: None  
**AC 覆盖**: AC30-AC31, AC37（表结构覆盖 AC30-AC37，但 AC32-AC36 的 Service/API 逻辑尚未实现，由 Phase 3/4 后续交付）

**步骤**:
1. 创建 `certification_levels`, `certification_applications`, `certificates` 表
2. 创建 `capstone_submissions` 表
3. Commit: `feat(cert): T16 certification tables`

**验证**:
```bash
pytest tests/test_certification.py::test_tables_exist -v
```

---

### T17: Certification L1 自动评定
**估时**: 30m  
**依赖**: T16, T8  
**AC 覆盖**: AC30  

**步骤**:
1. 实现 `auto_evaluate_l1()` 算法
2. 检查必修课程 + 平均分
3. Commit: `feat(cert): T17 L1 auto evaluation`

**验证**:
```bash
pytest tests/test_certification.py::test_l1_auto_evaluation -v
```

---

### T18: Certification L2 项目评审
**估时**: 45m  
**依赖**: T17  
**AC 覆盖**: AC31  

**步骤**:
1. 实现 Capstone 提交流程
2. 实现 AI 初审 + 人工抽检
3. Commit: `feat(cert): T18 L2 capstone review`

**验证**:
```bash
pytest tests/test_certification.py::test_l2_capstone_review -v
```

---

### T19: Certification 证书签名
**估时**: 45m  
**依赖**: T18  
**AC 覆盖**: AC37  

**步骤**:
1. 实现 ECDSA 签名生成
2. 实现 `GET /api/v1/certificates/{number}`
3. 实现验证接口
4. Commit: `feat(cert): T19 certificate ECDSA signature`

**验证**:
```bash
pytest tests/test_certification.py::test_certificate_signature -v
pytest tests/test_certification.py::test_certificate_verification -v
```

---

## Phase 3: 验证与执行（Sandbox + Profile + Employer）

> **交付标准**: Sandbox API + Profile API + Employer API 全量测试通过，AC38-AC47 验证完成  
> **验收检查点**: Phase 3 Review → Phase 3 QA → Phase 3 Accepted  
> **回归测试**: Phase 1+2 核心 10%（验证不破坏前置Phase）  
> **依赖**: Phase 1（Radar）+ Phase 2（Tutor/Certification）  
> **可独立交付**: ✅ **是**（依赖Phase 1+2已交付）

### T20: Sandbox 模块数据库表
**估时**: 20m  
**依赖**: None  
**AC 覆盖**: AC38-AC44  

**步骤**:
1. 创建 `execution_requests`, `external_executions`, `verification_tasks` 表
2. Commit: `feat(sandbox): T20 sandbox tables`

---

### T21: Sandbox Layer A 本地执行
**估时**: 45m  
**依赖**: T20  
**AC 覆盖**: AC38  

**步骤**:
1. 实现 `POST /api/v1/sandbox/execute` (layer=A)
2. 使用 subprocess 执行 Python 代码
3. 实现安全限制（timeout, memory）
4. Commit: `feat(sandbox): T21 Layer A local execution`

**验证**:
```bash
pytest tests/test_sandbox.py::test_layer_a_execution -v
```

---

### T22: Sandbox Layer B 外部资源
**估时**: 45m  
**依赖**: T21  
**AC 覆盖**: AC39  

**步骤**:
1. 实现 Kaggle/Colab 提交接口
2. 实现 webhook 回调接收
3. Commit: `feat(sandbox): T22 Layer B external execution`

**验证**:
```bash
pytest tests/test_sandbox.py::test_layer_b_submission -v
```

---

### T23: Sandbox Layer C 验证引擎
**估时**: 45m  
**依赖**: T22  
**AC 覆盖**: AC40, AC41  

**步骤**:
1. 实现模型验证流程（加载 model.pth，测试集推理）
2. 实现审计日志生成
3. Commit: `feat(sandbox): T23 Layer C verification`

**验证**:
```bash
pytest tests/test_sandbox.py::test_layer_c_verification -v
pytest tests/test_sandbox.py::test_verification_failure -v
```

---

### T24: Profile 数据库表
**估时**: 15m  
**依赖**: None  
**AC 覆盖**: AC42-AC44  

**步骤**:
1. 创建 `user_profiles`, `profile_cache` 表
2. Commit: `feat(profile): T24 profile tables`

---

### T25: Profile 公开主页 API
**估时**: 30m  
**依赖**: T24, T8  
**AC 覆盖**: AC43  

**步骤**:
1. 实现 `GET /api/v1/profiles/{username}`
2. 路径感知展示（突出显示对应维度）
3. Commit: `feat(profile): T25 public profile`

**验证**:
```bash
pytest tests/test_profile.py::test_public_profile -v
pytest tests/test_profile.py::test_path_aware_display -v
```

---

### T26: Profile 隐私控制
**估时**: 30m  
**依赖**: T25  
**AC 覆盖**: AC44  

**步骤**:
1. 实现 `PUT /api/v1/profile/privacy`
2. 根据设置过滤返回字段
3. Commit: `feat(profile): T26 privacy controls`

**验证**:
```bash
pytest tests/test_profile.py::test_privacy_controls -v
```

---

### T27: Employer 数据库表
**估时**: 20m  
**依赖**: None  
**AC 覆盖**: AC45-AC49  

**步骤**:
1. 创建 `employers`, `verification_codes`, `employer_api_logs` 表
2. Commit: `feat(employer): T27 employer tables`

---

### T28: Employer 证书验证 API
**估时**: 30m  
**依赖**: T27, T19  
**AC 覆盖**: AC46  

**步骤**:
1. 实现 `POST /api/v1/employer/verify`
2. 实现数字签名验证
3. Commit: `feat(employer): T28 certificate verification API`

**验证**:
```bash
pytest tests/test_employer.py::test_verify_certificate -v
```

---

### T29: Employer API 限流与授权
**估时**: 45m  
**依赖**: T28  
**AC 覆盖**: AC48, AC49  

**步骤**:
1. 实现 RateLimitMiddleware（1000/小时）
2. 实现授权码验证机制
3. Commit: `feat(employer): T29 rate limit and authorization`

**验证**:
```bash
pytest tests/test_employer.py::test_rate_limit -v
pytest tests/test_employer.py::test_authorization_code -v
```

---

## Phase 4: 演进引擎（Evolution）

> **交付标准**: Evolution API 全量测试通过，AC48 验证完成  
> **验收检查点**: Phase 4 Review → Phase 4 QA → Phase 4 Accepted  
> **回归测试**: Phase 1+2 核心 10%（验证不破坏前置Phase）  
> **依赖**: Phase 1（Radar）+ Phase 2（Tutor/Certification）  
> **可独立交付**: ✅ **是**（依赖Phase 1+2已交付）

### T30: Evolution 数据聚合任务
**估时**: 30m  
**依赖**: None  
**AC 覆盖**: AC22-AC29  

**步骤**:
1. 创建 `jd_sources`, `job_descriptions`, `market_skill_trends` 表
2. 创建 `content_update_suggestions` 表
3. Commit: `feat(evolution): T30 evolution tables`

---

### T31: Evolution JD 采集
**估时**: 45m  
**依赖**: T30  
**AC 覆盖**: AC22  

**步骤**:
1. 实现每日定时任务 `crawl_jd_daily()`
2. 实现 Boss直聘/拉勾 采集
3. Commit: `feat(evolution): T31 JD crawler`

**验证**:
```bash
pytest tests/test_evolution.py::test_jd_crawler -v
```

---

### T32: Evolution 技能趋势分析
**估时**: 30m  
**依赖**: T31  
**AC 覆盖**: AC23, AC29  

**步骤**:
1. 实现技能提取（NLP）
2. 实现趋势统计（环比增长率）
3. Commit: `feat(evolution): T32 skill trend analysis`

**验证**:
```bash
pytest tests/test_evolution.py::test_skill_trends -v
```

---

### T33: Evolution 更新建议生成
**估时**: 30m  
**依赖**: T32  
**AC 覆盖**: AC24, AC28  

**步骤**:
1. 实现更新建议算法
2. 整合 JD 趋势 + 学生数据
3. Commit: `feat(evolution): T33 update suggestions`

**验证**:
```bash
pytest tests/test_evolution.py::test_update_suggestions -v
```

---

### T34: Evolution 三层更新策略
**估时**: 30m  
**依赖**: T33  
**AC 覆盖**: AC25-AC27  

**步骤**:
1. 实现 L3(2周)/L2(2月)/L1(6月) 更新周期
2. Commit: `feat(evolution): T34 3-layer update strategy`

**验证**:
```bash
pytest tests/test_evolution.py::test_layered_update_strategy -v
```

---

## Phase 5: 集成测试

> **交付标准**: 全量集成测试通过 100%，AC49 验证完成，系统生产就绪  
> **验收检查点**: Final Review → Final QA → Production Ready  
> **回归测试**: 全量回归测试 100%（归档前全量验证）  
> **依赖**: Phase 1 + Phase 2 + Phase 3 + Phase 4  
> **可独立交付**: ✅ **是**（所有前置Phase已交付）

### T35: 全量 API 集成测试
**估时**: 30m  
**依赖**: T5, T10  
**AC 覆盖**: AC1-AC14  

**步骤**:
1. 测试路径完成自动更新技能雷达
2. Commit: `test(integration): T35 path-radar integration`

---

### T36: Sandbox + Radar 集成测试
**估时**: 30m  
**依赖**: T23, T8  
**AC 覆盖**: AC38-AC44  

**步骤**:
1. 测试实验完成触发技能更新
2. Commit: `test(integration): T36 sandbox-radar integration`

---

### T37: Certification + Profile 集成测试
**估时**: 30m  
**依赖**: T19, T25  
**AC 覆盖**: AC30-AC44  

**步骤**:
1. 测试证书获得后公开主页更新
2. Commit: `test(integration): T37 cert-profile integration`

---

### T38: Employer API 端到端测试
**估时**: 30m  
**依赖**: T29  
**AC 覆盖**: AC45-AC49  

**步骤**:
1. 测试完整验证流程
2. Commit: `test(integration): T38 employer e2e`

---

### T39: 全量 AC 覆盖测试
**估时**: 45m  
**依赖**: T35-T38  
**AC 覆盖**: AC1-AC49  

**步骤**:
1. 运行全量 AC 测试矩阵
2. 生成 AC 覆盖报告
3. Commit: `test(integration): T39 full AC coverage`

**验证**:
```bash
pytest tests/ -v --ac-coverage-report
```

---

## 汇总统计

| Phase | Tasks | 估时 | AC 覆盖 |
|------|:-----:|------|:-------:|
| Phase 1: 基础数据层 | 10 | 6h 15m | AC1-AC14 |
| Phase 2: 核心服务层 | 9 | 5h 30m | AC15-AC31, AC37（AC32-AC36 后续 Phase） |
| Phase 3: 验证与执行 | 10 | 5h 25m | AC38-AC49 |
| Phase 4: 演进引擎 | 5 | 2h 45m | AC22-AC29 |
| Phase 5: 集成测试 | 5 | 2h 45m | AC1-AC49 |
| **总计** | **39** | **~22h** | **44/49（Phase 2 交付），AC32-AC36 后续 Phase** |

---

## AC 覆盖矩阵（Summary）

| AC | Task(s) | 模块 | 状态 |
|:---:|---------|------|:---:|
| AC1 | T2, T3 | Path | ⏳ |
| AC2 | T2 | Path | ⏳ |
| AC3 | T3 | Path | ⏳ |
| AC4 | T4 | Path | ⏳ |
| AC5 | T3 | Path | ⏳ |
| AC6 | T5 | Path | ⏳ |
| AC7 | T6, T8 | Radar | ⏳ |
| AC8 | T8 | Radar | ⏳ |
| AC9 | T6, T7 | Radar | ⏳ |
| AC10 | T7 | Radar | ⏳ |
| AC11 | T8 | Radar | ⏳ |
| AC12 | T9 | Radar | ⏳ |
| AC13 | T10 | Radar | ⏳ |
| AC14 | T8 | Radar | ⏳ |
| AC15 | T12 | Tutor | ⏳ |
| AC16 | T13 | Tutor | ⏳ |
| AC17 | T13 | Tutor | ⏳ |
| AC18 | T14 | Tutor | ⏳ |
| AC19 | T14 | Tutor | ⏳ |
| AC20 | T15 | Tutor | ⏳ |
| AC21 | T11, T12 | Tutor | ⏳ |
| AC22 | T31 | Evolution | ⏳ |
| AC23 | T32 | Evolution | ⏳ |
| AC24 | T33 | Evolution | ⏳ |
| AC25 | T34 | Evolution | ⏳ |
| AC26 | T34 | Evolution | ⏳ |
| AC27 | T34 | Evolution | ⏳ |
| AC28 | T33 | Evolution | ⏳ |
| AC29 | T32 | Evolution | ⏳ |
| AC30 | T17 | Certification | ⏳ |
| AC31 | T18 | Certification | ⏳ |
| AC32 | T18 | Certification | 🔜 后续 Phase |
| AC33 | T18 | Certification | 🔜 后续 Phase |
| AC34 | T19 | Certification | 🔜 后续 Phase |
| AC35 | T19 | Certification | 🔜 后续 Phase |
| AC36 | T18 | Certification | 🔜 后续 Phase |
| AC37 | T19 | Certification | ⏳ |
| AC38 | T21 | Sandbox | ⏳ |
| AC39 | T22 | Sandbox | ⏳ |
| AC40 | T23 | Sandbox | ⏳ |
| AC41 | T23 | Sandbox | ⏳ |
| AC42 | T23 | Sandbox | ⏳ |
| AC43 | T25 | Profile | ⏳ |
| AC44 | T26 | Profile | ⏳ |
| AC45 | T28 | Employer | ⏳ |
| AC46 | T28 | Employer | ⏳ |
| AC47 | T19 | Certification | ⏳ |
| AC48 | T29 | Employer | ⏳ |
| AC49 | T29 | Employer | ⏳ |

**覆盖度**: 44/49 = **89.8%**（Phase 2 交付范围内，AC32-AC36 由 Phase 3/4 后续交付）

---

**Tasks 状态**: ✅ Architect 阶段完成  
**下一步**: 用户确认后进入 Coder 阶段，按 Phase 1→5 顺序执行。**注意**：AC32-AC36（Certification 能力等级评定 Service/API 逻辑）将在 Phase 3/4 中由 T20-T29、T30-T34 覆盖实现，Phase 2 仅完成数据库表结构。
