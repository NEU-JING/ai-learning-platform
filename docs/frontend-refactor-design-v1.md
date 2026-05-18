# JING AI 学习平台 · 前端重构设计文档 v1.0

> 基于 React 18 CDN 零构建方案，从 `/tmp/jing_extract/optimized/` 原型反推正式工程化设计。
> 日期：2026-05-19

---

## 1. 技术选型决策

### 1.1 核心约束

| 约束 | 说明 |
|------|------|
| 零构建 | 不使用 Webpack/Vite/esbuild，所有 JSX 由浏览器端 Babel Standalone 实时编译 |
| CDN 加载 | React 18.3.1 + Babel 7.29.0 通过 unpkg CDN 引入，SRI 完整性校验 |
| 单页应用 | 纯前端路由（hash-based），无服务端渲染 |
| 即时调试 | TweaksPanel 实时调整主题/布局参数，`useTweaks` Hook 驱动 |

### 1.2 选型对比与决策理由

| 选项 | 优势 | 劣势 | 决策 |
|------|------|------|------|
| React 18 CDN + Babel Standalone | 零配置、即开即用、原型→生产无缝 | 无 Tree-shaking、首屏慢~200ms（Babel 编译） | **选用** — 匹配零构建约束 |
| React + Vite/Webpack | HMR、Tree-shaking、生产优化 | 需 Node.js 工具链、构建配置复杂 | 否 — 违反零构建约束 |
| Vue 3 CDN | 模板编译更轻 | 团队技术栈偏 React | 否 — 技术栈不匹配 |
| 原生 Web Components | 零依赖 | 状态管理原始、组件生态弱 | 否 — 开发效率低 |
| Preact CDN | 体积极小（3KB） | 生态兼容性差、Hooks 行为微差 | 备选 — 如需优化首屏可切换 |

### 1.3 关键依赖版本

```
react@18.3.1           (UMD development)
react-dom@18.3.1       (UMD development)
@babel/standalone@7.29.0 (浏览器端 JSX 编译)
Google Fonts: Inter + JetBrains Mono
```

> 生产环境建议切换至 `react.production.min.js` + `react-dom.production.min.js`，Babel 预编译可选但当前阶段不强制。

---

## 2. 项目结构设计

### 2.1 文件拓扑

```
frontend/
├── index.html                 # 入口 HTML（CDN 加载 + 组件脚本引用）
├── styles.css                 # 全局设计令牌 + 布局 + 组件样式
├── data.js                    # Mock 数据层（纯 JS，Object.assign→window）
├── icons.jsx                  # SVG Icon 系统（Lucide 风格）
├── tweaks-panel.jsx           # 调试面板（useTweaks + 通用控件）
├── nav.jsx                    # Topbar / MobileNav / CommandPalette
├── screen-home.jsx            # 01 首页
├── screen-courses.jsx         # 02 课程列表
├── screen-course-detail.jsx   # 03 课程详情
├── screen-chapter.jsx         # 04 章节阅读
├── screen-lab.jsx             # 05 在线实验
├── screen-progress.jsx        # 06 学习进度
└── app.jsx                    # App Shell（路由 + 主题 + TweaksPanel 接线）
```

### 2.2 加载顺序（关键）

HTML 中 `<script type="text/babel">` 按依赖拓扑排列，**顺序不可乱**：

```
1. data.js          → 纯 JS，无依赖，注入 window.COURSES 等
2. icons.jsx        → 依赖 React（CDN），注入 window.Icon
3. tweaks-panel.jsx → 依赖 React + Icon，注入 window.useTweaks / TweaksPanel 等
4. nav.jsx          → 依赖 Icon / COURSES，注入 Topbar / MobileNav / CommandPalette
5. screen-*.jsx     → 依赖 Icon / data / TweaksPanel
6. app.jsx          → 依赖所有组件，最终 render
```

### 2.3 模块通信机制

CDN 方案无 ES Modules，组件通过 `window` 全局注册/消费：

```javascript
// 注册方（每个文件底部）
Object.assign(window, { ScreenHome, CourseCard });

// 消费方（直接引用 window 上的全局变量）
const ScreenHome = window.ScreenHome;  // 隐式，JSX 中直接用 <ScreenHome>
```

