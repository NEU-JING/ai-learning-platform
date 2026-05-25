# AI学习平台 - API文档

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **API版本**: v1
- **认证方式**: Bearer Token (JWT)

## 认证

### 获取Token

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**响应**:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### 使用Token

在请求头中添加:
```
Authorization: Bearer <your_token>
```

## API端点

### 用户认证

#### 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**响应**:
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2024-01-01T00:00:00",
    "is_active": true
}
```

#### 获取当前用户信息
```http
GET /api/auth/me
Authorization: Bearer <token>
```

**响应**:
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2024-01-01T00:00:00",
    "is_active": true
}
```

### 课程管理

#### 获取所有课程
```http
GET /api/courses
```

**响应**:
```json
[
    {
        "id": 1,
        "title": "Python基础与AI工具链",
        "description": "从零开始学习Python，掌握AI开发必备工具",
        "level": "beginner",
        "category": "foundation",
        "duration_hours": 28,
        "order_index": 1,
        "is_published": true,
        "chapters": [
            {
                "id": 1,
                "title": "Day 1 - Python vs Java：语法对比",
                "chapter_type": "text",
                "duration_minutes": 120,
                "order_index": 1
            }
        ]
    }
]
```

#### 获取课程详情
```http
GET /api/courses/{course_id}
```

**响应**:
```json
{
    "id": 1,
    "title": "Python基础与AI工具链",
    "description": "从零开始学习Python，掌握AI开发必备工具",
    "level": "beginner",
    "category": "foundation",
    "duration_hours": 28,
    "chapters": [
        {
            "id": 1,
            "title": "Day 1 - Python vs Java：语法对比",
            "content": "# Python vs Java...",
            "chapter_type": "text",
            "duration_minutes": 120,
            "order_index": 1,
            "has_lab": true
        }
    ]
}
```

#### 获取章节详情
```http
GET /api/chapters/{chapter_id}
```

**响应**:
```json
{
    "id": 1,
    "title": "Day 1 - Python vs Java：语法对比",
    "content": "# Markdown内容...",
    "chapter_type": "text",
    "duration_minutes": 120,
    "course_id": 1,
    "lab": {
        "id": 1,
        "title": "Python基础练习",
        "description": "完成基础Python语法练习",
        "starter_code": "# 在此编写你的代码\nprint('Hello')",
        "hints": ["使用print函数", "注意缩进"]
    }
}
```

### 代码执行

#### 执行Python代码
```http
POST /api/code/execute
Authorization: Bearer <token>
Content-Type: application/json

{
    "code": "print('Hello, World!')",
    "timeout": 30
}
```

**响应**:
```json
{
    "success": true,
    "output": "Hello, World!\n",
    "error": null,
    "execution_time_ms": 45
}
```

**错误响应**:
```json
{
    "success": false,
    "output": "",
    "error": "NameError: name 'undefined_var' is not defined",
    "execution_time_ms": 12
}
```

### 实验提交

#### 提交实验
```http
POST /api/labs/{lab_id}/submit
Authorization: Bearer <token>
Content-Type: application/json

{
    "code": "def hello():\n    return 'Hello'\nprint(hello())"
}
```

**响应**:
```json
{
    "success": true,
    "output": "Hello\n",
    "error": null,
    "execution_time_ms": 23,
    "submission_id": 123
}
```

#### 获取实验历史
```http
GET /api/labs/{lab_id}/submissions
Authorization: Bearer <token>
```

**响应**:
```json
[
    {
        "id": 123,
        "code": "def hello():...",
        "output": "Hello\n",
        "status": "success",
        "execution_time_ms": 23,
        "created_at": "2024-01-01T12:00:00"
    }
]
```

### 学习进度

#### 获取学习进度
```http
GET /api/progress
Authorization: Bearer <token>
```

**响应**:
```json
[
    {
        "id": 1,
        "chapter_id": 1,
        "status": "completed",
        "completed_at": "2024-01-01T12:00:00",
        "last_accessed_at": "2024-01-01T12:00:00"
    },
    {
        "id": 2,
        "chapter_id": 2,
        "status": "in_progress",
        "completed_at": null,
        "last_accessed_at": "2024-01-01T13:00:00"
    }
]
```

#### 更新学习进度
```http
POST /api/progress/{chapter_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "status": "completed"
}
```

状态可选值:
- `not_started` - 未开始
- `in_progress` - 学习中
- `completed` - 已完成

**响应**:
```json
{
    "message": "进度更新成功"
}
```

### 用户统计

#### 获取学习统计
```http
GET /api/stats
Authorization: Bearer <token>
```

