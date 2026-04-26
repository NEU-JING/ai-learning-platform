# Day 85 - Claude Code/Cursor架构解析

> **目标**: 理解Claude Code、Cursor、Copilot的核心架构和工作原理
> **预计时长**: 2小时
> **前置知识**: Python基础、API调用基础

---

## 🎯 今日学习目标

完成本日学习后，你将能够：
1. 解释Claude Code的Agent Loop工作机制
2. 对比分析Cursor和Copilot的架构差异
3. 理解AI编程工具的上下文管理系统
4. 分析工具的API调用链和决策流程

---

## 📖 核心内容

### 1. AI编程工具概览

#### 1.1 主流工具对比

| 特性 | Claude Code | Cursor | GitHub Copilot |
|------|-------------|--------|----------------|
| **开发商** | Anthropic | Anysphere | GitHub/OpenAI |
| **核心模型** | Claude 3.5 Sonnet | GPT-4/Claude | Codex/GPT-4 |
| **交互方式** | 命令行 + 对话 | IDE集成 | 实时代码补全 |
| **上下文理解** | 整个代码库 | 当前文件+相关 | 当前编辑位置 |
| **Agent能力** | 强（可执行命令） | 中等 | 弱（仅补全） |
| **价格** | API按量 | 订阅制 | 订阅制 |

#### 1.2 工具演进历程

```
第一代: 代码补全 (2018-2020)
├── 代表: TabNine
└── 能力: 基于上下文的代码补全

第二代: 对话式编程 (2021-2023)
├── 代表: GitHub Copilot Chat
└── 能力: 问答、解释、简单修改

第三代: Agent式编程 (2024+)
├── 代表: Claude Code, Cursor Composer
└── 能力: 理解整个代码库、执行复杂任务
```

---

### 2. Claude Code 架构深度解析

#### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Claude Code 架构                            │
└─────────────────────────────────────────────────────────────────┘

用户输入
    │
    ▼
┌─────────────────┐
│  输入处理层      │
│  - Query解析     │
│  - 意图识别      │
│  - 上下文提取    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  上下文管理层    │
│  - 代码库索引    │ ◄── RAG检索增强
│  - 会话历史      │
│  - 工具状态      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  推理决策层      │◄────│  System Prompt  │
│  - 任务分解      │     │  - 角色定义      │
│  - 工具选择      │     │  - 工作流规范    │
│  - 执行规划      │     │  - 安全约束      │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  工具执行层      │
│  - Bash命令     │
│  - 文件操作     │
│  - 代码编辑     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  结果验证层      │
│  - 输出检查      │
│  - 错误处理      │
│  - 用户确认      │
└────────┬────────┘
         │
         ▼
      用户反馈
```

#### 2.2 Agent Loop 工作机制

Claude Code 的核心是 **Agent Loop（代理循环）**，这是一个持续观察-思考-行动的循环：

```python
# Agent Loop 伪代码
class AgentLoop:
    def run(self, user_input: str):
        context = self.gather_context()
        
        while not task_completed():
            # 1. 观察 (Observation)
            observation = self.observe_environment()
            
            # 2. 思考 (Reasoning)
            thought = self.llm.think(
                system_prompt=SYSTEM_PROMPT,
                context=context,
                observation=observation
            )
            
            # 3. 行动 (Action)
            action = self.parse_action(thought)
            
            if action.type == "tool_call":
                result = self.execute_tool(action)
                context.add_result(result)
            elif action.type == "final_answer":
                return action.content
            
            # 4. 等待用户确认（关键安全机制）
            if action.requires_confirmation:
                user_confirm = self.wait_for_user()
                if not user_confirm:
                    break
