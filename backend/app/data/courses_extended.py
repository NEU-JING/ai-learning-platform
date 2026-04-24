"""
AI学习平台完整课程体系 - 14周98天学习计划
从Python基础到AI工程化的完整学习路径
适合有Java背景的开发者转型AI
"""

COURSES_DATA = [
    {
        "title": "Phase 1: Python基础与AI工具链（2周/14天）",
        "description": "从Java开发者视角快速掌握Python，学习NumPy、Pandas等AI核心工具链。专为有编程基础的开发者设计，高效入门AI开发。",
        "level": "beginner",
        "category": "python",
        "duration_hours": 28,
        "order_index": 1,
        "chapters": [
            {
                "title": "第1章：Python快速上手 - 从Java视角入门",
                "content": """# Python快速上手：Python vs Java语法对比

## 🎯 学习目标
- 理解Python与Java的核心差异（动态类型、缩进语法、一切皆对象）
- 掌握Python基本数据类型和控制流
- 完成Python环境配置，能独立运行脚本
- 理解Python的"Pythonic"写法

---

## 📖 核心内容

### 1. 语言设计理念对比

| 特性 | Java | Python |
|------|------|--------|
| **类型系统** | 静态类型，编译期检查 | 动态类型，运行时确定 |
| **语法风格** | 大括号 `{}` 定义代码块 | 缩进定义代码块 |
| **执行方式** | 编译为字节码，JVM执行 | 解释执行，CPython为C实现 |
| **内存管理** | 垃圾回收器（GC） | 引用计数 + 垃圾回收 |
| **编程范式** | 面向对象为主 | 多范式（OO + 函数式 + 过程式）|

**作为Java开发者，你需要放下这些习惯：**
- ❌ 不需要声明变量类型
- ❌ 不需要写分号结束语句
- ❌ 不需要大括号包裹代码块
- ❌ 不需要getter/setter（用@property）
- ❌ 不需要main方法才能运行

### 2. 环境配置与第一个程序

**安装Python（推荐3.9+）：**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 验证安装
python3 --version  # Python 3.10.12
pip3 --version

# 创建虚拟环境（强烈建议）
python3 -m venv ~/ai-venv
source ~/ai-venv/bin/activate  # Windows: ai-venv\\Scripts\\activate

# 退出虚拟环境
deactivate
```

**第一个Python程序：**
```python
# hello.py - 不需要类，不需要main方法
print("Hello, AI World!")

# 可以直接写顶层代码
name = "Python"
print(f"Welcome to {name}!")  # f-string格式化，类似Java的 "Welcome to " + name
```

### 3. 变量与数据类型

```python
# Python是动态类型，不需要声明类型
age = 25                    # int
height = 1.75               # float
name = "Alice"              # str
is_student = True           # bool

# 类型检查
type(age)       # <class 'int'>
type(name)      # <class 'str'>

# 类型转换（类似Java的包装类方法）
age_str = str(age)          # "25"
age_float = float(age)      # 25.0
height_int = int(height)    # 1（截断小数）

# Python的变量是引用，不是盒子
a = [1, 2, 3]
b = a           # b和a指向同一个列表
b.append(4)
print(a)        # [1, 2, 3, 4] - a也被修改了！

# 复制要用copy()
c = a.copy()    # 或 list(a), a[:]
c.append(5)
print(a)        # [1, 2, 3, 4] - a不变
print(c)        # [1, 2, 3, 4, 5]
```

### 4. 基础数据结构（对比Java）

**列表 List - 对应Java的ArrayList：**
```python
# 创建
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]  # Python列表可以混存不同类型

# 访问（同Java数组）
print(fruits[0])        # "apple"
print(fruits[-1])       # "cherry" - 负数索引，Python特色！

# 切片（超级强大）
print(numbers[0:3])     # [1, 2, 3] - 索引0到2
print(numbers[:3])      # [1, 2, 3] - 从头开始
print(numbers[3:])      # [4, 5] - 到末尾
print(numbers[::2])     # [1, 3, 5] - 步长为2
print(numbers[::-1])    # [5, 4, 3, 2, 1] - 反转！

# 常用方法
fruits.append("date")           # 添加元素
fruits.insert(1, "apricot")     # 插入
fruits.remove("banana")         # 删除指定值
popped = fruits.pop()           # 删除并返回最后一个
fruits.sort()                   # 原地排序
fruits.reverse()                # 原地反转

# 列表推导式（Python灵魂语法）
squares = [x**2 for x in range(10)]
evens = [x for x in range(10) if x % 2 == 0]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
print(evens)    # [0, 2, 4, 6, 8]
```

**字典 Dict - 对应Java的HashMap：**
```python
# 创建
student = {
    "name": "张三",
    "age": 25,
    "courses": ["Math", "AI"]
}

# 访问
print(student["name"])          # "张三"
print(student.get("grade", "N/A"))  # "N/A" - 默认值，不会报错

# 添加/修改
student["grade"] = "A"
student["age"] = 26

# 遍历
for key in student:
    print(f"{key}: {student[key]}")

for key, value in student.items():
    print(f"{key}: {value}")

# 字典推导式
squares_dict = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

**元组 Tuple - 不可变列表：**
```python
# 元组一旦创建不能修改（类似Java的final List）
coordinates = (10, 20)
# coordinates[0] = 15  # ❌ 报错！

# 解包（Pythonic写法）
x, y = coordinates
print(x, y)  # 10 20

# 多返回值（本质是返回元组）
def get_min_max(numbers):
    return min(numbers), max(numbers)

min_val, max_val = get_min_max([3, 1, 4, 1, 5])
```

**集合 Set - 对应Java的HashSet：**
```python
# 创建
fruits = {"apple", "banana", "cherry"}

# 操作
fruits.add("date")
fruits.remove("banana")

# 集合运算
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print(a & b)  # {3, 4} - 交集
print(a | b)  # {1, 2, 3, 4, 5, 6} - 并集
print(a - b)  # {1, 2} - 差集
print(a ^ b)  # {1, 2, 5, 6} - 对称差集
```

### 5. 控制流

**条件语句：**
```python
age = 18

if age < 13:
    print("儿童")
elif age < 20:  # else if 简写
    print("青少年")  # 输出
else:
    print("成年人")

# 三元表达式（类似Java的 condition ? a : b）
status = "成年" if age >= 18 else "未成年"

# Python没有switch-case，用字典替代
def get_day_name(day_number):
    days = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }
    return days.get(day_number, "Invalid")
```

**循环：**
```python
# for循环 - 迭代器模式
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# range() - 生成整数序列
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 10, 2):   # 2, 4, 6, 8 (start, stop, step)
    print(i)

# while循环
count = 0
while count < 5:
    print(count)
    count += 1  # Python没有++/--

# 循环控制
for num in range(10):
    if num == 3:
        continue    # 跳过当前迭代
    if num == 7:
        break       # 终止循环
    print(num)

# enumerate - 同时获取索引和值
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
# 0: apple
# 1: banana
# 2: cherry

# zip - 并行迭代多个序列
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name} is {age} years old")
```

### 6. 函数定义

```python
# 基本函数
def greet(name, greeting="Hello"):  # 默认参数
    """函数的文档字符串（docstring）"""
    return f"{greeting}, {name}!"

print(greet("Alice"))           # Hello, Alice!
print(greet("Bob", "Hi"))       # Hi, Bob!
print(greet(name="Carol"))      # 关键字参数

# 可变参数 *args（类似Java的...）
def sum_all(*args):
    return sum(args)

print(sum_all(1, 2, 3, 4))  # 10

# 关键字参数 **kwargs（接收字典）
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25, city="Beijing")

# Lambda表达式（类似Java的箭头函数）
square = lambda x: x ** 2
print(square(5))  # 25

# 排序用lambda
students = [("Alice", 25), ("Bob", 20), ("Carol", 30)]
students.sort(key=lambda x: x[1])  # 按年龄排序
print(students)  # [('Bob', 20), ('Alice', 25), ('Carol', 30)]
```

### 7. 输入输出与文件操作

```python
# 用户输入
name = input("请输入你的名字: ")  # 返回字符串
age = int(input("请输入年龄: "))  # 需要类型转换

# 文件操作（with语句自动关闭，类似Java的try-with-resources）
# 写入
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, Python!\\n")
    f.write("第二行内容\\n")

# 读取
with open("output.txt", "r", encoding="utf-8") as f:
    content = f.read()          # 读取全部
    lines = f.readlines()       # 读取为列表

# 逐行读取（推荐大文件使用）
with open("output.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())     # strip()去除换行符
```

### 8. 异常处理

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"除零错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
else:
    print("没有异常时执行")
finally:
    print("无论有无异常都执行（类似Java的finally）")

# 自定义异常
class ValidationError(Exception):
    pass

def validate_age(age):
    if age < 0:
        raise ValidationError("年龄不能为负数")
```

### 9. 模块与包

```python
# 导入模块
import os
import sys

# 从模块导入特定函数
from math import sqrt, pi
print(sqrt(16))  # 4.0
print(pi)        # 3.141592653589793

# 导入并起别名
import numpy as np
import pandas as pd

# 查看模块路径
print(sys.path)

# 安装第三方包
# pip install requests
# pip install -r requirements.txt
```

---

## 💡 学习提示

**从Java到Python的思维转换：**

1. **类型声明** → 鸭子类型
2. **循环方式** → 迭代器优先
3. **空值检查** → 真值判断

**常见错误预防：**
- ⚠️ 缩进错误：使用4个空格，不要用Tab
- ⚠️ 可变对象默认参数陷阱

**IDE推荐：**
- PyCharm（功能最全，类似IntelliJ IDEA）
- VS Code + Python插件（轻量）
- Jupyter Notebook（数据探索）

---

## ✅ 今日产出检查清单

- [ ] 成功安装Python 3.9+并配置虚拟环境
- [ ] 运行第一个Python脚本（Hello World）
- [ ] 理解动态类型与静态类型的区别
- [ ] 掌握列表、字典的基本操作
- [ ] 理解Pythonic的代码风格
""",
                "chapter_type": "text",
                "duration_minutes": 120,
                "order_index": 1
            },
            {
                "title": "第2章：Python函数与面向对象编程",
                "content": """# Python函数与面向对象编程

## 🎯 学习目标
- 掌握Python函数高级特性
- 理解装饰器原理与应用
- 掌握类与面向对象编程
- 理解Python与Java OOP的差异

---

## 📖 核心内容

### 1. 函数是第一类公民

```python
# 函数可以赋值给变量
def greet(name):
    return f"Hello, {name}!"

say_hello = greet
print(say_hello("Alice"))  # Hello, Alice!

# 函数可以作为参数
def execute(func, arg):
    return func(arg)

result = execute(greet, "Bob")
print(result)  # Hello, Bob!

# 函数可以返回函数（闭包）
def make_multiplier(n):
    def multiplier(x):
        return x * n
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))  # 10
print(triple(5))  # 15
```

### 2. 装饰器详解

```python
import functools
import time

# 无参数装饰器
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("函数执行前")
        result = func(*args, **kwargs)
        print("函数执行后")
        return result
    return wrapper

# 使用装饰器
@my_decorator
def say_hello():
    print("Hello!")

# 带参数装饰器
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hi, {name}")

# 实际应用：计时装饰器
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} 耗时: {elapsed:.4f}秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"
```

### 3. 类与对象

```python
class Student:
    # 类属性
    school = "AI Academy"
    
    # 构造方法
    def __init__(self, name, age):
        self.name = name      # 实例属性
        self._age = age       # 约定：受保护属性
        self.__id = "S001"    # 名称改编：私有属性
    
    # 实例方法
    def introduce(self):
        return f"我是{self.name}，{self._age}岁"
    
    # 类方法
    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["age"])
    
    # 静态方法
    @staticmethod
    def is_adult(age):
        return age >= 18
    
    # 属性装饰器
    @property
    def age(self):
        return self._age
    
    @age.setter
    def age(self, value):
        if value < 0:
            raise ValueError("年龄不能为负数")
        self._age = value
    
    # 魔术方法
    def __str__(self):
        return f"Student(name={self.name}, age={self._age})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Student):
            return False
        return self.name == other.name

# 创建对象
stu = Student("Alice", 20)
print(stu.introduce())
```

### 4. 继承与多态

```python
class Person:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        raise NotImplementedError("子类必须实现")

class Teacher(Person):
    def __init__(self, name, subject):
        super().__init__(name)
        self.subject = subject
    
    def speak(self):
        return f"{self.name}老师说：今天学习{self.subject}"

class Student(Person):
    def __init__(self, name, grade):
        super().__init__(name)
        self.grade = grade
    
    def speak(self):
        return f"{self.name}同学说：我是{self.grade}年级学生"

# 多态
def let_them_speak(person):
    print(person.speak())

let_them_speak(Teacher("张", "Python"))
let_them_speak(Student("李", "大三"))
```

### 5. Python vs Java OOP对比

| 特性 | Java | Python |
|------|------|--------|
| 访问控制 | public/private/protected | 命名约定(_protected, __private) |
| 抽象类 | abstract class | abc模块 + @abstractmethod |
| 接口 | interface | 抽象基类 + 鸭子类型 |
| 多继承 | 不支持（接口可多实现） | 支持多继承 |
| 泛型 | 支持<T> | 类型提示(3.5+) |

---

## 💻 代码实践

**任务1: 数据验证装饰器**
```python
def validate_types(**types):
    """参数类型验证装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取函数参数名
            import inspect
            arg_names = list(inspect.signature(func).parameters.keys())
            
            # 验证位置参数
            for i, arg in enumerate(args):
                if i < len(arg_names) and arg_names[i] in types:
                    expected_type = types[arg_names[i]]
                    if not isinstance(arg, expected_type):
                        raise TypeError(f"{arg_names[i]}必须是{expected_type}")
            
            # 验证关键字参数
            for key, value in kwargs.items():
                if key in types and not isinstance(value, types[key]):
                    raise TypeError(f"{key}必须是{types[key]}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 使用
@validate_types(name=str, age=int)
def create_user(name, age):
    return {"name": name, "age": age}
```

---

## ✅ 检查点

- [ ] 掌握装饰器的定义和使用
- [ ] 理解类属性、实例属性、私有属性
- [ ] 能使用@property定义getter/setter
- [ ] 理解Python的多态和鸭子类型
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 2,
                "lab": {
                    "title": "实验：实现一个数据验证装饰器",
                    "description": "创建一个通用的参数类型验证装饰器，用于函数参数类型检查",
                    "starter_code": """import functools
import inspect

def validate_types(**types):
    \"\"\"
    参数类型验证装饰器
    用法: @validate_types(name=str, age=int, scores=list)
    \"\"\"
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # TODO: 获取函数参数名
            arg_names = list(inspect.signature(func).parameters.keys())
            
            # TODO: 验证位置参数类型
            # 遍历args，检查每个参数是否在types中且类型匹配
            
            # TODO: 验证关键字参数类型
            # 遍历kwargs，检查每个参数是否在types中且类型匹配
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 测试代码
@validate_types(name=str, age=int)
def create_user(name, age):
    return {"name": name, "age": age}

# 正常调用
print(create_user("Alice", 25))

# 错误调用（应该抛出TypeError）
try:
    print(create_user("Bob", "25"))  # age应该是int
except TypeError as e:
    print(f"捕获到错误: {e}")
""",
                    "solution_code": """import functools
import inspect

def validate_types(**types):
    \"\"\"
    参数类型验证装饰器
    用法: @validate_types(name=str, age=int, scores=list)
    \"\"\"
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数参数名
            arg_names = list(inspect.signature(func).parameters.keys())
            
            # 验证位置参数
            for i, arg in enumerate(args):
                if i < len(arg_names) and arg_names[i] in types:
                    expected_type = types[arg_names[i]]
                    if not isinstance(arg, expected_type):
                        raise TypeError(
                            f"参数'{arg_names[i]}'必须是{expected_type.__name__}，"
                            f"实际是{type(arg).__name__}"
                        )
            
            # 验证关键字参数
            for key, value in kwargs.items():
                if key in types and not isinstance(value, types[key]):
                    raise TypeError(
                        f"参数'{key}'必须是{types[key].__name__}，"
                        f"实际是{type(value).__name__}"
                    )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 测试代码
@validate_types(name=str, age=int)
def create_user(name, age):
    return {"name": name, "age": age}

# 正常调用
print(create_user("Alice", 25))

# 错误调用（应该抛出TypeError）
try:
    print(create_user("Bob", "25"))  # age应该是int
except TypeError as e:
    print(f"捕获到错误: {e}")
""",
                    "test_cases": [
                        {"description": "正常参数调用通过", "expected": "返回正确结果"},
                        {"description": "类型错误时抛出TypeError", "expected": "抛出异常"},
                        {"description": "错误信息包含参数名和期望类型", "expected": "错误信息完整"}
                    ],
                    "hints": [
                        "使用inspect.signature获取函数参数名",
                        "使用isinstance()进行类型检查",
                        "注意位置参数和关键字参数都要验证"
                    ]
                }
            },
            {
                "title": "第3章：NumPy基础 - 数组与矩阵运算",
                "content": """# NumPy基础：数组与矩阵运算

## 🎯 学习目标
- 理解ndarray内存结构与Java数组的本质区别
- 掌握向量化计算，性能提升10-100倍
- 理解并应用广播机制处理不同形状数组
- 完成矩阵运算实战

---

## 📖 核心内容

### 1. 为什么需要NumPy？

**Python原生列表的问题：**
```python
# Python列表 - 存储的是对象引用
python_list = [1, 2, 3, 4, 5]
# 内存布局: [指针→PyObject(1), 指针→PyObject(2), ...]

# NumPy数组的优势 - 连续内存块
import numpy as np
numpy_array = np.array([1, 2, 3, 4, 5])
# 内存布局: [1|2|3|4|5] - 原始C数组，无Python对象开销
```

**性能对比实测：**
```python
import time
import numpy as np

size = 1000000
python_list = list(range(size))
numpy_array = np.arange(size)

# Python方式
start = time.time()
result_python = [x ** 2 for x in python_list]
python_time = time.time() - start

# NumPy向量化方式
start = time.time()
result_numpy = numpy_array ** 2
numpy_time = time.time() - start

print(f"加速比: {python_time/numpy_time:.1f}倍")  # 典型结果: 50-100倍
```

### 2. ndarray核心属性

```python
import numpy as np

arr = np.array([[1, 2, 3], [4, 5, 6]])

print(f"形状 (shape): {arr.shape}")        # (2, 3) - 2行3列
print(f"维度 (ndim): {arr.ndim}")          # 2 - 二维数组
print(f"元素总数 (size): {arr.size}")      # 6
print(f"数据类型 (dtype): {arr.dtype}")    # int64
print(f"总字节数 (nbytes): {arr.nbytes}")  # 48 = 6*8
```

**数据类型对比表：**

| NumPy类型 | Java对应 | 字节数 | 范围 |
|-----------|----------|--------|------|
| int32 | int | 4 | -21亿 ~ 21亿 |
| int64 | long | 8 | 极大范围 |
| float32 | float | 4 | 单精度浮点 |
| float64 | double | 8 | 双精度浮点 |
| bool | boolean | 1 | True/False |

### 3. 数组创建方法

```python
import numpy as np

# 1. 从列表创建
arr1 = np.array([1, 2, 3])
arr2 = np.array([[1, 2], [3, 4]], dtype=np.float32)

# 2. 等差数列
arr3 = np.arange(0, 10, 2)        # [0, 2, 4, 6, 8]
arr4 = np.linspace(0, 1, 5)       # [0, 0.25, 0.5, 0.75, 1]

# 3. 特殊数组
zeros = np.zeros((3, 4))          # 3x4零矩阵
ones = np.ones((2, 3))            # 2x3全1矩阵
full = np.full((2, 2), 7)         # 2x2全7矩阵
identity = np.eye(3)              # 3x3单位矩阵

# 4. 随机数组
np.random.seed(42)                # 设置随机种子
rand_uniform = np.random.rand(3, 3)      # [0,1)均匀分布
rand_normal = np.random.randn(3, 3)      # 标准正态分布 N(0,1)
rand_int = np.random.randint(0, 10, (3, 3))  # [0,10)随机整数
```

### 4. 向量化操作 - 告别循环

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])

# 标量运算
print(a + 10)        # [11 12 13 14 15]
print(a * 2)         # [ 2  4  6  8 10]
print(a ** 2)        # [ 1  4  9 16 25]
print(np.sqrt(a))    # [1. 1.414 1.732 2. 2.236]

# 数组间运算
b = np.array([10, 20, 30, 40, 50])
print(a + b)         # [11 22 33 44 55]
print(a * b)         # [10 40 90 160 250]

# 统计函数
data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print(f"总和: {np.sum(data)}")           # 55
print(f"均值: {np.mean(data)}")          # 5.5
print(f"标准差: {np.std(data)}")         # 2.872...
print(f"最小值: {np.min(data)}")         # 1
print(f"最大值: {np.max(data)}")         # 10

# 多维数组统计
matrix = np.array([[1, 2, 3], [4, 5, 6]])
print(f"按列求和: {np.sum(matrix, axis=0)}")   # [5, 7, 9]
print(f"按行求和: {np.sum(matrix, axis=1)}")   # [6, 15]
```

### 5. 广播机制 (Broadcasting)

```python
import numpy as np

# 场景1: 数组 + 标量
a = np.array([1, 2, 3])
print(a + 10)  # 广播: [1,2,3] + [10,10,10] = [11,12,13]

# 场景2: 二维数组 + 一维数组
matrix = np.array([[1, 2, 3],
                   [4, 5, 6]])      # shape: (2, 3)
vector = np.array([10, 20, 30])      # shape: (3,)
print(matrix + vector)  # vector广播为[[10,20,30], [10,20,30]]

# 场景3: 列向量 + 行向量
col = np.array([[1], [2], [3]])      # shape: (3, 1)
row = np.array([10, 20, 30])         # shape: (3,)
print(col + row)  # 两个维度都扩展为(3,3)
```

### 6. 矩阵运算

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# 矩阵乘法
print("矩阵乘法 A @ B:")
print(A @ B)
# [[19, 22],
#  [43, 50]]

# 矩阵转置
print("A的转置:", A.T)

# 矩阵求逆
A_inv = np.linalg.inv(A)
print("A的逆矩阵:", A_inv)

# 行列式
det_A = np.linalg.det(A)
print(f"行列式: {det_A}")  # -2.0

# 特征值和特征向量
eigenvalues, eigenvectors = np.linalg.eig(A)
print(f"特征值: {eigenvalues}")

# 解线性方程组 Ax = b
A = np.array([[1, 2], [3, 4]])
b = np.array([5, 6])
x = np.linalg.solve(A, b)
print(f"解: x={x[0]:.2f}, y={x[1]:.2f}")
```

---

## 💻 代码实践

**任务1: 数据标准化函数**
```python
import numpy as np

def standardize_data(data):
    """
    数据标准化: (x - mean) / std
    这是机器学习数据预处理的标准操作
    """
    mean = np.mean(data)
    std = np.std(data)
    standardized = (data - mean) / std
    return standardized

# 测试
np.random.seed(42)
data = np.random.randn(1000) * 10 + 50
standardized = standardize_data(data)
print(f"标准化后 - 均值: {np.mean(standardized):.6f}, 标准差: {np.std(standardized):.6f}")
```

**任务2: 简单推荐系统**
```python
import numpy as np

def cosine_similarity(a, b):
    """计算余弦相似度"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 用户评分矩阵
ratings = np.array([
    [5, 1, 4, 2],   # 用户1: 喜欢动作片
    [2, 5, 3, 4],   # 用户2: 喜欢爱情片
    [4, 2, 5, 1],   # 用户3: 喜欢科幻片
])

# 计算相似度
sim_1_2 = cosine_similarity(ratings[0], ratings[1])
sim_1_3 = cosine_similarity(ratings[0], ratings[2])
print(f"用户1与用户3相似度更高: {sim_1_3:.3f} > {sim_1_2:.3f}")
```

---

## ✅ 检查点

- [ ] 理解ndarray与Python列表的性能差异
- [ ] 掌握向量化计算（避免Python循环）
- [ ] 理解广播机制并能应用
- [ ] 掌握基础矩阵运算
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 3,
                "lab": {
                    "title": "实验：向量化计算性能对比",
                    "description": "对比Python循环和NumPy向量化的性能差异，感受向量化的威力",
                    "starter_code": """import time
import numpy as np

def measure_performance():
    \"\"\"
    对比Python循环 vs NumPy向量化
    任务: 计算数组每个元素的平方加0.5倍自身
    \"\"\"
    size = 1000000
    
    # Python方式
    start = time.time()
    python_result = []
    for i in range(size):
        # TODO: 计算 i^2 + i*0.5
        pass
    python_time = time.time() - start
    
    # NumPy方式
    start = time.time()
    # TODO: 使用NumPy向量化计算
    arr = np.arange(size)
    numpy_result = None  # 完成计算
    numpy_time = time.time() - start
    
    print(f"Python循环: {python_time:.4f}秒")
    print(f"NumPy向量化: {numpy_time:.4f}秒")
    print(f"加速比: {python_time/numpy_time:.1f}倍")
    
    return python_time / numpy_time

# 运行测试
speedup = measure_performance()
assert speedup > 10, "加速比应该大于10倍"
print("✅ 任务完成 - 感受向量化的威力")
""",
                    "solution_code": """import time
import numpy as np

def measure_performance():
    \"\"\"
    对比Python循环 vs NumPy向量化
    任务: 计算数组每个元素的平方加0.5倍自身
    \"\"\"
    size = 1000000
    
    # Python方式
    start = time.time()
    python_result = []
    for i in range(size):
        python_result.append(i ** 2 + i * 0.5)
    python_time = time.time() - start
    
    # NumPy方式
    start = time.time()
    arr = np.arange(size)
    numpy_result = arr ** 2 + arr * 0.5
    numpy_time = time.time() - start
    
    print(f"Python循环: {python_time:.4f}秒")
    print(f"NumPy向量化: {numpy_time:.4f}秒")
    print(f"加速比: {python_time/numpy_time:.1f}倍")
    
    return python_time / numpy_time

# 运行测试
speedup = measure_performance()
assert speedup > 10, "加速比应该大于10倍"
print("✅ 任务完成 - 感受向量化的威力")
""",
                    "test_cases": [
                        {"description": "向量化计算结果正确", "expected": "结果数组正确"},
                        {"description": "加速比大于10倍", "expected": "speedup > 10"}
                    ],
                    "hints": [
                        "NumPy使用arr ** 2计算平方",
                        "向量化操作会自动应用到每个元素",
                        "对比时注意结果一致性"
                    ]
                }
            },
            {
                "title": "第4章：Pandas入门 - 从SQL视角理解DataFrame",
                "content": """# Pandas入门：从SQL视角理解DataFrame

## 🎯 学习目标
- 理解DataFrame与SQL表的对应关系
- 掌握Pandas数据读取（CSV/Excel/JSON/SQL）
- 掌握基础查询（loc/iloc/条件筛选）
- 能够用Pandas替代简单的SQL查询

---

## 📖 核心内容

### 1. DataFrame vs SQL表 - 概念对照

| SQL概念 | Pandas对应 | 说明 |
|---------|-----------|------|
| 表 (Table) | DataFrame | 二维数据结构，有行列 |
| 行 (Row) | Index | 默认整数索引，可自定义 |
| 列 (Column) | Column | 列名就是字段名 |
| 数据类型 | dtype | int64, float64, object等 |
| 主键 | Index | 可设置唯一索引 |
| NULL | NaN | Not a Number，缺失值标记 |

### 2. 创建DataFrame

```python
import pandas as pd

# 从字典创建（类似INSERT VALUES）
data = {
    'user_id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': [25, 30, 35, 28, 32],
    'city': ['Beijing', 'Shanghai', 'Beijing', 'Shenzhen', 'Shanghai'],
    'salary': [8000.0, 12000.0, 15000.0, 10000.0, 11000.0]
}
df = pd.DataFrame(data)

# 从NumPy数组创建
import numpy as np
data = np.random.randn(1000, 5)
df = pd.DataFrame(data, columns=['A', 'B', 'C', 'D', 'E'])
```

### 3. 数据读取

```python
# 读取CSV
df = pd.read_csv('data.csv', encoding='utf-8')

# 从SQL数据库读取
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://user:password@host/dbname')
df = pd.read_sql("SELECT * FROM users WHERE age > 25", engine)

# 读取Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')
```

### 4. 数据查询

```python
# 基础信息
df.head(10)      # 查看前10行
df.info()        # 数据类型和缺失值
df.describe()    # 统计摘要

# 条件筛选（类似SQL WHERE）
df[df['age'] > 25]  # WHERE age > 25
df[(df['age'] > 25) & (df['city'] == 'Beijing')]  # AND条件
df[df['city'].isin(['Beijing', 'Shanghai'])]  # IN条件

# loc - 按标签选择
df.loc[0:5, ['name', 'age']]  # 行0-5，列name和age
df.loc[df['age'] > 25, ['name', 'salary']]  # 条件+选择列

# iloc - 按位置选择
df.iloc[0:5, 0:3]  # 前5行前3列
```

### 5. 数据清洗

```python
# 处理缺失值
df.isnull().sum()              # 查看每列缺失值数量
df.dropna()                    # 删除包含缺失值的行
df.fillna(0)                   # 用0填充缺失值

# 处理重复值
df.duplicated().sum()          # 查看重复行数
df.drop_duplicates()           # 删除重复行

# 数据类型转换
df['age'] = df['age'].astype(int)
```

---

## ✅ 检查点

- [ ] 理解DataFrame与SQL表的对应关系
- [ ] 掌握基础数据读取和查询
- [ ] 能进行简单的数据清洗
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 4,
                "lab": {
                    "title": "实验：CSV数据处理与编码处理",
                    "description": "学习如何正确读取CSV文件，处理各种编码问题，包括UTF-8、GBK等常见编码",
                    "starter_code": """import pandas as pd
import os

def read_csv_with_encoding(filepath):
    """
    读取CSV文件，自动检测并处理编码问题
    需要处理的编码: utf-8, gbk, latin-1
    
    Args:
        filepath: CSV文件路径
    
    Returns:
        DataFrame对象
    """
    # TODO: 实现编码检测和读取
    # 1. 尝试用utf-8读取
    # 2. 如果失败，尝试gbk
    # 3. 如果还失败，尝试latin-1
    pass


def process_csv_data(filepath):
    """
    完整的CSV处理流程
    - 读取数据
    - 显示基本信息
    - 处理缺失值
    - 保存处理后的数据
    """
    # TODO: 实现完整处理流程
    pass


# 测试代码
if __name__ == "__main__":
    # 创建测试数据
    test_data = """姓名,年龄,城市,收入
张三,25,北京,8000
李四,30,上海,12000
王五,35,广州,15000
赵六,28,深圳,10000"""
    
    # 保存为不同编码的文件
    with open('test_utf8.csv', 'w', encoding='utf-8') as f:
        f.write(test_data)
    
    with open('test_gbk.csv', 'w', encoding='gbk') as f:
        f.write(test_data)
    
    # TODO: 测试读取函数
    # df = read_csv_with_encoding('test_utf8.csv')
    # print(df)
""",
                    "solution_code": """import pandas as pd
import os

def read_csv_with_encoding(filepath):
    """
    读取CSV文件，自动检测并处理编码问题
    需要处理的编码: utf-8, gbk, latin-1
    """
    encodings = ['utf-8', 'gbk', 'latin-1', 'utf-16']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            print(f"成功使用 {encoding} 编码读取文件")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"使用 {encoding} 失败: {e}")
            continue
    
    raise ValueError(f"无法使用已知编码读取文件: {filepath}")


def process_csv_data(filepath, output_path='processed.csv'):
    """
    完整的CSV处理流程
    """
    # 1. 读取数据
    df = read_csv_with_encoding(filepath)
    
    # 2. 显示基本信息
    print("=" * 50)
    print("数据基本信息:")
    print(f"行数: {len(df)}")
    print(f"列数: {len(df.columns)}")
    print(f"列名: {list(df.columns)}")
    print("\\n数据类型:")
    print(df.dtypes)
    
    # 3. 缺失值统计
    print("\\n缺失值统计:")
    print(df.isnull().sum())
    
    # 4. 处理缺失值（删除完全缺失的行）
    before_count = len(df)
    df = df.dropna(how='all')
    after_count = len(df)
    print(f"\\n删除完全缺失的行: {before_count - after_count} 行")
    
    # 5. 数值列的统计信息
    print("\\n数值列统计:")
    print(df.describe())
    
    # 6. 保存处理后的数据（统一使用utf-8-sig以兼容Excel）
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\\n处理后的数据已保存: {output_path}")
    
    return df


# 测试代码
if __name__ == "__main__":
    # 创建测试数据
    test_data = """姓名,年龄,城市,收入
张三,25,北京,8000
李四,30,上海,12000
王五,35,广州,15000
赵六,28,深圳,10000"""
    
    # 保存为不同编码的文件
    with open('test_utf8.csv', 'w', encoding='utf-8') as f:
        f.write(test_data)
    
    with open('test_gbk.csv', 'w', encoding='gbk') as f:
        f.write(test_data)
    
    # 测试读取函数
    print("=== 测试UTF-8文件 ===")
    df1 = read_csv_with_encoding('test_utf8.csv')
    print(df1)
    
    print("\\n=== 测试GBK文件 ===")
    df2 = read_csv_with_encoding('test_gbk.csv')
    print(df2)
    
    # 测试完整处理流程
    print("\\n=== 测试完整处理流程 ===")
    df_processed = process_csv_data('test_utf8.csv', 'output.csv')
""",
                    "test_cases": [
                        {"description": "能正确读取UTF-8编码的CSV", "expected": "DataFrame读取成功"},
                        {"description": "能正确读取GBK编码的CSV", "expected": "DataFrame读取成功"},
                        {"description": "处理后的数据保存为UTF-8-SIG格式", "expected": "文件可正常打开"},
                        {"description": "显示正确的数据基本信息", "expected": "行列数正确"}
                    ],
                    "validation_rules": [
                        {"type": "function_exists", "name": "read_csv_with_encoding"},
                        {"type": "function_exists", "name": "process_csv_data"},
                        {"type": "code_contains", "pattern": "encoding"},
                        {"type": "code_contains", "pattern": "pd.read_csv"}
                    ]
                }
            },
            {
                "title": "第5章：Pandas高级数据操作",
                "content": """# Pandas高级数据操作

## 🎯 学习目标
- 掌握数据清洗技巧
- 学会数据转换
- 掌握GroupBy分组聚合
- 理解窗口函数

---

## 📖 核心内容

### 1. 数据清洗进阶

```python
import pandas as pd
import numpy as np

# 字符串处理
df['name_upper'] = df['name'].str.upper()
df['email_domain'] = df['email'].str.split('@').str[1]
df['name'].str.contains('li', case=False)  # LIKE '%li%'

# 日期处理
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['dayofweek'] = df['date'].dt.dayofweek

# 数据替换
df['gender'].replace({'M': 'Male', 'F': 'Female'}, inplace=True)
df['city'].map({'Beijing': '北京', 'Shanghai': '上海'})
```

### 2. 数据转换

```python
# apply - 应用函数
df['age_group'] = df['age'].apply(lambda x: '青年' if x < 30 else '中年')

# 多列apply
df['full_name'] = df.apply(lambda row: f"{row['first_name']} {row['last_name']}", axis=1)

# 条件赋值
df.loc[df['age'] > 30, 'salary'] = df['salary'] * 1.1  # 年龄>30加薪10%
```

### 3. GroupBy分组聚合

```python
# 基础分组
result = df.groupby('city')['salary'].mean()  # 每个城市的平均工资

# 多列聚合
city_stats = df.groupby('city').agg({
    'age': ['mean', 'min', 'max'],
    'salary': ['mean', 'sum', 'count']
})

# 多列分组
df.groupby(['city', 'gender']).size()  # 每个城市男女数量

# 透视表（类似Excel PivotTable）
pivot = df.pivot_table(
    values='salary',
    index='city',
    columns='gender',
    aggfunc='mean'
)
```

### 4. 数据合并

```python
# merge - 类似SQL JOIN
merged = pd.merge(df1, df2, on='key', how='inner')   # 内连接
merged = pd.merge(df1, df2, on='key', how='left')    # 左连接

# concat - 纵向拼接
df_combined = pd.concat([df1, df2], ignore_index=True)
```

---

## 💻 实战案例

```python
# 从数仓导出数据并进行分析
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:password@warehouse:5432/prod_db')

sql = """
SELECT user_id, user_name, age, city, total_order_amount
FROM dim_user
WHERE registration_date >= '2024-01-01'
LIMIT 5000
"""

df = pd.read_sql(sql, engine)

# 分析
print("城市分布（Top 10）:")
print(df['city'].value_counts().head(10))

print("\\n高价值用户（消费>10000）:")
high_value = df[df['total_order_amount'] > 10000]
print(f"数量: {len(high_value)}")
```

---

## ✅ 检查点

- [ ] 掌握GroupBy分组聚合
- [ ] 能进行复杂的数据清洗
- [ ] 理解透视表和交叉表
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 5,
                "lab": {
                    "title": "实验：Pandas数据转换与清洗",
                    "description": "学习使用Pandas进行数据清洗、类型转换、数据格式化处理",
                    "starter_code": """import pandas as pd
import numpy as np

def clean_and_transform_data(df):
    """
    数据清洗和转换函数
    包括: 类型转换、缺失值处理、异常值检测、格式标准化
    
    Args:
        df: 原始DataFrame
    
    Returns:
        清洗后的DataFrame
    """
    # 创建副本避免修改原始数据
    df_clean = df.copy()
    
    # TODO: 实现数据清洗逻辑
    # 1. 数据类型转换 - 将年龄转为整数，收入转为浮点数
    
    # 2. 处理缺失值 - 数值列用中位数填充，文本列用众数填充
    
    # 3. 异常值检测 - 使用IQR方法检测异常值
    
    # 4. 字符串标准化 - 统一大小写、去除空格
    
    # 5. 日期解析 - 将日期字符串转为datetime对象
    
    return df_clean


def transform_categories(df, column, mapping):
    """
    类别数据转换
    例如: 将城市名称映射为区域
    
    Args:
        df: DataFrame
        column: 需要转换的列名
        mapping: 映射字典
    
    Returns:
        转换后的DataFrame
    """
    # TODO: 实现类别映射
    pass


def create_derived_features(df):
    """
    创建派生特征
    例如: 根据年龄计算年龄段，根据收入计算收入水平
    """
    # TODO: 创建以下派生特征:
    # 1. 年龄段 (青年/中年/老年)
    # 2. 收入水平 (低/中/高)
    # 3. 城市等级 (一线/二线/三线)
    
    return df


# 测试数据
test_data = {
    '姓名': ['张三', '李四', '王五', '赵六', '  孙七  '],
    '年龄': ['25', '30', 'N/A', '28', '35'],
    '城市': ['北京', '上海', '广州', '深圳', '北京'],
    '收入': ['8000', '12000', '15000', 'invalid', '10000'],
    '入职日期': ['2020-01-15', '2019/03/20', '2021.06.10', '2020-12-01', '2018-08-08']
}

df_test = pd.DataFrame(test_data)
print("原始数据:")
print(df_test)
print("\\n数据类型:")
print(df_test.dtypes)

# TODO: 调用清洗函数
# df_cleaned = clean_and_transform_data(df_test)
# print("\\n清洗后数据:")
# print(df_cleaned)
""",
                    "solution_code": """import pandas as pd
import numpy as np

def clean_and_transform_data(df):
    """
    数据清洗和转换函数
    """
    df_clean = df.copy()
    
    # 1. 数据类型转换
    # 将年龄转为数值，无法转换的设为NaN
    df_clean['年龄'] = pd.to_numeric(df_clean['年龄'], errors='coerce')
    # 将收入转为数值
    df_clean['收入'] = pd.to_numeric(df_clean['收入'], errors='coerce')
    
    # 2. 处理缺失值
    # 数值列用中位数填充
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        median_val = df_clean[col].median()
        df_clean[col].fillna(median_val, inplace=True)
    
    # 文本列用众数填充
    text_cols = df_clean.select_dtypes(include=['object']).columns
    for col in text_cols:
        if col != '入职日期':  # 日期单独处理
            mode_val = df_clean[col].mode()
            if len(mode_val) > 0:
                df_clean[col].fillna(mode_val[0], inplace=True)
    
    # 3. 异常值检测 (使用IQR方法)
    for col in ['年龄', '收入']:
        if col in df_clean.columns:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # 标记异常值
            outliers = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
            if outliers.sum() > 0:
                print(f"列 '{col}' 发现 {outliers.sum()} 个异常值")
                # 用边界值替换异常值
                df_clean.loc[df_clean[col] < lower_bound, col] = lower_bound
                df_clean.loc[df_clean[col] > upper_bound, col] = upper_bound
    
    # 4. 字符串标准化
    for col in text_cols:
        if df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str).str.strip().str.title()
    
    # 5. 日期解析 - 智能识别多种日期格式
    def parse_date(date_str):
        """尝试多种日期格式解析"""
        if pd.isna(date_str):
            return pd.NaT
        
        formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%d-%m-%Y', '%m/%d/%Y']
        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue
        return pd.to_datetime(date_str, errors='coerce')
    
    if '入职日期' in df_clean.columns:
        df_clean['入职日期'] = df_clean['入职日期'].apply(parse_date)
        df_clean['入职年份'] = df_clean['入职日期'].dt.year
        df_clean['入职月份'] = df_clean['入职日期'].dt.month
    
    return df_clean


def transform_categories(df, column, mapping):
    """
    类别数据转换
    """
    df_result = df.copy()
    df_result[f'{column}_区域'] = df_result[column].map(mapping)
    return df_result


def create_derived_features(df):
    """
    创建派生特征
    """
    df_new = df.copy()
    
    # 1. 年龄段
    df_new['年龄段'] = pd.cut(
        df_new['年龄'],
        bins=[0, 25, 35, 50, 100],
        labels=['青年', '中青年', '中年', '老年']
    )
    
    # 2. 收入水平
    income_median = df_new['收入'].median()
    df_new['收入水平'] = pd.cut(
        df_new['收入'],
        bins=[0, income_median * 0.7, income_median * 1.3, float('inf')],
        labels=['低', '中', '高']
    )
    
    # 3. 城市等级
    city_mapping = {
        '北京': '一线', '上海': '一线', '广州': '一线', '深圳': '一线',
        '杭州': '二线', '南京': '二线', '成都': '二线', '武汉': '二线',
        '西安': '三线', '郑州': '三线', '长沙': '三线'
    }
    df_new['城市等级'] = df_new['城市'].map(city_mapping).fillna('其他')
    
    return df_new


# 测试数据
test_data = {
    '姓名': ['张三', '李四', '王五', '赵六', '  孙七  '],
    '年龄': ['25', '30', 'N/A', '28', '35'],
    '城市': ['北京', '上海', '广州', '深圳', '北京'],
    '收入': ['8000', '12000', '15000', 'invalid', '10000'],
    '入职日期': ['2020-01-15', '2019/03/20', '2021.06.10', '2020-12-01', '2018-08-08']
}

df_test = pd.DataFrame(test_data)
print("原始数据:")
print(df_test)
print("\\n数据类型:")
print(df_test.dtypes)

# 调用清洗函数
df_cleaned = clean_and_transform_data(df_test)
print("\\n清洗后数据:")
print(df_cleaned)
print("\\n清洗后数据类型:")
print(df_cleaned.dtypes)

# 创建派生特征
df_final = create_derived_features(df_cleaned)
print("\\n最终数据 (含派生特征):")
print(df_final)
print("\\n数据统计:")
print(df_final.describe())
""",
                    "test_cases": [
                        {"description": "能正确转换数据类型", "expected": "年龄转为int，收入转为float"},
                        {"description": "能正确处理缺失值", "expected": "无NaN值或已合理填充"},
                        {"description": "能正确解析多种日期格式", "expected": "日期列转为datetime类型"},
                        {"description": "能正确创建派生特征", "expected": "新增年龄段、收入水平列"}
                    ],
                    "validation_rules": [
                        {"type": "function_exists", "name": "clean_and_transform_data"},
                        {"type": "function_exists", "name": "create_derived_features"},
                        {"type": "code_contains", "pattern": "pd.to_numeric"},
                        {"type": "code_contains", "pattern": "fillna"},
                        {"type": "code_contains", "pattern": "pd.cut"}
                    ]
                }
            },
            {
                "title": "第6章：Python ETL项目实战",
                "content": """# Python ETL项目实战

## 🎯 学习目标
- 整合Python、NumPy、Pandas知识
- 完成完整ETL流程
- 输出项目文档

---

## 📖 项目需求

设计一个完整的ETL流程：
1. **Extract**: 从CSV/数据库抽取数据
2. **Transform**: 数据清洗、转换、聚合
3. **Load**: 加载到目标数据库/文件
4. **Report**: 生成数据报表

---

## 💻 项目代码框架

```python
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self, source_conn, target_conn):
        self.source_engine = create_engine(source_conn)
        self.target_engine = create_engine(target_conn)
    
    def extract(self, query):
        \"\"\"数据抽取\"\"\"
        logger.info("开始抽取数据...")
        df = pd.read_sql(query, self.source_engine)
        logger.info(f"抽取完成: {len(df)} 行")
        return df
    
    def transform(self, df):
        \"\"\"数据转换\"\"\"
        logger.info("开始数据转换...")
        
        # 清洗
        df = df.dropna(subset=['user_id'])
        df = df.drop_duplicates()
        
        # 转换
        df['age_group'] = pd.cut(df['age'], 
                                  bins=[0, 18, 35, 50, 100],
                                  labels=['未成年', '青年', '中年', '老年'])
        
        # 聚合
        summary = df.groupby('age_group').agg({
            'user_id': 'count',
            'order_amount': ['sum', 'mean']
        })
        
        logger.info("转换完成")
        return df, summary
    
    def load(self, df, table_name):
        \"\"\"数据加载\"\"\"
        logger.info(f"开始加载到 {table_name}...")
        df.to_sql(table_name, self.target_engine, 
                  if_exists='replace', index=False)
        logger.info("加载完成")
    
    def run(self, query, target_table):
        \"\"\"执行完整ETL流程\"\"\"
        df = self.extract(query)
        df_clean, summary = self.transform(df)
        self.load(df_clean, target_table)
        return summary

# 使用
if __name__ == "__main__":
    pipeline = ETLPipeline(
        source_conn="mysql://user:pass@source/db",
        target_conn="postgresql://user:pass@target/db"
    )
    
    summary = pipeline.run(
        query="SELECT * FROM orders WHERE date >= '2024-01-01'",
        target_table="cleaned_orders"
    )
    
    print(summary)
```

---

## ✅ 项目检查点

- [ ] 完整的Extract-Transform-Load流程
- [ ] 异常处理和日志记录
- [ ] 数据质量检查
- [ ] 项目文档和README
""",
                "chapter_type": "lab",
                "duration_minutes": 180,
                "order_index": 6,
                "lab": {
                    "title": "完整ETL项目开发",
                    "description": "开发一个完整的ETL数据处理管道，包含数据抽取、清洗转换、加载、报表生成",
                    "starter_code": """import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETLPipeline:
    \"\"\"
    ETL数据处理管道
    支持从多种数据源抽取、转换、加载数据
    \"\"\"
    
    def __init__(self):
        self.source_data = None
        self.transformed_data = None
    
    def extract_from_csv(self, filepath):
        \"\"\"
        从CSV文件抽取数据
        TODO: 实现CSV读取，处理编码问题
        \"\"\"
        pass
    
    def transform(self, df):
        \"\"\"
        数据转换
        TODO: 实现以下转换:
        1. 删除缺失值
        2. 数据类型转换
        3. 添加新列（如年龄分组）
        4. 异常值处理
        \"\"\"
        pass
    
    def aggregate(self, df):
        \"\"\"
        数据聚合
        TODO: 按指定维度分组统计
        \"\"\"
        pass
    
    def load_to_csv(self, df, filepath):
        \"\"\"
        加载到CSV
        TODO: 保存处理后的数据
        \"\"\"
        pass
    
    def generate_report(self, summary_stats):
        \"\"\"
        生成数据报表
        TODO: 输出关键指标统计
        \"\"\"
        pass
    
    def run(self, input_file, output_file):
        \"\"\"执行完整ETL流程\"\"\"
        # TODO: 调用上述方法完成完整流程
        pass


# 测试数据生成
def generate_test_data(filepath):
    \"\"\"生成测试数据\"\"\"
    np.random.seed(42)
    n = 1000
    
    data = {
        'user_id': range(1, n+1),
        'name': [f'User_{i}' for i in range(1, n+1)],
        'age': np.random.randint(18, 80, n),
        'city': np.random.choice(['北京', '上海', '广州', '深圳'], n),
        'salary': np.random.normal(10000, 3000, n).astype(int),
        'order_amount': np.random.exponential(500, n),
    }
    
    df = pd.DataFrame(data)
    # 添加一些缺失值和异常值
    df.loc[np.random.choice(n, 10, replace=False), 'age'] = np.nan
    df.loc[np.random.choice(n, 5, replace=False), 'salary'] = -1000  # 异常值
    
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"测试数据已生成: {filepath}")


if __name__ == "__main__":
    # 生成测试数据
    generate_test_data('test_data.csv')
    
    # TODO: 运行ETL流程
    # pipeline = ETLPipeline()
    # pipeline.run('test_data.csv', 'output.csv')
""",
                    "solution_code": """import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETLPipeline:
    \"\"\"
    ETL数据处理管道
    支持从多种数据源抽取、转换、加载数据
    \"\"\"
    
    def __init__(self):
        self.source_data = None
        self.transformed_data = None
    
    def extract_from_csv(self, filepath):
        \"\"\"从CSV文件抽取数据\"\"\"
        logger.info(f"开始从 {filepath} 抽取数据...")
        df = pd.read_csv(filepath, encoding='utf-8')
        logger.info(f"抽取完成: {len(df)} 行, {len(df.columns)} 列")
        self.source_data = df
        return df
    
    def transform(self, df):
        \"\"\"数据转换\"\"\"
        logger.info("开始数据转换...")
        
        # 1. 删除缺失值
        before_count = len(df)
        df = df.dropna(subset=['user_id', 'age', 'salary'])
        after_count = len(df)
        logger.info(f"删除缺失值: {before_count - after_count} 行")
        
        # 2. 数据类型转换
        df['user_id'] = df['user_id'].astype(int)
        df['age'] = df['age'].astype(int)
        df['salary'] = df['salary'].astype(float)
        df['order_amount'] = df['order_amount'].astype(float)
        
        # 3. 异常值处理（工资不能为负）
        abnormal_count = len(df[df['salary'] < 0])
        df = df[df['salary'] >= 0]
        logger.info(f"删除异常值: {abnormal_count} 行")
        
        # 4. 添加新列：年龄分组
        df['age_group'] = pd.cut(df['age'], 
                                  bins=[0, 25, 35, 45, 100],
                                  labels=['青年', '中青年', '中年', '老年'])
        
        # 5. 添加新列：消费等级
        df['spending_level'] = pd.cut(df['order_amount'],
                                       bins=[0, 200, 500, 1000, float('inf')],
                                       labels=['低', '中', '高', '超高'])
        
        self.transformed_data = df
        logger.info("数据转换完成")
        return df
    
    def aggregate(self, df):
        \"\"\"数据聚合\"\"\"
        logger.info("开始数据聚合...")
        
        # 按城市统计
        city_stats = df.groupby('city').agg({
            'user_id': 'count',
            'salary': ['mean', 'median', 'std'],
            'order_amount': ['sum', 'mean']
        }).round(2)
        
        # 按年龄分组统计
        age_stats = df.groupby('age_group').agg({
            'user_id': 'count',
            'salary': 'mean',
            'order_amount': 'mean'
        }).round(2)
        
        return {'city_stats': city_stats, 'age_stats': age_stats}
    
    def load_to_csv(self, df, filepath):
        \"\"\"加载到CSV\"\"\"
        logger.info(f"开始保存到 {filepath}...")
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info("保存完成")
    
    def generate_report(self, summary_stats):
        \"\"\"生成数据报表\"\"\"
        report = []
        report.append("=" * 50)
        report.append("ETL数据处理报表")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 50)
        report.append("")
        
        report.append("【城市统计】")
        report.append(str(summary_stats['city_stats']))
        report.append("")
        
        report.append("【年龄分组统计】")
        report.append(str(summary_stats['age_stats']))
        report.append("")
        
        report_text = "\\n".join(report)
        
        # 保存报表
        with open('report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info("报表已生成: report.txt")
        return report_text
    
    def run(self, input_file, output_file):
        \"\"\"执行完整ETL流程\"\"\"
        logger.info("=" * 50)
        logger.info("ETL流程开始")
        logger.info("=" * 50)
        
        # Extract
        df = self.extract_from_csv(input_file)
        
        # Transform
        df_clean = self.transform(df)
        
        # Aggregate
        summary = self.aggregate(df_clean)
        
        # Load
        self.load_to_csv(df_clean, output_file)
        
        # Report
        report = self.generate_report(summary)
        
        logger.info("=" * 50)
        logger.info("ETL流程完成")
        logger.info("=" * 50)
        
        return summary, report


# 测试数据生成
def generate_test_data(filepath):
    \"\"\"生成测试数据\"\"\"
    np.random.seed(42)
    n = 1000
    
    data = {
        'user_id': range(1, n+1),
        'name': [f'User_{i}' for i in range(1, n+1)],
        'age': np.random.randint(18, 80, n),
        'city': np.random.choice(['北京', '上海', '广州', '深圳'], n),
        'salary': np.random.normal(10000, 3000, n).astype(int),
        'order_amount': np.random.exponential(500, n),
    }
    
    df = pd.DataFrame(data)
    # 添加一些缺失值和异常值
    df.loc[np.random.choice(n, 10, replace=False), 'age'] = np.nan
    df.loc[np.random.choice(n, 5, replace=False), 'salary'] = -1000
    
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"测试数据已生成: {filepath}")


if __name__ == "__main__":
    # 生成测试数据
    generate_test_data('test_data.csv')
    
    # 运行ETL流程
    pipeline = ETLPipeline()
    summary, report = pipeline.run('test_data.csv', 'cleaned_data.csv')
    
    print("\\n" + "=" * 50)
    print("处理结果预览:")
    print(report)
""",
                    "test_cases": [
                        {"description": "能正确读取CSV数据", "expected": "数据读取成功"},
                        {"description": "能正确清洗数据（缺失值、异常值）", "expected": "数据清洗成功"},
                        {"description": "能正确聚合数据", "expected": "分组统计正确"},
                        {"description": "能生成报表文件", "expected": "report.txt已生成"}
                    ],
                    "hints": [
                        "使用pd.read_csv读取数据",
                        "使用dropna删除缺失值",
                        "使用groupby进行分组聚合",
                        "注意处理异常值（如负数工资）"
                    ]
                }
            },
            {
                "title": "第7章：Phase 1 复习与总结",
                "content": """# Phase 1: Python基础复习与总结

## 🎯 本章目标
- 复习2周学习内容
- 整理Python与Java的差异
- 准备进入数学基础阶段

---

## 📚 知识图谱

```
Phase 1: Python基础 (2周/14天)
├── Week 1: Python语法入门
│   ├── Day 1: Python快速上手
│   ├── Day 2: 函数与类
│   └── Day 3-4: NumPy基础
├── Week 2: 数据处理
│   ├── Day 5-7: Pandas数据处理
│   ├── Day 8-9: 可视化与性能
│   └── Day 10-14: 项目实战
```

---

## 🔑 核心概念对比

### Python vs Java

| 概念 | Python | Java |
|------|--------|------|
| 类型系统 | 动态类型 | 静态类型 |
| 语法 | 缩进定义代码块 | 大括号定义代码块 |
| 代码执行 | 解释执行 | 编译执行 |
| OOP | 多继承、鸭子类型 | 单继承、接口 |
| 函数 | 一等公民 | 非一等公民 |

### NumPy vs Java数组

| 特性 | NumPy ndarray | Java数组 |
|------|---------------|----------|
| 内存布局 | 连续内存 | 对象引用 |
| 运算 | 向量化 | 循环 |
| 性能 | 快10-100倍 | 较慢 |
| 广播 | 支持 | 不支持 |

---

## ✅ Phase 1 检查清单

- [ ] 能独立编写Python数据处理脚本
- [ ] 能用Pandas完成复杂数据操作
- [ ] 理解Python与Java的差异
- [ ] 完成ETL项目并提交到GitHub
- [ ] 能使用NumPy进行向量化计算

---

## 🚀 下一步

进入 **Phase 2: 数学基础**
- 线性代数基础
- 矩阵分解与PCA
- 概率与统计
- 梯度下降优化
""",
                "chapter_type": "text",
                "duration_minutes": 60,
                "order_index": 7
            }
        ]
    },
    {
        "title": "Phase 2: 数学基础（1周/7天）",
        "description": "学习AI必需的数学基础：线性代数、矩阵分解、概率统计、梯度下降。精简高效，直击AI应用核心。",
        "level": "intermediate",
        "category": "math",
        "duration_hours": 14,
        "order_index": 2,
        "chapters": [
            {
                "title": "第8章：线性代数基础 - 向量与矩阵",
                "content": """# 线性代数基础：向量与矩阵

## 🎯 学习目标
- 理解向量运算
- 掌握矩阵乘法
- 完成NumPy实现
- 理解数据矩阵的含义

---

## 📖 核心内容

### 1. 向量的概念

```python
import numpy as np

# 行向量
row_vector = np.array([1, 2, 3])

# 列向量
col_vector = np.array([[1], [2], [3]])

# 向量运算
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# 向量加法
print(a + b)  # [5, 7, 9]

# 点积（内积）
dot_product = np.dot(a, b)  # 1*4 + 2*5 + 3*6 = 32

# 向量的模（长度）
norm = np.linalg.norm(a)  # sqrt(1^2 + 2^2 + 3^2) = 3.74...
```

### 2. 矩阵基础

```python
# 创建矩阵
A = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

# 矩阵的形状
print(A.shape)  # (3, 3) - 3行3列

# 特殊矩阵
I = np.eye(3)  # 单位矩阵
Z = np.zeros((3, 3))  # 零矩阵
O = np.ones((3, 3))  # 全1矩阵
```

### 3. 矩阵乘法

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# 矩阵乘法 (不是元素相乘!)
C = A @ B  # 或 np.dot(A, B)
# [[19, 22],
#  [43, 50]]

# 矩阵乘法的意义：线性变换
# 每个矩阵都代表一种变换（旋转、缩放、投影等）
```

### 4. 数据矩阵

在机器学习中，数据通常表示为矩阵：
- **行** = 样本（samples）
- **列** = 特征（features）

```python
# 示例：房价预测数据
# 每行是一个房子，每列是一个特征
houses = np.array([
    [100, 3, 10],   # 面积100平, 3室, 距离地铁10km, 价格300万
    [120, 4, 5],    # 面积120平, 4室, 距离地铁5km, 价格450万
    [80, 2, 15],    # 面积80平, 2室, 距离地铁15km, 价格200万
])

# houses.shape = (3, 3) - 3个样本，3个特征
```

---

## ✅ 检查点

- [ ] 理解向量和矩阵的基本运算
- [ ] 掌握矩阵乘法规则
- [ ] 理解数据矩阵的含义（行=样本，列=特征）
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 1
            },
            {
                "title": "第9章：矩阵分解与PCA降维",
                "content": """# 矩阵分解与PCA降维

## 🎯 学习目标
- 理解SVD原理
- 掌握PCA降维
- 完成实战应用

---

## 📖 核心内容

### 1. SVD奇异值分解

```python
import numpy as np

A = np.array([[1, 2], [3, 4], [5, 6]])

# SVD分解: A = U * Σ * V^T
U, S, Vt = np.linalg.svd(A, full_matrices=False)

print("U的形状:", U.shape)    # (3, 2)
print("奇异值:", S)           # (2,)
print("Vt的形状:", Vt.shape)  # (2, 2)

# 重构
Sigma = np.diag(S)
A_reconstructed = U @ Sigma @ Vt
print("重构误差:", np.allclose(A, A_reconstructed))
```

### 2. PCA主成分分析

```python
from sklearn.decomposition import PCA

# 生成示例数据
np.random.seed(42)
X = np.random.randn(100, 10)  # 100个样本，10个特征

# PCA降维
pca = PCA(n_components=2)  # 降到2维
X_pca = pca.fit_transform(X)

print("原始形状:", X.shape)      # (100, 10)
print("降维后形状:", X_pca.shape)  # (100, 2)

# 解释方差比例
print("解释方差比例:", pca.explained_variance_ratio_)
```

### 3. 手动实现PCA

```python
import numpy as np

def pca_manual(X, n_components):
    \"\"\"
    手动实现PCA
    \"\"\"
    # 1. 中心化
    X_centered = X - np.mean(X, axis=0)
    
    # 2. 计算协方差矩阵
    cov_matrix = np.cov(X_centered, rowvar=False)
    
    # 3. 特征值分解
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    
    # 4. 选择前n个主成分
    idx = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, idx[:n_components]]
    
    # 5. 投影
    X_pca = X_centered @ eigenvectors
    
    return X_pca, eigenvectors

# 测试
X_pca_manual, components = pca_manual(X, 2)
```

---

## 💡 PCA的应用场景

1. **数据可视化**：高维数据降到2D/3D绘图
2. **降噪**：保留主要成分，去除噪声
3. **特征压缩**：减少特征数量，加速训练
4. **去相关**：消除特征间的相关性

---

## ✅ 检查点

- [ ] 理解SVD的基本概念
- [ ] 能用sklearn进行PCA降维
- [ ] 理解PCA的应用场景
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 2
            },
            {
                "title": "第10章：概率与统计基础",
                "content": """# 概率与统计基础

## 🎯 学习目标
- 理解常见分布
- 掌握贝叶斯定理
- 应用到数据

---

## 📖 核心内容

### 1. 常见概率分布

```python
import numpy as np
import matplotlib.pyplot as plt

# 均匀分布
uniform_data = np.random.uniform(0, 1, 1000)

# 正态分布（高斯分布）
normal_data = np.random.normal(0, 1, 1000)

# 二项分布
binom_data = np.random.binomial(10, 0.5, 1000)

# 泊松分布
poisson_data = np.random.poisson(3, 1000)
```

### 2. 描述性统计

```python
data = np.random.normal(100, 15, 1000)  # 均值100，标准差15

# 集中趋势
mean = np.mean(data)      # 均值
median = np.median(data)  # 中位数

# 离散程度
std = np.std(data)        # 标准差
var = np.var(data)        # 方差
range_val = np.max(data) - np.min(data)  # 极差

# 百分位数
q25 = np.percentile(data, 25)  # 第一四分位数
q75 = np.percentile(data, 75)  # 第三四分位数
iqr = q75 - q25                # 四分位距
```

### 3. 贝叶斯定理

```
P(A|B) = P(B|A) * P(A) / P(B)

后验概率 = 似然 * 先验概率 / 证据
```

```python
# 示例：垃圾邮件分类
# P(垃圾邮件|包含"免费") = P(包含"免费"|垃圾邮件) * P(垃圾邮件) / P(包含"免费")

def bayesian_spam(word, spam_emails, ham_emails):
    \"\"\"
    使用贝叶斯定理计算邮件是垃圾邮件的概率
    \"\"\"
    total = len(spam_emails) + len(ham_emails)
    p_spam = len(spam_emails) / total
    p_ham = len(ham_emails) / total
    
    # 计算条件概率（加1平滑）
    p_word_given_spam = (spam_emails.count(word) + 1) / (len(spam_emails) + 2)
    p_word_given_ham = (ham_emails.count(word) + 1) / (len(ham_emails) + 2)
    
    # 贝叶斯公式
    p_word = p_word_given_spam * p_spam + p_word_given_ham * p_ham
    p_spam_given_word = (p_word_given_spam * p_spam) / p_word
    
    return p_spam_given_word
```

---

## ✅ 检查点

- [ ] 理解正态分布的特点
- [ ] 掌握描述性统计指标
- [ ] 理解贝叶斯定理的基本思想
""",
                "chapter_type": "text",
                "duration_minutes": 60,
                "order_index": 3
            },
            {
                "title": "第11章：梯度下降优化",
                "content": """# 梯度下降优化

## 🎯 学习目标
- 理解导数和梯度
- 掌握梯度下降
- 可视化优化过程

---

## 📖 核心内容

### 1. 导数与梯度

导数表示函数在某点的变化率。
梯度是多元函数导数的推广，指向函数增长最快的方向。

```python
import numpy as np

# 函数 f(x) = x^2 的导数是 f'(x) = 2x
def f(x):
    return x ** 2

def df(x):
    return 2 * x

# 多元函数 f(x,y) = x^2 + y^2
# 梯度 ∇f = [2x, 2y]
def gradient(x, y):
    return np.array([2*x, 2*y])
```

### 2. 梯度下降算法

```python
def gradient_descent(f, df, x0, learning_rate=0.1, n_iterations=100):
    \"\"\"
    梯度下降优化
    
    参数:
        f: 目标函数
        df: 导数函数
        x0: 初始值
        learning_rate: 学习率
        n_iterations: 迭代次数
    \"\"\"
    x = x0
    history = [x]
    
    for i in range(n_iterations):
        gradient = df(x)
        x = x - learning_rate * gradient  # 沿负梯度方向更新
        history.append(x)
        
        if i % 10 == 0:
            print(f"迭代 {i}: x={x:.4f}, f(x)={f(x):.4f}")
    
    return x, history

# 使用示例
# 最小化 f(x) = x^2
x_min, history = gradient_descent(
    f=lambda x: x**2,
    df=lambda x: 2*x,
    x0=5.0,
    learning_rate=0.1,
    n_iterations=50
)
print(f"最小值点: x={x_min:.4f}")
```

### 3. 学习率的影响

```python
# 学习率太小 → 收敛慢
# 学习率太大 → 震荡甚至发散
# 学习率适中 → 快速收敛

learning_rates = [0.01, 0.1, 0.5, 1.0]
# 实验不同学习率的效果
```

### 4. 多元梯度下降

```python
def gradient_descent_2d(f, grad_f, x0, y0, lr=0.1, n_iter=100):
    \"\"\"
    二元函数的梯度下降
    \"\"\"
    x, y = x0, y0
    history = [(x, y)]
    
    for i in range(n_iter):
        gx, gy = grad_f(x, y)
        x -= lr * gx
        y -= lr * gy
        history.append((x, y))
    
    return x, y, history

# 最小化 f(x,y) = (x-2)^2 + (y-3)^2
def f(x, y):
    return (x-2)**2 + (y-3)**2

def grad_f(x, y):
    return 2*(x-2), 2*(y-3)

x_min, y_min, hist = gradient_descent_2d(f, grad_f, 0, 0)
print(f"最小值点: ({x_min:.4f}, {y_min:.4f})")  # 应该接近 (2, 3)
```

---

## 💡 梯度下降在ML中的应用

- **线性回归**：最小化均方误差
- **逻辑回归**：最小化交叉熵损失
- **神经网络**：反向传播+梯度下降
- **所有参数优化**：模型参数的更新

---

## ✅ 检查点

- [ ] 理解导数和梯度的概念
- [ ] 能实现简单的梯度下降
- [ ] 理解学习率的重要性
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 4
            }
        ]
    },
    {
        "title": "Phase 3: 机器学习（4周/28天）",
        "description": "系统学习机器学习算法：监督学习、无监督学习、特征工程、模型评估与调优。从理论到实战，掌握ML全流程。",
        "level": "intermediate",
        "category": "ml",
        "duration_hours": 56,
        "order_index": 3,
        "chapters": [
            {
                "title": "第12章：机器学习概述与Scikit-Learn入门",
                "content": """# 机器学习概述与Scikit-Learn入门

## 🎯 学习目标
- 理解机器学习基本范式
- 掌握Scikit-Learn的fit/predict模式
- 完成第一个ML模型

---

## 📖 核心内容

### 1. 机器学习类型

```
监督学习 (Supervised Learning)
├── 分类 (Classification): 预测离散类别
│   └── 邮件分类、图像识别、疾病诊断
└── 回归 (Regression): 预测连续值
    └── 房价预测、销量预测、股票价格

无监督学习 (Unsupervised Learning)
├── 聚类 (Clustering): 发现数据分组
│   └── 客户分群、文档分类
└── 降维 (Dimensionality Reduction)
    └── 特征压缩、数据可视化
```

### 2. Scikit-Learn基础

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# 加载数据
iris = load_iris()
X, y = iris.data, iris.target

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 特征标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 训练模型
model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# 预测
y_pred = model.predict(X_test_scaled)

# 评估
accuracy = accuracy_score(y_test, y_pred)
print(f"准确率: {accuracy:.4f}")
```

### 3. ML工作流程

```
1. 数据收集
2. 数据预处理（清洗、缺失值处理）
3. 特征工程（特征选择、特征变换）
4. 划分训练集/测试集
5. 选择模型
6. 训练模型 (fit)
7. 评估模型 (predict + metrics)
8. 调优超参数
9. 部署模型
```

---

## ✅ 检查点

- [ ] 理解监督学习vs无监督学习的区别
- [ ] 掌握Scikit-Learn的基本使用流程
- [ ] 完成第一个鸢尾花分类模型
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 1
            },
            {
                "title": "第13章：特征工程",
                "content": """# 特征工程

## 🎯 学习目标
- 掌握特征缩放
- 学会特征编码
- 理解特征选择

---

## 📖 核心内容

### 1. 特征缩放

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

# 标准化 (Z-score标准化) - 均值为0，方差为1
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 归一化 - 缩放到[0,1]范围
normalizer = MinMaxScaler()
X_normalized = normalizer.fit_transform(X)

# 稳健标准化 - 使用中位数和IQR，对异常值鲁棒
robust_scaler = RobustScaler()
X_robust = robust_scaler.fit_transform(X)
```

### 2. 特征编码

```python
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import pandas as pd

# 标签编码（适用于有序类别）
le = LabelEncoder()
colors = ['红', '绿', '蓝', '红', '绿']
colors_encoded = le.fit_transform(colors)  # [2, 1, 0, 2, 1]

# 独热编码（适用于无序类别）
df = pd.DataFrame({'color': ['红', '绿', '蓝', '红']})
df_encoded = pd.get_dummies(df, columns=['color'])
#    color_红  color_绿  color_蓝
# 0       1       0       0
# 1       0       1       0
# 2       0       0       1
# 3       1       0       0
```

### 3. 特征选择

```python
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.ensemble import RandomForestClassifier

# 过滤法 - 基于统计检验
selector = SelectKBest(f_classif, k=5)
X_selected = selector.fit_transform(X, y)

# 包装法 - 递归特征消除
model = RandomForestClassifier()
rfe = RFE(model, n_features_to_select=5)
X_rfe = rfe.fit_transform(X, y)

# 嵌入法 - 基于模型特征重要性
model = RandomForestClassifier()
model.fit(X, y)
importances = model.feature_importances_
```

---

## ✅ 检查点

- [ ] 掌握标准化和归一化的区别
- [ ] 能进行类别特征编码
- [ ] 了解特征选择的基本方法
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 2,
                "lab": {
                    "title": "实验：数据清洗 - 处理缺失值与异常值",
                    "description": "学习如何处理数据中的缺失值和异常值，掌握多种填充策略和异常值检测方法",
                    "starter_code": """import pandas as pd
import numpy as np
from scipy import stats

def handle_missing_values(df, strategy='auto'):
    """
    处理缺失值
    
    Args:
        df: 输入DataFrame
        strategy: 填充策略 ('auto', 'mean', 'median', 'mode', 'drop')
    
    Returns:
        处理后的DataFrame
    """
    df_clean = df.copy()
    
    # TODO: 实现缺失值处理逻辑
    # 1. 统计每列的缺失值数量
    
    # 2. 根据strategy选择填充方法:
    #    - 数值列: mean, median
    #    - 类别列: mode
    #    - 时间列: 前后填充
    
    # 3. 如果某列缺失值超过50%，考虑删除该列
    
    return df_clean


def detect_outliers(df, method='iqr', columns=None):
    """
    检测异常值
    
    Args:
        df: 输入DataFrame
        method: 检测方法 ('iqr', 'zscore', 'modified_zscore')
        columns: 要检测的数值列，None则检测所有数值列
    
    Returns:
        异常值索引列表
    """
    outlier_indices = set()
    
    # TODO: 实现异常值检测
    # 1. 获取数值列
    
    # 2. 根据method选择检测方法:
    #    - IQR: Q1 - 1.5*IQR, Q3 + 1.5*IQR 之外的值
    #    - Z-score: |z| > 3 的值
    #    - Modified Z-score: 使用median代替mean
    
    return list(outlier_indices)


def handle_outliers(df, method='clip', outlier_indices=None):
    """
    处理检测到的异常值
    
    Args:
        df: 输入DataFrame
        method: 处理方法 ('clip', 'remove', 'replace_median')
        outlier_indices: 异常值索引
    
    Returns:
        处理后的DataFrame
    """
    df_clean = df.copy()
    
    # TODO: 实现异常值处理
    # - clip: 将异常值裁剪到边界
    # - remove: 删除异常值行
    # - replace_median: 用中位数替换
    
    return df_clean


# 创建含缺失值和异常值的测试数据
np.random.seed(42)
n = 200
test_df = pd.DataFrame({
    'id': range(1, n+1),
    '年龄': np.random.normal(35, 10, n).astype(int),
    '收入': np.random.normal(10000, 3000, n),
    '评分': np.random.uniform(1, 5, n),
    '类别': np.random.choice(['A', 'B', 'C'], n)
})

# 添加缺失值
test_df.loc[np.random.choice(n, 20, replace=False), '年龄'] = np.nan
test_df.loc[np.random.choice(n, 15, replace=False), '收入'] = np.nan
test_df.loc[np.random.choice(n, 10, replace=False), '类别'] = np.nan

# 添加异常值
test_df.loc[5, '年龄'] = 150  # 异常年龄
test_df.loc[10, '收入'] = 1000000  # 异常收入
test_df.loc[15, '评分'] = -10  # 异常评分

print("原始数据统计:")
print(test_df.describe())
print("\\n缺失值统计:")
print(test_df.isnull().sum())

# TODO: 调用函数进行处理
""",
                    "solution_code": """import pandas as pd
import numpy as np
from scipy import stats

def handle_missing_values(df, strategy='auto'):
    """
    处理缺失值
    """
    df_clean = df.copy()
    
    # 1. 统计每列的缺失值数量
    missing_stats = df_clean.isnull().sum()
    missing_percent = (missing_stats / len(df_clean)) * 100
    
    print("缺失值统计:")
    for col in df_clean.columns:
        if missing_stats[col] > 0:
            print(f"  {col}: {missing_stats[col]} ({missing_percent[col]:.1f}%)")
    
    # 2. 删除缺失值过多的列 (>50%)
    cols_to_drop = missing_percent[missing_percent > 50].index.tolist()
    if cols_to_drop:
        print(f"\\n删除缺失值过多的列: {cols_to_drop}")
        df_clean = df_clean.drop(columns=cols_to_drop)
    
    # 3. 填充缺失值
    for col in df_clean.columns:
        if df_clean[col].isnull().sum() == 0:
            continue
        
        if strategy == 'auto':
            # 根据列类型自动选择策略
            if df_clean[col].dtype in ['int64', 'float64']:
                # 数值列用中位数填充（更鲁棒）
                fill_value = df_clean[col].median()
                df_clean[col].fillna(fill_value, inplace=True)
                print(f"列 '{col}' 用中位数 {fill_value:.2f} 填充")
            elif pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                # 时间列用前后值填充
                df_clean[col].fillna(method='ffill', inplace=True)
                df_clean[col].fillna(method='bfill', inplace=True)
                print(f"列 '{col}' 用前后值填充")
            else:
                # 类别列用众数填充
                mode_val = df_clean[col].mode()
                if len(mode_val) > 0:
                    df_clean[col].fillna(mode_val[0], inplace=True)
                    print(f"列 '{col}' 用众数 '{mode_val[0]}' 填充")
        elif strategy == 'mean':
            df_clean[col].fillna(df_clean[col].mean(), inplace=True)
        elif strategy == 'median':
            df_clean[col].fillna(df_clean[col].median(), inplace=True)
        elif strategy == 'mode':
            mode_val = df_clean[col].mode()
            if len(mode_val) > 0:
                df_clean[col].fillna(mode_val[0], inplace=True)
        elif strategy == 'drop':
            df_clean.dropna(subset=[col], inplace=True)
    
    return df_clean


def detect_outliers(df, method='iqr', columns=None):
    """
    检测异常值
    """
    outlier_indices = set()
    
    # 获取数值列
    if columns is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    else:
        numeric_cols = columns
    
    print(f"检测异常值 - 数值列: {numeric_cols}")
    print(f"使用方法: {method}")
    
    for col in numeric_cols:
        if col not in df.columns:
            continue
        
        col_data = df[col].dropna()
        
        if method == 'iqr':
            # IQR方法
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index
            outlier_indices.update(outliers)
            print(f"  {col}: 发现 {len(outliers)} 个异常值 (范围: [{lower_bound:.2f}, {upper_bound:.2f}])")
            
        elif method == 'zscore':
            # Z-score方法
            z_scores = np.abs(stats.zscore(col_data))
            outliers = df.loc[col_data.index[z_scores > 3]].index
            outlier_indices.update(outliers)
            print(f"  {col}: 发现 {len(outliers)} 个异常值 (|z| > 3)")
            
        elif method == 'modified_zscore':
            # Modified Z-score (使用MAD)
            median = col_data.median()
            mad = np.median(np.abs(col_data - median))
            modified_z_scores = 0.6745 * (col_data - median) / mad
            outliers = df.loc[col_data.index[np.abs(modified_z_scores) > 3.5]].index
            outlier_indices.update(outliers)
            print(f"  {col}: 发现 {len(outliers)} 个异常值 (modified |z| > 3.5)")
    
    return list(outlier_indices)


def handle_outliers(df, method='clip', outlier_indices=None):
    """
    处理检测到的异常值
    """
    df_clean = df.copy()
    
    if outlier_indices is None or len(outlier_indices) == 0:
        print("没有检测到异常值")
        return df_clean
    
    print(f"\\n处理 {len(outlier_indices)} 个异常值 - 方法: {method}")
    
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        col_outliers = [idx for idx in outlier_indices if idx in df_clean.index and col in df_clean.columns]
        if not col_outliers:
            continue
        
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        if method == 'clip':
            # 裁剪到边界
            df_clean.loc[col_outliers, col] = df_clean.loc[col_outliers, col].clip(lower_bound, upper_bound)
            print(f"  {col}: 异常值已裁剪到 [{lower_bound:.2f}, {upper_bound:.2f}]")
            
        elif method == 'remove':
            # 删除异常值行
            df_clean = df_clean.drop(index=col_outliers)
            print(f"  {col}: 删除了 {len(col_outliers)} 行")
            
        elif method == 'replace_median':
            # 用中位数替换
            median_val = df_clean[col].median()
            df_clean.loc[col_outliers, col] = median_val
            print(f"  {col}: 异常值用中位数 {median_val:.2f} 替换")
    
    return df_clean


# 创建含缺失值和异常值的测试数据
np.random.seed(42)
n = 200
test_df = pd.DataFrame({
    'id': range(1, n+1),
    '年龄': np.random.normal(35, 10, n).astype(int),
    '收入': np.random.normal(10000, 3000, n),
    '评分': np.random.uniform(1, 5, n),
    '类别': np.random.choice(['A', 'B', 'C'], n)
})

# 添加缺失值
test_df.loc[np.random.choice(n, 20, replace=False), '年龄'] = np.nan
test_df.loc[np.random.choice(n, 15, replace=False), '收入'] = np.nan
test_df.loc[np.random.choice(n, 10, replace=False), '类别'] = np.nan

# 添加异常值
test_df.loc[5, '年龄'] = 150
test_df.loc[10, '收入'] = 1000000
test_df.loc[15, '评分'] = -10

print("=" * 60)
print("数据清洗演示")
print("=" * 60)

print("\\n原始数据统计:")
print(test_df.describe())
print("\\n缺失值统计:")
print(test_df.isnull().sum())

# 步骤1: 处理缺失值
df_no_missing = handle_missing_values(test_df, strategy='auto')

# 步骤2: 检测异常值
outliers = detect_outliers(df_no_missing, method='iqr')
print(f"\\n共检测到 {len(outliers)} 个异常值")

# 步骤3: 处理异常值
df_clean = handle_outliers(df_no_missing, method='clip', outlier_indices=outliers)

print("\\n清洗后数据统计:")
print(df_clean.describe())
print(f"\\n最终数据行数: {len(df_clean)}")
print(f"原始数据行数: {len(test_df)}")
""",
                    "test_cases": [
                        {"description": "能正确识别缺失值", "expected": "返回缺失值统计"},
                        {"description": "能正确处理数值列缺失值", "expected": "数值列无缺失"},
                        {"description": "能正确检测异常值", "expected": "返回异常值索引列表"},
                        {"description": "能正确处理异常值", "expected": "异常值被处理"}
                    ],
                    "validation_rules": [
                        {"type": "function_exists", "name": "handle_missing_values"},
                        {"type": "function_exists", "name": "detect_outliers"},
                        {"type": "function_exists", "name": "handle_outliers"},
                        {"type": "code_contains", "pattern": "fillna"},
                        {"type": "code_contains", "pattern": "quantile"}
                    ]
                }
            },
            {
                "title": "第14章：线性回归与正则化",
                "content": """# 线性回归与正则化

## 🎯 学习目标
- 理解线性回归原理
- 掌握正则化（L1/L2）
- 完成房价预测实战

---

## 📖 核心内容

### 1. 线性回归

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.datasets import fetch_california_housing

# 加载房价数据
housing = fetch_california_housing()
X, y = housing.data, housing.target

# 训练线性回归模型
model = LinearRegression()
model.fit(X, y)

# 查看系数
print("系数:", model.coef_)
print("截距:", model.intercept_)

# 预测
y_pred = model.predict(X)
```

### 2. 正则化

```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet

# L2正则化（Ridge回归）- 防止过拟合，系数平滑
ridge = Ridge(alpha=1.0)
ridge.fit(X_train, y_train)

# L1正则化（Lasso回归）- 产生稀疏解，自动特征选择
lasso = Lasso(alpha=0.1)
lasso.fit(X_train, y_train)

# ElasticNet - L1和L2结合
elastic = ElasticNet(alpha=0.1, l1_ratio=0.5)
elastic.fit(X_train, y_train)
```

### 3. 评估指标

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 回归评估指标
mse = mean_squared_error(y_true, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)  # R²决定系数

print(f"MSE: {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"MAE: {mae:.4f}")
print(f"R²: {r2:.4f}")
```

---

## ✅ 检查点

- [ ] 理解线性回归的原理
- [ ] 理解L1和L2正则化的区别
- [ ] 能进行房价预测并评估模型
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 3
            },
            {
                "title": "第15章：逻辑回归与分类算法",
                "content": """# 逻辑回归与分类算法

## 🎯 学习目标
- 理解逻辑回归原理
- 掌握分类评估指标
- 完成二分类任务

---

## 📖 核心内容

### 1. 逻辑回归

```python
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_breast_cancer

# 加载乳腺癌数据集
data = load_breast_cancer()
X, y = data.data, data.target

# 训练逻辑回归模型
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 预测概率
y_prob = model.predict_proba(X_test)
print("预测概率:", y_prob[:5])

# 预测类别
y_pred = model.predict(X_test)
```

### 2. 分类评估指标

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)

# 基础指标
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"准确率: {accuracy:.4f}")
print(f"精确率: {precision:.4f}")
print(f"召回率: {recall:.4f}")
print(f"F1分数: {f1:.4f}")

# 混淆矩阵
cm = confusion_matrix(y_test, y_pred)
print("混淆矩阵:")
print(cm)

# 完整报告
print(classification_report(y_test, y_pred))
```

### 3. 决策树

```python
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

# 训练决策树
tree = DecisionTreeClassifier(max_depth=3, random_state=42)
tree.fit(X_train, y_train)

# 可视化
plt.figure(figsize=(20, 10))
plot_tree(tree, feature_names=data.feature_names, 
          class_names=data.target_names, filled=True)
plt.savefig('tree.png')
```

---

## ✅ 检查点

- [ ] 理解逻辑回归与线性回归的区别
- [ ] 掌握分类评估指标（准确率、精确率、召回率、F1）
- [ ] 理解混淆矩阵
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 4
            },
            {
                "title": "第16章：集成学习 - Random Forest",
                "content": """# 集成学习 - Random Forest

## 🎯 学习目标
- 理解Bagging思想
- 掌握Random Forest
- 完成客户流失预测

---

## 📖 核心内容

### 1. 集成学习思想

```
集成学习: 三个臭皮匠，顶个诸葛亮

Bagging (Bootstrap Aggregating)
├── 随机采样训练数据
├── 训练多个基学习器
└── 投票/平均得到最终结果

Boosting
├── 串行训练
├── 关注前一个模型的错误
└── 加权组合
```

### 2. Random Forest

```python
from sklearn.ensemble import RandomForestClassifier

# 训练随机森林
rf = RandomForestClassifier(
    n_estimators=100,  # 树的数量
    max_depth=10,      # 最大深度
    min_samples_split=5,
    random_state=42
)
rf.fit(X_train, y_train)

# 预测
y_pred = rf.predict(X_test)

# 特征重要性
importances = rf.feature_importances_
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': importances
}).sort_values('importance', ascending=False)
print(feature_importance)
```

### 3. 客户流失预测实战

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

# 加载数据（模拟）
# df = pd.read_csv('churn_data.csv')

# 特征工程
# X = df.drop(['customer_id', 'churn'], axis=1)
# y = df['churn']

# 训练模型
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 交叉验证
cv_scores = cross_val_score(model, X, y, cv=5)
print(f"交叉验证分数: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# 预测并输出高风险客户
churn_prob = model.predict_proba(X_test)[:, 1]
high_risk = X_test[churn_prob > 0.7]
print(f"高风险客户数量: {len(high_risk)}")
```

---

## ✅ 检查点

- [ ] 理解Bagging和Boosting的区别
- [ ] 掌握Random Forest的使用
- [ ] 能进行特征重要性分析
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 5
            },
            {
                "title": "第17章：XGBoost与LightGBM",
                "content": """# XGBoost与LightGBM

## 🎯 学习目标
- 理解Boosting原理
- 掌握XGBoost和LightGBM
- 完成Kaggle入门竞赛

---

## 📖 核心内容

### 1. XGBoost

```python
import xgboost as xgb
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

# 加载数据
data = load_breast_cancer()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# XGBoost分类器
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# 预测
y_pred = model.predict(X_test)

# 特征重要性
xgb.plot_importance(model, max_num_features=10)
```

### 2. LightGBM

```python
import lightgbm as lgb

# LightGBM分类器
model = lgb.LGBMClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# 早停法（防止过拟合）
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    callbacks=[lgb.early_stopping(stopping_rounds=10)]
)
```

### 3. 对比

| 特性 | XGBoost | LightGBM |
|------|---------|----------|
| 训练速度 | 快 | 更快 |
| 内存占用 | 较大 | 较小 |
| 准确率 | 高 | 相当/更高 |
| 大数据 | 良好 | 优秀 |
| 类别特征 | 需编码 | 原生支持 |

---

## ✅ 检查点

- [ ] 理解Boosting的基本原理
- [ ] 掌握XGBoost的基本使用
- [ ] 了解XGBoost和LightGBM的差异
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 6
            },
            {
                "title": "第18章：模型评估与超参数调优",
                "content": """# 模型评估与超参数调优

## 🎯 学习目标
- 掌握交叉验证
- 理解过拟合与欠拟合
- 使用Optuna进行超参数优化

---

## 📖 核心内容

### 1. 交叉验证

```python
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold

# K折交叉验证
scores = cross_val_score(model, X, y, cv=5)
print(f"交叉验证分数: {scores.mean():.4f} (+/- {scores.std():.4f})")

# 分层K折（保持类别比例）
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=skf)
```

### 2. 学习曲线与验证曲线

```python
from sklearn.model_selection import learning_curve, validation_curve
import matplotlib.pyplot as plt

