# 前端用户体验优化设计文档

> 审计人：Hermes Agent (qianfan-code-latest)
> 日期：2026-05-18
> 版本：v1.0

---

## 1. 综述

### 1.1 优化目标

- **消除认知负担**：解决信息架构冗余（TOC vs 章节列表二选一）、导航路径断裂问题
- **提升沉浸感**：优化暗色主题的对比度、层次关系、微交互质感
- **补齐体验短板**：移动端适配、可及性、触摸交互
- **30% 改动覆盖 80% 体验痛点**：P0/P1 优先

### 1.2 设计原则

1. **单一路径原则** — 一个操作只留一个入口，不重复
2. **渐进信息** — 先给骨干，再给细节，不一次性堆满
3. **暗色优先** — 所有颜色在 #0a0e1a 背景上通过 WCAG AA 对比度
4. **移动优先** — 先保证 375px 可用，再增强到 1440px

---

## 2. 当前问题诊断

### 2.1 信息架构问题

| # | 问题 | 严重度 | 预估工时 |
|---|------|--------|---------|
| A1 | **右栏 TOC 与左栏章节列表功能完全重叠** — 课程详情页右栏的章节目录和左栏的章节列表都可点击跳转，用户要判断"点哪里" | 🔴 高 | 1-2h |
| A2 | **章节阅读页没有面包屑** — 返回按钮只知道回课程，但不知道"现在是第几章节/总共多少章" | 🟠 中 | 30min |
| A3 | **前后章导航两处重复** — 顶部圆形按钮和底部导航卡片功能重叠，但互不知晓状态 | 🟢 低 | 1h |

**A1 改进方案**：二选一策略

- **方案A**：左栏章节列表只做大纲展示（不可点击），跳转统一走右栏 TOC。左栏 hover 效果改为"预览高亮"而非"可点击"
- **方案B**：右栏改为"课程元信息卡"（进度统计、收藏、开始学习按钮），章节列表保留主交互。右栏 TOC 功能合并到左栏章节列表顶部加快速导航

> 推荐方案A：右栏 sticky 天然适合做导航，左栏适合做宽屏阅读。且方案B的右栏内容太少，无法填满 280px 空间。

**A2 改进方案**：返回按钮改为面包屑

```
← 课程 / Phase 1: Python快速通道 / 第3章 面向对象
```

用三个 `<a>` 标签，每级可点击回退。CSS 用 `color: var(--text-secondary)` 的 `. / .` 分隔符。

**A3 改进方案**：顶部按钮精简为"仅箭头 + tooltip"，底部卡片保留完整章节信息。顶部按钮鼠标经过时显示：

```html
<a href="#" title="上一章：2 函数式编程">‹</a>
```

---

### 2.2 导航问题

| # | 问题 | 严重度 | 预估工时 |
|---|------|--------|---------|
| B1 | **sticky 侧边栏可能溢出视口** — 长篇章节的 TOC 列表超出屏幕高度，没有滚动 | 🔴 高 | 10min |
| B2 | **前后章按钮首尾缺 disabled 态** — 第一章时"上一章"按钮无视觉提示，点上去无反应 | 🟠 中 | 15min |
| B3 | **返回按钮缺少来源上下文** — 从课程5点进章节，点返回回到哪里不确定 | 🟠 中 | 20min |

**B1 改进方案**：

```css
.sidebar-sticky {
  position: sticky;
  top: calc(64px + 52px + 20px);
  max-height: calc(100vh - 64px - 52px - 40px); /* navbar + topbar + margins */
  overflow-y: auto;
}
```

**B2 改进方案**：

```css
.btn-nav-disabled {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
}
```

---

### 2.3 视觉设计问题

| # | 问题 | 严重度 | 预估工时 |
|---|------|--------|---------|
| C1 | **暗色卡片与背景对比度不足** — #0a0e1a 背景 + #1a2035 卡片，亮度差仅 8%，正文文本对比度可能 < 4.5:1 | 🔴 高 | 15min |
| C2 | **渐变文字选中不可见** — `background-clip: text` + `-webkit-text-fill-color: transparent` 导致选中区域无文字色 | 🟠 中 | 5min |
| C3 | **进度条在暗色背景下"隐形"** — 4px 高度 + 深色轨道 = 看不见 | 🟢 低 | 10min |
| C4 | **实验章与普通章视觉无区分** — 都是同一套 .chapter-item 样式 | 🟢 低 | 20min |