```

#### 2.3 代码库索引与RAG

Claude Code 使用 **检索增强生成（RAG）** 来理解整个代码库：

```python
# 简化的代码库索引实现
class CodebaseIndex:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.index = self._build_index()
    
    def _build_index(self) -> dict:
        """构建代码库向量索引"""
        index = {
            "files": {},           # 文件路径 -> 元数据
            "symbols": {},         # 符号 -> 定义位置
            "embeddings": {}       # 文件片段 -> 向量
        }
        
        for file_path in self._list_code_files():
            # 1. 解析AST提取符号
            symbols = self._extract_symbols(file_path)
            index["symbols"].update(symbols)
            
            # 2. 生成文件摘要
            summary = self._generate_summary(file_path)
            index["files"][file_path] = summary
            
            # 3. 分块并生成向量
            chunks = self._chunk_file(file_path)
            for chunk in chunks:
                embedding = self._embed(chunk)
                index["embeddings"][chunk.id] = embedding
        
        return index
    
    def search(self, query: str, top_k: int = 5) -> list:
        """语义搜索相关代码片段"""
        query_embedding = self._embed(query)
        
        results = []
        for chunk_id, embedding in self.index["embeddings"].items():
            similarity = cosine_similarity(query_embedding, embedding)
            results.append((chunk_id, similarity))
        
        return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]
```

#### 2.4 System Prompt 设计

Claude Code 的 System Prompt 是其行为的核心定义：

```
System Prompt 核心结构:

1. 角色定义
   "你是一个专业的编程助手，帮助用户理解和修改代码..."

2. 工作流规范
   - 首先理解用户需求
   - 然后搜索相关代码
   - 提出修改方案
   - 执行修改前确认
   - 执行后验证

3. 工具使用规范
   - bash: 执行shell命令
   - file_read: 读取文件内容
   - file_edit: 编辑文件
   - file_create: 创建新文件
   - file_delete: 删除文件

4. 安全约束
   - 不执行危险命令
   - 修改前必须确认
   - 保护敏感信息

5. 输出格式
   - 使用XML标签结构化输出
   - <thinking> 思考过程
   - <action> 执行动作
   - <result> 执行结果
```

---

### 3. Cursor 架构对比

#### 3.1 Cursor Composer 架构

```
Cursor Composer 架构特点:

┌─────────────────────────────────────────────────┐
│                 Cursor 架构                      │
└─────────────────────────────────────────────────┘

1. IDE深度集成
   - VS Code 插件架构
   - 直接操作编辑器API
   - 实时语法高亮和错误检测

2. 上下文管理
   - 当前编辑器上下文
   - @符号引用 (文件/函数/类)
   - 跨文件引用追踪

3. Composer模式
   - 多文件同时编辑
   - 代码变更预览
   - 一键应用/回滚

4. 模型选择
   - GPT-4 通用编程
   - Claude 代码理解
   - 自定义模型支持
```

#### 3.2 Cursor vs Claude Code 核心差异

| 维度 | Cursor | Claude Code |
|------|--------|-------------|
| **交互模式** | IDE内嵌 | 命令行独立 |
| **上下文范围** | 用户显式选择 | 自动全库索引 |
| **Agent自主性** | 低（用户主导） | 高（自主执行） |
| **适用场景** | 日常编码、重构 | 复杂任务、探索 |
| **学习曲线** | 平缓 | 较陡 |

---

### 4. GitHub Copilot 工作原理

#### 4.1 实时代码补全流程

```
用户输入触发
    │
    ▼
┌─────────────────┐
│ 1. 上下文提取    │
│ - 当前文件       │
│ - 光标前后代码   │
│ - 打开的相关文件 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 提示工程      │
│ - 构建FIM提示    │
│ - 添加语言标识   │
│ - 注入相关片段   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 模型推理      │
│ - Codex模型      │
│ - 生成多个候选   │
│ - 后处理过滤     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 补全展示      │
│ - 排序推荐       │
│ - 幽灵文本       │
│ - Tab接受        │
└─────────────────┘
```

#### 4.2 FIM (Fill-In-the-Middle) 技术

Copilot 使用 FIM 技术理解代码上下文：

```python
# FIM 提示格式
prompt = f"""
<|fim_prefix|>{code_before_cursor}
<|fim_suffix|>{code_after_cursor}
<|fim_middle|>
"""

