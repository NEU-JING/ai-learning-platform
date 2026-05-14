/**
 * Discussion View — List discussions for a course
 */

import { API } from '../services/api.js';
import { AuthService } from '../services/auth.js';

export default async function Discussion() {
  const isLoggedIn = AuthService.isAuthenticated();
  let selectedCourseId = null;
  let discussions = [];
  let courses = [];
  let sort = 'newest';

  // Load courses
  try {
    courses = await API.courses.list();
  } catch (e) {
    courses = [];
  }

  async function loadDiscussions(courseId, sortBy = 'newest') {
    sort = sortBy;
    selectedCourseId = courseId;
    try {
      discussions = await API.discussions.list(courseId, sortBy);
    } catch (e) {
      discussions = [];
    }
    render();
  }

  async function handleCreate(title, content) {
    if (!selectedCourseId || !isLoggedIn) return;
    try {
      await API.discussions.create(selectedCourseId, { title, content });
      await loadDiscussions(selectedCourseId, sort);
    } catch (e) {
      alert('创建失败: ' + e.message);
    }
  }

  function formatTime(dt) {
    if (!dt) return '';
    const d = new Date(dt);
    const now = new Date();
    const diffMs = now - d;
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return '刚刚';
    if (diffMin < 60) return `${diffMin}分钟前`;
    const diffH = Math.floor(diffMin / 60);
    if (diffH < 24) return `${diffH}小时前`;
    const diffD = Math.floor(diffH / 24);
    if (diffD < 30) return `${diffD}天前`;
    return d.toLocaleDateString('zh-CN');
  }

  function render() {
    const container = document.getElementById('discussion-container');
    if (!container) return;

    const courseSelector = courses.map(c =>
      `<button class="btn ${selectedCourseId === c.id ? 'btn-primary' : ''}" 
        onclick="window.__discussSelect(${c.id})" 
        style="margin:0 4px 4px 0;font-size:0.85rem;">
        ${c.title}
      </button>`
    ).join('');

    const sortBtns = ['newest', 'popular', 'pinned'].map(s =>
      `<button class="btn ${sort === s ? 'btn-primary' : ''}" 
        onclick="window.__discussSort('${s}')" 
        style="font-size:0.8rem;margin-right:4px;">
        ${{newest:'最新',popular:'最热',pinned:'置顶'}[s]}
      </button>`
    ).join('');

    let discussionList = '';
    if (!selectedCourseId) {
      discussionList = '<p style="color:#666;text-align:center;padding:2rem;">请选择一个课程查看讨论</p>';
    } else if (discussions.length === 0) {
      discussionList = '<p style="color:#666;text-align:center;padding:2rem;">暂无讨论，来发起第一个吧！</p>';
    } else {
      discussionList = discussions.map(d => `
        <div class="card" style="margin-bottom:12px;cursor:pointer;" onclick="window.__discussDetail(${d.id})">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <h3 style="margin:0;font-size:1.05rem;">
              ${d.is_pinned ? '📌 ' : ''}${d.title}
            </h3>
            ${d.is_locked ? '<span style="color:#999;font-size:0.8rem;">🔒 已锁定</span>' : ''}
          </div>
          <p style="color:#666;margin:8px 0 0;font-size:0.9rem;">${d.content_preview || ''}</p>
          <div style="display:flex;gap:16px;margin-top:8px;font-size:0.8rem;color:#999;">
            <span>👤 ${d.user?.username || '匿名'}</span>
            <span>❤️ ${d.likes_count}</span>
            <span>💬 ${d.comments_count}</span>
            <span>🕐 ${formatTime(d.created_at)}</span>
          </div>
        </div>
      `).join('');
    }

    container.innerHTML = `
      <div style="margin-bottom:16px;">
        <h3 style="margin:0 0 8px;">选择课程</h3>
        <div>${courseSelector || '<p style="color:#999;">暂无课程</p>'}</div>
      </div>
      ${selectedCourseId ? `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div>${sortBtns}</div>
          ${isLoggedIn ? '<button class="btn btn-primary" onclick="window.__discussCreate()" style="font-size:0.85rem;">+ 发起讨论</button>' : ''}
        </div>
        ${discussionList}
      ` : ''}
    `;
  }

  // Expose handlers to global scope for onclick
  window.__discussSelect = (id) => loadDiscussions(id, sort);
  window.__discussSort = (s) => { if (selectedCourseId) loadDiscussions(selectedCourseId, s); };
  window.__discussDetail = (id) => { window.location.hash = `#/discussions/${id}`; };
  window.__discussCreate = () => {
    const title = prompt('讨论标题:');
    if (!title) return;
    const content = prompt('讨论内容:');
    if (!content) return;
    handleCreate(title, content);
  };

  // Initial render
  const html = `
    <div class="page">
      <div class="container">
        <h1 style="margin-bottom:16px;">💬 讨论区</h1>
        <div id="discussion-container"></div>
      </div>
    </div>
  `;

  // Defer render to after DOM mount
  setTimeout(() => render(), 0);
  return html;
}
