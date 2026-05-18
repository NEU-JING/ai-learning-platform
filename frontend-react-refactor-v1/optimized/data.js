/* Mock course data — modeled on real Phase 1-6 structure */

const COURSES = [
  {
    id: 1,
    phase: 1,
    title: "Python 快速通道",
    subtitle: "Phase 1 · 工程师必备的 Python 子集",
    description: "从零到能写工程代码：语法 / 数据结构 / 函数式 / OOP / 异步 / 类型注解。聚焦 AI/ML 高频用法，跳过冷僻特性。",
    level: "beginner",
    category: "python",
    duration_hours: 28,
    chapters_total: 14,
    chapters_done: 14,
    lab_total: 2,
    accent: "indigo",
    icon: "python",
    students: 12840,
    rating: 4.8,
    chapters: [
      { id: 11, num: 1,  title: "Python 基础语法",         duration: 25, type: "text", status: "completed" },
      { id: 12, num: 2,  title: "数据结构与控制流",       duration: 30, type: "text", status: "completed" },
      { id: 13, num: 3,  title: "函数式编程入门",         duration: 28, type: "text", status: "completed" },
      { id: 14, num: 4,  title: "面向对象编程",           duration: 35, type: "text", status: "completed" },
      { id: 15, num: 5,  title: "异常处理与文件 I/O",     duration: 22, type: "text", status: "completed" },
      { id: 16, num: 6,  title: "模块与包管理",           duration: 25, type: "text", status: "completed" },
      { id: 17, num: 7,  title: "装饰器与生成器",         duration: 38, type: "text", status: "completed" },
      { id: 18, num: 8,  title: "类型注解与 mypy",        duration: 30, type: "text", status: "completed" },
      { id: 19, num: 9,  title: "实验：CLI 工具",         duration: 60, type: "lab",  status: "completed" },
      { id: 110, num: 10, title: "asyncio 异步编程",      duration: 42, type: "text", status: "completed" },
      { id: 111, num: 11, title: "上下文管理器",          duration: 18, type: "text", status: "completed" },
      { id: 112, num: 12, title: "实验：异步爬虫",        duration: 75, type: "lab",  status: "completed" },
      { id: 113, num: 13, title: "包打包与发布",          duration: 26, type: "text", status: "completed" },
      { id: 114, num: 14, title: "工程化最佳实践",        duration: 22, type: "text", status: "completed" },
    ],
  },
  {
    id: 2,
    phase: 2,
    title: "AI 数学基础",
    subtitle: "Phase 2 · 线性代数 / 微积分 / 概率",
    description: "为模型训练打好直觉：向量空间、矩阵分解、梯度、概率分布、信息论。每个概念都配代码验证。",
    level: "beginner",
    category: "math",
    duration_hours: 32,
    chapters_total: 12,
    chapters_done: 8,
    lab_total: 2,
    accent: "indigo",
    icon: "function",
    students: 9320,
    rating: 4.7,
    chapters: [
      { id: 21, num: 1,  title: "向量与矩阵运算",   duration: 35, type: "text", status: "completed" },
      { id: 22, num: 2,  title: "线性变换的几何直觉", duration: 40, type: "text", status: "completed" },
      { id: 23, num: 3,  title: "特征值与 SVD",     duration: 45, type: "text", status: "completed" },
      { id: 24, num: 4,  title: "实验：用 NumPy 实现 PCA", duration: 60, type: "lab",  status: "completed" },
      { id: 25, num: 5,  title: "导数与偏导",       duration: 28, type: "text", status: "completed" },
      { id: 26, num: 6,  title: "链式法则与反向传播", duration: 42, type: "text", status: "completed" },
      { id: 27, num: 7,  title: "概率与贝叶斯",     duration: 38, type: "text", status: "completed" },
      { id: 28, num: 8,  title: "信息论入门",       duration: 32, type: "text", status: "completed" },
      { id: 29, num: 9,  title: "梯度下降族",       duration: 35, type: "text", status: "in_progress" },
      { id: 210, num: 10, title: "凸优化基础",      duration: 30, type: "text", status: "not_started" },
      { id: 211, num: 11, title: "实验:手写梯度下降", duration: 75, type: "lab",  status: "not_started" },
      { id: 212, num: 12, title: "数值稳定性",       duration: 25, type: "text", status: "not_started" },
    ],
  },
  {
    id: 3,
    phase: 3,
    title: "机器学习核心",
    subtitle: "Phase 3 · 经典算法 / 评估 / 调优",
    description: "线性回归到 Boosting：每个算法都用 sklearn 训练 + 手写实现一次，再讲清楚什么时候用、什么时候不用。",
    level: "intermediate",
    category: "ml",
    duration_hours: 48,
    chapters_total: 14,
    chapters_done: 3,
    lab_total: 4,
    accent: "indigo",
    icon: "trending",
    students: 7610,
    rating: 4.9,
    chapters: [
      { id: 31, num: 1, title: "监督学习 vs 无监督", duration: 22, type: "text", status: "completed" },
      { id: 32, num: 2, title: "线性回归与正则化", duration: 38, type: "text", status: "completed" },
      { id: 33, num: 3, title: "逻辑回归与分类",   duration: 35, type: "text", status: "in_progress" },
      { id: 34, num: 4, title: "决策树与随机森林", duration: 40, type: "text", status: "not_started" },
      { id: 35, num: 5, title: "实验：信用卡欺诈检测", duration: 90, type: "lab", status: "not_started" },
      { id: 36, num: 6, title: "支持向量机",       duration: 38, type: "text", status: "not_started" },
      { id: 37, num: 7, title: "集成学习与 XGBoost", duration: 45, type: "text", status: "not_started" },
      { id: 38, num: 8, title: "K-Means 与层次聚类", duration: 32, type: "text", status: "not_started" },
      { id: 39, num: 9, title: "降维：PCA / t-SNE", duration: 36, type: "text", status: "not_started" },
      { id: 310, num: 10, title: "实验：Kaggle Titanic", duration: 120, type: "lab", status: "not_started" },
      { id: 311, num: 11, title: "评估指标全解",   duration: 30, type: "text", status: "not_started" },
      { id: 312, num: 12, title: "超参调优与 AutoML", duration: 35, type: "text", status: "not_started" },
      { id: 313, num: 13, title: "特征工程套路",   duration: 40, type: "text", status: "not_started" },
      { id: 314, num: 14, title: "实验：端到端 ML 流水线", duration: 150, type: "lab", status: "not_started" },
    ],
  },
  {
    id: 4,
    phase: 4,
    title: "深度学习",
    subtitle: "Phase 4 · PyTorch / CNN / Transformer",
    description: "从张量到 Transformer。每一层都从零搭一遍，再用框架重写一遍，理解每个 API 背后在做什么。",
    level: "intermediate",
    category: "dl",
    duration_hours: 52,
    chapters_total: 13,
    chapters_done: 0,
    lab_total: 5,
    accent: "indigo",
    icon: "brain",
    students: 6240,
    rating: 4.9,
    chapters: [],
  },
  {
    id: 5,
    phase: 5,
    title: "LLM 应用开发",
    subtitle: "Phase 5 · Prompt / RAG / Agent",
    description: "从 Prompt Engineering 到生产级 Agent。RAG 检索增强、工具调用、多轮规划、评测体系。",
    level: "advanced",
    category: "llm",
    duration_hours: 42,
    chapters_total: 12,
    chapters_done: 0,
    lab_total: 4,
    accent: "indigo",
    icon: "sparkles",
    students: 8910,
    rating: 4.9,
    chapters: [],
  },
  {
    id: 6,
    phase: 6,
    title: "AI 工程化与团队",
    subtitle: "Phase 6 · MLOps / 部署 / Leader",
    description: "把模型变成产品：数据版本、实验追踪、CI/CD、A/B 测试、监控告警、团队协作。",
    level: "expert",
    category: "engineering",
    duration_hours: 38,
    chapters_total: 10,
    chapters_done: 0,
    lab_total: 3,
    accent: "indigo",
    icon: "layers",
    students: 3120,
    rating: 4.8,
    chapters: [],
  },
];