**响应**:
```json
{
    "total_courses": 6,
    "completed_courses": 2,
    "total_chapters": 84,
    "completed_chapters": 35,
    "total_labs": 50,
    "completed_labs": 20,
    "total_learning_hours": 45.5,
    "current_streak_days": 5,
    "longest_streak_days": 12
}
```

### 证书系统

#### 获取已获得证书
```http
GET /api/certificates
Authorization: Bearer <token>
```

**响应**:
```json
[
    {
        "id": 1,
        "title": "Python基础认证",
        "course_id": 1,
        "issued_at": "2024-01-15T10:00:00",
        "certificate_number": "AI-2024-001234",
        "download_url": "/api/certificates/1/download"
    }
]
```

#### 下载证书
```http
GET /api/certificates/{certificate_id}/download
Authorization: Bearer <token>
```

**响应**: PDF文件

### 社区功能

#### 获取讨论区帖子
```http
GET /api/discussions
```

**查询参数**:
- `course_id` - 按课程筛选（可选）
- `tag` - 按标签筛选（可选）
- `page` - 页码，默认1
- `limit` - 每页数量，默认20

**响应**:
```json
{
    "total": 100,
    "page": 1,
    "limit": 20,
    "items": [
        {
            "id": 1,
            "title": "Python语法问题求助",
            "content": "请问...",
            "author": {
                "id": 1,
                "username": "johndoe"
            },
            "tags": ["python", "beginner"],
            "replies_count": 5,
            "created_at": "2024-01-01T10:00:00"
        }
    ]
}
```

#### 创建帖子
```http
POST /api/discussions
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "我的问题",
    "content": "详细描述...",
    "course_id": 1,
    "tags": ["python", "question"]
}
```

### 系统健康

#### 健康检查
```http
GET /health
```

**响应**:
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2024-01-01T00:00:00Z",
    "services": {
        "database": "connected",
        "redis": "connected",
        "sandbox": "connected"
    }
}
```

## 错误代码

| 状态码 | 错误信息 | 说明 |
|--------|----------|------|
| 400 | 请求参数错误 | 检查请求参数 |
| 401 | 未授权 | Token无效或过期 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 资源不存在 | 检查URL |
| 422 | 验证错误 | 数据格式不正确 |
| 429 | 请求过于频繁 | 稍后重试 |
| 500 | 服务器内部错误 | 联系管理员 |

## 分页规范

列表接口默认支持分页:

```http
GET /api/discussions?page=2&limit=10
```

**响应**:
```json
{
    "total": 100,
    "page": 2,
    "limit": 10,
    "total_pages": 10,
    "items": [...]
}
```

## 限流规则

- 匿名用户: 60次/分钟
- 登录用户: 120次/分钟
- 代码执行: 10次/分钟

## 代码规范

### Python代码执行限制

- 超时: 30秒
- 内存限制: 512MB
- CPU限制: 1核心
- 禁止导入: `os`, `sys`, `subprocess`, `socket`

### 允许的标准库

```
math, random, datetime, json, re, collections,
itertools, functools, typing, string, hashlib,
base64, copy, pprint, decimal, fractions, statistics
```

### 允许的数据科学库

```
numpy, pandas, matplotlib, seaborn, scikit-learn
```

## SDK示例

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

class AILearningClient:
    def __init__(self, token=None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
    
    def login(self, email, password):
        resp = self.session.post(f"{BASE_URL}/auth/login", data={
            "username": email,
            "password": password
        })
        data = resp.json()
        self.token = data["access_token"]
        self.session.headers["Authorization"] = f"Bearer {self.token}"
        return data
    
    def get_courses(self):
        return self.session.get(f"{BASE_URL}/courses").json()
    
    def execute_code(self, code):
        return self.session.post(f"{BASE_URL}/code/execute", json={
            "code": code,
            "timeout": 30
        }).json()

# 使用示例
client = AILearningClient()
client.login("user@example.com", "password")
print(client.get_courses())
print(client.execute_code("print('Hello')"))
```

### JavaScript

```javascript
class AILearningClient {
    constructor(baseUrl = 'http://localhost:8000/api') {
        this.baseUrl = baseUrl;
        this.token = null;
    }
    
    async login(email, password) {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        const resp = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: formData
        });
        
        const data = await resp.json();
        this.token = data.access_token;
        return data;
    }
    
    async getCourses() {
        const resp = await fetch(`${this.baseUrl}/courses`, {
            headers: this.token ? {'Authorization': `Bearer ${this.token}`} : {}
        });
        return resp.json();
    }
    
    async executeCode(code) {
        const resp = await fetch(`${this.baseUrl}/code/execute`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({code, timeout: 30})
        });
        return resp.json();
    }
}

// 使用示例
const client = new AILearningClient();
await client.login('user@example.com', 'password');
console.log(await client.getCourses());
console.log(await client.executeCode("print('Hello')"));
```
