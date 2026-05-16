#!/usr/bin/env python3
"""
Batch deepen AILP course content for Phase 3-6.
Strategy: modify COURSES_DATA in memory, write back as Python source.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.data.courses_extended_fixed import COURSES_DATA

# Deep content for each chapter, keyed by chapter title
DEEPENED = {}

# ============================================================
# Phase 3: 机器学习 (chapters 12-23)
# ============================================================

DEEPENED["第12章：机器学习概述与Scikit-Learn入门"] = """# 机器学习概述与Scikit-Learn入门

## 🎯 学习目标
- 理解机器学习三大范式的本质区别，能判断一个业务场景该用哪种范式
- 掌握Scikit-Learn的fit/predict/transform统一接口设计思想
- 从零完成一个完整的ML项目：数据加载→预处理→训练→评估→预测

---

## 1. 什么是机器学习？——从规则到数据

### 1.1 传统编程 vs 机器学习

传统编程是"人写规则，机器执行"：

```python
# 传统方式：手动写规则判断垃圾邮件
def is_spam(email):
    if "免费" in email.subject and "中奖" in email.body:
        return True
    if email.sender.endswith("@spam.com"):
        return True
    # ... 越写越多，永远覆盖不完
    return False
```

机器学习是"人给数据，机器学规则"：

```python
# ML方式：让模型从数据中自动学习
from sklearn.naive_bayes import MultinomialNB

model = MultinomialNB()
model.fit(X_train_emails, y_train_labels)  # 喂数据，学规则
y_pred = model.predict(X_test_emails)       # 用学到的规则预测
```

**核心转变**：你不再是规则的编写者，而是数据的提供者和质量的把关者。

### 1.2 什么时候该用机器学习？

| 适合ML的场景 | 不适合ML的场景 |
|-------------|---------------|
| 规则太多太复杂，人工写不完 | 规则简单明确，几行if-else搞定 |
| 规则经常变化（反欺诈、推荐） | 需要精确数学证明（银行利息计算） |
| 有大量历史数据可学习 | 数据极少（< 100条） |
| 允许一定误差（预测而非精确计算） | 必须100%准确（航空航天控制） |

---

## 2. 三大范式：监督、无监督、强化

### 2.1 监督学习——有老师的学习

**核心**：你有"标准答案"（标签），模型学习输入→输出的映射。

| 类型 | 预测目标 | 举例 | 标签类型 |
|------|---------|------|---------|
| 分类 | 离散类别 | 邮件是否垃圾、客户是否流失 | 类别标签 |
| 回归 | 连续数值 | 房价、销量、温度 | 数值 |

**关键直觉**：如果你能给每条数据标注一个"正确答案"，就是监督学习。

### 2.2 无监督学习——自己找规律

**核心**：没有标准答案，模型自己发现数据中的结构。

```python
# 聚类：自动发现客户群体
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=3)
groups = kmeans.fit_predict(customer_features)

# 降维：把高维数据压缩到2D来可视化
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
X_2d = pca.fit_transform(X_high_dim)
```

### 2.3 如何选择？

```
你有标签数据吗？
├── 是 → 监督学习
│   ├── 标签是类别 → 分类（逻辑回归、随机森林、SVM）
│   └── 标签是数值 → 回归（线性回归、XGBoost）
└── 否 → 无监督学习
    ├── 想分组 → 聚类（K-Means、DBSCAN）
    └── 想压缩 → 降维（PCA、t-SNE）
```

---

## 3. Scikit-Learn设计哲学：统一的API

### 3.1 所有模型共享同一套API

```python
# 不管用什么模型，流程都一样：
model = SomeModel(超参数)     # 1. 创建模型
model.fit(X_train, y_train)   # 2. 训练
y_pred = model.predict(X_test) # 3. 预测

# 换模型只需改一行，其他代码不动
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# 三个模型，完全相同的API
for ModelClass in [LogisticRegression, RandomForestClassifier, SVC]:
    m = ModelClass()
    m.fit(X_train, y_train)
    print(m.predict(X_test))
```

### 3.2 预处理器也共享API

```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)  # 训练集: fit + transform
X_test_scaled = scaler.transform(X_test)   # 测试集: 只transform！
```

⚠️ **常见错误**：在测试集上用 `fit_transform`！会导致数据泄露。正确做法：训练集 `fit_transform`，测试集只 `transform`。

---

## 4. 完整实战：鸢尾花分类

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Step 1: 加载数据
iris = load_iris()
X, y = iris.data, iris.target

# Step 2: 划分数据集 (stratify保证类别比例一致)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Step 3: 特征标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 4: 训练
model = LogisticRegression(max_iter=200)
model.fit(X_train_scaled, y_train)