// Currently-reading focus
const CURRENT = {
  course_id: 3,
  chapter_id: 33, // 逻辑回归与分类
  resumed_at: "2 小时前",
};

// Sample chapter content (Markdown-like) for the 章节阅读 screen
const SAMPLE_CHAPTER = {
  id: 33,
  course_id: 3,
  course_title: "机器学习核心",
  num: 3,
  title: "逻辑回归与分类",
  duration: 35,
  total: 14,
  blocks: [
    { type: "h2", text: "为什么不能直接用线性回归做分类？" },
    { type: "p", text: "线性回归输出的是连续实数，可以是 -∞ 到 +∞ 的任何值。但分类问题需要的是「这个样本属于第 1 类的概率」——一个 [0, 1] 区间内的数字。" },
    { type: "p", text: "如果硬塞，会有两个问题：第一，预测值会跑出 [0, 1];第二，对极端样本极度敏感——一个离群点能把决策边界拉偏。" },
    { type: "callout", tone: "info", title: "核心直觉",
      text: "逻辑回归 = 线性回归 + Sigmoid 压缩。前半段还是 wx+b 的线性组合，后半段套一个 σ(z) 把它压回 (0, 1)。" },
    { type: "h2", text: "Sigmoid 函数" },
    { type: "p", text: "数学表达：σ(z) = 1 / (1 + e^(-z))。当 z=0 时输出 0.5；z 越大越接近 1；z 越小越接近 0。这正好是「概率」需要的形状。" },
    { type: "code", lang: "python", code:
`import numpy as np

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

# 直觉验证
print(sigmoid(0))      # 0.5
print(sigmoid(10))     # 0.9999...
print(sigmoid(-10))    # 0.0000...` },
    { type: "h2", text: "损失函数：交叉熵" },
    { type: "p", text: "如果继续用均方误差，会得到一个非凸的损失曲面，梯度下降很容易卡进局部最小值。所以我们换成 log-likelihood 推导出的交叉熵损失。" },
    { type: "code", lang: "python", code:
`def cross_entropy(y_true, y_pred):
    eps = 1e-9  # 防止 log(0)
    return -np.mean(
        y_true * np.log(y_pred + eps) +
        (1 - y_true) * np.log(1 - y_pred + eps)
    )` },
    { type: "callout", tone: "warn", title: "易踩坑",
      text: "实际项目里千万别自己写 sigmoid + log，会有数值溢出。直接用框架的 BCEWithLogitsLoss 或 sklearn 的 LogisticRegression。" },
    { type: "h2", text: "决策边界" },
    { type: "p", text: "训练完拿到 w 和 b，预测时算 σ(wx+b)。约定 ≥ 0.5 判为正类——这等价于 wx+b ≥ 0，所以决策边界就是 wx+b = 0 这个超平面。" },
    { type: "h2", text: "本章小结" },
    { type: "list", items: [
      "逻辑回归通过 Sigmoid 把线性输出压缩成概率",
      "用交叉熵而非 MSE，避免非凸优化问题",
      "决策边界本质仍是线性的——线性不可分时需换模型",
      "下一章会扩展到多分类（Softmax）",
    ] },
  ],
  toc: [
    { id: "s1", text: "为什么不能直接用线性回归做分类？", level: 2 },
    { id: "s2", text: "Sigmoid 函数", level: 2 },
    { id: "s3", text: "损失函数：交叉熵", level: 2 },
    { id: "s4", text: "决策边界", level: 2 },
    { id: "s5", text: "本章小结", level: 2 },
  ],
};

