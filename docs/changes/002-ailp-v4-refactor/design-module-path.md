# Design Module: Path — 目标导向学习路径

> **变更 ID**: 002-ailp-v4-refactor  
> **负责 AC**: AC1-AC6  
> **版本**: 1.0  

---

## 1. 模块职责

管理用户学习路径的生命周期：路径模板定义、入学诊断、个性化路径生成、进度追踪。

---

## 2. 数据模型

### 2.1 表结构

```sql
-- 路径模板（系统预定义）
CREATE TABLE path_templates (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(32) UNIQUE NOT NULL,  -- ai-researcher, ai-engineer, ai-applier, ai-manager
    name VARCHAR(64) NOT NULL,
    description TEXT,
    duration_weeks INT NOT NULL,  -- 20, 14, 8, 6
    target_role VARCHAR(32) NOT NULL,  -- AI专家, AI工程师, AI应用者, AI管理者
    required_courses JSONB NOT NULL,  -- [course_id1, course_id2, ...]
    elective_courses JSONB,  -- 可选课程
    capstone_count INT DEFAULT 2,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户路径实例
CREATE TABLE user_paths (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_id INT REFERENCES path_templates(id),
    status VARCHAR(16) DEFAULT 'active',  -- active, completed, paused, switched
    start_date DATE,
    target_end_date DATE,  -- 预计完成日期
    actual_end_date DATE,
    mode VARCHAR(16) DEFAULT 'standard',  -- standard, fast_track
    diagnosis_result JSONB,  -- 入学诊断结果 {skip_phase1: true, start_from: 2}
    progress_percent DECIMAL(5,2) DEFAULT 0.00,
    current_milestone INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, status) WHERE status = 'active'
);

-- 路径课程关联（记录用户在路径中的课程状态）
CREATE TABLE path_courses (
    id SERIAL PRIMARY KEY,
    path_id INT NOT NULL REFERENCES user_paths(id) ON DELETE CASCADE,
    course_id INT NOT NULL REFERENCES courses(id),
    sequence_order INT NOT NULL,  -- 在路径中的顺序
    status VARCHAR(16) DEFAULT 'pending',  -- pending, in_progress, completed, skipped
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    UNIQUE(path_id, course_id)
);

-- 里程碑定义
CREATE TABLE path_milestones (
    id SERIAL PRIMARY KEY,
    template_id INT REFERENCES path_templates(id),
    name VARCHAR(64) NOT NULL,
    description TEXT,
    sequence_order INT NOT NULL,
    required_courses JSONB,  -- 完成这些课程即达成里程碑
    reward_badge VARCHAR(32)
);

-- 能力缺口诊断记录
CREATE TABLE skill_gap_diagnoses (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    path_id INT REFERENCES user_paths(id),
    weak_dimensions JSONB,  -- ["algorithm_understanding", "linear_algebra"]
    recommended_courses JSONB,  -- 推荐的补强课程
    diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 索引设计

```sql
CREATE INDEX idx_user_paths_user_id ON user_paths(user_id);
CREATE INDEX idx_user_paths_status ON user_paths(status) WHERE status = 'active';
CREATE INDEX idx_path_courses_path_id ON path_courses(path_id);
CREATE INDEX idx_path_courses_status ON path_courses(status);
```

---

## 3. API 接口

### 3.1 获取路径模板列表

**URL**: `GET /api/v1/paths/templates`  
**Auth**: 可选（游客可见）

**响应**: 200 OK
```json
{
  "templates": [
    {
      "slug": "ai-engineer",
      "name": "AI工程师路径",
      "description": "侧重工程实现，14周完成",
      "duration_weeks": 14,
      "target_role": "AI工程师",
      "required_courses_count": 12,
      "elective_courses_count": 3,
      "capstone_count": 2
    }
  ]
}
```

### 3.2 入学诊断提交（AC1, AC2）

**URL**: `POST /api/v1/paths/diagnosis`  
**Auth**: Required

**请求**:
```json
{
  "target_role": "ai-engineer",
  "experience_years": 3,
  "python_level": "intermediate",
  "math_level": "beginner",
  "current_job": "Java开发",
  "time_commitment": "part_time",  // full_time, part_time
  "goal_timeline": "3_months"  // 6_months, 1_year
}
```

**响应**: 200 OK
```json
{
  "recommended_template": "ai-engineer",
  "recommended_mode": "fast_track",
  "diagnosis": {
    "can_skip_phase1": true,
    "start_from": 2,
    "weak_areas": ["linear_algebra"],
    "reasoning": "您有3年Python经验，可直接从Phase 2开始，但建议补充线性代数基础"
  },
  "estimated_duration_weeks": 8,
  "preview_path": {
    "courses": [...],
    "milestones": [...]
  }
}
```

**错误码**:
- 400: 无效的 target_role
- 409: 用户已有 active 路径

### 3.3 创建用户路径（AC1, AC5）

**URL**: `POST /api/v1/paths`  
**Auth**: Required

**请求**:
```json
{
  "template_slug": "ai-engineer",
  "mode": "fast_track",  // standard, fast_track
  "diagnosis_id": 123  // 可选，关联诊断结果
}
```

**响应**: 201 Created
```json
{
  "path_id": 456,
  "template": {...},
  "status": "active",
  "start_date": "2026-05-28",
  "target_end_date": "2026-07-23",
  "progress": {
    "percent": 0,
    "completed_courses": 0,
    "total_courses": 15
  },
  "next_course": {...}
}
```

### 3.4 获取路径进度（AC3）

**URL**: `GET /api/v1/paths/{path_id}/progress`  
**Auth**: Required

**响应**: 200 OK
```json
{
  "path_id": 456,
  "status": "active",
  "progress": {
    "percent": 20.0,
    "completed_courses": 3,
    "in_progress_courses": 1,
    "total_courses": 15
  },
  "milestones": [
    {"order": 1, "name": "Python基础", "status": "completed", "completed_at": "2026-05-30"},
    {"order": 2, "name": "数学基础", "status": "in_progress", "progress": 80}
  ],
  "estimated_remaining_days": 42,
  "ahead_behind_schedule": "ahead"  // ahead, on_track, behind
}
```

### 3.5 获取能力缺口诊断（AC4）

**URL**: `GET /api/v1/paths/{path_id}/gaps`  
**Auth**: Required

**响应**: 200 OK
```json
{
  "path_id": 456,
  "gaps": [
    {
      "dimension": "algorithm_understanding",
      "current_score": 55,
      "target_score": 70,
      "gap": 15,
      "recommended_courses": [
        {"id": 23, "name": "机器学习算法基础", "priority": "high"}
      ]
    }
  ],
  "overall_assessment": "数学基础薄弱，建议补充线性代数课程",
  "last_diagnosed_at": "2026-06-01"
}
```

### 3.6 获取路径可视化数据（AC6）

**URL**: `GET /api/v1/paths/{path_id}/visualization`  
**Auth**: Required

**响应**: 200 OK
```json
{
  "path_id": 456,
  "nodes": [
    {
      "id": "course_1",
      "type": "course",
      "name": "Python基础",
      "status": "completed",
      "dependencies": [],
      "position": {"x": 0, "y": 0}
    },
    {
      "id": "milestone_1",
      "type": "milestone",
      "name": "编程基础达成",
      "status": "completed"
    }
  ],
  "edges": [
    {"from": "course_1", "to": "course_2"},
    {"from": "course_2", "to": "milestone_1"}
  ],
  "milestones": [...]
}
```

---

## 4. 核心算法

### 4.1 入学诊断算法

```python
def diagnose_user_eligibility(diagnosis_data: dict) -> DiagnosisResult:
    """
    AC1, AC2: 根据用户背景推荐路径和起点
    """
    python_level = diagnosis_data['python_level']
    math_level = diagnosis_data['math_level']
    experience_years = diagnosis_data['experience_years']
    
    can_skip_phase1 = python_level in ['intermediate', 'advanced'] and experience_years >= 2
    
    weak_areas = []
    if math_level == 'beginner':
        weak_areas.append('linear_algebra')
    
    mode = 'fast_track' if diagnosis_data.get('goal_timeline') == '3_months' else 'standard'
    
    return DiagnosisResult(
        can_skip_phase1=can_skip_phase1,
        start_from=2 if can_skip_phase1 else 1,
        weak_areas=weak_areas,
        recommended_mode=mode
    )
