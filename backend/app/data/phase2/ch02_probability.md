# Day 2 - 概率论：不是公式背诵，是不确定性量化

## 主题

Java开发者习惯确定性思维——输入A必然输出B。但真实世界充满不确定性：用户会不会流失？这封邮件是不是垃圾？这张图是不是猫？

概率论就是量化不确定性的数学语言。AI模型本质上是在说："我不确定，但我的最佳猜测是X，置信度Y%。"

## 学习目标

- 理解概率是"不确定性的度量"，不是"频率的极限"
- 理解贝叶斯定理 = 用新证据更新信念
- 理解常见分布为什么长那样
- 用NumPy模拟概率实验，建立直觉

---

## 1. 概率：从"上帝视角"到"赌徒视角"

### 频率学派 vs 贝叶斯学派

| 学派 | 概率是什么 | 典型问题 |
|------|-----------|---------|
| 频率学派 | 重复实验的长期频率 | "抛硬币1000次，正面大约500次" |
| 贝叶斯学派 | 对命题的置信度 | "基于现有证据，这枚硬币是公平的概率是多少？" |

AI几乎都是贝叶斯学派——因为我们面对的是**单次事件**（这张图是不是猫？），不是无限重复。

### 用代码建立直觉

```python
import numpy as np

# 掷骰子实验
np.random.seed(42)
n_rolls = 100000
rolls = np.random.randint(1, 7, size=n_rolls)

# 概率 = 长期频率
for face in range(1, 7):
    prob = (rolls == face).mean()
    print(f"面{face}: {prob:.4f} (理论值: {1/6:.4f})")

# 条件概率：已知是偶数，是6的概率？
even_rolls = rolls[rolls % 2 == 0]
prob_6_given_even = (even_rolls == 6).mean()
print(f"\nP(6|偶数) = {prob_6_given_even:.4f} (理论值: {1/3:.4f})")
```

---

## 2. 贝叶斯定理：AI最重要的一个公式

### 公式

$$P(A|B) = \frac{P(B|A) \times P(A)}{P(B)}$$

### 用人话说

- P(A)：先验——没有证据时的信念
- P(B|A)：似然——如果A是真的，看到证据B的可能性
- P(A|B)：后验——看到证据B后，更新后的信念

**贝叶斯定理 = 先验 + 证据 → 后验**

### 垃圾邮件分类器

```python
# 朴素贝叶斯分类器的直觉
# 问题：一封包含"免费"的邮件，是垃圾邮件的概率？

# 先验：历史数据中30%是垃圾邮件
p_spam = 0.30

# 似然：垃圾邮件中80%包含"免费"
p_free_given_spam = 0.80

# 证据：正常邮件中10%包含"免费"
p_free_given_ham = 0.10

# 全概率
p_free = p_free_given_spam * p_spam + p_free_given_ham * (1 - p_spam)

# 贝叶斯：P(垃圾|免费)
p_spam_given_free = (p_free_given_spam * p_spam) / p_free
print(f"P(垃圾邮件|含'免费') = {p_spam_given_free:.2%}")  # 77.42%

# 关键洞察：即使"免费"在垃圾邮件中很常见(80%)
# 但先验概率(30%)也很重要——不能只看似然
```

### 为什么这叫"朴素"贝叶斯

因为它假设所有特征**条件独立**（"免费"和"中奖"出现互不影响）。这个假设几乎总是错的，但朴素贝叶斯在很多场景下效果出奇地好——因为分类只需要排序正确，不需要概率值精确。

---

## 3. 常见分布：为什么它们长那样

### 正态分布——万物默认分布

```python
import numpy as np

# 中心极限定理：不管原始分布是什么，大量独立随机变量的和趋向正态
np.random.seed(42)

# 原始分布：均匀分布（完全不是正态）
samples = np.random.uniform(0, 1, size=(10000, 100))
means = samples.mean(axis=1)  # 10000组，每组100个均匀随机数的均值

print(f"均值: {means.mean():.4f} (理论: 0.5)")
print(f"标准差: {means.std():.4f} (理论: {1/np.sqrt(12*100):.4f})")
# 均值的分布就是正态的！
```

**中心极限定理**是概率论最强大的结论：任何独立同分布的随机变量，只要数量够多，它们的**平均值**就近似正态分布。这就是为什么正态分布在统计学和AI中无处不在。

### 为什么AI假设噪声是正态的

因为噪声通常是大量微小独立因素的叠加——根据中心极限定理，它自然趋向正态。

```python
# 正态分布在AI中的角色
# 线性回归假设: y = wx + b + ε, 其中ε~N(0, σ²)
# 逻辑回归假设: P(y=1|x) = sigmoid(wx + b)
# 神经网络初始化: 权重从N(0, 0.01)采样

# 权重初始化的直觉
w_xavier = np.random.randn(100, 50) * np.sqrt(2.0 / (100 + 50))
print(f"Xavier初始化权重的标准差: {w_xavier.std():.4f}")
print(f"理论值: {np.sqrt(2.0/(100+50)):.4f}")
```

