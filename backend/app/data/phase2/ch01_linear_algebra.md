# Day 1 - 线性代数：不是矩阵运算，是空间变换

## 主题

如果你是从Java来的，你对"线性代数"的印象可能是——矩阵乘法、行列式计算、一堆数字的排列组合。但那是计算视角。

AI真正需要的是**几何视角**：线性代数描述的是空间变换。

理解了这个，你就理解了为什么PCA能降维、为什么神经网络用矩阵乘法、为什么特征值重要。

## 学习目标

- 用NumPy理解向量/矩阵的几何意义
- 理解矩阵乘法 = 空间变换（旋转、缩放、投影）
- 理解特征值/特征向量 = 变换的不变方向
- 理解为什么AI模型全是矩阵运算

---

## 1. 向量：不只是数字列表

### 你已经知道的

在Java里，`double[] v = {1.0, 2.0}` 就是一个数组。但在线性代数里，这个数组有**几何含义**——它是二维空间中的一个箭头，从原点指向坐标(1, 2)。

```python
import numpy as np

v = np.array([1, 2])  # 二维向量
print(f"长度(范数): {np.linalg.norm(v):.4f}")  # 2.2361
print(f"方向角: {np.degrees(np.arctan2(v[1], v[0])):.1f}°")  # 63.4°
```

### 为什么这很重要

AI模型中，**每个数据点都是一个向量**。一张28×28的灰度图是784维向量，一段文本的embedding是768维向量。理解向量就是在理解"数据长什么样"。

### 向量运算 = 空间中的操作

```python
a = np.array([1, 2])
b = np.array([3, 1])

# 加法：平行四边形法则
c = a + b  # [4, 3] — 从a的终点再走b的距离

# 数乘：缩放
d = 2 * a  # [2, 4] — 方向不变，长度翻倍

# 点积：一个向量在另一个向量上的投影
dot = np.dot(a, b)  # 5 = |a|×|b|×cos(θ)
```

**点积的直觉**：它衡量两个向量的"方向一致性"。点积为正 → 大致同向；为负 → 大致反向；为零 → 垂直。

这就是为什么**余弦相似度**（归一化的点积）能衡量文本相似性——两段文本的embedding向量方向越接近，语义越相似。

```python
def cosine_similarity(a, b):
    """这就是AI中最常用的相似度度量"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"相似度: {cosine_similarity(a, b):.4f}")  # 0.7071 — 大致同向
```

---

## 2. 矩阵：不是数字表格，是变换规则

### 关键认知跳跃

矩阵不是一堆数字的排列，而是**一个函数**——它把输入向量变换成输出向量。

```python
# 一个2×2矩阵
M = np.array([[2, 0],
              [0, 0.5]])

# "乘法"就是"应用变换"
v = np.array([1, 1])
result = M @ v  # [2, 0.5]

# 几何含义：x方向拉伸2倍，y方向压缩到0.5
```

这个矩阵M做了什么？它在x方向把空间拉宽了2倍，在y方向把空间压扁了一半。这就是"线性变换"——直线的还是直线，原点不动。

### 常见变换的矩阵

```python
# 旋转90度（逆时针）
rotate_90 = np.array([[0, -1],
                       [1, 0]])

# 水平翻转（镜像）
flip_h = np.array([[-1, 0],
                    [0, 1]])

# 投影到x轴（丢失y信息）
project_x = np.array([[1, 0],
                       [0, 0]])

# 验证
v = np.array([3, 4])
print(f"旋转后: {rotate_90 @ v}")     # [-4, 3]
print(f"翻转后: {flip_h @ v}")         # [-3, 4]
print(f"投影后: {project_x @ v}")      # [3, 0] — y信息丢失了
```

### 为什么AI全是矩阵运算

神经网络的一层就是 `output = W @ input + b`，其中W是权重矩阵，b是偏置向量。

**这个运算的几何含义**：W把输入向量变换到另一个空间，b平移了原点。每一层都在做空间变换，逐层把数据从"原始空间"映射到"分类空间"。

```python
# 一个简单的2→3→2神经网络层
W1 = np.random.randn(3, 2)  # 2维→3维，升维
W2 = np.random.randn(2, 3)  # 3维→2维，降维

x = np.array([0.5, -0.3])   # 输入
h = W1 @ x                   # 隐藏层：2维空间映射到3维
y = W2 @ h                   # 输出：3维映射回2维

print(f"输入维度: {x.shape}, 隐藏维度: {h.shape}, 输出维度: {y.shape}")
```

---

## 3. 特征值与特征向量：变换中的不变量

### 直觉

