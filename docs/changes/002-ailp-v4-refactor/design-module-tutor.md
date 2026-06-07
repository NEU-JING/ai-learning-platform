# Design Module: Tutor — AI 辅助学习

> **变更 ID**: 002-ailp-v4-refactor  
> **负责 AC**: AC15-AC21  
> **版本**: 1.0  

---

## 1. 模块职责

提供 24/7 AI 导师服务：入学诊断对话、代码审查、个性化内容推荐、学习障碍识别。

---

## 2. 数据模型

```sql
-- AI 导师对话会话
CREATE TABLE tutor_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(32) NOT NULL,  -- diagnosis, code_review, qa, recommendation
    context_id INT,  -- 关联的 lab_id, course_id 等
    status VARCHAR(16) DEFAULT 'active',  -- active, closed
    message_count INT DEFAULT 0,
    effectiveness_score DECIMAL(3,2),  -- 会话效果评分
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

-- 对话消息
CREATE TABLE tutor_messages (
    id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES tutor_sessions(id) ON DELETE CASCADE,
    role VARCHAR(16) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    message_metadata JSONB,  -- 代码片段、错误信息等
    tokens_used INT,
    model VARCHAR(32),  -- 使用的 LLM 模型
    latency_ms INT,  -- 响应延迟
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 代码审查记录
CREATE TABLE code_reviews (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lab_id INT REFERENCES labs(id),
    code_content TEXT NOT NULL,
    language VARCHAR(16) NOT NULL,  -- python, javascript
    issues JSONB,  -- [{type, line, message, suggestion}]
    overall_score DECIMAL(5,2),  -- 0-100
    summary TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学习障碍检测
CREATE TABLE learning_obstacles (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lab_id INT REFERENCES labs(id),
    obstacle_type VARCHAR(32),  -- time_exceeded, multiple_failures, stuck
    detection_data JSONB,  -- 检测依据
    tutor_response TEXT,  -- AI 导师的响应
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. API 接口

### 3.1 AI 导师对话（AC15, AC16, AC21）

**URL**: `POST /api/v1/tutor/chat`  
**Auth**: Required

**请求**:
```json
{
  "session_id": "optional-existing-session-id",
  "session_type": "code_review",
  "context_id": 123,
  "message": "这段代码运行报错：IndexError: list index out of range",
  "attachments": [
    {"type": "code", "content": "def foo(): ...", "language": "python"}
  ]
}
```

**响应**: 200 OK (< 5s)
```json
{
  "session_id": "sess_abc123",
  "response": {
    "content": "我看到问题了。在第5行，你试图访问 `data[10]`，但列表只有5个元素...",
    "suggestions": [
      "检查列表长度后再访问",
      "使用 try-except 处理异常"
    ],
    "code_fix": "if len(data) > 10: value = data[10]"
  },
  "diagnosis": {
    "issue_type": "index_error",
    "complexity": "beginner",
    "similar_cases": 3
  },
  "latency_ms": 1200
}
```

**错误码**:
- 429: LLM 限流，自动降级到备用模型
- 503: 所有 LLM 不可用，返回 "服务暂时不可用，请稍后重试"

### 3.2 代码审查（AC16）

**URL**: `POST /api/v1/tutor/code-review`  
**Auth**: Required

**请求**:
```json
{
  "lab_id": 123,
  "code": "def train_model(X, y): ...",
  "language": "python"
}
```

**响应**:
```json
{
  "review_id": 456,
  "overall_score": 75.5,
  "summary": "代码结构良好，但缺少输入验证",
  "issues": [
    {
      "type": "warning",
      "line": 3,
      "message": "未检查输入数据是否为None",
      "suggestion": "添加 if X is None: raise ValueError(...)"
    },
    {
      "type": "improvement",
      "line": 8,
      "message": "可以使用列表推导式简化",
      "suggestion": "scores = [f(x) for x in data]"
    }
  ],
  "positive_points": ["函数命名清晰", "注释完整"]
}
```

### 3.3 获取个性化推荐（AC18）

**URL**: `GET /api/v1/tutor/recommendations`  
**Auth**: Required

**响应**:
```json
{
  "based_on": "algorithm_understanding 维度薄弱",
  "recommendations": [
    {
      "type": "course",
      "title": "线性代数可视化课程",
      "reason": "补强数学基础，提高算法理解",
      "priority": "high",
      "estimated_time": "4小时"
    },
    {
      "type": "practice",
      "title": "矩阵运算练习题",
      "reason": "针对性练习",
      "priority": "medium"
    }
  ]
}
```

### 3.4 学习障碍检测（AC20）

**URL**: `GET /api/v1/tutor/obstacles`  
**Auth**: Required

**响应**:
```json
{
  "has_obstacles": true,
  "obstacles": [
    {
      "lab_id": 45,
      "lab_name": "神经网络反向传播",
      "type": "time_exceeded",
      "data": {
        "user_time": "3小时",
        "average_time": "1小时",
        "ratio": 3.0
      },
      "tutor_message": "是否需要帮助？其他同学在此Lab的平均用时30分钟。我可以为你提供分步指导。"
    }
  ]
}
```

---

## 4. LLM 路由与降级策略

```python
class LLMRouter:
    """
    四级 LLM 降级链
    """
    LAYERS = [
        {"name": "primary", "provider": "ark", "model": "doubao-pro", "timeout": 30},
        {"name": "fallback1", "provider": "openrouter", "model": "claude-sonnet-4", "timeout": 30},
        {"name": "fallback2", "provider": "baidu", "model": "glm-4", "timeout": 20},
        {"name": "local", "provider": "local", "model": "qwen-7b", "timeout": 60}
    ]
    
    async def chat(self, messages: list, session_type: str = "qa") -> ChatResponse:
        for layer in self.LAYERS:
            try:
                response = await self._call_layer(layer, messages, session_type)
                return response
            except (TimeoutError, RateLimitError, ServiceUnavailableError) as e:
                logger.warning(f"Layer {layer['name']} failed: {e}")
                continue
        
        raise AllLayersFailed("所有 LLM 层均不可用")
```

---

## 5. AC 覆盖声明

| AC | 实现 | 验证 |
|:---:|------|------|
| AC15 | `POST /api/v1/tutor/chat` (session_type=diagnosis) | 测试诊断对话 |
| AC16 | `POST /api/v1/tutor/code-review` | 测试代码审查返回结构 |
| AC17 | `tutor_sessions.effectiveness_score` | 测试对话质量分析 |
| AC18 | `GET /api/v1/tutor/recommendations` | 测试推荐内容 |
| AC19 | 定期分析用户进度，主动推送建议 | 集成测试 |
| AC20 | `GET /api/v1/tutor/obstacles` | 测试障碍检测 |
| AC21 | `POST /api/v1/tutor/chat` + LLM 降级 | 测试 <5s 响应 |

---

## 6. Tasks

| Task | 内容 | 估时 | AC |
|------|------|:----:|:--:|
| T1 | 创建 tutor_sessions, tutor_messages 表 | 20m | - |
| T2 | 实现 LLM Router 四级降级 | 45m | AC21 |
| T3 | 实现对话 API | 30m | AC15, AC21 |
| T4 | 实现代码审查 API | 45m | AC16, AC17 |
| T5 | 实现个性化推荐 API | 30m | AC18, AC19 |
| T6 | 实现学习障碍检测 | 30m | AC20 |
| T7 | 单元测试 | 30m | AC15-AC21 |

**小计**: 7 Tasks, 3.5h
