# Day 2 - 数据预处理：垃圾进垃圾出的防线

## 为什么数据预处理占ML项目60%的时间

如果你做过数据仓库ETL，你理解"数据清洗占80%时间"这句话。ML的数据预处理是ETL的加强版——不仅要清洗，还要让数据变成模型能理解的格式。

一个真实的统计：Kaggle调查中，数据科学家平均花费60%的时间在数据预处理上。

```
数据获取(10%) → 数据清洗(30%) → 特征工程(20%) → 建模(15%) → 部署(25%)
```

## 缺失值：ML的第一个敌人

### 缺失值的类型

不是所有缺失值都是一样的。理解缺失类型决定处理策略：

**完全随机缺失（MCAR）**：缺失概率与任何变量无关
- 例：传感器偶发性故障
- 处理：删除或插补都可以

**随机缺失（MAR）**：缺失概率与其他观测到的变量有关
- 例：男性更可能不填"收入"字段
- 处理：用其他特征做条件插补

**非随机缺失（MNAR）**：缺失概率与自身未观测值有关
- 例：低收入者更可能不填收入
- 处理：最棘手，可能需要领域知识建模

### 处理策略

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'age': [25, 30, np.nan, 45, 50],
    'income': [50000, np.nan, np.nan, 80000, 90000],
    'gender': ['M', 'F', 'M', np.nan, 'F'],
    'purchased': [1, 0, 1, 1, 0]
})

# 策略1：删除——最简单但最浪费
df_drop = df.dropna()                    # 删除任何有缺失的行
df_drop_cols = df.dropna(axis=1)         # 删除有缺失的列
df_drop_thresh = df.dropna(thresh=3)     # 至少3个非缺失值才保留

# 策略2：常数填充——快速但粗暴
df_fill = df.fillna(0)                   # 数值填0
df_fill_dict = df.fillna({'gender': 'Unknown'})  # 指定列填特定值

# 策略3：统计量填充——最常用
df_median = df['age'].fillna(df['age'].median())  # 中位数（比均值抗异常值）
df_mode = df['gender'].fillna(df['gender'].mode()[0])  # 众数

# 策略4：前向/后向填充——时序数据专用
df_ffill = df.fillna(method='ffill')    # 用前一个非缺失值填充
df_bfill = df.fillna(method='bfill')    # 用后一个非缺失值填充

# 策略5：插值——时序数据更精细
df_interp = df.interpolate(method='linear')  # 线性插值

# 策略6：模型预测填充——最精确但最复杂
from sklearn.ensemble import RandomForestRegressor
# 用其他特征预测缺失值（需要注意不要用标签！）
```

### 选择策略的决策树

```
缺失比例 < 5%？
  ├─ 是 → 删除行（影响小）
  └─ 否 → 缺失类型？
       ├─ MCAR → 均值/中位数填充
       ├─ MAR  → 条件填充（按其他特征分组计算统计量）
       └─ MNAR → 加缺失指示列 + 领域特定填充
```

**关键技巧**：不管用什么填充策略，**加一列缺失指示变量**：

```python
df['age_missing'] = df['age'].isnull().astype(int)
df['age'] = df['age'].fillna(df['age'].median())
# 模型可以学到"年龄缺失"本身是有信息量的！
```

## 异常值：数据的叛逆者

### 识别异常值

**IQR法（箱线图法）**：

```python
Q1 = df['income'].quantile(0.25)
Q3 = df['income'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
outliers = df[(df['income'] < lower) | (df['income'] > upper)]
```

**Z-Score法**：

```python
from scipy import stats
z_scores = np.abs(stats.zscore(df['income']))
outliers = df[z_scores > 3]  # 超过3个标准差
```

**Isolation Forest**：高维数据异常检测

```python
from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.05, random_state=42)
outlier_labels = iso.fit_predict(df[['age', 'income']])
# -1 = 异常, 1 = 正常
```

### 处理异常值

| 策略 | 适用场景 | 风险 |
|------|----------|------|
| 删除 | 明确的错误数据 | 可能丢失有价值的极端案例 |
| 截断（Winsorize） | 保留但限制影响 | 改变了分布 |
| 对数变换 | 右偏分布（收入、价格） | 不能处理0和负值 |
| 分箱 | 有业务含义的区间 | 丢失精度 |
| 保留 | 异常值本身有意义 | 需要鲁棒模型 |

**重要**：异常值不一定是错误！欺诈检测中，异常值就是你要找的目标。

## 类别变量编码：让模型理解"文字"

ML模型只能处理数值。但真实数据充满了类别变量（性别、城市、产品类型）。

### 编码方法对比

**Label Encoding**：每个类别映射为一个整数

```python
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['gender_encoded'] = le.fit_transform(df['gender'])
# M → 1, F → 0
```

⚠️ 问题：模型会认为1 > 0，暗示有序关系。性别没有序，但城市代码1和城市代码2也没有序。

**One-Hot Encoding**：每个类别变成一个二进制列

```python
pd.get_dummies(df['city'], prefix='city')
# city_beijing  city_shanghai  city_guangzhou
#      1              0              0
#      0              1              0
```

⚠️ 问题：高基数类别（如城市名有100个）会产生100列——维度爆炸。

**Target Encoding**：用目标变量的均值替代类别

```python
city_target_mean = df.groupby('city')['purchased'].mean()
df['city_encoded'] = df['city'].map(city_target_mean)
# Beijing: 0.3 → 北京用户的购买率30%
```

⚠️ 问题：容易过拟合！需要交叉验证编码。

### 选择决策

```
类别基数(cardinality)
├─ ≤ 10   → One-Hot Encoding
├─ 10-100 → One-Hot 或 Target Encoding
└─ > 100  → Target Encoding 或 Hash Encoding
     （注意：Target Encoding 必须用交叉验证防止过拟合）