# 示例
# 用户代码:
def calculate_total(items):
    total = 0
    # 光标在这里
    return total

# FIM提示:
<|fim_prefix|>def calculate_total(items):
    total = 0
    
<|fim_suffix|>
    return total
<|fim_middle|>

# 模型生成:
for item in items:
    total += item.price
```

---

## 💻 代码实践

### 实验1: 分析工具的API调用链

**目标**: 通过实际调用分析Claude Code的API使用模式

```python
# experimental/api_analyzer.py
import json
import time
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class APICall:
    timestamp: float
    endpoint: str
    tokens_input: int
    tokens_output: int
    latency_ms: float
    tool_calls: List[str]

class ClaudeCodeAnalyzer:
    """分析Claude Code的API调用模式"""
    
    def __init__(self):
        self.calls: List[APICall] = []
        self.session_start = time.time()
    
    def analyze_session(self, log_file: str) -> dict:
        """分析一个工作会话的API调用"""
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        analysis = {
            "total_calls": len(logs),
            "total_tokens": 0,
            "total_latency_ms": 0,
            "tool_usage": {},
            "call_sequence": []
        }
        
        for log in logs:
            call = APICall(
                timestamp=log["timestamp"],
                endpoint=log["endpoint"],
                tokens_input=log["usage"]["input_tokens"],
                tokens_output=log["usage"]["output_tokens"],
                latency_ms=log["latency_ms"],
                tool_calls=log.get("tool_calls", [])
            )
            
            self.calls.append(call)
            
            # 统计
            analysis["total_tokens"] += call.tokens_input + call.tokens_output
            analysis["total_latency_ms"] += call.latency_ms
            
            # 工具使用统计
            for tool in call.tool_calls:
                analysis["tool_usage"][tool] = analysis["tool_usage"].get(tool, 0) + 1
        
        return analysis
    
    def generate_report(self) -> str:
        """生成分析报告"""
        if not self.calls:
            return "没有数据"
        
        total_tokens = sum(c.tokens_input + c.tokens_output for c in self.calls)
        total_latency = sum(c.latency_ms for c in self.calls)
        
        report = f"""
# Claude Code API调用分析报告

## 会话概览
- 会话时长: {time.time() - self.session_start:.1f}秒
- API调用次数: {len(self.calls)}
- 总Token消耗: {total_tokens}
- 平均延迟: {total_latency / len(self.calls):.0f}ms

## Token消耗分析
- Input Tokens: {sum(c.tokens_input for c in self.calls)}
- Output Tokens: {sum(c.tokens_output for c in self.calls)}
- 平均每次调用: {total_tokens / len(self.calls):.0f} tokens

## 调用时序
"""
        for i, call in enumerate(self.calls[:10], 1):  # 显示前10次
            report += f"\n{i}. [{call.endpoint}] {call.latency_ms:.0f}ms | {call.tokens_input}+{call.tokens_output}tokens"
        
        return report

# 使用示例
if __name__ == "__main__":
    analyzer = ClaudeCodeAnalyzer()
    # analysis = analyzer.analyze_session("session_logs.json")
    # print(analyzer.generate_report())
```

### 实验2: 实现简单的工具调用追踪器

```python
# experimental/tool_tracer.py
from typing import Dict, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class ToolExecution:
    tool_name: str
    params: dict
    result: any = None
    error: str = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = None
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0

