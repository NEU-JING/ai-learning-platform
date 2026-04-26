# Day 87 - Prompt Engineering 进阶

> **目标**: 掌握高质量Prompt编写能力，设计可复用的Prompt模板
> **预计时长**: 1.5小时
> **前置知识**: Day 85-86内容、LLM基础

---

## 🎯 今日学习目标

完成本日学习后，你将能够：
1. 设计高质量的System Prompt
2. 掌握Few-shot提示优化技巧
3. 使用Chain-of-Thought方法
4. 构建可复用的Prompt模板库

---

## 📖 核心内容

### 1. System Prompt 设计模式

#### 1.1 System Prompt的作用

System Prompt是定义AI助手行为的"宪法"，它决定了：
- AI的角色和身份
- 回答的风格和格式
- 工作的流程和规范
- 安全的约束和边界

#### 1.2 代码助手的System Prompt模板

```markdown
# System Prompt: 专业代码助手

## 角色定义
你是Claude，一个专业的编程助手。你擅长：
- 代码审查和优化建议
- 代码解释和文档生成
- Bug分析和修复方案
- 架构设计和技术选型

## 工作流规范

### 1. 理解需求
- 仔细阅读用户的问题
- 识别核心需求和上下文
- 如有不明确，主动询问

### 2. 分析代码
- 审查代码的逻辑正确性
- 检查代码风格和规范
- 识别潜在的性能问题
- 发现安全漏洞

### 3. 提供方案
- 给出具体的修改建议
- 提供修改后的完整代码
- 解释修改的原因
- 说明可能的影响

### 4. 验证结果
- 检查修改后的代码是否正确
- 确认没有引入新问题
- 提供测试建议

## 输出格式规范

### 代码审查报告格式
```markdown
## 审查概览
- 文件: [文件名]
- 行数: [行数统计]
- 问题数量: [问题数]

## 发现的问题
### [严重程度] [问题类型]: [描述]
- **位置**: [行号]
- **问题**: [详细说明]
- **建议**: [修改方案]
- **代码**:
  ```[语言]
  [修改后的代码]
  ```

## 优化建议
1. [建议1]
2. [建议2]

## 整体评价
[综合评价]
```

### 代码解释格式
```markdown
## 功能概述
[一句话描述]

## 详细解析
### 1. [步骤1名称]
[解释]

### 2. [步骤2名称]
[解释]

## 关键代码段
```[语言]
[代码]
```
[逐行解释]

## 使用示例
```[语言]
[示例代码]
```

## 注意事项
- [注意1]
- [注意2]
```

## 安全约束
- 不提供执行恶意代码的方案
- 不协助绕过安全措施
- 发现安全漏洞时优先报告
- 敏感信息（密码、密钥）用占位符代替

## 风格指南
- 使用中文回答
- 技术术语保留英文
- 代码注释使用中文
- 提供具体的代码示例
```

#### 1.3 System Prompt设计原则

```python
# system_prompt_designer.py

class SystemPromptDesigner:
    """System Prompt设计助手"""
    
    # 设计原则
    PRINCIPLES = {
        "clarity": "清晰明确 - 每个指令都要具体无歧义",
        "conciseness": "简洁有力 - 避免冗余，突出重点",
        "structure": "结构清晰 - 使用分层组织",
        "examples": "示例驱动 - 用例子说明期望输出",
        "constraints": "约束明确 - 定义不能做什么",
    }
    
    @staticmethod
    def create_role_section(role: str, expertise: list) -> str:
        """创建角色定义部分"""
        expertise_str = "\n- ".join([""] + expertise)
        return f"""## 角色定义
你是{role}。你擅长：{expertise_str}
"""
    
    @staticmethod
    def create_workflow_section(steps: list) -> str:
        """创建工作流部分"""
        steps_str = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        return f"""## 工作流规范
{steps_str}
"""
    
    @staticmethod
    def create_format_section(format_template: str) -> str:
        """创建输出格式部分"""
        return f"""## 输出格式规范
{format_template}
"""
    
    @staticmethod
    def create_constraints_section(constraints: list) -> str:
        """创建约束部分"""
        constraints_str = "\n- ".join([""] + constraints)
        return f"""## 安全约束{constraints_str}
"""

# 使用示例
designer = SystemPromptDesigner()

system_prompt = f"""{designer.create_role_section(
    "代码审查专家",
    ["发现代码中的潜在Bug", "识别性能瓶颈", "提出重构建议", "确保代码安全"]
)}

{designer.create_workflow_section([
    "通读代码，理解整体逻辑",
    "逐行检查，标记问题点",
    "分类整理发现的问题",
    "提供具体的修改方案",
    "给出整体优化建议"
])}

{designer.create_format_section('''
## 审查报告
### 问题列表
| 严重程度 | 类型 | 位置 | 描述 | 建议 |
|---------|------|------|------|------|
| [P0-P3] | [类型] | [行号] | [描述] | [建议] |

### 修改后的代码
```[语言]
[完整代码]
```
''')}

{designer.create_constraints_section([
    "不审查加密算法实现",
    "不协助绕过安全检查",
    "发现严重漏洞时立即报告",
])}
"""

print(system_prompt)
```