```

## 数据不平衡：当99%的样本是负样本

### 现实中的不平衡

| 场景 | 正样本比例 | 影响 |
|------|-----------|------|
| 欺诈检测 | 0.1% | 99.9%准确率毫无意义 |
| 疾病诊断 | 1% | 漏诊代价极高 |
| 广告点击 | 2% | 大量负样本淹没信号 |
| 设备故障 | 0.5% | 故障样本太少学不到模式 |

### 为什么准确率是骗子

```python
# 一个永远预测"正常"的欺诈检测模型
y_pred = np.zeros(len(y_test))  # 全部预测为0（正常）
accuracy = accuracy_score(y_test, y_pred)  # 99.9%！
# 但它一个欺诈都没抓到。
```

### 处理策略

**重采样**：

```python
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

# 过采样：生成少数类样本
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# 欠采样：减少多数类样本
undersample = RandomUnderSampler(random_state=42)
X_resampled, y_resampled = undersample.fit_resample(X_train, y_train)
```

**类别权重**：不用改变数据，改模型损失函数

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(class_weight='balanced')
# 自动按类别比例调整权重
# 或者手动指定
model = LogisticRegression(class_weight={0: 1, 1: 100})
```

**选择策略**：

| 方法 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 过采样(SMOTE) | 不丢信息 | 可能生成噪声样本 | 中等数据量 |
| 欠采样 | 简单快速 | 丢失多数类信息 | 大数据量 |
| 类别权重 | 不改数据 | 不是所有模型支持 | 首选方案 |
| 异常检测范式 | 天然适合极低比例 | 需要不同评估框架 | <1%正样本 |

## 数据预处理Pipeline：防止泄露的关键

### 错误的做法

```python
# ❌ 逐步处理，容易泄露
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df)  # 用了全部数据
X_train, X_test = train_test_split(df_scaled)
```

### 正确的做法：用sklearn Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# 定义数值列和类别列
numeric_features = ['age', 'income']
categorical_features = ['gender', 'city']

# 列级预处理
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ]
)

# 完整Pipeline
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression())
])

# 训练：所有fit只在训练集上
pipeline.fit(X_train, y_train)

# 预测：自动用训练集的参数transform
y_pred = pipeline.predict(X_test)
```

Pipeline的魔力：
1. **防止数据泄露**：fit只在训练集上调用
2. **代码简洁**：一行代码完成预处理+建模
3. **可序列化**：保存pipeline = 保存整个工作流
4. **可交叉验证**：交叉验证时预处理在每个fold内独立进行

## 实战：预处理一个真实数据集

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# 加载Titanic数据集
df = pd.read_csv('titanic.csv')
print(f"原始数据: {df.shape}")
print(f"缺失值:\n{df.isnull().sum()}")

# 步骤1：问题建模
# 目标：预测乘客是否生还（二分类）
# 特征：age, sex, pclass, fare, embarked

# 步骤2：特征选择（基于领域知识，不是相关性）
features = ['age', 'sex', 'pclass', 'fare', 'embarked']
target = 'survived'
X = df[features]
y = df[target]

# 步骤3：数据切分
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 步骤4：预处理Pipeline
numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer([
    ('num', numeric_transformer, ['age', 'fare']),
    ('cat', categorical_transformer, ['sex', 'embarked'])
])

# 步骤5：完整Pipeline
full_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(random_state=42))
])

# 步骤6：训练和评估
full_pipeline.fit(X_train, y_train)
score = full_pipeline.score(X_test, y_test)
print(f"Test accuracy: {score:.3f}")
```

## 今日要点

1. **缺失值处理的第一步是理解缺失类型**（MCAR/MAR/MNAR），而不是急着填充。
2. **异常值不一定是错误**——先判断是噪声还是信号。
3. **类别编码选择取决于基数**：低基数→One-Hot，高基数→Target Encoding。
4. **数据不平衡时准确率是骗子**，用F1/precision-recall AUC。
5. **Pipeline是防止数据泄露的最佳工具**——所有预处理操作必须包在Pipeline里。

> 下一步：Day 3我们将进入特征工程——从原始数据中提炼模型能理解的信号，这是ML工程师的"手艺活"。
