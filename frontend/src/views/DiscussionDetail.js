/**
 * 讨论详情视图
 */

export default async function DiscussionDetail({ params, store }) {
  const discussionId = params.id;
  let discussion = null;
  let loading = true;
  let replyingTo = null;

  try {
    discussion = await store.$api.discussions.get(discussionId);
  } catch (error) {
    console.error('加载讨论详情失败:', error);
  } finally {
    loading = false;
  }

  const isOwner = store.state.user && discussion && store.state.user.id === discussion.user.id;
  const canEdit = isOwner || (store.state.user && ['admin', 'teacher'].includes(store.state.user.role));

  const renderComment = (comment, isReply = false) => {
    const timeAgo = formatTimeAgo(comment.created_at);
    const isSolution = comment.is_solution ? '<span class="solution-badge">✓ 解决方案</span>' : '';
    
    const replyButton = store.state.user && !isReply && !discussion.is_locked
      ? `<button class="reply-btn" onclick="startReply(${comment.id})">回复</button>`
      : '';

    const replyForm = replyingTo === comment.id
      ? `
        <div class="reply-form" id="reply-form-${comment.id}">
          <textarea id="reply-content-${comment.id}" rows="3" placeholder="写下你的回复..."></textarea>
          <div class="reply-actions">
            <button class="btn btn-secondary btn-sm" onclick="cancelReply()">取消</button>
            <button class="btn btn-primary btn-sm" onclick="submitReply(${comment.id})">提交回复</button>
          </div>
        </div>
      `
      : '';

    const repliesHtml = comment.replies && comment.replies.length > 0
      ? `<div class="replies">${comment.replies.map(r => renderComment(r, true)).join('')}</div>`
      : '';

    return `
      <div class="comment-item ${isReply ? 'reply' : ''}">
        <div class="comment-header">
          <img src="${comment.user.avatar_url || '/assets/default-avatar.png'}" 
               alt="${comment.user.username}" 
               class="comment-avatar">
          <div class="comment-meta">
            <span class="comment-author">${comment.user.username}</span>
            <span class="comment-time">${timeAgo}</span>
            ${isSolution}
          </div>
        </div>
        <div class="comment-content">${escapeHtml(comment.content)}</div>
        <div class="comment-actions">
          ${replyButton}
        </div>
        ${replyForm}
        ${repliesHtml}
      </div>
    `;
  };

  const commentsHtml = discussion && discussion.comments.length > 0
    ? discussion.comments.map(c => renderComment(c)).join('')
    : `
      <div class="empty-comments">
        <p>暂无评论，来说点什么吧！</p>
      </div>
    `;

  const html = `
    <div class="page discussion-detail-page">
      <nav class="navbar">
        <a href="#/" class="navbar-brand">
          <div class="navbar-logo">AI</div>
          <span>AI学习平台</span>
        </a>
        <ul class="navbar-nav">
          <li><a href="#/">首页</a></li>
          <li><a href="#/courses">课程</a></li>
          ${discussion ? `<li><a href="#/courses/${discussion.course_id}">课程详情</a></li>` : ''}
          ${discussion ? `<li><a href="#/courses/${discussion.course_id}/discussions">讨论区</a></li>` : ''}
        </ul>
        <div class="navbar-right">
          ${store.state.user ? `
            <span class="user-name">${store.state.user.email || store.state.user.username}</span>
            <a href="#" class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout'); return false;">退出</a>
          ` : `
            <a href="#/login" class="btn btn-secondary btn-sm">登录</a>
          `}
        </div>
      </nav>

      <div class="container">
        ${loading ? '<div class="loading">加载中...</div>' : ''}
        
        ${discussion ? `
          <div class="discussion-detail">
            <div class="discussion-breadcrumb">
              <a href="#/courses/${discussion.course_id}/discussions">← 返回讨论列表</a>
            </div>

            <div class="discussion-main">
              <div class="discussion-header-detail">
                <img src="${discussion.user.avatar_url || '/assets/default-avatar.png'}" 
                     alt="${discussion.user.username}" 
                     class="discussion-author-avatar">
                <div class="discussion-author-info">
                  <span class="author-name">${discussion.user.username}</span>
                  <span class="publish-time">${formatTimeAgo(discussion.created_at)}</span>
                </div>
                ${discussion.is_pinned ? '<span class="badge pinned">📌 置顶</span>' : ''}
                ${discussion.is_locked ? '<span class="badge locked">🔒 已锁定</span>' : ''}
              </div>

              <h1 class="discussion-detail-title">${discussion.title}</h1>
              <div class="discussion-detail-content">${escapeHtml(discussion.content)}</div>

              <div class="discussion-detail-actions">
                <button class="action-btn ${discussion.liked ? 'liked' : ''}" onclick="handleLike()">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                  </svg>
                  <span id="like-count">${discussion.likes_count}</span>
                </button>
                ${canEdit ? `
                  <button class="action-btn" onclick="showEditModal()">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                    编辑
                  </button>
                  <button class="action-btn danger" onclick="handleDelete()">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                    删除
                  </button>
                ` : ''}
              </div>
            </div>

            <div class="comments-section">
              <h2 class="comments-title">
                💬 评论 (${discussion.comments_count})
                ${discussion.is_locked ? '<span class="locked-hint">（讨论已锁定）</span>' : ''}
              </h2>

              ${store.state.user && !discussion.is_locked ? `
                <div class="comment-form">
                  <div class="comment-form-header">
                    <img src="${store.state.user.avatar_url || '/assets/default-avatar.png'}" 
                         alt="${store.state.user.username}" 
                         class="current-user-avatar">
                    <span>${store.state.user.username}</span>
                  </div>
                  <textarea id="main-comment" rows="4" 
                            placeholder="分享你的想法..."
                            ${discussion.is_locked ? 'disabled' : ''}></textarea>
                  <div class="comment-form-actions">
                    <button class="btn btn-primary" onclick="submitMainComment()" 
                            ${discussion.is_locked ? 'disabled' : ''}>
                      发表评论
                    </button>
                  </div>
                </div>
              ` : !store.state.user ? `
                <div class="login-to-comment">
                  <p>请<a href="#/login">登录</a>后参与讨论</p>
                </div>
              ` : ''}

              <div class="comments-list">
                ${commentsHtml}
              </div>
            </div>
          </div>
        ` : ''}
      </div>

      ${canEdit ? `
        <div id="edit-modal" class="modal" style="display: none;">
          <div class="modal-overlay" onclick="hideEditModal()"></div>
          <div class="modal-content">
            <div class="modal-header">
              <h2>编辑讨论</h2>
              <button class="modal-close" onclick="hideEditModal()">×</button>
            </div>
            <form id="edit-discussion-form" onsubmit="handleEditSubmit(event)">
              <div class="form-group">
                <label for="edit-title">标题</label>
                <input type="text" id="edit-title" name="title" required 
                       value="${discussion ? discussion.title : ''}" maxlength="200">
              </div>
              <div class="form-group">
                <label for="edit-content">内容</label>
                <textarea id="edit-content" name="content" required rows="8">${discussion ? discussion.content : ''}</textarea>
              </div>
              <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="hideEditModal()">取消</button>
                <button type="submit" class="btn btn-primary">保存修改</button>
              </div>
            </form>
          </div>
        </div>
      ` : ''}
    </div>
  `;

  // 挂载方法到window
  window.showEditModal = () => {
    const modal = document.getElementById('edit-modal');
    if (modal) modal.style.display = 'block';
  };

  window.hideEditModal = () => {
    const modal = document.getElementById('edit-modal');
    if (modal) modal.style.display = 'none';
  };

  window.handleEditSubmit = async (event) => {
    event.preventDefault();
    const form = event.target;
    const title = form.title.value;
    const content = form.content.value;

    try {
      await store.$api.discussions.update(discussionId, { title, content });
      hideEditModal();
      // 刷新页面
      discussion = await store.$api.discussions.get(discussionId);
      window.$router.replace(window.location.hash.slice(1));
    } catch (error) {
      alert('更新失败: ' + error.message);
    }
  };

  window.handleDelete = async () => {
    if (!confirm('确定要删除这个讨论吗？此操作不可撤销。')) return;
    
    try {
      await store.$api.discussions.delete(discussionId);
      window.$router.push(`/courses/${discussion.course_id}/discussions`);
    } catch (error) {
      alert('删除失败: ' + error.message);
    }
  };

  window.handleLike = async () => {
    if (!store.state.user) {
      alert('请先登录');
      window.$router.push('/login');
      return;
    }

    try {
      const result = await store.$api.discussions.like(discussionId);
      const likeCountEl = document.getElementById('like-count');
      if (likeCountEl) {
        likeCountEl.textContent = result.likes_count;
      }
    } catch (error) {
      console.error('点赞失败:', error);
    }
  };

  window.submitMainComment = async () => {
    const textarea = document.getElementById('main-comment');
    const content = textarea.value.trim();
    
    if (!content) {
      alert('请输入评论内容');
      return;
    }

    try {
      await store.$api.discussions.createComment(discussionId, content);
      textarea.value = '';
      // 刷新讨论
      discussion = await store.$api.discussions.get(discussionId);
      window.$router.replace(window.location.hash.slice(1));
    } catch (error) {
      alert('评论失败: ' + error.message);
    }
  };

  window.startReply = (commentId) => {
    replyingTo = commentId;
    // 重新渲染以显示回复表单
    window.$router.replace(window.location.hash.slice(1));
  };

  window.cancelReply = () => {
    replyingTo = null;
    window.$router.replace(window.location.hash.slice(1));
  };

  window.submitReply = async (commentId) => {
    const textarea = document.getElementById(`reply-content-${commentId}`);
    const content = textarea.value.trim();
    
    if (!content) {
      alert('请输入回复内容');
      return;
    }

    try {
      await store.$api.discussions.createComment(discussionId, content, commentId);
      replyingTo = null;
      // 刷新讨论
      discussion = await store.$api.discussions.get(discussionId);
      window.$router.replace(window.location.hash.slice(1));
    } catch (error) {
      alert('回复失败: ' + error.message);
    }
  };

  return html;
}

// 辅助函数
function formatTimeAgo(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (seconds < 60) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 30) return `${days}天前`;
  
  return date.toLocaleDateString('zh-CN');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML.replace(/\n/g, '<br>');
}