```

### 4.2 进度计算算法

```python
def calculate_path_progress(path_id: int) -> PathProgress:
    """
    AC3: 计算路径整体进度
    """
    courses = db.query(PathCourse).filter_by(path_id=path_id).all()
    
    total = len(courses)
    completed = sum(1 for c in courses if c.status == 'completed')
    in_progress = sum(1 for c in courses if c.status == 'in_progress')
    
    # 已完成的按100%，进行中的按50%
    percent = ((completed * 1.0 + in_progress * 0.5) / total) * 100
    
    return PathProgress(
        percent=round(percent, 2),
        completed_courses=completed,
        in_progress_courses=in_progress,
        total_courses=total
    )
```

### 4.3 能力缺口检测算法

```python
def detect_skill_gaps(user_id: int, path_id: int) -> List[SkillGap]:
    """
    AC4: 基于实验通过率检测能力缺口
    """
    # 获取用户最近20个实验结果
    recent_labs = get_recent_lab_results(user_id, limit=20)
    
    # 按维度聚合
    dimension_scores = {}
    for lab in recent_labs:
        for dim in lab.dimensions:
            if dim.name not in dimension_scores:
                dimension_scores[dim.name] = []
            dimension_scores[dim.name].append(lab.score)
    
    gaps = []
    for dim_name, scores in dimension_scores.items():
        avg_score = sum(scores) / len(scores)
        if avg_score < 60:  # 低于60%视为薄弱
            gaps.append(SkillGap(
                dimension=dim_name,
                current_score=avg_score,
                target_score=70,
                recommended_courses=get_remedial_courses(dim_name)
            ))
    
    return gaps
