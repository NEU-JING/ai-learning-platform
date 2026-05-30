# SDD 增量交付模式分析

## 一、Phase 依赖关系验证

基于 design.md 的**模块间接口契约**分析：

| Phase | 模块 | 依赖 | 可独立交付 |
|-------|------|------|:----------:|
| Phase 1 | Path + Radar | 无 | ✅ **完全独立** |
| Phase 2 | Tutor | Radar Service (`get_skill_radar`) | ✅ 依赖 Phase 1 |
| Phase 2 | Certification | Radar Service (`get_skill_summary`) | ✅ 依赖 Phase 1 |
| Phase 3 | Sandbox | Radar Service (`record_execution`) | ✅ 依赖 Phase 1+2 |
| Phase 3 | Profile | Radar Service (`get_public_radar`) | ✅ 依赖 Phase 1+2 |
| Phase 3 | Employer | Certification + Profile | ✅ 依赖 Phase 1+2+3 |
| Phase 4 | Evolution | Radar Service (`get_aggregate_skills`) | ✅ 依赖 Phase 1+2 |

**结论**：
1. **Phase 1 完全不依赖 Phase 2**，可以独立交付
2. Phase 2 (Tutor) 依赖 Phase 1 的 Radar 数据
3. Phase 3+ 都依赖前面 Phase 的基础能力

---

## 二、增量交付模式的优势

### 当前 SDD 流程（线性瀑布）
```
Design → All Tasks → All Coding → Review → QA → 验收 → 归档
   ↑                                      ↓
   └────── 问题发现晚，返工成本高 ────────┘
```

### 提议的增量交付模式
```
Design → Phase 1 Tasks → Coding → Review → QA → 验收 → (可上线)
            ↓
        Phase 2 Tasks → Coding → Review → QA → 验收 → (可上线)
            ↓
        Phase 3 Tasks → Coding → Review → QA → 验收 → (可上线)
```

**优势**：
1. **快速验证**：Phase 1 完成即可验证核心架构是否正确
2. **风险可控**：问题在早期发现，返工范围小
3. **用户反馈**：每 Phase 交付后可演示，及时调整方向
4. **渐进上线**：Phase 1 稳定后可先上线，后续 Phase 迭代追加
5. **团队节奏**：小步快跑，避免长周期开发的心理压力

---

## 三、SDD 技能如何支持增量交付

### 方案 A：Phase 内嵌套子 SDD 流程（推荐）

保持顶层 SDD 流程不变，在每个 Phase 内增加 **Mini Review + Mini QA**：

```
PO → BA → Architect → [Phase 1 Coder → Phase 1 Review → Phase 1 QA] → 
                      [Phase 2 Coder → Phase 2 Review → Phase 2 QA] →
                      [Phase 3 Coder → Phase 3 Review → Phase 3 QA] →
                      最终 Review → 最终 QA → 验收 → 归档
```

**实现方式**：
1. `tasks.md` 保持 5 个 Phase 的分组结构
2. 每完成一个 Phase，主动触发 Reviewer + QA
3. `.sdd-state.json` 记录 Phase 级别状态

**JSON 状态扩展**：
```json
{
  "change_id": "002-ailp-v4-refactor",
  "flow_level": "Standard",
  "current_phase": "coder",
  "current_sub_phase": "phase_2_tutor",  // 新增
  "phases_completed": ["po", "ba", "architect"],
  "sub_phases_completed": ["phase_1_path_radar"],  // 新增
  "phase_status": {
    "phase_1": {"status": "completed", "ac_covered": ["AC1-AC14"]},
    "phase_2": {"status": "in_progress", "ac_covered": ["AC15-AC21"]}
  }
}
```

### 方案 B：多变更 ID 拆分（替代方案）

将 5 个 Phase 拆分为 5 个独立变更：
- `002-ailp-v4-phase1-path-radar`
- `003-ailp-v4-phase2-tutor`
- `004-ailp-v4-phase3-certification`
- ...

**优点**：完全遵循现有 SDD 流程
**缺点**：管理复杂，变更间依赖需要手动协调

---

## 四、对 SDD 技能的改进建议

### 1. tasks.md 结构优化

当前：
```markdown
## Phase 1: 基础数据层
### T1: Path 模块数据库表
### T2: Path 入学诊断 API
...

## Phase 2: 核心服务层
### T11: Tutor LLM Router
...
```

优化后（增加交付标记）：
```markdown
## Phase 1: 基础数据层 [可独立交付]
**交付标准**: Path + Radar API 全量测试通过，AC1-AC14 验证完成
**验收检查点**: Phase 1 Review + Phase 1 QA

### T1: Path 模块数据库表
...

## Phase 2: 核心服务层 [依赖 Phase 1]
**交付标准**: Tutor API + Certification API 测试通过，AC15-AC37 验证完成
**依赖检查**: Phase 1 必须已完成 Review + QA
```

### 2. sdd-orchestrator 增强

增加 `--incremental` 标志：
```bash
# 启用增量交付模式
hermes sdd start "AILP V4 重构" --incremental

# 完成当前 Phase 后，询问是否进入下一 Phase
"Phase 1 已完成 Review + QA，是否进入 Phase 2？(y/n)"
```

### 3. Reviewer Agent 增强

增加 Phase 级别检查：
```python
# 在 review-report.md 中增加 Phase 评估
class PhaseReviewReport:
    phase_name: str
    ac_covered: List[str]
    is_phase_complete: bool  # 该 Phase 是否可独立交付
    blockers_for_next_phase: List[str]  # 阻塞下一 Phase 的问题
```

### 4. QA Agent 增强

增加 Phase 回归测试：
```python
# 每完成一个 Phase，运行该 Phase 的全量测试
# 同时运行前面 Phase 的核心测试（确保无回归）
pytest tests/test_path.py tests/test_radar.py  # Phase 1
pytest tests/test_tutor.py  # Phase 2
pytest tests/test_path.py tests/test_radar.py  # Phase 1 回归
```

---

## 五、针对 AILP V4 的具体实施建议

### 立即执行（当前状态）

**Phase 1 已完成**：
- ✅ Path 模块 (T1-T5): 24 测试通过
- ✅ Radar 模块 (T6-T10): 75 测试通过
- ✅ 全量测试: 293 测试通过

**建议操作**：
1. **立即启动 Phase 1 Review**
2. **完成后启动 Phase 1 QA**
3. **QA 通过后，Phase 1 可视为"可交付状态"**
4. **用户确认后，再进入 Phase 2**

### 调整后的 tasks.md

```markdown
## Phase 1: 基础数据层 ✅ [已完成，待 Review/QA]
- T1-T5: Path 模块
- T6-T10: Radar 模块
- **AC 覆盖**: AC1-AC14
- **检查点**: 293 测试通过

## Phase 2: 核心服务层 ⏳ [待启动]
- T11-T15: Tutor 模块
- T16-T19: Certification 模块
- **AC 覆盖**: AC15-AC37
- **依赖**: Phase 1 Review + QA 通过
```

---

## 六、总结

| 问题 | 答案 |
|------|------|
| Phase 1 是否依赖 Phase 2？ | **否**，完全独立 |
| 是否应增量交付？ | **是**，推荐每 Phase 完成后 Review + QA |
| SDD 如何支持？ | Phase 内嵌套 Mini Review/QA，或拆分为多变更 ID |
| 当前建议？ | Phase 1 已完成，立即启动 Review → QA → 验收 → 再进 Phase 2 |
