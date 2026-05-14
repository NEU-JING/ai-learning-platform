# Day 6 - 信息论与正则化：为什么简单模型更可靠

## 主题

奥卡姆剃刀：如无必要，勿增实体。但为什么简单模型更可靠？信息论给出了精确的数学回答。

## 学习目标

- 理解KL散度 = 两个分布的"距离"
- 理解交叉熵损失 = AI最常用的损失函数的信息论本质
- 理解L1/L2正则化的概率解释
- 理解为什么"简单"是数学上的要求，不是审美偏好

---

## 1. 信息论回顾：熵与信息量

```python
import numpy as np

def entropy(p):
    """香农熵——不确定性的度量"""
    p = np.array(p)
    p = p[p > 0]
    return -np.sum(p * np.log2(p))

# 熵越高 = 不确定性越大 = 需要更多信息描述
print(f"确定性: {entropy([1.0]):.2f} bits")      # 0 — 没有不确定性
print(f"公平硬币: {entropy([0.5, 0.5]):.2f} bits")  # 1 — 1 bit不确定性
print(f"4面骰子: {entropy([0.25]*4):.2f} bits")    # 2 — 2 bits
print(f"8面骰子: {entropy([0.125]*8):.2f} bits")   # 3 — 3 bits
```

### 最短编码定理

熵 = 描述一个事件平均需要的最少bit数。

```python
# 英文字母的熵
letter_probs = [0.08, 0.02, 0.03, 0.04, 0.13, 0.02, 0.02, 0.06,
                0.07, 0.01, 0.01, 0.04, 0.03, 0.07, 0.08, 0.02,
                0.01, 0.06, 0.06, 0.09, 0.03, 0.01, 0.02, 0.001, 0.02, 0.001]
print(f"英文字母的熵: {entropy(letter_probs):.2f} bits")
# ≈4.2 bits，意味着平均用4.2bit就能编码一个字母（而非5bit的等长编码）
```

---

## 2. KL散度：两个分布的"距离"

### 定义

$$D_{KL}(P \| Q) = \sum_x P(x) \log \frac{P(x)}{Q(x)}$$

**直觉**：用Q分布的编码去描述P分布的数据，平均多用多少bit。

```python
def kl_divergence(p, q):
    """KL散度：P相对于Q的"额外信息量" """
    p, q = np.array(p), np.array(q)
    mask = (p > 0) & (q > 0)
    return np.sum(p[mask] * np.log(p[mask] / q[mask]))

# 例子：真实分布P vs 模型预测Q
p_true = [0.4, 0.3, 0.2, 0.1]  # 真实分布

# 好的模型预测
q_good = [0.38, 0.32, 0.18, 0.12]
# 差的模型预测
q_bad = [0.1, 0.1, 0.1, 0.7]

print(f"KL(P||Q_good) = {kl_divergence(p_true, q_good):.4f}")
print(f"KL(P||Q_bad)  = {kl_divergence(p_true, q_bad):.4f}")
# 好模型的KL散度小→预测接近真实分布
```

### KL散度不是真正的距离

- 非对称：KL(P||Q) ≠ KL(Q||P)
- 不满足三角不等式
- 最小值=0（当且仅当P=Q）

---

## 3. 交叉熵损失：AI最常用的损失函数

### 交叉熵 = 熵 + KL散度

$$H(P, Q) = H(P) + D_{KL}(P \| Q)$$

当P是固定的（真实标签），最小化交叉熵 = 最小化KL散度 = 让Q接近P。

```python
def cross_entropy(p, q):
    """交叉熵"""
    p, q = np.array(p), np.log(np.array(q) + 1e-10)
    mask = p > 0
    return -np.sum(p[mask] * q[mask])

# 二分类交叉熵（逻辑回归的损失函数）
def binary_cross_entropy(y_true, y_pred):
    """BCE = -[y·log(p) + (1-y)·log(1-p)]"""
    eps = 1e-10
    return -(y_true * np.log(y_pred + eps) + (1 - y_true) * np.log(1 - y_pred + eps))

# 例子：预测"是否垃圾邮件"
y_true = 1  # 真实标签：是垃圾邮件
for y_pred in [0.9, 0.7, 0.5, 0.3, 0.1]:
    loss = binary_cross_entropy(y_true, y_pred)
    print(f"预测={y_pred:.1f}: 损失={loss:.4f}")
# 预测越准→损失越低
```

### 多分类交叉熵

```python
# 三分类问题
true_label = 1  # 类别1
predictions = [
    [0.1, 0.8, 0.1],  # 好预测：类别1概率0.8
    [0.3, 0.4, 0.3],  # 中等预测
    [0.6, 0.2, 0.2],  # 差预测：猜错了
]

for pred in predictions:
    loss = -np.log(pred[true_label] + 1e-10)
    print(f"预测={pred}, 交叉熵损失={loss:.4f}")
```