> **风险**：命名冲突。缓解措施：所有组件使用 PascalCase 且前缀 Screen/Card/List 等语义化命名。

---

## 3. 组件架构设计

### 3.1 组件层级图

```
App
├── Topbar
│   ├── Brand (brand-mark + title)
│   ├── Nav (tab links)
│   ├── SearchTrigger
│   ├── IconButton (notifications)
│   └── Avatar
├── <main> — Screen Router
│   ├── ScreenHome
│   │   ├── Hero (centered | split layout)
│   │   │   ├── HeroStats
│   │   │   └── HeroVisual (mini code editor mock)
│   │   ├── ContinueCard
│   │   ├── LearningPath (6 Phase cards)
│   │   └── CourseCard[] (recommended)
│   ├── ScreenCourses
│   │   ├── FilterGroup[] (level, category)
│   │   ├── CourseCard[] (grid view)
│   │   └── CourseRow[] (list view)
│   ├── ScreenCourseDetail
│   │   ├── Breadcrumb
│   │   ├── ChapterListPanel
│   │   │   ├── FilterGroup (all/unread/lab)
│   │   │   └── ChapterItem[]
│   │   ├── CourseProgressCard (sidebar)
│   │   ├── CourseFactsCard (sidebar)
│   │   └── CourseInstructorCard (sidebar)
│   ├── ScreenChapter
│   │   ├── StickyBreadcrumb + ProgressBar
│   │   ├── ChapterSidebar (TOC + chapters tabs)
│   │   ├── ChapterHeader
│   │   ├── Block[] (h2/p/code/callout/list renderer)
│   │   ├── LabEntryCard
│   │   ├── NavCard[] (prev/next)
│   │   ├── FeedbackStrip
│   │   └── MobileDrawer
│   ├── ScreenLab
│   │   ├── LabHeader
│   │   ├── LabBriefPanel (left sidebar)
│   │   ├── CodeEditor (textarea-based)
│   │   ├── ResultPanel
│   │   │   ├── TestsList
│   │   │   ├── OutputView
│   │   │   └── ConsoleView
│   │   └── AIAssistant (slide-over panel)
│   └── ScreenProgress
│       ├── StatCard[] (4-grid)
│       ├── ActivityChart (bar chart)
│       ├── PathOverview (circular progress SVG)
│       ├── CourseProgressList
│       └── RecentActivity
├── MobileNav (bottom tab bar, <720px)
├── CommandPalette (⌘K search overlay)
└── TweaksPanel
    ├── TweakSection
    ├── TweakRadio (segmented control)
    ├── TweakColor (palette chips)
    ├── TweakSlider
    ├── TweakToggle
    ├── TweakNumber (scrub input)
    ├── TweakSelect
    ├── TweakText
    └── TweakButton
```

### 3.2 组件分类

| 类别 | 组件 | 职责 |
|------|------|------|
| **Shell** | App, Topbar, MobileNav | 应用外壳、导航框架 |
| **Screen** | Screen* (6个) | 页面级路由容器 |
| **Layout** | Hero, ChapterSidebar, LabBriefPanel, ResultPanel | 页面内区域布局 |
| **Card** | CourseCard, ContinueCard, StatCard, NavCard, ChapterItem | 可复用卡片单元 |
| **Overlay** | CommandPalette, AIAssistant, MobileDrawer, TweaksPanel | 浮层/抽屉 |
| **Primitive** | Icon, Block, FilterGroup, Tweak* | 最小功能单元 |

### 3.3 Props 设计模式

所有组件遵循统一 Props 约定：

```typescript
// 路由回调：统一签名
onNavigate: (screenName: string, params?: object) => void

// 数据注入：父组件查数据，子组件只渲染
course: Course        // 完整对象，非 ID
chapter: Chapter

// 状态控制：受控 vs 非受控
value + onChange      // 受控（TweaksPanel 控件）
内部 useState          // 非受控（Screen 级 UI 状态）
```

---

## 4. 主题系统设计

### 4.1 CSS Variables 架构

主题系统通过 HTML 元素上的 `data-*` 属性驱动 CSS 变量切换，**无 JS 运行时开销**：

