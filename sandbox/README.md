# AI学习平台 - 代码执行沙箱

## 概述

安全的Python代码执行环境，使用Docker容器隔离和资源限制，防止恶意代码执行。

## 文件结构

```
sandbox/
├── Dockerfile      # Docker镜像定义
├── runner.py       # 沙箱内代码执行器
└── README.md       # 本文档
```

## 安全特性

### 1. 容器隔离
- 基于 `python:3.11-slim` 镜像
- 非root用户运行
- 只读根文件系统
- 禁用网络访问

### 2. 资源限制
- **CPU**: 0.5核
- **内存**: 256MB (无swap)
- **执行时间**: 30秒 (可配置)
- **输出大小**: 1MB
- **进程数**: 50个

### 3. 代码安全检测
- 危险模块导入检测 (os, sys, subprocess等)
- 危险函数调用检测 (eval, exec, open等)
- AST静态分析
- 正则表达式模式匹配

### 4. 文件系统限制
- 仅允许写入 `/home/sandbox/tmp`
- 禁止访问 `/proc`, `/sys`, `/dev`, `/etc` 等敏感目录

## 使用方法

### 构建Docker镜像

```bash
cd /path/to/sandbox
docker build -t ai-learning-platform-sandbox .
```

### 运行代码

```python
from app.services.code_executor import execute_code_sandbox
import asyncio

async def main():
    result = await execute_code_sandbox('''
import numpy as np
arr = np.array([1, 2, 3])
print(f"数组: {arr}")
print(f"平均值: {np.mean(arr)}")
''')
    print(result)

asyncio.run(main())
```

### API接口

```python
POST /api/code/execute
Content-Type: application/json

{
    "code": "print('Hello World')",
    "timeout": 30
}
```

响应:
```json
{
    "success": true,
    "output": "Hello World\n",
    "error": null,
    "execution_time_ms": 123
}
```

## 允许的模块

### 数学计算
- `math`, `random`, `statistics`, `fractions`, `decimal`
- `numpy`, `pandas`, `matplotlib`, `scikit-learn`, `scipy`

### 数据处理
- `datetime`, `time`, `calendar`
- `collections`, `itertools`, `functools`, `operator`
- `re`, `string`, `json`, `csv`

### 内置函数
- 基础类型: `int`, `float`, `str`, `list`, `dict`, `set`, `tuple`
- 函数: `print`, `len`, `range`, `map`, `filter`, `zip`, `enumerate`
- 异常: 所有标准异常类型

## 禁止的操作

### 系统操作
- 导入 `os`, `sys`, `subprocess`, `socket`
- 调用 `os.system`, `os.popen`, `os.fork`, `os.exec`
- 访问 `sys.modules`, `sys.path`

### 文件操作
- 使用 `open()`, `file()`
- 导入 `shutil`, `pathlib`
- 文件删除操作

### 网络操作
- 导入 `urllib`, `requests`, `http`
- 创建socket连接

### 代码执行
- 使用 `eval()`, `exec()`, `compile()`
- 使用 `__import__()`

### 多线程/进程
- 使用 `threading`, `multiprocessing`, `asyncio`

## 回退模式

当Docker不可用时，系统会自动回退到本地subprocess模式执行代码，并应用资源限制。

## 测试

```bash
# 运行沙箱测试
python3 test_sandbox.py
```

## 注意事项

1. **生产环境**必须使用Docker模式运行
2. 定期清理已停止的容器: `docker container prune`
3. 监控资源使用情况
4. 定期更新基础镜像以获取安全补丁
