# Day 1 - ML不是调参：问题建模与数据思维

## 你以为的ML vs 真正的ML

如果你来自传统软件开发，你大概觉得ML是这样的：

```
1. 拿到数据
2. 调用 model.fit()
3. 调用 model.predict()
4. 上线
```

这个流程技术上没错，但它忽略了ML项目最关键的80%工作——**问题建模**。

想想你在后端开发中的经验：如果需求文档写错了，代码写得再漂亮也是白搭。ML项目也一样，甚至更严重——因为ML的"需求"不是产品经理写的PRD，而是你对问题的**数学抽象**。

## 从Java思维到ML思维

### 思维转换1：确定性 → 概率性

传统软件的逻辑是确定性的：

```java
if (user.getAge() > 18) {
    return "adult";
} else {
    return "minor";
}
```

ML的逻辑是概率性的：

```python
model.predict_proba([[age=18]])  # → [0.47, 0.53]
```

这意味着：
- **同样的输入，每次预测可能不同**（取决于训练数据）
- **你永远无法100%确定预测是对的**（只能量化置信度）
- **边界是模糊的**（18岁和18岁零1天的区别，传统软件一秒搞定，ML需要学）

### 思维转换2：代码是数据 → 数据是代码

传统软件中，业务逻辑写在代码里。ML中，业务逻辑"编码"在模型参数里：

| 维度 | 传统软件 | ML系统 |
|------|----------|--------|
| 逻辑在哪里 | 源代码 | 训练数据 + 模型参数 |
| Bug修复 | 改代码 | 改数据/重新训练 |
| 测试方式 | 断言输入输出 | 统计意义上的正确率 |
| 复杂度增长 | 代码量增长 | 数据量增长 |
| 可解释性 | 看代码就懂 | 看参数看不懂 |

### 思维转换3：手写规则 → 学习规则

传统方式——风控规则引擎：

```java
public boolean isFraud(Transaction tx) {
    if (tx.getAmount() > 10000 && tx.getCountry().equals("高风险国家")) return true;
    if (tx.getFrequencyLast24h() > 5) return true;
    // ... 几百条规则
    return false;
}
```

ML方式：

```python
model = RandomForestClassifier()
model.fit(historical_transactions, fraud_labels)
model.predict(new_transaction)  # → 自动学习规则
```

**关键问题**：什么时候用规则引擎，什么时候用ML？

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 规则明确、极少变化 | 规则引擎 | 可解释、可审计、确定性 |
| 规则复杂、持续变化 | ML | 人写不完的规则让模型学 |
| 合规要求严格 | 规则引擎 | 监管需要解释每一条决策 |
| 模式隐藏在数据中 | ML | 人看不到的模式模型能发现 |

**最佳实践**：不是二选一，而是规则 + ML 混合。规则处理已知边界，ML处理模糊地带。

## 问题建模：ML项目的第一步

### 好的问题定义长什么样

一个ML问题定义必须回答5个问题：

1. **业务目标**：我们要优化什么？（比如：降低客户流失率）
2. **ML目标**：如何把业务目标翻译成数学问题？（比如：预测客户下月是否续约）
3. **成功标准**：模型做到什么程度算成功？（比如：F1 > 0.8，且recall > 0.9）
4. **数据来源**：训练数据从哪来？标签怎么获得？
5. **约束条件**：延迟要求？可解释性？公平性？

举个具体例子——**信用卡反欺诈**：

```
业务目标：降低欺诈损失，同时不误杀正常用户
ML目标：  判断一笔交易是否为欺诈（二分类）
成功标准：recall > 0.95（不能漏欺诈），precision > 0.5（误杀可控）
数据来源：历史交易记录 + 用户反馈标签
约束条件：预测延迟 < 100ms，可解释（监管要求）
```

### 坏的问题定义长什么样

❌ "我要做一个AI模型预测股票涨跌"

