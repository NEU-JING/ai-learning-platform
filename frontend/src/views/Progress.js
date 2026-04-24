/**
 * 学习进度视图 - 包含学习路径可视化
 */

export default async function Progress({ store }) {
  await store.dispatch('fetchProgress');
  
  // 获取学习路径数据
  const learningPath = await window.$api.progress.getLearningPath();
  const stats = await window.$api.progress.getStats();
  
  const levelIcons = {
    beginner: '🌱',
    intermediate: '📚',
    advanced: '🚀',
    expert: '👑'
  };
  
  const levelNames = {
    beginner: '入门',
    intermediate: '进阶',
    advanced: '高级',
    expert: '专家'
  };

  // 生成学习路径节点
  const pathNodes = learningPath.map((course, index) => {
    const icon = levelIcons[course.level] || '📖';
    const levelName = levelNames[course.level] || course.level;
    const isCompleted = course.progress_percentage >= 100;
    const isInProgress = course.progress_percentage > 0 && !isCompleted;
    const statusIcon = isCompleted ? '✅' : isInProgress ? '🔄' : '⏳';
    
    return `
      <div class="path-node ${isCompleted ? 'completed' : ''} ${isInProgress ? 'in-progress' : ''}">
        <div class="path-connector" style="${index === 0 ? 'display:none' : ''}"></div>
        <div class="node-content" onclick="window.$router.push('/courses/${course.course_id}')">
          <div class="node-icon">${icon}</div>
          <div class="node-info">
            <h4>${course.course_title}</h4>
            <span class="node-level">${levelName}</span>
            <div class="node-progress">
              <div class="progress-bar">
                <div class="progress-bar-fill" style="width: ${course.progress_percentage}%"></div>
              </div>
              <span>${Math.round(course.progress_percentage)}%</span>
            </div>
          </div>
          <div class="node-status">${statusIcon}</div>
        </div>
      </div>
    `;
  }).join('');

  return `
    <div class="page progress-page">
      <nav class="navbar">
        <a href="#/" class="navbar-brand">
          <div class="navbar-logo">AI</div>
          <span>AI学习平台</span>
        </a>
        <ul class="navbar-nav">
          <li><a href="#/">首页</a></li>
          <li><a href="#/courses">课程</a></li>
          <li><a href="#/progress" class="active">进度</a></li>
        </ul>
        <div class="navbar-right">
          <span class="user-name">${store.state.user?.email || ''}</span>
          <a href="#" class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout'); return false;">退出</a>
        </div>
      </nav>

      <div class="container">
        <!-- 学习统计 -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-value">${stats.completed_chapters}</div>
            <div class="stat-label">已完成章节</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏱️</div>
            <div class="stat-value">${Math.round(stats.total_learning_minutes / 60)}</div>
            <div class="stat-label">学习时长(小时)</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🏆</div>
            <div class="stat-value">${stats.completed_courses}</div>
            <div class="stat-label">完成课程</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-value">${Math.round((stats.completed_chapters / Math.max(stats.total_chapters_accessed, 1)) * 100)}%</div>
            <div class="stat-label">总体进度</div>
          </div>
        </div>

        <!-- 学习路径可视化 -->
        <div class="learning-path-section">
          <h2>🛤️ 学习路径</h2>
          <p class="path-description">从入门到AI团队Leader的完整学习路径</p>
          <div class="learning-path">
            ${pathNodes}
          </div>
        </div>

        <!-- 成就系统 -->
        <div class="achievements-section">
          <h2>🏅 学习成就</h2>
          <div class="achievements-grid">
            ${stats.completed_courses >= 1 ? `
              <div class="achievement unlocked">
                <div class="achievement-icon">🎓</div>
                <div class="achievement-title">初学者</div>
                <div class="achievement-desc">完成第一门课程</div>
              </div>
            ` : `
              <div class="achievement locked">
                <div class="achievement-icon">🔒</div>
                <div class="achievement-title">初学者</div>
                <div class="achievement-desc">完成第一门课程解锁</div>
              </div>
            `}
            
            ${stats.completed_courses >= 2 ? `
              <div class="achievement unlocked">
                <div class="achievement-icon">💻</div>
                <div class="achievement-title">编码能手</div>
                <div class="achievement-desc">完成2门课程</div>
              </div>
            ` : `
              <div class="achievement locked">
                <div class="achievement-icon">🔒</div>
                <div class="achievement-title">编码能手</div>
                <div class="achievement-desc">完成2门课程解锁</div>
              </div>
            `}
            
            ${stats.completed_courses >= 4 ? `
              <div class="achievement unlocked">
                <div class="achievement-icon">👑</div>
                <div class="achievement-title">AI专家</div>
                <div class="achievement-desc">完成所有阶段</div>
              </div>
            ` : `
              <div class="achievement locked">
                <div class="achievement-icon">🔒</div>
                <div class="achievement-title">AI专家</div>
                <div class="achievement-desc">完成所有阶段解锁</div>
              </div>
            `}
          </div>
        </div>
      </div>
    </div>
  `;
}
