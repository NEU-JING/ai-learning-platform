#!/usr/bin/env python3
"""
Mini Code Assistant - 极简AI编程助手
基于Day 85-87课程内容实现

功能：
1. 代码库索引和RAG检索
2. 多轮对话上下文管理
3. 代码分析和解释
"""

import ast
import hashlib
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# ==================== 数据模型 ====================


@dataclass
class Message:
    """对话消息"""

    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class ToolExecution:
    """工具执行记录"""

    tool_name: str
    params: Dict
    result: Any = None
    error: str = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0


# ==================== 代码分析器 ====================


class CodeAnalyzer:
    """代码分析器 - 提取代码结构和符号"""

    def __init__(self, code: str):
        try:
            self.tree = ast.parse(code)
            self.valid = True
        except SyntaxError:
            self.tree = None
            self.valid = False

        self.symbols = {"functions": [], "classes": [], "imports": [], "variables": []}

    def analyze(self) -> Dict[str, Any]:
        """分析代码并提取符号"""
        if not self.valid:
            return self.symbols

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
        }
        self.symbols["functions"].append(func_info)

    def _extract_class(self, node: ast.ClassDef):
        """提取类信息"""
        class_info = {
            "name": node.name,
            "line": node.lineno,
            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
            "docstring": ast.get_docstring(node),
        }
        self.symbols["classes"].append(class_info)

    def _extract_import(self, node):
        """提取导入信息"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.symbols["imports"].append({"name": alias.name, "line": node.lineno})
        elif isinstance(node, ast.ImportFrom):
            self.symbols["imports"].append(
                {
                    "module": node.module,
                    "names": [alias.name for alias in node.names],
                    "line": node.lineno,
                }
            )


# ==================== 向量嵌入 ====================


class SimpleEmbedding:
    """简化版嵌入生成器"""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed(self, text: str) -> np.ndarray:
        """生成文本的向量表示（简化实现）"""
        hash_val = hashlib.md5(text.encode()).hexdigest()
        np.random.seed(int(hash_val[:8], 16))
        return np.random.randn(self.dimension)

    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


# ==================== 代码库索引 ====================


class CodebaseIndex:
    """代码库索引 - RAG检索基础"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.embedder = SimpleEmbedding()
        self.documents: List[Dict] = []
        self.embeddings: List[np.ndarray] = []

    def index_file(self, file_path: str, content: str):
        """索引单个文件"""
        try:
            analyzer = CodeAnalyzer(content)
            symbols = analyzer.analyze()
        except:
            symbols = {"functions": [], "classes": []}

        # 按函数/类分块
        for func in symbols.get("functions", []):
            chunk_text = f"Function: {func['name']}\n"
            chunk_text += f"Args: {', '.join(func['args'])}\n"
            chunk_text += f"Doc: {func.get('docstring', 'No docstring')}"

            self._add_chunk(
                {
                    "type": "function",
                    "name": func["name"],
                    "content": chunk_text,
                    "file": file_path,
                    "line": func.get("line", 0),
                }
            )

        for cls in symbols.get("classes", []):
            chunk_text = f"Class: {cls['name']}\n"
            chunk_text += f"Methods: {', '.join(cls.get('methods', []))}\n"
            chunk_text += f"Doc: {cls.get('docstring', 'No docstring')}"

            self._add_chunk(
                {
                    "type": "class",
                    "name": cls["name"],
                    "content": chunk_text,
                    "file": file_path,
                    "line": cls.get("line", 0),
                }
            )

    def _add_chunk(self, chunk: Dict):
        """添加代码块到索引"""
        embedding = self.embedder.embed(chunk["content"])
        self.documents.append(chunk)
        self.embeddings.append(embedding)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """搜索相关代码片段"""
        if not self.embeddings:
            return []

        query_embedding = self.embedder.embed(query)

        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            sim = self.embedder.similarity(query_embedding, doc_embedding)
            similarities.append((self.documents[i], sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def build_index(self, file_contents: Dict[str, str]):
        """构建完整索引"""
        for file_path, content in file_contents.items():
            if file_path.endswith(".py"):
                self.index_file(file_path, content)

        print(f"✅ 索引完成: {len(self.documents)} 个代码块")


# ==================== 对话上下文 ====================


class ConversationContext:
    """对话上下文管理"""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.messages: List[Message] = []
        self.tool_executions: List[ToolExecution] = []

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """添加消息"""
        self.messages.append(Message(role=role, content=content, metadata=metadata or {}))

    def get_recent_messages(self, n: int = 10) -> List[Message]:
        """获取最近N条消息"""
        return self.messages[-n:]

    def get_history_text(self, n: int = 5) -> str:
        """获取历史对话文本"""
        recent = self.get_recent_messages(n)
        lines = []
        for msg in recent:
            lines.append(f"{msg.role}: {msg.content[:100]}...")
        return "\n".join(lines)


# ==================== 模拟LLM客户端 ====================


class MockLLMClient:
    """模拟LLM客户端"""

    def complete(self, messages: List[Dict]) -> str:
        """模拟生成回复"""
        user_msg = messages[-1].get("content", "")

        # 模拟智能回复
        if "explain" in user_msg.lower() or "解释" in user_msg:
            return self._generate_explanation()
        elif "function" in user_msg.lower() or "函数" in user_msg:
            return self._generate_function_info()
        else:
            return self._generate_generic_response()

    def _generate_explanation(self) -> str:
        return """根据代码库分析：

**功能概述**:
这段代码实现了一个数据处理流程，包括加载、过滤和转换。

**关键实现**:
1. 使用面向对象设计，封装了DataProcessor类
2. 采用函数式编程风格，支持链式调用
3. 使用类型提示，提高代码可读性

**代码示例**:
```python
processor = DataProcessor("data.json")
data = processor.load()
filtered = processor.filter_by("status", "active")
```

**注意事项**:
- 需要确保数据文件存在
- 大数据集可能导致内存问题
- 建议添加错误处理"""

    def _generate_function_info(self) -> str:
        return """我找到了以下相关函数：

**Function: load_data**
- 位置: data_processor.py:15
- 参数: source (str)
- 功能: 从JSON文件加载数据
- 返回值: List[Dict]

**Function: process**
- 位置: data_processor.py:25
- 参数: data (List[Dict]), transformer (callable)
- 功能: 处理数据并应用转换
- 返回值: List[Dict]

**使用示例**:
```python
# 加载数据
data = load_data("input.json")

# 处理数据
result = process(data, lambda x: x["value"] * 2)
```"""

    def _generate_generic_response(self) -> str:
        return """我查看了相关代码，这里是分析结果：

**相关代码位置**:
- 文件: main.py, utils.py
- 关键函数: process_data, validate_input

**分析**:
代码整体结构清晰，采用了分层架构设计。

**建议**:
1. 添加更多的单元测试
2. 考虑添加日志记录
3. 优化大数据集处理性能"""


# ==================== Mini Code Assistant ====================


class MiniCodeAssistant:
    """极简AI编程助手"""

    def __init__(self, codebase_path: str = ".", llm_client=None):
        self.codebase_path = codebase_path
        self.llm_client = llm_client or MockLLMClient()

        self.index = CodebaseIndex(codebase_path)
        self.context = ConversationContext()
        self.initialized = False

    def initialize(self):
        """初始化 - 构建代码库索引"""
        print("🔍 正在索引代码库...")
        file_contents = self._load_codebase()
        self.index.build_index(file_contents)
        self.initialized = True
        print(f"✅ 初始化完成，共 {len(file_contents)} 个文件")

    def _load_codebase(self) -> Dict[str, str]:
        """加载代码库文件"""
        files = {}
        for root, _, filenames in os.walk(self.codebase_path):
            # 跳过隐藏目录和常见非代码目录
            if any(part.startswith(".") for part in root.split(os.sep)):
                continue
            if any(skip in root for skip in ["venv", "__pycache__", "node_modules"]):
                continue

            for filename in filenames:
                if filename.endswith(".py"):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            rel_path = os.path.relpath(filepath, self.codebase_path)
                            files[rel_path] = f.read()
                    except Exception as e:
                        print(f"⚠️ 无法读取文件 {filepath}: {e}")
        return files

    def chat(self, user_input: str) -> str:
        """处理用户输入并返回回复"""
        if not self.initialized:
            self.initialize()

        # 1. 记录用户输入
        self.context.add_message("user", user_input)

        # 2. 检索相关代码
        relevant_code = self.index.search(user_input, top_k=3)

        # 3. 构建Prompt
        prompt = self._build_prompt(user_input, relevant_code)

        # 4. 调用LLM
        response = self.llm_client.complete(prompt)

        # 5. 记录回复
        self.context.add_message("assistant", response)

        return response

    def _build_prompt(self, query: str, relevant_code: List) -> List[Dict]:
        """构建完整的Prompt"""
        # 构建代码上下文
        code_context = (
            "\n\n".join(
                [
                    f"【{chunk['type']}】{chunk['name']} (文件: {chunk['file']})\n{chunk['content'][:300]}"
                    for chunk, score in relevant_code
                ]
            )
            if relevant_code
            else "未找到相关代码"
        )

        # 构建系统提示
        system_prompt = f"""你是一个专业的代码助手，帮助用户理解和修改代码。

## 相关代码上下文
{code_context}

## 回答要求
1. 基于提供的代码上下文回答
2. 引用具体的文件名和函数名
3. 如果代码片段不够，说明需要更多信息
4. 提供具体的代码示例和详细解释"""

        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}]

    def find_symbol(self, symbol_name: str) -> List[Dict]:
        """查找符号"""
        results = []
        for doc in self.index.documents:
            if symbol_name.lower() in doc.get("name", "").lower():
                results.append(
                    {
                        "file": doc.get("file"),
                        "type": doc.get("type"),
                        "name": doc.get("name"),
                        "line": doc.get("line"),
                    }
                )
        return results

    def get_stats(self) -> Dict:
        """获取助手统计信息"""
        return {
            "session_id": self.context.session_id,
            "messages_count": len(self.context.messages),
            "indexed_documents": len(self.index.documents),
            "codebase_path": self.codebase_path,
        }


