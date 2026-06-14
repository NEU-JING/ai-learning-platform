# AILP V4 Design Baseline

> **归档来源**: change 002-ailp-v4-refactor
> **归档时间**: 2026-06-14

---

## 变更摘要

**目标**: 将 AILP 从学习平台重构为 AI 能力验证平台

### 关键架构决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 技能雷达计算 | 预计算 + 90天半衰期 | 查询性能 <2s，支持历史快照 |
| 沙箱执行 | 混合模型 Layer A/B/C | 成本可控，利用免费资源 |
| LLM 降级 | 三级降级链 | 确保 24/7 可用 |
| 证书防伪 | ECDSA-SHA256 数字签名 | 轻量，无需外部依赖 |
| 模块划分 | 业务场景维度（8模块） | 高内聚，独立部署 |
| 文档结构 | 地图模式 | 上下文可控 |
| Profile 缓存 | CDN + Redis | 公开页高频访问 <500ms |
| JD 存储 | Meilisearch | 全文搜索，快速聚合 |

### 架构层次

```
接入层: Web前端 / 公开主页 / 雇主验证API / Admin后台
API层:  Path/Radar/Tutor/Sandbox/Profile/Employer APIs
服务层:  各模块 Service
核心引擎: Certification Engine / Evolution Engine / LLM Router
数据层:  PostgreSQL / Redis / Object Store / Meilisearch
```

### 模块总览

| 模块 | AC 范围 | 核心交付 |
|------|--------|---------|
| Path | AC1-AC6 | 四路径模板、入学诊断、进度追踪 |
| Radar | AC7-AC14 | 10维技能模型、时间衰减、差距分析 |
| Tutor | AC15-AC21 | 诊断对话、代码审查、个性化推荐 |
| Evolution | AC22-AC29 | JD采集、技能趋势、三层更新 |
| Certification | AC30-AC37 | L1-L4认证、证书签名、续期 |
| Sandbox | AC38-AC44 | Layer A/B/C执行、验证引擎 |
| Profile | AC42-AC44 | 路径感知主页、隐私控制 |
| Employer | AC45-AC49 | 证书验证、API限流、授权 |

### 完成状态

| Phase | 状态 | 完成时间 |
|:-----:|:----:|:--------:|
| Phase 1: 基础数据层（Path + Radar） | ✅ coder_to_qa | 2026-05-31 |
| Phase 2: 核心服务层（Tutor + Certification） | ✅ 已验收 | 2026-06-01 |
| Phase 3: 验证与执行（Sandbox + Profile + Employer） | ⏳ 待启动 | — |
| Phase 4: 演进引擎（Evolution） | ⏳ 待启动 | — |
| Phase 5: 集成测试 | ⏳ 待启动 | — |
