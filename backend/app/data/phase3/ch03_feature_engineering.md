# Day 3 - 特征工程：从原始数据到模型输入

## 特征工程是什么？为什么它仍然重要

在深度学习时代，有一种说法："特征工程已死，深度学习自动学特征"。这个说法半对半错：

- **对的部分**：图像、语音、自然语言等领域，深度学习确实取代了手工特征
- **错的部分**：结构化数据（表格、日志、交易记录）领域，特征工程仍然是关键

你工作中的数据——交易记录、用户行为、风控指标——大多是结构化数据。在这些场景中，好的特征工程可以让简单模型超越没有特征工程的复杂模型。

```
好的特征 + 简单模型 > 差的特征 + 复杂模型
```

类比：你用精炼的SQL查询+合适的索引，比用全文检索引擎搜结构化数据快得多。

## 特征工程的三层思维

### 第一层：基础变换——让数据变成模型能吃的格式

**数值特征标准化**：

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

# StandardScaler: z = (x - mean) / std —— 默认选择
# MinMaxScaler:   z = (x - min) / (max - min) —— 神经网络常用
# RobustScaler:   z = (x - median) / IQR —— 有异常值时更稳定

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
```

**什么时候用哪个**？

| 场景 | 推荐 | 原因 |
|------|------|------|
| 特征近似正态分布 | StandardScaler | 标准化后均值0方差1 |
| 特征范围已知 | MinMaxScaler | 映射到[0,1] |
| 有明显异常值 | RobustScaler | 用中位数和IQR，不受异常值影响 |
| 树模型（RF/XGBoost） | 不需要标准化 | 树模型对单调变换不敏感 |

**对数变换**：处理右偏分布

```python
import numpy as np

# 收入、价格、点击量等通常是右偏分布
df['income_log'] = np.log1p(df['income'])  # log1p = log(1+x)，处理0值
# 变换前：均值被极端值拉高
# 变换后：分布更接近正态，模型更容易学
```

### 第二层：特征构造——从领域知识中提炼信号

这是特征工程最体现功力的部分。

**时间特征提取**：

```python
df['transaction_time'] = pd.to_datetime(df['transaction_time'])

# 基础提取
df['hour'] = df['transaction_time'].dt.hour
df['day_of_week'] = df['transaction_time'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

# 业务特征
df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)
df['is_business_hour'] = ((df['hour'] >= 9) & (df['hour'] <= 17)).astype(int)

# 比原始时间戳有用得多——欺诈交易更多在深夜
```

**聚合特征**：从"行"到"实体"

```python
# 每个用户的交易统计
user_stats = df.groupby('user_id').agg(
    tx_count=('amount', 'count'),          # 交易次数
    tx_mean=('amount', 'mean'),            # 平均金额
    tx_std=('amount', 'std'),              # 金额波动
    tx_max=('amount', 'max'),              # 最大单笔
    tx_night_ratio=('is_night', 'mean'),   # 夜间交易比例
    unique_merchants=('merchant_id', 'nunique')  # 商户多样性
).reset_index()
```

**交叉特征**：1+1 > 2

```python
# 单独的年龄和收入都有信息量，但"年龄-收入比"更有信息量
df['income_per_age'] = df['income'] / df['age']

# 单独的价格和面积有意义，但"单价"更有意义
df['price_per_sqm'] = df['price'] / df['area']

# 类别交叉
df['city_income_tier'] = df['city'] + '_' + df['income_tier']
```

**滑窗特征**：时序数据的核心

```python
# 过去7天交易统计
df = df.sort_values(['user_id', 'transaction_time'])
df['amount_7d_mean'] = df.groupby('user_id')['amount'].rolling(7, min_periods=1).mean().values
df['amount_7d_std'] = df.groupby('user_id')['amount'].rolling(7, min_periods=1).std().values
df['tx_count_7d'] = df.groupby('user_id')['amount'].rolling(7, min_periods=1).count().values
```

### 第三层：特征选择——从噪声中分离信号

**为什么需要特征选择**？

- 维数灾难：特征太多、样本太少 → 模型过拟合
- 训练速度：减少无用特征 → 训练更快
- 可解释性：特征越少 → 越容易解释

**方法1：过滤法——统计检验**

```python
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif

# 方差分析（ANOVA F-value）
selector = SelectKBest(f_classif, k=10)
X_selected = selector.fit_transform(X_train, y_train)

# 互信息（捕获非线性关系）
selector = SelectKBest(mutual_info_classif, k=10)
X_selected = selector.fit_transform(X_train, y_train)

# 查看选中的特征
selected_features = X_train.columns[selector.get_support()].tolist()
```

**方法2：包裹法——递归特征消除**

```python
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier

estimator = RandomForestClassifier(n_estimators=50, random_state=42)
selector = RFE(estimator, n_features_to_select=10)
X_selected = selector.fit_transform(X_train, y_train)

# 特征排名
rankings = pd.Series(selector.ranking_, index=X_train.columns).sort_values()
```

**方法3：嵌入法——模型自带特征选择**

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 特征重要性
importances = pd.Series(model.feature_importances_, index=X_train.columns)
importances.sort_values(ascending=False).head(10)

# L1正则化（Lasso）自动将不重要特征的系数压为0
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(penalty='l1', solver='saga', C=0.1)
model.fit(X_train, y_train)
# 系数非0的特征就是被选中的
```

