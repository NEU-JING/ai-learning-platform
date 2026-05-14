# Day 4 - 微积分：不是求导规则，是变化率的语言

## 主题

Java开发者习惯了离散世界——数组索引、循环计数、状态机。但AI的核心是连续优化：参数是连续的，损失函数是连续的，我们在连续空间中寻找最低点。

微积分就是描述连续变化的数学语言。不是背求导规则，而是理解"变化率"这个概念。

## 学习目标

- 理解导数 = 瞬时变化率 = 函数的"速度计"
- 理解链式法则 = 复合函数的变化传递
- 用NumPy数值计算导数，建立直觉
- 理解为什么AI需要可微函数

---

## 1. 导数：函数的速度计

### 从平均变化率到瞬时变化率

```python
import numpy as np

# 函数 f(x) = x²
def f(x):
    return x ** 2

# 平均变化率（你熟悉的：Java里的slope）
x0 = 3.0
h_large = 1.0
avg_rate = (f(x0 + h_large) - f(x0)) / h_large
print(f"平均变化率(h=1.0): {avg_rate:.2f}")  # 7.0

# 让h越来越小
for h in [0.1, 0.01, 0.001, 0.0001]:
    rate = (f(x0 + h) - f(x0)) / h
    print(f"h={h:.4f}: 变化率 = {rate:.6f}")

# 当h→0，变化率→6.0，这就是x=3处的导数
```

### 数值导数

```python
def numerical_derivative(f, x, h=1e-5):
    """数值求导——AI最常用的求导方式"""
    return (f(x + h) - f(x - h)) / (2 * h)

# 验证：x²的导数 = 2x
for x in [0, 1, 2, 3, -1]:
    analytical = 2 * x           # 解析解
    numerical = numerical_derivative(lambda t: t**2, x)
    print(f"x={x:2d}: 解析={analytical:.4f}, 数值={numerical:.4f}")
```

### 导数的几何含义

```python
# 导数 = 切线斜率 = 函数在该点的"倾斜程度"
# 正导数 → 函数在上升；负导数 → 函数在下降；零导数 → 局部极值

import numpy as np

x = np.linspace(-3, 3, 100)
y = x ** 3 - 3 * x  # 有两个极值的函数

# 找极值点（导数=0的地方）
# f'(x) = 3x² - 3 = 0 → x = ±1
print(f"x=-1: f={(-1)**3 - 3*(-1):.1f} (局部极大)")
print(f"x=+1: f={(1)**3 - 3*(1):.1f} (局部极小)")
```

---

## 2. 偏导数：多维空间的变化率

### 为什么需要偏导数

AI模型的参数不是1个，是几千到几十亿个。每个参数的变化都会影响损失函数。偏导数告诉我们：**只动这一个参数，损失变化多少？**

```python
# 函数 f(x, y) = x² + y² （一个碗形曲面）
def f_2d(x, y):
    return x**2 + y**2

# 对x的偏导数：把y当常数
# ∂f/∂x = 2x
# 对y的偏导数：把x当常数
# ∂f/∂y = 2y

def numerical_partial(f, x, y, var='x', h=1e-5):
    """数值偏导数"""
    if var == 'x':
        return (f(x + h, y) - f(x - h, y)) / (2 * h)
    else:
        return (f(x, y + h) - f(x, y - h)) / (2 * h)

# 在点(3, 4)处的偏导数
x0, y0 = 3.0, 4.0
df_dx = numerical_partial(f_2d, x0, y0, 'x')
df_dy = numerical_partial(f_2d, x0, y0, 'y')
print(f"∂f/∂x = {df_dx:.4f} (理论: {2*x0})")
print(f"∂f/∂y = {df_dy:.4f} (理论: {2*y0})")
```

### 梯度 = 所有偏导数组成的向量

```python
# 梯度指向函数增长最快的方向
gradient = np.array([df_dx, df_dy])
print(f"梯度: {gradient}")
print(f"梯度方向: {gradient / np.linalg.norm(gradient)}")
print(f"梯度模长: {np.linalg.norm(gradient):.4f}")

# 梯度的反方向 = 函数下降最快的方向
# 这就是"梯度下降"的由来！
print(f"最速下降方向: {-gradient / np.linalg.norm(gradient)}")
```

---

## 3. 链式法则：深度学习的数学引擎

### 一句话概括

如果 y = f(g(x))，那么 dy/dx = (dy/dg) × (dg/dx)。

**用人话说**：变化是一层一层传递的——外层的变化率 × 内层的变化率 = 总变化率。

