# AILP 文档基线 (V4)

> **AILP (AI Learning Platform)** — 从学习平台到 AI 能力验证平台  
> 当前版本：V4.0（重构中）  
> 最后更新：2026-05-31

---

## 文档结构（SDD 规范）

```
docs/
├── current/          # 当前权威文档（只读索引）
├── changes/          # 进行中的变更
│   └── 002-ailp-v4-refactor/  # V4重构（当前进行中）
├── archive/          # 已归档变更
│   ├── 001-public-profile/    # ✅ 已归档
│   ├── backups-20260531/      # 开发过程文档
│   ├── PRD-v2.0-20260513.md   # 旧版本PRD
│   └── DESIGN-v2.0-20260513.md # 旧版本Design
├── engineering/      # 工程实践文档
│   └── DEVELOPMENT_HARNESS.md # 分支策略、CI/CD规范
└── templates/        # SDD文档模板
```

---

## 当前变更状态

| 变更 ID | 标题 | 当前阶段 | 状态 |
|--------|------|---------|------|
| **002-ailp-v4-refactor** | AILP V4 重构 — AI能力验证平台 | Design | 📝 等待用户确认Design后进入Coder阶段 |

> 注：Coder阶段曾因"SDD技能未启用"回滚，当前等待重新启动。

---

## 权威文档索引

### 当前变更 (002-ailp-v4-refactor)

| 文档 | 路径 | 说明 |
|------|------|------|
| **PRD** | `docs/changes/002-ailp-v4-refactor/prd.md` | 产品需求：从学习平台到验证平台 |
| **Spec** | `docs/changes/002-ailp-v4-refactor/spec.md` | 功能规格：49项AC，100%覆盖 |
| **Design (主)** | `docs/changes/002-ailp-v4-refactor/design.md` | 架构总览 |
| **Design (Path)** | `docs/changes/002-ailp-v4-refactor/design-module-path.md` | 学习路径模块 |
| **Design (Radar)** | `docs/changes/002-ailp-v4-refactor/design-module-radar.md` | 技能雷达模块 |
| **Design (Tutor)** | `docs/changes/002-ailp-v4-refactor/design-module-tutor.md` | AI导师模块 |
| **Design (Cert)** | `docs/changes/002-ailp-v4-refactor/design-module-certification.md` | 证书验证模块 |
| **Design (Sandbox)** | `docs/changes/002-ailp-v4-refactor/design-module-sandbox.md` | 沙箱执行模块 |
| **Design (Profile)** | `docs/changes/002-ailp-v4-refactor/design-module-profile.md` | 能力画像模块 |
| **Design (Employer)** | `docs/changes/002-ailp-v4-refactor/design-module-employer.md` | 雇主验证模块 |
| **Design (Evolution)** | `docs/changes/002-ailp-v4-refactor/design-module-evolution.md` | 内容演进模块 |
| **Tasks** | `docs/changes/002-ailp-v4-refactor/tasks.md` | 39项任务，22小时估时 |
| **评审报告** | `docs/changes/002-ailp-v4-refactor/design-review-report.md` | Design Review结果 |
| **增量分析** | `docs/changes/002-ailp-v4-refactor/incremental-delivery-analysis.md` | 分阶段交付策略 |

### 项目配置（根目录）

| 文档 | 路径 | 说明 |
|------|------|------|
| **项目宪法** | `CONSTITUTION.md` | 不可违反的红线规则 |
| **流程配置** | `AGENTS.md` | SDD流程配置与Agent约束 |
| **已知陷阱** | `QUIRKS.md` | 环境约束与常见问题 |
| **开发工具** | `DEVELOPMENT_HARNESS.md` | 开发工具链配置 |

---

## 快速导航

- **后端代码**: `backend/app/`
- **前端代码**: `frontend/src/`
- **测试**: `backend/tests/`
- **实验/沙箱**: `labs/`, `sandbox/`
- **课程数据**: `backend/app/data/phase{1-6}/`

---

## 变更历史

| 变更 ID | 标题 | 影响范围 | 状态 | 归档日期 |
|--------|------|---------|------|---------|
| 001-public-profile | 公开能力主页 | UserProfile模型+API+前端页面+OG标签 | ✅ 已归档 | 2026-05-25 |

---

## 最近更新

- 2026-05-31: 整理文档结构，归档旧版本PRD/DESIGN
- 2026-05-30: 数据恢复 - Phase 3 42章深化内容已保住
- 2026-05-29: Design Review完成，100%AC覆盖，Coder阶段准备就绪
- 2026-05-28: Coder阶段因SDD技能未启用回滚
- 2026-05-25: 归档 001-public-profile，接入 hermes-harness SDD流程