问题在于：
- 什么时间尺度？分钟？日？月？
- 涨多少算"涨"？0.01%？1%？5%？
- 训练数据是什么？技术指标？新闻？资金流？
- 交易成本考虑了吗？滑点呢？

❌ "用ML提高推荐系统效果"

问题在于：
- "效果"是什么指标？点击率？转化率？用户停留时间？
- A/B test基准是什么？
- 冷启动怎么处理？

### 问题分类：选择正确的ML范式

```
                有标签？
               /       \
             是          否
            /              \
     监督学习            无监督学习
     /    |    \         /        \
  分类  回归  序列     聚类     降维
  |      |     |       |         |
 离散  连续  有序    发现模式  压缩特征
 输出  输出  输出
```

常见业务场景→ML范式映射：

| 业务场景 | ML范式 | 典型算法 |
|----------|--------|----------|
| 垃圾邮件检测 | 二分类 | Naive Bayes, SVM |
| 商品推荐 | 多分类/排序 | 协同过滤, FM |
| 房价预测 | 回归 | Linear Regression, XGBoost |
| 用户分群 | 聚类 | K-Means, DBSCAN |
| 文档主题发现 | 降维+聚类 | LDA, NMF |
| 机器翻译 | 序列到序列 | Transformer |
| 异常检测 | One-class/无监督 | Isolation Forest, AutoEncoder |

## 数据思维：ML项目的燃料

### 数据质量的6个维度

你在后端开发中关心数据一致性（ACID）。ML中你需要关心更多：

1. **准确性**：标签是否正确？传感器数据有没有噪声？
2. **完整性**：缺失值比例多少？是随机缺失还是系统性缺失？
3. **一致性**：同一实体在不同数据源中是否一致？
4. **时效性**：训练数据的时间范围？概念漂移（Concept Drift）的风险？
5. **代表性**：训练数据是否代表真实分布？有没有选择偏差？
6. **数量**：样本量够不够？类别是否平衡？

### 一个真实的教训

某银行做信用评分模型，训练数据是2019-2021年的贷款记录。模型在验证集上AUC=0.92，上线后：

- 2022年利率环境剧变 → 用户还款行为变化
- 新客户群体（自由职业者）占比上升 → 训练数据中几乎没有
- 线上AUC跌到0.71

**教训**：数据不是静态的，模型也不是一训练就完事。需要**监控数据分布变化**和**定期重训练**。

### 数据泄露：ML项目最隐蔽的Bug

数据泄露（Data Leakage）是ML特有的Bug——训练时模型"偷看"了它不该看到的信息。

经典案例：

```python
# ❌ 数据泄露：先标准化再切分
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # 用了全部数据计算均值和方差
X_train, X_test = train_test_split(X_scaled, test_size=0.2)
# 测试集的信息泄露到了训练过程中！

# ✅ 正确做法：先切分再标准化
X_train, X_test = train_test_split(X, test_size=0.2)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # 只用训练集fit
X_test_scaled = scaler.transform(X_test)          # 用训练集的参数transform
```

常见泄露场景：

| 泄露类型 | 描述 | 检测方法 |
|----------|------|----------|
| 预处理泄露 | 全局标准化/特征选择后再切分 | 验证预处理是否只用训练集 |
| 时间泄露 | 用未来数据预测过去 | 检查时间切分 |
| 标签泄露 | 特征中隐含了标签信息 | 检查特征与标签的相关性 |
| 重复样本泄露 | 同一实体的多条记录分散在训练和测试集 | 按实体ID切分 |

**类比后端开发**：数据泄露就像测试时连了生产数据库——你的测试结果毫无意义，但你不知道。

## Python环境：ML工程师的工具箱

### 你需要的核心库

