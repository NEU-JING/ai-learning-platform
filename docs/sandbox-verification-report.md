# AILP 沙盒环境验证报告

> 日期：2026-05-19 | 验证人：Hermes | 环境：2核4G 服务器

---

## 1. 架构概览

```
前端提交代码
    │
    ▼
labs.py (API入口)
    │
    ├── check_code_security() ← 安全检查
    │
    ├── execute_code_docker() ← 代码执行
    │       ├── Docker模式（当前不可用）
    │       └── subprocess回退模式（当前走这条路）
    │
    ├── CodeGrader.grade_in_sandbox() ← 评测打分
    │
    └── LabService.submit_and_grade() ← 写结果+更新进度
```

## 2. 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| Docker 沙箱 | ❌ 不可用 | sandbox 目录不存在，服务器资源不足 |
| Subprocess 回退 | ✅ 运行中 | 自动降级，本地进程执行 |
| 依赖库 | ✅ 已安装 | numpy/pandas/sklearn/scipy/matplotlib |
| 安全检查 | ⚠️ 可用但过严 | 详见第4节 |

## 3. Subprocess 回退模式能力评估

### ✅ 能做的

- Phase 1-2 基础 Python（语法/数据结构/OOP/函数式）
- numpy/pandas/sklearn/scipy/matplotlib 数据处理
- 资源限制：CPU 时间、内存 256MB、文件大小 1MB、进程数
- 超时控制：默认 30 秒，最大 300 秒
- 输出截断：10KB 限制

### ❌ 不能做的（被安全策略阻断）

- 读取数据文件（`open()` 被禁）
- 使用 `os`/`sys` 模块（Phase 1 常用）
- 使用 `pathlib`（数据路径处理）
- 使用 `hashlib`（白名单和黑名单矛盾）
- 访问 `__class__`/`__dict__` 等 OOP 核心属性（Phase 1 教学内容）

## 4. 安全策略问题详解

### 4.1 P0：`open()` 被禁止 → 实验课完全不可用

```
# 安全检查直接拦截
> open('creditcard.csv')  → "禁止使用 open 函数"
```

**影响**：所有需要读取数据的实验课（信用卡欺诈检测、Kaggle Titanic、端到端 ML 流水线等）都无法执行。这不是边缘情况，是**核心功能不可用**。

### 4.2 P0：Grader 用 `eval()` 执行测试，但安全检查禁止 `eval()`

```python
# grader.py 第165行
_fn = eval(_func)  # 评测脚本自身用了 eval
```

如果安全检查对评测脚本也生效，所有实验课评测都无法工作。

### 4.3 P1：黑名单过严，学习必需操作被误杀

| 被禁止 | 实际影响 | 建议 |
|--------|---------|------|
| `import os` | Phase 1 文件操作练习 | 只禁 `os.system`/`os.popen`/`os.fork` 等 |
| `import sys` | Phase 1 命令行练习 | 只禁 `sys.exit`/`sys.modules` |
| `open()` | 所有读数据实验 | 允许只读模式 `open(path, 'r')` |
| `__class__`/`__dict__` | OOP 教学核心 | 应该允许 |
| `import pathlib` | 数据路径处理 | 移入白名单 |
| `hashlib` | 白名单+黑名单矛盾 | 去黑名单保留白名单 |

### 4.4 P1：Subprocess 代码包装有语法陷阱

```python
# code_executor.py 第288-318行
# 用户代码被缩进4格放在 try: 块里
try:
    <用户代码>   # ← 如果有函数外的 return/yield/break → SyntaxError
except Exception as e:
    ...
```

函数外的 `return`/`yield`/`break`/`continue` 会直接报语法错误。

## 5. 未完成验证项

- ❌ 未端到端跑通"提交实验代码 → 评测 → 出分"完整流程（登录密码问题被阻）
- ❌ 未验证 Grader 生成的评测脚本能通过安全检查
- ❌ 未验证前端 LabPage 的"运行"/"提交评测"按钮与后端 API 的完整链路

## 6. 修复建议

### P0（不修则实验课完全不可用）

1. **`open()` 白名单化**：允许只读模式 `open(path, 'r')`，禁止写入/删除
2. **Grader 评测脚本绕过安全检查**：评测代码不应受用户级安全限制

### P1（不修则体验严重受损）

3. **收紧黑名单精度**：`os`/`sys` 大部分功能无害，只禁危险调用
4. **解决 `hashlib` 矛盾**：白名单和黑名单同时存在
5. **修复代码包装语法陷阱**：用户代码应放在函数体内执行

### P2（基础设施）

6. **服务器升级 4 核 8G + 80GB**：部署 Docker 沙箱，实现真正的隔离执行

## 7. 一句话结论

> **沙盒执行引擎本身能用，但安全策略把实验课需要的能力都禁了。** 需要从"禁止一切危险操作"转向"允许学习必需操作 + 精准禁危险调用"——即安全策略 2.0。
