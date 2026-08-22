# Tasks: Phase 4 游戏化学习体验（P0）

> 变更: 002-ailp-v4-refactor | 分支: phase4/002-ailp-v4-refactor
> 前置: PRD v1.2 + Spec v1.0 + design-module-gamified.md
> 每个 Task 一个 commit，独立 review；TDD（先写测试红→绿）

## 1. 数据模型（T1）

- [ ] 1.1 新增 8 表模型：xp_events / user_xp / badges / user_badges / capstone_chains / capstone_tasks / capstone_attempts / daily_challenges + daily_challenge_attempts
- [ ] 1.2 模型注册进 models/__init__.py + __all__
- [ ] 1.3 数据契约测试补齐（新表在 test_data_contract.py 覆盖）

## 2. 游戏化服务（T2, T3）

- [ ] 2.1 gamification.py：award_xp 幂等发放 + user_xp 累计 + 升级判定
- [ ] 2.2 award_badge 条件发放（首个 Lab / 任务链完成 / 连续打卡）
- [ ] 2.3 每日挑战：today 获取 + submit 评分 + 双倍 XP + streak
- [ ] 2.4 get_user_gamification 汇总（TDD：award_xp 幂等、升级、徽章、streak 归零边界）

## 3. 任务链服务（T4, T5）

- [ ] 3.1 capstone.py：list/start/get_task
- [ ] 3.2 submit_task：复用 CodeGrader → 写 attempt → 发 XP → 解锁下一任务
- [ ] 3.3 链全过 → 证据卡生成 + 完成徽章 + 触发 L1 判定
- [ ] 3.4 L1 自动发证 hook：lab pass 触发（复用 auto_evaluate_l1，幂等）
- [ ] 3.5 L1 自动发证 hook：chain complete 触发

## 4. API + Schemas（T6）

- [ ] 4.1 gamification schemas + 路由（/gamification/me, badges, daily-challenge）
- [ ] 4.2 capstone schemas + 路由（chains, start, task, submit, evidence）
- [ ] 4.3 契约测试 + 前端字段名一致（config/schemas 引用核对）

## 5. 前端（T7）

- [ ] 5.1 GamificationPanel（等级/徽章/streak，嵌入进度页）
- [ ] 5.2 DailyChallengeBanner（当日挑战 + 即时反馈）
- [ ] 5.3 CapstoneView（任务链列表 + 执行 + 证据卡）
- [ ] 5.4 前端冒烟（Playwright）

## 6. 收口（T8）

- [ ] 6.1 全量测试（pytest）+ 契约测试
- [ ] 6.2 post-coding-review 三阶段
- [ ] 6.3 各模块独立 commit + 推送