# Step 5: 预测与评估
y_pred = model.predict(X_test_scaled)
print(f"准确率: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=iris.target_names))

# Step 6: 预测新数据
new_flower = np.array([[5.1, 3.5, 1.4, 0.2]])
print(f"预测: {iris.target_names[model.predict(scaler.transform(new_flower))[0]]}")

# 预测概率
proba = model.predict_proba(scaler.transform(new_flower))
for name, p in zip(iris.target_names, proba[0]):
    print(f"  {name}: {p:.4f}")
```

---

## 5. 常见陷阱与最佳实践

| 陷阱 | 正确做法 |
|------|---------|
| 测试集上fit_transform | 训练集fit_transform，测试集只transform |
| 不设random_state | 固定random_state确保可复现 |
| 只看accuracy | 看classification_report + confusion_matrix |
| 不做特征标准化 | 大多数模型需要标准化（树模型除外） |
| 用全部数据训练 | 必须划分训练/测试集评估泛化能力 |

---

## ✅ 检查点

- [ ] 能解释传统编程和机器学习的本质区别
- [ ] 能判断一个场景该用监督学习还是无监督学习
- [ ] 理解sklearn的fit/predict/transform统一接口
- [ ] 能独立完成：加载数据→预处理→训练→评估→预测的完整流程
- [ ] 理解为什么测试集不能fit，以及数据泄露的危害
"""

DEEPENED["第13章：特征工程"] = """# 特征工程

## 🎯 学习目标
- 理解特征工程在ML中的决定性地位："数据和特征决定了ML的上限，模型只是逼近这个上限"
- 掌握特征缩放、编码、构造、选择的实战方法
- 能根据数据特点选择正确的预处理策略，避免常见错误

---

## 1. 为什么特征工程如此重要？

Andrew Ng的名言：**"Applied ML is basically feature engineering."**

```python
# 假设你要预测房价，原始数据有：面积、卧室数、建造年份
# 不好：直接用原始特征
X_raw = df[['area', 'bedrooms', 'year_built']]

# 好：构造更有表达力的特征
X_engineered = pd.DataFrame({
    'area': df['area'],
    'bedrooms': df['bedrooms'],
    'age': 2024 - df['year_built'],            # 房龄比建造年份更直观
    'area_per_bedroom': df['area'] / df['bedrooms'],  # 单卧室面积
    'is_new': (df['year_built'] > 2015).astype(int),  # 是否新房
})
```

特征工程把"模型需要自己学的规律"变成了"特征直接告诉模型的规律"。

---

## 2. 特征缩放：让特征在同一量级上

### 2.1 三种缩放方法

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import numpy as np

# 测试数据（含异常值）
X = np.array([[1], [2], [3], [4], [5], [100]])

# StandardScaler: (x-均值)/标准差 → 均值0, 标准差1
# 适用: 大多数场景，线性模型、SVM、神经网络
scaler = StandardScaler()
X_std = scaler.fit_transform(X)

# MinMaxScaler: (x-min)/(max-min) → [0,1]
# 适用: 需要固定范围的场景，神经网络输入
mm = MinMaxScaler()
X_mm = mm.fit_transform(X)

# RobustScaler: (x-中位数)/IQR → 对异常值鲁棒
# 适用: 数据有明显异常值
rs = RobustScaler()
X_robust = rs.fit_transform(X)
```

### 2.2 选择决策

| 场景 | 推荐方法 | 原因 |
|------|---------|------|
| 一般情况 | StandardScaler | 最通用 |
| 数据有明显异常值 | RobustScaler | 不被异常值影响 |
| 需要固定范围(0-1) | MinMaxScaler | 神经网络、图像处理 |
| 树模型(Random Forest等) | **不需要缩放** | 树模型基于排序，与尺度无关 |

---

## 3. 特征编码：让模型读懂类别

### 3.1 LabelEncoding vs OneHotEncoding

```python
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# LabelEncoding: 有序类别（小<中<大）
sizes = ['S', 'M', 'L', 'M', 'S', 'XL']
le = LabelEncoder()
sizes_encoded = le.fit_transform(sizes)  # [2, 1, 3, 1, 2, 4]
# ⚠️ 模型可能认为4>2是数值大小关系，只有类别有序时才用

# OneHotEncoding: 无序类别（颜色、城市）
df = pd.DataFrame({'color': ['红', '绿', '蓝', '红']})
df_encoded = pd.get_dummies(df, columns=['color'], drop_first=True)
# drop_first=True: 删掉一列避免多重共线性（线性模型必须！）
```

### 3.2 高基数类别的处理

```python
# 如果类别有1000个不同的值（如城市名），独热编码会产生1000列！
# 目标编码：用该类别的目标均值替代
city_target_mean = df.groupby('city')['price'].mean()
df['city_encoded'] = df['city'].map(city_target_mean)

# 频率编码：用该类别的出现频率替代
city_freq = df['city'].value_counts(normalize=True)
df['city_freq'] = df['city'].map(city_freq)
```

```
类别特征有几个不同的值？
├── < 10个 → 独热编码(drop_first=True)
├── 10-50个 → 独热编码或目标编码
└── > 50个 → 目标编码 / 频率编码
```

---

## 4. 特征构造与选择

### 4.1 特征构造

```python
# 时间特征
df['order_hour'] = df['order_date'].dt.hour
df['is_weekend'] = df['order_date'].dt.dayofweek >= 5

# 交互特征
df['bmi'] = df['weight'] / (df['height'] / 100) ** 2
df['area_per_room'] = df['area'] / df['rooms']

# 多项式特征（捕捉非线性关系）
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X[['age', 'income']])
# 自动生成: age, income, age^2, age*income, income^2
```

### 4.2 特征选择三大方法

```python
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.ensemble import RandomForestClassifier

# 方法1: 过滤法 - 统计检验，快但不考虑模型
selector = SelectKBest(f_classif, k=2)
X_selected = selector.fit_transform(X, y)

# 方法2: 包装法(RFE) - 用模型评估，准但慢
rfe = RFE(RandomForestClassifier(n_estimators=50), n_features_to_select=2)
X_rfe = rfe.fit_transform(X, y)

# 方法3: 嵌入法 - 训练时自动选择（日常首选）
model = RandomForestClassifier(n_estimators=50)
model.fit(X, y)
print(pd.Series(model.feature_importances_, index=feature_names).sort_values(ascending=False))
```

| 方法 | 速度 | 准确性 | 适用场景 |
|------|------|--------|---------|
| 过滤法 | 最快 | 一般 | 快速筛选，特征>1000 |
| 包装法 | 最慢 | 最高 | 特征少，要最佳子集 |
| 嵌入法 | 中等 | 高 | 日常首选 |

---

## 5. Pipeline：防止数据泄露的最佳实践

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_features),
    ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features),
])

pipe = Pipeline([('preprocessor', preprocessor), ('classifier', LogisticRegression())])

# Pipeline + cross_val_score = 防止数据泄露的黄金标准
scores = cross_val_score(pipe, X, y, cv=5, scoring='accuracy')
print(f"CV准确率: {scores.mean():.4f} +/- {scores.std():.4f}")
```

---

## ✅ 检查点

- [ ] 能解释三种特征缩放方法的区别和适用场景
- [ ] 知道什么情况下用LabelEncoding vs OneHotEncoding
- [ ] 理解高基数类别的处理策略
- [ ] 能构造有效的衍生特征
- [ ] 掌握三种特征选择方法的特点
- [ ] 理解Pipeline如何防止数据泄露
"""

DEEPENED["第14章：线性回归与正则化"] = """# 线性回归与正则化

## 🎯 学习目标
- 理解线性回归的数学原理：从最小二乘法到闭式解
- 掌握L1(Lasso)和L2(Ridge)正则化的本质区别与选择策略
- 能用回归指标(MSE/MAE/R2)评估模型并理解其含义

---

## 1. 线性回归：最简单也最深刻的模型

线性回归假设目标值是特征的线性组合：y = w1*x1 + w2*x2 + ... + b

### 1.1 手动实现最小二乘法

```python
import numpy as np

def least_squares(X, y):
    X_b = np.c_[np.ones((X.shape[0], 1)), X]  # 添加偏置列
    w = np.linalg.inv(X_b.T @ X_b) @ X_b.T @ y  # 闭式解
    return w

np.random.seed(42)
X = 2 * np.random.rand(100, 1)
y = 4 + 3 * X + np.random.randn(100, 1)
w = least_squares(X, y)
print(f"截距: {w[0]:.4f}, 斜率: {w[1]:.4f}")  # ≈ 4.0, 3.0
```

### 1.2 sklearn实现

```python
from sklearn.linear_model import LinearRegression
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

housing = fetch_california_housing()
X, y = housing.data, housing.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

lr = LinearRegression()
lr.fit(X_train_s, y_train)

# 系数反映特征重要性
import pandas as pd
coef_df = pd.DataFrame({'feature': housing.feature_names, 'coef': lr.coef_})
print(coef_df.sort_values('coef', key=abs, ascending=False))
```

---

## 2. 过拟合与正则化

正则化 = 在损失函数中加惩罚项，限制系数大小。L = MSE(w) + lambda*惩罚项(w)

### 2.1 Ridge回归 (L2正则化)

```python
from sklearn.linear_model import Ridge

# 惩罚项: lambda*sum(wi^2) → 系数被压缩但不为零
ridge = Ridge(alpha=1.0)
ridge.fit(X_train_s, y_train)
# 适用：特征都有用，只想控制过拟合
```

### 2.2 Lasso回归 (L1正则化)

```python
from sklearn.linear_model import Lasso