# ==================== 主函数 ====================


def main():
    """主函数 - 演示Mini Code Assistant"""
    print("=" * 60)
    print("Mini Code Assistant 演示")
    print("=" * 60)

    # 创建测试代码库
    test_repo = "test_repo"
    os.makedirs(test_repo, exist_ok=True)

    # 创建测试文件
    test_files = {
        "calculator.py": '''
def add(a, b):
    """加法运算"""
    return a + b

def subtract(a, b):
    """减法运算"""
    return a - b
''',
        "data_processor.py": '''
import json
from typing import List, Dict

class DataProcessor:
    """数据处理类"""
    
    def __init__(self, source: str):
        self.source = source
        self.data = []
    
    def load(self) -> List[Dict]:
        """从JSON文件加载数据"""
        with open(self.source, 'r') as f:
            self.data = json.load(f)
        return self.data
    
    def filter_by(self, key: str, value) -> List[Dict]:
        """按条件过滤数据"""
        return [item for item in self.data if item.get(key) == value]
''',
    }

    for filename, content in test_files.items():
        with open(os.path.join(test_repo, filename), "w") as f:
            f.write(content)

    # 初始化助手
    assistant = MiniCodeAssistant(test_repo)
    assistant.initialize()

    # 测试对话
    print("\n" + "=" * 60)
    print("开始对话测试")
    print("=" * 60)

    test_questions = [
        "DataProcessor类有什么功能？",
        "有哪些数学运算函数？",
        "filter_by方法怎么用？",
    ]

    for question in test_questions:
        print(f"\n🙋 用户: {question}")
        print("-" * 40)
        response = assistant.chat(question)
        print(f"🤖 助手:\n{response}")
        print("=" * 60)

    # 显示统计
    print("\n📊 统计信息:")
    stats = assistant.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 清理
    import shutil

    shutil.rmtree(test_repo)
    print("\n✅ 演示完成，已清理测试目录")


if __name__ == "__main__":
    main()
