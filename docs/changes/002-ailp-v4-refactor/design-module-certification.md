# Design Module: Certification — 四级认证

> **变更 ID**: 002-ailp-v4-refactor  
> **负责 AC**: AC30-AC37  
> **版本**: 1.0  

---

## 1. 模块职责

实现 L1-L4 四级认证体系：自动评定、项目评审、场景挑战、专家审核、证书签名。

---

## 2. 数据模型

```sql
-- 认证定义
CREATE TABLE certification_levels (
    id SERIAL PRIMARY KEY,
    level VARCHAR(8) UNIQUE NOT NULL,  -- L1, L2, L3, L4
    name VARCHAR(64) NOT NULL,
    description TEXT,
    requirements JSONB,  -- 认证条件
    validity_months INT DEFAULT 24
);

-- 用户认证申请
CREATE TABLE certification_applications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    level VARCHAR(8) NOT NULL,
    status VARCHAR(16) DEFAULT 'pending',  -- pending, approved, rejected, expired
    application_data JSONB,  -- 申请材料
    reviewed_by INT REFERENCES users(id),  -- 审核人
    review_notes TEXT,
    approved_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 证书
CREATE TABLE certificates (
    id SERIAL PRIMARY KEY,
    cert_number VARCHAR(32) UNIQUE NOT NULL,  -- AILP-L2-XXXX-XXXX
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    application_id INT REFERENCES certification_applications(id),
    level VARCHAR(8) NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    signature TEXT,  -- ECDSA 签名
    revoked BOOLEAN DEFAULT FALSE
);

-- 项目提交（L2认证）
CREATE TABLE capstone_submissions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_name VARCHAR(128),
    description TEXT,
    repository_url VARCHAR(256),
    demo_url VARCHAR(256),
    documentation TEXT,
    ai_review_score DECIMAL(5,2),  -- AI初审分数
    human_review_score DECIMAL(5,2),
    status VARCHAR(16) DEFAULT 'pending',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 审计日志
CREATE TABLE certification_audit_logs (
    id SERIAL PRIMARY KEY,
    cert_id INT REFERENCES certificates(id),
    event_type VARCHAR(32),  -- issued, renewed, revoked, verified
    event_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. API 接口

### 3.1 提交认证申请（AC30-AC33）

**URL**: `POST /api/v1/certifications/apply`  
**Auth**: Required

**请求**:
```json
{
  "level": "L2",
  "capstone_id": 123  -- L2需要
}
```

**响应**:
```json
{
  "application_id": 456,
  "level": "L2",
  "status": "pending",
  "requirements_check": {
    "required_courses": "12/12 completed",
    "avg_score": "85.5 >= 85",
    "passed": true
  },
  "next_steps": ["等待人工审核"],
  "estimated_review_days": 3
}
```

### 3.2 L1 自动评定

```python
async def auto_evaluate_l1(user_id: int) -> CertificationResult:
    """
    AC30: L1自动评定
    """
    # 检查必修课程
    required_courses = await get_completed_courses(user_id, required_only=True)
    if len(required_courses) < 12:
        return CertificationResult(passed=False, reason="必修课程未完成")
    
    # 检查平均分
    avg_score = await calculate_avg_lab_score(user_id)
    if avg_score < 85:
        return CertificationResult(passed=False, reason="实验平均分不足85")
    
    # 自动生成证书
    cert = await generate_certificate(user_id, "L1")
    return CertificationResult(passed=True, cert_number=cert.number)
```

### 3.3 获取证书（AC37）

**URL**: `GET /api/v1/certificates/{cert_number}`  
**Auth**: Optional

**响应**:
```json
{
  "cert_number": "AILP-L2-ABCD-1234",
  "holder": {"name": "张三", "username": "zhangsan"},
  "level": "L2",
  "issued_at": "2026-05-01",
  "expires_at": "2028-05-01",
  "signature": "MEUCIQ...",  -- ECDSA 签名
  "verification_url": "https://ailp.com/verify/AILP-L2-ABCD-1234"
}
```

### 3.4 证书验证

```python
def verify_certificate(cert_number: str, signature: str) -> bool:
    """
    AC37: 验证证书真伪
    使用 ECDSA with SHA256
    """
    cert = db.query(Certificate).filter_by(cert_number=cert_number).first()
    if not cert or cert.revoked:
        return False
    
    # 构造签名数据
    message = f"{cert_number}|{cert.user_id}|{cert.level}|{cert.issued_at}|{cert.expires_at}"
    
    # 验证签名
    public_key = load_public_key_from_env()
    try:
        public_key.verify(
            base64.b64decode(signature),
            message.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except InvalidSignature:
        return False
```

### 3.5 续期申请（AC35）

**URL**: `POST /api/v1/certifications/{cert_id}/renew`  
**Auth**: Required

---

## 4. AC 覆盖声明

| AC | 实现 |
|:---:|------|
| AC30 | `auto_evaluate_l1()` |
| AC31 | L2 项目提交流程 + AI初审 + 人工抽检 |
| AC32 | L3 场景挑战 + 专家评审 |
| AC33 | L4 专家委员会评审 |
| AC34 | 定时任务检查过期，发送提醒 |
| AC35 | `POST /renew` 续期流程 |
| AC36 | 路径特化评审标准 |
| AC37 | ECDSA 签名 + 验证接口 |

---

## 5. Tasks

| Task | 内容 | 估时 | AC |
|------|------|:----:|:--:|
| C1 | 创建认证相关表 | 30m | - |
| C2 | 实现 L1 自动评定 | 30m | AC30 |
| C3 | 实现 L2 项目提交流程 | 45m | AC31 |
| C4 | 实现 L3/L4 专家审核 | 30m | AC32-AC33 |
| C5 | 实现证书 ECDSA 签名 | 45m | AC37 |
| C6 | 实现证书验证 API | 30m | AC37 |
| C7 | 实现过期提醒 + 续期 | 30m | AC34-AC35 |
| C8 | 单元测试 | 30m | AC30-AC37 |

**小计**: 8 Tasks, 4.5h
