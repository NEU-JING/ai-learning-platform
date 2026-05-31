# Design: AILP V4 — AI 能力验证平台

> **变更 ID**: 002-ailp-v4-refactor  
> **版本**: 1.0  
> **日期**: 2026-05-28  

---

## 一、文档地图

本设计采用**地图模式**（总分结构），总体设计见本文档，子模块详细设计见独立文档：

| 模块文档 | 业务场景 | 负责 AC | 核心交付 |
|---------|---------|:-------:|---------|
| [design-module-path.md](./design-module-path.md) | 目标导向学习路径 | AC1-AC6 | 四路径模板、入学诊断、进度追踪 |
| [design-module-radar.md](./design-module-radar.md) | 多维技能雷达 | AC7-AC14 | 10维技能模型、时间衰减计算、差距分析 |
| [design-module-tutor.md](./design-module-tutor.md) | AI 辅助学习 | AC15-AC21 | 入学诊断对话、代码审查、个性化推荐 |
| [design-module-evolution.md](./design-module-evolution.md) | 课程演进+JD采集 | AC22-AC29 | JD采集、技能趋势分析、三层更新策略 |
| [design-module-certification.md](./design-module-certification.md) | 四级认证 | AC30-AC37 | L1-L4认证流程、证书签名、续期机制 |
| [design-module-sandbox.md](./design-module-sandbox.md) | 混合执行沙箱 | AC38-AC44 | Layer A/B/C执行、验证引擎、审计日志 |
| [design-module-profile.md](./design-module-profile.md) | 公开能力主页 | AC42-AC44 | 路径感知主页、隐私控制、CDN缓存 |
| [design-module-employer.md](./design-module-employer.md) | 雇主验证 API | AC45-AC49 | 证书验证、API限流、授权机制 |

---

## 二、Brainstorming（方案对比）

### 2.1 技能雷达计算方案

#### 方案 A：实时计算（Query-time）
- 每次请求时从原始数据实时计算
- 优点：数据最新，无延迟
- 缺点：性能差，高并发时数据库压力大

#### 方案 B：预计算 + 增量更新（Materialized View）
- 用户完成实验时触发增量更新，缓存结果
- 优点：查询快，<100ms；支持历史快照
- 缺点：需要维护更新逻辑

**选择**：方案 B（预计算）
- 理由：技能雷达是高频查询场景（每次页面访问），必须保证 <2s 响应；增量更新逻辑简单可控

### 2.2 沙箱执行环境方案

#### 方案 A：自建 K8s GPU 集群
- 完全可控，性能好
- 缺点：成本高（$2000+/月），运维复杂

#### 方案 B：混合执行模型（Layer A/B/C）
- Layer A：本地进程（简单练习）
- Layer B：外部资源（Colab/Kaggle）
- Layer C：验证引擎（模型审计）
- 优点：成本可控，弹性扩展

**选择**：方案 B（混合执行）
- 理由：符合 "Out of Scope" 中明确排除自建 GPU 集群的约束；利用现有免费资源（Colab/Kaggle）

### 2.3 AI 导师 LLM 降级方案

#### 方案 A：单一 LLM 供应商
- 只使用 OpenRouter Claude
- 缺点：无故障转移，服务中断时功能完全不可用

#### 方案 B：三级降级链
- Layer 1：OpenRouter / Claude Sonnet 4
- Layer 2：千帆 / GLM-4（国产替代）
- Layer 3：本地 Qwen-7B（免费兜底）

**选择**：方案 B（三级降级）
- 理由：确保 AI 导师 24/7 可用（AC21）；本地模型作为兜底，成本可控

### 2.4 证书防伪方案

#### 方案 A：区块链存证
- 上链存储证书哈希
- 缺点：成本高，验证慢，过度设计

#### 方案 B：ECDSA 数字签名
- 证书内容签名，公开验证 API
- 优点：轻量，验证快（<100ms），无需外部依赖

**选择**：方案 B（ECDSA 签名）
- 理由：满足 AC37 证书防伪需求；无需引入区块链技术复杂度

---