### 选择策略

```
特征数 < 50  → 用嵌入法（特征重要性），简单直接
特征数 50-500 → 过滤法初筛 + 嵌入法精选
特征数 > 500  → 过滤法快速降维 + 递归特征消除
              （注意：包裹法计算量大，高维时慎用）
```

## 特征工程的常见陷阱

### 陷阱1：用测试集信息做特征选择

```python
# ❌ 全量数据做特征选择
selector.fit(X_all, y_all)  # 测试集信息泄露到特征选择中

# ✅ 只用训练集
selector.fit(X_train, y_train)
X_test_selected = selector.transform(X_test)  # 只用transform
```

### 陷阱2：过度特征工程

```python
# ❌ 暴力组合所有特征
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=3, interaction_only=True)
# 10个原始特征 → 120个组合特征 → 大部分是噪声
```

好的特征工程是**有领域知识驱动的**，不是暴力组合。

### 陷阱3：忽略特征分布变化

训练时的特征分布 ≠ 预测时的特征分布（Concept Drift / Covariate Shift）

```python
# 监控特征分布变化
from scipy import stats

def check_distribution_shift(X_train, X_new, feature_name, threshold=0.05):
    """KS检验：检测特征分布是否发生显著变化"""
    statistic, p_value = stats.ks_2samp(
        X_train[feature_name], X_new[feature_name]
    )
    if p_value < threshold:
        print(f"⚠️ {feature_name} 分布已变化! p={p_value:.4f}")
    return p_value
```

## 特征工程的系统化方法

### 特征清单模板

| 特征名 | 类型 | 来源 | 构造逻辑 | 业务含义 |
|--------|------|------|----------|----------|
| age | 数值 | 原始 | 直接使用 | 用户年龄 |
| income_log | 数值 | 原始 | log1p变换 | 对数收入 |
| tx_7d_count | 数值 | 聚合 | 7日滑窗计数 | 近期活跃度 |
| is_night | 二值 | 派生 | hour∈[22,5] | 夜间交易标志 |
| city_income | 类别 | 交叉 | city×income_tier | 城市-收入等级 |

### 特征质量评估

```python
def evaluate_feature(df, feature_name, target_name):
    """评估单个特征的预测力"""
    from sklearn.metrics import roc_auc_score
    
    # 1. 缺失率
    missing_rate = df[feature_name].isnull().mean()
    
    # 2. 唯一值比例（太低=常数特征，太高=ID特征）
    unique_ratio = df[feature_name].nunique() / len(df)
    
    # 3. 与目标的单变量AUC
    if df[feature_name].dtype in ['float64', 'int64']:
        valid = df[[feature_name, target_name]].dropna()
        auc = roc_auc_score(valid[target_name], valid[feature_name])
    else:
        auc = None
    
    return {
        'feature': feature_name,
        'missing_rate': f'{missing_rate:.2%}',
        'unique_ratio': f'{unique_ratio:.2%}',
        'univariate_auc': f'{auc:.3f}' if auc else 'N/A'
    }
```

## 实战：为信用评分构造特征

```python
# 原始数据：贷款申请表
df = pd.read_csv('loan_applications.csv')

# === 第一层：基础变换 ===
df['income_log'] = np.log1p(df['annual_income'])
df['loan_to_income'] = df['loan_amount'] / df['annual_income']
df['rate_diff'] = df['interest_rate'] - df['market_rate']  # 利差

# === 第二层：特征构造 ===
# 时间特征
df['application_hour'] = pd.to_datetime(df['application_time']).dt.hour
df['is_business_day'] = pd.to_datetime(df['application_time']).dt.dayofweek < 5

# 聚合特征（借款人历史）
borrower_stats = df.groupby('borrower_id').agg(
    prev_loan_count=('loan_id', 'count'),
    prev_default_rate=('is_default', 'mean'),
    avg_loan_amount=('loan_amount', 'mean'),
    max_overdue_days=('overdue_days', 'max')
).reset_index()
df = df.merge(borrower_stats, on='borrower_id', how='left')

# 交叉特征
df['risk_tier'] = df['credit_score'].apply(
    lambda x: 'high' if x > 700 else 'medium' if x > 600 else 'low'
)
df['loan_purpose_risk'] = df['loan_purpose'] + '_' + df['risk_tier']

# === 第三层：特征选择 ===
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Top 15 特征
top_features = pd.Series(
    model.feature_importances_, index=X_train.columns
).nlargest(15).index.tolist()

print(f"最终特征集: {top_features}")
```

## 今日要点

1. **特征工程三层**：基础变换（格式化）→ 特征构造（提炼信号）→ 特征选择（去噪）
2. **领域知识是特征工程的核心**——最有价值的特征往往来自对业务的理解，不是暴力组合
3. **聚合特征是结构化数据的杀手锏**——把行级数据变成实体级特征
4. **特征选择必须在训练集上做**，否则数据泄露
5. **监控特征分布变化**——训练时和预测时分布不同是生产环境最常见的故障

> 下一步：实验1，你将把这些知识整合成一个端到端的ML Pipeline。
