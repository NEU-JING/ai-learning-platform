# Pandas入门: 从SQL到DataFrame

## 学习目标
- 将SQL查询思维迁移到Pandas操作
- 掌握DataFrame的CRUD操作
- 理解Series、Index、GroupBy核心概念

---

## 1. DataFrame = 内存中的数据库表

如果你会用SQL, 你就会用Pandas——几乎每个SQL操作都有对应的Pandas方法。

```python
import pandas as pd

# 创建DataFrame(类似CREATE TABLE + INSERT)
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'department': ['Engineering', 'Sales', 'Engineering', 'Sales', 'Engineering'],
    'salary': [12000, 9000, 15000, 8500, 11000],
    'age': [28, 35, 42, 26, 31],
    'performance': [4.5, 3.2, 4.8, 3.5, 4.1]
})

df.head()           # SELECT * FROM df LIMIT 5
df.shape            # (5, 5) -- 5行5列
df.dtypes           # 每列的数据类型
df.describe()       # 数值列的统计摘要
```

### SQL -> Pandas 对照表

| SQL | Pandas |
|-----|--------|
| `SELECT * FROM t` | `df` |
| `SELECT col1, col2 FROM t` | `df[['col1', 'col2']]` |
| `WHERE col = val` | `df[df['col'] == val]` |
| `WHERE col > val` | `df[df['col'] > val]` |
| `ORDER BY col DESC` | `df.sort_values('col', ascending=False)` |
| `GROUP BY col` | `df.groupby('col')` |
| `LIMIT 10` | `df.head(10)` |
| `COUNT(*)` | `df.shape[0]` 或 `len(df)` |
| `JOIN` | `pd.merge()` |

---

## 2. 数据选择与过滤

### 2.1 列选择

```python
# 单列(返回Series)
df['name']

# 多列(返回DataFrame)
df[['name', 'salary']]

# 用属性访问(列名必须是合法Python标识符)
df.salary              # 等价于 df['salary']
```

### 2.2 行过滤(WHERE)

```python
# 单条件
df[df['salary'] > 10000]

# 多条件(& = AND, | = OR, 注意括号!)
df[(df['salary'] > 10000) & (df['department'] == 'Engineering')]

# isin(SQL的IN)
df[df['department'].isin(['Engineering', 'Sales'])]

# 字符串包含(SQL的LIKE)
df[df['name'].str.contains('li')]

# 空值过滤
df[df['salary'].notna()]
```

### 2.3 loc vs iloc

```python
# loc: 按标签选择(行名+列名)
df.loc[0, 'name']                    # 第0行name列
df.loc[0:2, ['name', 'salary']]     # 第0到2行(包含2!)
df.loc[df['salary'] > 10000, 'name'] # 条件选择

# iloc: 按位置选择(纯整数索引)
df.iloc[0, 0]                        # 第0行第0列
df.iloc[0:2, :]                      # 第0到1行(不含2! 和Python切片一致)
df.iloc[[0, 2, 4], [0, 2]]           # 指定行和列
```

**常见坑**: `loc`的切片包含右端点, `iloc`不包含——这是初学者最常犯的错。

---

## 3. 数据操作

### 3.1 新增列(ALTER TABLE ADD COLUMN)

```python
# 直接赋值
df['bonus'] = df['salary'] * 0.1

# 条件赋值(SQL的CASE WHEN)
import numpy as np
df['level'] = np.where(df['salary'] > 12000, 'Senior', 'Junior')

# 多条件
conditions = [
    df['performance'] >= 4.5,
    df['performance'] >= 3.5,
]
choices = ['Excellent', 'Good']
df['rating'] = np.select(conditions, choices, default='Average')
```

### 3.2 修改数据(UPDATE)

```python
# 按条件修改
df.loc[df['name'] == 'Alice', 'salary'] = 13000

# 整列运算
df['salary'] = df['salary'] * 1.1    # 涨薪10%
```

### 3.3 删除(DELETE)

```python
# 删除列
df = df.drop('bonus', axis=1)
df = df.drop(columns=['bonus', 'level'])

# 删除行
df = df.drop(0)                       # 删除第0行
df = df[df['name'] != 'Bob']          # 按条件删除
```

---

## 4. 聚合与分组(GROUP BY)

```python
# 基础分组
df.groupby('department')['salary'].mean()
# Engineering    12666.67
# Sales           8750.00

# 多个聚合函数
df.groupby('department')['salary'].agg(['mean', 'median', 'count', 'std'])

# 多列聚合
df.groupby('department').agg({
    'salary': ['mean', 'max'],
    'performance': 'mean',
    'name': 'count'
})

# 分组后排序
df.groupby('department')['salary'].mean().sort_values(ascending=False)
```

---

## 5. 合并(JOIN)

```python
# 创建第二个表
departments = pd.DataFrame({
    'department': ['Engineering', 'Sales', 'HR'],
    'manager': ['张工', '李总', '王主任'],
    'budget': [500000, 300000, 200000]
})

# INNER JOIN
pd.merge(df, departments, on='department', how='inner')

# LEFT JOIN
pd.merge(df, departments, on='department', how='left')

# 列名不同时
pd.merge(df, departments, left_on='dept', right_on='department', how='inner')
```

---

## 6. 读写数据

```python
# CSV(最常用)
df.to_csv('output.csv', index=False, encoding='utf-8')
df = pd.read_csv('data.csv', encoding='utf-8')

# Excel
df.to_excel('output.xlsx', sheet_name='Sheet1')
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# SQL(需要sqlalchemy)
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@host/db')
df.to_sql('employees', engine, if_exists='replace', index=False)
df = pd.read_sql('SELECT * FROM employees WHERE salary > 10000', engine)

# JSON
df.to_json('output.json', orient='records', force_ascii=False)
df = pd.read_json('data.json')
```

---

## 练习题

1. 用Pandas实现: 按部门分组, 找出每个部门薪资最高的员工(类似SQL的ROW_NUMBER)
2. 给定两个DataFrame——订单表和客户表, 用merge找出"消费总额Top10的客户"
3. 读取一个CSV文件, 处理缺失值(填充均值或删除), 计算每列的统计信息