# 惩罚项: lambda*sum(|wi|) → 部分系数直接变零，自动特征选择
lasso = Lasso(alpha=0.1)
lasso.fit(X_train_s, y_train)
print(f"非零系数: {np.sum(lasso.coef_ != 0)}/{len(lasso.coef_)}")
# 适用：特征很多但只有少数有用
```

### 2.3 Ridge vs Lasso

| 维度 | Ridge (L2) | Lasso (L1) |
|------|-----------|-----------|
| 系数效果 | 压缩但非零 | 部分变零 |
| 特征选择 | 保留所有特征 | 自动选择 |
| 适用场景 | 特征都有用 | 特征多但多数无用 |

---

## 3. 回归评估指标

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

y_pred = lr.predict(X_test_s)

mse = mean_squared_error(y_test, y_pred)    # 惩罚大误差
rmse = np.sqrt(mse)                          # 和y同量级，更直观
mae = mean_absolute_error(y_test, y_pred)    # 对异常值鲁棒
r2 = r2_score(y_test, y_pred)                # 0-1，模型解释了多少方差

# R2解读: 0.6 = 模型解释了60%的变化; <0 = 比均值还烂
```

---

## 4. 用交叉验证选择最佳alpha

```python
from sklearn.linear_model import RidgeCV, LassoCV

ridge_cv = RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0, 100.0], cv=5)
ridge_cv.fit(X_train_s, y_train)
print(f"最佳alpha: {ridge_cv.alpha_}, 测试R2: {ridge_cv.score(X_test_s, y_test):.4f}")
```

---

## ✅ 检查点

- [ ] 能用数学公式解释线性回归的原理
- [ ] 理解Ridge和Lasso的本质区别：压缩 vs 稀疏
- [ ] 知道什么场景用Ridge，什么场景用Lasso
- [ ] 能解释MSE/MAE/R2的含义和选择依据
- [ ] 会用RidgeCV/LassoCV自动选择正则化强度
"""

DEEPENED["第15章：逻辑回归与分类算法"] = """# 逻辑回归与分类算法

## 🎯 学习目标
- 理解逻辑回归的数学本质：从线性回归到Sigmoid的转换
- 掌握分类评估指标体系：Accuracy/Precision/Recall/F1/AUC的选择策略
- 能根据业务场景选择正确的评估指标

---

## 1. 逻辑回归：名字叫回归，其实是分类

### 1.1 Sigmoid函数

```python
import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# sigmoid(0) = 0.5 (不确定)
# sigmoid(大正值) ≈ 1 (确定正类)
# sigmoid(大负值) ≈ 0 (确定负类)
# 输出是概率！P > 0.5 → 预测为正类
```

线性回归输出连续值，逻辑回归通过Sigmoid映射到(0,1)作为概率。

### 1.2 完整实现

```python
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer()
X, y = data.data, data.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train_s, y_train)

y_prob = model.predict_proba(X_test_s)  # 概率
y_pred = model.predict(X_test_s)         # 类别
```

---

## 2. 分类评估指标：Accuracy远远不够

### 2.1 为什么Accuracy不够？

1000人中只有10人患病，模型预测所有人都健康 → Accuracy=99%，但完全没用。

### 2.2 混淆矩阵与四大指标

```
                  预测正类    预测负类
实际正类          TP(真正例)  FN(假负例)
实际负类          FP(假正例)  TN(真负例)
```

```python
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_auc_score)

cm = confusion_matrix(y_test, y_pred)
TN, FP, FN, TP = cm.ravel()

accuracy  = accuracy_score(y_test, y_pred)     # (TP+TN)/总数
precision = precision_score(y_test, y_pred)     # TP/(TP+FP) 预测为正的靠谱率
recall    = recall_score(y_test, y_pred)        # TP/(TP+FN) 正类被找全率
f1        = f1_score(y_test, y_pred)            # 两者调和平均
```

### 2.3 指标选择决策——看业务场景

| 场景 | 核心指标 | 原因 |
|------|---------|------|
| 癌症筛查 | **Recall** | 漏诊致命，宁可误报不能漏 |
| 垃圾邮件 | **Precision** | 正常邮件被当垃圾代价高 |
| 欺诈检测 | **F1** | 平衡找到欺诈和误杀正常 |
| 类别均衡 | **Accuracy** | 正负样本差不多时 |

**黄金法则**：先问"假正和假负哪个代价更高"，再选指标。

### 2.4 ROC曲线与AUC

```python
y_prob_pos = model.predict_proba(X_test_s)[:, 1]
auc = roc_auc_score(y_test, y_prob_pos)
# AUC=1.0 完美, 0.5 随机猜, >0.8 不错
# 优势：不受阈值和类别比例影响
```

---

## 3. 决策树：可解释的分类器

```python
from sklearn.tree import DecisionTreeClassifier

tree = DecisionTreeClassifier(max_depth=3, random_state=42)
tree.fit(X_train_s, y_train)

# vs 逻辑回归
# 逻辑回归: 线性边界，需标准化，不易过拟合
# 决策树: 非线性边界，不需标准化，容易过拟合(需剪枝)
```

---

## ✅ 检查点

- [ ] 能解释Sigmoid函数如何把线性输出转为概率
- [ ] 理解Precision和Recall的本质区别
- [ ] 能根据业务场景选择正确的评估指标
- [ ] 理解混淆矩阵中TP/FP/FN/TN的含义
- [ ] 知道AUC指标的优势和适用场景
"""

# Phase 3 remaining chapters (16-23)
DEEPENED["第16章：集成学习 - Random Forest"] = """# 集成学习 - Random Forest

## 🎯 学习目标
- 理解集成学习的核心思想：三个臭皮匠顶个诸葛亮
- 掌握Bagging和Random Forest的原理与实战
- 知道什么时候用随机森林，以及它的优缺点

---

## 1. 集成学习的直觉

```
单个模型：可能过拟合或欠拟合
多个模型投票：个别模型的错误被多数纠正

就像问100个人同一个问题取多数答案 → 比问1个人可靠
```

## 2. Bagging：并行训练多个模型

```python
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier

# Bagging = Bootstrap Aggregating
# 每个模型用不同的随机子集训练，最后投票/平均
bagging = BaggingClassifier(
    estimator=DecisionTreeClassifier(),
    n_estimators=100,     # 100棵树
    max_samples=0.8,      # 每棵树用80%的数据
    random_state=42
)
bagging.fit(X_train, y_train)
```

## 3. Random Forest：Bagging + 随机特征选择

```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=100,     # 树的数量
    max_depth=10,         # 限制深度防过拟合
    min_samples_leaf=5,   # 叶节点最小样本数
    random_state=42,
    n_jobs=-1             # 并行训练
)
rf.fit(X_train, y_train)

# 特征重要性（RF的独特优势）
importances = pd.Series(rf.feature_importances_, index=feature_names)
print(importances.sort_values(ascending=False).head(5))

# OOB评估：无需划分验证集
rf_oob = RandomForestClassifier(oob_score=True, random_state=42)
rf_oob.fit(X_train, y_train)
print(f"OOB准确率: {rf_oob.oob_score_:.4f}")
```

## 4. 随机森林的优缺点

| 优点 | 缺点 |
|------|------|
| 不需要特征标准化 | 模型大，预测慢 |
| 能处理高维数据 | 不擅长外推(预测超出训练范围的值) |
| 内置特征重要性 | 对稀疏特征表现一般 |
| OOB自带验证 | 黑盒，可解释性不如单棵树 |

---

## ✅ 检查点

- [ ] 理解Bagging的核心思想
- [ ] 知道Random Forest比单棵Decision Tree好在哪里
- [ ] 能解释特征重要性的含义
- [ ] 知道RF的适用场景和局限性
"""

DEEPENED["第17章：XGBoost与LightGBM"] = """# XGBoost与LightGBM

