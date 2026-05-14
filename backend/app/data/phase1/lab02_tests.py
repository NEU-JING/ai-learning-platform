import sys
sys.path.insert(0, '.')
import pandas as pd
import numpy as np
from pathlib import Path

# 创建测试数据
customers = pd.DataFrame({
    'customer_id': range(1, 11),
    'name': [f'Customer_{i}' for i in range(1, 11)],
    'email': [f'user{i}@test.com' if i % 3 != 0 else None for i in range(1, 11)],
    'age': [25, 30, 35, 200, 28, 32, 40, 29, 33, 45],  # 200 is outlier
    'segment': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
})

transactions = pd.DataFrame({
    'transaction_id': range(1, 21),
    'customer_id': [i % 10 + 1 for i in range(20)],
    'product_id': [i % 5 + 1 for i in range(20)],
    'amount': [100 * (i + 1) for i in range(20)],
    'date': pd.date_range('2024-01-01', periods=20, freq='5D')
})

products = pd.DataFrame({
    'product_id': range(1, 6),
    'product_name': [f'Product_{i}' for i in range(1, 6)],
    'category': ['Electronics', 'Books', 'Electronics', 'Clothing', 'Books']
})

pipeline = ETLPipeline()

# === 测试1: Validate ===
report = pipeline.validate(customers)
assert report['total_rows'] == 10, f"期望10行, 得到{report['total_rows']}"
assert 'null_counts' in report, "报告应包含null_counts"
assert report['null_counts']['email'] == 3, f"email缺失应为3, 得到{report['null_counts'].get('email', 0)}"
print("测试1: 数据验证 PASSED")

# === 测试2: Clean - 缺失值填充 ===
cleaned = pipeline.clean(customers, fillna={'email': 'unknown@test.com'})
assert cleaned['email'].isnull().sum() == 0, "填充后不应有缺失值"
print("测试2.1: 缺失值填充 PASSED")

# === 测试3: Clean - 异常值处理 ===
cleaned = pipeline.clean(customers, fillna={'email': 'unknown@test.com'}, 
                         remove_outliers={'age': (0, 120)})
assert cleaned['age'].max() <= 120, f"异常值应被处理, max={cleaned['age'].max()}"
assert len(cleaned) == 9, f"异常值行应被删除, 剩余{len(cleaned)}行"
print("测试2.2: 异常值处理 PASSED")

# === 测试4: Clean - 去重 ===
dup_customers = pd.concat([customers, customers.iloc[[0]]], ignore_index=True)
assert len(dup_customers) == 11
cleaned = pipeline.clean(dup_customers, drop_duplicates=True)
assert len(cleaned) == 10, f"去重后应为10行, 得到{len(cleaned)}"
print("测试2.3: 去重 PASSED")

# === 测试5: Transform ===
enriched = pipeline.transform(customers, transactions, products)
assert 'recency' in enriched.columns or 'Recency' in enriched.columns, "应包含Recency特征"
assert 'frequency' in enriched.columns or 'Frequency' in enriched.columns, "应包含Frequency特征"
assert 'monetary' in enriched.columns or 'Monetary' in enriched.columns, "应包含Monetary特征"
print("测试3: RFM特征计算 PASSED")

# === 测试6: Load CSV ===
import tempfile, os
with tempfile.TemporaryDirectory() as tmpdir:
    outpath = os.path.join(tmpdir, 'output.csv')
    pipeline.load(enriched, outpath)
    assert os.path.exists(outpath), "输出文件应存在"
    loaded = pd.read_csv(outpath)
    assert len(loaded) > 0, "加载后应有数据"
    print("测试4: 数据加载CSV PASSED")

print("所有测试通过!")
