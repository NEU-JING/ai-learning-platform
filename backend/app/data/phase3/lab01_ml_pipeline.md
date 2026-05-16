# 实验1 - 端到端ML Pipeline：从CSV到预测

## 实验目标

构建一个完整的ML Pipeline，从原始CSV数据到可部署的预测模型。你将实践Day 1-3学到的所有知识：
- 问题建模与数据切分
- 数据预处理（缺失值、编码、标准化）
- 特征工程
- Pipeline构建（防止数据泄露）
- 模型训练与评估

## 数据集：客户流失预测

一个电信公司的客户数据，目标是预测客户是否会流失（churn）。

字段说明：
- `customer_id`: 客户ID（不作为特征）
- `tenure`: 在网月数
- `monthly_charges`: 月费用
- `total_charges`: 总费用
- `contract`: 合同类型（Month-to-month/One year/Two year）
- `payment_method`: 付款方式
- `internet_service`: 网络服务类型
- `senior_citizen`: 是否老年用户（0/1）
- `partner`: 是否有伴侣（Yes/No）
- `dependents`: 是否有家属（Yes/No）
- `churn`: 是否流失（目标变量，Yes/No）

## 任务要求

1. 实现数据加载和探索性分析
2. 实现数据预处理Pipeline
3. 实现特征工程
4. 训练模型并评估
5. 最终F1 score ≥ 0.60

## 提交方式

完善 `lab01_starter.py` 中的 TODO 部分，通过所有测试用例。
