# AI学习平台 - 代码执行沙箱

## 概述

安全的Python代码执行环境，支持两种模式：
1. **Docker模式**（生产推荐）：容器隔离和资源限制，防止恶意代码执行
2. **Subprocess回退模式**（开发环境）：Docker不可用时自动降级，无隔离但可执行代码

> **当前服务器限制**：2核4G，Docker不可用，仅使用subprocess回退模式。
> Phase 3+实验需要numpy/pandas/scikit-learn等数据科学库，已安装到venv中。
> **推荐升级至4核8G+80GB磁盘**以支持Docker沙箱。

## 文件结构

```
sandbox/
├── Dockerfile      # Docker镜像定义
├── runner.py       # 沙箱内代码执行器
└── README.md       # 本文档
```

## 双模式执行架构

```
POST /api/v1/labs/{id}/execute
  → LabService
  → code_executor.execute_code()
      → check_docker_available()
      ├── Docker可用 → execute_code_docker()
      │     → 拉取/构建镜像
      │     → 创建容器（资源限制）
      │     → 运行runner.py
      │     → 收集输出
      │     └── 清理容器
      └── Docker不可用 → execute_code_subprocess_fallback()
            → check_code_security() [AST+正则安全检查]
            → subprocess.run() [本地执行]
            → 资源限制（仅超时）
            └── 返回结果
```

## Docker模式安全特性

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

### 3. 代码安全检测（双模式共用）
- 危险模块导入检测 (os, sys, subprocess等)
- 危险函数调用检测 (eval, exec, open等)
- AST静态分析
- 正则表达式模式匹配

### 4. 文件系统限制
- 仅允许写入 `/home/sandbox/tmp`
- 禁止访问 `/proc`, `/sys`, `/dev`, `/etc` 等敏感目录

## Subprocess回退模式

当Docker不可用时，系统自动降级到subprocess模式：

**限制**：
- 无容器隔离（代码在主进程中运行）
- 无内存限制（依赖OS级OOM）
- 无文件系统限制（依赖代码安全检测）
- 有超时限制（默认30秒）
- Phase 1/2纯Python代码可正常执行
- Phase 3+需要数据科学库（numpy/pandas/scikit-learn/scipy/matplotlib），需在venv中预装

**⚠️ 安全警告**：subprocess模式仅适用于开发和受信任环境，**生产环境必须使用Docker模式**。

## 使用方法

### 构建Docker镜像

```bash
cd /path/to/sandbox
docker build -t ai-learning-platform-sandbox .
```

### API接口

```python
POST /api/v1/labs/{lab_id}/execute
Authorization: Bearer <token>
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

> **注意**：旧API路径 `/api/code/execute` 已废弃，请使用 `/api/v1/labs/{id}/execute`。

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

## 测试

```bash
# 运行沙箱相关测试
cd backend && source /tmp/ailp-venv/bin/activate
pytest tests/test_code_execution.py -v
pytest tests/test_code_security.py -v
```

## 注意事项

1. **生产环境**必须使用Docker模式运行
2. 定期清理已停止的容器: `docker container prune`
3. 监控资源使用情况
4. 定期更新基础镜像以获取安全补丁
5. subprocess模式下Phase 3+实验需要venv中预装数据科学库
6. `runner.py` 中 `hashlib` 同时出现在白名单和 `FORBIDDEN_MODULES` 中（已知矛盾，待修）
