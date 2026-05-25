# AILP 文档基线

> **AILP (AI Learning Platform)** — AI 能力的可信验证平台  
> 当前版本：V3.5（公开主页已上线）  
> 最后更新：2026-05-25

---

## 核心文档

| 文档 | 路径 | 说明 |
|------|------|------|
| **PRD** | `docs/archive/001-public-profile/prd.md` | 公开能力主页产品需求（已归档） |
| **Spec** | `docs/archive/001-public-profile/spec.md` | 功能规格与验收标准（已归档） |
| **Design** | `docs/archive/001-public-profile/design.md` | 技术设计文档（已归档） |
| **当前项目配置** | `AGENTS.md` | SDD 流程配置与项目约束 |
| **项目宪法** | `CONSTITUTION.md` | 不可违反的红线规则 |
| **已知陷阱** | `QUIRKS.md` | 环境约束与常见问题 |

---

## 变更历史

| 变更 ID | 标题 | 影响范围 | 状态 | 归档日期 |
|--------|------|---------|------|---------|
| 001-public-profile | 公开能力主页 | UserProfile模型+API+前端页面+OG标签 | ✅ 已归档 | 2026-05-25 |

---

## 进行中变更

| 变更 ID | 标题 | 当前阶段 | 分支 |
|--------|------|---------|------|
| 002-ailp-v4-refactor | AILP V4 重构（验证平台定位重置） | 📝 PO 阶段 | feature/001-public-profile |

> 注：002 的 PRD 已产出，待用户确认后进入 BA 阶段。

---

## 快速导航

- **后端代码**：`backend/app/`
- **前端代码**：`frontend/src/`
- **测试**：`backend/tests/`
- **实验/沙箱**：`labs/`, `sandbox/`
- **SDD 配置**：`AGENTS.md`, `CONSTITUTION.md`, `QUIRKS.md`

---

## 最近更新

- 2026-05-25: 归档 001-public-profile，QA 有条件通过（99.5% 通过率）
- 2026-05-25: 接入 hermes-harness SDD 流程，添加 pre-commit hooks
- 2026-05-25: 创建 002-ailp-v4-refactor 变更目录，产出 V4 PRD
