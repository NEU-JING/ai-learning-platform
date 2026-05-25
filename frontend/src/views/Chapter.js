/**
 * Chapter View - SPA 版本 v3.0
 * 固定顶部操作栏（返回/标题/导航）+ 右侧目录 + 上下章导航
 */
import { API } from '../services/api.js';
import { Store } from '../core/store.js';

const store = Store.getInstance();

export default async function Chapter({ params }) {
  const chapterId = params?.id;
  if (!chapterId) {
    return '<div class="error-page"><h1>章节ID缺失</h1><a href="#/courses" class="btn btn-primary">返回课程列表</a></div>';
  }

  const container = document.createElement('div');
  container.className = 'page chapter-page page-enter';

  const isAuth = !!store.state.token;
  const navbar = buildNavbar(isAuth, store);

  container.innerHTML = `
    ${navbar}
    <div class="container">
      <div class="loading" style="padding:80px 0;"><span style="font-size:2rem;">⏳</span><br>加载中...</div>
    </div>`;

  try {
    const chapter = await API.courses.getChapter(chapterId);
    if (!chapter) throw new Error('章节不存在');

    const courseId = chapter.course_id;
    // 同时获取课程信息和章节列表（用于TOC和导航）
    let courseTitle = '课程';
    let chapters = [];
    let currentIdx = -1;
    try {
      const [course, chList] = await Promise.all([
        API.courses.get(courseId),
        API.courses.getChapters(courseId)
      ]);
      courseTitle = course.title;
      chapters = Array.isArray(chList) ? chList : (chList?.items || []);
      currentIdx = chapters.findIndex(c => c.id == chapterId);
    } catch (e) {}

    const hasPrev = currentIdx > 0;
    const hasNext = currentIdx >= 0 && currentIdx < chapters.length - 1;
    const prevChapter = hasPrev ? chapters[currentIdx - 1] : null;
    const nextChapter = hasNext ? chapters[currentIdx + 1] : null;

    // 渲染markdown内容
    const contentHtml = renderMarkdown(chapter.content || '');

    const hasLab = chapter.has_lab || chapter.lab;

    // 右侧目录TOC
    const tocItemsHtml = chapters.map((ch, i) => {
      const isLab = ch.chapter_type === 'lab' || ch.title?.startsWith('E');
      const isCurrent = ch.id == chapterId;
      const statusIcon = ch.is_completed ? '✅' : (isCurrent ? '📖' : '');
      return `
        <a href="#/chapters/${ch.id}" class="toc-item ${isLab ? 'toc-lab' : ''} ${isCurrent ? 'toc-active' : ''}">
          <span class="toc-index">${statusIcon || ch.order_index}</span>
          <span class="toc-title">${ch.title}</span>
        </a>`;
    }).join('');

    container.innerHTML = `
      ${navbar}
      <div class="chapter-layout">
        <!-- 固定顶部操作栏 -->
        <div class="chapter-topbar">
          <div class="container">
            <div class="topbar-inner">
              <div class="topbar-left">
                <a href="#/courses/${courseId}" class="topbar-back" title="返回课程">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5m7-7-7 7 7 7"/></svg>
                  <span class="topbar-back-text">${courseTitle}</span>
                </a>
              </div>
              <div class="topbar-center">
                <span class="topbar-chapter-title">${chapter.title}</span>
              </div>
              <div class="topbar-right">
                <span class="topbar-meta">
                  ${chapter.duration_minutes ? `⏱️ ${chapter.duration_minutes}分钟` : ''}
                  ${currentIdx >= 0 ? `· ${currentIdx + 1}/${chapters.length}` : ''}
                </span>
                <div class="topbar-nav">
                  ${hasPrev
                    ? `<a href="#/chapters/${prevChapter.id}" class="btn-nav btn-nav-prev" title="上一章：${prevChapter.title}">‹</a>`
                    : '<span class="btn-nav btn-nav-disabled">‹</span>'}
                  ${hasNext
                    ? `<a href="#/chapters/${nextChapter.id}" class="btn-nav btn-nav-next" title="下一章：${nextChapter.title}">›</a>`
                    : '<span class="btn-nav btn-nav-disabled">›</span>'}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="container">
          <div class="chapter-body-layout">
            <!-- 左侧主内容 -->
            <div class="chapter-main">
              <div class="md-content">
                ${contentHtml}
              </div>

              <!-- 实验入口 -->
              ${hasLab ? `
              <div class="lab-entry">
                <a href="#/labs/${hasLab.id || chapter.id}" class="btn btn-primary" style="padding:14px 32px;">
                  🧪 进入实验课
                </a>
              </div>` : ''}

              <!-- 上下章导航 -->
              <div class="chapter-nav-footer">
                ${hasPrev
                  ? `<a href="#/chapters/${prevChapter.id}" class="nav-card nav-card-prev">
                      <span class="nav-card-label">← 上一章</span>
                      <span class="nav-card-title">${prevChapter.title}</span>
                    </a>`
                  : '<div class="nav-card nav-card-empty"></div>'}
                ${hasNext
                  ? `<a href="#/chapters/${nextChapter.id}" class="nav-card nav-card-next">
                      <span class="nav-card-label">下一章 →</span>
                      <span class="nav-card-title">${nextChapter.title}</span>
                    </a>`
                  : '<div class="nav-card nav-card-empty"></div>'}
              </div>
            </div>

            <!-- 右侧目录侧边栏 -->
            <aside class="chapter-sidebar">
              <div class="sidebar-sticky">
                <div class="sidebar-title">📋 ${courseTitle}</div>
                <div class="sidebar-progress">
                  <div class="progress-track">
                    <div class="progress-fill" style="width:${chapters.length ? Math.round((currentIdx + 1) / chapters.length * 100) : 0}%"></div>
                  </div>
                  <span class="progress-text">${currentIdx + 1}/${chapters.length}</span>
                </div>
                <div class="toc-list">
                  ${tocItemsHtml}
                </div>
              </div>
            </aside>
          </div>
        </div>
      </div>`;

    // 自动代码高亮
    setTimeout(() => {
      container.querySelectorAll('.md-content pre code').forEach((block) => {
        if (typeof hljs !== 'undefined') {
          hljs.highlightElement(block);
        }
      });
    }, 100);

  } catch (err) {
    container.innerHTML = `
      ${navbar}
      <div class="container">
        <div class="error-page" style="min-height:50vh;">
          <h1>😅</h1>
          <p style="color:var(--text-secondary);margin-top:16px;">${err.message || '加载失败'}</p>
          <a href="#/courses" class="btn btn-primary" style="margin-top:16px;">返回课程列表</a>
        </div>
      </div>`;
  }

  return container;
}

