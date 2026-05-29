# Design Module: Employer — 雇主验证 API

> **变更 ID**: 002-ailp-v4-refactor  
> **负责 AC**: AC45-AC49  
> **版本**: 1.0  

---

## 1. 模块职责

提供雇主验证服务：证书真伪验证、能力数据查询、API 限流、授权机制。

---

## 2. 数据模型

```sql
-- 雇主账户
CREATE TABLE employers (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(128) NOT NULL,
    contact_email VARCHAR(128) UNIQUE NOT NULL,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    rate_limit INT DEFAULT 1000,  -- 每小时请求数
    tier VARCHAR(16) DEFAULT 'basic',  -- basic, premium, enterprise
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 验证授权码
CREATE TABLE verification_codes (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code VARCHAR(32) UNIQUE NOT NULL,  -- 8位字母数字
    permissions JSONB DEFAULT '{"certifications": true, "skill_summary": true, "lab_history": false}',
    expires_at TIMESTAMP NOT NULL,
    used_by INT REFERENCES employers(id),
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API 调用日志
CREATE TABLE employer_api_logs (
    id SERIAL PRIMARY KEY,
    employer_id INT REFERENCES employers(id),
    endpoint VARCHAR(64),
    status_code INT,
    response_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. API 接口

### 3.1 证书扫码验证（AC45）

**URL**: `GET /verify/{cert_number}`  
**Auth**: None (公开访问)

**响应**:
```html
<!-- 渲染HTML页面 -->
证书持有者：张三
认证等级：L2 AI Engineer
有效期：2026-05-01 至 2028-05-01
技能雷达：[雷达图]
实验数量：45个
```

### 3.2 数字签名验证 API（AC46）

**URL**: `POST /api/v1/employer/verify`  
**Auth**: API Key

**请求**:
```json
{
  "cert_number": "AILP-L2-ABCD-1234",
  "signature": "MEUCIQ..."
}
```

**响应**:
```json
{
  "valid": true,
  "cert_data": {
    "holder": "张三",
    "level": "L2",
    "issued_at": "2026-05-01",
    "expires_at": "2028-05-01"
  },
  "audit_summary": {
    "completed_labs": 45,
    "avg_score": 85.5,
    "verification_count": 12
  }
}
```

### 3.3 授权查询（AC49）

**URL**: `POST /api/v1/employer/query`  
**Auth**: API Key + Verification Code

**请求**:
```json
{
  "verification_code": "X7B9K2M1",
  "requested_fields": ["certifications", "skill_radar", "lab_history"]
}
```

**响应**:
```json
{
  "user": {"name": "张三", "username": "zhangsan"},
  "certifications": [...],
  "skill_radar": {...},  -- 如果授权包含
  "lab_history": [...]    -- 如果授权包含
}
```

### 3.4 限流中间件（AC48）

```python
class RateLimitMiddleware:
    """
    每小时限流 1000 次
    """
    async def check_rate_limit(self, api_key: str) -> bool:
        key = f"rate_limit:{api_key}:{datetime.now().hour}"
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, 3600)
        
        limit = await get_employer_limit(api_key)
        if current > limit:
            raise HTTPException(429, "超出配额")
        
        return True
```

---

## 4. AC 覆盖声明

| AC | 实现 |
|:---:|------|
| AC45 | 公开验证页面 |
| AC46 | 数字签名验证 API |
| AC47 | 审计日志记录 |
| AC48 | API 限流中间件 |
| AC49 | 授权码验证机制 |

---

## 5. Tasks

| Task | 内容 | 估时 | AC |
|------|------|:----:|:--:|
| E1 | 创建 employer 相关表 | 20m | - |
| E2 | 实现证书验证页面 | 30m | AC45 |
| E3 | 实现数字签名验证 API | 30m | AC46 |
| E4 | 实现 API 限流 | 30m | AC48 |
| E5 | 实现授权码查询 | 30m | AC49 |
| E6 | 单元测试 | 20m | AC45-AC49 |

**小计**: 6 Tasks, 2.5h