## 🎯 学习目标
- 理解Boosting与Bagging的本质区别
- 掌握XGBoost/LightGBM的核心参数与调优
- 能在实战中选择正确的梯度提升框架

---

## 1. Boosting：串行纠错

```
Bagging: 每个模型独立训练，最后投票 (Random Forest)
Boosting: 每个模型重点学习前一个模型的错误 (XGBoost)

模型1 → 预测 → 找错 → 模型2重点学这些错 → 再找错 → 模型3...
```

## 2. XGBoost实战

```python
from xgboost import XGBClassifier

xgb = XGBClassifier(
    n_estimators=200,       # 树的数量
    max_depth=6,            # 树的深度
    learning_rate=0.1,      # 学习率(小=更保守)
    subsample=0.8,          # 行采样
    colsample_bytree=0.8,   # 列采样
    random_state=42
)
xgb.fit(X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False)

# 早停：验证集指标不再提升就停止
xgb.fit(X_train, y_train,
        eval_set=[(X_test, y_test)],
        early_stopping_rounds=10,
        verbose=False)
print(f"最佳迭代: {xgb.best_iteration}")
```

## 3. LightGBM：更快的XGBoost

```python
from lightgbm import LGBMClassifier

lgbm = LGBMClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    num_leaves=31,          # LGBM特有：叶节点数
    random_state=42
)
lgbm.fit(X_train, y_train,
         eval_set=[(X_test, y_test)],
         callbacks=[early_stopping(10)])
```

## 4. 选哪个？

| 维度 | Random Forest | XGBoost | LightGBM |
|------|-------------|---------|----------|
| 精度 | 好 | 更好 | 更好 |
| 训练速度 | 中 | 慢 | 快 |
| 调参难度 | 低 | 中 | 中 |
| 适用数据量 | 中小 | 中大 | 大 |

---

## ✅ 检查点

- [ ] 能解释Boosting和Bagging的区别
- [ ] 知道XGBoost的关键参数含义
- [ ] 会使用early_stopping防止过拟合
- [ ] 能根据数据特点选择RF/XGB/LGBM
"""

DEEPENED["第18章：模型评估与超参数调优"] = """# 模型评估与超参数调优

## 🎯 学习目标
- 掌握交叉验证的正确用法，避免评估偏差
- 学会用GridSearch/RandomSearch高效调参
- 理解偏差-方差权衡，判断模型是过拟合还是欠拟合

---

## 1. 交叉验证：比单次划分更可靠

```python
from sklearn.model_selection import cross_val_score, KFold

# 5折交叉验证：数据分成5份，轮流当测试集
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"CV准确率: {scores.mean():.4f} +/- {scores.std():.4f}")

# 为什么比单次train_test_split好？
# 单次划分可能"运气好"或"运气差"
# CV用5次评估的平均值，更稳定可靠
```

## 2. 超参数调优

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

# GridSearch: 穷举所有组合
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 10],
}
grid = GridSearchCV(RandomForestClassifier(), param_grid, cv=5, scoring='f1')
grid.fit(X, y)
print(f"最佳参数: {grid.best_params_}")
print(f"最佳分数: {grid.best_score_:.4f}")

# RandomizedSearch: 随机采样，更快
from scipy.stats import randint
param_dist = {
    'n_estimators': randint(50, 300),
    'max_depth': randint(3, 15),
}
random_search = RandomizedSearchCV(RandomForestClassifier(), param_dist,
    n_iter=20, cv=5, scoring='f1', random_state=42)
random_search.fit(X, y)
```

## 3. 偏差-方差权衡

```
高偏差(欠拟合): 训练分数低，测试分数低 → 模型太简单
高方差(过拟合): 训练分数高，测试分数低 → 模型太复杂

对策:
欠拟合 → 增加模型复杂度、增加特征、减少正则化
过拟合 → 减少模型复杂度、增加数据、增加正则化
```

---

## ✅ 检查点

- [ ] 理解为什么交叉验证比单次划分更可靠
- [ ] 会用GridSearchCV和RandomizedSearchCV调参
- [ ] 能根据训练/测试分数判断过拟合还是欠拟合
"""

DEEPENED["第19章：K-Means聚类与客户分群"] = """# K-Means聚类与客户分群

## 🎯 学习目标
- 理解K-Means算法原理与迭代过程
- 掌握选择K值的方法（肘部法则、轮廓系数）
- 能用聚类做客户分群等业务分析

---

## 1. K-Means原理

```
1. 随机选K个中心点
2. 每个样本分配到最近的中心 → 形成K个簇
3. 重新计算每个簇的中心（均值）
4. 重复2-3直到中心不再变化
```

```python
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(X)
print(f"簇中心: {kmeans.cluster_centers_}")
```

## 2. 选择K值

```python
import matplotlib.pyplot as plt

# 肘部法则：SSE随K增大而减小，选"拐点"
sse = []
for k in range(1, 11):
    km = KMeans(n_clusters=k, random_state=42)
    km.fit(X)
    sse.append(km.inertia_)  # SSE

# 轮廓系数：-1到1，越大越好
from sklearn.metrics import silhouette_score
for k in range(2, 11):
    labels = KMeans(n_clusters=k, random_state=42).fit_predict(X)
    score = silhouette_score(X, labels)
    print(f"K={k}: 轮廓系数={score:.4f}")
```

## 3. 实战：客户分群

```python
# RFM模型：Recency(最近消费), Frequency(消费频率), Monetary(消费金额)
rfm = pd.DataFrame({
    'recency': [...], 'frequency': [...], 'monetary': [...]
})

# 标准化后聚类
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm)

kmeans = KMeans(n_clusters=4, random_state=42)
rfm['segment'] = kmeans.fit_predict(rfm_scaled)

# 分析每个客群的特征
print(rfm.groupby('segment').mean())
```

---

## ✅ 检查点

- [ ] 能描述K-Means的迭代过程
- [ ] 知道如何选择合适的K值
- [ ] 能用聚类做客户分群分析
"""

DEEPENED["第20章：机器学习项目实战"] = """# 机器学习项目实战

## 🎯 学习目标
- 掌握ML项目的完整流程：从业务理解到模型部署
- 学会在实战中做特征工程、模型选择和结果分析
- 建立ML项目的检查清单思维

---

## 1. ML项目全流程

```
1. 业务理解 → 要解决什么问题？怎么定义成功？
2. 数据获取 → 数据从哪来？质量如何？
3. 探索性分析 → 数据长什么样？有什么规律？
4. 特征工程 → 哪些特征有用？需要什么变换？
5. 基线模型 → 用最简单的模型建立baseline
6. 模型优化 → 尝试更复杂的模型和调参
7. 结果分析 → 模型为什么对？为什么错？
8. 部署上线 → 模型如何持续服务？
```

## 2. 实战：客户流失预测

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score

# Step 1: 探索性分析
print(df.info())
print(df.describe())
print(df['churn'].value_counts(normalize=True))  # 类别分布

# Step 2: 特征工程
numeric_features = ['tenure', 'MonthlyCharges', 'TotalCharges']
categorical_features = ['Contract', 'PaymentMethod', 'InternetService']

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_features),
    ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features),
])

# Step 3: 建立baseline
baseline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000))
])
scores = cross_val_score(baseline, X, y, cv=5, scoring='roc_auc')
print(f"LogisticRegression AUC: {scores.mean():.4f}")

# Step 4: 模型对比
for name, clf in [('RF', RandomForestClassifier(n_estimators=100)),
                   ('GB', GradientBoostingClassifier(n_estimators=100))]:
    pipe = Pipeline([('preprocessor', preprocessor), ('classifier', clf)])
    scores = cross_val_score(pipe, X, y, cv=5, scoring='roc_auc')
    print(f"{name} AUC: {scores.mean():.4f}")
```

