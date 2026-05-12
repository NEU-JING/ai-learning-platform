/**
 * 讨论区列表视图
 */

export default async function Discussion({ params }) {
  const store = window.$store;
  const courseId = params.id;
  let discussions = [];
  let course = null;
  let currentSort = 'newest';
  let loading = true;

  try {
    course = await store.$api.courses.get(courseId);
    discussions = await store.$api.discussions.list(courseId, currentSort);
  } catch (error) {
    console.error('加载讨论区失败:', error);
  } finally {
    loading = false;
  }

  const renderDiscussionItem = (discussion) => {
    const pinnedBadge = discussion.is_pinned 
      ? '<span class="discussion-badge pinned">📌 置顶</span>' 
      : '';
    
    const lockedBadge = discussion.is_locked 
      ? '<span class="discussion-badge locked">🔒 已锁定</span>' 
      : '';

    const timeAgo = formatTimeAgo(discussion.created_at);

    return `
      <div class="discussion-item" onclick="window.$router.push('/courses/${courseId}/discussions/${discussion.id}')">
        <div class="discussion-header">
          <img src="${discussion.user.avatar_url || '/assets/default-avatar.png'}" 
               alt="${discussion.user.username}" 
               class="discussion-avatar">
          <div class="discussion-meta">
            <span class="discussion-author">${discussion.user.username}</span>
            <span class="discussion-time">${timeAgo}</span>
          </div>
          ${pinnedBadge}
          ${lockedBadge}
        </div>
        <h3 class="discussion-title">${discussion.title}</h3>
        <p class="discussion-preview">${discussion.content_preview}</p>
        <div class="discussion-stats">
          <span class="stat-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
            </svg>
            ${discussion.likes_count}
          </span>
          <span class="stat-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            ${discussion.comments_count}
          </span>
        </div>
      </div>
    `;
  };

  const discussionsHtml = discussions.length > 0
    ? discussions.map(renderDiscussionItem).join('')
    : `
      <div class="empty-state">
        <div class="empty-icon">💬</div>
        <h3>暂无讨论</h3>
        <p>成为第一个发起讨论的人吧！</p>
      </div>
    `;

  const html = `
    <div class="page discussion-page">
      <nav class="navbar">
        <a href="#/" class="navbar-brand">
          <div class="navbar-logo">AI</div>
          <span>AI学习平台</span>
        </a>
        <ul class="navbar-nav">
          <li><a href="#/">首页</a></li>
          <li><a href="#/courses">课程</a></li>
          <li><a href="#/courses/${courseId}">${course ? course.title : '课程'}</a></li>
          <li><a href="#/courses/${courseId}/discussions" class="active">讨论区</a></li>
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
        <div class="discussion-header-section">
          <div class="discussion-breadcrumb">
            <a href="#/courses/${courseId}">← 返回课程</a>
          </div>
          <div class="discussion-title-section">
            <h1>💬 讨论区</h1>
            <p class="course-title">${course ? course.title : ''}</p>
          </div>
          <div class="discussion-actions">
            <div class="sort-options">
              <button class="sort-btn ${currentSort === 'newest' ? 'active' : ''}" 
                      onclick="changeSort('newest')">最新</button>
              <button class="sort-btn ${currentSort === 'popular' ? 'active' : ''}" 
                      onclick="changeSort('popular')">最热</button>
              <button class="sort-btn ${currentSort === 'pinned' ? 'active' : ''}" 
                      onclick="changeSort('pinned')">置顶</button>
            </div>
            ${store.state.user ? `
              <button class="btn btn-primary" onclick="showCreateModal()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                发起讨论
              </button>
            ` : ''}
          </div>
        </div>

        <div class="discussions-list">
          ${loading ? '<div class="loading">加载中...</div>' : discussionsHtml}
        </div>
      </div>

      ${store.state.user ? `
        <div id="create-modal" class="modal" style="display: none;">
          <div class="modal-overlay" onclick="hideCreateModal()"></div>
          <div class="modal-content">
            <div class="modal-header">
              <h2>发起新讨论</h2>
              <button class="modal-close" onclick="hideCreateModal()">×</button>
            </div>
            <form id="create-discussion-form" onsubmit="handleCreateSubmit(event)">
              <div class="form-group">
                <label for="discussion-title">标题</label>
                <input type="text" id="discussion-title" name="title" required 
                       placeholder="简短描述你的问题或话题" maxlength="200">
              </div>
              <div class="form-group">
                <label for="discussion-content">内容</label>
                <textarea id="discussion-content" name="content" required rows="8"
                          placeholder="详细描述你的问题、想法或经验..."></textarea>
              </div>
              <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="hideCreateModal()">取消</button>
                <button type="submit" class="btn btn-primary">发布讨论</button>
              </div>
            </form>
          </div>
        </div>
      ` : ''}
    </div>
  `;

  // 挂载方法到window
  window.showCreateModal = () => {
    const modal = document.getElementById('create-modal');
    if (modal) modal.style.display = 'block';
  };

  window.hideCreateModal = () => {
    const modal = document.getElementById('create-modal');
    if (modal) modal.style.display = 'none';
  };

  window.changeSort = async (sort) => {
    currentSort = sort;
    try {
      discussions = await store.$api.discussions.list(courseId, sort);
      // 重新渲染讨论列表
      const listContainer = document.querySelector('.discussions-list');
      if (listContainer) {
        listContainer.innerHTML = discussions.length > 0
          ? discussions.map(renderDiscussionItem).join('')
          : `
            <div class="empty-state">
              <div class="empty-icon">💬</div>
              <h3>暂无讨论</h3>
              <p>成为第一个发起讨论的人吧！</p>
            </div>
          `;
      }
      // 更新按钮状态
      document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.classList.remove('active');
      });
      const activeBtn = document.querySelector(`.sort-btn[onclick="changeSort('${sort}')"]`);
      if (activeBtn) activeBtn.classList.add('active');
    } catch (error) {
      console.error('切换排序失败:', error);
    }
  };

  window.handleCreateSubmit = async (event) => {
    event.preventDefault();
    const form = event.target;
    const title = form.title.value;
    const content = form.content.value;

    try {
      await store.$api.discussions.create(courseId, { title, content });
      hideCreateModal();
      form.reset();
      // 刷新列表
      discussions = await store.$api.discussions.list(courseId, currentSort);
      const listContainer = document.querySelector('.discussions-list');
      if (listContainer) {
        listContainer.innerHTML = discussions.map(renderDiscussionItem).join('');
      }
    } catch (error) {
      alert('发布失败: ' + error.message);
    }
  };

  return html;
}

// 辅助函数：格式化时间
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
