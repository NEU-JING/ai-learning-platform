# Design Module: Profile — 公开能力主页

> **变更 ID**: 002-ailp-v4-refactor  
> **负责 AC**: AC42-AC44  
> **版本**: 1.0  

---

## 1. 模块职责

管理用户公开能力主页：隐私控制、路径感知展示、CDN 缓存。

---

## 2. 数据模型

```sql
-- 用户公开主页配置
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR(32) UNIQUE NOT NULL,  -- 公开URL: ailp.com/p/{username}
    is_public BOOLEAN DEFAULT FALSE,
    privacy_settings JSONB DEFAULT '{
      "show_skill_radar": true,
      "show_certifications": true,
      "show_lab_history": true,
      "show_ai_tutor_chats": false,
      "allow_employer_view": true
    }',
    custom_title VARCHAR(128),
    bio TEXT,
    avatar_url VARCHAR(256),
    theme VARCHAR(16) DEFAULT 'default',  -- default, minimal, detailed
    view_count INT DEFAULT 0,
    last_synced_at TIMESTAMP,
    UNIQUE(user_id)
);

-- 公开页面缓存
CREATE TABLE profile_cache (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cache_key VARCHAR(64) NOT NULL,
    cached_data JSONB,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, cache_key)
);
```

---

## 3. API 接口

### 3.1 获取公开主页（AC43）

**URL**: `GET /p/{username}` 或 `GET /api/v1/profiles/{username}`  
**Auth**: Optional

**响应**:
```json
{
  "username": "zhangsan",
  "title": "AI工程师",
  "bio": "专注于LLM应用开发",
  "certifications": [
    {"level": "L2", "name": "AI Engineer", "issued_at": "2026-05-01"}
  ],
  "skill_radar": {
    "visible": true,
    "dimensions": [
      {"name": "工程实现", "score": 90, "highlight": true},
      {"name": "研究深度", "score": 45, "highlight": false}
    ],
    "path_type": "ai-engineer"
  },
  "stats": {
    "completed_labs": 45,
    "learning_streak": 30
  },
  "verification_url": "https://ailp.com/verify/AILP-L2-XXXX"
}
```

### 3.2 更新隐私设置（AC44）

**URL**: `PUT /api/v1/profile/privacy`  
**Auth**: Required

**请求**:
```json
{
  "show_skill_radar": false,
  "show_certifications": true
}
```

**响应**:
```json
{
  "settings": {
    "show_skill_radar": false,
    "message": "该用户未公开此维度"
  }
}
```

---

## 4. 缓存策略

```
User Request → CloudFlare CDN (1h) → 命中？→ 返回
                    ↓ 未命中
              Redis (30m) → 命中？→ 返回
                    ↓ 未命中
              DB Query → 写入 Redis → 返回
```

---

## 5. AC 覆盖声明

| AC | 实现 |
|:---:|------|
| AC42 | 混合流程完成标记（与Sandbox协作） |
| AC43 | 路径感知主页展示 |
| AC44 | 隐私控制设置 |

---

## 6. Tasks

| Task | 内容 | 估时 | AC |
|------|------|:----:|:--:|
| PR1 | 创建 user_profiles 表 | 15m | - |
| PR2 | 实现公开主页 API | 30m | AC43 |
| PR3 | 实现隐私控制 | 30m | AC44 |
| PR4 | 实现 CDN + Redis 缓存 | 30m | AC43 |
| PR5 | 单元测试 | 15m | AC42-AC44 |

**小计**: 5 Tasks, 2h