### 其他重要分布

```python
# 伯努利分布：抛一次硬币
# P(X=1) = p, P(X=0) = 1-p
# 应用：二分类问题的标签

# 二项分布：抛n次硬币，正面次数
n, p = 100, 0.3
binomial = np.random.binomial(n, p, size=10000)
print(f"二项分布均值: {binomial.mean():.2f} (理论: {n*p})")
print(f"二项分布方差: {binomial.var():.2f} (理论: {n*p*(1-p)})")

# 指数分布：等待时间
# 应用：用户停留时间、请求间隔
exp_samples = np.random.exponential(scale=2.0, size=10000)
print(f"指数分布均值: {exp_samples.mean():.2f} (理论: 2.0)")

# Softmax：从分数到概率分布
logits = np.array([2.0, 1.0, 0.1])
probs = np.exp(logits) / np.exp(logits).sum()
print(f"Softmax输出: {probs.round(3)}")  # [0.659, 0.242, 0.098] — 概率分布！
```

---

## 4. 期望与方差：不确定性的两个维度

### 期望（Expected Value）——不确定性的中心

```python
# 期望 = 长期平均值
# 彩票的期望值
prizes = [0, 0, 0, 5, 100, 10000]  # 奖金
probs = [0.5, 0.3, 0.15, 0.03, 0.019, 0.001]  # 概率

expected_value = sum(p * z for p, z in zip(probs, prizes))
print(f"彩票期望值: {expected_value:.2f}元")
print(f"如果售价2元，期望收益: {expected_value - 2:.2f}元")  # 负的→不值得买
```

### 方差（Variance）——不确定性的大小

```python
# 两个投资方案，期望收益相同
investment_a = np.array([4, 5, 6, 5, 5])  # 稳健
investment_b = np.array([0, 10, 2, 8, 0])  # 激进

print(f"A: 期望={investment_a.mean():.1f}, 方差={investment_a.var():.1f}")
print(f"B: 期望={investment_b.mean():.1f}, 方差={investment_b.var():.1f}")
# 同样期望，B的方差大得多→风险高

# AI中的方差-偏差权衡
# 偏差(Bias)：模型预测与真实值的系统性偏离
# 方差(Variance)：模型对不同训练集的敏感度
# 好模型 = 低偏差 + 低方差，但往往需要权衡
```

---

## 5. 信息量与熵

### 信息量 = 意外程度

```python
# 越不可能发生的事件，发生时携带的信息越多
def information(p):
    """事件的信息量 = -log2(p)"""
    return -np.log2(p)

print(f"抛硬币正面(P=0.5)的信息量: {information(0.5):.2f} bits")  # 1 bit
print(f"骰子6点(P=1/6)的信息量: {information(1/6):.2f} bits")     # 2.58 bits
print(f"罕见事件(P=0.01)的信息量: {information(0.01):.2f} bits")  # 6.64 bits
```

### 熵 = 平均信息量 = 不确定性

```python
def entropy(probs):
    """香农熵 = 不确定性的度量"""
    probs = np.array(probs)
    probs = probs[probs > 0]  # 排除0概率
    return -np.sum(probs * np.log2(probs))

print(f"公平硬币的熵: {entropy([0.5, 0.5]):.2f} bits")   # 1.00 — 最大不确定性
print(f"偏心硬币的熵: {entropy([0.9, 0.1]):.2f} bits")    # 0.47 — 几乎确定
print(f"确定性事件的熵: {entropy([1.0]):.2f} bits")       # 0.00 — 完全确定

# 交叉熵 = 分类损失的数学基础
# 交叉熵越低 → 模型预测越接近真实分布
def cross_entropy(p_true, p_pred):
    """p_true: 真实分布, p_pred: 预测分布"""
    return -np.sum(p_true * np.log2(p_pred + 1e-10))

p_true = [1, 0]  # 真实标签：类别0
good_pred = [0.9, 0.1]  # 好预测
bad_pred = [0.3, 0.7]   # 差预测

print(f"好预测的交叉熵: {cross_entropy(p_true, good_pred):.2f}")  # 0.15
print(f"差预测的交叉熵: {cross_entropy(p_true, bad_pred):.2f}")   # 1.74
```

---

## 本节关键收获

| 概念 | 公式视角（考试用的） | 直觉视角（AI需要的） |
|------|---------------------|---------------------|
| 概率 | 频率的极限 | 对不确定性的度量 |
| 贝叶斯 | P(A\|B)=... | 用证据更新信念 |
| 正态分布 | 钟形曲线 | 大量独立因素叠加的默认分布 |
| 期望 | Σpᵢxᵢ | 长期平均 |
| 方差 | E[(X-μ)²] | 不确定性的大小/风险 |
| 熵 | -Σpᵢlog(pᵢ) | 不确定性的信息论度量 |

## 下一节预告

统计推断：从样本到结论的桥梁——如何用有限数据推断整体规律，以及AI模型如何量化预测的置信度。
