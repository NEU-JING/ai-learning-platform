# Lab: Mini Code Assistant

> 实验项目：构建极简AI编程助手
> 对应课程：Day 85-87 - AI编程工具原理与应用

---

## 🎯 实验目标

完成本实验后，你将能够：
1. 使用AST解析代码结构
2. 实现基于RAG的代码检索系统
3. 构建多轮对话上下文管理
4. 开发一个可运行的Mini Code Assistant原型

---

## 📁 项目结构

```
lab_mini_code_assistant/
├── README.md              # 本文件
├── src/
│   └── mini_assistant.py  # 主程序
├── tests/
│   └── test_assistant.py  # 测试用例
└── docs/
    └── architecture.md    # 架构文档
```

---

## 🚀 快速开始

### 1. 环境要求
- Python 3.9+
- NumPy

### 2. 运行演示
```bash
cd labs/lab_mini_code_assistant/src
python mini_assistant.py
```

### 3. 使用交互模式
```python
from mini_assistant import MiniCodeAssistant

# 创建助手
assistant = MiniCodeAssistant("/path/to/your/codebase")
assistant.initialize()

# 开始对话
response = assistant.chat("解释DataProcessor类的功能")
print(response)

# 查找符号
results = assistant.find_symbol("load_data")
print(results)
```

---

## 📚 核心组件

### 1. CodeAnalyzer - 代码分析器
- 使用Python AST解析代码
- 提取函数、类、导入信息
- 生成代码摘要

### 2. CodebaseIndex - 代码库索引
- RAG检索增强
- 向量嵌入（简化版）
- 语义搜索

### 3. ConversationContext - 对话上下文
- 多轮对话管理
- 消息历史记录
- 工具执行追踪

### 4. MiniCodeAssistant - 主助手
- 整合所有组件
- Agent Loop实现
- 智能回复生成

---

## 🔧 扩展任务

1. **替换嵌入模型**: 将SimpleEmbedding替换为SentenceTransformer
2. **添加更多语言支持**: 扩展支持JavaScript/TypeScript
3. **实现代码修改建议**: 添加代码重构功能
4. **集成真实LLM**: 替换MockLLMClient为OpenAI/Claude API

---

## 📝 学习要点

1. **AST是代码的"DNA"** - 理解代码结构的基础
2. **RAG = 检索 + 生成** - 提高回答的相关性
3. **上下文管理是Agent的"记忆"** - 支持多轮对话
4. **System Prompt是行为的"宪法"** - 定义AI的角色和约束

---

**创建日期**: 2026-04-26
