# 函数式编程: 从Java Stream到Python推导式

## 学习目标
- 掌握Python函数定义、参数类型与闭包
- 理解Python函数式编程的核心工具: 推导式、map/filter、lambda
- 将Java Stream API经验迁移到Python

---

## 1. 函数定义: 比Java灵活得多

### 1.1 基础定义

```java
// Java: 必须声明返回类型和参数类型
public static int add(int a, int b) {
    return a + b;
}
```

```python
# Python: 类型是可选的
def add(a, b):
    return a + b

# 可以加类型提示(但不强制, 只是文档和IDE提示)
def add(a: int, b: int) -> int:
    return a + b
```

### 1.2 参数的四种形态

```python
# 1. 位置参数(最基本)
def greet(name):
    return f"Hello, {name}"

# 2. 默认参数(Java没有直接对应)
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}"

greet("Alice")                  # Hello, Alice
greet("Alice", "Hi")            # Hi, Alice
greet(greeting="Hi", name="Alice")  # 关键字参数, 顺序无关

# 3. *args: 可变位置参数
def sum_all(*args):
    return sum(args)

sum_all(1, 2, 3)               # 6
sum_all(1, 2, 3, 4, 5)        # 15

# 4. **kwargs: 可变关键字参数
def create_user(**kwargs):
    return kwargs

create_user(name="Alice", age=25)  # {"name": "Alice", "age": 25}
```

**Java对比**: Java 5有可变参数`String... args`, 但只支持位置参数, 不支持关键字参数和默认值。

### 1.3 默认参数的陷阱

```python
# 错误写法!
def append_to(item, lst=[]):
    lst.append(item)
    return lst

append_to(1)    # [1]
append_to(2)    # [1, 2]  <- 意外! 默认列表被共享了

# 正确写法
def append_to(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

**规则**: 默认参数只在函数定义时计算一次, 可变对象(list/dict/set)作为默认值会导致共享状态。

---

## 2. Lambda与函数式工具

### 2.1 Lambda——Java的对应

```java
// Java Lambda
Function<Integer, Integer> square = x -> x * x;
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
```

```python
# Python Lambda(限制: 只能单表达式)
square = lambda x: x * x
add = lambda a, b: a + b

# 使用场景: 作为参数传递
students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
students.sort(key=lambda s: s[1], reverse=True)  # 按分数降序
# [("Bob", 92), ("Alice", 85), ("Charlie", 78)]
```

**Python哲学**: Lambda只用于简单的内联函数。超过一行的逻辑, 用def定义具名函数。

### 2.2 map/filter/reduce -> Java Stream的对应

```java
// Java Stream
List<Integer> result = numbers.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .collect(Collectors.toList());
```

```python
# Python方式1: 函数式
result = list(map(lambda n: n*n, filter(lambda n: n%2==0, numbers)))

# Python方式2: 列表推导式(更Pythonic, 推荐!)
result = [n*n for n in numbers if n%2 == 0]
```

**规则**: 在Python中, 推导式 > map/filter。推导式可读性更好, 性能相当。

### 2.3 reduce

```python
from functools import reduce

# 累乘
numbers = [1, 2, 3, 4, 5]
product = reduce(lambda acc, n: acc * n, numbers)  # 120
```

---

## 3. 闭包与装饰器

### 3.1 闭包

```python
def make_multiplier(factor):
    '''外部函数"记住"了factor的值'''
    def multiply(x):
        return x * factor      # 引用了外部变量
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

double(5)    # 10
triple(5)    # 15
```

**Java对比**: 类似Java的Lambda捕获外部变量, 但Python更灵活——捕获的变量可以修改(用`nonlocal`声明)。

### 3.2 装饰器——Python最强大的语法糖

装饰器本质是**接受函数并返回函数的高阶函数**。Java没有直接对应, 最接近的是注解+AOP。

```python
import time

def timer(func):
    '''计算函数执行时间的装饰器'''
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} 执行耗时: {elapsed:.3f}秒")
        return result
    return wrapper

@timer                    # 等价于 slow_function = timer(slow_function)
def slow_function():
    time.sleep(1)
    return "done"

slow_function()           # slow_function 执行耗时: 1.001秒
```

### 3.3 带参数的装饰器

```python
def retry(max_attempts=3):
    '''重试装饰器工厂'''
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"第{attempt+1}次失败, 重试中...")
        return wrapper
    return decorator

@retry(max_attempts=5)    # 最多重试5次
def call_api():
    pass
```

### 3.4 functools.wraps——保持函数元信息

```python
from functools import wraps

def timer(func):
    @wraps(func)            # 保持func的__name__, __doc__等
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.time()-start:.3f}s")
        return result
    return wrapper
```

**不加wraps**: 装饰后的函数`__name__`变成"wrapper", 调试时难以定位。**始终使用wraps!**

---

## 4. 生成器——惰性计算的Python方式

### 4.1 yield关键字

```python
def fibonacci(n):
    '''生成前n个斐波那契数'''
    a, b = 0, 1
    for _ in range(n):
        yield a           # yield而非return, 函数变成生成器
        a, b = b, a + b

fib = fibonacci(10)
print(list(fib))          # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

**Java对比**: 类似Java Stream的惰性求值, 但Python生成器更通用——任何函数都可以用yield变成迭代器。

### 4.2 生成器表达式

```python
# 列表推导式——立即计算, 占内存
squares = [x**2 for x in range(1000000)]    # ~8MB内存

# 生成器表达式——惰性计算, 几乎不占内存
squares_gen = (x**2 for x in range(1000000))  # 几乎0内存

# 生成器只能遍历一次
sum(squares_gen)          # 一次遍历求和
```

**经验法则**: 处理大数据时, 用生成器表达式替代列表推导式。

---

## 练习题

1. 写一个装饰器`@validate_type(**types)`, 检查函数参数类型。例如`@validate_type(name=str, age=int)`会在调用时检查name是否为str、age是否为int
2. 用生成器实现一个"读取大文件并过滤"的函数: 逐行读取文件, 只yield包含关键词的行
3. 将以下Java Stream代码转为Python列表推导式:
```java
List<String> result = words.stream()
    .filter(w -> w.length() > 3)
    .map(String::toUpperCase)
    .sorted()
    .collect(Collectors.toList());
```