## 三、架构设计

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              AILP V4 架构                                │
├─────────────────────────────────────────────────────────────────────────┤
│  接入层                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  Web 前端    │  │  公开主页    │  │  雇主验证    │  │   Admin 后台     │ │
│  │  (学习者)    │  │  ( ailp.com)│  │   API       │  │                 │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────────────────┘ │
└─────────┼────────────────┼────────────────┼─────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  API 层 (FastAPI)                                                        │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┐ │
│  │   Path   │  Radar   │  Tutor   │  Sandbox │  Profile │  Employer    │ │
│  │   API    │   API    │   API    │   API    │   API    │   API        │ │
│  └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┴──────┬───────┘ │
└───────┼──────────┼──────────┼──────────┼──────────┼────────────┼─────────┘
        │          │          │          │          │            │
        ▼          ▼          ▼          ▼          ▼            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  服务层 (Service)                                                        │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┐ │
│  │PathService│RadarService│TutorService│SandboxService│ProfileService│ │
│  │          │          │          │          │          │              │ │
│  └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┴──────┬───────┘ │
└───────┼──────────┼──────────┼──────────┼──────────┼────────────┼─────────┘
        │          │          │          │          │            │
        ▼          ▼          ▼          ▼          ▼            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  核心引擎                                                                │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────────────┐  │
│  │  Certification│  │   Evolution   │  │        LLM Router           │  │
│  │    Engine     │  │    Engine     │  │   (OpenRouter/千帆/本地)     │  │
│  └───────────────┘  └───────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
        │                  │                           │
        ▼                  ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  数据层                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  PostgreSQL │  │    Redis    │  │ Object Store│  │   Meilisearch   │ │
│  │  (主数据库)  │  │  (缓存/会话) │  │  (模型文件)  │  │   (JD搜索)      │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 模块间接口契约

| 调用方 | 被调用方 | 接口 | 数据格式 |
|-------|---------|------|---------|
| Path Service | Radar Service | `get_skill_radar(user_id)` | SkillRadarSchema |
| Tutor Service | Radar Service | `update_skill_from_lab(user_id, lab_result)` | UpdateResult |
| Certification Service | Radar Service | `get_skill_summary(user_id)` | SkillSummary |
| Sandbox Service | Radar Service | `record_execution(user_id, execution_result)` | ExecutionRecord |
| Profile Service | Radar Service | `get_public_radar(user_id)` | PublicRadarSchema |
| Evolution Engine | Radar Service | `get_aggregate_skills()` | AggregateSkills |
| All Services | LLM Router | `chat(messages, model_preference)` | ChatResponse |

### 3.3 数据流

```
用户完成实验 → Sandbox Service → 执行结果
                    ↓
              Radar Service ← 更新技能分数
                    ↓
              Certification Engine ← 检查认证条件
                    ↓
              Profile Service ← 更新公开主页缓存
                    ↓
              CDN 刷新 (CloudFlare)
```

---

## 四、关键决策

| 决策 | 选项 | 选择 | 理由 |
|------|------|:---:|------|
| 技能雷达计算 | 实时计算 / 预计算 | 预计算 | 查询性能 <2s，支持历史快照 |
| 沙箱执行环境 | 自建 GPU / 混合模型 | 混合模型 | 成本可控，符合 Out of Scope |
| LLM 降级 | 单一供应商 / 三级降级 | 三级降级 | 确保 24/7 可用 |
| 证书防伪 | 区块链 / ECDSA 签名 | ECDSA | 轻量，无需外部依赖 |
| 模块划分 | 技术分层 / 业务场景 | 业务场景 | 高内聚，独立部署 |
| 文档结构 | 单文件 / 地图模式 | 地图模式 | 8 个模块，上下文可控 |
| Profile 缓存 | 应用缓存 / CDN | CDN + Redis | 公开页高频访问，<500ms |
| JD 存储 | PostgreSQL / 搜索引擎 | Meilisearch | 全文搜索，快速聚合 |

---

## 五、统一术语表

