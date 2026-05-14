/**
 * Discussion Detail View — Show discussion content, comments, like
 */

import { API } from '../services/api.js';
import { AuthService } from '../services/auth.js';

export default async function DiscussionDetail({ params }) {
  const discussionId = params?.id;
  if (!discussionId) {
    return '<div class="page"><div class="container"><h1>讨论ID缺失</h1><a href="#/discussions">返回讨论区</a></div></div>';
  }

  const isLoggedIn = AuthService.isAuthenticated();
  let discussion = null;
  let liked = false;

  try {
    discussion = await API.discussions.get(discussionId);
  } catch (e) {
    return `<div class="page"><div class="container"><h1>加载失败</h1><p>${e.message}</p><a href="#/discussions">返回讨论区</a></div></div>`;
  }

  function formatTime(dt) {
    if (!dt) return '';
    const d = new Date(dt);
    const diffMs = Date.now() - d;
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return '刚刚';
    if (diffMin < 60) return `${diffMin}分钟前`;
    const diffH = Math.floor(diffMin / 60);
    if (diffH < 24) return `${diffH}小时前`;
    return d.toLocaleDateString('zh-CN');
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  async function handleLike() {
    if (!isLoggedIn) { alert('请先登录'); return; }
    try {
      const result = await API.discussions.like(discussionId);
      liked = result.liked;
      // Update UI
      const likeBtn = document.getElementById('like-btn');
      const likeCount = document.getElementById('like-count');
      if (likeBtn) likeBtn.textContent = liked ? '❤️ 已赞' : '🤍 点赞';
      if (likeCount) likeCount.textContent = result.likes_count;
    } catch (e) { /* ignore */ }
  }

  async function handleComment(content, parentId = null) {
    if (!isLoggedIn) { alert('请先登录'); return; }
    try {
      await API.discussions.createComment(discussionId, content);
      // Reload discussion
      discussion = await API.discussions.get(discussionId);
      renderComments();
    } catch (e) {
      alert('评论失败: ' + e.message);
    }
  }

  function renderComments() {
    const container = document.getElementById('comments-container');
    if (!container || !discussion) return;

    const commentsHtml = (discussion.comments || []).map(c => `
      <div class="card" style="margin-bottom:10px;padding:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
          <strong style="font-size:0.9rem;">👤 ${escapeHtml(c.user?.username || '匿名')}</strong>
          <span style="font-size:0.75rem;color:#999;">${formatTime(c.created_at)}</span>
        </div>
        <p style="margin:0;font-size:0.9rem;white-space:pre-wrap;">${escapeHtml(c.content)}</p>
        <div style="margin-top:6px;font-size:0.8rem;color:#999;">
          ❤️ ${c.likes_count}
          ${isLoggedIn ? ` | <a href="javascript:void(0)" onclick="window.__replyComment(${c.id})">回复</a>` : ''}
          ${c.is_solution ? ' | ✅ 最佳答案' : ''}
        </div>
        ${(c.replies || []).map(r => `
          <div style="margin-top:8px;padding:8px 12px;background:#f8f9fa;border-radius:6px;border-left:3px solid #ddd;">
            <strong style="font-size:0.85rem;">👤 ${escapeHtml(r.user?.username || '匿名')}</strong>
            <span style="font-size:0.75rem;color:#999;margin-left:8px;">${formatTime(r.created_at)}</span>
            <p style="margin:4px 0 0;font-size:0.85rem;white-space:pre-wrap;">${escapeHtml(r.content)}</p>
          </div>
        `).join('')}
      </div>
    `).join('');

    container.innerHTML = commentsHtml || '<p style="color:#999;text-align:center;">暂无评论</p>';
  }

  // Expose handlers
  window.__likeDiscussion = () => handleLike();
  window.__submitComment = () => {
    const input = document.getElementById('comment-input');
    if (!input || !input.value.trim()) return;
    handleComment(input.value.trim());
    input.value = '';
  };
  window.__replyComment = (parentId) => {
    const content = prompt('回复内容:');
    if (!content) return;
    handleComment(content, parentId);
  };

  const html = `
    <div class="page">
      <div class="container">
        <a href="#/discussions" style="color:var(--primary,#4F46E5);font-size:0.9rem;">← 返回讨论区</a>
        <div class="card" style="margin-top:16px;padding:20px;">
          <h1 style="margin:0 0 8px;font-size:1.3rem;">${escapeHtml(discussion.title)}</h1>
          <div style="display:flex;gap:12px;font-size:0.85rem;color:#666;margin-bottom:16px;">
            <span>👤 ${escapeHtml(discussion.user?.username || '匿名')}</span>
            <span>🕐 ${formatTime(discussion.created_at)}</span>
            ${discussion.is_pinned ? '<span>📌 置顶</span>' : ''}
            ${discussion.is_locked ? '<span>🔒 已锁定</span>' : ''}
          </div>
          <div style="white-space:pre-wrap;line-height:1.6;font-size:0.95rem;">${escapeHtml(discussion.content)}</div>
          <div style="margin-top:16px;display:flex;gap:12px;align-items:center;">
            <button id="like-btn" class="btn" onclick="window.__likeDiscussion()" style="font-size:0.85rem;">
              🤍 点赞
            </button>
            <span id="like-count">${discussion.likes_count}</span>
            <span style="color:#999;font-size:0.85rem;">💬 ${discussion.comments_count} 条评论</span>
          </div>
        </div>

        <h2 style="font-size:1.1rem;margin:20px 0 12px;">评论</h2>
        ${isLoggedIn && !discussion.is_locked ? `
          <div class="card" style="margin-bottom:16px;padding:12px;">
            <textarea id="comment-input" placeholder="写下你的评论..." 
              style="width:100%;min-height:60px;border:1px solid #ddd;border-radius:6px;padding:8px;font-size:0.9rem;resize:vertical;"></textarea>
            <button class="btn btn-primary" onclick="window.__submitComment()" 
              style="margin-top:8px;font-size:0.85rem;">发表评论</button>
          </div>
        ` : ''}
        <div id="comments-container"></div>
      </div>
    </div>
  `;

  setTimeout(() => renderComments(), 0);
  return html;
}
