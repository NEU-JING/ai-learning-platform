# Day 7 - 高维空间：维数灾难与特征工程

## 主题

人类能直观理解3维空间，但AI数据动辄几百上千维。高维空间有反直觉的性质——数据稀疏、距离失效、过拟合加剧。

理解维数灾难，你就理解了为什么需要降维、特征选择和正则化。

## 学习目标

- 理解高维空间的反直觉性质
- 理解维数灾难的3种表现
- 理解PCA降维的数学本质
- 理解特征工程 = 用人类先验压缩维度

---

## 1. 高维空间的反直觉

### 体积集中在角落

```python
import numpy as np

# 在d维单位超立方体中，内切超球的体积随维度急剧缩小
from scipy.special import gamma

def hypersphere_volume(d, r=1.0):
    """d维超球的体积"""
    return np.pi**(d/2) / gamma(d/2 + 1) * r**d

for d in [2, 3, 5, 10, 20, 50]:
    v = hypersphere_volume(d)
    cube_v = 2**d  # 超立方体体积
    ratio = v / cube_v if cube_v > 0 else 0
    print(f"d={d:2d}: 超球体积={v:.6f}, 占立方体比例={ratio:.2e}")
# d=50时，超球体积≈0——几乎所有体积都在角落！
```

### 距离趋于相同

```python
np.random.seed(42)
for d in [2, 10, 100, 1000]:
    points = np.random.uniform(0, 1, size=(100, d))
    
    # 计算所有点对之间的距离
    from scipy.spatial.distance import pdist
    dists = pdist(points)
    
    print(f"d={d:4d}: 均值={dists.mean():.4f}, 标准差={dists.std():.4f}, CV={dists.std()/dists.mean():.4f}")
# 高维时，所有点之间的距离几乎相同 → 距离度量失效
```

**对AI的影响**：KNN、聚类等基于距离的算法在高维空间性能急剧下降。

---

## 2. 维数灾难的3种表现

### 表现1：数据稀疏

```python
# 要在d维空间中获得与1维中100个点相同密度的采样
# 每个维度需要n^(1/d)个点

for d in [1, 2, 5, 10, 20]:
    n_per_dim = 100 ** (1.0 / d)
    total = n_per_dim ** d
    print(f"d={d:2d}: 每维需要{n_per_dim:.1f}个点, 总共需要{total:.0f}个样本")
# d=10: 每维1.58个点，但总共还是要100个
# d=20: 每维1.26个点——几乎每个维度只有1-2个取值
```

### 表现2：过拟合加剧

```python
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

np.random.seed(42)

for d in [2, 5, 10, 20, 50]:
    n = 200
    X = np.random.randn(n, d)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)  # 只依赖前2个特征
    
    knn = KNeighborsClassifier(n_neighbors=5)
    scores = cross_val_score(knn, X, y, cv=5)
    print(f"d={d:2d}: KNN准确率={scores.mean():.4f}±{scores.std():.4f}")
# 无用维度增加 → 准确率下降
```

### 表现3：计算成本爆炸

```python
# 矩阵运算的复杂度
for d in [100, 1000, 10000]:
    # X^T X: O(n × d²)
    ops = 1000 * d * d
    print(f"d={d:5d}: X^TX运算量={ops:.2e}")
```

---

## 3. PCA降维：用线性代数压缩维度

### PCA的数学本质

PCA = 在数据方差最大的方向上投影 = 对协方差矩阵做特征分解

```python
np.random.seed(42)
n = 500

# 生成相关数据：大部分方差在某个方向上
angle = np.pi / 4
rotation = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle),  np.cos(angle)]])
data = np.random.randn(n, 2) @ np.diag([3, 0.5]) @ rotation.T

# PCA
mean = data.mean(axis=0)
centered = data - mean
cov = np.cov(centered.T)

eigenvalues, eigenvectors = np.linalg.eig(cov)
# 排序
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

print(f"特征值: {eigenvalues.round(3)}")
print(f"方差解释比: {(eigenvalues / eigenvalues.sum()).round(3)}")
print(f"第1主成分方向: {eigenvectors[:, 0].round(3)}")

# 投影到第1主成分（1维）
projected = centered @ eigenvectors[:, :1]
print(f"原始维度: 2, 降维后: 1")
print(f"保留方差: {eigenvalues[0]/eigenvalues.sum():.2%}")
```

### 高维PCA实战

```python
from sklearn.decomposition import PCA
from sklearn.datasets import load_digits

digits = load_digits()
X, y = digits.data, digits.target  # 64维（8×8像素）

pca = PCA(n_components=0.95)  # 保留95%方差
X_pca = pca.fit_transform(X)

print(f"原始维度: {X.shape[1]}")
print(f"降维后: {X_pca.shape[1]}")
print(f"各成分方差解释比: {pca.explained_variance_ratio_[:5].round(3)}")
print(f"累计方差: {pca.explained_variance_ratio_.sum():.2%}")
```

---

## 4. 特特征工程：用人类先验压缩维度

### 为什么特征工程仍然重要

```python
# 原始特征：交易金额、交易时间、交易地点
# 衍生特征：近1小时交易次数、日均交易金额、异地交易比例

# 例子：用特征工程替代高维原始数据
np.random.seed(42)
n = 1000

# 原始数据：7天的每小时点击量 = 168维
raw_clicks = np.random.poisson(5, size=(n, 168))

# 特征工程：提取有意义的统计量
features = np.column_stack([
    raw_clicks.mean(axis=1),      # 日均点击
    raw_clicks.std(axis=1),       # 点击波动
    raw_clicks[:, :24].sum(axis=1),  # 第1天总点击
    raw_clicks[:, -24:].sum(axis=1), # 最后1天总点击
    (raw_clicks > 0).sum(axis=1) / 168,  # 活跃时段比例
])

print(f"原始维度: {raw_clicks.shape[1]}")
print(f"工程后维度: {features.shape[1]}")
print(f"压缩比: {features.shape[1]/raw_clicks.shape[1]:.2%}")
```

### 常见特征工程技巧

| 技巧 | 场景 | Python |
|------|------|--------|
| 对数变换 | 右偏分布 | `np.log1p(x)` |
| 标准化 | 不同量纲 | `(x - mean) / std` |
| 分箱 | 非线性关系 | `pd.cut(x, bins)` |
| 交叉特征 | 特征交互 | `x1 * x2` |
| 时间特征 | 时间序列 | 星期几、小时、是否节假日 |
| 文本特征 | NLP | TF-IDF、embedding |

---

## 本节关键收获

| 概念 | 直觉 | AI中的角色 |
|------|------|-----------|
| 维数灾难 | 维度↑→数据稀疏→过拟合 | 理解为什么需要降维 |
| 距离失效 | 高维中所有点"一样远" | KNN/聚类在高维效果差 |
| PCA | 找方差最大的方向投影 | 最常用的降维方法 |
| 特征工程 | 用人类知识压缩维度 | 在数据和模型之间的桥梁 |
| 特征选择 | 去掉无用维度 | L1正则化、树模型特征重要性 |

## 下一节预告

实验2：手写梯度下降与正则化对比——亲眼看到L1/L2如何影响模型参数。