```css
/* 四维控制轴 */
<html data-theme="dark|light"    →  颜色明暗
       data-brand="indigo|teal|amber|rose|lime"  →  品牌色
       data-density="compact|standard|spacious"   →  间距密度
       data-corners="square|soft|pill"            →  圆角风格
```

### 4.2 令牌分层

```
Layer 0: 基底 (bg, fg, line)          — 主题切换重置
Layer 1: 语义 (brand, ok, warn, err)  — 功能语义不变
Layer 2: 复合 (brand-soft, brand-ink) — 品牌色派生
Layer 3: 组件 (card, btn, tag)        — 消费 Layer 0-2
```

#### 核心变量清单（暗色默认）

| 变量 | 值 | 用途 |
|------|------|------|
| `--bg` | `#0a0b0d` | 页面底色 |
| `--bg-1` | `#0f1115` | 次级底色 |
| `--surface` | `#14171c` | 卡片/面板 |
| `--surface-2` | `#1a1e25` | Hover 态 |
| `--surface-3` | `#20252e` | 进度条底色 |
| `--line` | `rgba(255,255,255,0.06)` | 1级描边 |
| `--line-2` | `rgba(255,255,255,0.10)` | 2级描边 |
| `--fg` | `#e7e9ec` | 主文字 |
| `--fg-2` | `#b4b8bf` | 次文字 |
| `--fg-3` | `#7c828a` | 辅助文字 |
| `--fg-4` | `#535860` | 最淡文字 |
| `--brand` | `#818cf8` | 品牌色（indigo） |
| `--brand-soft` | `rgba(129,140,248,0.12)` | 品牌底色 |
| `--ok` | `#4ade80` | 成功 |
| `--warn` | `#fbbf24` | 警告 |
| `--err` | `#f87171` | 错误 |
| `--code-bg` | `#0c0e12` | 代码块底色 |

### 4.3 品牌色系统

5 套品牌色通过 `[data-brand]` 选择器切换，每套提供 3 个派生值：

```
brand     → 主色（按钮、进度条、高亮）
brand-2   → 深色变体（按钮边框、渐变终点）
brand-soft → 12% 透明底（背景高亮、Tag底色）
brand-soft-2 → 22% 透明底（Hover、Active态）
```

| 品牌 | brand | brand-2 |
|------|-------|---------|
| indigo | `#818cf8` | `#6366f1` |
| teal | `#2dd4bf` | `#14b8a6` |
| amber | `#f5b342` | `#d99633` |
| rose | `#fb7185` | `#e11d48` |
| lime | `#a3e635` | `#84cc16` |

### 4.4 密度与圆角

```css
/* 密度控制行高和卡片内边距 */
[data-density="compact"]   { --row-h: 36px; --pad-card: 14px; }
[data-density="standard"]  { --row-h: 44px; --pad-card: 20px; }
[data-density="spacious"]  { --row-h: 52px; --pad-card: 28px; }

/* 圆角控制所有 radius 变量 */
[data-corners="square"] { --radius-sm: 2px;  --radius: 4px;  --radius-lg: 6px;  --radius-xl: 8px; }
[data-corners="soft"]   { --radius-sm: 6px;  --radius: 10px; --radius-lg: 14px; --radius-xl: 20px; }
[data-corners="pill"]   { --radius-sm: 999px; --radius: 999px; --radius-lg: 16px; --radius-xl: 24px; }
```

### 4.5 亮色模式

`[data-theme="light"]` 覆盖 Layer 0 变量，Layer 1-3 自动适配：

```
--bg: #f8f8f6 → --surface: #ffffff → --fg: #1c1e22
```

品牌色在亮色模式下 `brand-soft` 透明度略降（10%/18%），避免过于饱和。

### 4.6 主题切换实现

```javascript
// App.jsx — useEffect 同步到 DOM
useEffect(() => {
  const el = document.documentElement;
  el.setAttribute("data-theme",   t.theme);
  el.setAttribute("data-brand",   t.brand);
  el.setAttribute("data-density", t.density);
  el.setAttribute("data-corners", t.corners);
}, [t.theme, t.brand, t.density, t.corners]);
```

**零 JS 运行时**：CSS Variables 在浏览器层直接切换，无需 React re-render 组件树。

---

## 5. 路由系统设计

### 5.1 路由模型