## 3. 项目检查清单

| 阶段 | 关键检查项 |
|------|----------|
| 数据 | 是否有泄露？类别是否均衡？缺失值处理？ |
| 特征 | 是否需要缩放？编码方式？是否构造了衍生特征？ |
| 模型 | 是否用了Pipeline？是否交叉验证？是否对比了多个模型？ |
| 部署 | 模型如何持久化？如何监控性能？如何处理数据漂移？ |

---

## ✅ 检查点

- [ ] 能按照完整流程执行一个ML项目
- [ ] 知道先建baseline再优化的重要性
- [ ] 建立了ML项目的检查清单思维
"""

DEEPENED["第21章：时间序列分析基础"] = """# 时间序列分析基础

## 🎯 学习目标
- 理解时间序列的核心组成：趋势、季节性、残差
- 掌握移动平均、指数平滑等基础预测方法
- 能用Prophet做业务级时间序列预测

---

## 1. 时间序列的分解

```python
import pandas as pd

# 时间序列 = 趋势 + 季节性 + 残差
# 趋势: 长期上升/下降方向
# 季节性: 周期性重复模式(如月度/季度)
# 残差: 去掉趋势和季节性后的随机波动

from statsmodels.tsa.seasonal import seasonal_decompose
result = seasonal_decompose(df['value'], model='additive', period=12)
result.plot()
```

## 2. 基础预测方法

```python
# 移动平均：用最近N个值的平均作为预测
df['MA_7'] = df['value'].rolling(window=7).mean()

# 指数平滑：越近的数据权重越大
from statsmodels.tsa.holtwinters import ExponentialSmoothing
model = ExponentialSmoothing(df['value'], trend='add', seasonal='add', seasonal_periods=12)
fitted = model.fit()
forecast = fitted.forecast(steps=30)
```

## 3. Prophet：业务友好的预测

```python
from prophet import Prophet

# Prophet自动处理趋势变化、季节性、节假日
df_prophet = df.reset_index().rename(columns={'date': 'ds', 'value': 'y'})
m = Prophet(yearly_seasonality=True)
m.fit(df_prophet)
future = m.make_future_dataframe(periods=90)
forecast = m.predict(future)
```

---

## ✅ 检查点

- [ ] 能分解时间序列的趋势、季节性、残差
- [ ] 知道移动平均和指数平滑的区别
- [ ] 会用Prophet做基础预测
"""

DEEPENED["第22章：ML工程化基础"] = """# ML工程化基础

## 🎯 学习目标
- 理解ML工程化的核心挑战：数据漂移、模型衰退、可复现性
- 掌握模型版本管理、实验追踪的基本方法
- 建立ML系统的监控意识

---

## 1. 为什么ML需要工程化？

```
Notebook里的模型 ≠ 生产可用的系统

常见问题:
- 模型上线后精度持续下降(数据漂移)
- 换个环境跑不出同样的结果(不可复现)
- 模型预测变慢影响用户体验(性能)
- 出了问题不知道回滚到哪个版本(版本管理)
```

## 2. 实验追踪

```python
import mlflow

mlflow.set_experiment("customer_churn")

with mlflow.start_run():
    # 记录参数
    mlflow.log_params({"n_estimators": 100, "max_depth": 5})
    
    # 训练模型
    model.fit(X_train, y_train)
    
    # 记录指标
    mlflow.log_metrics({"auc": roc_auc, "f1": f1})
    
    # 保存模型
    mlflow.sklearn.log_model(model, "model")
```

## 3. 模型监控要点

| 监控维度 | 指标 | 触发告警 |
|---------|------|---------|
| 预测性能 | AUC/F1持续下降 | 低于基线5% |
| 数据质量 | 特征分布变化 | KS检验p<0.05 |
| 系统性能 | 延迟P99 | 超过SLA |
| 业务指标 | 转化率/点击率 | 异常波动 |

---

## ✅ 检查点

- [ ] 理解ML系统需要工程化的原因
- [ ] 会用MLflow记录实验参数和指标
- [ ] 知道模型上线后需要监控什么
"""

DEEPENED["第23章：Phase 3 复习与总结"] = """# Phase 3 复习与总结

## 🎯 学习目标
- 梳理机器学习全流程的知识框架
- 建立从问题到模型的决策路径
- 为深度学习阶段打下基础

---

## 1. 知识框架回顾

```
机器学习全流程:
├── 问题定义 → 监督(分类/回归) vs 无监督(聚类/降维)
├── 数据准备 → 清洗、特征工程(缩放/编码/构造/选择)
├── 模型选择
│   ├── 线性模型 → 逻辑回归/Ridge/Lasso
│   ├── 树模型 → 决策树/随机森林/XGBoost
│   └── 聚类 → K-Means
├── 模型评估
│   ├── 分类 → Precision/Recall/F1/AUC
│   ├── 回归 → MSE/RMSE/MAE/R2
│   └── 交叉验证
└── 工程化 → Pipeline/实验追踪/监控
```

## 2. 模型选择速查

| 数据量 | 特点 | 首选模型 |
|-------|------|---------|
| 小(<1K) | 线性关系 | 逻辑回归/Ridge |
| 中(1K-100K) | 非线性 | 随机森林/XGBoost |
| 大(>100K) | 复杂 | XGBoost/LightGBM |
| 无标签 | 分群 | K-Means |

## 3. 从ML到DL的过渡

```
ML的局限:
- 特征工程是人工的 → 深度学习自动学特征
- 结构化数据为主 → 深度学习擅长图像/文本/语音
- 表达能力有限 → 深度神经网络可以拟合极复杂的函数

下一阶段预告:
Phase 4 将学习神经网络和PyTorch → 从"人工设计特征"到"自动学习特征"
```

---

## ✅ 检查点

- [ ] 能画出ML全流程的知识框架
- [ ] 能根据问题类型快速选择模型
- [ ] 理解ML到DL的演进逻辑
"""

# ============================================================
# Phase 4: 深度学习 (chapters 24-29)
# ============================================================

DEEPENED["第24章：神经网络基础与PyTorch入门"] = """# 神经网络基础与PyTorch入门

## 🎯 学习目标
- 理解神经网络的基本单元：感知器、激活函数、层
- 掌握PyTorch的核心概念：Tensor、autograd、nn.Module
- 能用PyTorch构建并训练第一个神经网络

---

## 1. 从线性回归到神经网络

```
线性回归: y = Wx + b
神经网络: y = activation(W2 * activation(W1 * x + b1) + b2)

关键差异:
1. 多层 → 可以学习非线性关系
2. 激活函数 → 引入非线性(没有激活函数，多层=一层)
3. 自动特征提取 → 不需要手动构造多项式特征
```

## 2. PyTorch核心概念

```python
import torch

# Tensor: 类似numpy数组，但支持GPU和自动求导
x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)

# 自动求导
y = (x ** 2).sum()
y.backward()
print(x.grad)  # dy/dx = 2x = [2, 4, 6]
```

## 3. 构建第一个神经网络

