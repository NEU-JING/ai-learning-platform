# 实验2: ETL项目实战——从API到数据仓库

## 实验目标
构建一个完整的ETL(Extract-Transform-Load)Pipeline, 将多个数据源清洗、转换后加载到分析就绪的格式。这是数据工程师的日常, 也是AI项目的数据准备基础。

## 背景
你是一家金融科技公司的数据工程师, 需要从以下数据源构建客户画像:
1. 客户基础信息(CSV文件)
2. 交易记录(JSON API)
3. 产品信息(Excel文件)

需要完成: 数据抽取 -> 质量检查 -> 清洗转换 -> 特征计算 -> 加载输出。

## 需求规格

实现一个`ETLPipeline`类, 包含以下方法:

```python
pipeline = ETLPipeline()

# 1. 抽取
customers = pipeline.extract_csv("customers.csv")
transactions = pipeline.extract_json("transactions.json")  
products = pipeline.extract_excel("products.xlsx")

# 2. 验证(返回数据质量报告)
report = pipeline.validate(customers)
# {"total_rows": 1000, "null_counts": {"email": 50, "phone": 120}, "duplicates": 3}

# 3. 清洗
clean = pipeline.clean(customers, 
    fillna={"email": "unknown", "phone": "N/A"},
    drop_duplicates=True,
    remove_outliers={"age": (0, 120)})

# 4. 转换
enriched = pipeline.transform(clean, transactions, products)
# 合并三个表, 计算RFM特征(Recency/Frequency/Monetary)

# 5. 加载
pipeline.load(enriched, "output/customer_profiles.csv")
```

## 入门代码
在实验编辑器中完成实现。请确保所有测试用例通过。