# 学习曲线
train_sizes, train_scores, val_scores = learning_curve(
    model, X, y, cv=5, 
    train_sizes=np.linspace(0.1, 1.0, 10)
)

# 验证曲线
param_range = [1, 3, 5, 7, 10]
train_scores, val_scores = validation_curve(
    model, X, y, param_name='max_depth',
    param_range=param_range, cv=5
)
```

### 3. 超参数调优

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

# 网格搜索
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.3]
}

grid_search = GridSearchCV(
    estimator=xgb.XGBClassifier(),
    param_grid=param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)
grid_search.fit(X, y)
print(f"最佳参数: {grid_search.best_params_}")
print(f"最佳分数: {grid_search.best_score_:.4f}")
```

### 4. Optuna自动调参

```python
import optuna

def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0)
    }
    
    model = xgb.XGBClassifier(**params)
    score = cross_val_score(model, X, y, cv=5).mean()
    return score

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=50)
print(f"最佳参数: {study.best_params}")
```

---

## ✅ 检查点

- [ ] 掌握交叉验证的使用
- [ ] 能识别过拟合和欠拟合
- [ ] 了解超参数调优的方法
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 7
            },
            {
                "title": "第19章：K-Means聚类与客户分群",
                "content": """# K-Means聚类与客户分群

## 🎯 学习目标
- 理解聚类原理
- 掌握K-Means算法
- 完成客户分群实战

---

## 📖 核心内容

### 1. K-Means算法

```python
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt

# 生成示例数据
X, _ = make_blobs(n_samples=300, centers=4, random_state=42)

# K-Means聚类
kmeans = KMeans(n_clusters=4, random_state=42)
labels = kmeans.fit_predict(X)

# 聚类中心
centers = kmeans.cluster_centers_

# 可视化
plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis')
plt.scatter(centers[:, 0], centers[:, 1], c='red', marker='x', s=200)
plt.title('K-Means Clustering')
plt.show()
```

### 2. 确定最佳K值

```python
# 肘部法则
inertias = []
K_range = range(1, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)

# 绘制肘部图
plt.plot(K_range, inertias, 'bo-')
plt.xlabel('K')
plt.ylabel('Inertia')
plt.title('Elbow Method')
plt.show()
```

### 3. 客户分群实战

```python
import pandas as pd
from sklearn.preprocessing import StandardScaler

# 客户数据示例
# RFM模型: Recency, Frequency, Monetary
customers = pd.DataFrame({
    'recency': [10, 5, 30, 2, 15],      # 最近购买天数
    'frequency': [5, 10, 2, 15, 3],     # 购买频率
    'monetary': [500, 1000, 200, 1500, 300]  # 消费金额
})

# 标准化
scaler = StandardScaler()
customers_scaled = scaler.fit_transform(customers)

# 聚类
kmeans = KMeans(n_clusters=3, random_state=42)
customers['cluster'] = kmeans.fit_predict(customers_scaled)

# 分析每个群体
print(customers.groupby('cluster').mean())
```

---

## ✅ 检查点

- [ ] 理解K-Means的基本原理
- [ ] 掌握确定最佳K值的方法
- [ ] 能进行客户分群分析
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 8
            },
            {
                "title": "第20章：机器学习项目实战",
                "content": """# 机器学习项目实战

## 🎯 项目目标
完成一个完整的机器学习项目：客户流失预测

---

## 📋 项目流程

### Day 1: 数据探索
- 加载数据
- 查看数据分布
- 处理缺失值

### Day 2: 特征工程
- 特征创建
- 特征选择
- 数据标准化

### Day 3: 模型训练
- 训练多个模型（LR, RF, XGBoost）
- 交叉验证
- 超参数调优

### Day 4: 模型评估与部署
- 选择最佳模型
- 特征重要性分析
- 保存模型

---

## 核心代码框架

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import joblib

# 1. 数据加载
df = pd.read_csv('churn_data.csv')

# 2. 数据预处理
# 处理缺失值、异常值
# 编码类别特征

# 3. 划分数据集
X = df.drop(['customer_id', 'churn'], axis=1)
y = df['churn']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 4. 特征工程
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. 模型训练
models = {
    'LogisticRegression': LogisticRegression(),
    'RandomForest': RandomForestClassifier(),
    'XGBoost': xgb.XGBClassifier()
}

for name, model in models.items():
    scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    print(f"{name}: {scores.mean():.4f}")

# 6. 选择最佳模型并调优
# ...

# 7. 保存模型
joblib.dump(best_model, 'churn_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
```

---

## ✅ 项目交付物

- [ ] 完整的Jupyter Notebook
- [ ] 训练好的模型文件
- [ ] 项目报告（包含数据分析、模型选择、结果）
- [ ] GitHub代码仓库
""",
                "chapter_type": "lab",
                "duration_minutes": 480,
                "order_index": 9
            },
            {
                "title": "第21章：时间序列分析基础",
                "content": """# 时间序列分析基础

## 🎯 学习目标
- 理解时序特点
- 掌握时序预处理
- 了解ARIMA模型

---

## 📖 核心内容

### 1. 时间序列特征

```python
import pandas as pd
import numpy as np

# 创建时间序列
dates = pd.date_range('2020-01-01', periods=365, freq='D')
values = np.cumsum(np.random.randn(365)) + 100
ts = pd.Series(values, index=dates)

# 时间序列分解
from statsmodels.tsa.seasonal import seasonal_decompose

decomposition = seasonal_decompose(ts, model='additive', period=30)
trend = decomposition.trend
seasonal = decomposition.seasonal
residual = decomposition.resid
```

### 2. ARIMA模型

```python
from statsmodels.tsa.arima.model import ARIMA

# 拟合ARIMA模型
# ARIMA(p, d, q) - 自回归阶数、差分阶数、移动平均阶数
model = ARIMA(ts, order=(1, 1, 1))
model_fit = model.fit()

# 预测
forecast = model_fit.forecast(steps=30)
```

---

## ✅ 检查点

- [ ] 理解时间序列的组成（趋势、季节、残差）
- [ ] 了解ARIMA的基本概念
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 10
            },
            {
                "title": "第22章：ML工程化基础",
                "content": """# ML工程化基础

## 🎯 学习目标
- 模型服务化（Flask API）
- Pipeline与调度
- 了解Airflow

---

## 📖 核心内容

### 1. Flask模型服务

```python
from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)
model = joblib.load('model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = np.array(data['features']).reshape(1, -1)
    prediction = model.predict(features)
    return jsonify({'prediction': prediction.tolist()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 2. Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# 构建Pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier())
])

# 训练和预测
pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)

# 保存整个Pipeline
joblib.dump(pipeline, 'pipeline.pkl')
```

### 3. Airflow基础

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def train_model():
    # 训练模型
    pass

def evaluate_model():
    # 评估模型
    pass

with DAG('ml_pipeline', start_date=datetime(2024, 1, 1)) as dag:
    train_task = PythonOperator(task_id='train', python_callable=train_model)
    eval_task = PythonOperator(task_id='evaluate', python_callable=evaluate_model)
    
    train_task >> eval_task
```

---

## ✅ 检查点

- [ ] 能用Flask部署模型API
- [ ] 理解Pipeline的优势
- [ ] 了解Airflow的基本概念
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 11
            },
            {
                "title": "第23章：Phase 3 复习与总结",
                "content": """# Phase 3: 机器学习复习与总结

## 📚 知识图谱

```
Phase 3: 机器学习 (4周/28天)
├── Week 1: ML基础
│   ├── ML概述与Scikit-Learn
│   ├── 特征工程
│   └── 线性/逻辑回归
├── Week 2: 算法进阶
│   ├── 决策树
│   ├── Random Forest
│   └── XGBoost/LightGBM
├── Week 3: 模型优化
│   ├── 模型评估与调优
│   ├── 聚类算法
│   └── 时间序列
└── Week 4: 项目实战
    ├── ML项目全流程
    ├── ML工程化
    └── 总结复习
```

## 🎯 核心能力

- [ ] 能独立完成ML项目全流程
- [ ] 掌握常用算法原理和应用
- [ ] 能进行特征工程和调优
- [ ] 理解ML工程化基础

## 🚀 下一步

进入 **Phase 4: 深度学习**
- 神经网络基础
- PyTorch框架
- CNN/RNN
""",
                "chapter_type": "text",
                "duration_minutes": 60,
                "order_index": 12
            }
        ]
    },
    {
        "title": "Phase 4: 深度学习（2周/14天）",
        "description": "学习深度学习基础：神经网络、PyTorch框架、CNN、RNN。应用导向，快速掌握深度学习核心技术。",
        "level": "advanced",
        "category": "dl",
        "duration_hours": 28,
        "order_index": 4,
        "chapters": [
            {
                "title": "第24章：神经网络基础与PyTorch入门",
                "content": """# 神经网络基础与PyTorch入门

## 🎯 学习目标
- 理解神经网络基本原理
- 掌握PyTorch基础
- 完成第一个神经网络

---

## 📖 核心内容

### 1. 神经网络基础

```
神经网络结构:
输入层 → 隐藏层 → 隐藏层 → 输出层

神经元计算: y = activation(w·x + b)

激活函数:
- ReLU: max(0, x)
- Sigmoid: 1 / (1 + e^(-x))
- Tanh: (e^x - e^(-x)) / (e^x + e^(-x))
```

### 2. PyTorch安装与基础

```python
import torch
import torch.nn as nn
import torch.optim as optim

# 检查GPU
print(torch.cuda.is_available())

# Tensor基础
x = torch.tensor([1.0, 2.0, 3.0])
y = torch.rand(3, 3)
z = torch.zeros(2, 3)

# Tensor操作
a = torch.tensor([[1, 2], [3, 4]])
b = torch.tensor([[5, 6], [7, 8]])
print(a + b)
print(a @ b)  # 矩阵乘法
```

### 3. 自动求导

```python
# 创建需要梯度的张量
x = torch.tensor(2.0, requires_grad=True)

# 定义计算
y = x ** 2 + 3 * x + 1

# 反向传播
y.backward()

# 查看梯度
print(x.grad)  # dy/dx = 2x + 3 = 7
```

### 4. 定义神经网络

```python
class NeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

# 创建模型
model = NeuralNetwork(input_size=784, hidden_size=256, num_classes=10)
```

---

## ✅ 检查点

- [ ] 理解神经网络的基本结构
- [ ] 掌握PyTorch Tensor操作
- [ ] 理解自动求导机制
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 1
            },
            {
                "title": "第25章：MNIST手写字识别实战",
                "content": """# MNIST手写字识别实战

## 🎯 学习目标
- 搭建全连接神经网络
- 训练与评估
- 可视化结果

---

## 📖 完整代码

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

# 1. 数据加载
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# 2. 定义模型
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(28*28, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        x = x.view(-1, 28*28)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

model = Net()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 3. 训练
num_epochs = 5
for epoch in range(num_epochs):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        if batch_idx % 100 == 0:
            print(f'Epoch: {epoch}, Batch: {batch_idx}, Loss: {loss.item():.4f}')

# 4. 评估
model.eval()
correct = 0
total = 0
with torch.no_grad():
    for data, target in test_loader:
        output = model(data)
        _, predicted = torch.max(output.data, 1)
        total += target.size(0)
        correct += (predicted == target).sum().item()

print(f'准确率: {100 * correct / total:.2f}%')
```

---

## ✅ 检查点

- [ ] 完成MNIST数据加载
- [ ] 训练并评估模型
- [ ] 达到90%+准确率
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 2
            },
            {
                "title": "第26章：卷积神经网络CNN",
                "content": """# 卷积神经网络CNN

## 🎯 学习目标
- 理解卷积操作
- 掌握池化层
- 实现CNN图像分类

---

## 📖 核心内容

### 1. 卷积操作

```python
import torch.nn as nn

# 卷积层
conv = nn.Conv2d(
    in_channels=1,   # 输入通道数
    out_channels=32, # 输出通道数
    kernel_size=3,   # 卷积核大小
    stride=1,        # 步长
    padding=1        # 填充
)
```

### 2. CNN架构

```python
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        # 卷积层 + 池化层
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.25)
        
        # 全连接层
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        # 卷积块1: 28x28 -> 14x14
        x = self.pool(torch.relu(self.conv1(x)))
        # 卷积块2: 14x14 -> 7x7
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.dropout(x)
        
        # 展平
        x = x.view(-1, 64 * 7 * 7)
        
        # 全连接
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x
```

### 3. 经典网络

- **LeNet**: 最早的CNN
- **AlexNet**: 引入ReLU和Dropout
- **VGG**: 小卷积核(3x3)堆叠
- **ResNet**: 残差连接，解决梯度消失

---

## ✅ 检查点

- [ ] 理解卷积的作用
- [ ] 掌握CNN的基本结构
- [ ] 能实现CNN图像分类
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 3
            },
            {
                "title": "第27章：循环神经网络RNN与LSTM",
                "content": """# 循环神经网络RNN与LSTM

## 🎯 学习目标
- 理解RNN结构
- 掌握LSTM
- 时序预测实战

---

## 📖 核心内容

### 1. RNN基础

```python
import torch.nn as nn

# LSTM层
lstm = nn.LSTM(
    input_size=10,   # 输入特征维度
    hidden_size=20,  # 隐藏层维度
    num_layers=2,    # LSTM层数
    batch_first=True # 批次维度在前
)
```

### 2. LSTM时序预测

```python
class LSTM predictor(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(LSTM predictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out
```

### 3. 股票价格预测示例

```python
import numpy as np
import pandas as pd

# 数据准备
def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:(i + seq_length)]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

# 加载数据（示例）
# prices = pd.read_csv('stock_prices.csv')['close'].values
# X, y = create_sequences(prices, seq_length=30)
```

---

## ✅ 检查点

- [ ] 理解RNN和LSTM的区别
- [ ] 掌握LSTM的基本使用
- [ ] 能进行简单的时序预测
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 4
            },
            {
                "title": "第28章：深度学习优化与部署",
                "content": """# 深度学习优化与部署

## 🎯 学习目标
- 掌握批归一化和Dropout
- 模型保存与加载
- 了解部署方案

---

## 📖 核心内容

### 1. 优化技巧

```python
class OptimizedNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3)
        self.bn1 = nn.BatchNorm2d(32)  # 批归一化
        self.conv2 = nn.Conv2d(32, 64, 3)
        self.bn2 = nn.BatchNorm2d(64)
        self.dropout = nn.Dropout(0.5)  # Dropout
        self.fc = nn.Linear(64 * 5 * 5, 10)
    
    def forward(self, x):
        x = self.bn1(torch.relu(self.conv1(x)))
        x = self.bn2(torch.relu(self.conv2(x)))
        x = self.dropout(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x
```

### 2. 学习率调度

```python
# 学习率衰减
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
# 余弦退火
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

# 训练循环中使用
for epoch in range(num_epochs):
    train(...)
    scheduler.step()
```

### 3. 模型保存与加载

```python
# 保存模型
torch.save(model.state_dict(), 'model.pth')

# 加载模型
model = TheModelClass(*args, **kwargs)
model.load_state_dict(torch.load('model.pth'))
model.eval()

# 保存完整模型
torch.save(model, 'model_complete.pth')
model = torch.load('model_complete.pth')
```

### 4. TorchScript导出

```python
# 转换为TorchScript
scripted_model = torch.jit.script(model)
scripted_model.save('model_scripted.pt')

# 加载
loaded_model = torch.jit.load('model_scripted.pt')
```

---

## ✅ 检查点

- [ ] 理解批归一化和Dropout的作用
- [ ] 能保存和加载模型
- [ ] 了解TorchScript部署
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 5
            },
            {
                "title": "第29章：Phase 4 复习与总结",
                "content": """# Phase 4: 深度学习复习与总结

## 📚 知识图谱

```
Phase 4: 深度学习 (2周/14天)
├── Week 1: DL基础
│   ├── 神经网络原理
│   ├── PyTorch入门
│   └── MNIST实战
└── Week 2: 进阶网络
    ├── CNN卷积网络
    ├── RNN/LSTM序列模型
    └── 优化与部署
```

## 🎯 核心能力

- [ ] 能用PyTorch搭建神经网络
- [ ] 理解CNN/RNN原理
- [ ] 能进行简单的DL项目
- [ ] 了解模型部署基础

## 🚀 下一步

进入 **Phase 5: LLM大模型**
- Transformer架构
- BERT/GPT
- LangChain开发
""",
                "chapter_type": "text",
                "duration_minutes": 60,
                "order_index": 6
            }
        ]
    },
    {
        "title": "Phase 5: LLM大模型（3周/21天）",
        "description": "学习大语言模型技术：Transformer架构、Prompt Engineering、LangChain框架、RAG应用、模型微调。掌握最前沿的AI应用技术。",
        "level": "advanced",
        "category": "llm",
        "duration_hours": 42,
        "order_index": 5,
        "chapters": [
            {
                "title": "第30章：NLP基础与Word2Vec",
                "content": """# NLP基础与Word2Vec

## 🎯 学习目标
- 理解文本处理流程
- 掌握Tokenization
- 理解词向量概念

---

## 📖 核心内容

### 1. 文本预处理

```python
import re

# 分词
def tokenize(text):
    # 简单空格分词
    return text.lower().split()

# 清洗
def clean_text(text):
    text = re.sub(r'[^\\w\\s]', '', text)  # 去除标点
    text = re.sub(r'\\d+', '', text)       # 去除数字
    return text.strip()

# 去除停用词
stopwords = {'the', 'a', 'is', 'are', 'was', 'were'}
def remove_stopwords(tokens):
    return [t for t in tokens if t not in stopwords]
```

### 2. Word2Vec

```python
from gensim.models import Word2Vec

# 准备语料
sentences = [
    ['machine', 'learning', 'is', 'fun'],
    ['deep', 'learning', 'is', 'powerful'],
    ['natural', 'language', 'processing', 'is', 'interesting']
]

# 训练模型
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1)

# 获取词向量
vector = model.wv['learning']

# 找相似词
similar = model.wv.most_similar('learning', topn=3)
```

### 3. 词向量可视化

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

words = ['machine', 'learning', 'deep', 'natural', 'language', 'processing']
vectors = [model.wv[w] for w in words]

pca = PCA(n_components=2)
reduced = pca.fit_transform(vectors)

plt.scatter(reduced[:, 0], reduced[:, 1])
for i, word in enumerate(words):
    plt.annotate(word, (reduced[i, 0], reduced[i, 1]))
plt.show()
```

---

## ✅ 检查点

- [ ] 理解文本预处理流程
- [ ] 了解Word2Vec的基本概念
- [ ] 理解词向量的意义
""",
                "chapter_type": "code",
                "duration_minutes": 60,
                "order_index": 1
            },
            {
                "title": "第31章：Transformer架构",
                "content": """# Transformer架构

## 🎯 学习目标
- 理解Self-Attention机制
- 掌握Transformer结构
- 阅读Attention Is All You Need论文

---

## 📖 核心内容

### 1. Self-Attention机制

```
Self-Attention的计算:
1. 计算Query, Key, Value
2. Attention(Q, K, V) = softmax(QK^T / √d_k) V

核心思想: 每个词都和其他所有词计算相关性
```

### 2. Transformer结构

```python
import torch.nn as nn

class TransformerBlock(nn.Module):
    def __init__(self, embed_dim, num_heads):
        super().__init__()
        self.attention = nn.MultiheadAttention(embed_dim, num_heads)
        self.norm1 = nn.LayerNorm(embed_dim)
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, 4 * embed_dim),
            nn.ReLU(),
            nn.Linear(4 * embed_dim, embed_dim)
        )
        self.norm2 = nn.LayerNorm(embed_dim)
    
    def forward(self, x):
        # Self-Attention + 残差连接
        attn_out, _ = self.attention(x, x, x)
        x = self.norm1(x + attn_out)
        
        # Feed Forward + 残差连接
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        return x
```

### 3. 位置编码

```python
import math

def positional_encoding(max_len, d_model):
    pe = torch.zeros(max_len, d_model)
    position = torch.arange(0, max_len).unsqueeze(1)
    div_term = torch.exp(torch.arange(0, d_model, 2) * -(math.log(10000.0) / d_model))
    
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    return pe
```

---

## ✅ 检查点

- [ ] 理解Self-Attention的核心思想
- [ ] 了解Transformer的编码器-解码器结构
- [ ] 理解位置编码的作用
""",
                "chapter_type": "text",
                "duration_minutes": 120,
                "order_index": 2
            },
            {
                "title": "第32章：BERT与GPT模型",
                "content": """# BERT与GPT模型

## 🎯 学习目标
- 理解BERT的双向编码
- 理解GPT的自回归生成
- 掌握预训练模型的使用

---

## 📖 核心内容

### 1. BERT (Bidirectional Encoder Representations from Transformers)

```python
from transformers import BertTokenizer, BertModel

# 加载BERT
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
model = BertModel.from_pretrained('bert-base-chinese')

# 编码文本
text = "这是一个测试句子"
inputs = tokenizer(text, return_tensors='pt', padding=True)
outputs = model(**inputs)

# 获取句向量
sentence_embedding = outputs.last_hidden_state[:, 0, :]  # [CLS] token
```

### 2. GPT (Generative Pre-trained Transformer)

```python
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# 加载GPT-2
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

# 文本生成
prompt = "Once upon a time"
inputs = tokenizer(prompt, return_tensors='pt')
outputs = model.generate(
    **inputs,
    max_length=50,
    num_return_sequences=1,
    temperature=0.7
)
generated_text = tokenizer.decode(outputs[0])
```

### 3. BERT vs GPT对比

| 特性 | BERT | GPT |
|------|------|-----|
| 方向 | 双向 | 单向（自左向右）|
| 任务 | 理解任务（分类、NER）| 生成任务 |
| 训练目标 | Masked LM + NSP | 自回归语言模型 |
| 代表应用 | 文本分类、问答 | 文本生成、对话 |

---

## ✅ 检查点

- [ ] 理解BERT和GPT的结构差异
- [ ] 能用transformers库加载预训练模型
- [ ] 了解两种模型的应用场景
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 3
            },
            {
                "title": "第33章：Prompt Engineering",
                "content": """# Prompt Engineering

## 🎯 学习目标
- 掌握Zero-shot和Few-shot提示技巧
- 学会Chain-of-Thought思维链
- 了解Prompt设计最佳实践

## 📖 核心内容

### 1. Zero-shot vs Few-shot

**Zero-shot**: 直接提问，不给示例
```
请将以下中文翻译成英文：你好世界
```

**Few-shot**: 提供示例引导
```
中文 -> 英文
猫 -> cat
狗 -> dog
你好世界 ->
```

### 2. Chain-of-Thought

```
问题：一个农场有鸡和兔共35只，脚共94只。鸡兔各几只？

请逐步思考：
1. 设鸡有x只，兔有y只
2. x + y = 35
3. 2x + 4y = 94
4. 解方程得...
```

### 3. Prompt设计原则
- 清晰具体
- 提供上下文
- 使用分隔符
- 指定输出格式
""",
                "chapter_type": "text",
                "duration_minutes": 60,
                "order_index": 4
            }
        ]
    },
    {
        "title": "Phase 6: AI工程化（2周/14天）",
        "description": "学习AI模型部署、MLOps、与现有系统集成的工程化实践。结合数仓背景，掌握AI生产环境最佳实践。",
        "level": "expert",
        "category": "engineering",
        "duration_hours": 28,
        "order_index": 6,
        "chapters": [
            {
                "title": "第34章：模型部署与服务化",
                "content": """# 模型部署与服务化

## 🎯 学习目标
- 掌握模型导出格式（ONNX、TorchScript）
- 学会构建模型服务API
- 了解模型版本管理

## 📖 核心内容

### 1. 模型导出

**PyTorch -> ONNX**
```python
import torch
import torch.onnx

# 导出模型
dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    export_params=True,
    opset_version=11
)
```

**PyTorch -> TorchScript**
```python
# 使用torch.jit.script
scripted_model = torch.jit.script(model)
scripted_model.save("model.pt")

# 加载并使用
loaded_model = torch.jit.load("model.pt")
```

### 2. FastAPI模型服务

```python
from fastapi import FastAPI
from pydantic import BaseModel
import torch

app = FastAPI()
model = torch.jit.load("model.pt")

class PredictionRequest(BaseModel):
    data: list

@app.post("/predict")
async def predict(request: PredictionRequest):
    input_tensor = torch.tensor(request.data)
    with torch.no_grad():
        output = model(input_tensor)
    return {"prediction": output.tolist()}
```

### 3. 模型版本管理

**MLflow基础**
```python
import mlflow

mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    # 记录参数
    mlflow.log_param("lr", 0.01)
    
    # 记录指标
    mlflow.log_metric("accuracy", 0.95)
    
    # 保存模型
    mlflow.pytorch.log_model(model, "model")
```
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 1
            },
            {
                "title": "第35章：MLOps与监控",
                "content": """# MLOps与监控

## 🎯 学习目标
- 了解MLOps核心概念
- 掌握模型监控方法
- 学会数据漂移检测

## 📖 核心内容

### 1. MLOps核心组件

- **实验跟踪**: MLflow, Weights & Biases
- **特征存储**: Feast, Tecton
- **模型注册**: MLflow Model Registry
- **模型监控**: Evidently, WhyLabs

### 2. 模型性能监控

```python
# 监控指标
track_metrics = {
    "accuracy": accuracy_score(y_true, y_pred),
    "latency": inference_time,
    "throughput": requests_per_second
}

# 告警阈值
if accuracy < 0.85:
    send_alert("Model accuracy degraded!")
```

### 3. 数据漂移检测

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=reference, current_data=current)
report.save_html("drift_report.html")
```
""",
                "chapter_type": "text",
                "duration_minutes": 60,
                "order_index": 2
            },
            {
                "title": "第36章：AI系统架构设计",
                "content": """# AI系统架构设计

## 🎯 学习目标
- 理解AI系统架构模式
- 掌握在线vs离线预测场景
- 了解与数仓系统集成

## 📖 核心内容

### 1. 架构模式

**在线预测 (Online)**
```
用户请求 -> API Gateway -> 模型服务 -> 返回结果
                ↓
            特征服务 (实时特征)
```

**离线批量 (Batch)**
```
数仓数据 -> 特征工程 -> 批量预测 -> 结果回写数仓
```

### 2. 特征平台

**在线特征 vs 离线特征**
- 离线特征：批处理计算，存储在数仓
- 在线特征：实时计算，缓存供API使用

### 3. 与数仓集成

```sql
-- 数仓中的AI预测结果
CREATE TABLE ai_predictions (
    user_id STRING,
    prediction_date DATE,
    churn_probability FLOAT,
    model_version STRING,
    created_at TIMESTAMP
);
```
""",
                "chapter_type": "text",
                "duration_minutes": 60,
                "order_index": 3,
                "lab": {
                    "title": "构建端到端AI Pipeline",
                    "description": "设计一个完整的AI系统，包括数据准备、模型训练、部署和监控",
                    "starter_code": """# TODO: 设计AI系统架构
# 1. 定义问题：客户流失预测
# 2. 数据流设计
# 3. 模型服务设计
# 4. 监控方案

def design_ai_system():
    """设计AI系统架构"""
    architecture = {
        "problem": "客户流失预测",
        "data_source": "数据仓库",
        "feature_pipeline": "TODO",
        "model_service": "TODO",
        "monitoring": "TODO"
    }
    return architecture

# 输出设计
print(design_ai_system())
""",
                    "solution_code": """def design_ai_system():
    """设计AI系统架构"""
    architecture = {
        "problem": "客户流失预测",
        "data_source": "数仓用户行为表",
        "feature_pipeline": "每日批处理，Airflow调度",
        "model_service": "FastAPI + Docker",
        "monitoring": "MLflow + Prometheus",
        "deployment": "Kubernetes + 蓝绿部署"
    }
    return architecture

print(design_ai_system())
""",
                    "test_cases": [
                        {"description": "返回架构字典", "expected": "dict"}
                    ],
                    "hints": ["考虑数据来源", "考虑部署方式", "考虑监控方案"]
                }
            }
        ]
    }
]

