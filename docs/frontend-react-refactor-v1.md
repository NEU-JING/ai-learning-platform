# AILP 前端 React 重构设计文档 v1.0

> 基于 React 18 CDN 零构建方案，适配现有后端 API
> 日期：2026-05-19

---

## 1. 架构决策

### 1.1 技术栈确认

| 层级 | 选择 | 理由 |
|------|------|------|
| 框架 | React 18.3.1 (CDN) | 组件化、生态成熟、Agent友好 |
| 构建 | 零构建 (Babel Standalone) | 无Node依赖，即开即用 |
| 样式 | CSS Variables + BEM | 运行时主题切换，TweaksPanel兼容 |
| 路由 | 内存路由 (useState) | 极简，与TweaksPanel不冲突 |
| 状态 | useState + useContext | 够用，无需Redux |
| HTTP | Fetch API | 原生，无依赖 |

### 1.2 与现有架构对比

| 维度 | 现有(Vanilla) | 新方案(React) | 决策 |
|------|--------------|--------------|------|
| 组件化 | 模板字符串 | JSX | 升级 |
| 路由 | Hash Router | 内存路由 | 变更 |
| 状态 | Proxy Store | useState | 变更 |
| 样式 | spa.css | CSS Variables | 升级 |
| 调试 | 无 | TweaksPanel | 新增 |

---

## 2. 目录结构

```
frontend/
├── index.html              # 入口 + CDN加载
├── styles.css              # CSS Variables + 工具类
├── data.js                 # Adapter层 + Mock数据
├── icons.jsx               # SVG Icon组件
├── tweaks-panel.jsx        # 调试面板
├── nav.jsx                 # Topbar + MobileNav + CommandPalette
├── app.jsx                 # App Shell + 路由
├── adapters/
│   └── courseAdapter.js    # 后端字段映射
├── hooks/
│   └── useApi.js           # API请求Hook
├── screens/
│   ├── screen-home.jsx
│   ├── screen-courses.jsx
│   ├── screen-course-detail.jsx
│   ├── screen-chapter.jsx
│   ├── screen-lab.jsx
│   └── screen-progress.jsx
└── components/
    ├── Hero.jsx
    ├── CourseCard.jsx
    ├── ChapterList.jsx
    └── LabEditor.jsx
```

---

## 3. 后端适配层设计

### 3.1 字段映射表

| 前端字段 | 后端字段 | 处理方式 |
|---------|---------|---------|
| `chapters_total` | `chapters_count` | 直接映射 |
| `chapters_done` | 需计算 | 从`/progress`获取 |
| `lab_total` | 需计算 | chapters中type=lab计数 |
| `num` | `order_index` | 直接映射 |
| `duration` | `duration_minutes` | 直接映射 |
| `type` | `chapter_type` | 直接映射 |
| `status` | 需用户数据 | 从`/progress`获取 |
| `subtitle` | 缺失 | Mock数据填充 |
| `phase` | 缺失 | 从course_id推断 |
| `accent` | 缺失 | 默认值'indigo' |
| `icon` | `cover_image` | 映射或默认值 |
| `students` | 缺失 | Mock数据填充 |
| `rating` | 缺失 | Mock数据填充 |

### 3.2 Adapter实现

```javascript
// adapters/courseAdapter.js
const PHASE_MAP = {
  1: { title: 'Python快速通道', phase: 1, accent: 'indigo', icon: 'python' },
  2: { title: 'AI数学基础', phase: 2, accent: 'teal', icon: 'function' },
  3: { title: '机器学习核心', phase: 3, accent: 'indigo', icon: 'trending' },
  4: { title: '深度学习', phase: 4, accent: 'amber', icon: 'brain' },
  5: { title: 'LLM应用开发', phase: 5, accent: 'rose', icon: 'sparkles' },
  6: { title: 'AI工程化', phase: 6, accent: 'lime', icon: 'layers' },
};

export const adaptCourse = (backendCourse, progressData = null) => {
  const phaseInfo = PHASE_MAP[backendCourse.id] || { phase: 1, accent: 'indigo', icon: 'book' };
  
  return {
    id: backendCourse.id,
    title: backendCourse.title,
    subtitle: phaseInfo.title + (backendCourse.subtitle ? ` · ${backendCourse.subtitle}` : ''),
    description: backendCourse.description,
    phase: phaseInfo.phase,
    level: backendCourse.level,
    category: backendCourse.category,
    duration_hours: backendCourse.duration_hours,
    chapters_total: backendCourse.chapters_count,
    chapters_done: progressData?.completed_chapters || 0,
    lab_total: backendCourse.chapters?.filter(ch => ch.chapter_type === 'lab').length || 0,
    accent: phaseInfo.accent,
    icon: phaseInfo.icon,
    students: 8000 + backendCourse.id * 1000, // Mock统计数据
    rating: 4.7 + backendCourse.id * 0.05,    // Mock统计数据
    chapters: (backendCourse.chapters || []).map(adaptChapter),
  };
};

export const adaptChapter = (backendChapter, userProgress = null) => {
  const status = userProgress?.chapter_status?.[backendChapter.id] || 'not_started';
  
  return {
    id: backendChapter.id,
    num: backendChapter.order_index,
    title: backendChapter.title,
    duration: backendChapter.duration_minutes,
    type: backendChapter.chapter_type || 'text',
    status: status,
  };
};
```

