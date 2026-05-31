# Design Module: Radar — 多维技能雷达

> **变更 ID**: 002-ailp-v4-refactor  
> **负责 AC**: AC7-AC14  
> **版本**: 1.0  

---

## 1. 模块职责

基于用户学习行为数据，计算和维护多维技能分数，提供技能雷达可视化、历史对比、差距分析。

---

## 2. 数据模型

### 2.1 表结构

```sql
-- 技能维度定义
CREATE TABLE skill_dimensions (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(64) NOT NULL,
    name_en VARCHAR(64),
    description TEXT,
    category VARCHAR(16) NOT NULL,  -- hard, soft, specialized
    weight_formula TEXT,  -- 计算公式，如 "avg(lab_scores) * time_decay"
    max_score DECIMAL(5,2) DEFAULT 100.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户技能分数（当前值）
CREATE TABLE user_skill_scores (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dimension_id INT NOT NULL REFERENCES skill_dimensions(id),
    score DECIMAL(5,2) NOT NULL,  -- 0-100
    confidence DECIMAL(3,2) DEFAULT 0.80,  -- 置信度 0-1
    data_points INT DEFAULT 0,  -- 基于多少数据点计算
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, dimension_id)
);

-- 技能分数历史快照（用于对比功能）
CREATE TABLE user_skill_snapshots (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    snapshot_name VARCHAR(64),  -- 用户自定义名称，如 "入职前"
    snapshot_date DATE NOT NULL,
    scores JSONB NOT NULL,  -- {dimension_slug: score, ...}
    path_id INT REFERENCES user_paths(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 技能事件日志（用于重新计算）
CREATE TABLE skill_events (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(32) NOT NULL,  -- lab_completed, project_submitted, etc.
    dimension_id INT REFERENCES skill_dimensions(id),
    score_impact DECIMAL(5,2),  -- 对分数的影响
    metadata JSONB,  -- 关联的lab_id, project_id等
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 目标岗位技能要求
CREATE TABLE job_skill_requirements (
    id SERIAL PRIMARY KEY,
    job_title VARCHAR(64) NOT NULL,
    job_level VARCHAR(16),  -- junior, mid, senior
    required_skills JSONB NOT NULL,  -- {dimension_slug: min_score}
    source VARCHAR(32),  -- jd_analysis, manual
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 索引设计

```sql
CREATE INDEX idx_user_skill_scores_user_id ON user_skill_scores(user_id);
CREATE INDEX idx_user_skill_scores_dimension ON user_skill_scores(dimension_id);
CREATE INDEX idx_user_skill_snapshots_user_id ON user_skill_snapshots(user_id);
CREATE INDEX idx_skill_events_user_id ON skill_events(user_id, created_at);
```

---

## 3. API 接口

### 3.1 获取技能雷达数据（AC7, AC11）

**URL**: `GET /api/v1/radar`  
**Auth**: Required

**响应**: 200 OK
```json
{
  "user_id": 123,
  "dimensions": [
    {
      "slug": "coding_thinking",
      "name": "编程思维",
      "category": "hard",
      "score": 85.5,
      "max_score": 100,
      "percentile": 75,  -- 超过75%的用户
      "confidence": 0.92,
      "data_points": 50
    },
    {
      "slug": "algorithm_understanding",
      "name": "算法理解",
      "category": "hard",
      "score": 72.0,
      "max_score": 100,
      "percentile": 60,
      "confidence": 0.85,
      "data_points": 35
    }
    -- 共10维
  ],
  "overall": {
    "average_score": 78.5,
    "top_dimension": "coding_thinking",
    "weak_dimension": "algorithm_understanding"
  },
  "last_updated": "2026-05-28T10:30:00Z"
}
```

### 3.2 获取路径特化雷达（AC8）

**URL**: `GET /api/v1/radar?path_type=ai-engineer`  
**Auth**: Required

**响应**: 200 OK
```json
{
  "path_type": "ai-engineer",
  "dimensions": [
    {"slug": "coding_thinking", "score": 85.5, "highlight": true},
    {"slug": "system_design", "score": 70.0, "highlight": true},  -- AI工程师突出显示
    {"slug": "research_depth", "score": 45.0, "highlight": false, "dimmed": true}  -- 研究深度淡化
  ],
  "highlighted_dimensions": ["coding_thinking", "system_design", "engineering_practice"],
  "specialization_note": "AI工程师路径侧重工程实现维度"
}
```

### 3.3 获取历史对比（AC12）

**URL**: `GET /api/v1/radar/compare?snapshot_id=456`  
**Auth**: Required

**响应**: 200 OK
```json
{
  "current": {"coding_thinking": 85.5, "algorithm_understanding": 72.0, ...},
  "snapshot": {"coding_thinking": 70.0, "algorithm_understanding": 75.0, ...},
  "comparison": [
    {
      "dimension": "coding_thinking",
      "current": 85.5,
      "snapshot": 70.0,
      "change": 15.5,
      "trend": "up"
    },
    {
      "dimension": "algorithm_understanding",
      "current": 72.0,
      "snapshot": 75.0,
      "change": -3.0,
      "trend": "down"
    }
  ],
  "assessment": "工程能力提升，理论基础需加强",
  "snapshot_info": {
    "name": "入职前",
    "date": "2026-02-28"
  }
}
```

### 3.4 获取目标差距分析（AC13）

**URL**: `GET /api/v1/radar/gap-analysis?target_job=ai-engineer`  
**Auth**: Required

**响应**: 200 OK
```json
{
  "target_job": "AI工程师",
  "target_level": "mid",
  "gaps": [
    {
      "dimension": "system_design",
      "current_score": 60.0,
      "required_score": 75.0,
      "gap": 15.0,
      "priority": "high",
      "recommended_courses": [
        {"id": 45, "name": "系统设计基础", "relevance": 0.95},
        {"id": 46, "name": "微服务架构实践", "relevance": 0.85}
      ]
    }
  ],
  "overall_readiness": 65,  -- 整体准备度%
  "estimated_gap_days": 30  -- 预计弥补差距需要的天数
}
```

### 3.5 创建快照（AC12）

**URL**: `POST /api/v1/radar/snapshots`  
**Auth**: Required

**请求**:
```json
{
  "name": "入职前",
  "path_id": 789  -- 可选
}
```

**响应**: 201 Created
```json
{
  "snapshot_id": 456,
  "name": "入职前",
  "snapshot_date": "2026-05-28",
  "scores": {...}
}
```

---

## 4. 核心算法

### 4.1 时间衰减权重算法（AC10）

```python
def calculate_time_decay_weight(event_date: datetime, half_life_days: int = 90) -> float:
    """
    AC10: 时间衰减计算，默认90天半衰期
    公式: weight = 0.5 ^ (days_passed / half_life_days)
    """
    days_passed = (datetime.now() - event_date).days
    weight = 0.5 ** (days_passed / half_life_days)
    return max(weight, 0.1)  -- 最小权重10%