```python
import torch.nn as nn

class SimpleNet(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model = SimpleNet(8, 32, 1)

# 训练循环
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

for epoch in range(100):
    y_pred = model(X_train)
    loss = criterion(y_pred, y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if epoch % 20 == 0:
        print(f"Epoch {epoch}: loss={loss.item():.4f}")
```

---

## ✅ 检查点

- [ ] 理解激活函数为什么是神经网络的关键
- [ ] 会用PyTorch定义一个nn.Module
- [ ] 能写出完整的训练循环(forward→loss→backward→step)
"""

DEEPENED["第25章：MNIST手写字识别实战"] = """# MNIST手写字识别实战

## 🎯 学习目标
- 完成一个端到端的图像分类项目
- 掌握数据加载、模型训练、评估的完整流程
- 理解过拟合的表现与应对

---

## 1. 数据准备

```python
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=1000)
```

## 2. 构建分类网络

```python
class MNISTNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(784, 256),
            nn.ReLU(),
            nn.Dropout(0.2),    # 防过拟合
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 10)  # 10个数字
        )
    
    def forward(self, x):
        return self.net(x)

model = MNISTNet()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()
```

## 3. 训练与评估

```python
for epoch in range(10):
    model.train()
    for batch_x, batch_y in train_loader:
        loss = criterion(model(batch_x), batch_y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    # 评估
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            pred = model(batch_x).argmax(dim=1)
            correct += (pred == batch_y).sum().item()
            total += batch_y.size(0)
    print(f"Epoch {epoch}: 准确率={correct/total:.4f}")
```

---

## ✅ 检查点

- [ ] 能用DataLoader加载MNIST数据
- [ ] 理解Dropout如何防止过拟合
- [ ] 知道model.train()和model.eval()的区别
"""

DEEPENED["第26章：卷积神经网络CNN"] = """# 卷积神经网络CNN

## 🎯 学习目标
- 理解卷积操作的本质：局部感受野+参数共享
- 掌握CNN的核心组件：卷积层、池化层、全连接层
- 能用CNN处理图像分类任务

---

## 1. 为什么图像需要CNN？

```
全连接网络处理28x28图像: 输入784维 → 需要大量参数
CNN核心思想:
1. 局部感受野: 每个神经元只看一小块区域(如3x3)
2. 参数共享: 同一个滤波器扫过整张图 → 参数极少
3. 平移不变性: 猫在图片左边和右边都能识别
```

## 2. CNN核心组件

```python
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),  # 卷积: 1通道→32通道
            nn.ReLU(),
            nn.MaxPool2d(2),                  # 池化: 尺寸减半
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x
```

## 3. 关键超参数

| 参数 | 含义 | 典型值 |
|------|------|--------|
| in/out channels | 输入/输出通道数 | 1/32/64 |
| kernel_size | 卷积核大小 | 3, 5 |
| stride | 步长 | 1, 2 |
| padding | 填充 | 0, 1 |

---

## ✅ 检查点

- [ ] 理解卷积的局部感受野和参数共享
- [ ] 知道池化层的作用
- [ ] 能搭建一个基本的CNN模型
"""

DEEPENED["第27章：循环神经网络RNN与LSTM"] = """# 循环神经网络RNN与LSTM

## 🎯 学习目标
- 理解RNN处理序列数据的原理
- 掌握LSTM如何解决RNN的梯度消失问题
- 能用LSTM处理时间序列预测任务

---

## 1. RNN：有记忆的网络

```
普通网络: 每个输入独立处理
RNN: 当前输出依赖之前的隐状态 → 有"记忆"

h_t = tanh(W_x * x_t + W_h * h_{t-1} + b)
```

```python
class SimpleRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.rnn = nn.RNN(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        out, _ = self.rnn(x)
        return self.fc(out[:, -1, :])  # 取最后时刻的输出
```

## 2. LSTM：解决梯度消失

```
RNN问题: 长序列中梯度消失/爆炸 → 记不住很久之前的信息
LSTM解法: 三个门控机制
- 遗忘门: 决定忘掉哪些旧信息
- 输入门: 决定存入哪些新信息  
- 输出门: 决定输出哪些信息
```

```python
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                           batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])
```

---

## ✅ 检查点

- [ ] 理解RNN的隐状态如何传递信息
- [ ] 知道LSTM三个门控的作用
- [ ] 能用LSTM做时间序列预测
"""

DEEPENED["第28章：深度学习优化与部署"] = """# 深度学习优化与部署

## 🎯 学习目标
- 掌握训练优化的核心技巧：学习率调度、梯度裁剪、混合精度
- 理解模型部署的常见方案：ONNX、TorchServe
- 建立DL项目的工程化意识

---

## 1. 训练优化技巧

```python
# 学习率调度: 训练初期大步前进，后期精细调整
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

# 梯度裁剪: 防止梯度爆炸(RNN/LSTM常用)
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# 混合精度训练: FP16加速，节省显存
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    loss = criterion(model(x), y)
scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

## 2. 模型导出与部署

```python
# 导出ONNX格式(跨框架通用)
dummy_input = torch.randn(1, 1, 28, 28)
torch.onnx.export(model, dummy_input, "model.onnx")

# TorchServe部署
# 1. torch-model-archiver --model-name mnist --version 1.0 --model-file model.py --serialized-file model.pth
# 2. torchserve --start --model-store model_store --models mnist=mnist.mar
```

---

## ✅ 检查点

- [ ] 知道学习率调度的作用
- [ ] 理解混合精度训练的原理
- [ ] 了解模型部署的基本流程
"""

DEEPENED["第29章：Phase 4 复习与总结"] = """# Phase 4 复习与总结

## 🎯 学习目标
- 梳理深度学习的核心知识框架
- 理解不同网络架构的适用场景
- 为LLM阶段建立必要的知识基础

---

## 1. 深度学习知识框架

```
深度学习:
├── 基础 → Tensor/autograd/nn.Module/训练循环
├── 架构
│   ├── 全连接 → 表格数据分类
│   ├── CNN → 图像(局部特征+平移不变)
│   └── RNN/LSTM → 序列(时间依赖)
├── 优化 → 学习率调度/梯度裁剪/混合精度
└── 部署 → ONNX/TorchServe
```

## 2. 架构选择指南

| 数据类型 | 首选架构 | 原因 |
|---------|---------|------|
| 表格数据 | 全连接/树模型 | 特征独立，无需空间假设 |
| 图像 | CNN | 局部特征+参数共享 |
| 文本/时间序列 | LSTM/Transformer | 序列依赖关系 |

## 3. 从DL到LLM的桥梁

```
当前: 学习了CNN(视觉)和RNN(序列)
下一步: Transformer = "升级版RNN"，用注意力机制替代循环
  → 更好地处理长距离依赖
  → 并行计算更高效
  → 是GPT/BERT等大模型的基础架构
```

---

## ✅ 检查点

- [ ] 能根据数据类型选择合适的网络架构
- [ ] 理解CNN和RNN各自的设计动机
- [ ] 知道Transformer是下一阶段的核心
"""

# ============================================================
# Phase 5: LLM大模型 (chapters 30-33)
# ============================================================

DEEPENED["第30章：NLP基础与Word2Vec"] = """# NLP基础与Word2Vec

## 🎯 学习目标
- 理解词嵌入的核心思想：把词映射到语义空间
- 掌握Word2Vec的CBOW和Skip-gram模型
- 能用预训练词向量做文本相似度计算

---

## 1. 从One-Hot到词嵌入

```
One-Hot: "猫" = [0,0,1,0,...,0] → 高维稀疏，无法表达语义关系
Word2Vec: "猫" = [0.23, -0.15, 0.87, ...] → 低维稠密，语义相近的词向量相近

