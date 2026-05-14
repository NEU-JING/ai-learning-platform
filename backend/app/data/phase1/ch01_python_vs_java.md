# 心智模型转换: Python vs Java

## 学习目标
- 理解Python与Java在设计哲学上的根本差异
- 建立Python的"鸭子类型"思维, 摆脱Java的"契约优先"惯性
- 掌握Python核心数据类型及其与Java类型的映射关系

---

## 1. 设计哲学: 为什么Python"看起来简单"

Java的设计目标是"一次编写, 到处运行", 强调**安全性和规范性**——编译器是你的朋友, 在代码运行之前就帮你排除错误。

Python的设计目标是"人生苦短, 我用Python", 强调**开发效率和表达力**——程序员的时间比CPU的时间更宝贵。

这导致了根本性的差异:

| 维度 | Java思维 | Python思维 |
|------|---------|-----------|
| 类型安全 | 编译期保证, 不通过不运行 | 运行时发现, 快速试错 |
| 代码风格 | 一切皆类, 设计模式先行 | 能用函数就不用类, 简单即美 |
| 错误处理 | 编译器是第一道防线 | EAFP(Easier to Ask Forgiveness than Permission) |
| 接口契约 | 必须显式声明implements | 鸭子类型: 走起来像鸭子就是鸭子 |

**关键转变**: 从"先设计好一切再动手"到"先让它跑起来, 再逐步优化"。

---

## 2. 动态类型: Python最核心的心智转变

### 2.1 变量不是"盒子", 是"标签"

```java
// Java: 变量是一个盒子, 类型决定了盒子能装什么
String name = "Alice";    // 盒子只能装String
name = 42;                // 编译错误!
```

```python
# Python: 变量是一个标签, 贴在任何对象上
name = "Alice"           # 标签贴在str对象上
name = 42                # 标签撕下来贴在int对象上, 完全合法
name = [1, 2, 3]         # 再贴到list上, 也OK
```

**理解要点**: Python中变量没有类型, 对象才有类型。变量只是指向对象的引用(标签)。

### 2.2 鸭子类型实战

```java
// Java: 必须声明接口
public interface Quackable {
    void quack();
}

public class Duck implements Quackable {
    public void quack() { System.out.println("嘎嘎"); }
}

public void makeSound(Quackable animal) {  // 必须是Quackable
    animal.quack();
}
```

```python
# Python: 不需要接口声明
class Duck:
    def quack(self):
        print("嘎嘎")

class ToyDuck:
    def quack(self):
        print("电子嘎嘎")

def make_sound(animal):  # 不限定类型
    animal.quack()        # 只要有quack方法就行

make_sound(Duck())       # 嘎嘎
make_sound(ToyDuck())    # 电子嘎嘎
```

这就是**鸭子类型**: 如果它走起来像鸭子, 叫起来像鸭子, 那它就是鸭子。不需要事先声明"我是鸭子"。

---

## 3. 核心数据类型映射

### 3.1 基本类型

| Java | Python | 关键差异 |
|------|--------|---------|
| `int` (32位) | `int` (任意精度) | Python的int不会溢出! `2**1000`直接算 |
| `double` | `float` (64位) | 基本一致 |
| `boolean` | `bool` | `True/False`(大写!) |
| `String` | `str` | 不可变, 支持切片 |
| `null` | `None` | Python的空值 |

### 3.2 集合类型

```python
# list = Java ArrayList(但更强大)
fruits = ["apple", "banana", "cherry"]
fruits.append("date")           # 末尾添加
fruits.insert(1, "blueberry")   # 指定位置插入
fruits[0]                       # 索引访问
fruits[-1]                      # 反向索引! Java没有
fruits[1:3]                     # 切片! Java没有

# dict = Java HashMap
student = {"name": "张三", "age": 25}
student["name"]                  # 取值
student.get("grade", "N/A")     # 安全取值(类似Java的getOrDefault)
student["email"] = "a@b.com"    # 添加/更新

# set = Java HashSet
unique = {1, 2, 3, 2}           # 自动去重 -> {1, 2, 3}
unique.add(4)
unique & {3, 4, 5}              # 交集 -> {3, 4}
unique | {3, 4, 5}              # 并集 -> {1, 2, 3, 4, 5}

# tuple = 不可变list(Java没有直接对应)
point = (3, 4)                   # 创建后不可修改
x, y = point                     # 解构赋值!
```

### 3.3 切片——Python最优雅的特性

切片是Java开发者最容易忽视但最强大的特性:

```python
s = "Hello, Python!"

# 基本切片 s[start:stop:step]
s[7:]        # "Python!"    从第7个到末尾
s[:5]        # "Hello"      从开头到第5个
s[7:13]      # "Python"     第7到12个
s[::-1]      # "!nohtyP ,olleH"  反转!
s[::2]       # "Hlo yhn"    每隔一个取

# 切片同样适用于list
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
nums[2:8:2]  # [2, 4, 6]
nums[-3:]    # [7, 8, 9]    最后3个
```

**Java对比**: Java取子串/子列表需要`substring()`/`subList()`, 反转需要`Collections.reverse()`, Python一行搞定。

---

## 4. 控制流: 小差异大影响

### 4.1 if-elif-else

```python
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:      # 注意: elif, 不是else if
    grade = "B"
else:
    grade = "C"
```

### 4.2 for循环——Python的for是foreach

```java
// Java for循环
for (int i = 0; i < list.size(); i++) {
    System.out.println(list.get(i));
}
```

```python
# Python: for-each 是唯一的for
for item in my_list:
    print(item)

# 需要索引? 用enumerate
for i, item in enumerate(my_list):
    print(f"第{i}个: {item}")

# 需要数字序列? 用range
for i in range(10):        # 0到9
    print(i)

# 同时遍历两个列表? 用zip
names = ["Alice", "Bob"]
ages = [25, 30]
for name, age in zip(names, ages):
    print(f"{name}: {age}")
```

### 4.3 列表推导式——Python的杀手级特性

```java
// Java: 筛选偶数并平方
List<Integer> result = new ArrayList<>();
for (int n : numbers) {
    if (n % 2 == 0) {
        result.add(n * n);
    }
}
```

```python
# Python: 一行搞定
result = [n * n for n in numbers if n % 2 == 0]

# 更复杂的例子
words = ["Hello", "World", "AI"]
lower_words = [w.lower() for w in words]          # ["hello", "world", "ai"]
word_lengths = {w: len(w) for w in words}         # 字典推导式
```

---

## 5. 字符串格式化

```python
name = "张三"
score = 95.5

# f-string(Python 3.6+, 最推荐)
print(f"{name}的成绩是{score}分")           # 张三的成绩是95.5分
print(f"{name:*^20}")                       # *******张三*******
print(f"百分比: {score/100:.1%}")            # 百分比: 95.5%

# format方法(兼容旧代码)
"{}的成绩是{}分".format(name, score)

# 拼接(不推荐, 但常见)
name + "的成绩是" + str(score) + "分"
```

---

## 练习题

1. **列表操作**: 给定一个字符串列表, 用列表推导式生成一个字典, key是字符串, value是其长度
2. **切片练习**: 将字符串"Hello, Python World!"反转, 然后取出前5个字符
3. **类型思维**: 写一个函数`process(data)`, 它能处理list、tuple、set三种输入, 返回排序后的列表。思考: 你需要检查类型吗?
