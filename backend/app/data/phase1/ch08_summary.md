# Phase 1 复习与总结

## 学习目标
- 回顾Phase 1所有核心知识点
- 建立"Java -> Python"心智模型速查表
- 明确下一阶段(数学基础)的学习方向

---

## 1. 知识点速查表

### 1.1 语法差异

| Java | Python | 记忆口诀 |
|------|--------|---------|
| `String s = "hi"` | `s = "hi"` | 变量是标签不是盒子 |
| `if (x > 0) {}` | `if x > 0:` | 括号可选, 冒号必须有 |
| `for (int i : list)` | `for item in list:` | Python的for就是foreach |
| `list.get(i)` | `list[i]` | 统一用方括号 |
| `map.getOrDefault(k, v)` | `dict.get(k, v)` | 几乎一样 |
| `a ? b : c` | `b if a else c` | 条件表达式语法反转 |
| `instanceof` | `isinstance()` | 函数而非运算符 |
| `interface` | Protocol / ABC | 鸭子类型优先 |
| `@Override` | `@abstractmethod` | 不一样但相关 |

### 1.2 数据结构映射

| Java | Python | 性能 |
|------|--------|------|
| `ArrayList` | `list` | 类似, Python list更快 |
| `HashMap` | `dict` | 类似, Python dict更简洁 |
| `HashSet` | `set` | 完全对应 |
| 数组 `int[]` | `numpy.ndarray` | NumPy快10-100x |
| `Stream` | 推导式 / 生成器 | 推导式更Pythonic |

### 1.3 设计模式差异

| Java模式 | Python方式 | 原因 |
|----------|-----------|------|
| 接口+实现 | 鸭子类型 | 不需要预先声明 |
| 工厂模式 | 函数+闭包 | 函数是一等公民 |
| 策略模式 | 函数参数 | 不需要策略接口 |
| 单例模式 | 模块级变量 | 模块天然单例 |
| 装饰器模式 | @decorator语法糖 | 语言级支持 |
| Builder模式 | 默认参数+关键字参数 | 函数天然支持 |

---

## 2. 常见陷阱回顾

### 2.1 可变默认参数
```python
# 错误
def foo(items=[]):
    items.append(1)
    return items

# 正确
def foo(items=None):
    if items is None:
        items = []
    items.append(1)
    return items
```

### 2.2 is vs ==
```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b      # True(值相等)
a is b      # False(不是同一对象)

# is 只用于 None、True、False 检查
if x is None:   # OK
if x == None:   # 能工作但不规范
```

### 2.3 浅拷贝 vs 深拷贝
```python
import copy
original = [[1, 2], [3, 4]]

shallow = original.copy()       # 或 list(original)
deep = copy.deepcopy(original)

original[0][0] = 99
shallow[0][0]   # 99! 子列表是共享的
deep[0][0]      # 1, 完全独立
```

### 2.4 闭包中的循环变量
```python
# 经典错误
funcs = [lambda: i for i in range(5)]
[f() for f in funcs]  # [4, 4, 4, 4, 4]!

# 正确: 用默认参数捕获当前值
funcs = [lambda i=i: i for i in range(5)]
[f() for f in funcs]  # [0, 1, 2, 3, 4]
```

---

## 3. 工具链速查

| 工具 | 用途 | 安装 |
|------|------|------|
| `pip` | 包管理 | Python自带 |
| `venv` | 虚拟环境 | `python -m venv .venv` |
| `jupyter` | 交互式笔记本 | `pip install jupyter` |
| `black` | 代码格式化 | `pip install black` |
| `ruff` | 快速linter | `pip install ruff` |
| `pytest` | 测试框架 | `pip install pytest` |
| `mypy` | 类型检查 | `pip install mypy` |

---

## 4. Phase 2 预告

Phase 2将进入**AI数学直觉**——不是数学课, 而是"为什么这些数学是AI的基础":

- **线性代数**: 不是矩阵运算练习, 而是"为什么数据需要向量化"
- **概率统计**: 不是概率论考试, 而是"为什么机器学习本质是概率推理"
- **梯度下降**: 不是优化理论, 而是"为什么这个简单的迭代能训练出强大的模型"

**你现在应该有的基础**:
- Python语法流畅(能读能写)
- NumPy向量化思维(不用循环)
- Pandas数据处理(能做ETL)
- 函数式编程工具(装饰器、生成器)

**Phase 2结束后你将获得**:
- 数学直觉: 看到公式能理解"它在做什么"
- 编程能力: 用NumPy实现ML算法的核心步骤
- 工程视角: 知道数学公式如何变成代码

---

## 自我评估清单

完成以下检查, 确认是否准备好进入Phase 2:

- [ ] 能不看文档写出列表推导式和字典推导式
- [ ] 能解释`@wraps`的作用和为什么需要它
- [ ] 能说出NumPy广播的三条规则
- [ ] 能用Pandas实现SQL的GROUP BY + HAVING
- [ ] 理解生成器与列表的区别, 知道何时用哪个
- [ ] 能实现一个带参数的装饰器
- [ ] 理解`loc`和`iloc`的区别

如果以上都能做到, 恭喜你, Phase 1过关!