---

## 4. 正则化：信息论视角

### 过拟合 = 编码了噪声

```python
np.random.seed(42)
n = 20
x = np.random.uniform(0, 2*np.pi, n)
y_true = np.sin(x)
y = y_true + np.random.normal(0, 0.3, n)  # 加噪声

from numpy.linalg import lstsq

# 多项式拟合
for degree in [1, 3, 15]:
    X = np.column_stack([x**k for k in range(degree + 1)])
    w, _, _, _ = lstsq(X, y, rcond=None)
    
    train_mse = np.mean((X @ w - y) ** 2)
    
    # 在新数据上测试
    x_test = np.random.uniform(0, 2*np.pi, 100)
    y_test = np.sin(x_test)
    X_test = np.column_stack([x_test**k for k in range(degree + 1)])
    test_mse = np.mean((X_test @ w - y_test) ** 2)
    
    print(f"度数={degree:2d}: 训练MSE={train_mse:.4f}, 测试MSE={test_mse:.4f}")
```

### L2正则化的概率解释 = 高斯先验

```python
# L2正则化：loss = MSE + λ·||w||²
# 等价于假设 w ~ N(0, σ²)，即权重的先验分布是高斯的
# λ = σ²(噪声方差) / σ²(先验方差)

def ridge_regression(X, y, alpha=1.0):
    """L2正则化的最小二乘 = 岭回归"""
    n_features = X.shape[1]
    w = np.linalg.solve(X.T @ X + alpha * np.eye(n_features), X.T @ y)
    return w

# 对比：无正则化 vs L2正则化
X_poly = np.column_stack([x**k for k in range(16)])  # 15次多项式
w_noreg = lstsq(X_poly, y, rcond=None)[0]
w_ridge = ridge_regression(X_poly, y, alpha=0.1)

print(f"无正则化权重大小: {np.sum(w_noreg**2):.2f}")
print(f"L2正则化权重大小: {np.sum(w_ridge**2):.2f}")
# 正则化强制权重更小 → 模型更简单 → 泛化更好
```

### L1正则化的概率解释 = 拉普拉斯先验

```python
# L1正则化：loss = MSE + λ·||w||₁
# 等价于假设 w ~ Laplace(0, b)，即权重的先验集中在0附近
# L1使权重稀疏（很多变成0）→ 自动特征选择

from scipy.optimize import minimize

def lasso_loss(w, X, y, alpha):
    """L1正则化损失"""
    residual = X @ w - y
    return np.sum(residual**2) + alpha * np.sum(np.abs(w))

result = minimize(lasso_loss, np.zeros(16), args=(X_poly, y, 0.5), method='L-BFGS-B')
w_lasso = result.x
print(f"L1零权重数: {np.sum(np.abs(w_lasso) < 0.01)}/16")
print(f"L1非零权重: {np.where(np.abs(w_lasso) >= 0.01)[0].tolist()}")
```

---

## 5. MDL原则：最小描述长度

### 核心思想

最好的模型 = 最短地描述数据的模型。

总描述长度 = 描述模型的长度 + 描述残差的长度

```python
# 模型复杂度 vs 拟合误差的权衡
# 复杂模型：拟合误差小但模型本身需要更多bit描述
# 简单模型：模型描述短但拟合误差大

def mdl_score(train_mse, n_params, n_samples):
    """简化的MDL分数（越低越好）"""
    data_cost = n_samples * np.log2(train_mse + 1e-10)  # 编码残差的代价
    model_cost = n_params * 32  # 假设每个参数32bit
    return data_cost + model_cost

for degree in [1, 3, 5, 10, 15]:
    X = np.column_stack([x**k for k in range(degree + 1)])
    w, _, _, _ = lstsq(X, y, rcond=None)
    mse = np.mean((X @ w - y) ** 2)
    mdl = mdl_score(mse, degree + 1, n)
    print(f"度数={degree:2d}: MSE={mse:.4f}, 参数={degree+1}, MDL={mdl:.1f}")
```

---

## 本节关键收获

| 概念 | 信息论含义 | AI中的角色 |
|------|-----------|-----------|
| 熵 | 不确定性/最短编码 | 分类损失的基准 |
| KL散度 | 两个分布的"距离" | VAE、策略优化 |
| 交叉熵 | 熵+KL散度 | 分类问题的损失函数 |
| L2正则化 | 高斯先验 | 防过拟合，权重衰减 |
| L1正则化 | 拉普拉斯先验 | 稀疏性，特征选择 |
| MDL | 最短描述 | 模型选择的理论基础 |

## 下一节预告

高维空间：维数灾难与特征工程——为什么100维的数据比10维的难处理得多。
