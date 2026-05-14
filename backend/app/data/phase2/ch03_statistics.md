# Day 3 - 统计推断：从样本到结论的桥梁

## 主题

你永远无法获得所有数据——不可能调查所有用户，不可能看到所有可能的图片。统计推断就是从有限样本推断整体规律的数学框架。

AI模型本质上在做统计推断：用训练集（样本）推断真实数据分布（整体）。

## 学习目标

- 理解点估计与区间估计的区别
- 理解假设检验的逻辑（不是证明，是排除）
- 理解p值的真实含义（以及为什么被滥用）
- 理解最大似然估计 = AI模型训练的数学基础

---

## 1. 点估计：用样本猜总体

### 问题

你有一个网站的1000个用户停留时间样本，想推断所有用户的平均停留时间。

```python
import numpy as np

np.random.seed(42)
# 真实总体（你不知道）
true_mean = 5.0
true_std = 2.0
population = np.random.normal(true_mean, true_std, size=100000)

# 你只有100个样本
sample = np.random.choice(population, size=100, replace=False)

# 点估计：用样本均值估计总体均值
sample_mean = sample.mean()
sample_std = sample.std()

print(f"真实均值: {true_mean:.2f}")
print(f"样本均值: {sample_mean:.2f} (估计)")
print(f"误差: {abs(sample_mean - true_mean):.2f}")
```

### 点估计的问题

点估计给出了一个数字，但没告诉你**有多确定**。样本均值5.2，但真实值可能是4.8或5.6——你不知道。

---

## 2. 置信区间：给估计加误差棒

### 核心公式

$$\text{CI} = \bar{x} \pm z \times \frac{s}{\sqrt{n}}$$

- x̄：样本均值
- z：置信水平对应的z值（95%置信 → z=1.96）
- s：样本标准差
- n：样本量

### 直觉

置信区间的宽度取决于三个因素：

```python
from scipy import stats

def confidence_interval(data, confidence=0.95):
    """计算均值的置信区间"""
    n = len(data)
    mean = np.mean(data)
    se = stats.sem(data)  # 标准误 = s/√n
    h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean - h, mean + h

# 样本量越大 → 区间越窄
for n in [30, 100, 1000]:
    sample = np.random.choice(population, size=n, replace=False)
    lo, hi = confidence_interval(sample)
    width = hi - lo
    print(f"n={n:4d}: 均值={sample.mean():.2f}, 95%CI=[{lo:.2f}, {hi:.2f}], 宽度={width:.2f}")

# 输出示例：
# n=  30: 均值=5.12, 95%CI=[4.38, 5.86], 宽度=1.48
# n= 100: 均值=5.02, 95%CI=[4.66, 5.38], 宽度=0.72
# n=1000: 均值=5.01, 95%CI=[4.89, 5.13], 宽度=0.24
```

**核心洞察**：样本量翻4倍，区间宽度减半（因为 √n）。这就是为什么AI需要大量数据——不是"越多越好"，而是样本量决定估计精度。

---

## 3. 假设检验：不是证明，是排除

### 逻辑框架

```
1. 提出零假设 H₀："没有效果"（A/B测试中：新版本没有提升）
2. 提出备择假设 H₁："有效果"（新版本有提升）
3. 计算p值：在H₀为真的前提下，观察到当前或更极端结果的概率
4. 如果p < α（通常0.05），拒绝H₀
```

**关键理解**：p值不是"H₀为假的概率"，而是"如果H₀为真，看到这个结果的概率"。

```python
# A/B测试：新按钮颜色是否提高点击率
np.random.seed(42)

# A组（对照组）：1000次展示，120次点击
n_a, clicks_a = 1000, 120
rate_a = clicks_a / n_a

# B组（实验组）：1000次展示，145次点击
n_b, clicks_b = 1000, 145
rate_b = clicks_b / n_b

print(f"A组点击率: {rate_a:.2%}")
print(f"B组点击率: {rate_b:.2%}")
print(f"提升: {(rate_b - rate_a) / rate_a:.2%}")

# Z检验
pooled_rate = (clicks_a + clicks_b) / (n_a + n_b)
se = np.sqrt(pooled_rate * (1 - pooled_rate) * (1/n_a + 1/n_b))
z = (rate_b - rate_a) / se
p_value = 1 - stats.norm.cdf(z)

print(f"Z统计量: {z:.3f}")
print(f"p值: {p_value:.4f}")
print(f"结论: {'显著' if p_value < 0.05 else '不显著'} (α=0.05)")
```

