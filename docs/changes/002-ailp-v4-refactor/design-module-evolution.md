# Design Module: Evolution — 课程演进+JD采集

> **变更 ID**: 002-ailp-v4-refactor  
> **负责 AC**: AC22-AC29  
> **版本**: 1.0  

---

## 1. 模块职责

多渠道采集 JD 数据，分析技能供需趋势，驱动课程内容三层（L1/L2/L3）差异化更新。

---

## 2. 数据模型

```sql
-- JD 数据源配置
CREATE TABLE jd_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL,  -- boss_zhipin, lagou, linkedin
    source_type VARCHAR(16),  -- api, scraper
    config JSONB,  -- API key, endpoint等
    is_active BOOLEAN DEFAULT TRUE,
    last_crawl_at TIMESTAMP
);

-- 原始 JD 数据
CREATE TABLE job_descriptions (
    id SERIAL PRIMARY KEY,
    source_id INT REFERENCES jd_sources(id),
    external_id VARCHAR(64),  -- 源系统的ID
    title VARCHAR(128),
    company VARCHAR(64),
    location VARCHAR(64),
    description TEXT,
    requirements TEXT,
    extracted_skills JSONB,  -- ["Python", "PyTorch", "LangChain"]
    salary_range VARCHAR(32),
    post_date DATE,
    crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 技能趋势统计
CREATE TABLE market_skill_trends (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(32) NOT NULL,
    date DATE NOT NULL,
    mention_count INT DEFAULT 0,
    growth_rate DECIMAL(5,2),  -- 环比增长率
    demand_level VARCHAR(8),  -- high, medium, low
    UNIQUE(skill_name, date)
);

-- 课程更新建议
CREATE TABLE content_update_suggestions (
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(id),
    suggestion_type VARCHAR(16),  -- l3_quick, l2_method, l1_principle
    trigger_source VARCHAR(32),  -- jd_trend, student_gap, tech_radar
    priority VARCHAR(8),  -- p0, p1, p2
    description TEXT,
    evidence JSONB,  -- 支撑数据
    status VARCHAR(16) DEFAULT 'pending',  -- pending, approved, rejected, done
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. API 接口

### 3.1 获取技能趋势（AC23）

**URL**: `GET /api/v1/evolution/skill-trends`  
**Auth**: Admin

**响应**:
```json
{
  "trends": [
    {
      "skill": "LangChain",
      "current_month": 450,
      "last_month": 300,
      "growth_rate": 50.0,
      "demand_level": "high",
      "suggestion": "建议更新Phase 5课程内容"
    }
  ],
  "analysis_date": "2026-05-28"
}
```

### 3.2 获取更新建议（AC24, AC28）

**URL**: `GET /api/v1/evolution/update-suggestions`  
**Auth**: Admin

**响应**:
```json
{
  "suggestions": [
    {
      "id": 123,
      "course_name": "Transformer架构",
      "type": "l3_quick",
      "priority": "p0",
      "trigger": "jd_trend",
      "description": "检测到T5相关内容过时，建议2周内更新",
      "evidence": {
        "jd_mentions": {"old": 50, "new": 5},
        "student_feedback": ["内容太旧"]
      }
    }
  ]
}
```

---

## 4. 核心算法

### JD 采集定时任务

```python
async def crawl_jd_daily():
    """
    AC22: 每日采集JD
    """
    sources = await get_active_jd_sources()
    
    for source in sources:
        try:
            if source.type == 'api':
                jobs = await fetch_from_api(source)
            else:
                jobs = await scrape_from_web(source)
            
            for job in jobs:
                skills = extract_skills_with_nlp(job.description)
                await save_job_description(job, skills)
        
        except Exception as e:
            logger.error(f"Source {source.name} failed: {e}")
    
    # 更新趋势统计
    await update_skill_trends()
```

### 三层更新策略

| 层级 | 周期 | 触发条件 | AC |
|-----|-----|---------|----|
| L3 工具层 | 2周 | 新工具发布、重大更新 | AC25 |
| L2 方法层 | 2月 | 学术论文、最佳实践变化 | AC26 |
| L1 原理层 | 6月 | 原理验证成熟 | AC27 |

---

## 5. AC 覆盖声明

| AC | 实现 |
|:---:|------|
| AC22 | 每日定时任务 `crawl_jd_daily()` |
| AC23 | `GET /api/v1/evolution/skill-trends` |
| AC24 | `GET /api/v1/evolution/update-suggestions` |
| AC25 | L3 更新流程：2周检查工具层 |
| AC26 | L2 更新流程：2月检查方法层 |
| AC27 | L1 更新流程：6月审慎验证 |
| AC28 | aggregate 学生数据生成缺口建议 |
| AC29 | 多渠道信号整合算法 |

---

## 6. Tasks

| Task | 内容 | 估时 | AC |
|------|------|:----:|:--:|
| E1 | 创建 jd_sources, job_descriptions 表 | 30m | AC22 |
| E2 | 实现 JD 采集定时任务 | 45m | AC22 |
| E3 | 实现技能提取 NLP | 30m | AC23 |
| E4 | 实现技能趋势分析 | 30m | AC23, AC29 |
| E5 | 实现更新建议生成 | 30m | AC24, AC28 |
| E6 | 实现三层更新策略 | 30m | AC25-AC27 |
| E7 | 单元测试 | 15m | AC22-AC29 |

**小计**: 7 Tasks, 3.5h