```javascript
// 状态驱动，非 URL 驱动
const [route, setRoute] = useState({ name: "home", params: {} });

const navigate = (name, params = {}) => {
  setRoute({ name, params });
  window.scrollTo({ top: 0, behavior: "instant" });
};
```

### 5.2 路由表

| name | params | Screen | 导航入口 |
|------|--------|--------|----------|
| `home` | — | ScreenHome | Topbar "首页" |
| `courses` | — | ScreenCourses | Topbar "课程" |
| `course` | `{ id }` | ScreenCourseDetail | 课程卡片 |
| `chapter` | `{ id }` | ScreenChapter | 章节列表项 |
| `lab` | `{ id }` | ScreenLab | 实验章节项 |
| `progress` | — | ScreenProgress | Topbar "进度" |
| `discuss` | — | ScreenStub | Topbar "讨论区" |

### 5.3 路由匹配

```jsx
// 条件渲染，非组件化路由
{route.name === "home"     && <ScreenHome onNavigate={navigate} tweaks={t} />}
{route.name === "courses"  && <ScreenCourses onNavigate={navigate} />}
{route.name === "course"   && <ScreenCourseDetail params={route.params} onNavigate={navigate} />}
// ...
```

### 5.4 URL 同步（待实现）

当前原型不与浏览器 URL 同步，刷新丢失路由状态。演进方案：

| 阶段 | 方案 | 复杂度 |
|------|------|--------|
| MVP | 纯状态路由（当前） | ★☆☆ |
| V1.1 | `window.location.hash` 同步 | ★★☆ |
| V2 | `popstate` + history API | ★★★ |

**推荐 V1.1**：`navigate` 时写 `location.hash`，App mount 时读 hash 恢复路由，约 20 行代码。

### 5.5 Topbar 导航高亮

```javascript
// 子路由映射到父 Tab
const active = route.name === "course" ? "courses"
             : route.name === "chapter" ? "courses"
             : route.name === "lab" ? "courses"
             : route.name;
```

---

## 6. 数据流设计

### 6.1 数据流全景

```
┌─────────────────────────────────────────────────┐
│                    App                          │
│  ┌──────────┐   ┌────────────┐   ┌──────────┐  │
│  │  route   │   │   tweaks   │   │ search   │  │
│  │ useState │   │ useTweaks  │   │ useState │  │
│  └────┬─────┘   └─────┬──────┘   └────┬─────┘  │
│       │               │               │         │
│       ▼               ▼               ▼         │
│  ┌─────────────────────────────────────────┐    │
│  │           Screen (props drilling)       │    │
│  │  onNavigate  tweaks  params            │    │
│  └──────────────┬──────────────────────────┘    │
│                 │                                │
│                 ▼                                │
│  ┌──────────────────────────────────────────┐   │
│  │         Component (local state)          │   │
│  │  ScreenCourses: level, category, view    │   │
│  │  ScreenLab: code, tab, running, results  │   │
│  │  ScreenChapter: activeSection, drawerOpen│   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │         data.js (global, read-only)      │   │
│  │  COURSES  CURRENT  SAMPLE_CHAPTER        │   │
│  │  SAMPLE_LAB  PROGRESS_STATS              │   │
│  │  LEVEL_MAP  CATEGORY_MAP                 │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 6.2 数据层设计

```javascript
// data.js — 全局只读，通过 window 暴露
const COURSES = [ ... ];           // 6 门课程 + 章节嵌套
const CURRENT = { ... };           // 当前学习焦点
const SAMPLE_CHAPTER = { ... };    // 章节内容（blocks 数组）
const SAMPLE_LAB = { ... };        // 实验数据（starter code + tests）
const PROGRESS_STATS = { ... };    // 进度统计
const LEVEL_MAP = { ... };         // 难度映射
const CATEGORY_MAP = { ... };      // 分类映射

