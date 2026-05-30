# AILP 文档地图

> 快速找到你需要的文档

---

## 🔥 当前变更（进行中）

**变更 ID**: `002-ailp-v4-refactor`  
**状态**: Design阶段完成，等待进入Coder阶段

| 想做什么 | 看这里 |
|---------|-------|
| 了解产品要做什么 | [prd.md](changes/002-ailp-v4-refactor/prd.md) |
| 查看功能规格和验收标准 | [spec.md](changes/002-ailp-v4-refactor/spec.md) |
| 了解技术架构 | [design.md](changes/002-ailp-v4-refactor/design.md) |
| 查看具体模块设计 | `design-module-*.md` (8个模块) |
| 查看开发任务 | [tasks.md](changes/002-ailp-v4-refactor/tasks.md) |
| 查看设计评审结果 | [design-review-report.md](changes/002-ailp-v4-refactor/design-review-report.md) |
| 了解分阶段交付策略 | [incremental-delivery-analysis.md](changes/002-ailp-v4-refactor/incremental-delivery-analysis.md) |

**模块设计文档**:
- [Path模块](changes/002-ailp-v4-refactor/design-module-path.md) - 学习路径定制
- [Radar模块](changes/002-ailp-v4-refactor/design-module-radar.md) - 技能雷达图
- [Tutor模块](changes/002-ailp-v4-refactor/design-module-tutor.md) - AI导师
- [Certification模块](changes/002-ailp-v4-refactor/design-module-certification.md) - 四级证书
- [Sandbox模块](changes/002-ailp-v4-refactor/design-module-sandbox.md) - 代码执行沙箱
- [Profile模块](changes/002-ailp-v4-refactor/design-module-profile.md) - 能力画像
- [Employer模块](changes/002-ailp-v4-refactor/design-module-employer.md) - 雇主验证
- [Evolution模块](changes/002-ailp-v4-refactor/design-module-evolution.md) - 内容演进

---

## 📚 按角色查找

### 如果你是产品经理 (PO)
1. [当前变更PRD](changes/002-ailp-v4-refactor/prd.md)
2. [产品背景分析](../docs/AILP-V4-PRD-重构版.md) (补充阅读)
3. [课程体系重构](../docs/AILP-V4-课程体系重构.md) (补充阅读)

### 如果你是开发工程师 (Coder)
1. [架构总览](changes/002-ailp-v4-refactor/design.md)
2. [模块设计文档](changes/002-ailp-v4-refactor/design-module-*.md) - 看你负责哪个模块
3. [开发任务清单](changes/002-ailp-v4-refactor/tasks.md) - 39项任务
4. [项目宪法](../CONSTITUTION.md) - 不可违反的规则
5. [开发陷阱](../QUIRKS.md) - 环境问题和解决方案

### 如果你是架构师
1. [架构总览](changes/002-ailp-v4-refactor/design.md)
2. [8个模块设计文档](changes/002-ailp-v4-refactor/design-module-*.md)
3. [设计评审报告](changes/002-ailp-v4-refactor/design-review-report.md)
4. [增量交付分析](changes/002-ailp-v4-refactor/incremental-delivery-analysis.md)

### 如果你是测试/QA
1. [功能规格](changes/002-ailp-v4-refactor/spec.md) - 49项AC
2. [设计评审报告](changes/002-ailp-v4-refactor/design-review-report.md)

---

### SDD项目配置（根目录）

| 文件 | 用途 |
|------|------|
| [CONSTITUTION.md](../CONSTITUTION.md) | 项目宪法 - 不可违反的红线 |
| [AGENTS.md](../AGENTS.md) | SDD流程配置 |
| [QUIRKS.md](../QUIRKS.md) | 已知陷阱和环境问题 |
| [README.md](../README.md) | 项目根说明 |

### 工程实践文档

| 文件 | 路径 | 用途 |
|------|------|------|
| [DEVELOPMENT_HARNESS.md](engineering/DEVELOPMENT_HARNESS.md) | `docs/engineering/` | 分支策略、CI/CD、代码质量规范 |

---

## 📦 归档文档

### 已完成的变更
- [001-public-profile](archive/001-public-profile/) - 公开能力主页（已上线）

### 旧版本文档
- [PRD-v2.0](archive/PRD-v2.0-20260513.md) - 2026-05-13版本
- [DESIGN-v2.0](archive/DESIGN-v2.0-20260513.md) - 2026-05-13版本

### 开发过程文档
- [backups-20260531](archive/backups-20260531/) - 开发过程中的临时文档

---

## 🎯 常用快捷方式

```bash
# 查看最新PRD
cat docs/changes/002-ailp-v4-refactor/prd.md

# 查看当前任务
cat docs/changes/002-ailp-v4-refactor/tasks.md | head -100

# 查看项目约束
cat CONSTITUTION.md

# 查看环境陷阱
cat QUIRKS.md
```

---

## 📊 文档统计

| 类别 | 数量 |
|------|------|
| 当前变更文档 | 13个 |
| 模块设计文档 | 8个 |
| **SDD项目配置（根目录）** | 4个 |
| 工程实践文档 | 1个 |
| 已归档变更 | 1个 |
| 历史版本文档 | 2个 |
| 开发过程文档 | 9个 |

---

*最后更新: 2026-05-31*