---

### 2. Few-shot提示优化

#### 2.1 Few-shot的基本原理

Few-shot通过在Prompt中提供示例，让LLM理解期望的输出格式和风格：

```
Zero-shot: 直接提问，不提供示例
One-shot: 提供1个示例
Few-shot: 提供3-5个示例（最佳实践）
Many-shot: 提供10+示例（适用于复杂任务）
```

#### 2.2 代码审查的Few-shot示例

```markdown
# 代码审查任务 - Few-shot示例

## 任务说明
审查以下代码，找出问题并提供修改建议。

## 输出格式要求
对每个问题，按以下格式输出：
```
[严重程度: P0/P1/P2/P3] [问题类型]
- 位置: 第X行
- 问题: [描述]
- 建议: [修改方案]
```

## 示例1

### 输入代码
```python
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

### 审查结果
```
[P0] SQL注入漏洞
- 位置: 第2行
- 问题: 直接拼接用户输入到SQL查询，存在SQL注入风险
- 建议: 使用参数化查询
  ```python
  query = "SELECT * FROM users WHERE id = ?"
  return db.execute(query, (user_id,))
  ```
```

## 示例2

### 输入代码
```python
def calculate(items):
    total = 0
    for i in range(len(items)):
        total += items[i].price
    return total
```

### 审查结果
```
[P1] 代码可读性
- 位置: 第3-4行
- 问题: 使用索引循环不如直接迭代清晰
- 建议: 使用for-each循环
  ```python
  for item in items:
      total += item.price
  ```

[P2] 空列表处理
- 位置: 整个函数
- 问题: 如果items为空，返回0是合理的，但最好显式说明
- 建议: 添加文档字符串说明
  ```python
  def calculate(items):
      """计算商品总价，空列表返回0"""
      ...
  ```
```

## 示例3

### 输入代码
```python
import os

SECRET_KEY = "hardcoded_secret_key_12345"

def connect():
    password = "admin123"
    return Database.connect(password=password)
```

### 审查结果
```
[P0] 硬编码密钥
- 位置: 第3行
- 问题: 将密钥硬编码在代码中，安全风险极高
- 建议: 使用环境变量
  ```python
  import os
  SECRET_KEY = os.getenv("SECRET_KEY")
  if not SECRET_KEY:
      raise ValueError("SECRET_KEY environment variable is not set")
  ```

[P0] 硬编码密码
- 位置: 第6行
- 问题: 数据库密码硬编码
- 建议: 同样使用环境变量或密钥管理服务

[P1] 敏感信息泄露
- 位置: 整个文件
- 问题: 即使修改后，Git历史中仍有敏感信息
- 建议: 
  1. 立即轮换所有涉及的密钥和密码
  2. 使用git-filter-branch或BFG清理历史
  3. 启用GitHub secret scanning
```

---

## 现在开始审查

### 输入代码
```python
{user_code}
```

### 审查结果
```
```
```

#### 2.3 Few-shot示例选择原则

```python
class FewShotExampleSelector:
    """Few-shot示例选择器"""
    
    def __init__(self, examples: list):
        self.examples = examples
    
    def select(self, query: str, n: int = 3) -> list:
        """
        为查询选择最相关的示例
        
        策略：
        1. 多样性 - 覆盖不同类型的问题
        2. 相关性 - 与查询相似
        3. 难度递进 - 从简单到复杂
        """
        selected = []
        
        # 1. 选择不同类型的示例
        categories = set()
        for example in self.examples:
            if example["category"] not in categories:
                selected.append(example)
                categories.add(example["category"])
                if len(selected) >= n:
                    break
        
        # 2. 如果不够，按相似度补充
        if len(selected) < n:
            # 简化版：随机补充
            import random
            remaining = [e for e in self.examples if e not in selected]
            selected.extend(random.sample(remaining, n - len(selected)))
        
        return selected[:n]
    
    def format_examples(self, examples: list) -> str:
        """将示例格式化为Prompt"""
        formatted = []
        for i, ex in enumerate(examples, 1):
            formatted.append(f"""## 示例{i}

### 输入代码
```python
{ex['input']}
```

### 审查结果
```
{ex['output']}
```
""")
        return "\n".join(formatted)