```

---

## 5. 配置项

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|---------|-------|------|
| 路径最大并发数 | `MAX_ACTIVE_PATHS_PER_USER` | 1 | 用户同时只能有1个active路径 |
| Fast Track 最小周数 | `FAST_TRACK_MIN_WEEKS` | 6 | Fast Track模式最少周数 |
| 诊断有效期 | `DIAGNOSIS_VALID_DAYS` | 7 | 入学诊断结果有效期 |
| 进度缓存 TTL | `PROGRESS_CACHE_TTL` | 300 | 进度数据Redis缓存秒数 |

---

## 6. AC 覆盖声明

| AC | 实现位置 | 验证方式 |
|:---:|---------|---------|
| AC1 | `POST /api/v1/paths/diagnosis` + `POST /api/v1/paths` | 单元测试：不同角色生成不同路径 |
| AC2 | 诊断算法中的 `can_skip_phase1` 逻辑 | 单元测试：有经验用户跳过Phase 1 |
| AC3 | `GET /api/v1/paths/{id}/progress` | 集成测试：完成课程后进度更新 |
| AC4 | `GET /api/v1/paths/{id}/gaps` + 缺口检测算法 | 单元测试：低通过率触发缺口提示 |
| AC5 | 路径创建时的 `mode` 参数 | 单元测试：fast_track模式生成8周路径 |
| AC6 | `GET /api/v1/paths/{id}/visualization` | API测试：返回nodes和edges |

---

## 7. Tasks 拆分（Path 模块）

| Task | 内容 | 估时 | AC 覆盖 |
|------|------|:----:|:-------:|
| P1 | 创建 path_templates 表 + 种子数据 | 30m | AC1 |
| P2 | 创建 user_paths, path_courses, path_milestones 表 | 30m | AC1, AC3 |
| P3 | 实现入学诊断 API (POST /diagnosis) | 45m | AC1, AC2 |
| P4 | 实现路径创建 API (POST /paths) | 30m | AC1, AC5 |
| P5 | 实现进度查询 API (GET /progress) | 30m | AC3 |
| P6 | 实现能力缺口诊断 API (GET /gaps) | 45m | AC4 |
| P7 | 实现可视化数据 API (GET /visualization) | 30m | AC6 |
| P8 | Path 模块单元测试 | 30m | AC1-AC6 |

**小计**: 6 Tasks, 4.5h
