/**
 * Course Detail View - SPA 版本 v3.0
 * 两栏布局：左侧课程内容 + 右侧章节目录导航（sticky）
 */
import { API } from '../services/api.js';
import { Store } from '../core/store.js';

const store = Store.getInstance();

export default async function CourseDetail({ params }) {
  const courseId = params?.id;
  if (!courseId) {
    return '<div class="error-page"><h1>课程ID缺失</h1><a href="#/courses" class="btn btn-primary">返回课程列表</a></div>';
  }

  const container = document.createElement('div');
  container.className = 'page course-detail-page page-enter';

  const isAuth = !!store.state.token;
  const navbar = buildNavbar(isAuth, store);

  container.innerHTML = `
    ${navbar}
    <div class="container">
      <div class="loading" style="padding: 60px 0;"><span style="font-size:2rem;">⏳</span><br>加载课程中...</div>
    </div>`;

  try {
    const course = await API.courses.get(courseId);
    if (!course) throw new Error('课程不存在');

    const chapters = await API.courses.getChapters(courseId);
    const chapterList = Array.isArray(chapters) ? chapters : (chapters?.items || []);

    const chapterItemsHtml = chapterList.map(ch => {
      const isLab = ch.chapter_type === 'lab' || ch.title?.startsWith('E');
      return `
        <a href="#/chapters/${ch.id}" class="chapter-item ${isLab ? 'lab' : ''}">
          <div class="chapter-num">${isLab ? '🧪' : ch.order_index}</div>
          <div class="chapter-info">
            <div class="chapter-title">${ch.title}</div>
            <div class="chapter-meta">
              ${isLab ? '实验课' : ch.duration_minutes ? ch.duration_minutes + '分钟' : ''}
            </div>
          </div>
          <div class="chapter-status">${ch.is_completed ? '✅' : '📖'}</div>
        </a>`;
    }).join('');

    const totalMinutes = chapterList.reduce((s, c) => s + (c.duration_minutes || 0), 0);
    const labCount = chapterList.filter(c => c.chapter_type === 'lab' || c.title?.startsWith('E')).length;

    // 右侧目录侧边栏
    const tocItemsHtml = chapterList.map((ch, i) => {
      const isLab = ch.chapter_type === 'lab' || ch.title?.startsWith('E');
      const statusIcon = ch.is_completed ? '✅' : (i === 0 ? '📖' : '');
      return `
        <a href="#/chapters/${ch.id}" class="toc-item ${isLab ? 'toc-lab' : ''}">
          <span class="toc-index">${statusIcon || ch.order_index}</span>
          <span class="toc-title">${ch.title}</span>
        </a>`;
    }).join('');

    container.innerHTML = `
      ${navbar}
      <div class="container">
        <div class="course-detail-layout">
          <!-- 左侧主内容 -->
          <div class="course-detail-main">
            <div class="course-detail-header">
              <h1>${course.title}</h1>
              <p>${course.description || ''}</p>
              <div class="course-meta-tags">
                ${getLevelBadge(course.level)}
                <span style="color:var(--text-muted);font-size:0.85rem;">⏱️ ${totalMinutes}分钟</span>
                <span style="color:var(--text-muted);font-size:0.85rem;">📚 ${chapterList.length}章节</span>
                ${labCount ? `<span style="color:var(--text-muted);font-size:0.85rem;">🧪 ${labCount}实验</span>` : ''}
              </div>
            </div>
            <div class="chapter-list">
              ${chapterItemsHtml || '<div style="padding:40px;text-align:center;color:var(--text-muted);">暂无章节内容</div>'}
            </div>
          </div>
          <!-- 右侧目录侧边栏 -->
          <aside class="course-sidebar">
            <div class="sidebar-sticky">
              <div class="sidebar-title">📋 章节目录</div>
              <div class="sidebar-progress">
                <div class="progress-track">
                  <div class="progress-fill" style="width:0%"></div>
                </div>
                <span class="progress-text">0/${chapterList.length}</span>
              </div>
              <div class="toc-list">
                ${tocItemsHtml}
              </div>
            </div>
          </aside>
        </div>
      </div>`;
  } catch (err) {
    container.innerHTML = `
      ${navbar}
      <div class="container">
        <div class="error-page" style="min-height:50vh;">
          <h1>😅</h1>
          <p style="color:var(--text-secondary);margin-top:16px;">${err.message || '加载课程失败'}</p>
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

function getLevelBadge(level) {
  const levels = {
    beginner: { text: '入门', color: '#10b981' },
    intermediate: { text: '进阶', color: '#f59e0b' },
    advanced: { text: '高级', color: '#ef4444' }
  };
  const lv = levels[level];
  return lv
    ? `<span class="course-level" style="background:rgba(${lv.color === '#10b981' ? '16,185,129' : lv.color === '#f59e0b' ? '245,158,11' : '239,68,68'},0.15);color:${lv.color};">${lv.text}</span>`
    : '';
}