# 示例库
code_review_examples = [
    {
        "category": "security",
        "input": "...",  # SQL注入示例
        "output": "..."
    },
    {
        "category": "performance",
        "input": "...",  # 性能问题示例
        "output": "..."
    },
    {
        "category": "style",
        "input": "...",  # 代码风格示例
        "output": "..."
    },
]
```

---

### 3. Chain-of-Thought方法

#### 3.1 CoT的基本原理

Chain-of-Thought（思维链）通过让模型展示推理过程，提高复杂任务的准确性：

```
标准提示: Q -> A
CoT提示: Q -> 推理过程 -> A
```

#### 3.2 代码分析的CoT示例

```markdown
# Chain-of-Thought代码分析

## 问题
分析以下代码的时间复杂度

```python
def find_pairs(nums, target):
    result = []
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                result.append((nums[i], nums[j]))
    return result
```

## 分析过程（展示推理链）

让我逐步分析这段代码：

**Step 1: 识别循环结构**
- 外层循环: for i in range(len(nums)) - 遍历n次
- 内层循环: for j in range(i + 1, len(nums)) - 遍历次数递减

**Step 2: 计算内层循环执行次数**
- 当 i=0 时，j 从 1 到 n-1，执行 n-1 次
- 当 i=1 时，j 从 2 到 n-1，执行 n-2 次
- ...
- 当 i=n-2 时，j 为 n-1，执行 1 次
- 当 i=n-1 时，不执行

**Step 3: 求和计算**
总次数 = (n-1) + (n-2) + ... + 1
       = n(n-1)/2
       = O(n²)

**Step 4: 其他操作**
- nums[i] + nums[j] == target: O(1)
- result.append(...): O(1)（均摊）

**Step 5: 结论**
时间复杂度: O(n²)
空间复杂度: O(k)，k为结果对数

## 最终答案
- **时间复杂度**: O(n²)
- **空间复杂度**: O(k)，k为满足条件的对数
- **优化建议**: 可以使用哈希表优化到O(n)
```

#### 3.3 CoT模板生成器

```python
class CoTTemplateGenerator:
    """思维链模板生成器"""
    
    TEMPLATES = {
        "complexity_analysis": """让我逐步分析这段代码的时间复杂度：

**Step 1: 识别基本操作**
[列出基本操作]

**Step 2: 分析循环结构**
[分析每个循环]

**Step 3: 计算执行次数**
[数学计算]

**Step 4: 确定主导项**
[找出复杂度最高的部分]

**Step 5: 给出结论**
时间复杂度: [结果]
空间复杂度: [结果]""",
        
        "bug_analysis": """让我逐步分析这个Bug：

**Step 1: 理解预期行为**
[代码应该做什么]

**Step 2: 分析实际执行**
[逐行追踪执行流程]

**Step 3: 找出问题点**
[哪里出错了]

**Step 4: 根因分析**
[为什么会出错]

**Step 5: 提供修复方案**
[如何修复]""",
        
        "refactoring": """让我逐步分析重构方案：

**Step 1: 识别代码坏味道**
[列出问题]

**Step 2: 确定重构目标**
[要改善什么]

**Step 3: 设计新结构**
[新架构设计]

**Step 4: 逐步实施**
[重构步骤]

**Step 5: 验证改进**
[改进点总结]""",
    }
    
    @classmethod
    def get_template(cls, task_type: str) -> str:
        """获取指定任务的CoT模板"""
        return cls.TEMPLATES.get(task_type, "请逐步分析和解答：")
    
    @classmethod
    def create_prompt(cls, task_type: str, question: str) -> str:
        """创建完整的CoT提示"""
        template = cls.get_template(task_type)
        return f"""{question}

请按照以下步骤进行分析和解答：

{template}

请确保每个步骤都有清晰的解释。"""