关键能力: vector("国王") - vector("男人") + vector("女人") ≈ vector("女王")
```

## 2. Word2Vec两种模型

```python
from gensim.models import Word2Vec

# Skip-gram: 给定中心词，预测上下文
model_sg = Word2Vec(sentences, vector_size=100, window=5, sg=1)

# CBOW: 给定上下文，预测中心词
model_cbow = Word2Vec(sentences, vector_size=100, window=5, sg=0)

# 语义相似度
print(model_sg.wv.most_similar('猫', topn=5))
print(model_sg.wv.similarity('猫', '狗'))
```

## 3. 预训练词向量

```python
import gensim.downloader as api
wv = api.load('word2vec-google-news-300')

# 词语类比
result = wv.most_similar(positive=['king', 'woman'], negative=['man'])
print(result)  # queen排在前面
```

---

## ✅ 检查点

- [ ] 理解词嵌入相比One-Hot的优势
- [ ] 知道Skip-gram和CBOW的区别
- [ ] 能用词向量做语义相似度计算
"""

DEEPENED["第31章：Transformer架构"] = """# Transformer架构

## 🎯 学习目标
- 理解自注意力机制：让模型关注输入中的重要部分
- 掌握Transformer的核心组件：多头注意力、位置编码、残差连接
- 理解为什么Transformer取代了RNN成为主流架构

---

## 1. 自注意力机制

```
核心问题: 处理序列时，如何让每个位置关注到相关位置？

注意力计算:
Q(查询) × K(键) → 注意力分数 → softmax → 加权V(值)

直觉: 每个词都在"问"其他词"你跟我有多相关？"，然后根据相关性加权聚合信息
```

```python
import torch
import torch.nn as nn
import math

class SelfAttention(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        Q, K, V = self.W_q(x), self.W_k(x), self.W_v(x)
        scores = Q @ K.transpose(-2, -1) / math.sqrt(x.size(-1))
        attn = torch.softmax(scores, dim=-1)
        return attn @ V
```

## 2. Transformer完整架构

```
输入 → 位置编码 → [多头注意力 + 残差+LayerNorm] × N
                 → [FFN + 残差+LayerNorm] × N → 输出

关键设计:
- 多头注意力: 多组Q/K/V并行计算，捕获不同类型的关系
- 位置编码: Transformer没有顺序概念，需要显式注入位置信息
- 残差连接: 缓解深层网络的梯度消失
```

## 3. Transformer vs RNN

| 维度 | RNN | Transformer |
|------|-----|-------------|
| 并行性 | 串行(必须逐个处理) | 完全并行 |
| 长距离依赖 | 差(梯度消失) | 好(注意力直连) |
| 计算复杂度 | O(n) | O(n^2) |
| 适合序列长度 | 短 | 长(但非常长时显存压力大) |

---

## ✅ 检查点

- [ ] 能用代码实现自注意力计算
- [ ] 理解Q/K/V的含义和注意力分数的计算
- [ ] 知道Transformer相比RNN的优势
"""

DEEPENED["第32章：BERT与GPT模型"] = """# BERT与GPT模型

## 🎯 学习目标
- 理解预训练+微调的范式
- 掌握BERT(双向编码)和GPT(单向生成)的核心区别
- 能用HuggingFace加载预训练模型做下游任务

---

## 1. 预训练+微调范式

```
传统: 从零训练模型 → 需要大量标注数据
预训练+微调:
  1. 在海量无标注文本上预训练(学语言知识)
  2. 在少量标注数据上微调(适应具体任务)

好处: 只需要少量标注数据就能获得好效果
```

## 2. BERT：双向理解

```
预训练任务: Masked Language Model(完形填空)
"我[MASK]欢机器学习" → 预测[MASK]="喜"

特点: 同时看左右上下文 → 适合理解类任务
典型任务: 文本分类、命名实体识别、问答
```

```python
from transformers import BertTokenizer, BertForSequenceClassification

tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=2)

inputs = tokenizer("这个产品很好用", return_tensors="pt")
outputs = model(**inputs)
pred = outputs.logits.argmax(dim=1)
```

## 3. GPT：单向生成

```
预训练任务: Next Token Prediction(预测下一个词)
"我喜欢机器" → 预测下一个="学习"

特点: 只看左侧上下文 → 适合生成类任务
典型任务: 文本生成、对话、代码补全
```

## 4. BERT vs GPT

| 维度 | BERT | GPT |
|------|------|-----|
| 注意力方向 | 双向 | 单向 |
| 预训练任务 | 完形填空 | 预测下一个词 |
| 擅长 | 理解(分类/抽取) | 生成(对话/写作) |
| 模型规模 | 百兆~十亿 | 十亿~万亿 |

---

## ✅ 检查点

- [ ] 理解预训练+微调范式的好处
- [ ] 知道BERT和GPT的核心区别
- [ ] 会用HuggingFace加载预训练模型
"""

DEEPENED["第33章：Prompt Engineering"] = """# Prompt Engineering

## 🎯 学习目标
- 掌握Prompt设计的核心原则与常用技巧
- 理解Few-shot、Chain-of-Thought等高级策略
- 能为实际业务场景设计有效的Prompt

---

## 1. Prompt设计原则

```
好的Prompt = 清晰的指令 + 具体的约束 + 示例

原则:
1. 明确角色: "你是一个资深的Python开发者"
2. 具体任务: "将以下Java代码改写为Python代码"
3. 输出格式: "请用JSON格式输出，包含name和age字段"
4. 约束条件: "不要使用任何第三方库"
```

## 2. 常用技巧

```python
# Zero-shot: 不给示例
"请判断以下评论的情感：这件商品太差了"

# Few-shot: 给几个示例
"""请判断评论的情感：
评论: 这个产品很好用 → 正面
评论: 质量太差了 → 负面
评论: 物流很快 → 正面
评论: 这件商品太差了 →"""

# Chain-of-Thought: 引导分步推理
"请一步步分析：如果公司有100个客户，20%流失，每个客户价值5000元，流失成本是多少？"
```

## 3. 高级策略

| 策略 | 方法 | 适用场景 |
|------|------|---------|
| Self-Consistency | 多次生成取多数 | 减少随机性 |
| ReAct | 推理+行动交替 | 需要调用工具 |
| 分解任务 | 大任务拆成小步骤 | 复杂问题 |

---

## ✅ 检查点

- [ ] 掌握Prompt设计的四个原则
- [ ] 知道Zero-shot/Few-shot/CoT的区别和用法
- [ ] 能为业务场景设计结构化的Prompt
"""

# ============================================================
# Phase 6: AI工程化 (chapters 34-36)
# ============================================================

DEEPENED["第34章：模型部署与服务化"] = """# 模型部署与服务化

## 🎯 学习目标
- 理解模型从Notebook到生产的关键差距
- 掌握模型服务化的常见架构：REST API、批处理、流式
- 能用FastAPI部署一个ML模型服务

---

## 1. 部署的三种模式

| 模式 | 延迟 | 吞吐量 | 典型场景 |
|------|------|--------|---------|
| 实时API | <100ms | 中 | 推荐、风控 |
| 批处理 | 分钟级 | 高 | 离线报表 |
| 流式 | 秒级 | 中 | 实时监控 |

## 2. FastAPI部署ML模型

```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')