大部分向量在矩阵变换后会改变方向。但有些特殊向量，变换后方向不变（只缩放），这些就是**特征向量**，缩放的比例就是**特征值**。

```python
# 一个剪切变换矩阵
S = np.array([[1, 1],
              [0, 1]])

eigenvalues, eigenvectors = np.linalg.eig(S)
print(f"特征值: {eigenvalues}")        # [1, 1]
print(f"特征向量: {eigenvectors.T}")   # [[1, 0], [-1, 1]] (近似)

# 验证：特征向量变换后方向不变
ev = eigenvectors[:, 0]
transformed = S @ ev
print(f"原向量: {ev}")
print(f"变换后: {transformed}")
print(f"比值(特征值): {transformed[0]/ev[0]:.4f}")
```

### 为什么这在AI中重要

1. **PCA降维**：找方差最大的方向（最大特征值对应的特征向量），投影到这些方向上——用更少维度保留最多信息
2. **PageRank**：Google网页排名本质是求转移矩阵的最大特征向量
3. **谱聚类**：用图的特征向量做聚类

```python
# PCA的直觉：用特征值找最重要的方向
np.random.seed(42)
data = np.random.randn(100, 2) @ np.array([[3, 0], [0, 0.5]])  # x方向方差大，y方向方差小

cov_matrix = np.cov(data.T)  # 协方差矩阵
eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

print(f"特征值: {eigenvalues}")
print(f"最大特征值占比: {eigenvalues[0]/eigenvalues.sum():.2%}")
# 最大特征值对应的方向就是数据"展开最宽"的方向——降维就保留这个方向
```

---

## 4. 矩阵分解：拆解变换

### 你已经知道的类比

在Java里，复杂的操作可以拆成简单步骤。矩阵也一样——复杂变换可以拆成简单变换的复合。

### SVD（奇异值分解）——最重要的矩阵分解

任何矩阵A都可以分解为 `A = U × Σ × V^T`，其中：
- U：左奇异向量（输出空间的基）
- Σ：奇异值（每个维度的"重要性"）
- V^T：右奇异向量（输入空间的基）

```python
# 用SVD理解图像压缩
np.random.seed(42)
A = np.random.randn(10, 6)  # 一个10×6的矩阵

U, S, Vt = np.linalg.svd(A, full_matrices=False)
print(f"U: {U.shape}, S: {S.shape}, Vt: {Vt.shape}")
print(f"奇异值: {S.round(2)}")
print(f"前2个奇异值占比: {S[:2].sum()/S.sum():.2%}")

# 用前k个奇异值重建（有损压缩）
k = 2
A_reconstructed = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
print(f"重建误差: {np.linalg.norm(A - A_reconstructed):.4f}")
```

### SVD在AI中的应用

| 应用 | 怎么用 |
|------|--------|
| **LSA（潜在语义分析）** | 对词-文档矩阵做SVD，找语义主题 |
| **推荐系统** | 对用户-物品评分矩阵做SVD，补全缺失值 |
| **模型压缩** | 对神经网络权重矩阵做SVD，用低秩近似减少参数量 |
| **PCA** | PCA本质就是对去中心化数据做SVD |

---

## 5. 实战：用线性代数理解AI预处理

```python
# 场景：你有一组数据，要喂给ML模型
data = np.random.randn(100, 5)  # 100个样本，5个特征

# 标准化（Z-score）— 线性变换
mean = data.mean(axis=0)
std = data.std(axis=0)
data_normalized = (data - mean) / std

# 白化（Whitening）— 用协方差矩阵做更彻底的变换
cov = np.cov(data.T)
U, S, Vt = np.linalg.svd(cov)
# 白化变换：让数据各维度不相关且方差为1
whitening_matrix = U @ np.diag(1.0 / np.sqrt(S)) @ Vt
data_whitened = data @ whitening_matrix

print(f"原始协方差对角线: {np.diag(cov).round(2)}")
print(f"白化后协方差对角线: {np.diag(np.cov(data_whitened.T)).round(2)}")  # 全是1
```

---

## 本节关键收获

| 概念 | 计算视角（不要停留在这） | 几何视角（你要记住的） |
|------|------------------------|----------------------|
| 向量 | 数字列表 | 空间中的箭头 |
| 矩阵 | 数字表格 | 空间变换函数 |
| 矩阵乘法 | 行乘列 | 变换的复合 |
| 特征值 | 方程的根 | 变换中不变的缩放比例 |
| SVD | 矩阵分解 | 把变换拆成旋转-缩放-旋转 |

## 下一节预告

概率论不是公式背诵——它是不确定性的语言。AI模型的核心问题就是"如何在不确定中做决策"，而概率论提供了这套语言。