**C1 改进方案**：

```css
/* 卡片背景提升亮度差 */
--bg-card: #1e293b;        /* 从 #1a2035 改 */
/* 正文文字提升亮度 */
--text-primary: #e2e8f0;   /* 从 #f1f5f9 微调，实际需要对比度检测 */
/* 卡片边框 */
--border: rgba(255,255,255,0.06); /* 透明边框提升分离感 */
```

**C2 改进方案**：

```css
/* 在 spa.css 添加 */
::selection {
  -webkit-text-fill-color: #fff;
  background: rgba(99, 102, 241, 0.4);
}
```

**C4 改进方案**：实验章增加视觉标识

```css
.chapter-item.lab {
  border-left: 3px solid var(--accent);  /* #22d3ee */
}
.chapter-item.lab .chapter-num {
  background: rgba(34, 211, 238, 0.15);
  color: var(--accent);
}
```

---

### 2.4 交互反馈问题

| # | 问题 | 严重度 | 预估工时 |
|---|------|--------|---------|
| D1 | **章节列表 hover 左移方向反直觉** — `translateX(-8px)` 是"推开"语义，用户预期是"选中/聚焦" | 🟠 中 | 10min |
| D2 | **TOC 高亮切换无过渡** — 当前章高亮是硬切换，没有淡入效果 | 🟢 低 | 15min |
| D3 | **前后章按钮无 tooltip** — 只有箭头图标，不知道下一章叫什么 | 🟢 低 | 10min |

**D1 改进方案**：

```css
/* 改为右侧指示 + 背景高亮 */
.chapter-item:hover {
  background: var(--bg-card-hover);
  border-left: 3px solid var(--primary);
  transform: translateX(0); /* 取消左移 */
}
```

**D2 改进方案**：

```css
.toc-item {
  transition: background 0.2s ease, color 0.2s ease;
}
.toc-item.toc-active {
  background: rgba(99, 102, 241, 0.12);
  color: var(--primary);
}
```

---

### 2.5 可及性问题

| # | 问题 | 严重度 | 预估工时 |
|---|------|--------|---------|
| E1 | **进度条用 `<div>` 实现** — 屏幕阅读器无法识别 | 🟠 中 | 5min |
| E2 | **章节列表项不可 Tab 聚焦** — 键盘用户无法遍历章节 | 🟢 低 | 10min |
| E3 | **移动端触摸目标 < 44px** — 圆形按钮、TOC 链接尺寸不足 | 🟠 中 | 20min |

**E1 改进方案**：

```html
<!-- 语义化进度条 -->
<progress value="3" max="10" class="progress-track"></progress>
<span class="progress-text">3/10</span>
```

或保留视觉样式但增加 ARIA 属性：

```html
<div class="progress-track" role="progressbar" aria-valuenow="30" aria-valuemin="0" aria-valuemax="100">
  <div class="progress-fill" style="width:30%"></div>
</div>
```

---

### 2.6 移动端适配问题

| # | 问题 | 严重度 | 预估工时 |
|---|------|--------|---------|
| F1 | **两栏→单栏后 TOC 消失** — 右侧边栏 `display:none`，用户失去导航 | 🔴 高 | 1-2h |
| F2 | **毛玻璃导航栏低端设备掉帧** — `backdrop-filter: blur()` 在低端机卡顿 | 🟢 低 | 15min |

**F1 改进方案**：TOC 折叠为 Accordion

```html
<details class="mobile-toc">
  <summary>📋 章节目录 ▾</summary>
  <div class="toc-list"><!-- TOC 内容 --></div>
</details>
```

只在 `<768px` 显示：

```css
@media (max-width: 768px) {
  .course-sidebar, .chapter-sidebar { display: none; }
  .mobile-toc { display: block; }
}
```

**F2 改进方案**：

```css
@supports (backdrop-filter: blur(10px)) {
  .navbar { backdrop-filter: blur(16px); }
}
@supports not (backdrop-filter: blur(10px)) {
  .navbar { background: rgba(10, 14, 26, 0.95); }
}
```

---

## 3. 详细设计方案（P0 条目）

### 3.1 修复 sticky 侧边栏溢出

**当前状态**：右栏 TOC 列表超出视口时无法滚动，底部选项被截断

**目标状态**：侧边栏独立滚动，不超过底栏

