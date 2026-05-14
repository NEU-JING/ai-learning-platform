# Day 5 - 优化：为什么梯度下降能工作

## 主题

AI模型训练的本质就是优化：找到一组参数让损失函数最小。梯度下降是最常用的优化算法。

但为什么它有效？什么情况下会失败？为什么需要学习率调度？这些问题不懂，调参就是玄学。

## 学习目标

- 理解梯度下降的几何直觉
- 理解学习率的影响（太大→发散，太小→太慢）
- 理解凸函数 vs 非凸函数的区别
- 理解SGD/Adam等变体的动机

---

## 1. 梯度下降的几何直觉

### 球下山坡

想象一个球放在山坡上，它会往哪个方向滚？**最陡的下坡方向**——这就是负梯度方向。

```python
import numpy as np

def gradient_descent_1d(f, df, x0, lr=0.1, n_iters=100):
    """1D梯度下降的可视化"""
    x = x0
    path = [x]
    for _ in range(n_iters):
        grad = df(x)
        x = x - lr * grad  # 往负梯度方向走一步
        path.append(x)
    return x, path

# f(x) = x² + 2x + 1 = (x+1)², 最小值在x=-1
f = lambda x: x**2 + 2*x + 1
df = lambda x: 2*x + 2

x_min, path = gradient_descent_1d(f, df, x0=3.0, lr=0.1)
print(f"起点: 3.0, 终点: {x_min:.6f}, 理论最小: -1.0")
print(f"前5步: {[f'{p:.4f}' for p in path[:5]]}")
```

### 学习率的影响

```python
# 学习率太大 → 震荡甚至发散
for lr in [0.01, 0.1, 0.5, 1.0, 2.0]:
    try:
        x_min, path = gradient_descent_1d(f, df, x0=3.0, lr=lr, n_iters=20)
        diverged = abs(x_min) > 100
        print(f"lr={lr:.2f}: 终点={x_min:.4f} {'⚠️ 发散!' if diverged else '✅ 收敛'}")
    except:
        print(f"lr={lr:.2f}: ❌ 数值溢出")
```

---

## 2. 凸函数：保证能找到全局最优

### 为什么凸函数重要

```python
# 凸函数：只有一个极小值 = 全局最小值
# 线性回归的损失函数是凸的 → 梯度下降一定收敛到全局最优

# 非凸函数：多个局部极小值
def non_convex(x):
    return x**4 - 4*x**3 + 2*x**2 + x

def non_convex_grad(x):
    return 4*x**3 - 12*x**2 + 4*x + 1

# 从不同起点出发，可能到达不同的局部极小值
for x0 in [-1.0, 0.0, 1.0, 2.5, 4.0]:
    x_min, _ = gradient_descent_1d(non_convex, non_convex_grad, x0, lr=0.01, n_iters=500)
    print(f"起点={x0:4.1f} → 终点={x_min:.4f}, f={non_convex(x_min):.4f}")
```

### 神经网络的损失函数是非凸的

这就是为什么：
- 初始化很重要（不同起点可能到达不同极小值）
- 学习率调度很重要（前期大步探索，后期小步精修）
- 随机性有帮助（SGD的噪声帮助跳出局部极小值）

---

## 3. SGD与Adam：从理论到实践

### 批量梯度下降 vs 随机梯度下降

