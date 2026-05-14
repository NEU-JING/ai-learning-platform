/**
 * 首页视图
 */

import { AuthService } from '../services/auth.js';

export default async function Home() {
  const store = window.$store;
  const isAuthenticated = AuthService.isAuthenticated();
  const courses = store?.state?.courses || [];
  
  if (courses.length === 0) {
    await store?.dispatch('fetchCourses');
  }

  const levelColors = {
    beginner: { bg: '#c6f6d5', color: '#22543d', text: '入门' },
    intermediate: { bg: '#feebc8', color: '#744210', text: '进阶' },
    advanced: { bg: '#fed7d7', color: '#742a2a', text: '高级' },
    expert: { bg: '#e9d8fd', color: '#553c9a', text: '专家' }
  };

  const courseCards = courses.map(course => {
    const level = levelColors[course.level] || levelColors.beginner;
    return `
      <div class="course-card" onclick="window.$router.push('/courses/${course.id}')">
        <div class="course-level" style="background: ${level.bg}; color: ${level.color};">
          ${level.text}
        </div>
        <h3 class="course-title">${course.title}</h3>
        <p class="course-desc">${course.description || ''}</p>
        <div class="course-meta">
          <span>⏱️ ${course.duration_hours}小时</span>
          <span>📚 ${course.chapter_count || 0}章节</span>
        </div>
      </div>
    `;
  }).join('');

  return `
    <div class="page home-page">
      <nav class="navbar">
        <a href="#/" class="navbar-brand">
          <div class="navbar-logo">AI</div>
          <span>AI学习平台</span>
        </a>
        <ul class="navbar-nav">
          <li><a href="#/">首页</a></li>
          <li><a href="#/courses">课程</a></li>
          ${isAuthenticated ? `
            <li><a href="#/progress">进度</a></li>
          ` : ''}
        </ul>
        <div class="navbar-right">
          ${isAuthenticated && store?.state?.user ? `
            <span class="user-name">${store.state.user.email}</span>
            <a href="#" class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout'); window.location.hash = '#/'; return false;">退出</a>
          ` : isAuthenticated ? `
            <a href="#" class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout'); window.location.hash = '#/'; return false;">退出</a>
          ` : `
            <a href="#/login" class="btn btn-secondary btn-sm">登录</a>
            <a href="#/register" class="btn btn-primary btn-sm">注册</a>
          `}
        </div>
      </nav>

      <header class="hero">
        <h1>🚀 从入门到AI团队Leader</h1>
        <p class="subtitle">系统化AI学习平台 · 在线实验环境 · 完整知识体系</p>
        <a href="#/courses" class="btn btn-primary btn-lg">开始学习</a>
      </header>

      <div class="container">
        <h2 class="section-title">📚 热门课程</h2>
        <div class="courses-grid">
          ${courseCards || '<div class="loading">加载课程中...</div>'}
        </div>
      </div>
    </div>
  `;
}