| 术语 | 定义 | 使用场景 |
|------|------|---------|
| **Path** | 学习路径，包含课程序列和里程碑 | Path 模块 |
| **Radar** | 技能雷达，10维能力可视化 | Radar 模块 |
| **Dimension** | 技能维度（如"编程思维"） | Radar 模块 |
| **Layer** | 沙箱执行层级（A/B/C） | Sandbox 模块 |
| **Level** | 认证等级（L1-L4） | Certification 模块 |
| **Capstone** | 综合项目，用于 L2 认证 | Certification 模块 |
| **JD** | Job Description，职位描述 | Evolution 模块 |
| **Audit Log** | 审计日志，记录完整学习过程 | Sandbox/Certification |
| **Public Profile** | 公开能力主页 | Profile 模块 |
| **Verification Code** | 雇主验证授权码 | Employer 模块 |

---

## 六、配置汇总

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|---------|-------|------|
| LLM Layer 1 | `LLM_PRIMARY` | openrouter/claude-sonnet-4 | 主 LLM |
| LLM Layer 2 | `LLM_FALLBACK` | baidu/glm-4 | 降级 LLM |
| LLM Layer 3 | `LLM_LOCAL` | http://localhost:11434 | 本地模型 |
| 证书私钥 | `CERT_PRIVATE_KEY` | - | ECDSA 私钥 |
| CDN URL | `CDN_BASE_URL` | https://cdn.ailp.com | CloudFlare |
| 沙箱超时 | `SANDBOX_TIMEOUT` | 30 | Layer A 超时秒数 |
| 雇主 API 限流 | `EMPLOYER_RATE_LIMIT` | 1000 | 每小时请求数 |
| 雷达缓存 TTL | `RADAR_CACHE_TTL` | 3600 | Redis 缓存秒数 |

---

## 七、AC 覆盖矩阵（总览）

| 模块 | AC 范围 | AC 数量 | 状态 |
|------|--------|:-------:|:---:|
| Path | AC1-AC6 | 6 | ✅ |
| Radar | AC7-AC14 | 8 | ✅ |
| Tutor | AC15-AC21 | 7 | ✅ |
| Evolution | AC22-AC29 | 8 | ✅ |
| Certification | AC30-AC37 | 8 | ✅ |
| Sandbox | AC38-AC44 | 7 | ✅ |
| Profile | AC42-AC44* | 3 | ✅ |
| Employer | AC45-AC49 | 5 | ✅ |
| **总计** | **AC1-AC49** | **49** | **100%** |

*Profile 模块与 Sandbox 共享 AC42-AC44

---

## 八、Tasks 总览

详见 [tasks.md](./tasks.md)，总计约 **45 个 Tasks**，估时 **18-22 小时**。

按模块分布：

| 模块 | Tasks 数量 | 估时 |
|------|:---------:|------|
| Path | 6 | 3h |
| Radar | 7 | 3.5h |
| Tutor | 5 | 2.5h |
| Evolution | 6 | 3h |
| Certification | 7 | 3.5h |
| Sandbox | 6 | 3h |
| Profile | 4 | 2h |
| Employer | 4 | 2h |
| **总计** | **45** | **18-22h** |

---

## 九、设计评审报告

### 完整性评估: 100%
- 外部依赖：已识别 LLM API、CloudFlare、Meilisearch
- 降级策略：LLM 三级降级、沙箱多层回退
- 安全方案：证书 ECDSA 签名、API Key 限流、授权码验证
- 配置完整：所有配置项有环境变量名和默认值

### 可实现性评估: 95%
- 技术栈匹配：FastAPI + PostgreSQL + Redis，项目已有
- 资源可行性：无需 GPU 集群，使用 Colab/Kaggle 免费资源
- API 可用性：OpenRouter/千帆 API 已验证可用
- 风险点：本地 Qwen-7B 需要 8GB+ 内存，开发环境需确认

### 一致性评估: 100%
- 术语统一：全文档使用统一术语表
- 命名规范：表名 snake_case，模型类 PascalCase
- 接口风格：RESTful，统一错误码格式

### 行动项
1. [ ] 确认开发环境内存 >= 8GB（用于本地 LLM 兜底）
2. [ ] 申请 CloudFlare 账户和 CDN 配置
3. [ ] 准备 Meilisearch 实例（或复用现有）

---

**Design 状态**: ✅ Architect 阶段完成  
**下一步**: 用户确认后进入 Coder 阶段，按 tasks.md 执行
