# Day 4 - 模型选择：没有银弹，只有权衡

## 为什么没有一个模型解决所有问题

如果你来自Java世界，你可能习惯了"最佳实践"——用Spring Boot做Web、用Kafka做消息队列、用Redis做缓存。每个领域都有一个主流选择。

ML不是这样。没有一个算法在所有问题上都是最好的——这是**No Free Lunch定理**的核心思想。

但这不意味着模型选择是玄学。它是一种权衡分析——就像你在技术选型时权衡一致性vs可用性一样。

## 模型选择的三个维度

### 维度1：数据特征

| 数据特征 | 推荐模型 | 原因 |
|----------|----------|------|
| 结构化表格数据 | 树模型(XGBoost/LightGBM) | 表格数据的SOTA |
| 图像 | CNN/ViT | 空间结构信息 |
| 文本 | Transformer | 序列依赖 |
| 小数据(<1000样本) | 简单模型(LR/SVM) | 复杂模型会过拟合 |
| 高维稀疏 | 线性模型+正则 | 树模型在稀疏特征上表现差 |
| 类别特征多 | CatBoost | 专门处理类别特征 |

### 维度2：业务约束

| 约束 | 影响 | 选择 |
|------|------|------|
| 需要可解释性 | 监管/合规要求 | LR、决策树、SHAP辅助 |
| 预测延迟要求高 | 实时推理 | 轻量模型、模型压缩 |
| 训练数据持续增长 | 增量学习 | 在线学习、增量训练 |
| 分布式训练需求 | 大数据场景 | XGBoost分布式、Spark ML |
| 公平性要求 | 反歧视 | 可解释模型+公平性审计 |

### 维度3：团队能力

| 团队水平 | 推荐策略 | 原因 |
|----------|----------|------|
| ML新手 | sklearn简单模型 | 可解释、易调试 |
| 有ML经验 | XGBoost/LightGBM | 表格数据最优 |
| 深度学习团队 | PyTorch | 灵活、研究友好 |
| 工程团队 | AutoML(H2O/Auto-sklearn) | 降低ML门槛 |

## 核心算法直觉

### 线性模型：最简单但最被低估

```python
from sklearn.linear_model import LogisticRegression

# 逻辑回归的决策边界是一条直线（或超平面）
# 优点：快、可解释、不容易过拟合
# 缺点：只能学线性关系
model = LogisticRegression(C=1.0, penalty='l2')
```

**什么时候用**：
- 特征和目标的关系近似线性
- 需要概率输出（不只是分类）
- 需要可解释性（系数=特征重要性）
- Baseline模型（总是先试线性模型）

### 决策树：直观但脆弱

```python
from sklearn.tree import DecisionTreeClassifier

# 决策树 = if-else规则树
# 优点：直观、无需特征缩放、可处理混合类型
# 缺点：极度过拟合、不稳定（数据微变→树大变）
model = DecisionTreeClassifier(max_depth=5, min_samples_leaf=10)
```

**类比Java**：决策树就是你写的if-else规则引擎，只是规则是从数据中学的。

### 随机森林：集体的智慧

```python
from sklearn.ensemble import RandomForestClassifier

# 核心思想：训多棵树，投票决定
# 1. 每棵树用不同的数据子集（Bagging）
# 2. 每次分裂用不同的特征子集
# 3. 多棵不相关的树 → 降低方差
model = RandomForestClassifier(n_estimators=100, max_depth=10)
```

**为什么有效**：
- 单棵决策树：高方差（过拟合）
- 多棵独立决策树投票：方差降低
- 关键：树之间要"不相关"→ 数据+特征双重随机

**类比**：就像Code Review，一个评审可能有偏见，5个独立评审投票更可靠。

### 梯度提升树：当前的表格数据之王

```python
from sklearn.ensemble import GradientBoostingClassifier
# 或更好：import xgboost as xgb / import lightgbm as lgb

# 核心思想：每棵新树修正上一棵的错误
# 1. 第1棵树拟合数据
# 2. 第2棵树拟合残差（第1棵树的错误）
# 3. 第3棵树拟合残差的残差
# 4. ...逐步提升
model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5)
```

**随机森林 vs 梯度提升**：

| 维度 | 随机森林 | 梯度提升 |
|------|----------|----------|
| 训练方式 | 并行（树独立） | 串行（树依赖） |
| 过拟合风险 | 较低 | 较高（需要调参） |
| 精度 | 好 | 更好 |
| 调参难度 | 简单 | 中等 |
| 推荐场景 | Baseline/快速迭代 | 追求最佳性能 |

### SVM：高维空间的利器

```python
from sklearn.svm import SVC

# 核心思想：找到最宽的"马路"把两类分开
# 核技巧：把数据映射到高维空间，使线性可分
model = SVC(kernel='rbf', C=1.0)
```

**什么时候用**：
- 中小规模数据（<10万样本）
- 高维特征（如文本TF-IDF）
- 类别边界复杂

**缺点**：大数据量训练极慢，不如树模型实用。

### KNN：最直觉的算法

