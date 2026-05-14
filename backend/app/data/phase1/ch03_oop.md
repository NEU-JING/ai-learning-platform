# 面向对象: 超越Java的OOP

## 学习目标
- 掌握Python类定义与Java类的核心差异
- 理解多继承、MixIn、描述符等Java没有的OOP特性
- 学会用Pythonic的方式组织代码(不一定需要类)

---

## 1. 类定义基础差异

### 1.1 最简类

```java
// Java: 必须有class声明, 属性需声明类型
public class Dog {
    private String name;
    private int age;
    
    public Dog(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String info() {
        return name + ", " + age;
    }
}
```

```python
# Python: 极简版
class Dog:
    def __init__(self, name, age):    # 构造方法, self = Java的this
        self.name = name               # 属性无需声明, 直接赋值
        self.age = age
    
    def info(self):
        return f"{self.name}, {self.age}"
```

**关键差异**:
- `self`必须显式写在参数列表第一个位置(Java的`this`是隐式的)
- 属性不需要提前声明, 在`__init__`中赋值即可创建
- 没有public/private/protected关键字

### 1.2 访问控制——Python的"君子协定"

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self._balance = balance        # _前缀: 内部使用, 但外部仍可访问
        self.__secret = "s3cret"       # __前缀: 名称修饰, 非真正私有
    
    @property                          # 只读属性(类似Java的getter)
    def balance(self):
        return self._balance
    
    @balance.setter                    # 可写属性(类似setter)
    def balance(self, value):
        if value < 0:
            raise ValueError("余额不能为负")
        self._balance = value

account = BankAccount("Alice", 1000)
account.balance           # 1000(通过@property访问, 像属性不像方法)
account.balance = 500     # 通过@setter验证后赋值
account.balance = -100    # ValueError!
```

**Python哲学**: "我们都是成年人"——用`_`前缀表示"内部使用", 但不强制禁止访问。

---

## 2. 继承: 单继承 vs 多继承

### 2.1 单继承(和Java类似)

```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        raise NotImplementedError     # 类似Java的abstract

class Dog(Animal):
    def speak(self):
        return f"{self.name}说: 汪汪!"
```

### 2.2 多继承——Python有, Java没有

```python
class Loggable:
    '''MixIn: 为任何类添加日志功能'''
    def log(self, message):
        print(f"[{self.__class__.__name__}] {message}")

class Serializable:
    '''MixIn: 为任何类添加序列化功能'''
    def to_dict(self):
        return self.__dict__

class User(Loggable, Serializable):    # 多继承
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.log(f"用户创建: {name}")  # 来自Loggable

user = User("Alice", "a@b.com")
user.to_dict()          # {"name": "Alice", "email": "a@b.com"} -- 来自Serializable
```

**MixIn模式**: 多继承的正确用法是继承功能碎片(MixIn), 而不是继承多个"完整"的类。这替代了Java中接口+默认方法的组合。

### 2.3 MRO(方法解析顺序)

```python
class A:
    def greet(self): return "A"

class B(A):
    def greet(self): return "B"

class C(A):
    def greet(self): return "C"

class D(B, C):
    pass

D().greet()                  # "B"
print(D.__mro__)             # D -> B -> C -> A -> object
```

Python使用C3线性化算法确定方法查找顺序, 避免菱形继承的歧义。

---

## 3. 魔术方法: 运算符重载与协议

Python的"协议"替代了Java的"接口"——不要求声明implements, 只要实现了对应的方法, 就支持对应的行为。

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):                    # str() / print() 时调用
        return f"Vector({self.x}, {self.y})"
    
    def __add__(self, other):              # + 运算符
        return Vector(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):             # * 运算符
        return Vector(self.x * scalar, self.y * scalar)
    
    def __abs__(self):                     # abs() 函数
        return (self.x**2 + self.y**2)**0.5
    
    def __eq__(self, other):               # == 运算符
        return self.x == other.x and self.y == other.y
    
    def __len__(self):                     # len() 函数
        return int(abs(self))
    
    def __getitem__(self, index):          # [] 索引
        if index == 0: return self.x
        if index == 1: return self.y
        raise IndexError("Vector index out of range")

v1 = Vector(3, 4)
v2 = Vector(1, 2)
v1 + v2          # Vector(4, 6)
v1 * 3           # Vector(9, 12)
abs(v1)          # 5.0
len(v1)          # 5
v1[0]            # 3
```

**Java对比**: Java没有运算符重载(除了String的+), Python几乎可以重载所有运算符。

---

## 4. dataclass——现代Python的数据类

```python
from dataclasses import dataclass, field

@dataclass
class Student:
    name: str
    age: int
    scores: list = field(default_factory=list)  # 安全的默认值
    grade: str = "N/A"
    
    @property
    def average(self):
        return sum(self.scores) / len(self.scores) if self.scores else 0

# 自动生成 __init__, __repr__, __eq__
s1 = Student("Alice", 20, [90, 85, 92])
s2 = Student("Alice", 20, [90, 85, 92])
s1 == s2          # True(自动比较所有字段)
print(s1)         # Student(name='Alice', age=20, scores=[90, 85, 92], grade='N/A')
```

**Java对比**: 类似Java Record(Java 16+), 但dataclass可变, 更灵活。

---

## 5. 什么时候不用类

Python不是Java——不是所有东西都需要是类。

```python
# Java思维: 什么都要包在类里
class MathUtils:
    @staticmethod
    def add(a, b): return a + b
    @staticmethod
    def multiply(a, b): return a * b

# Pythonic: 直接用模块级函数
def add(a, b): return a + b
def multiply(a, b): return a * b
```

**经验法则**:
- 只有一两个函数? 用模块就够了
- 需要维护状态? 用类
- 需要多态? 用类或协议(Protocol)
- 只是传递数据? 用dataclass或NamedTuple

---

## 练习题

1. 实现一个`Money`类, 支持`+`、`-`、`*`运算和比较, 格式化输出
2. 实现一个`Validated`描述符, 验证属性值满足条件(如`age`必须是0-150的整数)
3. 用dataclass重构上面两个类中适合dataclass的那个
