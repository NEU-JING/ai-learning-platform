from datetime import datetime


class ETLPipeline:
    """ETL数据管道"""

    def __init__(self):
        self.log = []

    def _log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.append(f"[{timestamp}] {msg}")
        print(self.log[-1])

    # === Extract ===
    def extract_csv(self, filepath, **kwargs):
        """从CSV文件抽取数据"""
        # TODO: 读取CSV, 处理编码问题

    def extract_json(self, filepath, **kwargs):
        """从JSON文件抽取数据"""
        # TODO: 读取JSON, 处理嵌套结构

    def extract_excel(self, filepath, **kwargs):
        """从Excel文件抽取数据"""
        # TODO: 读取Excel, 处理多Sheet

    # === Validate ===
    def validate(self, df):
        """数据质量验证, 返回报告"""
        # TODO: 检查缺失值、重复值、数据类型、值域
        # 返回 {"total_rows": N, "null_counts": {...}, "duplicates": N, ...}

    # === Clean ===
    def clean(self, df, fillna=None, drop_duplicates=True, remove_outliers=None):
        """数据清洗"""
        # TODO: 1. 缺失值填充 2. 去重 3. 异常值处理

    # === Transform ===
    def transform(self, customers, transactions, products):
        """数据转换: 合并表 + 计算RFM特征"""
        # TODO:
        # 1. 合并三个DataFrame
        # 2. 计算RFM:
        #    - Recency: 距最近一次交易的天数
        #    - Frequency: 交易次数
        #    - Monetary: 总交易金额
        # 3. 添加客户等级标签

    # === Load ===
    def load(self, df, filepath):
        """加载数据到目标"""
        # TODO: 根据扩展名选择格式(csv/parquet/json)