### p值的滥用

| 错误理解 | 正确理解 |
|---------|---------|
| p=0.03 意味着97%的概率有效 | p=0.03 意味着如果没有效果，3%的概率会看到这样的数据 |
| p<0.05 = 真理 | p<0.05 只是"值得进一步研究"的阈值 |
| p值衡量效果大小 | p值只衡量证据强度，效果大小看效应量 |

---

## 4. 最大似然估计：AI模型训练的数学基础

### 核心思想

给定数据，找一组参数使"观测到这些数据的概率"最大。

```python
# 例子：抛硬币10次，7次正面，这枚硬币的公平性？
# 似然函数：P(7次正面 | p) = C(10,7) × p^7 × (1-p)^3

from scipy.optimize import minimize_scalar

def neg_log_likelihood(p):
    """负对数似然（我们要最小化它）"""
    if p <= 0 or p >= 1:
        return 1e10
    n, k = 10, 7
    return -(k * np.log(p) + (n - k) * np.log(1 - p))

result = minimize_scalar(neg_log_likelihood, bounds=(0.01, 0.99), method='bounded')
mle_p = result.x
print(f"MLE估计: p = {mle_p:.4f}")  # 0.7000
print(f"直觉估计: 7/10 = {7/10}")     # 完全一致！
```

### 为什么MLE在AI中无处不在

| 模型 | 训练目标 | 本质 |
|------|---------|------|
| 线性回归 | 最小化MSE | 最大化正态分布似然 |
| 逻辑回归 | 最小化交叉熵 | 最大化伯努利分布似然 |
| 神经网络(分类) | 最小化交叉熵损失 | 最大似然估计 |
| 神经网络(回归) | 最小化MSE | 最大似然估计(假设高斯噪声) |

```python
# 线性回归 = 高斯噪声假设下的MLE
np.random.seed(42)
n = 100
x = np.random.uniform(0, 10, n)
true_w, true_b = 2.5, 1.0
y = true_w * x + true_b + np.random.normal(0, 1, n)  # 加高斯噪声

# MLE解 = 最小二乘解
from numpy.linalg import lstsq
X = np.column_stack([x, np.ones(n)])
w_mle, residuals, _, _ = lstsq(X, y, rcond=None)
print(f"MLE: w={w_mle[0]:.3f}, b={w_mle[1]:.3f}")
print(f"真实: w={true_w}, b={true_b}")
```

---

## 5. 过拟合的统计视角

### 偏差-方差分解

```python
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

np.random.seed(42)
n = 50
x = np.random.uniform(0, 2*np.pi, n)
y_true = np.sin(x)
y = y_true + np.random.normal(0, 0.3, n)

# 不同复杂度模型的偏差-方差
degrees = [1, 3, 5, 15]
for d in degrees:
    model = Pipeline([
        ('poly', PolynomialFeatures(d)),
        ('lr', LinearRegression())
    ])
    
    # 交叉验证MSE ≈ 偏差² + 方差 + 不可约误差
    scores = cross_val_score(model, x.reshape(-1,1), y, cv=5, scoring='neg_mean_squared_error')
    mse = -scores.mean()
    
    model.fit(x.reshape(-1,1), y)
    train_mse = np.mean((model.predict(x.reshape(-1,1)) - y)**2)
    
    print(f"度数={d:2d}: 训练MSE={train_mse:.4f}, 验证MSE={mse:.4f}")
    # 度数=1: 欠拟合（高偏差）
    # 度数=3: 刚好
    # 度数=15: 过拟合（训练MSE低但验证MSE高）
```

### 统计学的启示

- **过拟合** = 低偏差 + 高方差（记住训练数据但泛化差）
- **欠拟合** = 高偏差 + 低方差（连训练数据都没学好）
- **正则化** = 人为增加偏差来降低方差

---

## 本节关键收获

| 概念 | 统计学定义 | AI中的角色 |
|------|-----------|-----------|
| 点估计 | 用样本统计量估计总体参数 | 模型参数 |
| 置信区间 | 估计的不确定性范围 | 预测的置信度 |
| p值 | 在H₀下观测到当前结果的概率 | A/B测试、特征选择 |
| MLE | 最大化似然函数 | 几乎所有模型的训练目标 |
| 偏差-方差 | 预测误差的分解 | 理解过拟合/欠拟合 |

## 下一节预告

实验1：用NumPy从零实现线性回归——不用sklearn，自己手写最大似然估计和梯度下降。