---

## 4. API 层设计

### 4.1 端点映射

| 功能 | 前端调用 | 后端端点 | 状态 |
|------|---------|---------|------|
| 课程列表 | `GET /api/v1/courses/` | ✅ 已有 | 可用 |
| 课程详情 | `GET /api/v1/courses/{id}` | ✅ 已有 | 可用 |
| 章节列表 | `GET /api/v1/courses/{id}/chapters` | ✅ 已有 | 可用 |
| 章节详情 | `GET /api/v1/courses/chapters/{id}` | ✅ 已有 | 可用 |
| 实验详情 | `GET /api/v1/labs/{id}` | ✅ 已有 | 可用 |
| 提交代码 | `POST /api/v1/labs/{id}/submit` | ✅ 已有 | 可用 |
| 执行代码 | `POST /api/v1/labs/{id}/execute` | ✅ 已有 | 可用 |
| 用户进度 | `GET /api/v1/progress/` | ⚠️ 需确认 | 检查 |
| 当前学习 | `GET /api/v1/user/current` | ❌ 缺失 | Mock |

### 4.2 API Hook实现

```javascript
// hooks/useApi.js
const API_BASE = '/api/v1';

export const useApi = () => {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const fetchCourses = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/courses/`);
      const data = await res.json();
      return data.items || data; // 兼容分页和非分页
    } finally {
      setLoading(false);
    }
  };

  const fetchCourse = async (id) => {
    const res = await fetch(`${API_BASE}/courses/${id}`);
    return res.json();
  };

  const fetchProgress = async () => {
    try {
      const res = await fetch(`${API_BASE}/progress/`);
      return res.json();
    } catch {
      return { completed_chapters: [] }; // Fallback
    }
  };

  return { loading, error, fetchCourses, fetchCourse, fetchProgress };
};
```

---

## 5. 组件架构

### 5.1 组件层级

```
App
├── Topbar
│   ├── Brand
│   ├── Nav (home/courses/progress)
│   ├── SearchTrigger (⌘K)
│   └── UserMenu
├── Main (条件渲染 Screens)
│   ├── ScreenHome
│   │   ├── Hero
│   │   ├── ContinueCard
│   │   ├── LearningPath
│   │   └── CourseGrid
│   ├── ScreenCourses
│   │   ├── FilterBar
│   │   └── CourseCard × N
│   ├── ScreenCourseDetail
│   │   ├── CourseHeader
│   │   ├── ChapterList
│   │   └── Sidebar
│   ├── ScreenChapter
│   │   ├── ChapterNav
│   │   ├── ContentRenderer
│   │   └── TOC
│   ├── ScreenLab
│   │   ├── LabHeader
│   │   ├── CodeEditor
│   │   └── TestPanel
│   └── ScreenProgress
│       ├── StatsCards
│       └── ActivityTimeline
├── MobileNav
├── CommandPalette
└── TweaksPanel
```

### 5.2 关键组件接口

```javascript
// Hero组件
const Hero = ({ onNavigate, progress, layout }) => { ... };

// CourseCard组件
const CourseCard = ({ course, onOpen }) => { ... };

// ChapterList组件
const ChapterList = ({ chapters, currentId, onSelect }) => { ... };

// CodeEditor组件
const CodeEditor = ({ value, onChange, language }) => { ... };

// TestPanel组件
const TestPanel = ({ tests, running, onRun }) => { ... };
```

---

## 6. 主题系统设计

### 6.1 CSS Variables层级

```css
/* Layer 0: 基底 */
[data-theme="dark"] {
  --bg: #0a0b0d;
  --bg-1: #0f1115;
  --surface: #14171c;
  --fg: #e7e9ec;
  --fg-2: #b4b8bf;
  --line: rgba(255,255,255,0.06);
}

/* Layer 1: 品牌色 */
[data-brand="indigo"] {
  --brand: #818cf8;
  --brand-soft: rgba(129,140,248,0.12);
}

/* Layer 2: 密度 */
[data-density="compact"] { --pad: 12px; }
[data-density="spacious"] { --pad: 24px; }

/* Layer 3: 圆角 */
[data-corners="soft"] { --radius: 10px; }
```

### 6.2 TweaksPanel集成

```javascript
// useTweaks Hook
const useTweaks = (defaults) => {
  const [values, setValues] = React.useState(defaults);
  
  const setTweak = (key, val) => {
    setValues(prev => ({ ...prev, [key]: val }));
    // 同步到DOM
    document.documentElement.setAttribute(`data-${key}`, val);
  };
  
  return [values, setTweak];
};

