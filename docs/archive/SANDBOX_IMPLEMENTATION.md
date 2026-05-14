# AI学习平台 - 代码沙箱实现总结

## 完成内容

### 1. 沙箱Docker镜像 (sandbox/Dockerfile)
- 基于 `python:3.11-slim` 构建
- 预装AI库: numpy, pandas, matplotlib, scikit-learn, scipy
- 使用非root用户 (sandbox) 运行
- 使用清华镜像加速pip安装
- 配置只读文件系统和受限写入权限

### 2. 沙箱执行器 (sandbox/runner.py)
- 从stdin读取代码并执行
- AST静态分析安全检查
- 资源限制 (CPU/内存/时间/输出)
- 危险模块导入拦截
- 危险函数调用拦截
- 特殊属性访问拦截
- JSON格式结果输出

### 3. 安全检测模块 (backend/app/core/code_security.py)
- 危险模块黑名单 (os, sys, subprocess, socket等)
- 危险函数黑名单 (eval, exec, open, __import__等)
- 危险属性黑名单 (__subclasses__, __globals__, __code__等)
- 正则表达式模式检测
- AST静态分析器
- 允许的模块白名单

### 4. 代码执行服务 (backend/app/services/code_executor.py)
- Docker容器执行模式
- Subprocess回退模式
- 输入验证 (代码大小、超时时间)
- 自动清理容器和临时文件
- 超时处理
- 错误处理和结果解析

## 安全特性

### 禁止的操作
- 文件系统写操作（除/tmp外）
- 网络访问
- 子进程创建
- 危险模块导入 (os, sys, subprocess等)
- 危险函数调用 (eval, exec, open等)
- 多线程/多进程

### 资源限制
- CPU: 0.5核
- 内存: 256MB
- 执行时间: 30秒 (可配置)
- 输出限制: 1MB
- 代码大小: 100KB

## API接口

```python
POST /api/code/execute
Request: {"code": "print('hello')", "timeout": 30}
Response: {
    "success": true/false,
    "output": "执行输出",
    "error": "错误信息",
    "execution_time_ms": 1234
}
```

## 测试验证

所有功能测试通过:
- ✓ 基本执行
- ✓ 数学运算
- ✓ NumPy使用
- ✓ Pandas使用
- ✓ 错误处理
- ✓ 超时功能
- ✓ OS模块拦截
- ✓ Eval拦截
- ✓ Subprocess拦截
- ✓ Open函数拦截
- ✓ 大输出截断
- ✓ 语法错误处理
- ✓ 空代码处理
- ✓ 代码大小限制

## 使用方法

### 构建Docker镜像
```bash
cd sandbox
docker build -t ai-learning-platform-sandbox .
```

### 启动后端服务
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 调用API
```bash
curl -X POST http://localhost:8000/api/code/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"code": "print(\"Hello\")", "timeout": 30}'
```

## 文件列表

```
sandbox/
├── Dockerfile              # Docker镜像定义 (48行)
├── runner.py               # 沙箱执行器 (368行)
└── README.md               # 使用文档

backend/app/
├── core/
│   └── code_security.py    # 安全检测模块 (383行)
└── services/
    └── code_executor.py    # 代码执行服务 (628行)
```

## 后续优化建议

1. **生产环境部署**
   - 配置Docker守护进程安全选项
   - 使用更严格的seccomp配置
   - 配置容器运行时监控

2. **性能优化**
   - 预启动容器池，减少启动开销
   - 使用共享内存/tmp
   - 实现请求队列和限流

3. **监控告警**
   - 监控资源使用情况
   - 记录执行日志
   - 设置异常告警

4. **扩展功能**
   - 支持更多编程语言
   - 添加代码评分功能
   - 支持单元测试运行