class PredictRequest(BaseModel):
    features: list[float]

@app.post('/predict')
def predict(req: PredictRequest):
    X = scaler.transform(np.array([req.features]))
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0].tolist()
    return {'prediction': int(pred), 'probability': prob}

# 运行: uvicorn serve:app --host 0.0.0.0 --port 8000
```

## 3. 生产部署检查清单

| 检查项 | 说明 |
|-------|------|
| 模型版本管理 | 每次部署有版本号，可回滚 |
| 输入校验 | 防止非法输入导致崩溃 |
| 超时处理 | 预测超时返回默认值 |
| 健康检查 | /health端点监控服务状态 |
| 日志记录 | 记录每次预测的输入输出 |

---

## ✅ 检查点

- [ ] 知道三种部署模式的区别
- [ ] 能用FastAPI部署一个模型服务
- [ ] 理解生产部署的关键检查项
"""

DEEPENED["第35章：MLOps与监控"] = """# MLOps与监控

## 🎯 学习目标
- 理解MLOps的核心目标：让ML系统可靠、可复现、可持续
- 掌握数据漂移检测和模型衰退监控的方法
- 建立ML系统全生命周期的运维意识

---

## 1. MLOps成熟度

```
Level 0: 手动流程，无监控 → 大多数团队现状
Level 1: 自动训练Pipeline，有实验追踪
Level 2: CI/CD for ML，自动重训练，全面监控
```

## 2. 关键监控指标

```python
# 数据漂移检测: 训练数据 vs 在线数据的分布差异
from scipy.stats import ks_2samp

for feature in features:
    stat, p_value = ks_2samp(train_data[feature], online_data[feature])
    if p_value < 0.05:
        print(f"⚠️ {feature} 发生漂移! p={p_value:.4f}")

# 模型性能监控: 线上指标 vs 基线
if online_auc < baseline_auc * 0.95:
    alert("模型性能下降超过5%，建议重训练")
```

## 3. 自动重训练Pipeline

```
数据漂移/性能下降 → 触发重训练
→ 自动拉取最新数据 → 训练新模型
→ A/B测试对比 → 通过则替换，不通过则保留旧模型
```

| 监控维度 | 工具 | 告警阈值 |
|---------|------|---------|
| 数据质量 | Great Expectations | 缺失率>5% |
| 数据漂移 | Evidently AI | KS p<0.05 |
| 模型性能 | MLflow | 下降>5% |
| 系统延迟 | Prometheus | P99>500ms |

---

## ✅ 检查点

- [ ] 理解MLOps三级成熟度的区别
- [ ] 知道如何检测数据漂移
- [ ] 理解自动重训练Pipeline的逻辑
"""

DEEPENED["第36章：AI系统架构设计"] = """# AI系统架构设计

## 🎯 学习目标
- 理解AI系统的架构设计原则：可扩展、可观测、可回滚
- 掌握常见AI系统架构模式
- 能为实际业务设计端到端的AI系统

---

## 1. AI系统架构设计原则

```
1. 可扩展: 模型服务可水平扩展，特征计算可批/流切换
2. 可观测: 模型性能、数据质量、系统延迟全方位监控
3. 可回滚: 模型版本管理，A/B测试，灰度发布
4. 可复现: 数据版本+代码版本+模型版本三位一体
5. 容错降级: 模型故障时回退到规则系统
```

## 2. 常见架构模式

```
在线预测架构:
请求 → API网关 → 特征服务(取特征) → 模型服务(推理) → 后处理 → 响应
                    ↓                ↓
                特征缓存         模型版本管理

批处理架构:
数据源 → 特征Pipeline → 模型批量推理 → 结果存储 → 下游消费
            ↓
        Airflow调度

LLM应用架构:
用户请求 → Prompt构造 → LLM推理 → 输出解析 → 工具调用 → 响应
              ↓            ↓
          模板管理      多模型路由
```

## 3. 技术选型决策

| 组件 | 选项 | 选择依据 |
|------|------|---------|
| 模型服务 | Triton/TorchServe/自定义 | 模型类型和延迟要求 |
| 特征存储 | Feast/Redis/自研 | 实时性要求和数据规模 |
| 实验追踪 | MLflow/W&B | 团队规模和预算 |
| 编排调度 | Airflow/Prefect | 任务复杂度和依赖关系 |
| 监控 | Prometheus+Grafana | 已有基础设施 |

---

## ✅ 检查点

- [ ] 能说出AI系统架构的5个设计原则
- [ ] 理解在线预测和批处理架构的区别
- [ ] 知道如何为不同组件做技术选型
"""

# ============================================================
# Apply all deepened content to COURSES_DATA
# ============================================================

updated_count = 0
for course in COURSES_DATA:
    for chapter in course.get('chapters', []):
        title = chapter.get('title', '')
        if title in DEEPENED:
            chapter['content'] = DEEPENED[title]
            updated_count += 1

print(f"Updated {updated_count} chapters with deepened content")

# Verify lengths
for course in COURSES_DATA:
    for chapter in course.get('chapters', []):
        content_len = len(chapter.get('content', ''))
        if content_len < 3000:
            print(f"  ⚠️ {chapter['title'][:40]}: {content_len} chars (still short)")

# Now write back the file using repr() for safe string handling
output_lines = ['# Auto-generated course data with deepened content\n']
output_lines.append('COURSES_DATA = [\n')

for course in COURSES_DATA:
    output_lines.append('    {\n')
    for key in ['title', 'description', 'level', 'category', 'duration_hours', 'order_index']:
        val = course[key]
        if isinstance(val, str):
            output_lines.append(f'        {repr(key)}: {repr(val)},\n')
        else:
            output_lines.append(f'        {repr(key)}: {repr(val)},\n')
    
    is_published = course.get('is_published', True)
    output_lines.append(f'        "is_published": {is_published},\n')
    
    chapters = course.get('chapters', [])
    output_lines.append('        "chapters": [\n')
    
    for chapter in chapters:
        output_lines.append('            {\n')
        for key, val in chapter.items():
            if key == 'lab' and val is not None:
                output_lines.append('                "lab": {\n')
                for lk, lv in val.items():
                    if isinstance(lv, str):
                        output_lines.append(f'                    {repr(lk)}: {repr(lv)},\n')
                    elif isinstance(lv, list):
                        output_lines.append(f'                    {repr(lk)}: {repr(lv)},\n')
                    else:
                        output_lines.append(f'                    {repr(lk)}: {repr(lv)},\n')
                output_lines.append('                },\n')
            elif isinstance(val, str) and key == 'content':
                # Use repr for safe string handling (handles quotes, escapes, etc.)
                output_lines.append(f'                {repr(key)}: {repr(val)},\n')
            else:
                output_lines.append(f'                {repr(key)}: {repr(val)},\n')
        output_lines.append('            },\n')
    
    output_lines.append('        ],\n')
    output_lines.append('    },\n')

output_lines.append(']\n')

output_path = os.path.join(os.path.dirname(__file__), 'courses_extended_fixed.py')
with open(output_path, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"✅ Written to {output_path}")

# Verify the new file can be imported
import importlib
import app.data.courses_extended_fixed as cef
importlib.reload(cef)
print(f"✅ Verified: {len(cef.COURSES_DATA)} courses load successfully")
