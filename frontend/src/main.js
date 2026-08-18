/**
 * AI学习平台 - 主入口
 * 现代化SPA架构，使用原生JavaScript + 模块化设计
 */

import { Router } from './core/router.js';
import { Store } from './core/store.js';
import { API } from './services/api.js';
import { AuthService } from './services/auth.js';
import { progressBar } from './components/ProgressBar.js';
import { lazyImage } from './components/LazyImage.js';
import { themeManager } from './services/theme.js';
import { initGlobalErrorHandler, showGlobalError } from './components/ErrorBoundary.js';
import { initAnalytics } from './services/analytics.js';
import { MobileNav, BottomNav } from './components/MobileNav.js';

// 全局状态管理
const store = new Store({
  state: {
    user: null,
    token: localStorage.getItem('access_token'),
    courses: [],
    currentCourse: null,
    currentChapter: null,
    progress: [],
    loading: false,
    notifications: []
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user;
    },
    SET_TOKEN(state, token) {
      state.token = token;
      if (token) {
        localStorage.setItem('access_token', token);
      } else {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    },
    SET_COURSES(state, courses) {
      state.courses = courses;
    },
    SET_CURRENT_COURSE(state, course) {
      state.currentCourse = course;
    },
    SET_CURRENT_CHAPTER(state, chapter) {
      state.currentChapter = chapter;
    },
    SET_PROGRESS(state, progress) {
      state.progress = progress;
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    ADD_NOTIFICATION(state, notification) {
      state.notifications.push({
        id: Date.now(),
        ...notification
      });
    },
    REMOVE_NOTIFICATION(state, id) {
      state.notifications = state.notifications.filter(n => n.id !== id);
    }
  },
  
  actions: {
    async login({ commit }, credentials) {
      commit('SET_LOADING', true);
      try {
        const response = await API.auth.login(credentials);
        commit('SET_TOKEN', response.access_token);
        // 同时存储 refresh_token
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token);
        }
        commit('SET_USER', { email: credentials.email });
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async logout({ commit }) {
      commit('SET_TOKEN', null);
      commit('SET_USER', null);
      commit('SET_PROGRESS', []);
    },
    
    async fetchCourses({ commit }) {
      commit('SET_LOADING', true);
      try {
        const response = await API.courses.list();
        // API returns PaginatedResponse { items, total, page, ... }
        const courses = Array.isArray(response) ? response : (response.items || []);
        commit('SET_COURSES', courses);
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async fetchCourse({ commit }, courseId) {
      commit('SET_LOADING', true);
      try {
        const course = await API.courses.get(courseId);
        commit('SET_CURRENT_COURSE', course);
        return course;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async fetchProgress({ commit, state }) {
      if (!state.token) return;
      try {
        const progress = await API.progress.list();
        commit('SET_PROGRESS', progress);
      } catch (error) {
        console.error('获取进度失败:', error);
      }
    },
    
    async updateProgress({ dispatch }, { chapterId, status, courseId }) {
      await API.progress.update(chapterId, { status });
      // Analytics tracking
      try {
        const { trackChapterStart, trackChapterComplete } = await import('../services/analytics.js');
        if (status === 'in_progress') trackChapterStart(chapterId, courseId);
        if (status === 'completed') trackChapterComplete(chapterId, courseId);
      } catch (e) { /* analytics should never break the app */ }
      await dispatch('fetchProgress');
    }
  }
});

// 路由配置
const routes = [
  {
    path: '/',
    component: () => import('./views/Home.js'),
    title: '首页'
  },
  {
    path: '/courses',
    component: () => import('./views/Courses.js'),
    title: '全部课程'
  },
  {
    path: '/courses/:id',
    component: () => import('./views/CourseDetail.js'),
    title: '课程详情'
  },
  {
    path: '/chapters/:id',
    component: () => import('./views/Chapter.js'),
    title: '章节学习'
  },
  {
    path: '/labs/:id',
    component: () => import('./views/Lab.js'),
    title: '代码实验室'
  },
  {
    path: '/progress',
    component: () => import('./views/Progress.js'),
    title: '学习进度',
    requiresAuth: true
  },
  {
    path: '/discussions',
    component: () => import('./views/Discussion.js'),
    title: '讨论区'
  },
  {
    path: '/discussions/:id',
    component: () => import('./views/DiscussionDetail.js'),
    title: '讨论详情'
  },
  {
    path: '/login',
    component: () => import('./views/Login.js'),
    title: '登录',
    guestOnly: true
  },
  {
    path: '/register',
    component: () => import('./views/Register.js'),
    title: '注册',
    guestOnly: true
  },
  {
    path: '*',
    component: () => import('./views/NotFound.js'),
    title: '页面不存在'
  }
];

// 初始化路由
const router = new Router({
  routes,
  mode: 'hash',
  beforeEach: (to, from, next) => {
    // 路由切换时开始进度条
    progressBar.start();
    
    const isAuthenticated = !!store.state.token;
    
    // 需要登录的页面
    if (to.requiresAuth && !isAuthenticated) {
      next('/login');
      return;
    }
    
    // 已登录用户访问 /login 或 /register 时重定向到首页
    if (isAuthenticated && (to.path === '/login' || to.path === '/register')) {
      next('/');
      return;
    }
    
    // 仅限游客访问的页面（guestOnly 标记，兼容旧逻辑）
    if (to.guestOnly && isAuthenticated) {
      next('/');
      return;
    }
    
    next();
  },
  afterEach: (to) => {
    document.title = to.title ? `${to.title} - AI学习平台` : 'AI学习平台';
    
    // 路由切换完成后结束进度条
    progressBar.done();
    
    // 刷新懒加载图片
    setTimeout(() => lazyImage.refresh(), 100);
  }
});

// 注册Store单例 + 全局依赖注入
Store.setInstance(store);
window.$store = store;
window.$router = router;
window.$api = API;

// 初始化应用
async function initApp() {
  // 初始化全局错误处理器
  initGlobalErrorHandler();
  
  // 初始化主题管理器
  themeManager.init();
  
  // 初始化用户行为分析
  initAnalytics();
  
  // 初始化懒加载
  lazyImage.observeAll('img[data-src]');
  
  // 初始化移动端导航
  if (window.innerWidth <= 768) {
    const mobileNav = new MobileNav();
    const mobileNavEl = mobileNav.render();
    document.body.appendChild(mobileNavEl);
    
    const bottomNav = new BottomNav();
    const bottomNavEl = bottomNav.render();
    document.body.appendChild(bottomNavEl);
  }
  
  // 检查登录状态
  if (store.state.token) {
    try {
      // Fetch real user info from API
      const user = await API.auth.me();
      if (user) {
        store.commit('SET_USER', user);
      }
    } catch (error) {
      // Token invalid — logout
      console.warn('Token验证失败，自动登出:', error.message);
      store.dispatch('logout');
    }
  }
  
  // 启动路由
  try {
    await router.init();
  } catch (error) {
    console.error('路由初始化失败:', error);
    showGlobalError('应用初始化失败，请刷新重试');
  }
  
  console.log('🚀 AI学习平台已启动');
}

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', initApp);