```python
from sklearn.neighbors import KNeighborsClassifier

# 核心思想：你的邻居是什么，你就是什么
# 1. 存储所有训练数据
# 2. 预测时找最近的K个邻居
# 3. 投票决定类别
model = KNeighborsClassifier(n_neighbors=5)
```

**缺点**：
- 预测时需要扫描全部训练数据→慢
- 高维空间距离失效（维数灾难）
- 对特征缩放敏感

## 模型选择的实用流程

### Step 1: 总是从简单模型开始

```python
# Step 1a: Logistic Regression as baseline
baseline = LogisticRegression(random_state=42)
baseline.fit(X_train, y_train)
baseline_score = f1_score(y_test, baseline.predict(X_test))
print(f"Baseline (LR): F1={baseline_score:.3f}")

# Step 1b: Quick check with Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
rf_score = f1_score(y_test, rf.predict(X_test))
print(f"Random Forest: F1={rf_score:.3f}")

# 如果RF没有显著好于LR → 数据可能主要是线性关系
# 如果RF好很多 → 数据有非线性模式，值得尝试更复杂模型
```

### Step 2: 根据Baseline选择方向

```
LR vs RF 比较
├─ RF >> LR → 数据有强非线性 → 试XGBoost/LightGBM
├─ RF ≈ LR  → 数据主要是线性 → 坚持LR，优化特征
└─ LR > RF  → 过拟合或数据太少 → 增加数据或简化模型
```

### Step 3: 超参数调优

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

# Grid Search（穷举——适合少参数）
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15],
    'learning_rate': [0.01, 0.1, 0.3]
}

# Random Search（随机——适合多参数，更高效）
from scipy.stats import uniform, randint
param_dist = {
    'n_estimators': randint(50, 300),
    'max_depth': randint(3, 15),
    'learning_rate': uniform(0.01, 0.3)
}

search = RandomizedSearchCV(
    GradientBoostingClassifier(random_state=42),
    param_distributions=param_dist,
    n_iter=50,  # 只试50组
    cv=5,
    scoring='f1',
    random_state=42,
    n_jobs=-1
)
search.fit(X_train, y_train)
print(f"Best params: {search.best_params_}")
print(f"Best CV F1: {search.best_score_:.3f}")
```

## 偏差-方差权衡：ML的终极权衡

### 核心概念

```
总误差 = 偏差² + 方差 + 不可约误差

偏差(Bias)：模型对问题的错误假设 → 欠拟合
方差(Variance)：模型对训练数据的敏感度 → 过拟合
不可约误差：数据本身的噪声 → 无法消除
```

### 直觉理解

- **高偏差**：用直线拟合抛物线→怎么调都拟合不好
- **高方差**：用100阶多项式拟合10个点→完美通过每个点但对新数据灾难
- **理想**：找到偏差和方差的最佳平衡点

### 模型复杂度与偏差-方差

| 模型 | 偏差 | 方差 | 过拟合风险 |
|------|------|------|-----------|
| LR | 高 | 低 | 低 |
| 决策树(深) | 低 | 高 | 高 |
| 随机森林 | 中 | 低 | 低 |
| XGBoost | 低 | 中 | 中 |
| 深度神经网络 | 很低 | 很高 | 很高 |

### 诊断方法

```python
# 学习曲线：看训练误差和验证误差随数据量变化
from sklearn.model_selection import learning_curve

train_sizes, train_scores, val_scores = learning_curve(
    model, X_train, y_train, cv=5, 
    train_sizes=np.linspace(0.1, 1.0, 10),
    scoring='f1'
)

train_mean = train_scores.mean(axis=1)
val_mean = val_scores.mean(axis=1)

if train_mean[-1] - val_mean[-1] > 0.1:
    print("过拟合：训练分数远高于验证分数")
    print("→ 增加正则化/减少特征/增加数据")
elif train_mean[-1] < 0.7 and val_mean[-1] < 0.7:
    print("欠拟合：训练和验证分数都很低")
    print("→ 更复杂模型/更多特征/减少正则化")
```

## 模型选择速查表

```
你的数据是什么？
├─ 表格/结构化
│   ├─ <1000样本 → LogisticRegression / SVM
│   ├─ 1K-100K样本 → RandomForest → XGBoost
│   └─ >100K样本 → LightGBM（最快）/ XGBoost
├─ 图像
│   └─ CNN（小数据用迁移学习）
├─ 文本
│   ├─ 分类/NER → Transformer微调
│   └─ 简单分类 → TF-IDF + LR（Baseline）
└─ 时序
    ├─ 简单 → ARIMA / Prophet
    └─ 复杂 → LSTM / Transformer
```

## 今日要点

1. **No Free Lunch**：没有银弹，模型选择是权衡分析
2. **总是从简单模型开始**：LR Baseline → RF验证非线性 → XGBoost追求最优
3. **偏差-方差权衡**是理解模型行为的框架
4. **超参数调优用Random Search**，比Grid Search更高效
5. **业务约束决定模型选择**：可解释性/延迟/公平性比精度更重要

> 下一步：Day 5我们将深入评估策略——为什么准确率是最差的评估指标，以及如何选择正确的评估框架。