// Sample lab data
const SAMPLE_LAB = {
  id: 35,
  chapter_id: 35,
  course_title: "机器学习核心",
  title: "实验：信用卡欺诈检测",
  description: "使用 Kaggle 的 creditcard.csv（高度不平衡，欺诈样本仅 0.17%），训练一个分类器，要求 Recall ≥ 0.85 同时 Precision ≥ 0.70。",
  difficulty: "中等",
  duration: 90,
  hints: [
    "数据集极度不平衡——直接训练会得到全 0 预测",
    "考虑 class_weight='balanced'、SMOTE 重采样、或调整决策阈值",
    "评估时关注 PR-AUC 而非 ROC-AUC",
  ],
  tests: [
    { name: "test_data_loaded",     desc: "正确加载数据集，shape (284807, 31)", status: "pass", time: 120 },
    { name: "test_train_test_split", desc: "保持类别比例的 stratified split",   status: "pass", time: 45 },
    { name: "test_model_trained",   desc: "模型已 fit 且无报错",               status: "pass", time: 2840 },
    { name: "test_recall_threshold", desc: "Recall ≥ 0.85",                    status: "pass", time: 320 },
    { name: "test_precision_threshold", desc: "Precision ≥ 0.70",              status: "fail", time: 180, error: "AssertionError: 0.642 < 0.70" },
    { name: "test_no_data_leakage", desc: "测试集未在训练前接触过 scaler",      status: "pending" },
  ],
  starter: `import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# TODO: 读取 creditcard.csv
df = pd.read_csv("creditcard.csv")

# TODO: 切分特征与标签
X = df.drop("Class", axis=1)
y = df["Class"]

# TODO: 训练 / 测试集切分（注意类别不平衡）
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# TODO: 训练模型
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# TODO: 评估
y_pred = model.predict(X_test)
`,
};

// Progress data for dashboard
const PROGRESS_STATS = {
  streak_days: 12,
  total_minutes: 4280,
  chapters_completed: 25,
  labs_completed: 4,
  courses_active: 3,
  weekly: [22, 45, 30, 55, 70, 40, 65], // last 7 days minutes
  recent: [
    { kind: "chapter", title: "逻辑回归与分类",   course: "机器学习核心",   when: "2 小时前",  progress: 45 },
    { kind: "lab",     title: "用 NumPy 实现 PCA", course: "AI 数学基础",   when: "昨天",      score: 92 },
    { kind: "chapter", title: "信息论入门",       course: "AI 数学基础",   when: "昨天",      progress: 100 },
    { kind: "chapter", title: "概率与贝叶斯",     course: "AI 数学基础",   when: "2 天前",    progress: 100 },
    { kind: "lab",     title: "异步爬虫",         course: "Python 快速通道", when: "5 天前",  score: 88 },
  ],
};

const LEVEL_MAP = {
  beginner:     { text: "入门", color: "var(--ok)" },
  intermediate: { text: "进阶", color: "var(--brand)" },
  advanced:     { text: "高级", color: "var(--warn)" },
  expert:       { text: "专家", color: "var(--err)" },
};

const CATEGORY_MAP = {
  python: "Python",
  math: "数学",
  ml: "机器学习",
  dl: "深度学习",
  llm: "大语言模型",
  engineering: "工程化",
};

Object.assign(window, { COURSES, CURRENT, SAMPLE_CHAPTER, SAMPLE_LAB, PROGRESS_STATS, LEVEL_MAP, CATEGORY_MAP });
