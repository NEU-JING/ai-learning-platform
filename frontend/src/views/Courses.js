/**
 * 课程列表视图 - 带骨架屏加载
 */

import { Skeleton } from '../components/Skeleton.js';
import { AuthService } from '../services/auth.js';

export default async function Courses() {
  const store = window.$store;
  const isAuthenticated = AuthService.isAuthenticated();
  const container = document.createElement('div');
  container.className = 'page courses-page';
  
  // 渲染骨架屏
  const renderSkeleton = () => {
    const skeletonGrid = document.createElement('div');
    skeletonGrid.className = 'courses-grid';
    
    // 创建8个课程卡片骨架
    for (let i = 0; i < 8; i++) {
      skeletonGrid.appendChild(Skeleton.courseCard());
    }
    
    return skeletonGrid;
  };
  
  // 渲染导航栏
  const renderNavbar = () => `
    <nav class="navbar">
      <a href="#" class="navbar-brand" data-nav="/">
        <div class="navbar-logo">AI</div>
        <span>AI学习平台</span>
      </a>
      <ul class="navbar-nav">
        <li><a href="#" data-nav="/">首页</a></li>
        <li><a href="#" data-nav="/courses">课程</a></li>
      </ul>
      <div class="navbar-right">
        ${isAuthenticated && store?.state?.user ? `
          <span class="user-name">${store.state.user.email}</span>
          <a href="#" class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout'); window.location.hash = '#/'; return false;">退出</a>
        ` : isAuthenticated ? `
          <a href="#" class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout'); window.location.hash = '#/'; return false;">退出</a>
        ` : `
          <a href="#" class="btn btn-secondary btn-sm" data-nav="/login">登录</a>
          <a href="#" class="btn btn-primary btn-sm" data-nav="/register">注册</a>
        `}
      </div>
    </nav>
  `;
  
  // 渲染页面头部
  const renderHeader = () => `
    <div class="page-header">
      <h1>📚 全部课程</h1>
      <p>从Python基础到AI团队领导力，系统化学习路径</p>
    </div>
  `;
  
  // 渲染课程卡片
  const renderCourseCard = (course) => {
    const levelColors = {
      beginner: { bg: '#c6f6d5', color: '#22543d', text: '入门' },
      intermediate: { bg: '#feebc8', color: '#744210', text: '进阶' },
      advanced: { bg: '#fed7d7', color: '#742a2a', text: '高级' },
      expert: { bg: '#e9d8fd', color: '#553c9a', text: '专家' }
    };
    
    const level = levelColors[course.level] || levelColors.beginner;
    
    return `
      <div class="course-card" data-course-id="${course.id}">
        <div class="course-level" style="background: ${level.bg}; color: ${level.color};">
          ${level.text}
        </div>
        <h3 class="course-title">${course.title}</h3>
        <p class="course-desc">${course.description || ''}</p>
        <div class="course-meta">
          <span>⏱️ ${course.duration_hours}小时</span>
          <span>📚 ${course.chapters_count || 0}章节</span>
        </div>
      </div>
    `;
  };
  
  // 渲染课程列表
  const renderCourseList = (courses) => {
    const grid = document.createElement('div');
    grid.className = 'courses-grid';
    grid.innerHTML = courses.map(renderCourseCard).join('');
    
    // 绑定点击事件
    grid.querySelectorAll('.course-card').forEach(card => {
      card.addEventListener('click', () => {
        const courseId = card.dataset.courseId;
        window.$router.push(`/courses/${courseId}`);
      });
    });
    
    return grid;
  };
  
  // 构建初始页面（骨架屏）
  container.innerHTML = `
    ${renderNavbar()}
    <div class="container">
      ${renderHeader()}
      <div id="courses-content"></div>
    </div>
  `;
  
  const contentContainer = container.querySelector('#courses-content');
  
  // 显示骨架屏
  contentContainer.appendChild(renderSkeleton());
  
  // 异步加载数据
  store?.dispatch('fetchCourses').then(() => {
    const courses = store?.state?.courses;
    
    // 替换骨架屏为实际内容
    contentContainer.innerHTML = '';
    contentContainer.appendChild(renderCourseList(courses));
  });
  
  return container;
}
