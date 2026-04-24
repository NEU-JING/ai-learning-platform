# AI学习平台 API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: Bearer Token (JWT)
- **Content-Type**: `application/json`

---

## 认证

### 登录

```http
POST /auth/login
```

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**错误响应**:
- `401`: 邮箱或密码错误
- `422`: 请求格式错误

---

### 注册

```http
POST /auth/register
```

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "张三"
}
```

**响应**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "张三",
  "created_at": "2026-04-24T10:30:00Z"
}
```

---

### 刷新Token

```http
POST /auth/refresh
```

**请求头**:
```
Authorization: Bearer {refresh_token}
```

---

## 课程

### 获取课程列表

```http
GET /courses
```

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| level | string | 筛选级别: beginner, intermediate, advanced, expert |
| search | string | 搜索关键词 |
| page | int | 页码，默认1 |
| page_size | int | 每页数量，默认20 |

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Python基础",
      "description": "从零开始学习Python编程",
      "level": "beginner",
      "duration_hours": 20,
      "chapter_count": 8,
      "thumbnail_url": "/assets/course-1.png"
    }
  ],
  "total": 4,
  "page": 1,
  "page_size": 20
}
```

---

### 获取课程详情

```http
GET /courses/{course_id}
```

**响应**:
```json
{
  "id": 1,
  "title": "Python基础",
  "description": "从零开始学习Python编程",
  "level": "beginner",
  "duration_hours": 20,
  "chapters": [
    {
      "id": 1,
      "title": "第1章：Python简介",
      "order": 1,
      "has_lab": true
    }
  ],
  "learning_path": {
    "prerequisites": [],
    "next_courses": [2, 3]
  }
}
```

---

### 获取章节内容

```http
GET /courses/{course_id}/chapters/{chapter_id}
```

**响应**:
```json
{
  "id": 1,
  "title": "第1章：Python简介",
  "content": "...",
  "lab": {
    "id": 1,
    "title": "Hello World实验",
    "instructions": "..."
  }
}
```

---

## 实验

### 获取实验详情

```http
GET /labs/{lab_id}
```

**响应**:
```json
{
  "id": 1,
  "title": "Hello World实验",
  "instructions": "编写一个打印Hello World的程序",
  "starter_code": "# 在这里编写你的代码\n",
  "test_cases": [
    {
      "id": 1,
      "input": "",
      "expected_output": "Hello World"
    }
  ]
}
```

---

### 执行代码

```http
POST /labs/execute
```

**请求体**:
```json
{
  "code": "print('Hello World')",
  "lab_id": 1
}
```

**响应**:
```json
{
  "success": true,
  "output": "Hello World\n",
  "execution_time": 0.05,
  "memory_used": "2.5MB",
  "test_results": [
    {
      "test_id": 1,
      "passed": true,
      "output": "Hello World",
      "expected": "Hello World"
    }
  ],
  "grade": {
    "score": 100,
    "test_score": 80,
    "style_score": 20,
    "feedback": ["代码运行正确！"]
  }
}
```

**错误响应**:
- `400`: 代码安全检查失败
- `429`: 执行次数超限
- `500`: 执行环境错误

---

### 提交实验

```http
POST /courses/labs/{lab_id}/submit
```

**请求体**:
```json
{
  "code": "print('Hello World')"
}
```

**响应**:
```json
{
  "submission_id": 123,
  "grade": {
    "score": 100,
    "test_score": 80,
    "style_score": 20
  },
  "status": "completed",
  "completed_at": "2026-04-24T10:30:00Z"
}
```

---

## 学习进度

### 获取学习进度

```http
GET /progress
```

**响应**:
```json
{
  "total_completed": 5,
  "total_chapters": 20,
  "progress_percentage": 25,
  "courses": [
    {
      "course_id": 1,
      "course_title": "Python基础",
      "completed_chapters": 3,
      "total_chapters": 8,
      "progress_percentage": 37.5
    }
  ],
  "recent_activity": [
    {
      "chapter_id": 5,
      "chapter_title": "第5章：函数",
      "status": "completed",
      "completed_at": "2026-04-24T10:30:00Z"
    }
  ]
}
```

---

### 更新学习进度

```http
PUT /progress/{chapter_id}
```

**请求体**:
```json
{
  "status": "completed"
}
```

**状态枚举**: `not_started`, `in_progress`, `completed`

---

## 讨论区

### 获取课程讨论列表

```http
GET /courses/{course_id}/discussions
```

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| sort | string | 排序: newest, hottest, pinned |
| page | int | 页码 |
| page_size | int | 每页数量 |

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Python变量作用域问题",
      "content": "关于全局变量的使用...",
      "author": {
        "id": 1,
        "name": "张三"
      },
      "likes_count": 10,
      "comments_count": 5,
      "is_pinned": false,
      "created_at": "2026-04-24T10:30:00Z"
    }
  ],
  "total": 50
}
```

---

### 创建讨论

```http
POST /courses/{course_id}/discussions
```

**请求体**:
```json
{
  "title": "问题标题",
  "content": "详细描述"
}
```

---

### 发表评论

```http
POST /discussions/{discussion_id}/comments
```

**请求体**:
```json
{
  "content": "评论内容",
  "parent_id": null  // 回复评论时填写父评论ID
}
```

---

## 证书

### 生成证书

```http
GET /certificates/courses/{course_id}
```

**响应**:
```json
{
  "certificate_id": "CERT-2026-001",
  "certificate_url": "/certificates/CERT-2026-001.html",
  "issued_at": "2026-04-24T10:30:00Z",
  "course": {
    "id": 1,
    "title": "Python基础"
  },
  "verification_code": "abc123"
}
```

---

### 验证证书

```http
GET /certificates/verify/{certificate_id}
```

**响应**:
```json
{
  "valid": true,
  "course": "Python基础",
  "issued_at": "2026-04-24T10:30:00Z",
  "recipient": "张三"
}
```

---

## 错误响应格式

所有错误响应遵循以下格式：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  }
}
```

**错误代码列表**:
| 代码 | HTTP状态 | 说明 |
|------|----------|------|
| UNAUTHORIZED | 401 | 未认证或Token过期 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| VALIDATION_ERROR | 422 | 请求参数验证失败 |
| RATE_LIMITED | 429 | 请求频率超限 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

---

## 代码执行限制

| 限制项 | 值 |
|--------|-----|
| 执行超时 | 30秒 |
| 内存限制 | 256MB |
| 输出限制 | 1MB |
| 代码大小限制 | 100KB |
| 并发执行限制 | 10 |
| 每分钟执行次数 | 60 |

---

## WebSocket (可选)

实时代码执行输出：

```
WS /ws/labs/{lab_id}/execute
```

**消息格式**:
```json
{
  "type": "output",
  "data": "Hello World\n"
}
```

---

## 更新日志

### v1.0.0 (2026-04-24)
- 初始版本发布
- 支持课程、实验、进度、讨论区、证书功能
