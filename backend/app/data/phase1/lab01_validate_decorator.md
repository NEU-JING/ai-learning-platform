# 实验1: 实现数据验证装饰器框架

## 实验目标
构建一个类型安全装饰器框架, 让你体会Python装饰器+鸭子类型+异常处理的组合威力。

## 背景
在Java中, 类型安全由编译器保证。在Python中, 我们通常依赖EAFP(先做再说), 但在API边界(如Web接口、配置文件), 显式验证仍然重要。本实验要求你实现一个装饰器, 在运行时检查函数参数和返回值的类型。

## 需求规格

### 1. 基础功能: `@validate_types`

```python
@validate_types(name=str, age=int, returns=str)
def greet(name, age):
    return f"{name}今年{age}岁"

greet("Alice", 25)          # 正常
greet("Alice", "25")        # TypeError: 参数age期望int, 得到str
```

### 2. 高级功能: 自定义验证器

```python
@validate_types(
    email=lambda x: "@" in x,       # 自定义验证函数
    age=lambda x: 0 < x < 150,      # 范围验证
    name=lambda x: len(x) >= 2       # 长度验证
)
def register(email, age, name):
    return "OK"

register("a@b.com", 25, "Alice")     # 正常
register("invalid", 25, "Alice")     # ValueError: email验证失败
```

### 3. 可选验证

```python
@validate_types(name=str, age=int, _optional=["age"])
def greet(name, age=None):
    return f"Hello {name}"

greet("Alice")               # OK, age可选
greet("Alice", 25)           # OK
```

## 提示
- 使用`functools.wraps`保持函数元信息
- 使用`inspect.signature`获取函数参数名
- 类型检查用`isinstance`, 自定义验证直接调用
- 验证失败时抛出`TypeError`(类型错误)或`ValueError`(值错误)

## 入门代码
在实验编辑器中完成实现。请确保所有测试用例通过。
