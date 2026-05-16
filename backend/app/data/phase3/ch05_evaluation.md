# Day 5 - 评估策略：准确率欺骗了你

## 准确率的三个谎言

### 谎言1：99%准确率意味着模型很好

```python
# 信用卡欺诈检测：99.9%的交易是正常的
y_pred = np.zeros(len(y_test))  # 永远预测"正常"
accuracy = accuracy_score(y_test, y_pred)  # 99.9%！
# 但一个欺诈都没抓到。这个模型完全没用。
```

### 谎言2：训练集准确率=模型能力

```python
model.fit(X_train, y_train)
train_acc = model.score(X_train, y_train)  # 99.5%
test_acc = model.score(X_test, y_test)     # 72.3%
# 巨大的差距 = 严重过拟合
```

### 谎言3：测试集准确率=线上表现

测试集是从训练数据同分布采样的。但线上数据的分布可能已经变了。

## 混淆矩阵：评估的起点

### 二分类的四个象限

```
                 预测正   预测负
  实际正    TP(真阳)   FN(假阴)
  实际负    FP(假阳)   TN(真阴)
```

**从业务角度理解**：

| 指标 | 公式 | 业务含义 |
|------|------|----------|
| Precision(精确率) | TP/(TP+FP) | 预测为正的样本中，有多少真的是正 |
| Recall(召回率) | TP/(TP+FN) | 真正的正样本中，有多少被找到 |
| F1 Score | 2×P×R/(P+R) | P和R的调和平均 |
| Specificity | TN/(TN+FP) | 负样本中，有多少正确识别为负 |

### 为什么Precision和Recall是矛盾的

```python
# 提高Recall：把所有人都标记为正
y_pred = np.ones(len(y))  # Recall = 100%, Precision → 正样本比例
# 提高Precision：只标记最确定的为正
y_pred = (model.predict_proba(X)[:, 1] > 0.9).astype(int)  # Precision高, Recall低
```

**类比风控**：
- **高Recall**：宁可错杀不可放过 → FP高，用户体验差
- **高Precision**：只在确信时拦截 → FN高，风险敞口大
- **选哪个**取决于业务代价：漏掉欺诈（FN）vs 冻结正常用户（FP）

## 评估指标选择指南

### 按业务场景选指标

| 场景 | 核心指标 | 辅助指标 | 原因 |
|------|----------|----------|------|
| 疾病筛查 | Recall | F1 | 漏诊代价极高 |
| 垃圾邮件 | Precision | F1 | 误删重要邮件代价高 |
| 推荐系统 | NDCG/Hit Rate | Coverage | 关注排序质量 |
| 搜索排序 | MAP/NDCG | MRR | 位置很重要 |
| 异常检测 | Precision@K | AUROC | Top-K精确率 |
| 信用评分 | KS/AUC | Gini | 排序能力 |

### 概率校准：预测概率靠谱吗

```python
from sklearn.calibration import calibration_curve

# 模型说"70%概率是欺诈"，实际欺诈比例是否≈70%？
prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)
# 如果prob_true和prob_pred差很远 → 概率不可信
```

**校准的重要性**：
- 如果只关心排序（AUC），校准不重要
- 如果关心概率值（风险评分），校准很关键
- 逻辑回归天生校准好，树模型校准差

## 交叉验证：正确的评估姿势

### 为什么不能只做一次train-test split

一次split的评估结果有方差——可能运气好，可能运气差。交叉验证通过多次split降低评估方差。

### K-Fold Cross Validation

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X, y, cv=5, scoring='f1')
print(f"5-Fold F1: {scores.mean():.3f} ± {scores.std():.3f}")
```

### 分层K-Fold（分类问题必须用）

```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=skf, scoring='f1')
# 保证每个fold中正负样本比例一致
```

### 时间序列交叉验证

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
# 不能随机split——未来数据不能泄露到训练中
# Fold 1: train=[1]    test=[2]
# Fold 2: train=[1,2]  test=[3]
# Fold 3: train=[1,2,3] test=[4]
```

### 分组交叉验证