// App中使用
const App = () => {
  const [tweaks, setTweak] = useTweaks({
    theme: 'dark',
    brand: 'indigo',
    density: 'standard',
    corners: 'soft',
  });
  
  return (
    <div className="app">
      {/* Screens */}
      <TweaksPanel values={tweaks} onChange={setTweak} />
    </div>
  );
};
```

---

## 7. 路由设计

### 7.1 路由表

| 路由 | 组件 | 参数 |
|------|------|------|
| `home` | ScreenHome | - |
| `courses` | ScreenCourses | - |
| `course` | ScreenCourseDetail | `{ id }` |
| `chapter` | ScreenChapter | `{ id }` |
| `lab` | ScreenLab | `{ id }` |
| `progress` | ScreenProgress | - |
| `discuss` | ScreenStub | - (P2) |

### 7.2 导航实现

```javascript
const App = () => {
  const [route, setRoute] = React.useState({ name: 'home', params: {} });
  
  const navigate = (name, params = {}) => {
    setRoute({ name, params });
    window.scrollTo({ top: 0, behavior: 'instant' });
  };
  
  return (
    <div className="app">
      <Topbar onNavigate={navigate} />
      <main>
        {route.name === 'home' && <ScreenHome onNavigate={navigate} />}
        {route.name === 'courses' && <ScreenCourses onNavigate={navigate} />}
        {/* ... */}
      </main>
    </div>
  );
};
```

---

## 8. Agent 开发任务拆分

### 8.1 里程碑规划

| 里程碑 | 内容 | 估算 | 依赖 |
|--------|------|------|------|
| M1 | 基础骨架 | 3h | - |
| M2 | 主题系统 | 2h | M1 |
| M3 | 导航系统 | 2h | M1 |
| M4 | 首页 | 3h | M2, M3 |
| M5 | 课程浏览 | 3h | M3 |
| M6 | 章节阅读 | 4h | M5 |
| M7 | 在线实验 | 4h | M5 |
| M8 | 学习进度 | 2h | M3 |
| M9 | 后端适配 | 3h | M4-M8 |
| M10 | 集成测试 | 2h | M9 |
| **总计** | | **~28h** | |

### 8.2 任务明细

#### M1: 基础骨架 (3h)

| 任务 | 产出 | 估算 |
|------|------|------|
| M1-1 | index.html + CDN配置 | 30min |
| M1-2 | styles.css (CSS Variables) | 1h |
| M1-3 | icons.jsx | 30min |
| M1-4 | 目录结构创建 | 15min |
| M1-5 | 基础工具类CSS | 45min |

#### M2: 主题系统 (2h)

| 任务 | 产出 | 估算 |
|------|------|------|
| M2-1 | tweaks-panel.jsx | 1h |
| M2-2 | useTweaks Hook | 30min |
| M2-3 | 主题切换演示 | 30min |

#### M3: 导航系统 (2h)

| 任务 | 产出 | 估算 |
|------|------|------|
| M3-1 | Topbar组件 | 45min |
| M3-2 | MobileNav组件 | 30min |
| M3-3 | CommandPalette组件 | 45min |

#### M4-M8: 屏幕组件 (各2-4h)

每个Screen包含：
- 页面结构
- 数据获取
- 交互逻辑
- 响应式适配

#### M9: 后端适配 (3h)

| 任务 | 产出 | 估算 |
|------|------|------|
| M9-1 | courseAdapter.js | 1h |
| M9-2 | chapterAdapter.js | 30min |
| M9-3 | useApi Hook | 1h |
| M9-4 | 联调测试 | 30min |

---

## 9. 验收标准

### 9.1 功能验收

- [ ] 6个Screen正常渲染
- [ ] 导航切换流畅
- [ ] TweaksPanel实时切换主题
- [ ] 课程数据从后端API获取
- [ ] Adapter正确映射字段
- [ ] 移动端响应式正常

### 9.2 性能验收

- [ ] 首屏加载 < 3s
- [ ] 路由切换无闪烁
- [ ] 主题切换无卡顿

### 9.3 兼容性验收

- [ ] Chrome/Edge/Firefox/Safari
- [ ] 移动端375px+正常

---

## 10. 风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| 后端字段缺失 | 数据显示异常 | Adapter层Mock填充 |
| API响应慢 | 体验差 | 添加loading状态 |
| Babel编译慢 | 首屏慢 | 生产环境切production.min.js |
| 移动端适配 | 布局错乱 | 优先测试375px断点 |

---

## 附录

### 参考文件

- zip原型: `/tmp/jing_extract/optimized/`
- 现有设计: `/root/workspace/ai-learning-platform/DESIGN.md`
- UX设计: `/root/workspace/ai-learning-platform/docs/ux-optimization-design.md`

### 关键决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 路由方案 | 内存路由 | 简单，与TweaksPanel兼容 |
| 状态管理 | useState | 够用，学习成本低 |
| 后端适配 | Adapter层 | 最小化后端改动 |
| 字段缺失 | Mock填充 | 不阻塞前端开发 |