Object.assign(window, { COURSES, CURRENT, ... });
```

### 6.3 状态管理策略

| 状态类型 | 位置 | 例子 |
|----------|------|------|
| **全局路由** | App `useState` | `route: {name, params}` |
| **全局主题** | App `useTweaks` | `t: {theme, brand, density, corners, hero_layout}` |
| **全局搜索** | App `useState` | `searchOpen: boolean` |
| **页面 UI** | Screen `useState` | `level`, `category`, `view`, `tab`, `filter` |
| **内容数据** | `window` 全局 | `COURSES`, `SAMPLE_CHAPTER` |
| **编辑状态** | Screen `useState` | `code`, `running`, `results`（Lab） |

### 6.4 useTweaks Hook

```javascript
function useTweaks(defaults) {
  const [values, setValues] = React.useState(defaults);
  const setTweak = React.useCallback((keyOrEdits, val) => {
    const edits = typeof keyOrEdits === 'object'
      ? keyOrEdits : { [keyOrEdits]: val };
    setValues(prev => ({ ...prev, ...edits }));
    // Host 协议：通知外部编辑器持久化
    window.parent.postMessage({ type: '__edit_mode_set_keys', edits }, '*');
    // 同窗口信号：其他组件可监听
    window.dispatchEvent(new CustomEvent('tweakchange', { detail: edits }));
  }, []);
  return [values, setTweak];
}
```

**关键特性**：
- 支持 `setTweak('key', value)` 和 `setTweak({...batch})` 两种调用
- 通过 `postMessage` 与宿主环境（Omelette 编辑器）通信
- `EDITMODE-BEGIN/END` 注释标记用于宿主回写默认值块

### 6.5 数据流演进路线

| 阶段 | 数据源 | 方案 |
|------|--------|------|
| MVP | `data.js` 硬编码 | 当前原型 |
| V1.1 | 后端 API | `fetch()` + `useState` + `useEffect` |
| V2 | 后端 API + 缓存 | 简易 Store（发布-订阅模式） |
| V3 | 后端 API + 离线 | Service Worker + IndexedDB |

---

## 7. TweaksPanel 实时调试系统

### 7.1 架构

```
┌─ Host (Omelette) ─────────────────────┐
│  postMessage('__activate_edit_mode')    │
│  ← __edit_mode_available               │
│  ← __edit_mode_set_keys (edits)        │
│  → __deactivate_edit_mode              │
│  ← __edit_mode_dismissed               │
└────────────────────────────────────────┘