def calculate_dimension_score(user_id: int, dimension_id: int) -> float:
    """
    计算某维度的加权平均分
    """
    events = db.query(SkillEvent).filter_by(
        user_id=user_id, 
        dimension_id=dimension_id
    ).order_by(desc(SkillEvent.created_at)).limit(100).all()
    
    if not events:
        return 0.0
    
    weighted_sum = 0.0
    weight_sum = 0.0
    
    for event in events:
        weight = calculate_time_decay_weight(event.created_at)
        weighted_sum += event.score_impact * weight
        weight_sum += weight
    
    return weighted_sum / weight_sum if weight_sum > 0 else 0.0
```

### 4.2 事件触发更新（AC9）

```python
async def update_skill_from_lab(user_id: int, lab_result: LabResult):
    """
    AC9: 用户完成实验后更新技能分数
    """
    # 根据实验类型确定影响的维度
    dimension_mapping = {
        'python_basics': ['coding_thinking'],
        'ml_algorithm': ['algorithm_understanding', 'coding_thinking'],
        'llm_prompt': ['ai_collaboration', 'prompt_engineering'],
        'system_design': ['system_design', 'engineering_practice']
    }
    
    affected_dimensions = dimension_mapping.get(lab_result.lab_type, [])
    
    for dim_slug in affected_dimensions:
        dimension = await get_dimension_by_slug(dim_slug)
        
        # 计算本次实验对分数的影响
        score_impact = lab_result.score * 0.1  -- 每次实验最多影响10%
        
        # 记录事件
        event = SkillEvent(
            user_id=user_id,
            event_type='lab_completed',
            dimension_id=dimension.id,
            score_impact=score_impact,
            metadata={'lab_id': lab_result.lab_id, 'score': lab_result.score}
        )
        db.add(event)
        
        # 重新计算该维度分数
        new_score = calculate_dimension_score(user_id, dimension.id)
        await update_user_skill_score(user_id, dimension.id, new_score)
    
    # 清除缓存
    await redis.delete(f"radar:{user_id}")