```python
# 神经网络的一层：y = σ(w·x + b)
# σ是激活函数（如sigmoid），w和b是参数

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_deriv(x):
    """sigmoid的导数 = σ(x)(1-σ(x))"""
    s = sigmoid(x)
    return s * (1 - s)

# 链式法则：dy/dw = dy/dσ × dσ/dz × dz/dw
# 其中 z = wx + b
w, x, b = 0.5, 2.0, 1.0
z = w * x + b
sigma_z = sigmoid(z)

# dy/dw = σ'(z) × x
dy_dw = sigmoid_deriv(z) * x
print(f"dy/dw = {dy_dw:.4f}")

# 数值验证
h = 1e-5
dy_dw_numerical = (sigmoid((w+h)*x + b) - sigmoid((w-h)*x + b)) / (2*h)
print(f"dy/dw (数值) = {dy_dw_numerical:.4f}")
```

### 多层链式法则 = 反向传播

```python
# 2层网络：y = w2·σ(w1·x + b1) + b2
# 链式传递：dy/dw1 = dy/dh × dh/dz × dz/dw1

# 这就是反向传播！逐层从输出往回传梯度
# "反向"传播 = 链式法则从外到内展开

np.random.seed(42)
w1, b1 = np.random.randn(3, 2), np.random.randn(3)
w2, b2 = np.random.randn(1, 3), np.random.randn(1)
x_input = np.array([0.5, -0.3])

# 前向传播
z1 = w1 @ x_input + b1        # (3,)
h = sigmoid(z1)                # (3,)
z2 = w2 @ h + b2               # (1,)
y = z2[0]

print(f"输入: {x_input}")
print(f"隐藏层: {h.round(3)}")
print(f"输出: {y:.4f}")

# 反向传播（手动链式法则）
dy_dz2 = 1.0                          # y = z2, 导数为1
dz2_dw2 = h                            # z2 = w2·h + b2
dy_dw2 = dy_dz2 * dz2_dw2              # (3,) — w2的梯度

dz2_dh = w2[0]                         # (3,)
dh_dz1 = sigmoid_deriv(z1)             # (3,)
dz1_dw1 = x_input                      # (2,)
# 对w1的每个元素：链式传递
dy_dw1 = np.outer(dy_dz2 * dz2_dh * dh_dz1, dz1_dw1)  # (3,2)

print(f"w2梯度: {dy_dw2.round(4)}")
print(f"w1梯度形状: {dy_dw1.shape}")
```

---

## 4. 积分：从变化率还原总量

### 直觉

导数是"拆"（从函数到变化率），积分是"装"（从变化率回到函数）。它们互为逆运算。

```python
# 速度 → 距离：积分
# 速度是位置的变化率（导数），位置是速度的累积（积分）

# 数值积分：黎曼和
def integrate(f, a, b, n=10000):
    """数值积分（中点法）"""
    x = np.linspace(a, b, n)
    dx = (b - a) / n
    return np.sum(f(x)) * dx

# ∫₀¹ x² dx = 1/3
result = integrate(lambda x: x**2, 0, 1)
print(f"∫₀¹ x² dx = {result:.6f} (理论: {1/3:.6f})")

# AI中的积分：概率分布的归一化
# 概率密度函数的积分必须为1
# 正态分布的归一化常数就是通过积分得到的
```

### AI中的积分

| 场景 | 积分的角色 |
|------|-----------|
| 概率归一化 | ∫p(x)dx = 1 |
| 边缘概率 | P(X) = ∫P(X,Y)dY |
| 期望 | E[f(X)] = ∫f(x)p(x)dx |
| 变分推断 | 用积分近似后验分布 |

---

## 5. 为什么AI需要可微函数

### 不可微 = 梯度不存在 = 无法优化

```python
# 阶跃函数：不可微（在0处导数不存在）
# → 这就是为什么用sigmoid替代阶跃函数

# ReLU：在0处不可微，但几乎不影响
def relu(x):
    return np.maximum(0, x)

def relu_grad(x):
    """ReLU的次梯度"""
    return np.where(x > 0, 1.0, 0.0)

# 实际中，x=0的概率极低，所以ReLU的不可微点被忽略
```

### 梯度消失与梯度爆炸

```python
# 梯度消失：sigmoid的导数最大值只有0.25
# 多层叠加后，梯度指数级衰减
layers = 50
grad_magnitude = 0.25 ** layers
print(f"{layers}层后sigmoid梯度: {grad_magnitude:.2e}")  # ≈0

# 这就是为什么深层网络用ReLU——它的导数是1（正区间）
relu_grad_magnitude = 1.0 ** layers
print(f"{layers}层后ReLU梯度: {relu_grad_magnitude:.2e}")  # 1.0
```

---

## 本节关键收获

| 概念 | 数学定义 | AI中的角色 |
|------|---------|-----------|
| 导数 | 函数的变化率 | 损失函数的梯度 |
| 偏导数 | 多元函数对一个变量的变化率 | 每个参数的梯度 |
| 梯度 | 所有偏导数组成的向量 | 最速下降方向 |
| 链式法则 | 复合函数的导数传递 | 反向传播的数学基础 |
| 积分 | 变化率的累积 | 概率归一化、期望计算 |

## 下一节预告

优化：为什么梯度下降能工作——从凸函数到学习率，理解训练过程的本质。