# 使用示例
print(CoTTemplateGenerator.create_prompt(
    "complexity_analysis",
    "分析这段代码的时间复杂度：..."
))
```

---

### 4. Prompt模板库构建

#### 4.1 模板库结构

```yaml
# prompt_library.yaml
version: "1.0"
categories:
  code_review:
    name: "代码审查"
    templates:
      - id: "security_review"
        name: "安全审查"
        description: "专注于发现安全漏洞"
        system_prompt: "..."
        few_shot_examples: [...]
        
      - id: "performance_review"
        name: "性能审查"
        description: "检查性能瓶颈"
        system_prompt: "..."
        
      - id: "style_review"
        name: "代码风格审查"
        description: "检查代码风格和规范"
        system_prompt: "..."
  
  code_generation:
    name: "代码生成"
    templates:
      - id: "unit_test_gen"
        name: "单元测试生成"
        description: "为函数生成单元测试"
        system_prompt: "..."
        
      - id: "doc_gen"
        name: "文档生成"
        description: "生成函数文档"
        system_prompt: "..."
  
  code_explanation:
    name: "代码解释"
    templates:
      - id: "function_explain"
        name: "函数解释"
        description: "详细解释函数功能"
        system_prompt: "..."
        
      - id: "algorithm_explain"
        name: "算法解释"
        description: "解释算法原理和复杂度"
        system_prompt: "..."
```

#### 4.2 Prompt模板管理器

```python
# prompt_template_manager.py
import yaml
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    """Prompt模板"""
    id: str
    name: str
    description: str
    system_prompt: str
    few_shot_examples: List[dict]
    cot_template: Optional[str] = None
    output_format: Optional[str] = None

class PromptTemplateManager:
    """Prompt模板管理器"""
    
    def __init__(self, library_path: str = "content/resources/prompt_templates/"):
        self.library_path = library_path
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_library()
    
    def _load_library(self):
        """加载模板库"""
        # 加载YAML配置
        try:
            with open(f"{self.library_path}/library.yaml", 'r') as f:
                config = yaml.safe_load(f)
            
            for category in config.get("categories", {}).values():
                for template_config in category.get("templates", []):
                    template = PromptTemplate(**template_config)
                    self.templates[template.id] = template
        except FileNotFoundError:
            # 如果没有配置文件，使用内置模板
            self._load_builtin_templates()
    
    def _load_builtin_templates(self):
        """加载内置模板"""
        self.templates["code_review_security"] = PromptTemplate(
            id="code_review_security",
            name="安全审查",
            description="专注于发现安全漏洞",
            system_prompt="""你是一个安全专家，专注于发现代码中的安全漏洞。

审查重点：
1. SQL注入
2. XSS攻击
3. 硬编码密钥/密码
4. 不安全的反序列化
5. 路径遍历
6. 命令注入

输出格式：
[P0/P1/P2/P3] [漏洞类型]
- 位置: [文件:行号]
- 风险: [描述]
- 修复: [建议]
""",
            few_shot_examples=[],
            cot_template="""让我逐步检查这段代码的安全性：

Step 1: 检查用户输入处理
Step 2: 检查数据库查询
Step 3: 检查文件操作
Step 4: 检查命令执行
Step 5: 检查敏感信息处理"""
        )
        
        self.templates["code_review_performance"] = PromptTemplate(
            id="code_review_performance",
            name="性能审查",
            description="检查性能瓶颈",
            system_prompt="""你是一个性能优化专家，专注于发现代码中的性能问题。

审查重点：
1. 时间复杂度
2. 空间复杂度
3. 数据库查询优化
4. 循环优化
5. 内存使用

输出格式：
[严重程度] [问题类型]: [描述]
- 影响: [性能影响]
- 建议: [优化方案]
""",
            few_shot_examples=[],
            cot_template="""让我逐步分析这段代码的性能：

Step 1: 识别算法复杂度
Step 2: 检查数据库查询
Step 3: 分析内存使用
Step 4: 找出热点代码
Step 5: 提供优化建议"""
        )
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """获取指定模板"""
        return self.templates.get(template_id)
    
    def list_templates(self, category: str = None) -> List[PromptTemplate]:
        """列出所有模板"""
        templates = list(self.templates.values())
        if category:
            templates = [t for t in templates if t.id.startswith(category)]
        return templates
    
    def build_prompt(self, template_id: str, context: dict) -> str:
        """使用模板构建完整Prompt"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        prompt_parts = []
        
        # 1. System Prompt
        prompt_parts.append(f"# System\n{template.system_prompt}\n")
        
        # 2. Few-shot Examples
        if template.few_shot_examples:
            prompt_parts.append("# Examples\n")
            for i, example in enumerate(template.few_shot_examples, 1):
                prompt_parts.append(f"## Example {i}\n")
                prompt_parts.append(f"Input: {example['input']}\n")
                prompt_parts.append(f"Output: {example['output']}\n")
        
        # 3. Chain-of-Thought
        if template.cot_template:
            prompt_parts.append(f"# Analysis Steps\n{template.cot_template}\n")
        
        # 4. Current Task
        prompt_parts.append(f"# Task\n{context.get('task', '')}\n")
        prompt_parts.append(f"# Input\n```python\n{context.get('code', '')}\n```\n")
        prompt_parts.append("# Output\n")
        
        return "\n".join(prompt_parts)
    
    def add_template(self, template: PromptTemplate):
        """添加新模板"""
        self.templates[template.id] = template
    
    def export_library(self, filepath: str):
        """导出模板库"""
        library = {
            "version": "1.0",
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "system_prompt": t.system_prompt,
                    "few_shot_examples": t.few_shot_examples,
                    "cot_template": t.cot_template,
                }
                for t in self.templates.values()
            ]
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(library, f, default_flow_style=False)

# 使用示例
manager = PromptTemplateManager()

# 列出所有代码审查模板
templates = manager.list_templates("code_review")
print("可用模板:")
for t in templates:
    print(f"  - {t.name}: {t.description}")

# 使用模板构建Prompt
context = {
    "task": "审查这段代码的安全性",
    "code": "..."
}
prompt = manager.build_prompt("code_review_security", context)
print(prompt)
```

---

## 💻 实践任务

### 任务1: 创建自定义System Prompt

```python
# 为特定场景设计System Prompt

my_system_prompt = """
[System Prompt设计练习]