**改动文件**：`spa.css`

```css
.sidebar-sticky {
  position: sticky;
  top: calc(64px + 52px + 20px);
  max-height: calc(100vh - 64px - 52px - 40px);
  overflow-y: auto;
  scrollbar-width: thin;
}
```

**边界情况**：
- TOC 项少于视口高度时不滚（不需要滚动条）
- 侧边栏右侧紧贴窗口边缘时不影响主内容区

---

### 3.2 修复章节列表 hover 方向

**当前状态**：hover 时 `translateX(-8px)`，向左偏移

**目标状态**：hover 时左侧出现主色竖线 + 背景高亮

**改动文件**：`spa.css`

```css
.chapter-item {
  border-left: 3px solid transparent; /* 占位，防止hover时抖动 */
  transition: all 0.2s ease;
}
.chapter-item:hover {
  background: var(--bg-card-hover);
  border-left-color: var(--primary);
  transform: translateX(0);
}
```

---

### 3.3 进度条语义化

**改动文件**：`Chapter.js` 和 `CourseDetail.js`

将当前：

```html
<div class="progress-track">
  <div class="progress-fill" style="width:30%"></div>
</div>
```

改为：

```html
<div class="progress-track" role="progressbar" aria-valuenow="30" aria-valuemin="0" aria-valuemax="100">
  <div class="progress-fill" style="width:30%"></div>
</div>
```

---

## 4. 实施路线图

### P0：快速修复（30分钟内）

| 任务 | 文件 | 时间 |
|------|------|------|
| sticky 侧边栏溢出修复 | `spa.css` | 10min |
| 章节列表 hover 方向修复 | `spa.css` | 10min |
| 前后章按钮 disabled 态 | `spa.css` | 5min |
| 选中文字颜色修复 | `spa.css` | 5min |
| 进度条语义化 | `Chapter.js` + `CourseDetail.js` | 10min |

### P1：核心体验（1-3小时）

| 任务 | 时间 |
|------|------|
| 信息架构去重：TOC 与章节列表合并（方案A） | 1-2h |
| 返回按钮改为面包屑 | 30min |
| 前后章按钮 tooltip | 20min |
| 实验章视觉区分 | 20min |

### P2：体验打磨（3-6小时）

| 任务 | 时间 |
|------|------|
| 移动端 TOC 折叠 Accordion | 1-2h |
| 暗色主题对比度校准 | 30min |
| TOC 高亮过渡动效 | 20min |
| 触摸目标尺寸调整 | 1h |
| 毛玻璃渐进增强 | 15min |

### Future

| 任务 | 原因 |
|------|------|
| IntersectionObserver 联动 TOC 高亮 | 需要引入新依赖，门槛较高 |
| 阅读进度自动同步 | 需要后端配合 |
| 字体/字号设置 | 需要用户偏好存储 |

---

## 5. 验收标准

### 5.1 功能验收

- [ ] 课程详情页右侧 TOC 点击跳转正确
- [ ] 章节阅读页 sticky 操作栏在滚动时保持可见
- [ ] 前后章按钮首尾正确隐藏/禁用到
- [ ] 返回按钮回到正确课程
- [ ] 进度条数值与实际章节一致
- [ ] E2E 冒烟测试 6/6 通过

### 5.2 视觉验收

- [ ] 暗色主题下正文文本可通过 WCAG AA 对比度（4.5:1）
- [ ] hover 状态有平滑过渡（≥ 0.2s）
- [ ] 实验章与普通章视觉可区分
- [ ] 选中文字颜色正常（非透明）
- [ ] 移动端 375px 宽度下所有页面可用

### 5.3 性能验收

- [ ] 页面初始渲染时间 < 2s（无缓存）
- [ ] TOC 列表滚动无卡顿（60fps）
- [ ] 毛玻璃导航栏在无 `backdrop-filter` 设备上正常降级
- [ ] 未触发任何 JS console.error

---

## 附录：改动文件清单

| 文件 | P0 | P1 | P2 |
|------|----|----|----|
| `frontend/css/spa.css` | ✅ | ✅ | ✅ |
| `frontend/src/views/Chapter.js` | ✅ | ✅ | |
| `frontend/src/views/CourseDetail.js` | | ✅ | |
| `frontend/src/views/Courses.js` | | | ✅ |
| `frontend/spa.html` | | | ✅ |
