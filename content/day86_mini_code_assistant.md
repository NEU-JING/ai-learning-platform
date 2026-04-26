# Day 86 - 构建Mini Code Assistant

> **目标**: 实现一个能理解代码库并回答问题的极简AI编程助手
> **预计时长**: 2小时
> **前置知识**: Day 85内容、Python基础、API调用

---

## 🎯 今日学习目标

完成本日学习后，你将能够：
1. 使用AST解析代码结构
2. 实现基于RAG的代码检索系统
3. 构建多轮对话上下文管理
4. 开发一个可运行的Mini Code Assistant原型

---

## 📖 核心内容

### 1. AST抽象语法树基础

#### 1.1 什么是AST

AST（Abstract Syntax Tree，抽象语法树）是代码的结构化表示，将源代码转换为树形数据结构：

```python
# 源代码
def greet(name):
    return f"Hello, {name}!"

# AST表示（简化）
FunctionDef(
    name='greet',
    args=Arguments(args=[Arg(arg='name')]),
    body=[
        Return(
            value=JoinedStr(
                values=[
                    Constant(value='Hello, '),
                    FormattedValue(value=Name(id='name'))
                ]
            )
        )
    ]
)
```

#### 1.2 Python AST解析

```python
import ast
from typing import List, Dict, Any

class CodeAnalyzer:
    """代码分析器 - 提取代码结构和符号"""
    
    def __init__(self, code: str):
        self.tree = ast.parse(code)
        self.symbols = {
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": []
        }
    
    def analyze(self) -> Dict[str, Any]:
        """分析代码并提取符号"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self._extract_function(node)
            elif isinstance(node, ast.ClassDef):
                self._extract_class(node)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                self._extract_import(node)
        
        return self.symbols
    
    def _extract_function(self, node: ast.FunctionDef):
        """提取函数信息"""
        func_info = {
            "name": node.name,
            "line": node.lineno,
            "args": [arg.arg for arg in node.args.args],
            "docstring": ast.get_docstring(node),
            "complexity": self._calculate_complexity(node)
        }
        self.symbols["functions"].append(func_info)
    
    def _extract_class(self, node: ast.ClassDef):
        """提取类信息"""
        class_info = {
            "name": node.name,
            "line": node.lineno,
            "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
            "docstring": ast.get_docstring(node)
        }
        self.symbols["classes"].append(class_info)
    
    def _extract_import(self, node):
        """提取导入信息"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.symbols["imports"].append({
                    "name": alias.name,
                    "alias": alias.asname,
                    "line": node.lineno
                })
        elif isinstance(node, ast.ImportFrom):
            self.symbols["imports"].append({
                "module": node.module,
                "names": [alias.name for alias in node.names],
                "line": node.lineno
            })
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度（简化版）"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def get_code_snippet(self, line_start: int, line_end: int) -> str:
        """获取指定行范围的代码片段"""
        lines = ast.unparse(self.tree).split('\n')
        return '\n'.join(lines[line_start-1:line_end])

# 使用示例
code = '''
import json
from typing import List

class DataProcessor:
    """数据处理类"""
    
    def __init__(self, source: str):
        self.source = source
        self.data = []
    
    def load(self) -> List[dict]:
        """加载数据"""
        with open(self.source, 'r') as f:
            self.data = json.load(f)
        return self.data
    
    def filter(self, condition: callable) -> List[dict]:
        """过滤数据"""
        return [item for item in self.data if condition(item)]
'''

analyzer = CodeAnalyzer(code)
symbols = analyzer.analyze()
print(json.dumps(symbols, indent=2, ensure_ascii=False))
```

#### 1.3 代码摘要生成

```python
class CodeSummarizer:
    """代码摘要生成器"""
    
    def summarize_function(self, func_info: dict) -> str:
        """为函数生成自然语言摘要"""
        summary = f"函数 '{func_info['name']}'"
        
        if func_info['args']:
            summary += f"，接受参数: {', '.join(func_info['args'])}"
        else:
            summary += "，无参数"
        
        if func_info['docstring']:
            summary += f"。功能: {func_info['docstring']}"
        
        summary += f"。代码行数: {func_info.get('line', '未知')}"
        
        return summary
    
    def summarize_class(self, class_info: dict) -> str:
        """为类生成自然语言摘要"""
        summary = f"类 '{class_info['name']}'"
        
        if class_info['bases']:
            summary += f"，继承自 {', '.join(class_info['bases'])}"
        
        if class_info['methods']:
            summary += f"。包含方法: {', '.join(class_info['methods'])}"
        
        if class_info['docstring']:
            summary += f"。{class_info['docstring']}"
        
        return summary
```

