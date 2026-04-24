"""
内置课程数据 - AI学习平台完整课程体系
从入门到AI团队Leader的完整学习路径
"""

COURSES_DATA = [
    {
        "title": "Phase 1: Python for AI",
        "description": "为零基础学员设计的Python编程入门课程，涵盖基础语法、数据结构和常用库，为AI学习打下坚实基础。",
        "level": "beginner",
        "category": "python",
        "duration_hours": 28,
        "order_index": 1,
        "chapters": [
            {
                "title": "Day 1 - Python快速上手",
                "content": """# Day 1 - Python快速上手：Python vs Java语法对比

## 主题
从Java开发者的视角快速掌握Python核心语法

## 学习目标
- 理解Python与Java的核心差异（动态类型、缩进语法、一切皆对象）
- 掌握Python基本数据类型和控制流
- 完成Python环境配置，能独立运行脚本

## 核心内容

### 1. 语言设计理念对比

| 特性 | Java | Python |
|------|------|--------|
| 类型系统 | 静态类型，编译期检查 | 动态类型，运行时确定 |
| 语法风格 | 大括号 `{}` 定义代码块 | 缩进定义代码块 |
| 执行方式 | 编译为字节码，JVM执行 | 解释执行 |

### 2. 基础语法

```python
# 变量不需要声明类型
name = "Alice"      # 字符串
age = 25            # 整数
height = 1.75       # 浮点数
is_student = True   # 布尔值

# 列表 - 对应Java的ArrayList
fruits = ["apple", "banana", "cherry"]
fruits.append("date")
print(fruits[0])    # 访问: apple

# 字典 - 对应Java的HashMap
student = {"name": "张三", "age": 25}
print(student["name"])  # 访问: 张三
```

### 3. 控制流

```python
# if-elif-else
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"     # 输出B
else:
    grade = "C"

# for循环
for i in range(5):          # 0,1,2,3,4
    print(i)

# while循环
count = 0
while count < 5:
    print(count)
    count += 1
```

## 练习题
编写一个程序，接收用户输入的数字列表，计算并输出平均值。""",
                "order_index": 1,
                "chapter_type": "code",
                "duration_minutes": 120
            },
            {
                "title": "Day 2 - Python函数与类",
                "content": """# Day 2 - Python函数与类

## 主题
函数式编程与面向对象

## 学习目标
- 掌握Python函数定义与lambda
- 理解类的定义与继承
- 学习装饰器

## 核心内容

### 1. 函数定义

```python
# 基本函数
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# 可变参数
def sum_all(*args):
    return sum(args)

# 关键字参数
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

# Lambda表达式
square = lambda x: x ** 2
```

### 2. 类与继承

```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

dog = Dog("Buddy")
print(dog.speak())  # Buddy says Woof!
```

### 3. 装饰器

```python
def timing(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timing
def slow_function():
    import time
    time.sleep(1)
    return "Done"
```""",
                "order_index": 2,
                "chapter_type": "code",
                "duration_minutes": 90,
                "lab": {
                    "title": "实现数据验证装饰器",
                    "description": "创建一个装饰器，用于验证函数参数类型",
                    "starter_code": "def validate_types(**types):\n    \"\"\"\n    装饰器：验证函数参数类型\n    用法: @validate_types(name=str, age=int)\n    \"\"\"\n    # 你的代码在这里\n    pass\n\n@validate_types(name=str, age=int)\ndef create_user(name, age):\n    return {\"name\": name, \"age\": age}\n\n# 测试\nprint(create_user(\"Alice\", 25))  # 应该正常\n# print(create_user(\"Bob\", \"25\"))  # 应该报错\n",
                    "solution_code": "import inspect\nfrom functools import wraps\n\ndef validate_types(**types):\n    def decorator(func):\n        @wraps(func)\n        def wrapper(*args, **kwargs):\n            sig = inspect.signature(func)\n            params = list(sig.parameters.keys())\n            \n            for i, arg in enumerate(args):\n                if i < len(params):\n                    param_name = params[i]\n                    if param_name in types:\n                        if not isinstance(arg, types[param_name]):\n                            raise TypeError(\n                                f\"{param_name} should be {types[param_name].__name__}\")\n            \n            for key, value in kwargs.items():\n                if key in types:\n                    if not isinstance(value, types[key]):\n                        raise TypeError(\n                            f\"{key} should be {types[key].__name__}\")\n            \n            return func(*args, **kwargs)\n        return wrapper\n    return decorator",
                    "test_cases": [{"input": "create_user('Alice', 25)", "expected": "{'name': 'Alice', 'age': 25}"}]
                }
            }
        ]
    },
    {
        "title": "Phase 2: LangChain框架",
        "description": "深入学习LangChain框架，掌握Chain、Agent、Memory等核心概念，能够构建复杂的AI应用。",
        "level": "intermediate",
        "category": "langchain",
        "duration_hours": 42,
        "order_index": 2,
        "chapters": [
            {
                "title": "LangChain基础概念",
                "content": """# LangChain基础概念

## 什么是LangChain？
LangChain是一个用于开发LLM应用的框架，提供了：
- 模型接口抽象
- 提示词模板管理
- 链式调用（Chain）
- 工具集成（Agent）
- 记忆管理（Memory）

## 核心组件

### 1. LLM接口

```python
from langchain.llms import OpenAI

llm = OpenAI(temperature=0.7)
result = llm.predict("你好，请介绍一下自己")
print(result)
```

### 2. Prompt模板

```python
from langchain import PromptTemplate

template = """
你是一位{role}。请用{style}的风格回答以下问题：
问题：{question}
"""

prompt = PromptTemplate(
    input_variables=["role", "style", "question"],
    template=template
)

formatted = prompt.format(
    role="技术专家",
    style="通俗易懂",
    question="什么是机器学习？"
)
```

### 3. Chain链式调用

```python
from langchain import LLMChain

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.predict(
    role="数据科学家",
    style="专业",
    question="解释神经网络"
)
```

## 实践项目
构建一个简单的问答机器人，能够根据用户问题选择合适的回答风格。""",
                "order_index": 1,
                "chapter_type": "code",
                "duration_minutes": 120
            },
            {
                "title": "Agent与工具调用",
                "content": """# Agent与工具调用

## 什么是Agent？
Agent是LangChain中能够自主决策、调用工具的AI代理。

## 核心概念

### 1. 工具定义

```python
from langchain.tools import Tool

def search_web(query: str) -> str:
    \"\"\"模拟网络搜索\"\"\"\n    return f\"搜索结果：{query}的相关信息...\"

tools = [\n    Tool(\n        name=\"Search\",\n        func=search_web,\n        description=\"用于搜索网络信息\"\n    )\n]\n```

### 2. 创建Agent

```python
from langchain.agents import initialize_agent, AgentType

agent = initialize_agent(\n    tools=tools,\n    llm=llm,\n    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,\n    verbose=True\n)\n
agent.run(\"搜索Python最新版本的信息\")
```

### 3. 自定义Agent

```python
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.schema import AgentAction, AgentFinish

# 实现自定义逻辑
class MyAgent:
    def plan(self, intermediate_steps, **kwargs):
        # 决策逻辑
        pass
```

## 实战：构建数据分析师Agent
创建一个能够分析CSV数据、生成图表的AI Agent。""",
                "order_index": 2,
                "chapter_type": "lab",
                "duration_minutes": 180
            }
        ]
    },
    {
        "title": "Phase 3: AI Agent开发实战",
        "description": "通过实际项目掌握AI Agent开发，包括多Agent协作、RAG系统构建、自动化工作流设计。",
        "level": "advanced",
        "category": "agent",
        "duration_hours": 56,
        "order_index": 3,
        "chapters": [
            {
                "title": "多Agent协作架构",
                "content": """# 多Agent协作架构

## 为什么需要多Agent？
复杂任务需要多个专业Agent协作完成，类似团队分工。

## 架构模式

### 1. 主从模式
```
主Agent (协调者)
    ├─ Agent A (数据处理)
    ├─ Agent B (代码生成)
    └─ Agent C (代码审查)
```

### 2. 流水线模式
```
输入 → Agent 1 → Agent 2 → Agent 3 → 输出
```

## 实现示例

```python
class MultiAgentSystem:
    def __init__(self):
        self.agents = {}
        self.coordinator = None\n    \n    def register_agent(self, name, agent):\n        self.agents[name] = agent\n    \n    def execute(self, task):\n        # 协调逻辑\n        plan = self.coordinator.plan(task)\n        results = []\n        for step in plan:\n            agent = self.agents[step.agent_name]\n            result = agent.execute(step.action)\n            results.append(result)\n        return self.coordinator.synthesize(results)\n```

## 案例：软件开发团队Agent
- 产品经理Agent：需求分析
- 架构师Agent：系统设计
- 开发者Agent：代码实现
- 测试员Agent：质量保障""",
                "order_index": 1,
                "chapter_type": "code",
                "duration_minutes": 240
            },
            {
                "title": "RAG系统构建",
                "content": """# RAG系统构建（检索增强生成）

## 什么是RAG？
RAG (Retrieval-Augmented Generation) 结合检索和生成，让AI能够基于私有知识库回答问题。

## 架构流程
```
用户问题 → 向量化 → 检索相关文档 → 构建Prompt → LLM生成回答
```

## 核心实现

### 1. 文档向量化

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# 加载文档
from langchain.document_loaders import TextLoader
loader = TextLoader("knowledge.txt")
documents = loader.load()

# 分块
from langchain.text_splitter import CharacterTextSplitter
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

# 创建向量数据库
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(texts, embeddings)
```

### 2. 检索与生成

```python
# 检索相关文档
retriever = vectorstore.as_retriever()
relevant_docs = retriever.get_relevant_documents("问题内容")

# 构建增强Prompt
context = "\\n".join([doc.page_content for doc in relevant_docs])
prompt = f"""基于以下上下文回答问题：
{context}

问题：{question}
"""

# 生成回答
answer = llm.predict(prompt)
```

## 实践项目
构建一个企业内部知识库问答系统。""",
                "order_index": 2,
                "chapter_type": "lab",
                "duration_minutes": 300
            }
        ]
    },
    {
        "title": "Phase 4: AI团队领导力",
        "description": "培养AI团队Leadership能力，包括项目管理、技术决策、团队协作和风险控制。",
        "level": "expert",
        "category": "leadership",
        "duration_hours": 28,
        "order_index": 4,
        "chapters": [
            {
                "title": "AI项目管理",
                "content": """# AI项目管理

## AI项目的特殊性

### 与传统软件开发的区别
1. **不确定性**：模型性能难以预估
2. **数据依赖**：质量决定上限
3. **迭代频繁**：需要持续优化
4. **跨学科**：需要数据科学家、工程师、业务专家协作

## 项目管理框架

### 1. 阶段划分
```
Phase 1: 问题定义 → Phase 2: 数据准备 → Phase 3: 模型开发 → Phase 4: 部署运维
```

### 2. 里程碑设定
- **M1**: 数据收集完成
- **M2**: 基线模型建立
- **M3**: 模型性能达标
- **M4**: 生产环境部署

### 3. 风险管理
| 风险类型 | 应对策略 |
|---------|----------|
| 数据质量问题 | 数据验证流程、备用数据源 |
| 模型性能不达预期 | A/B测试、回滚机制 |
| 延迟/成本超标 | 分阶段交付、云资源弹性伸缩 |

## 实践工具
- 项目管理：Jira / Linear
- 实验追踪：MLflow / Weights & Biases
- 协作：Notion / Confluence""",
                "order_index": 1,
                "chapter_type": "text",
                "duration_minutes": 120
            },
            {
                "title": "技术决策与架构设计",
                "content": """# 技术决策与架构设计

## AI系统架构设计原则

### 1. 可扩展性
- 模型服务化（Model-as-a-Service）
- 水平扩展设计
- 异步处理队列

### 2. 可观测性
```python
# 监控指标
- 请求延迟 (P50, P95, P99)
- 吞吐量 (QPS)
- 模型性能指标 (Accuracy, F1, AUC)
- 资源使用 (CPU, GPU, Memory)
```

### 3. 容错设计
- 降级策略（Fallback）
- 熔断机制（Circuit Breaker）
- 限流（Rate Limiting）

## 技术选型决策树

```
模型部署方式？
├── 实时推理 (<100ms) → 本地部署 / 边缘计算
├── 批量处理 → 离线Pipeline
└── 混合场景 → 异步队列 + 缓存

模型更新频率？
├── 高频 (每天) → CI/CD自动化
└── 低频 (每月) → 手动发布流程
```

## 案例：推荐系统架构
```
用户请求 → API Gateway → Feature Store → Model Service → Ranking → Response
                ↓              ↓              ↓
            限流/熔断      特征缓存       模型版本管理
```

## 决策文档模板
```markdown
# ADR-001: 模型服务选型

## 背景
需要选择模型部署方案

## 考虑的选项
1. 自研服务
2. Triton Inference Server
3. TorchServe

## 决策
选择 Triton

## 原因
- 多框架支持
- 动态批处理
- GPU优化

## 后果
需要团队学习NVIDIA生态
```""",
                "order_index": 2,
                "chapter_type": "text",
                "duration_minutes": 180
            }
        ]
    }
]


def init_courses_data(db):
    """初始化课程数据到数据库"""
    from app.models import Course, Chapter, Lab
    
    for course_data in COURSES_DATA:
        chapters_data = course_data.pop("chapters", [])
        
        # 检查课程是否已存在
        existing = db.query(Course).filter(Course.title == course_data["title"]).first()
        if existing:
            continue
        
        # 创建课程
        course = Course(**course_data)
        db.add(course)
        db.flush()  # 获取course.id
        
        # 创建章节
        for chapter_data in chapters_data:
            lab_data = chapter_data.pop("lab", None)
            
            chapter = Chapter(course_id=course.id, **chapter_data)
            db.add(chapter)
            db.flush()
            
            # 创建实验
            if lab_data:
                lab = Lab(chapter_id=chapter.id, **lab_data)
                db.add(lab)
    
    db.commit()
    print(f"✅ 已初始化 {len(COURSES_DATA)} 门课程")
