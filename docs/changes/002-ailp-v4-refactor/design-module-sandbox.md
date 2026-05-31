# Design Module: Sandbox — 混合执行沙箱

> **变更 ID**: 002-ailp-v4-refactor  
> **负责 AC**: AC38-AC44  
> **版本**: 1.0  

---

## 1. 模块职责

提供三层执行环境：Layer A（本地进程）、Layer B（外部资源）、Layer C（验证引擎），支持代码执行、模型训练、结果验证。

---

## 2. 数据模型

```sql
-- 执行请求
CREATE TABLE execution_requests (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lab_id INT REFERENCES labs(id),
    layer VARCHAR(8) NOT NULL,  -- A, B, C
    code TEXT,
    language VARCHAR(16) DEFAULT 'python',
    resources JSONB,  -- {cpu: 2, memory: "4g"}
    status VARCHAR(16) DEFAULT 'pending',  -- pending, running, completed, failed
    result JSONB,  -- 执行结果
    logs TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 外部资源执行（Layer B）
CREATE TABLE external_executions (
    id SERIAL PRIMARY KEY,
    request_id INT REFERENCES execution_requests(id),
    provider VARCHAR(16),  -- kaggle, colab, autodl
    external_job_id VARCHAR(64),
    artifacts JSONB,  -- {model_url: "...", log_url: "..."}
    status VARCHAR(16),
    submitted_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- 验证任务（Layer C）
CREATE TABLE verification_tasks (
    id SERIAL PRIMARY KEY,
    request_id INT REFERENCES execution_requests(id),
    model_url VARCHAR(256),  -- 模型文件URL
    dataset VARCHAR(64),  -- 验证数据集
    metrics JSONB,  -- {accuracy: 0.92, loss: 0.15}
    audit_log JSONB,  -- 完整审计
    status VARCHAR(16),
    passed BOOLEAN,
    verified_at TIMESTAMP
);

-- 沙箱 Provider 健康状态
CREATE TABLE sandbox_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(16) UNIQUE NOT NULL,  -- local, kaggle, colab
    layer VARCHAR(8) NOT NULL,
    is_healthy BOOLEAN DEFAULT TRUE,
    last_health_check TIMESTAMP,
    failure_count INT DEFAULT 0,
    config JSONB
);
```

---

## 3. API 接口

### 3.1 提交代码执行（AC38）

**URL**: `POST /api/v1/sandbox/execute`  
**Auth**: Required

**请求**:
```json
{
  "lab_id": 123,
  "code": "print('hello world')",
  "language": "python",
  "layer": "A"
}
```

**响应**:
```json
{
  "execution_id": "exec_abc123",
  "status": "completed",
  "result": {
    "output": "hello world\n",
    "exit_code": 0,
    "execution_time_ms": 500
  },
  "score": 100,
  "passed": true
}
```

### 3.2 外部资源训练（AC39）

**URL**: `POST /api/v1/sandbox/external/submit`  
**Auth**: Required

**请求**:
```json
{
  "lab_id": 456,
  "provider": "kaggle",
  "notebook_url": "https://kaggle.com/user/notebook",
  "expected_output": "model.pth"
}
```

**响应**:
```json
{
  "submission_id": 789,
  "status": "queued",
  "estimated_wait": "5分钟",
  "webhook_url": "https://ailp.com/webhooks/kaggle/789"
}
```

### 3.3 上传训练产物验证（AC40）

**URL**: `POST /api/v1/sandbox/verify`  
**Auth**: Required

**请求**:
```json
{
  "lab_id": 456,
  "model_file": "<binary>",
  "training_log": "{...}"
}
```

**响应**:
```json
{
  "verification_id": 101,
  "status": "passed",
  "metrics": {
    "accuracy": 0.92,
    "precision": 0.91,
    "recall": 0.93
  },
  "audit": {
    "training_epochs": 10,
    "dataset_size": 60000,
    "no_anomalies": true
  }
}
```

---

## 4. 三层执行模型

| 层级 | 环境 | 安全 | 资源 | 适用 | AC |
|-----|-----|-----|-----|-----|----|
| Layer A | 本地进程 | 低 | 2核4G | 简单练习 | AC38 |
| Layer B | Kaggle/Colab | 中 | 有 | 模型训练 | AC39 |
| Layer C | 验证引擎 | 高 | 严格 | 模型审计 | AC40-AC41 |

### Provider 优先级

```python
PROVIDERS = {
    'layer_a': ['local_subprocess'],
    'layer_b': ['kaggle', 'colab', 'autodl'],  # 按稳定性排序
    'layer_c': ['dedicated_verifier']
}
```

---

## 5. AC 覆盖声明

| AC | 实现 |
|:---:|------|
| AC38 | Layer A 本地执行 |
| AC39 | Layer B 外部资源提交 |
| AC40 | Layer C 验证引擎 |
| AC41 | 验证失败处理 |
| AC42 | 混合流程状态标记 |
| AC43 | 路径感知（与Profile协作） |
| AC44 | 隐私控制（与Profile协作） |

---

## 6. Tasks

| Task | 内容 | 估时 | AC |
|------|------|:----:|:--:|
| S1 | 创建执行相关表 | 20m | - |
| S2 | 实现 Layer A 本地执行 | 45m | AC38 |
| S3 | 实现 Layer B 外部资源集成 | 45m | AC39 |
| S4 | 实现 Layer C 验证引擎 | 45m | AC40-AC41 |
| S5 | 实现混合流程完成标记 | 30m | AC42 |
| S6 | Provider 健康检查 | 30m | - |
| S7 | 单元测试 | 30m | AC38-AC44 |

**小计**: 7 Tasks, 4h 15m