```python
# 数据处理
import numpy as np          # 数值计算（你已经在Phase 2用过）
import pandas as pd         # 表格数据处理——ML的"SQL"

# 可视化
import matplotlib.pyplot as plt    # 基础绘图
import seaborn as sns              # 统计可视化

# ML框架
from sklearn.model_selection import train_test_split    # 数据切分
from sklearn.preprocessing import StandardScaler        # 特征标准化
from sklearn.linear_model import LogisticRegression    # 逻辑回归
from sklearn.ensemble import RandomForestClassifier    # 随机森林
from sklearn.metrics import accuracy_score, f1_score   # 评估指标
```

### Pandas：ML的数据操作利器

如果你熟悉SQL，Pandas的对照：

| SQL | Pandas | 用途 |
|-----|--------|------|
| SELECT col1, col2 | df[['col1', 'col2']] | 选择列 |
| WHERE age > 18 | df[df['age'] > 18] | 过滤行 |
| GROUP BY city | df.groupby('city') | 分组 |
| JOIN | pd.merge(df1, df2) | 连接表 |
| ORDER BY age DESC | df.sort_values('age', ascending=False) | 排序 |
| COUNT(*) | df.shape[0] | 计数 |

### 一个完整的ML项目骨架

```python
# 1. 加载数据
df = pd.read_csv('data.csv')

# 2. 探索性数据分析（EDA）
print(df.shape)           # (行数, 列数)
print(df.dtypes)          # 每列数据类型
print(df.describe())      # 统计摘要
print(df.isnull().sum())  # 缺失值统计

# 3. 问题建模
# 业务目标 → ML目标 → 成功标准

# 4. 数据切分（先切分！防止数据泄露）
X = df.drop('target', axis=1)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. 特征工程（只用训练集fit）
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 6. 模型训练
model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# 7. 评估
y_pred = model.predict(X_test_scaled)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
print(f"F1: {f1_score(y_test, y_pred):.3f}")

# 8. 分析错误
errors = X_test[y_pred != y_test]
print(f"误分类样本数: {len(errors)}")
```

## 从今天开始：你的第一个ML思维训练

### 练习1：问题分类

对以下业务场景，判断应该用什么ML范式（分类/回归/聚类/其他）：

1. 预测明天北京的温度 → **回归**（连续值输出）
2. 判断一封邮件是否是钓鱼邮件 → **二分类**
3. 把电商用户分成不同消费群体 → **聚类**
4. 预测股票价格走势（涨/跌/平） → **多分类**（注意：不是回归！因为交易决策是离散的）

### 练习2：识别数据泄露

```python
# 以下代码有什么问题？
df = pd.read_csv('loan.csv')
df['income_per_person'] = df['income'] / df['household_size']  # 特征工程

# 去掉高相关性特征
corr = df.corr()
high_corr_features = [col for col in corr.columns if any(corr[col] > 0.95)]
df = df.drop(high_corr_features, axis=1)  # ⚠️ 用了全部数据算相关性

# 标准化
scaler = StandardScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)  # ⚠️ 用了全部数据

# 切分
X = df_scaled.drop('default', axis=1)
y = df_scaled['default']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LogisticRegression()
model.fit(X_train, y_train)
```

**问题**：
1. 相关性计算用了全部数据 → 特征选择泄露
2. 标准化用了全部数据 → 预处理泄露
3. 正确做法：先切分，再在训练集上做特征选择和标准化

### 练习3：定义你自己的ML问题

选一个你工作中遇到的真实场景，按5要素框架定义：
1. 业务目标
2. ML目标
3. 成功标准
4. 数据来源
5. 约束条件

## 今日要点

1. **ML项目的80%是问题建模**，不是调参。问题定义错了，模型再好也白搭。
2. **数据泄露是ML最隐蔽的Bug**，记住：所有预处理操作只用训练集fit。
3. **规则和ML不是对立的**，生产系统通常是混合架构。
4. **数据是燃料**，质量比数量更重要。6个维度评估数据质量。
5. **从业务目标到ML目标**的翻译是ML工程师最核心的能力。

> 下一步：Day 2我们将深入数据预处理——如何在数据进入模型之前，建立一道"垃圾进垃圾出"的防线。
