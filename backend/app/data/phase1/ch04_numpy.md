# NumPy基础: 从Java数组到多维运算

## 学习目标
- 理解NumPy数组与Java数组的本质区别
- 掌握向量化运算——告别循环
- 学会数组创建、索引、切片、形状操作

---

## 1. 为什么需要NumPy

### 1.1 性能差距

```python
import numpy as np
import time

# 纯Python: 逐元素相加
a = list(range(1000000))
b = list(range(1000000))

start = time.time()
c = [x + y for x, y in zip(a, b)]    # 逐个相加
python_time = time.time() - start

# NumPy: 向量化运算
a_np = np.arange(1000000)
b_np = np.arange(1000000)

start = time.time()
c_np = a_np + b_np                     # 一次性相加
numpy_time = time.time() - start

print(f"Python: {python_time:.3f}s")
print(f"NumPy:  {numpy_time:.3f}s")
print(f"加速比: {python_time/numpy_time:.0f}x")
```

**为什么快这么多?**
- Python list存储对象指针, 每个元素是独立的Python对象
- NumPy数组存储连续的C类型数据, CPU缓存友好
- 向量化运算在C层执行, 避免Python循环开销

**Java对比**: Java的`int[]`也是连续内存, 性能接近NumPy。但Java缺少向量化操作——你不能直接写`a + b`对两个数组求和, 需要循环。NumPy让你写出**数学公式级别的代码**。

---

## 2. 数组创建

```python
import numpy as np

# 从列表创建
a = np.array([1, 2, 3, 4, 5])              # 1维
b = np.array([[1, 2], [3, 4]])              # 2维(矩阵)

# 特殊数组
np.zeros(5)                  # [0, 0, 0, 0, 0]
np.ones((3, 3))              # 3x3全1矩阵
np.arange(0, 10, 2)          # [0, 2, 4, 6, 8]  类似range
np.linspace(0, 1, 5)         # [0, 0.25, 0.5, 0.75, 1.0]  等间距
np.random.randn(3, 4)        # 3x4标准正态随机数
np.eye(3)                    # 3x3单位矩阵

# 数据类型
a = np.array([1, 2, 3], dtype=np.float64)   # 指定float64
a.dtype                      # dtype('float64')
```

---

## 3. 索引与切片

### 3.1 基础索引(和Python list一样)

```python
a = np.array([10, 20, 30, 40, 50])
a[0]          # 10
a[-1]         # 50
a[1:4]        # array([20, 30, 40])
```

### 3.2 多维索引

```python
m = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

m[0, 0]       # 1(第一行第一列)
m[1, :]       # array([4, 5, 6])(第二行)
m[:, 1]       # array([2, 5, 8])(第二列)
m[0:2, 1:3]   # array([[2, 3], [5, 6]])(子矩阵)
```

**Java对比**: Java二维数组是`m[i][j]`, NumPy是`m[i, j]`——更简洁, 且支持行列同时切片。

### 3.3 布尔索引——最强大的特性

```python
data = np.array([23, 45, 12, 67, 34, 89, 56])

# 筛选大于50的元素
mask = data > 50
data[mask]                   # array([67, 89, 56])

# 一步到位
data[data > 50]              # 同上

# 条件赋值
data[data > 50] = 50         # 将所有>50的值截断为50
```

**Java对比**: Java没有布尔索引, 需要循环+条件判断+新列表。NumPy一行搞定。

### 3.4 花式索引

```python
data = np.array([10, 20, 30, 40, 50])

# 用索引数组取值
indices = [0, 2, 4]
data[indices]                # array([10, 30, 50])

# 用另一个数组重新排列
order = [4, 3, 2, 1, 0]
data[order]                  # array([50, 40, 30, 20, 10])  反转
```

---

## 4. 向量化运算

```python
a = np.array([1, 2, 3, 4, 5])
b = np.array([10, 20, 30, 40, 50])

# 算术运算(逐元素)
a + b          # array([11, 22, 33, 44, 55])
a * b          # array([10, 40, 90, 160, 250])
a ** 2         # array([1, 4, 9, 16, 25])

# 比较运算(返回布尔数组)
a > 3          # array([False, False, False, True, True])

# 统计运算
a.sum()        # 15
a.mean()       # 3.0
a.std()        # 标准差
a.max()        # 5
a.argmax()     # 4(最大值的索引)

# 沿轴运算
m = np.array([[1, 2, 3],
              [4, 5, 6]])
m.sum(axis=0)   # array([5, 7, 9])   按列求和
m.sum(axis=1)   # array([6, 15])     按行求和
```

**理解axis**: `axis=0`是沿着行的方向(结果消去行->按列运算), `axis=1`是沿着列的方向(结果消去列->按行运算)。

---

## 5. 广播机制

NumPy最强大也最容易困惑的特性——不同形状的数组如何运算:

```python
# 形状(3,) + 标量 -> 标量广播到(3,)
a = np.array([1, 2, 3])
a + 10              # array([11, 12, 13])

# 形状(3,3) + 形状(3,) -> 行向量广播到(3,3)
m = np.ones((3, 3))
v = np.array([1, 2, 3])
m + v               # 每行都加上[1, 2, 3]

# 形状(3,1) + 形状(1,3) -> 互相广播到(3,3)
col = np.array([[1], [2], [3]])    # (3, 1)
row = np.array([[10, 20, 30]])     # (1, 3)
col + row           # (3, 3)矩阵, 每个元素 = col_i + row_j
```

**广播规则**:
1. 从最右侧维度开始对齐
2. 维度相等 或 其中一个为1 -> 兼容
3. 维度为1的会被"复制扩展"

---

## 6. 形状操作

```python
a = np.arange(12)            # [0,1,2,...,11], 形状(12,)

# reshape
a.reshape(3, 4)              # 3行4列矩阵
a.reshape(2, 6)              # 2行6列
a.reshape(3, -1)             # -1表示自动计算: 3行4列

# 转置
m = a.reshape(3, 4)
m.T                           # 4行3列

# 拼接
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
np.concatenate([a, b])       # array([1, 2, 3, 4, 5, 6])
np.vstack([a, b])            # 垂直堆叠
np.hstack([a, b])            # 水平堆叠
```

---

## 练习题

1. 不用循环, 计算100x100矩阵每行的均值和标准差
2. 实现矩阵乘法: 用广播和`sum(axis=)`实现`C = A @ B`(不用`np.dot`)
3. 给定一个(1000,)的数组, 找出所有局部极大值的索引(比左右邻居都大的元素)