class ToolTracer:
    """追踪AI编程工具的工具调用"""
    
    def __init__(self):
        self.executions: List[ToolExecution] = []
        self.tools: Dict[str, Callable] = {}
    
    def register_tool(self, name: str, func: Callable):
        """注册可追踪的工具"""
        self.tools[name] = func
    
    def execute(self, tool_name: str, **params) -> any:
        """执行工具并记录"""
        if tool_name not in self.tools:
            raise ValueError(f"未知工具: {tool_name}")
        
        execution = ToolExecution(
            tool_name=tool_name,
            params=params
        )
        
        try:
            result = self.tools[tool_name](**params)
            execution.result = result
        except Exception as e:
            execution.error = str(e)
            raise
        finally:
            execution.end_time = datetime.now()
            self.executions.append(execution)
        
        return result
    
    def get_tool_stats(self) -> dict:
        """获取工具使用统计"""
        stats = {}
        for exec in self.executions:
            if exec.tool_name not in stats:
                stats[exec.tool_name] = {
                    "count": 0,
                    "total_duration_ms": 0,
                    "errors": 0
                }
            
            stats[exec.tool_name]["count"] += 1
            stats[exec.tool_name]["total_duration_ms"] += exec.duration_ms
            if exec.error:
                stats[exec.tool_name]["errors"] += 1
        
        return stats
    
    def export_trace(self, filename: str):
        """导出执行轨迹"""
        trace = {
            "executions": [
                {
                    "tool": e.tool_name,
                    "params": e.params,
                    "result": str(e.result)[:200] if e.result else None,
                    "error": e.error,
                    "duration_ms": e.duration_ms
                }
                for e in self.executions
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(trace, f, indent=2, default=str)

# 示例工具实现
def read_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()

def write_file(path: str, content: str):
    with open(path, 'w') as f:
        f.write(content)

# 使用示例
tracer = ToolTracer()
tracer.register_tool("read_file", read_file)
tracer.register_tool("write_file", write_file)

# 模拟工具调用
try:
    content = tracer.execute("read_file", path="example.py")
    tracer.execute("write_file", path="output.py", content=content)
except Exception as e:
    print(f"错误: {e}")

# 查看统计
print(json.dumps(tracer.get_tool_stats(), indent=2))
tracer.export_trace("tool_trace.json")
```

---

## 📚 推荐资源

### 官方文档
- [Claude Code官方文档](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Cursor文档](https://cursor.com/docs)
- [GitHub Copilot文档](https://docs.github.com/en/copilot)

### 技术博客
- "Building Claude Code" - Anthropic技术博客
- "Cursor Composer Internals" - Anysphere博客
- "How Copilot Works" - GitHub工程博客

### 开源项目
- [Claude Code SDK (非官方)](https://github.com/anthropics/claude-code)
- [Cursor API逆向工程](https://github.com/cursor-ai/research)

---

## 💡 学习提示

### 针对Java开发者
- AI编程工具类似于 **智能IDE插件**，但自主性更强
- 类比理解：Claude Code ≈ 超级增强版的IntelliJ Assistant
- 关注工具如何处理**大规模代码库**的上下文管理

### 常见误区
- ❌ 认为AI工具只是简单的代码补全
- ✅ 实际是**Agent系统**，能理解需求并自主执行

- ❌ 忽视System Prompt的重要性
- ✅ System Prompt是工具行为的"宪法"

- ❌ 过度依赖工具而不理解代码
- ✅ 工具是助手，最终责任在开发者

---

## ✅ 今日产出检查清单

- [ ] 理解Claude Code的Agent Loop工作机制
- [ ] 能够画出工具的架构流程图
- [ ] 运行实验代码分析API调用模式
- [ ] 对比分析至少2个工具的架构差异
- [ ] 撰写学习笔记总结关键概念

---

## 📝 课后作业

1. **架构图绘制**: 画出Claude Code的完整数据流图
2. **对比分析**: 写一篇500字对比分析（Cursor vs Claude Code）
3. **实验记录**: 记录实验1的输出结果，分析API调用模式
4. **思考**: 如果你是设计者，会如何改进当前的Agent Loop？

---

**文档版本**: 1.0  
**创建日期**: 2026-04-26  
**作者**: AI Learning Platform