```

### 4.3 百分位计算

```python
def calculate_percentile(user_id: int, dimension_id: int, score: float) -> int:
    """
    计算用户在某维度的百分位（超过多少%的用户）
    """
    # 使用近似算法避免全表扫描
    total_users = get_cached_user_count()
    higher_scores = db.query(func.count(UserSkillScores.id)).filter(
        UserSkillScores.dimension_id == dimension_id,
        UserSkillScores.score > score
    ).scalar()
    
    percentile = ((total_users - higher_scores) / total_users) * 100
    return int(percentile)
```

---

## 5. 配置项

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|---------|-------|------|
| 时间半衰期 | `RADAR_TIME_HALFLIFE_DAYS` | 90 | 技能分数时间衰减半衰期 |
| 最小权重 | `RADAR_MIN_WEIGHT` | 0.1 | 时间衰减最小权重 |
| 缓存 TTL | `RADAR_CACHE_TTL` | 3600 | Redis 缓存秒数 |
| 事件保留 | `RADAR_EVENT_RETENTION_DAYS` | 365 | 技能事件保留天数 |
| 最大维度数 | `RADAR_MAX_DIMENSIONS` | 10 | 技能雷达最大维度数 |

---

## 6. AC 覆盖声明

| AC | 实现位置 | 验证方式 |
|:---:|---------|---------|
| AC7 | `GET /api/v1/radar` + 10维模型 | API测试：返回10维分数 |
| AC8 | `GET /api/v1/radar?path_type=` | API测试：AI工程师突出显示工程维度 |
| AC9 | `update_skill_from_lab()` | 集成测试：完成实验后分数更新 |
| AC10 | `calculate_time_decay_weight()` | 单元测试：旧数据权重降低 |
| AC11 | `GET /api/v1/radar` 返回格式 | API测试：包含percentile和confidence |
| AC12 | `GET /api/v1/radar/compare` + `POST /snapshots` | API测试：对比数据正确 |
| AC13 | `GET /api/v1/radar/gap-analysis` | API测试：返回差距和推荐课程 |
| AC14 | `GET /api/v1/radar?path_type=` 权重调整 | API测试：不同路径维度权重不同 |

---

## 7. Tasks 拆分（Radar 模块）

| Task | 内容 | 估时 | AC 覆盖 |
|------|------|:----:|:-------:|
| R1 | 创建 skill_dimensions 表 + 10维种子数据 | 30m | AC7 |
| R2 | 创建 user_skill_scores, skill_events 表 | 30m | AC9, AC10 |
| R3 | 创建 user_skill_snapshots 表 | 15m | AC12 |
| R4 | 实现雷达数据查询 API (GET /radar) | 30m | AC7, AC11 |
| R5 | 实现路径特化雷达 API | 30m | AC8, AC14 |
| R6 | 实现技能更新算法（时间衰减） | 45m | AC9, AC10 |
| R7 | 实现历史对比 API + 快照功能 | 45m | AC12 |
| R8 | 实现差距分析 API | 30m | AC13 |
| R9 | Radar 模块单元测试 | 30m | AC7-AC14 |

**小计**: 9 Tasks, 5h 15m