```python
np.random.seed(42)
n = 1000
X = np.random.randn(n, 5)
true_w = np.array([1.0, -0.5, 2.0, 0.0, -1.0])
y = X @ true_w + np.random.normal(0, 0.5, n)

def mse_loss(w):
    return np.mean((X @ w - y) ** 2)

def mse_grad(w):
    return 2 / n * X.T @ (X @ w - y)

# 批量梯度下降（每次用全部数据）
def batch_gd(lr=0.01, n_iters=200):
    w = np.zeros(5)
    losses = []
    for _ in range(n_iters):
        grad = mse_grad(w)
        w = w - lr * grad
        losses.append(mse_loss(w))
    return w, losses

# 随机梯度下降（每次只用1个样本）
def sgd(lr=0.01, n_epochs=20):
    w = np.zeros(5)
    losses = []
    for epoch in range(n_epochs):
        indices = np.random.permutation(n)
        for i in indices:
            xi, yi = X[i:i+1], y[i:i+1]
            grad = 2 * xi.T @ (xi @ w - yi)
            w = w - lr * grad
        losses.append(mse_loss(w))
    return w, losses

# 小批量梯度下降（折中方案，实际最常用）
def mini_batch_gd(lr=0.01, n_epochs=50, batch_size=32):
    w = np.zeros(5)
    losses = []
    for epoch in range(n_epochs):
        indices = np.random.permutation(n)
        for start in range(0, n, batch_size):
            batch_idx = indices[start:start+batch_size]
            Xb, yb = X[batch_idx], y[batch_idx]
            grad = 2 / len(batch_idx) * Xb.T @ (Xb @ w - yb)
            w = w - lr * grad
        losses.append(mse_loss(w))
    return w, losses

w_bgd, l_bgd = batch_gd()
w_sgd, l_sgd = sgd()
w_mbgd, l_mbgd = mini_batch_gd()

print(f"BGD 最终损失: {l_bgd[-1]:.6f}")
print(f"SGD 最终损失: {l_sgd[-1]:.6f}")
print(f"Mini-batch 最终损失: {l_mbgd[-1]:.6f}")
```

### Adam优化器：AI训练的默认选择

```python
def adam_optimize(grad_fn, x0, lr=0.001, betas=(0.9, 0.999), eps=1e-8, n_iters=500):
    """Adam优化器——自适应学习率 + 动量"""
    x = x0.copy()
    m = np.zeros_like(x)  # 一阶矩（动量）
    v = np.zeros_like(x)  # 二阶矩（自适应学习率）
    b1, b2 = betas
    
    for t in range(1, n_iters + 1):
        g = grad_fn(x)
        m = b1 * m + (1 - b1) * g          # 动量：梯度的指数移动平均
        v = b2 * v + (1 - b2) * g ** 2      # 自适应：梯度平方的指数移动平均
        m_hat = m / (1 - b1 ** t)            # 偏差修正
        v_hat = v / (1 - b2 ** t)            # 偏差修正
        x = x - lr * m_hat / (np.sqrt(v_hat) + eps)  # 自适应步长
    
    return x

w_adam = adam_optimize(mse_grad, np.zeros(5))
print(f"Adam 最终损失: {mse_loss(w_adam):.6f}")
print(f"Adam 参数: {w_adam.round(3)}")
print(f"真实参数: {true_w}")
```

---

## 4. 学习率调度

```python
# 为什么需要调度？
# - 前期：大学习率快速接近最优点
# - 后期：小学习率精修，避免在最优点附近震荡

def lr_schedule(epoch, initial_lr=0.1):
    """学习率调度示例"""
    # 余弦退火
    return initial_lr * 0.5 * (1 + np.cos(np.pi * epoch / 100))

for epoch in [0, 10, 25, 50, 75, 100]:
    print(f"Epoch {epoch:3d}: lr={lr_schedule(epoch):.6f}")
```

---

## 本节关键收获

| 概念 | 直觉 | AI中的角色 |
|------|------|-----------|
| 梯度下降 | 球往最陡的下坡方向滚 | 模型训练的基本算法 |
| 学习率 | 每一步走多远 | 太大→震荡，太小→太慢 |
| 凸函数 | 只有一个谷底 | 线性回归保证全局最优 |
| 非凸函数 | 多个谷底 | 神经网络需要技巧避免局部最优 |
| SGD | 每次只用部分数据 | 噪声帮助探索 + 计算效率 |
| Adam | 自适应步长+动量 | 默认优化器，大多数场景首选 |

## 下一节预告

信息论与正则化：为什么简单模型更可靠——从信息论角度理解过拟合和正则化。