---

### 2. RAG代码检索系统

#### 2.1 向量嵌入与索引

```python
import numpy as np
from typing import List, Tuple
import hashlib

class SimpleEmbedding:
    """简化版嵌入生成器（实际使用OpenAI/SentenceTransformers）"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def embed(self, text: str) -> np.ndarray:
        """
        生成文本的向量表示
        注意：这是简化实现，实际应使用预训练模型
        """
        # 使用哈希作为简化嵌入（仅演示用）
        hash_val = hashlib.md5(text.encode()).hexdigest()
        np.random.seed(int(hash_val[:8], 16))
        return np.random.randn(self.dimension)
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

class CodebaseIndex:
    """代码库索引 - RAG检索基础"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.embedder = SimpleEmbedding()
        self.documents: List[dict] = []
        self.embeddings: List[np.ndarray] = []
    
    def index_file(self, file_path: str, content: str):
        """索引单个文件"""
        # 1. 解析代码
        try:
            analyzer = CodeAnalyzer(content)
            symbols = analyzer.analyze()
        except:
            symbols = {"functions": [], "classes": []}
        
        # 2. 分块（简化版：按函数/类分块）
        chunks = []
        
        for func in symbols.get("functions", []):
            chunk_text = f"Function: {func['name']}\n"
            chunk_text += f"Args: {', '.join(func['args'])}\n"
            chunk_text += f"Doc: {func.get('docstring', 'No docstring')}"
            
            chunks.append({
                "type": "function",
                "name": func["name"],
                "content": chunk_text,
                "file": file_path,
                "line": func.get("line", 0)
            })
        
        for cls in symbols.get("classes", []):
            chunk_text = f"Class: {cls['name']}\n"
            chunk_text += f"Methods: {', '.join(cls.get('methods', []))}\n"
            chunk_text += f"Doc: {cls.get('docstring', 'No docstring')}"
            
            chunks.append({
                "type": "class",
                "name": cls["name"],
                "content": chunk_text,
                "file": file_path,
                "line": cls.get("line", 0)
            })
        
        # 3. 生成嵌入
        for chunk in chunks:
            embedding = self.embedder.embed(chunk["content"])
            self.documents.append(chunk)
            self.embeddings.append(embedding)
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[dict, float]]:
        """搜索相关代码片段"""
        query_embedding = self.embedder.embed(query)
        
        # 计算相似度
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            sim = self.embedder.similarity(query_embedding, doc_embedding)
            similarities.append((self.documents[i], sim))
        
        # 排序返回Top-K
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def build_index(self, file_contents: dict):
        """构建完整索引"""
        for file_path, content in file_contents.items():
            if file_path.endswith('.py'):
                self.index_file(file_path, content)
        
        print(f"索引完成: {len(self.documents)} 个代码块")
```

#### 2.2 检索增强提示构建

```python
class RAGPromptBuilder:
    """RAG增强的Prompt构建器"""
    
    def __init__(self, codebase_index: CodebaseIndex):
        self.index = codebase_index
    
    def build_prompt(self, query: str, conversation_history: List[dict] = None) -> str:
        """构建增强的Prompt"""
        
        # 1. 检索相关代码
        relevant_chunks = self.index.search(query, top_k=3)
        
        # 2. 构建上下文
        context = "\n\n".join([
            f"【{chunk['type']}】{chunk['name']} (文件: {chunk['file']})\n{chunk['content']}"
            for chunk, score in relevant_chunks
        ])
        
        # 3. 构建系统提示
        system_prompt = f"""你是一个专业的代码助手。基于以下代码库信息回答用户问题。

## 相关代码上下文
{context}

## 回答要求
1. 基于提供的代码上下文回答
2. 如果代码片段不够，说明需要更多信息
3. 提供具体的代码示例和解释
4. 如果涉及修改，展示完整的修改方案"""
        
        # 4. 组合完整提示
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加当前问题
        messages.append({"role": "user", "content": query})
        
        return messages
```

