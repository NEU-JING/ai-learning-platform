# Design Module: Phase 4 游戏化学习体验（F1 游戏化 + F2 任务链 + F3 L1 自动发证）

> **变更 ID**: 002-ailp-v4-refactor
> **负责模块**: F1 游戏化引擎 / F2 任务链 Capstone / F3 L1 自动发证（P0）
> **前置**: phase4-prd.md v1.2 + spec.md v1.0（14 AC）
> **版本**: 1.0

---

## 1. Context（现状锚点）

- **Lab 提交评分入口**: `lab_service.submit_and_grade()` — Lab 通过时（`passed`）已自动刷新技能雷达（`SkillRadarService.refresh_skill_scores`）。这是**发 XP + 触发 L1 判定的天然 hook 点**。
- **L1 判定已存在**: `CertificateService.auto_evaluate_l1()` 自动评定"必修课完成 + 均分阈值"，通过则创建 `approved` application。**缺口：手动 apply 触发**，且无任务链路径。
- **评分器**: `CodeGrader.grade_in_sandbox(code, test_cases)` — 按 test_cases 判分。任务链评分复用此机制。
- **认证模型**: `CertificationLevel`（含 `required_courses`、`min_average_score`）、`CertificationApplication`、`Certificate`、`CapstoneSubmission`（任务链路径重建为 Capstone 新方案后，CapstoneSubmission 相关端点停用）。

## 2. Goals / Non-Goals

**Goals**
- 游戏化：完成学习行为 → XP/升级/徽章/每日挑战（streak），全自动、幂等、只增不减
- 任务链：渐进小任务 + 即时自动评分 + 证据卡自动生成，零整理零人工评审
- L1 自动发证：Lab 全过或任务链完成 → 自动签发，幂等，事件驱动

**Non-Goals**
- 不做排行榜（P1）、付费门槛、扣 XP/降级惩罚
- 不做人工评审/抽检（v1.1 已废弃）
- 不做 AI 评审模型训练（复用 llm_router）
- 不做 Sprint 7 课程演进 / Docker 升级

## 3. 数据模型（新增 8 表，Phase 3-6 `create_only` 语义）

```sql
-- F1 游戏化
xp_events(id, user_id FK, action, ref_type, ref_id, xp, created_at)
  -- 幂等：UNIQUE(user_id, action, ref_type, ref_id) 保证同一行为只计一次
user_xp(user_id PK FK, total_xp, level, updated_at)
badges(id, code UNIQUE, name, description, icon, criteria JSON)   -- criteria 描述触发条件
user_badges(user_id FK, badge_code FK, awarded_at UNIQUE(user_id, badge_code), ref_id)

-- F2 任务链（capstone_chains/tasks/attempts）
capstone_chains(id, code UNIQUE, title, description, skill_tags JSON, is_active, xp_reward, cert_level_id FK NULL)
capstone_tasks(id, chain_id FK, seq, title, scenario, test_cases JSON, xp_reward)
capstone_attempts(id, task_id FK, user_id FK, status, score, output, passed, started_at, completed_at)
  -- 沙箱执行记录即证据；UNIQUE(user_id, task_id) 首过计 XP

-- F1 每日挑战
daily_challenges(id, date UNIQUE, task JSON, test_cases JSON, xp_reward, is_active)
daily_challenge_attempts(id, user_id FK, challenge_id FK, passed, completed_at, UNIQUE(user_id, challenge_id, date))
```

## 4. 服务层设计（backend/app/services/）

### gamification.py（新增）
- `award_xp(db, user_id, action, ref_type, ref_id, xp)` — 幂等发放（UNIQUE 冲突则跳过），更新 `user_xp` + 升级判定，返回 `{awarded, level_ups}`
- `award_badge(db, user_id, badge_code)` — 条件满足自动发，幂等
- `check_daily_challenge(db, user_id, date)` — 取当日挑战
- `submit_daily_challenge(db, user_id, date, code)` — 评分 → 通过发双倍 XP + streak
- `get_user_gamification(db, user_id)` — 汇总 XP/等级/徽章/streak 供前端

### capstone.py（新增）
- `list_chains/start_chain/get_task/submit_task` — 任务链生命周期
- `submit_task`：调 `CodeGrader.grade_in_sandbox` → 写 attempt → 通过则发 XP + 解锁下一任务 → 链全过则生成证据卡 + 发链完成徽章 + 触发 L1 判定
- `get_evidence_card(db, user_id, chain_id)` — 聚合证据卡（各任务分值/结果/耗时/时间戳）

### certificate_hooks.py 或并入 certificate.py
- `maybe_auto_certify_on_lab_pass(db, user_id)` — Lab 全过检查
- `maybe_auto_certify_on_chain_complete(db, user_id, chain_id)` — 复用 `auto_evaluate_l1`
- 保持 create_only 幂等：`_create_evaluation_result` 已处理自动通过

### lab_service 改动（hook）
在 `submit_and_grade()` 的 `passed` 分支追加：
1. `gamification.award_xp(lab-related)`
2. `certificate_hooks.maybe_auto_certify_on_lab_pass()`（若该 lab 属某认证必修）
3. （不动原技能雷达刷新）

## 5. API 设计（前端消费契约；Pydantic 为唯一真相源）

| Method | Path | 说明 |
|--------|------|------|
| GET | /gamification/me | XP/等级/徽章/streak 汇总 |
| GET | /gamification/badges | 徽章墙 |
| GET | /gamification/daily-challenge/today | 当日挑战 |
| POST | /gamification/daily-challenge/today/submit | 提交当日挑战 |
| GET | /capstone/chains | 任务链列表 |
| POST | /capstone/chains/{id}/start | 启动任务链 |
| GET | /capstone/chains/{id}/tasks/{seq} | 某任务 |
| POST | /capstone/chains/{id}/tasks/{seq}/submit | 提交任务（复用沙箱评分） |
| GET | /capstone/chains/{id}/evidence | 证据卡 |
| GET | /certifications/apply | 保留手动入口（额外触发，幂等） |

## 6. 前端（frontend/src/views/ 或 pages/）
- `GamificationPanel` 组件：等级进度条/徽章墙/streak（嵌入首页/进度页/学习页）
- `DailyChallengeBanner`：当日挑战入口（结果即时反馈）
- `CapstoneView`：任务链列表 + 任务执行 + 证据卡展示
- 前端修改必冒烟

## 7. 触发事件汇总（事件 → 行为）

| 事件 | 发 XP | 徽章 | L1 发证 |
|------|:---:|:---:|:---:|
| Lab 通过 | ✅ | 首个 Lab/系列 | ✅ 必修全过时 |
| 任务链任务通过 | ✅ | 完成者 | — |
| 任务链全完成 | ✅ 大额 | ✅ | ✅ 关联等级 |
| 每日挑战通过 | ✅ 双倍 | 连续打卡 | — |

## 8. 开放问题
- 无阻塞。XP 数值权重、徽章具体清单 → Tasks/实现时按 PRD 原则定（只增不减、成就向不惩罚向）

## 9. Tasks 概览
- T1: 数据模型（8 表 + 注册 + 契约测试）
- T2: gamification service + 幂等 + 升级/徽章
- T3: 每日挑战服务 + streak
- T4: capstone 任务链服务 + 评分复用 + 证据卡
- T5: L1 自动发证 hook（lab pass + chain complete）
- T6: API + schemas + 契约测试
- T7: 前端（GamificationPanel + DailyChallenge + CapstoneView）
- T8: 全量测试 + 冒烟 + 各 commit