┌─ TweaksPanel ─────────────────────────┐
│  监听 __activate_edit_mode → setOpen  │
│  监听 __deactivate_edit_mode → close  │
│  setTweak → postMessage + dispatch    │
│  可拖拽（mousedown → mousemove → up） │
│  视口约束（clampToViewport）          │
└────────────────────────────────────────┘
```

### 7.2 可调参数

| 分类 | 参数 | 类型 | 选项 |
|------|------|------|------|
| 主题 | `theme` | Radio | dark / light |
| 主题 | `brand` | Color | indigo / teal / amber / rose / lime |
| 布局 | `density` | Radio | compact / standard / spacious |
| 布局 | `corners` | Radio | square / soft / pill |
| 布局 | `hero_layout` | Radio | centered / split |
| 跳转 | 屏幕导航 | Button | 6 个快捷跳转 |

### 7.3 控件库

| 控件 | 用途 | 特性 |
|------|------|------|
| `TweakRadio` | 枚举选择 | Segmented control / Select 降级 |
| `TweakColor` | 颜色/调色板 | Chip 卡片式，支持单色和多色调色板 |
| `TweakSlider` | 连续值 | Range input + 实时数值显示 |
| `TweakToggle` | 布尔值 | iOS 风格开关 |
| `TweakNumber` | 数值 | 输入框 + 左右拖拽调整 |
| `TweakSelect` | 长枚举 | `<select>` 降级 |
| `TweakText` | 文本 | 单行输入 |
| `TweakButton` | 动作触发 | 主/次两级样式 |

### 7.4 TweakRadio 智能降级

```
if (选项数 ≤ 3 && 最大标签长度 ≤ 阈值) → Segmented Control
else → Select Dropdown
```

阈值计算：2 选项 = 16 字符，3 选项 = 10 字符（基于面板宽度 248px 推算）。

---

## 8. 开发工作流 — Agent 任务拆分

### 8.1 里程碑定义

| 里程碑 | 内容 | 前置依赖 |
|--------|------|----------|
| M1 | 项目骨架 + 主题系统 + TweaksPanel | 无 |
| M2 | Topbar + MobileNav + CommandPalette | M1 |
| M3 | 首页 (ScreenHome) | M2 |
| M4 | 课程列表 + 课程详情 | M2 |
| M5 | 章节阅读 | M4 |
| M6 | 在线实验 | M4 |
| M7 | 学习进度 | M2 |
| M8 | 数据层对接 API + URL 路由 | M3-M7 |
| M9 | 生产化（production.min.js + 性能优化） | M8 |

### 8.2 Agent 任务明细

#### M1: 项目骨架 + 主题系统 (2h)

| Agent 任务 | 描述 | 产出 | 估算 |
|------------|------|------|------|
| M1-1 | 创建 index.html 入口 + CDN 加载 | `index.html` | 30min |
| M1-2 | 迁移 styles.css 设计令牌 | `styles.css` | 30min |
| M1-3 | 迁移 icons.jsx | `icons.jsx` | 15min |
| M1-4 | 迁移 tweaks-panel.jsx + useTweaks | `tweaks-panel.jsx` | 30min |
| M1-5 | 创建 data.js (mock 数据) | `data.js` | 15min |

**验收**：浏览器打开 index.html，TweaksPanel 可拖拽，主题/品牌色/密度/圆角实时切换。

#### M2: 导航系统 (1.5h)

| Agent 任务 | 描述 | 产出 | 估算 |
|------------|------|------|------|
| M2-1 | 迁移 nav.jsx (Topbar + MobileNav) | `nav.jsx` | 30min |
| M2-2 | 迁移 CommandPalette | 包含在 nav.jsx | 30min |
| M2-3 | 创建 App Shell (路由 + 主题接线) | `app.jsx` | 30min |

**验收**：Topbar 导航可点击切换，⌘K 搜索面板可打开，MobileNav 在 <720px 显示。

#### M3: 首页 (2h)

| Agent 任务 | 描述 | 产出 | 估算 |
|------------|------|------|------|
| M3-1 | Hero 组件 (centered + split 两种布局) | `screen-home.jsx` | 40min |
| M3-2 | ContinueCard + LearningPath | 同上 | 30min |
| M3-3 | CourseCard 推荐 + HeroStats/HeroVisual | 同上 | 30min |
| M3-4 | TweaksPanel hero_layout 接线 | 同上 | 10min |

**验收**：首页渲染完整，Hero 布局切换（centered ↔ split）即时生效。

#### M4: 课程列表 + 详情 (2.5h)

| Agent 任务 | 描述 | 产出 | 估算 |
|------------|------|------|------|
| M4-1 | ScreenCourses + FilterGroup | `screen-courses.jsx` | 40min |
| M4-2 | CourseCard / CourseRow | 同上 | 30min |
| M4-3 | ScreenCourseDetail 布局 + Breadcrumb | `screen-course-detail.jsx` | 40min |
| M4-4 | ChapterListPanel + ChapterItem | 同上 | 30min |
| M4-5 | CourseProgressCard + CourseFactsCard + CourseInstructorCard | 同上 | 30min |

**验收**：课程筛选正常，课程详情侧边栏 sticky，章节列表过滤切换。

#### M5: 章节阅读 (2h)

| Agent 任务 | 描述 | 产出 | 估算 |
|------------|------|------|------|
| M5-1 | 章节阅读主体 + Block 渲染器 | `screen-chapter.jsx` | 50min |
| M5-2 | ChapterSidebar (TOC + 章节切换) | 同上 | 30min |
| M5-3 | Sticky 面包屑 + 进度条 + 上下章导航 | 同上 | 20min |
| M5-4 | MobileDrawer + Markdown 样式 | 同上 | 20min |

**验收**：章节内容渲染（h2/p/code/callout/list），TOC 高亮切换，上下章翻页。

#### M6: 在线实验 (2h)

| Agent 任务 | 描述 | 产出 | 估算 |
|------------|------|------|------|
| M6-1 | Lab 整体布局 + LabHeader | `screen-lab.jsx` | 30min |
| M6-2 | CodeEditor (textarea-based) | 同上 | 30min |
| M6-3 | LabBriefPanel + ResultPanel + TestsList | 同上 | 40min |
| M6-4 | AIAssistant 侧滑面板 | 同上 | 20min |

**验收**：代码可编辑，运行模拟跑通，测试结果逐步显示，AI 助手面板可打开。

#### M7: 学习进度 (1.5h)

| Agent 任务 | 描述 | 产出 | 估算 |
|------------|------|------|------|
| M7-1 | StatCard + ActivityChart | `screen-progress.jsx` | 40min |
| M7-2 | PathOverview (SVG 圆环进度) | 同上 | 30min |
| M7-3 | CourseProgressList + RecentActivity | 同上 | 20min |

**验收**：进度仪表盘数据渲染正确，SVG 圆环动画流畅。

#### M8: 数据层对接 (3h)

| Agent 任务 | 描述 | 产出 | 估算 |
|------------|------|------|------|
| M8-1 | 创建 api.js 封装 fetch 调用 | `api.js` | 40min |
| M8-2 | data.js → api.js 渐进替换 | 各 screen-*.jsx | 60min |
| M8-3 | hash-based URL 路由同步 | `app.jsx` | 30min |
| M8-4 | Loading/Error 状态处理 | 各组件 | 30min |

**验收**：刷新不丢失路由，API 数据加载有 loading 态，404 友好提示。

#### M9: 生产化 (2h)

| Agent 任务 | 描述 | 产出 | 估算 |
|------------|------|------|------|
| M9-1 | CDN 切换至 production.min.js | `index.html` | 15min |
| M9-2 | 预编译 JSX（可选 Babel CLI） | 构建脚本 | 45min |
| M9-3 | 字体本地化/子集化 | CSS/Font | 30min |
| M9-4 | Lighthouse 审计 + 优化 | 性能报告 | 30min |

**验收**：Lighthouse Performance ≥ 85，FCP < 1.5s。

### 8.3 总工作量估算

| 里程碑 | 估算 | 累计 |
|--------|------|------|
| M1 | 2h | 2h |
| M2 | 1.5h | 3.5h |
| M3 | 2h | 5.5h |
| M4 | 2.5h | 8h |
| M5 | 2h | 10h |
| M6 | 2h | 12h |
| M7 | 1.5h | 13.5h |
| M8 | 3h | 16.5h |
| M9 | 2h | 18.5h |

**总计**：~18.5 Agent-Hours（含测试验证时间）

---

## 9. 验收标准

### 9.1 功能验收

| ID | 验收项 | 优先级 | 对应 Screen |
|----|--------|--------|-------------|
| F01 | 首页渲染 Hero + 继续学习 + 学习路径 + 推荐课程 | P0 | Home |
| F02 | Hero 布局切换（centered ↔ split）即时生效 | P0 | Home |
| F03 | 课程列表页筛选（难度/方向）+ 视图切换（网格/列表） | P0 | Courses |
| F04 | 课程详情页章节列表 + 侧边栏进度卡 | P0 | CourseDetail |
| F05 | 章节阅读页 TOC 高亮 + 上下章翻页 + MobileDrawer | P0 | Chapter |
| F06 | 实验页代码编辑 + 模拟运行 + 测试结果展示 | P0 | Lab |
| F07 | AI 助手侧滑面板打开/关闭 | P1 | Lab |
| F08 | 进度页统计 + 活跃图 + SVG 圆环进度 | P1 | Progress |
| F09 | ⌘K 命令面板搜索课程/章节 | P1 | 全局 |
| F10 | Topbar 导航高亮跟随路由 | P0 | 全局 |
| F11 | MobileNav 在 <720px 显示，>=720px 隐藏 | P0 | 全局 |

### 9.2 主题系统验收

| ID | 验收项 | 优先级 |
|----|--------|--------|
| T01 | 暗/亮模式切换，所有变量正确覆盖 | P0 |
| T02 | 5 套品牌色切换，brand/brand-soft/brand-soft-2 同步 | P0 |
| T03 | 3 级密度切换，行高/卡片内边距响应 | P1 |
| T04 | 3 级圆角切换，所有 radius 变量响应 | P1 |
| T05 | 主题切换无闪烁（CSS Variables 原生切换） | P0 |
| T06 | TweaksPanel 可拖拽，视口边界约束 | P1 |
| T07 | TweaksPanel 关闭后宿主同步 dismissed | P2 |

### 9.3 性能验收

| ID | 验收项 | 指标 |
|----|--------|------|
| P01 | 首屏渲染 (FCP) | < 2s (CDN+development) / < 1.5s (production) |
| P02 | 主题切换延迟 | < 50ms (CSS Variables 无 re-render) |
| P03 | 路由切换延迟 | < 100ms (条件渲染，无动画) |
| P04 | TweaksPanel 拖拽流畅度 | 60fps |
| P05 | Babel Standalone 编译时间 | < 200ms (全部 JSX) |

### 9.4 兼容性验收

| 浏览器 | 版本 | 要求 |
|--------|------|------|
| Chrome | 90+ | 完全支持 |
| Firefox | 90+ | 完全支持 |
| Safari | 15+ | 完全支持 |
| Edge | 90+ | 完全支持 |
| Mobile Safari | 15+ | 布局适配 + MobileNav |
| Mobile Chrome | 90+ | 布局适配 + MobileNav |

### 9.5 代码质量验收

| ID | 验收项 | 标准 |
|----|--------|------|
| Q01 | 无 console.error / JS 运行时异常 | 浏览器 DevTools 清洁 |
| Q02 | CSS Variables 无未定义引用 | 全部 var(--xxx) 有对应声明 |
| Q03 | 组件 window 注册无冲突 | PascalCase + 语义前缀 |
| Q04 | 无内联样式硬编码颜色 | 所有颜色走 CSS Variables |
| Q05 | SRI 完整性校验通过 | CDN 脚本 integrity 属性正确 |
| Q06 | 无障碍基础 | 语义化 HTML + aria-label + role |

### 9.6 与现有项目的集成验收

| ID | 验收项 | 标准 |
|----|--------|------|
| I01 | 后端 SERVE_STATIC 正常服务前端 | `uvicorn` 启动后访问 `/` 返回 index.html |
| I02 | API 数据结构兼容 | 前端 data.js 字段名 = 后端 Pydantic schema |
| I03 | E2E 冒烟测试通过 | `npx playwright test tests/e2e/smoke.spec.js` 绿色 |
| I04 | 无 console.error | Playwright 采集浏览器日志无异常 |

---

## 附录 A: 原型文件 → 正式文件映射

| 原型文件 (`/tmp/jing_extract/optimized/`) | 行数 | 正式目标 |
|---------------------------------------------|------|----------|
| `index.html` | 54 | `frontend/index.html` |
| `styles.css` | 467 | `frontend/styles.css` |
| `data.js` | 301 | `frontend/data.js` → 后续替换为 `api.js` |
| `icons.jsx` | 86 | `frontend/icons.jsx` |
| `tweaks-panel.jsx` | 568 | `frontend/tweaks-panel.jsx` |
| `nav.jsx` | 201 | `frontend/nav.jsx` |
| `screen-home.jsx` | 315 | `frontend/screen-home.jsx` |
| `screen-courses.jsx` | 160 | `frontend/screen-courses.jsx` |
| `screen-course-detail.jsx` | 278 | `frontend/screen-course-detail.jsx` |
| `screen-chapter.jsx` | 401 | `frontend/screen-chapter.jsx` |
| `screen-lab.jsx` | 405 | `frontend/screen-lab.jsx` |
| `screen-progress.jsx` | 260 | `frontend/screen-progress.jsx` |
| `app.jsx` | 155 | `frontend/app.jsx` |

**总计**：~3,651 行代码

## 附录 B: 关键设计决策记录

| 决策 | 选项 | 理由 |
|------|------|------|
| 无构建工具 | CDN + Babel Standalone | 零配置、原型即生产、Agent 友好 |
| CSS Variables 主题 | 非 CSS-in-JS | 零运行时、浏览器原生切换、TweaksPanel 即时生效 |
| window 全局注册 | 非 ES Modules | CDN 方案限制、Babel Standalone 不支持 import |
| 条件渲染路由 | 非 React Router | 极简、零依赖、6 个页面足够 |
| textarea 代码编辑器 | 非 Monaco/CodeMirror | 零依赖、满足 MVP、后续可替换 |
| useTweaks Hook | 非 Context | 单消费者（App）、避免 Provider 嵌套 |
