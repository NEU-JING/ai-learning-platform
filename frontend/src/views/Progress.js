/**
 * 学习进度视图 v2.0 — 现代化设计
 * 横向时间线 + 环形进度 + 暗色统计卡片
 */

export default async function Progress() {
  const store = window.$store;
  await store?.dispatch('fetchProgress');

  let learningPath = [];
  let stats = {};

  try {
    learningPath = await window.$api.progress.getLearningPath();
  } catch (e) {
    learningPath = [];
  }
  try {
    stats = await window.$api.progress.getStats();
  } catch (e) {
    stats = { completed_chapters: 0, total_learning_minutes: 0, completed_courses: 0, total_chapters_accessed: 0 };
  }

  const totalHours = Math.round((stats.total_learning_minutes || 0) / 60);
  const overallPct = stats.total_chapters_accessed > 0
    ? Math.round((stats.completed_chapters / stats.total_chapters_accessed) * 100)
    : 0;

  // SVG circular progress
  function circleProgress(pct, size = 80, stroke = 6) {
    const r = (size - stroke) / 2;
    const circ = 2 * Math.PI * r;
    const offset = circ - (pct / 100) * circ;
    return `
      <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
        <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none"
          stroke="var(--border-color)" stroke-width="${stroke}"/>
        <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none"
          stroke="var(--bg-primary)" stroke-width="${stroke}"
          stroke-linecap="round"
          stroke-dasharray="${circ}" stroke-dashoffset="${offset}"
          transform="rotate(-90 ${size/2} ${size/2})"
          style="transition: stroke-dashoffset 1s ease;"/>
        <text x="${size/2}" y="${size/2}" text-anchor="middle" dy="0.35em"
          fill="var(--text-primary)" font-size="${size*0.25}" font-weight="700">
          ${pct}%
        </text>
      </svg>`;
  }

  // Phase icons
  const phaseIcons = ['🐍', '📐', '🤖', '🧠', '💬', '⚙️'];
  const phaseColors = ['#10b981', '#8b5cf6', '#3b82f6', '#f59e0b', '#ef4444', '#06b6d4'];

  // Build horizontal timeline
  const timelineNodes = learningPath.map((course, i) => {
    const pct = Math.round(course.progress_percentage || 0);
    const isComplete = pct >= 100;
    const isActive = pct > 0 && !isComplete;
    const color = phaseColors[i % phaseColors.length];
    const icon = phaseIcons[i % phaseIcons.length];

    return `
      <div class="tl-node ${isComplete ? 'completed' : ''} ${isActive ? 'active' : ''}"
           onclick="window.$router.push('/courses/${course.course_id}')">
        <div class="tl-icon" style="background:${color}20;border-color:${color};">
          <span>${icon}</span>
          ${isComplete ? '<div class="tl-check">✓</div>' : ''}
        </div>
        <div class="tl-body">
          <div class="tl-title">${course.course_title.replace(/^Phase \d+:?\s*/, '')}</div>
          <div class="tl-bar-track">
            <div class="tl-bar-fill" style="width:${pct}%;background:${color};"></div>
          </div>
          <div class="tl-meta">${pct}% · ${course.total_chapters}章</div>
        </div>
      </div>`;
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
          <li><a href="#/progress" class="active">学习进度</a></li>
        </ul>
        <div class="navbar-right">
          <span class="user-name">${store.state.user?.email || ''}</span>
          <a href="#" class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout'); return false;">退出</a>
        </div>
      </nav>

      <div class="container">
        <!-- Hero stats row -->
        <div class="stats-hero">
          <div class="stats-hero-main">
            ${circleProgress(overallPct, 120, 8)}
            <div class="stats-hero-label">总体进度</div>
          </div>
          <div class="stats-hero-cards">
            <div class="stat-pill">
              <span class="stat-pill-icon">📚</span>
              <div>
                <div class="stat-pill-val">${stats.completed_chapters || 0}</div>
                <div class="stat-pill-label">已完成章节</div>
              </div>
            </div>
            <div class="stat-pill">
              <span class="stat-pill-icon">⏱️</span>
              <div>
                <div class="stat-pill-val">${totalHours}h</div>
                <div class="stat-pill-label">学习时长</div>
              </div>
            </div>
            <div class="stat-pill">
              <span class="stat-pill-icon">🏆</span>
              <div>
                <div class="stat-pill-val">${stats.completed_courses || 0}</div>
                <div class="stat-pill-label">完成课程</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Learning path timeline -->
        <div class="section-header">
          <h2>🛤️ 学习路径</h2>
          <span class="section-subtitle">从Python到AI工程的完整路线</span>
        </div>
        <div class="tl-container">
          ${timelineNodes || '<div class="tl-empty">暂无课程</div>'}
        </div>

        <!-- Achievements -->
        <div class="section-header" style="margin-top:2rem;">
          <h2>🏅 成就</h2>
        </div>
        <div class="achievement-row">
          ${achievementCard('🎓', '初学者', '完成第一门课程', (stats.completed_courses || 0) >= 1)}
          ${achievementCard('💻', '编码能手', '完成2门课程', (stats.completed_courses || 0) >= 2)}
          ${achievementCard('🧠', '深度学习', '完成4门课程', (stats.completed_courses || 0) >= 4)}
          ${achievementCard('👑', 'AI全栈', '完成全部课程', (stats.completed_courses || 0) >= 6)}
        </div>
      </div>
    </div>`;
}

function achievementCard(icon, title, desc, unlocked) {
  return `
    <div class="ach-card ${unlocked ? 'unlocked' : 'locked'}">
      <div class="ach-icon">${unlocked ? icon : '🔒'}</div>
      <div class="ach-title">${title}</div>
      <div class="ach-desc">${unlocked ? desc : '???'}</div>
    </div>`;
}
