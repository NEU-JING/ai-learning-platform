/* Data layer — real API with mock fallback */

// ── API helpers ──────────────────────────────────────────
const API_BASE = '/api/v1';

async function fetchAPI(path) {
  try {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`API ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn(`[data] API fallback for ${path}:`, e.message);
    return null;
  }
}

// ── Maps ─────────────────────────────────────────────────
const LEVEL_MAP = {
  beginner: { label: '入门', color: 'var(--brand)' },
  intermediate: { label: '进阶', color: '#f5b342' },
  advanced: { label: '高级', color: '#fb7185' },
  expert: { label: '专家', color: '#a3e635' },
};

const CATEGORY_MAP = {
  python: 'Python',
  math: '数学',
  ml: '机器学习',
  dl: '深度学习',
  llm: '大语言模型',
  engineering: '工程化',
};

// ── Course loading ───────────────────────────────────────
async function loadCourses() {
  const data = await fetchAPI('/courses/');
  if (data?.items?.length) {
    return data.items.map(c => apiCourseToUI(c));
  }
  return MOCK_COURSES;
}

// ── Chapter loading ──────────────────────────────────────
async function loadChapter(chapterId) {
  const data = await fetchAPI(`/chapters/${chapterId}`);
  if (data) return apiChapterToUI(data);
  return MOCK_CHAPTER;
}

// ── Lab loading ──────────────────────────────────────────
async function loadLab(labId) {
  const data = await fetchAPI(`/labs/${labId}`);
  if (data) return apiLabToUI(data);
  return MOCK_LAB;
}

// ── Progress (mock only — no API yet) ────────────────────
const PROGRESS_STATS = {
  streak: 12,
  total_hours: 71.3,
  chapters_done: 25,
  chapters_total: 60,
  labs_done: 4,
  labs_total: 43,
  weekly_minutes: [22, 45, 30, 55, 70, 40, 65],
  overall_pct: 33,
};

// ── API → UI transforms ──────────────────────────────────
function apiCourseToUI(c) {
  const phase = c.order_index ?? c.id;
  const level = c.level || 'beginner';
  const categoryMap = { 1:'python', 2:'math', 3:'ml', 4:'dl', 5:'llm', 6:'engineering' };
  const accentMap = { 1:'indigo', 2:'teal', 3:'amber', 4:'rose', 5:'lime', 6:'indigo' };
  const iconMap = { 1:'python', 2:'sigma', 3:'brain', 4:'cpu', 5:'sparkles', 6:'terminal' };

  return {
    id: c.id,
    phase,
    title: c.title,
    subtitle: `Phase ${phase} · ${c.description?.substring(0, 30) || ''}`,
    description: c.description || '',
    level,
    category: categoryMap[c.id] || 'python',
    duration_hours: c.estimated_hours || 0,
    chapters_total: c.chapter_count || c.chapters?.length || 0,
    chapters_done: c.progress?.chapters_done || 0,
    lab_total: c.lab_count || c.labs?.length || 0,
    accent: accentMap[c.id] || 'indigo',
    icon: iconMap[c.id] || 'book',
    students: c.enrollment_count || 0,
    rating: c.rating || 4.8,
    chapters: (c.chapters || []).map(apiChapterBriefToUI),
    labs: (c.labs || []).map(apiLabBriefToUI),
  };
}

function apiChapterBriefToUI(ch) {
  return {
    id: ch.id,
    num: ch.order_index ?? ch.id,
    title: ch.title,
    duration: ch.estimated_minutes || 30,
    type: ch.is_lab ? 'lab' : 'text',
    status: ch.is_completed ? 'completed' : 'not_started',
  };
}

function apiLabBriefToUI(lab) {
  return {
    id: lab.id,
    title: lab.title,
    duration: lab.estimated_minutes || 60,
  };
}

function apiChapterToUI(ch) {
  return {
    id: ch.id,
    title: ch.title,
    course_id: ch.course_id,
    order_index: ch.order_index,
    sections: parseContentToSections(ch.content),
  };
}

function apiLabToUI(lab) {
  return {
    id: lab.id,
    title: lab.title,
    description: lab.description || '',
    starter_code: lab.starter_code || '',
    test_cases: lab.test_cases || [],
    time_limit: lab.time_limit_seconds || 30,
  };
}

function parseContentToSections(content) {
  if (!content) return [];
  // Simple h2-based section parser
  const lines = content.split('\n');
  const sections = [];
  let current = null;
  for (const line of lines) {
    const h2 = line.match(/^##\s+(.+)/);
    if (h2) {
      if (current) sections.push(current);
      current = { title: h2[1], content: '' };
    } else if (current) {
      current.content += line + '\n';
    }
  }
  if (current) sections.push(current);
  return sections.length ? sections : [{ title: '概述', content }];
}

// ── Mock data (fallback) ─────────────────────────────────
const CURRENT = {
  course_id: 3,
  chapter_id: 33,
  last_accessed: '2h',
};

const MOCK_COURSES = [
  { id:1, phase:1, title:"Python 快速通道", subtitle:"Phase 1 · 工程师必备", description:"从零到能写工程代码：语法 / 数据结构 / 函数式 / OOP / 异步 / 类型注解。", level:"beginner", category:"python", duration_hours:28, chapters_total:14, chapters_done:14, lab_total:2, accent:"indigo", icon:"python", students:12840, rating:4.8, chapters:[
    {id:11,num:1,title:"Python 基础语法",duration:25,type:"text",status:"completed"},{id:12,num:2,title:"数据结构与控制流",duration:30,type:"text",status:"completed"},{id:13,num:3,title:"函数式编程入门",duration:28,type:"text",status:"completed"},{id:14,num:4,title:"面向对象编程",duration:35,type:"text",status:"completed"},{id:15,num:5,title:"异常处理与文件 I/O",duration:22,type:"text",status:"completed"},{id:16,num:6,title:"模块与包管理",duration:25,type:"text",status:"completed"},{id:17,num:7,title:"装饰器与生成器",duration:38,type:"text",status:"completed"},{id:18,num:8,title:"类型注解与 mypy",duration:30,type:"text",status:"completed"},{id:19,num:9,title:"实验：CLI 工具",duration:60,type:"lab",status:"completed"},{id:110,num:10,title:"asyncio 异步编程",duration:42,type:"text",status:"completed"},{id:111,num:11,title:"上下文管理器",duration:18,type:"text",status:"completed"},{id:112,num:12,title:"实验：异步爬虫",duration:75,type:"lab",status:"completed"},{id:113,num:13,title:"包打包与发布",duration:26,type:"text",status:"completed"},{id:114,num:14,title:"工程化最佳实践",duration:22,type:"text",status:"completed"},
  ]},
  { id:2, phase:2, title:"AI 数学基础", subtitle:"Phase 2 · 为模型训练打好直觉", description:"向量空间、矩阵分解、梯度、概率分布、信息论。每个概念都配代码验证。", level:"beginner", category:"math", duration_hours:32, chapters_total:12, chapters_done:8, lab_total:2, accent:"teal", icon:"sigma", students:8920, rating:4.7, chapters:[
    {id:21,num:1,title:"向量与向量空间",duration:35,type:"text",status:"completed"},{id:22,num:2,title:"矩阵与线性变换",duration:40,type:"text",status:"completed"},{id:23,num:3,title:"特征值与 SVD",duration:45,type:"text",status:"completed"},{id:24,num:4,title:"梯度与 Jacobian",duration:38,type:"text",status:"completed"},{id:25,num:5,title:"概率与分布",duration:35,type:"text",status:"completed"},{id:26,num:6,title:"实验：概率模拟",duration:60,type:"lab",status:"completed"},{id:27,num:7,title:"信息论基础",duration:32,type:"text",status:"completed"},{id:28,num:8,title:"最优化入门",duration:38,type:"text",status:"completed"},{id:29,num:9,title:"实验：梯度下降",duration:90,type:"lab",status:"not_started"},{id:210,num:10,title:"贝叶斯思维",duration:35,type:"text",status:"not_started"},{id:211,num:11,title:"图论与网络",duration:30,type:"text",status:"not_started"},{id:212,num:12,title:"数学工具箱",duration:28,type:"text",status:"not_started"},
  ]},
  { id:3, phase:3, title:"机器学习核心", subtitle:"Phase 3 · 线性回归到 Boosting", description:"线性回归到 Boosting：每个算法都用 sklearn 训练 + 手写实现一次，再讲清楚什么时候用、什么时候不用。", level:"intermediate", category:"ml", duration_hours:48, chapters_total:14, chapters_done:3, lab_total:4, accent:"amber", icon:"brain", students:7610, rating:4.9, chapters:[
    {id:31,num:1,title:"监督学习 vs 无监督",duration:22,type:"text",status:"completed"},{id:32,num:2,title:"线性回归与正则化",duration:38,type:"text",status:"completed"},{id:33,num:3,title:"逻辑回归与分类",duration:35,type:"text",status:"completed"},{id:34,num:4,title:"决策树与随机森林",duration:40,type:"text",status:"not_started"},{id:35,num:5,title:"实验：信用卡欺诈检测",duration:90,type:"lab",status:"not_started"},{id:36,num:6,title:"支持向量机",duration:38,type:"text",status:"not_started"},{id:37,num:7,title:"集成学习与 XGBoost",duration:45,type:"text",status:"not_started"},{id:38,num:8,title:"K-Means 与层次聚类",duration:32,type:"text",status:"not_started"},{id:39,num:9,title:"降维：PCA / t-SNE",duration:36,type:"text",status:"not_started"},{id:310,num:10,title:"实验：Kaggle Titanic",duration:120,type:"lab",status:"not_started"},{id:311,num:11,title:"评估指标全解",duration:30,type:"text",status:"not_started"},{id:312,num:12,title:"超参调优与 AutoML",duration:35,type:"text",status:"not_started"},{id:313,num:13,title:"特征工程套路",duration:40,type:"text",status:"not_started"},{id:314,num:14,title:"实验：端到端 ML 流水线",duration:150,type:"lab",status:"not_started"},
  ]},
  { id:4, phase:4, title:"深度学习", subtitle:"Phase 4 · 从张量到 Transformer", description:"从张量到 Transformer。每一层都从零搭一遍，再用框架重写一遍，理解每个 API 背后在做什么。", level:"intermediate", category:"dl", duration_hours:52, chapters_total:13, chapters_done:0, lab_total:5, accent:"rose", icon:"cpu", students:5230, rating:4.8, chapters:[] },
  { id:5, phase:5, title:"LLM 应用开发", subtitle:"Phase 5 · Prompt Engineering 到 Agent", description:"从 Prompt Engineering 到生产级 Agent。RAG 检索增强、工具调用、多轮规划、评测体系。", level:"advanced", category:"llm", duration_hours:42, chapters_total:12, chapters_done:0, lab_total:4, accent:"lime", icon:"sparkles", students:4100, rating:4.9, chapters:[] },
  { id:6, phase:6, title:"AI 工程化与团队", subtitle:"Phase 6 · 把模型变成产品", description:"把模型变成产品：数据版本、实验追踪、CI/CD、A/B 测试、监控告警、团队协作。", level:"expert", category:"engineering", duration_hours:38, chapters_total:10, chapters_done:0, lab_total:3, accent:"indigo", icon:"terminal", students:2890, rating:4.7, chapters:[] },
];

const MOCK_CHAPTER = {
  id: 33, title: "逻辑回归与分类", course_id: 3,
  sections: [
    { title: "为什么不能直接用线性回归做分类？", content: "线性回归输出连续值，分类需要离散标签。Sigmoid 函数将输出映射到 [0,1] 区间。" },
    { title: "Sigmoid 函数", content: "σ(z) = 1 / (1 + e^(-z))，将任意实数映射到概率空间。" },
    { title: "损失函数：交叉熵", content: "L = -[y·log(ŷ) + (1-y)·log(1-ŷ)]，衡量预测概率与真实标签的差异。" },
    { title: "决策边界", content: "当 σ(w·x + b) = 0.5 时，w·x + b = 0 即为决策边界。" },
    { title: "本章小结", content: "逻辑回归是分类的基石，Sigmoid + 交叉熵的组合优雅且高效。" },
  ],
};

const MOCK_LAB = {
  id: 35, title: "实验：信用卡欺诈检测", description: "使用逻辑回归检测信用卡欺诈交易",
  starter_code: `import pandas as pd
# TODO: 读取 creditcard.csv
# TODO: 切分特征与标签
# TODO: 训练 / 测试集切分（注意类别不平衡）
# TODO: 训练模型
# TODO: 评估
`,
  test_cases: [
    { name: "数据加载", type: "output_match", function: "len", args: [["X_train"]], expected: "227845" },
    { name: "模型精度", type: "output_match", function: "round", args: [[0.87, 2]], expected: "0.87" },
  ],
  time_limit: 90,
};

export { loadCourses, loadChapter, loadLab, CURRENT, PROGRESS_STATS, LEVEL_MAP, CATEGORY_MAP, MOCK_COURSES, MOCK_CHAPTER, MOCK_LAB };
