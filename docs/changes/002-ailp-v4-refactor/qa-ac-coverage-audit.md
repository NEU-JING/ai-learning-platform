# QA Agent - AC 覆盖审核报告

**变更 ID**: 002-ailp-v4-refactor  
**Phase**: Phase 1 (Path + Radar)  
**审核时间**: 2026-05-31  
**审核依据**: QA Agent Skill v1.1.0 (R10 E2E完整性规则)  

---

## 审核结论：❌ BLOCKED

**核心问题**: Coder Agent 机械满足"≥7个E2E用例"数量要求，但**AC覆盖不完整**。

E2E测试的门禁标准应该是**完整覆盖所有AC**，而非单纯满足数量。

---

## Phase 1 AC 清单 (14个)

### 路径系统 (AC1-AC6)

| AC | 描述 | 覆盖状态 | E2E文件 | 行号 |
|:---:|------|:-------:|---------|------|
| AC1 | 目标选择与路径生成 | ✅ | diagnosis.spec.js | L60-138 |
| AC2 | 入学诊断支持起点调整 | ✅ | diagnosis.spec.js | L141-239 |
| AC3 | 路径进度可追踪 | ✅ | path-progress.spec.js | L61-215 |
| AC4 | 能力缺口自动诊断 | ✅ | skill-gap.spec.js | L61-218 |
| AC5 | 支持Fast Track模式 | ❌ | **缺失** | - |
| AC6 | 路径可视化数据接口 | ❌ | **缺失** | - |

### 技能雷达 (AC7-AC14)

| AC | 描述 | 覆盖状态 | E2E文件 | 行号 |
|:---:|------|:-------:|---------|------|
| AC7 | 10维分层技能模型落地 | ✅ | radar-display.spec.js | L46-183 |
| AC8 | 硬实力/软实力/路径特化维度区分 | ✅ | radar-display.spec.js | L120-169 |
| AC9 | 自动汇总多源数据 | ✅ | radar-update.spec.js | L68-147 |
| AC10 | 支持时间衰减计算 | ❌ | **缺失** | - |
| AC11 | 雷达图可视化数据生成 | ❌ | **缺失** | - |
| AC12 | 历史版本对比功能 | ⚠️ 部分 | radar-update.spec.js | L149-189 |
| AC13 | 与目标岗位差距分析 | ✅ | radar-update.spec.js | L191-225 |
| AC14 | 路径特化维度权重调整 | ❌ | **缺失** | - |

---

## 覆盖统计

```
总 AC 数: 14 (Phase 1)
E2E 覆盖: 9
覆盖率: 64.3%
缺失: 5 (AC5, AC6, AC10, AC11, AC14)
部分覆盖: 1 (AC12)
```

---

## 缺失AC详细说明

### AC5: 支持Fast Track模式
**spec.md定义**:
> 用户选择"3个月内跳槽"目标 → 选择Fast Track模式 → 生成8周密集路径，每天需完成2-3个实验

**缺失原因**: diagnosis.spec.js中仅测试了fast_track模式的路径创建，未验证密集路径的排期和每日任务量计算。

**需要补充的E2E**:
```javascript
// Fast Track模式验证
- 选择"3个月内跳槽"目标
- 验证返回mode: 'fast_track'
- 验证estimated_duration_weeks = 8
- 验证每日任务量: 2-3个实验
```

---

### AC6: 路径可视化数据接口
**spec.md定义**:
> AI工程师用户查看路径页面 → 请求路径数据 → 返回包含阶段节点、课程依赖、里程碑标记的JSON数据

**缺失原因**: 无专门测试验证可视化数据接口的结构。

**需要补充的E2E**:
```javascript
// 路径可视化数据接口
- GET /api/v1/paths/{id}/visualization
- 验证返回结构: { nodes: [...], edges: [...] }
- 验证节点包含阶段信息
- 验证边包含课程依赖关系
```

---

### AC10: 支持时间衰减计算
**spec.md定义**:
> 用户3个月前完成Phase 1实验，最近完成Phase 3实验 → 查看当前雷达图 → Phase 1数据权重降低，Phase 3数据权重提高，体现技能时效性

**缺失原因**: radar-update.spec.js未验证时间衰减算法的实际权重计算。

**需要补充的E2E**:
```javascript
// 时间衰减计算
- 创建3个月前的历史实验记录
- 创建最近的实验记录
- 验证雷达分数反映时间权重差异
- 验证Phase 1数据权重 < Phase 3数据权重
```

---

### AC11: 雷达图可视化数据生成
**spec.md定义**:
> 用户访问技能页面 → 请求雷达数据 → 返回包含维度名称、分数、满分、百分位的JSON，可直接渲染雷达图

**缺失原因**: radar-display.spec.js验证了维度数据，但未专门验证可视化所需的完整数据结构。

**需要补充的E2E**:
```javascript
// 雷达图可视化数据
- GET /api/v1/radar
- 验证返回可直接用于Chart.js/ECharts的结构
- 验证包含: labels, datasets, options
```

---

### AC14: 路径特化维度权重调整
**spec.md定义**:
> AI应用者路径用户选择"产品经理"细分方向 → 更新路径配置 → 雷达图增加"场景洞察"和"需求转化"维度权重，降低"算法深度"权重

**缺失原因**: 无测试验证路径特化对维度权重的调整。

**需要补充的E2E**:
```javascript
// 路径特化维度权重调整
- 切换路径类型到 ai-applier + 细分方向 product_manager
- 验证雷达维度权重变化
- 验证"场景洞察"权重提升
- 验证"算法深度"权重降低
```

---

## 建议修复方案

### 方案1: 补充缺失的E2E用例 (推荐)

创建以下5个E2E测试文件：

1. `fast-track-mode.spec.js` - 覆盖AC5
2. `path-visualization.spec.js` - 覆盖AC6
3. `time-decay.spec.js` - 覆盖AC10
4. `radar-chart-data.spec.js` - 覆盖AC11
5. `path-specialization.spec.js` - 覆盖AC14

### 方案2: 扩展现有E2E文件

在现有文件中补充测试用例：
- `diagnosis.spec.js` 补充AC5的Fast Track验证
- `path-progress.spec.js` 补充AC6的可视化数据验证
- `radar-update.spec.js` 补充AC10的时间衰减验证
- `radar-display.spec.js` 补充AC11和AC14的验证

---

## QA 判定

根据QA Agent Skill R10规则：

> **5.1 检查 E2E 用例存在性** - ✅ 通过 (7个用例 ≥ 7)  
> **5.2 检查 PR 与 CI 执行状态** - ⏳ 待PR创建后验证  
> **5.3 检查 CI 执行结果** - ⏳ 待CI触发后验证  

**但**: E2E用例应**完整覆盖AC**，而非仅满足数量要求。

**结论**: 返回Coder Agent补充缺失的AC覆盖。

---

## 后续行动

1. Coder Agent补充5个缺失AC的E2E测试
2. 重新运行全量E2E测试验证
3. QA Agent再次审核AC覆盖矩阵
4. 创建PR并触发CI

---

**审核人**: QA Agent  
**状态**: BLOCKED → CODER_FIX_REQUIRED