---

### 3. 多轮对话上下文管理

#### 3.1 对话状态机

```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ConversationState(Enum):
    """对话状态"""
    INITIAL = "initial"           # 初始状态
    GATHERING_INFO = "gathering"  # 收集信息
    PROPOSING_SOLUTION = "proposing"  # 提出方案
    EXECUTING = "executing"       # 执行中
    CONFIRMING = "confirming"     # 等待确认
    COMPLETED = "completed"       # 已完成

@dataclass
class Message:
    """对话消息"""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

@dataclass
class ConversationContext:
    """对话上下文"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    state: ConversationState = ConversationState.INITIAL
    codebase_context: dict = field(default_factory=dict)
    pending_actions: List[dict] = field(default_factory=list)
    
    def add_message(self, role: str, content: str, metadata: dict = None):
        """添加消息"""
        self.messages.append(Message(
            role=role,
            content=content,
            metadata=metadata or {}
        ))
    
    def get_recent_messages(self, n: int = 10) -> List[Message]:
        """获取最近N条消息"""
        return self.messages[-n:]
    
    def get_conversation_summary(self) -> str:
        """获取对话摘要（用于长对话压缩）"""
        # 简化版：返回用户最初的问题和当前状态
        user_messages = [m for m in self.messages if m.role == "user"]
        if user_messages:
            return f"用户最初问题: {user_messages[0].content[:100]}...\n当前状态: {self.state.value}"
        return "新对话"
    
    def clear(self):
        """清空对话"""
        self.messages = []
        self.state = ConversationState.INITIAL
        self.pending_actions = []
```

#### 3.2 上下文窗口管理

```python
class ContextWindowManager:
    """上下文窗口管理 - 处理长对话的Token限制"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.token_estimate_ratio = 4  # 粗略估计：1 token ≈ 4字符
    
    def estimate_tokens(self, text: str) -> int:
        """估计文本的token数"""
        return len(text) // self.token_estimate_ratio
    
    def trim_context(self, messages: List[Message]) -> List[Message]:
        """裁剪上下文以适应token限制"""
        total_tokens = 0
        trimmed = []
        
        # 从后往前添加，保留最近的消息
        for msg in reversed(messages):
            msg_tokens = self.estimate_tokens(msg.content)
            if total_tokens + msg_tokens > self.max_tokens:
                break
            trimmed.insert(0, msg)
            total_tokens += msg_tokens
        
        return trimmed
    
    def compress_context(self, messages: List[Message]) -> List[Message]:
        """压缩长对话上下文"""
        if len(messages) <= 5:
            return messages
        
        # 保留：系统提示 + 最近5条 + 摘要
        system_msgs = [m for m in messages if m.role == "system"]
        recent_msgs = messages[-5:]
        
        # 中间部分生成摘要
        middle_msgs = messages[len(system_msgs):-5]
        if middle_msgs:
            summary = self._generate_summary(middle_msgs)
            summary_msg = Message(role="system", content=f"[之前对话摘要] {summary}")
            return system_msgs + [summary_msg] + recent_msgs
        
        return system_msgs + recent_msgs
    
    def _generate_summary(self, messages: List[Message]) -> str:
        """生成对话摘要（简化版）"""
        user_msgs = [m.content for m in messages if m.role == "user"]
        if user_msgs:
            return f"用户之前询问了: {'; '.join(user_msgs[:3])}"
        return "之前的对话内容"
```

---

### 4. Mini Code Assistant 完整实现