场景: 你正在为一个数据工程团队设计代码审查助手。

请设计一个System Prompt，要求：
1. 角色定位为数据工程专家
2. 擅长领域：SQL优化、数据处理、数据质量
3. 输出格式包含：性能分析、数据质量检查、SQL优化建议
4. 安全约束：检查数据泄露风险

请完整写出System Prompt，并说明设计理由。
"""

# 设计框架
def design_system_prompt():
    prompt = f"""## 角色定义
你是数据工程专家，擅长：
- SQL查询优化
- 数据处理管道设计
- 数据质量检查
- ETL流程审查

## 工作流规范
1. 首先理解数据处理目标
2. 检查数据源的可靠性
3. 分析SQL查询性能
4. 检查数据质量约束
5. 提出优化建议

## 输出格式
```markdown
## 审查概览
- 数据源: [描述]
- 处理目标: [描述]
- 风险等级: [P0/P1/P2/P3]

## SQL分析
### 查询复杂度
[分析]

### 优化建议
```sql
[优化后的SQL]
```

## 数据质量检查
- [ ] 空值处理
- [ ] 重复数据
- [ ] 数据类型
- [ ] 约束检查

## 安全问题
- 数据泄露风险: [评估]
- 敏感数据处理: [检查]
```

## 安全约束
- 不审查生产环境的密码
- 发现敏感数据泄露立即警告
- 建议使用数据脱敏
"""
    return prompt
```

### 任务2: 设计Few-shot示例集

```python
# 为代码重构任务设计3个Few-shot示例

refactoring_examples = [
    {
        "input": "...",  # 待重构代码
        "output": "..."  # 重构方案
    },
    # ... 更多示例
]
```

### 任务3: 创建Prompt模板库

```python
# 使用PromptTemplateManager创建自己的模板库

manager = PromptTemplateManager()

# 添加自定义模板
my_template = PromptTemplate(
    id="my_code_review",
    name="我的代码审查",
    description="针对Java代码的审查",
    system_prompt="...",
    few_shot_examples=[...],
)

manager.add_template(my_template)
manager.export_library("my_templates.yaml")
```

---

## ✅ 今日产出检查清单

- [ ] 理解System Prompt的设计原则
- [ ] 能够设计高质量的System Prompt
- [ ] 掌握Few-shot示例选择方法
- [ ] 能够使用Chain-of-Thought方法
- [ ] 创建了至少3个Prompt模板
- [ ] 理解Prompt模板库的管理

---

## 📝 课后作业

1. **完善模板库**: 创建10个以上的Prompt模板，覆盖不同场景
2. **A/B测试**: 设计两个版本的System Prompt，对比效果
3. **动态Few-shot**: 实现基于相似度的动态示例选择
4. **Prompt优化**: 选择之前写的Prompt，应用今天学到的技巧优化
5. **思考**: Prompt Engineering和Fine-tuning各适用于什么场景？

---

**文档版本**: 1.0  
**创建日期**: 2026-04-26  
**作者**: AI Learning Platform