function buildNavbar(isAuth, store) {
  return `
    <nav class="navbar">
      <a href="#/" class="navbar-brand">
        <div class="navbar-logo">AI</div>
        <span>AI学习平台</span>
      </a>
      <ul class="navbar-nav">
        <li><a href="#/">首页</a></li>
        <li><a href="#/courses" class="active">课程</a></li>
        <li><a href="#/progress">学习进度</a></li>
          <li><a href="#/profile/settings">我的公开主页</a></li>
      </ul>
      <div class="navbar-right">
        ${isAuth && store.state.user
          ? `<span class="user-name">${store.state.user.email}</span>
             <a href="#" class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout'); window.location.hash='#/'; return false;">退出</a>`
          : `<a href="#/login" class="btn btn-secondary btn-sm">登录</a>
             <a href="#/register" class="btn btn-primary btn-sm">注册</a>`
        }
      </div>
    </nav>`;
}

/**
 * Markdown 渲染器 v2.0
 * 修复：避免将所有内容包裹在 <p> 标签中破坏 HTML 结构
 */
function renderMarkdown(md) {
  if (!md) return '<p style="color:var(--text-muted);">暂无内容</p>';

  let html = md;

  // 1️⃣ Code blocks (must go first, before any other processing)
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (m, lang, code) => {
    const langClass = lang ? ` class="language-${lang}"` : '';
    return `%%%CODEBLOCK%%%<pre><code${langClass}>${escapeHtml(code.trim())}</code></pre>%%%/CODEBLOCK%%%`;
  });

  // 2️⃣ Details/Summary blocks — preserve as HTML
  html = html.replace(/<details>/g, '%%%DETAILS%%%<details style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);padding:12px 16px;margin:16px 0;">');
  html = html.replace(/<\/details>/g, '</details>%%%/DETAILS%%%');
  html = html.replace(/<summary>/g, '<summary style="cursor:pointer;font-weight:600;color:var(--primary);font-size:0.95rem;">');
  html = html.replace(/<\/summary>/g, '</summary>');

  // 3️⃣ Headers
  html = html.replace(/^### (.*$)/gm, '%%%HEADER%%%<h3>$1</h3>%%%/HEADER%%%');
  html = html.replace(/^## (.*$)/gm, '%%%HEADER%%%<h2 style="font-size:1.4rem;font-weight:700;margin-top:32px;margin-bottom:12px;border-bottom:1px solid var(--border);padding-bottom:8px;">$1</h2>%%%/HEADER%%%');
  html = html.replace(/^# (.*$)/gm, '%%%HEADER%%%<h1 style="font-size:1.6rem;font-weight:700;margin-top:32px;margin-bottom:12px;">$1</h1>%%%/HEADER%%%');

  // 4️⃣ Horizontal rules
  html = html.replace(/^---$/gm, '%%%HR%%%<hr style="border:none;border-top:1px solid var(--border);margin:24px 0;">%%%/HR%%%');

  // 5️⃣ Bold & italic
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // 6️⃣ Inline code
  html = html.replace(/`([^`]+)`/g, '<code style="background:var(--bg-elevated);padding:2px 6px;border-radius:4px;font-family:monospace;color:var(--accent);font-size:0.88em;">$1</code>');

  // 7️⃣ Blockquotes
  html = html.replace(/^> (.*$)/gm, '%%%BLOCKQUOTE%%%<blockquote style="border-left:3px solid var(--primary);padding:12px 20px;margin:16px 0;background:rgba(99,102,241,0.05);border-radius:0 var(--radius-sm) var(--radius-sm) 0;color:var(--text-secondary);">$1</blockquote>%%%/BLOCKQUOTE%%%');

  // 8️⃣ Tables (simple)
  html = html.replace(/\|(.+)\|/g, (m) => {
    const cells = m.split('|').filter(c => c.trim());
    if (cells.every(c => /^[-:\s]+$/.test(c))) return '%%%TABLE%%%<tr class="table-sep">%%%/TABLE%%%';
    return `%%%TABLE%%%<tr><td>${cells.join('</td><td>')}</td></tr>%%%/TABLE%%%`;
  });
  html = html.replace(/(%%%TABLE%%%(?:<tr[^>]*>.*?<\/tr>%%%/TABLE%%%\n?)+)/g, '<table style="width:100%;border-collapse:collapse;margin:16px 0;"><thead style="background:var(--bg-elevated);font-weight:600;">$1</thead></table>');

  // 9️⃣ Lists
  html = html.replace(/^- (.*$)/gm, '%%%LI%%%<li>$1</li>%%%/LI%%%');
  html = html.replace(/(%%%LI%%%<li>.*?<\/li>%%%/LI%%%\n?)+/g, '<ul style="margin-bottom:16px;padding-left:24px;">$&</ul>');
  html = html.replace(/%%%LI%%%|%%%/LI%%%/g, '');

  // 🔟 Paragraphs — wrap remaining non-tag lines
  // Split by lines, wrap non-HTML lines in <p>
  const lines = html.split('\n');
  html = lines.map(line => {
    const trimmed = line.trim();
    if (!trimmed) return '';
    // Skip lines that are part of block elements or already wrapped
    if (trimmed.startsWith('<') && (trimmed.includes('>') || trimmed.startsWith('%%%'))) return line;
    return `<p style="margin-bottom:16px;line-height:1.8;">${trimmed}</p>`;
  }).join('\n');

  // Clean up block markers
  html = html.replace(/%%%(\/)?(CODEBLOCK|DETAILS|HEADER|HR|BLOCKQUOTE|TABLE)%%%/g, '');

  // Fix: remove empty <p> tags
  html = html.replace(/<p[^>]*>\s*<\/p>/g, '');

  // Fix nested markers and duplicates
  html = html.replace(/%%%\/?(LI)%%%/g, '');

  return html;
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