```python
# mini_code_assistant.py
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
import uuid

class MiniCodeAssistant:
    """
    极简AI编程助手
    
    功能：
    1. 理解代码库结构
    2. 回答代码相关问题
    3. 支持多轮对话
    4. 基于RAG检索相关代码
    """
    
    def __init__(self, codebase_path: str, llm_client=None):
        self.codebase_path = codebase_path
        self.llm_client = llm_client or MockLLMClient()
        
        # 初始化组件
        self.index = CodebaseIndex(codebase_path)
        self.context = ConversationContext(session_id=str(uuid.uuid4()))
        self.rag_builder = RAGPromptBuilder(self.index)
        self.window_manager = ContextWindowManager()
    
    def initialize(self):
        """初始化 - 构建代码库索引"""
        print("🔍 正在索引代码库...")
        file_contents = self._load_codebase()
        self.index.build_index(file_contents)
        print(f"✅ 索引完成，共 {len(file_contents)} 个文件")
    
    def _load_codebase(self) -> Dict[str, str]:
        """加载代码库文件"""
        files = {}
        for root, _, filenames in os.walk(self.codebase_path):
            # 跳过隐藏目录和常见非代码目录
            if any(part.startswith('.') for part in root.split(os.sep)):
                continue
            if 'venv' in root or '__pycache__' in root:
                continue
            
            for filename in filenames:
                if filename.endswith('.py'):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            files[filepath] = f.read()
                    except:
                        pass
        return files
    
    def chat(self, user_input: str) -> str:
        """
        处理用户输入并返回回复
        
        这是核心Agent Loop的简化实现
        """
        # 1. 记录用户输入
        self.context.add_message("user", user_input)
        
        # 2. 理解意图（简化版：直接检索相关代码）
        relevant_code = self.index.search(user_input, top_k=3)
        
        # 3. 构建增强Prompt
        prompt = self._build_prompt(user_input, relevant_code)
        
        # 4. 调用LLM生成回复
        response = self.llm_client.complete(prompt)
        
        # 5. 记录回复
        self.context.add_message("assistant", response)
        
        return response
    
    def _build_prompt(self, query: str, relevant_code: List) -> str:
        """构建完整的Prompt"""
        
        # 构建代码上下文
        code_context = "\n\n".join([
            f"【代码片段 {i+1}】(相关度: {score:.2f})\n文件: {chunk['file']}\n内容:\n{chunk['content'][:500]}"
            for i, (chunk, score) in enumerate(relevant_code)
        ])
        
        # 构建系统提示
        system_prompt = f"""你是一个专业的代码助手，帮助用户理解和修改代码。

## 代码库信息
以下是与用户问题相关的代码片段：
{code_context}

## 回答要求
1. 基于提供的代码片段回答
2. 引用具体的文件名和函数名
3. 如果代码片段不足，说明需要查看哪些文件
4. 提供具体的代码示例和详细解释"""

        # 组合完整提示
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        return messages
    
    def explain_function(self, function_name: str) -> str:
        """解释特定函数的功能"""
        query = f"解释函数 {function_name} 的功能和实现"
        return self.chat(query)
    
    def find_usage(self, symbol_name: str) -> List[Dict]:
        """查找符号的使用位置"""
        results = []
        for doc in self.index.documents:
            if symbol_name in doc.get("content", ""):
                results.append({
                    "file": doc.get("file"),
                    "type": doc.get("type"),
                    "name": doc.get("name")
                })
        return results
    
    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in self.context.messages
        ]


class MockLLMClient:
    """模拟LLM客户端（实际使用时替换为OpenAI/Claude API）"""
    
    def complete(self, messages: List[Dict]) -> str:
        """模拟生成回复"""
        user_msg = messages[-1]["content"]
        
        # 模拟回复模板
        if "explain" in user_msg.lower() or "解释" in user_msg:
            return f"""根据代码库分析，我来解释这个功能：

**功能概述**:
这段代码实现了[功能描述]。

**关键实现**:
1. 首先[步骤1]
2. 然后[步骤2]
3. 最后[步骤3]

**代码示例**:
```python
# 示例代码
```

**注意事项**:
- [注意点1]
- [注意点2]
"""
        else:
            return f"""我查看了相关代码，这里是分析结果：

**相关代码位置**:
- 文件: [文件名]
- 函数: [函数名]

**分析**:
基于代码库中的实现，[具体分析内容]。

**建议**:
1. [建议1]
2. [建议2]
"""
```

---

## 💻 实践任务

### 任务1: 运行Mini Code Assistant

