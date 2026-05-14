# Pandas高级: 数据清洗与特征工程

## 学习目标
- 掌握缺失值处理、重复值清洗、数据类型转换
- 学会时间序列处理、透视表、窗口函数
- 为后续ML课程奠定特征工程基础

---

## 1. 缺失值处理

### 1.1 检测缺失值

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'name': ['Alice', 'Bob', None, 'Diana'],
    'age': [25, np.nan, 35, 28],
    'salary': [12000, 9000, np.nan, np.nan],
    'join_date': ['2024-01-15', None, '2024-03-01', '2024-02-20']
})

# 检测
df.isnull()                  # 布尔矩阵
df.isnull().sum()            # 每列缺失数
df.isnull().sum() / len(df)  # 缺失比例
```

### 1.2 处理策略

```python
# 策略1: 删除(缺失比例低时适用)
df.dropna()                          # 删除任何含缺失值的行
df.dropna(subset=['salary'])         # 只看salary列
df.dropna(thresh=3)                  # 至少3个非缺失值才保留

# 策略2: 填充
df['age'].fillna(df['age'].mean())           # 均值填充
df['salary'].fillna(df['salary'].median())   # 中位数填充(更抗异常值)
df['name'].fillna('Unknown')                 # 常数填充

# 策略3: 前向/后向填充(时间序列常用)
df['salary'].ffill()               # 用前一个非缺失值填充
df['salary'].bfill()               # 用后一个非缺失值填充

# 策略4: 插值
df['age'].interpolate()              # 线性插值
df['age'].interpolate(method='cubic')  # 三次样条插值
```

**选择原则**:
- 缺失 < 5%: 删除或填充
- 缺失 5-30%: 填充(均值/中位数/插值)
- 缺失 > 30%: 考虑删除该列或作为特征保留(缺失本身可能是信号)

---

## 2. 数据类型转换

```python
# 字符串转日期
df['join_date'] = pd.to_datetime(df['join_date'], errors='coerce')
# errors='coerce': 无法解析的变为NaT(而不是报错)

# 日期提取
df['join_year'] = df['join_date'].dt.year
df['join_month'] = df['join_date'].dt.month
df['join_quarter'] = df['join_date'].dt.quarter
df['day_of_week'] = df['join_date'].dt.day_name()

# 数值类型优化(减少内存)
df['age'] = df['age'].astype('int8')       # -128到127足够存年龄
df['salary'] = df['salary'].astype('float32')  # 32位浮点通常够用

# category类型(低基数字符串列)
df['department'] = df['department'].astype('category')
# 内存从每行存完整字符串 -> 存整数编码+映射表
```

---

## 3. 重复值与异常值

### 3.1 重复值

```python
# 检测
df.duplicated()                    # 每行是否是重复行
df.duplicated().sum()              # 重复行数
df.duplicated(subset=['email'])    # 按列检测

# 处理
df = df.drop_duplicates()
df = df.drop_duplicates(subset=['email'], keep='last')  # 保留最后一条
```

### 3.2 异常值

```python
# 方法1: Z-Score(假设正态分布)
from scipy import stats
z_scores = stats.zscore(df['salary'])
df_clean = df[np.abs(z_scores) < 3]     # 保留3sigma内的数据

# 方法2: IQR(不假设分布)
Q1 = df['salary'].quantile(0.25)
Q3 = df['salary'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
df_clean = df[(df['salary'] >= lower) & (df['salary'] <= upper)]

# 方法3: 分位数截断
lower = df['salary'].quantile(0.01)
upper = df['salary'].quantile(0.99)
df['salary'] = df['salary'].clip(lower, upper)   # 截断而非删除
```

---

## 4. 透视表与交叉表

### 4.1 pivot_table(SQL没有直接对应)

```python
sales = pd.DataFrame({
    'region': ['East', 'East', 'West', 'West', 'East', 'West'],
    'product': ['A', 'B', 'A', 'B', 'A', 'A'],
    'quarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q2', 'Q2'],
    'revenue': [100, 200, 150, 180, 120, 160]
})

# 按地区和产品汇总季度收入
pivot = sales.pivot_table(
    values='revenue',
    index='region',
    columns='product',
    aggfunc='sum',
    fill_value=0
)
# product    A    B
# region
# East     220  200
# West     310  180
```

### 4.2 交叉表(频次统计)

```python
pd.crosstab(df['department'], df['level'], margins=True)
# margins=True 添加行/列合计
```

---

## 5. 窗口函数(SQL窗口函数的Pandas版)

```python
# 排名
df['salary_rank'] = df.groupby('department')['salary'].rank(ascending=False)

# 移动平均
df['salary_ma3'] = df['salary'].rolling(window=3).mean()

# 累计求和
df['cumulative'] = df['salary'].cumsum()

# 滞后/领先
df['prev_salary'] = df.groupby('name')['salary'].shift(1)   # LAG
df['next_salary'] = df.groupby('name')['salary'].shift(-1)  # LEAD

# 组内百分比
df['pct_in_dept'] = df.groupby('department')['salary'].transform(
    lambda x: x / x.sum()
)
```

---

## 6. 特征工程预览

为后续ML课程铺垫, 这里介绍最常见的特征变换:

```python
# 数值特征标准化
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
df[['salary_scaled', 'age_scaled']] = scaler.fit_transform(df[['salary', 'age']])

# 类别特征编码
df['dept_code'] = df['department'].map({'Engineering': 0, 'Sales': 1})  # Label编码
df = pd.get_dummies(df, columns=['department'])                         # One-Hot编码

# 数值分箱
df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 50, 100],
                          labels=['Young', 'Mid', 'Senior', 'Elder'])
df['salary_quartile'] = pd.qcut(df['salary'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

# 交叉特征
df['salary_per_year'] = df['salary'] / (df['age'] - 22)  # 每工作年薪水
```

---

## 练习题

1. 给定一个含缺失值的数据集, 实现一个函数`smart_fillna(df)`: 数值列用中位数填充, 类别列用众数填充, 日期列用前向填充
2. 用pivot_table实现"每月各部门的销售额Top3员工"
3. 用窗口函数计算每个员工的薪资在其部门内的百分位排名
