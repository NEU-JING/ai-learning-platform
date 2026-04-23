"""
内置完整AI课程体系
包含从Python基础到AI团队Leader的完整学习路径
"""

COURSES_DATA = [
    {
        "title": "Phase 1: Python基础与AI入门",
        "description": "从零开始学习Python，掌握AI开发的基础编程技能。适合零基础学员。",
        "level": "beginner",
        "category": "python",
        "duration_hours": 40,
        "order_index": 1,
        "chapters": [
            {
                "title": "第1章：Python环境搭建与基础语法",
                "content": """# Python环境搭建与基础语法

## 学习目标
- 安装Python开发环境
- 理解Python基本语法
- 掌握变量、数据类型、运算符

## 1.1 Python简介

Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。

**特点：**
- 语法简洁清晰
- 丰富的标准库和第三方库
- 跨平台支持
- 广泛应用于AI、数据分析、Web开发

## 1.2 环境搭建

### 安装Python 3.9+
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 验证安装
python3 --version
```

### 虚拟环境（重要！）
```bash
# 创建虚拟环境
python3 -m venv ai-learning

# 激活环境
source ai-learning/bin/activate  # Linux/Mac
# 或 ai-learning\\Scripts\\activate  # Windows

# 退出环境
deactivate
```

## 1.3 基础语法

### 变量与数据类型
```python
# 变量不需要声明类型
name = "Alice"      # 字符串
age = 25           # 整数
height = 1.75      # 浮点数
is_student = True  # 布尔值

# 查看类型
print(type(name))   # <class 'str'>
```

### 基础数据结构
```python
# 列表（List）- 可变序列
fruits = ["apple", "banana", "cherry"]
fruits.append("date")
print(fruits[0])    # "apple"

# 字典（Dict）- 键值对
student = {
    "name": "张三",
    "age": 25,
    "grade": "A"
}
print(student["name"])

# 元组（Tuple）- 不可变
coordinates = (10, 20)

# 集合（Set）- 无序不重复
numbers = {1, 2, 3, 4, 5}
```

### 控制流
```python
# if语句
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"

# for循环
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# while循环
count = 0
while count < 5:
    print(count)
    count += 1
```

## 1.4 函数定义
```python
def greet(name, greeting="Hello"):
    \"\"\"函数的文档字符串（docstring）\"\"\"
    return f"{greeting}, {name}!"

# 调用
print(greet("Alice"))           # Hello, Alice!
print(greet("Bob", "Hi"))       # Hi, Bob!

# Lambda表达式
square = lambda x: x ** 2
print(square(5))  # 25
```

## 课后练习

1. 编写一个函数，接收一个列表，返回列表中所有偶数的和
2. 创建一个学生信息字典，包含姓名、年龄、成绩，并实现查询功能
3. 使用列表推导式生成1-100中所有能被3整除的数

## 学习提示
- 多动手练习，不要只看不动手
- 善用Python的交互式解释器（python3 -i）
- 遇到问题先查官方文档
""",
                "chapter_type": "text",
                "duration_minutes": 60,
                "order_index": 1
            },
            {
                "title": "第2章：Python面向对象编程",
                "content": """# Python面向对象编程

## 学习目标
- 理解面向对象编程概念
- 掌握类和对象的定义
- 学习继承和多态
- 理解装饰器

## 2.1 类与对象

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

# 创建对象
stu = Student("Alice", 20)
print(stu.introduce())
```

## 2.2 继承与多态

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

## 2.3 装饰器详解

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

# 使用装饰器
@my_decorator
def say_hello():
    print("Hello!")

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

## 2.4 魔法方法（Dunder Methods）

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __len__(self):
        return int((self.x ** 2 + self.y ** 2) ** 0.5)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

v1 = Vector(3, 4)
v2 = Vector(1, 2)
v3 = v1 + v2  # Vector(4, 6)
print(v3)     # Vector(4, 6)
print(len(v1))  # 5
```

## 课后练习

1. 设计一个`BankAccount`类，支持存款、取款、查询余额
2. 实现一个`Cache`装饰器，缓存函数结果
3. 创建一个`Shape`基类，派生出`Rectangle`和`Circle`，计算面积
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 2,
                "lab": {
                    "title": "实现一个图书管理系统",
                    "description": "使用面向对象编程思想，实现一个简单的图书管理系统",
                    "starter_code": """class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_borrowed = False
    
    def __repr__(self):
        return f"Book({self.title}, {self.author})"

class Library:
    def __init__(self, name):
        self.name = name
        self.books = []
        self.borrowed_books = {}
    
    def add_book(self, book):
        # TODO: 添加书籍到图书馆
        pass
    
    def borrow_book(self, isbn, user):
        # TODO: 借出书籍
        pass
    
    def return_book(self, isbn):
        # TODO: 归还书籍
        pass
    
    def search_by_title(self, title):
        # TODO: 根据标题搜索书籍
        pass
    
    def get_available_books(self):
        # TODO: 获取所有可借阅的书籍
        pass

# 测试代码
library = Library("城市图书馆")
library.add_book(Book("Python编程", "张三", "ISBN001"))
library.add_book(Book("机器学习", "李四", "ISBN002"))

print("可借阅书籍:", library.get_available_books())
library.borrow_book("ISBN001", "王五")
print("借阅后可借阅书籍:", library.get_available_books())
""",
                    "test_cases": [
                        {"input": "", "expected": "可借阅书籍", "description": "能获取可借阅书籍列表"}
                    ],
                    "hints": ["使用列表存储书籍", "使用字典记录借阅信息", "注意处理书籍不存在的情况"]
                }
            },
            {
                "title": "第3章：NumPy数值计算基础",
                "content": """# NumPy数值计算基础

## 学习目标
- 掌握NumPy数组操作
- 理解向量化计算
- 学会矩阵运算

## 3.1 NumPy简介

NumPy是Python科学计算的基础库，提供高性能的多维数组对象。

```python
import numpy as np

# 创建数组
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.array([[1, 2, 3], [4, 5, 6]])

# 特殊数组
zeros = np.zeros((3, 3))      # 3x3零矩阵
ones = np.ones((2, 4))        # 2x4全1矩阵
identity = np.eye(3)          # 3x3单位矩阵
random = np.random.rand(3, 3) # 3x3随机矩阵
arange = np.arange(0, 10, 2)  # [0, 2, 4, 6, 8]
linspace = np.linspace(0, 1, 5)  # [0, 0.25, 0.5, 0.75, 1]
```

## 3.2 数组操作

```python
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# 索引和切片
print(arr[0, 1])      # 2
print(arr[0:2, 1:3])  # [[2, 3], [5, 6]]
print(arr[:, 0])      # 第一列 [1, 4, 7]

# 形状操作
print(arr.shape)      # (3, 3)
print(arr.reshape(1, 9))  # 变为一行
print(arr.flatten())  # 展平为一维

# 数组运算
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

print(a + b)  # [5, 7, 9]
print(a * b)  # [4, 10, 18]
print(a ** 2) # [1, 4, 9]
```

## 3.3 矩阵运算

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# 矩阵乘法
C = np.dot(A, B)
# 或 C = A @ B

# 转置
A_T = A.T

# 逆矩阵
A_inv = np.linalg.inv(A)

# 行列式
det = np.linalg.det(A)

# 特征值和特征向量
eigenvalues, eigenvectors = np.linalg.eig(A)

# 解线性方程组 Ax = b
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
x = np.linalg.solve(A, b)
print(x)  # [2, 3]
```

## 3.4 向量化计算

```python
# 普通Python循环（慢）
def sum_squares_python(n):
    result = 0
    for i in range(n):
        result += i ** 2
    return result

# NumPy向量化（快100倍）
def sum_squares_numpy(n):
    return np.sum(np.arange(n) ** 2)

# 广播机制
a = np.array([[1, 2, 3], [4, 5, 6]])  # (2, 3)
b = np.array([10, 20, 30])            # (3,) -> 广播为 (2, 3)
print(a + b)
# [[11, 22, 33],
#  [14, 25, 36]]
```

## 课后练习

1. 使用NumPy实现矩阵乘法（不使用np.dot）
2. 计算一批数据的均值、方差、标准差
3. 实现图像数据的简单处理（翻转、旋转）
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 3
            },
            {
                "title": "第4章：Pandas数据处理",
                "content": """# Pandas数据处理

## 学习目标
- 掌握DataFrame操作
- 学会数据清洗
- 掌握数据分组与聚合

## 4.1 DataFrame基础

```python
import pandas as pd
import numpy as np

# 创建DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [25, 30, 35, 28],
    'city': ['北京', '上海', '广州', '深圳'],
    'salary': [50000, 60000, 75000, 55000]
}
df = pd.DataFrame(data)

# 基本信息
print(df.shape)      # (4, 4)
print(df.columns)    # Index(['name', 'age', 'city', 'salary'], dtype='object')
print(df.dtypes)     # 各列数据类型
print(df.describe()) # 统计摘要
```

## 4.2 数据选择与过滤

```python
# 选择列
names = df['name']
subset = df[['name', 'age']]

# 选择行
print(df.iloc[0])      # 第一行
print(df.iloc[0:2])    # 前两行
print(df.loc[0, 'name'])  # 第一行的name

# 条件过滤
adults = df[df['age'] >= 30]
high_earners = df[df['salary'] > 55000]
beijing_residents = df[df['city'] == '北京']

# 多条件
result = df[(df['age'] >= 25) & (df['salary'] > 50000)]
```

## 4.3 数据清洗

```python
# 处理缺失值
df.isnull().sum()              # 查看每列缺失值数量
df.dropna()                    # 删除包含缺失值的行
df.fillna(0)                   # 用0填充缺失值
df['age'].fillna(df['age'].mean())  # 用均值填充

# 处理重复值
df.duplicated().sum()          # 查看重复行数
df.drop_duplicates()           # 删除重复行

# 数据类型转换
df['age'] = df['age'].astype(int)
df['salary'] = df['salary'].astype(float)

# 字符串处理
df['name_upper'] = df['name'].str.upper()
df['name_lower'] = df['name'].str.lower()
df['name_length'] = df['name'].str.len()
```

## 4.4 分组与聚合

```python
# 按城市分组，计算平均年龄和工资
city_stats = df.groupby('city').agg({
    'age': 'mean',
    'salary': ['mean', 'sum', 'count']
})

# 透视表
pivot = df.pivot_table(
    values='salary',
    index='city',
    columns='age',
    aggfunc='mean'
)

# 多列分组
df.groupby(['city', 'age']).size()
```

## 4.5 数据合并

```python
# 创建两个DataFrame
df1 = pd.DataFrame({'key': ['A', 'B', 'C'], 'value1': [1, 2, 3]})
df2 = pd.DataFrame({'key': ['B', 'C', 'D'], 'value2': [4, 5, 6]})

# 合并（类似SQL JOIN）
merged = pd.merge(df1, df2, on='key', how='inner')   # 内连接
merged = pd.merge(df1, df2, on='key', how='left')    # 左连接
merged = pd.merge(df1, df2, on='key', how='outer')   # 外连接

# 纵向拼接
df_combined = pd.concat([df1, df2], ignore_index=True)
```

## 课后练习

1. 读取CSV文件，进行数据清洗和统计分析
2. 实现一个数据报告生成器（自动计算各项统计指标）
3. 对销售数据进行分组分析，找出最佳销售区域
""",
                "chapter_type": "code",
                "duration_minutes": 90,
                "order_index": 4
            }
        ]
    },
    {
        "title": "Phase 2: AI基础与机器学习",
        "description": "学习AI核心概念，掌握机器学习基础算法，为后续深度学习打下基础。",
        "level": "intermediate",
        "category": "ml",
        "duration_hours": 60,
        "order_index": 2,
        "chapters": [
            {
                "title": "第5章：机器学习基础概念",
                "content": """# 机器学习基础概念

## 学习目标
- 理解机器学习基本范式
- 掌握监督学习 vs 无监督学习
- 了解模型评估方法

## 5.1 什么是机器学习

**定义：** 机器学习是让计算机从数据中学习规律，而无需明确编程。

**传统编程 vs 机器学习：**

```
传统编程：
数据 + 规则 → 答案

机器学习：
数据 + 答案 → 规则（模型）
```

## 5.2 机器学习类型

### 监督学习（Supervised Learning）
有标签数据，学习输入到输出的映射。

**常见任务：**
- 分类（Classification）：预测离散类别
  - 邮件是否为垃圾邮件
  - 图片中的动物类别
  
- 回归（Regression）：预测连续值
  - 房价预测
  - 股票价格预测

### 无监督学习（Unsupervised Learning）
无标签数据，发现数据内在结构。

**常见任务：**
- 聚类（Clustering）：将相似数据分组
  - 客户分群
  - 文档主题分类
  
- 降维（Dimensionality Reduction）：减少特征数量
  - PCA主成分分析
  - t-SNE可视化

### 强化学习（Reinforcement Learning）
通过与环境交互学习最优策略。

**应用场景：**
- 游戏AI（AlphaGo）
- 自动驾驶
- 机器人控制

## 5.3 机器学习工作流程

```
1. 数据收集 → 2. 数据预处理 → 3. 特征工程 
→ 4. 模型选择 → 5. 训练 → 6. 评估 → 7. 部署
```

## 5.4 模型评估

### 分类指标

**准确率（Accuracy）：**
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

**精确率（Precision）：**
```
Precision = TP / (TP + FP)
```

**召回率（Recall）：**
```
Recall = TP / (TP + FN)
```

**F1分数：**
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

### 混淆矩阵

```
                预测值
              正类  负类
实际值  正类   TP    FN
        负类   FP    TN
```

### 回归指标

- **MAE**（平均绝对误差）
- **MSE**（均方误差）
- **RMSE**（均方根误差）
- **R²**（决定系数）

## 5.5 过拟合与欠拟合

**欠拟合（Underfitting）：**
- 模型太简单，无法捕捉数据规律
- 训练误差和测试误差都高

**过拟合（Overfitting）：**
- 模型太复杂，记住了训练数据噪声
- 训练误差低，测试误差高

**解决方案：**
- 欠拟合：增加模型复杂度、添加特征
- 过拟合：正则化、增加数据、早停、Dropout

## 课后练习

1. 解释分类和回归的区别，各举3个实际例子
2. 计算给定混淆矩阵的各项指标
3. 分析一个模型的过拟合/欠拟合情况
""",
                "chapter_type": "text",
                "duration_minutes": 60,
                "order_index": 1
            }
        ]
    },
    {
        "title": "Phase 3: LangChain与AI Agent开发",
        "description": "深入学习LangChain框架，掌握AI Agent开发技术，能够构建智能应用。",
        "level": "advanced",
        "category": "langchain",
        "duration_hours": 80,
        "order_index": 3,
        "chapters": [
            {
                "title": "第6章：LangChain基础",
                "content": """# LangChain基础

## 学习目标
- 理解LangChain核心概念
- 掌握Chains和Prompts
- 学会使用不同的LLM

## 6.1 LangChain简介

LangChain是一个用于开发LLM应用的框架，提供了：
- 统一的LLM接口
- 链式调用（Chains）
- 记忆管理（Memory）
- 工具集成（Tools）
- Agent系统

## 6.2 安装与配置

```bash
pip install langchain langchain-openai

# 设置API密钥
export OPENAI_API_KEY="your-key-here"
```

## 6.3 基础使用

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 创建LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 直接调用
response = llm.invoke("你好，请介绍一下机器学习")
print(response.content)

# 使用Prompt模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}。"),
    ("human", "{question}")
])

chain = prompt | llm
result = chain.invoke({
    "role": "数据科学家",
    "question": "什么是过拟合？"
})
print(result.content)
```

## 6.4 Chains详解

### SimpleChain（简单链）

```python
from langchain_core.output_parsers import StrOutputParser

# 构建链
template = "将以下内容翻译成中文：{text}"
prompt = ChatPromptTemplate.from_template(template)

chain = prompt | llm | StrOutputParser()

# 执行
result = chain.invoke({"text": "Hello, world!"})
print(result)  # 你好，世界！
```

### Sequential Chain（顺序链）

```python
from langchain_core.runnables import RunnablePassthrough

# 第一个链：生成故事标题
title_template = "根据主题'{topic}'生成一个吸引人的故事标题"
title_chain = (
    ChatPromptTemplate.from_template(title_template) 
    | llm 
    | StrOutputParser()
)

# 第二个链：根据标题写故事
story_template = "根据标题'{title}'写一个100字的故事"
story_chain = (
    ChatPromptTemplate.from_template(story_template) 
    | llm 
    | StrOutputParser()
)

# 组合链
full_chain = (
    {"topic": RunnablePassthrough()}
    | {"title": title_chain}
    | {"story": story_chain}
)

result = full_chain.invoke("人工智能")
print(result)
```

## 6.5 Memory（记忆）

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# 创建记忆
memory = ConversationBufferMemory()

# 创建对话链
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 多轮对话
conversation.predict(input="你好，我叫张三")
conversation.predict(input="我叫什么名字？")  # 能记住之前的对话
```

## 6.6 Tools和Agent

```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.tools import tool

# 定义工具
@tool
def search(query: str) -> str:
    \"\"\"搜索信息\"\"\"
    # 这里可以接入真实的搜索引擎
    return f"搜索结果：关于'{query}'的信息..."

@tool
def calculate(expression: str) -> str:
    \"\"\"计算数学表达式\"\"\"
    try:
        result = eval(expression)
        return str(result)
    except:
        return "计算错误"

tools = [search, calculate]

# 创建Agent
from langchain_core.prompts import MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个 helpful 助手，可以使用工具来回答问题。"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 运行
response = agent_executor.invoke({"input": "3乘以7等于多少？"})
print(response["output"])
```

## 课后练习

1. 实现一个翻译链，支持多语言翻译
2. 创建一个带记忆的问答机器人
3. 设计一个Agent，能查询天气并给出穿衣建议
""",
                "chapter_type": "code",
                "duration_minutes": 120,
                "order_index": 1
            }
        ]
    },
    {
        "title": "Phase 4: AI团队Leadership",
        "description": "培养AI项目管理能力，学习如何带领AI团队，从技术专家成长为技术Leader。",
        "level": "expert",
        "category": "leadership",
        "duration_hours": 50,
        "order_index": 4,
        "chapters": [
            {
                "title": "第7章：AI项目管理",
                "content": """# AI项目管理

## 学习目标
- 掌握AI项目生命周期
- 学会需求分析与技术选型
- 掌握AI项目风险管理

## 7.1 AI项目 vs 传统项目

| 维度 | 传统软件项目 | AI项目 |
|------|-------------|--------|
| 需求确定性 | 高 | 低 |
| 交付物 | 明确的代码 | 概率模型 |
| 成功标准 | 功能正确 | 准确率达标 |
| 不确定性 | 低 | 高 |
| 迭代频率 | 较低 | 高频 |

## 7.2 AI项目生命周期

### Phase 1: 问题定义
- 明确业务目标
- 确定成功指标（Accuracy、Precision、Recall等）
- 评估数据可用性

### Phase 2: 数据准备
- 数据收集策略
- 数据清洗与标注
- 数据质量评估

### Phase 3: 模型开发
- 基线模型建立
- 模型迭代优化
- 实验追踪与管理

### Phase 4: 部署与监控
- 模型服务化
- A/B测试
- 持续监控与迭代

## 7.3 需求分析框架

**5W1H分析法：**
- **What**: 要解决什么问题？
- **Why**: 为什么需要AI？传统方法不行吗？
- **Who**: 谁是最终用户？
- **When**: 什么时候需要上线？
- **Where**: 在什么场景下使用？
- **How**: 如何衡量成功？

**可行性评估清单：**
- [ ] 是否有足够的标注数据？
- [ ] 业务目标是否可量化？
- [ ] 技术方案是否可行？
- [ ] 资源（算力、人力）是否充足？
- [ ] 合规性是否满足？

## 7.4 技术选型决策

### 选型维度

1. **模型选择**
   - 自研 vs 开源 vs 商业API
   - 大模型 vs 小模型
   - 通用模型 vs 领域模型

2. **技术栈选择**
   - 编程语言（Python/Rust/Java）
   - 框架（PyTorch/TensorFlow/JAX）
   - 部署方案（云服务/私有化/边缘）

3. **数据基础设施**
   - 数据存储（数据湖/数据仓库）
   - 特征平台
   - 数据标注工具

### 决策矩阵示例

```
评估维度         权重    方案A    方案B    方案C
技术成熟度       25%      9        7        8
团队熟悉度       20%      8        9        6
性能表现         20%      7        8        9
成本             20%      6        8        7
可维护性         15%      8        7        7
─────────────────────────────────────────────
加权总分                 7.55     7.85     7.45
```

## 7.5 风险管理

### 常见风险

| 风险类型 | 具体表现 | 应对策略 |
|---------|---------|---------|
| 数据风险 | 数据质量差、标注不准确 | 数据验证流程、多轮审核 |
| 模型风险 | 性能不达预期、泛化能力差 | 快速原型、逐步迭代 |
| 技术风险 | 新技术不成熟、人才短缺 | 技术预研、培养计划 |
| 业务风险 | 需求变更、业务理解偏差 | 紧密协作、快速反馈 |
| 合规风险 | 数据隐私、模型偏见 | 合规审查、伦理评估 |

### 风险登记册模板

```
风险ID: R001
风险描述: 标注数据质量不达标
可能性: 高
影响程度: 高
风险等级: 高
应对策略: 
  1. 建立数据质量检查流程
  2. 设置多轮标注和审核
  3. 准备数据增强方案
负责人: 数据团队负责人
状态: 监控中
```

## 7.6 MLOps实践

**持续集成/持续部署（CI/CD）：**
```
代码提交 → 自动测试 → 模型训练 → 模型验证 → 自动部署
```

**实验管理：**
- 使用MLflow、Wandb等工具
- 记录超参数、指标、代码版本
- 模型版本管理

**监控体系：**
- 模型性能监控（准确率、延迟）
- 数据漂移检测
- 业务指标监控

## 课后练习

1. 为一个AI客服项目制定完整的项目计划
2. 评估一个AI项目的技术选型方案
3. 设计一个AI项目的风险登记册
""",
                "chapter_type": "text",
                "duration_minutes": 90,
                "order_index": 1
            }
        ]
    }
]

# 实验课程详细数据
LABS_DATA = [
    {
        "chapter_title": "Python基础实验",
        "labs": [
            {
                "title": "实验1：变量与数据类型",
                "description": "练习Python基本数据类型和变量操作",
                "starter_code": "# 练习1：创建不同类型的变量\n# 请创建以下变量：\n# 1. name: 你的名字（字符串）\n# 2. age: 你的年龄（整数）\n# 3. height: 你的身高（浮点数）\n# 4. is_student: 是否为学生（布尔值）\n\n# 在这里写代码\n\n\n# 打印变量信息\n# print(f\"姓名: {name}\")\n",
                "test_cases": [
                    {"description": "变量类型正确", "check": "type_check"}
                ],
                "hints": ["使用=赋值", "字符串用引号包裹", "布尔值首字母大写"]
            }
        ]
    }
]