```python
from sklearn.model_selection import GroupKFold

# 同一用户的记录必须全部在训练或全部在测试
gkf = GroupKFold(n_splits=5)
scores = cross_val_score(model, X, y, cv=gkf, groups=df['user_id'])
```

## ROC和AUC：排序能力的度量

### ROC曲线

```python
from sklearn.metrics import roc_curve, auc

fpr, tpr, thresholds = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

# FPR: 假阳率 = FP/(FP+TN)  → X轴
# TPR: 真阳率 = TP/(TP+FN)  → Y轴（=Recall）
# 曲线下面积 = AUC
```

### AUC的业务含义

AUC = 随机取一个正样本和一个负样本，模型给正样本更高概率的概率。

- AUC = 0.5 → 随机猜
- AUC = 0.7 → 有区分力
- AUC = 0.8 → 较好
- AUC = 0.9+ → 很好（但小心数据泄露）
- AUC = 1.0 → 几乎一定是泄露

### AUC的局限性

1. **对类别不平衡不敏感**：99%负样本时AUC可能很高，但Precision极低
2. **不关心概率校准**：排序正确但概率值可能偏差很大
3. **对业务不直观**：很难把AUC翻译成业务指标

**替代**：Precision-Recall AUC（不平衡数据更推荐）

## 评估中的常见陷阱

### 陷阱1：在测试集上调参

```python
# ❌ 在测试集上搜索超参数
for C in [0.01, 0.1, 1, 10]:
    model = LogisticRegression(C=C)
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)  # 测试集变成验证集了！
    if score > best_score:
        best_C = C  # 测试集信息泄露到超参数中

# ✅ 用交叉验证选超参数
from sklearn.model_selection import GridSearchCV
search = GridSearchCV(model, param_grid, cv=5)
search.fit(X_train, y_train)  # 只在训练集上CV
final_score = search.score(X_test, y_test)  # 最终只在测试集评估一次
```

### 陷阱2：忽略数据泄露的评估

```python
# ❌ 同一用户的数据分散在训练和测试集
X_train, X_test = train_test_split(df)  # 同一用户两条记录可能在两侧

# ✅ 按用户ID切分
from sklearn.model_selection import GroupShuffleSplit
gss = GroupShuffleSplit(n_splits=1, test_size=0.2)
train_idx, test_idx = next(gss.split(X, y, groups=df['user_id']))
```

### 陷阱3：单一指标评估

```python
# ❌ 只看Accuracy
print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")

# ✅ 多维度评估
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred, target_names=['Normal', 'Fraud']))
# 同时看precision, recall, f1 for每个类别
```

## 实战：正确的评估流程

```python
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import make_scorer, f1_score, precision_score, recall_score

# 定义多指标评估
scoring = {
    'f1': make_scorer(f1_score),
    'precision': make_scorer(precision_score),
    'recall': make_scorer(recall_score)
}

# 5折交叉验证
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_results = cross_validate(model, X, y, cv=skf, scoring=scoring, return_train_score=True)

# 输出结果
for metric in ['f1', 'precision', 'recall']:
    test_mean = cv_results[f'test_{metric}'].mean()
    test_std = cv_results[f'test_{metric}'].std()
    train_mean = cv_results[f'train_{metric}'].mean()
    print(f"{metric}: train={train_mean:.3f}, test={test_mean:.3f}±{test_std:.3f}")
    if train_mean - test_mean > 0.1:
        print(f"  ⚠️ 过拟合风险：训练-验证差距={train_mean-test_mean:.3f}")
```

## 今日要点

1. **准确率是最差的评估指标**——在类别不平衡时完全失效
2. **Precision vs Recall是业务决策**，不是技术选择——取决于FP和FN的代价
3. **交叉验证是标准评估方法**——分类用StratifiedKFold，时序用TimeSeriesSplit
4. **AUC度量排序能力**，但不直接对应业务指标
5. **测试集只能用一次**——在上面调参 = 浪费测试集

> 下一步：Day 6我们将学习sklearn Pipeline——让ML工作流可复现、可部署、防泄露。