```python
# 创建测试代码库
test_codebase = {
    "calculator.py": '''
def add(a, b):
    """加法运算"""
    return a + b

def subtract(a, b):
    """减法运算"""
    return a - b

def multiply(a, b):
    """乘法运算"""
    return a * b

def divide(a, b):
    """除法运算"""
    if b == 0:
        raise ValueError("不能除以零")
    return a / b
''',
    "data_processor.py": '''
import json
from typing import List, Dict

class DataProcessor:
    """数据处理类，支持加载、过滤和转换数据"""
    
    def __init__(self, source: str):
        self.source = source
        self.data: List[Dict] = []
    
    def load(self) -> List[Dict]:
        """从JSON文件加载数据"""
        with open(self.source, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        return self.data
    
    def filter_by(self, key: str, value) -> List[Dict]:
        """按条件过滤数据"""
        return [item for item in self.data if item.get(key) == value]
    
    def transform(self, transformer: callable) -> List[Dict]:
        """转换数据"""
        return [transformer(item) for item in self.data]
'''
}

# 保存测试文件
import os
os.makedirs("test_repo", exist_ok=True)
for filename, content in test_codebase.items():
    with open(f"test_repo/{filename}", 'w') as f:
        f.write(content)

# 初始化助手
assistant = MiniCodeAssistant("test_repo")
assistant.initialize()

# 开始对话
print("=" * 50)
print("Mini Code Assistant 测试")
print("=" * 50)

questions = [
    "DataProcessor类有什么功能？",
    "calculator.py中有哪些函数？",
    "filter_by方法怎么用？",
]

for question in questions:
    print(f"\n🙋 用户: {question}")
    response = assistant.chat(question)
    print(f"🤖 助手: {response}")
    print("-" * 50)
```

### 任务2: 扩展功能

1. **添加代码修改建议功能**:
   - 实现 `suggest_improvements(function_name)` 方法
   - 分析代码复杂度并提出优化建议

2. **添加代码搜索功能**:
   - 实现 `search_code(pattern)` 方法
   - 支持正则表达式搜索

3. **添加对话导出功能**:
   - 实现 `export_conversation(filename)` 方法
   - 导出为Markdown格式

---

## 📚 推荐资源

### Python AST
- [ast模块官方文档](https://docs.python.org/3/library/ast.html)
- [Python AST Explorer](https://python-ast-explorer.com/)

### RAG系统
- [LangChain RAG教程](https://python.langchain.com/docs/use_cases/question_answering/)
- [Sentence Transformers](https://www.sbert.net/)

### LLM应用开发
- [OpenAI API指南](https://platform.openai.com/docs/guides/gpt)
- [Claude API文档](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

---

## 💡 学习提示

### 关键概念
1. **AST是代码的"DNA"** - 理解AST就能理解代码结构
2. **RAG = 检索 + 生成** - 先找相关信息，再生成回答
3. **上下文管理是Agent的"记忆"** - 决定Agent能否理解长对话

### 常见错误
- ❌ 一次性加载整个代码库到Prompt - Token超限
- ✅ 使用RAG检索最相关的片段

- ❌ 忽略对话历史 - 答非所问
- ✅ 维护对话上下文，理解上下文依赖

- ❌ 直接返回代码不解释 - 用户难以理解
- ✅ 提供解释 + 代码示例 + 使用说明

---

## ✅ 今日产出检查清单

- [ ] 理解AST的概念和用途
- [ ] 成功运行CodeAnalyzer提取代码符号
- [ ] 理解RAG检索的工作原理
- [ ] 成功运行Mini Code Assistant原型
- [ ] 完成至少3轮对话测试
- [ ] 实现至少一个扩展功能

---

## 📝 课后作业

1. **改进嵌入模型**: 将SimpleEmbedding替换为真实模型（如SentenceTransformer）
2. **添加更多语言支持**: 扩展支持JavaScript/TypeScript代码分析
3. **实现代码diff展示**: 添加代码修改前后的对比显示
4. **优化检索算法**: 实现混合检索（关键词+向量）
5. **思考**: 如果要支持整个代码库的理解，还需要哪些功能？

---

**文档版本**: 1.0  
**创建日期**: 2026-04-26  
**作者**: AI Learning Platform
