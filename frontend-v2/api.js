/**
 * API Client - 连接后端真实数据
 * 基于现有后端 API 封装
 */

const API_BASE = '/api/v1';

// 请求拦截器 - 自动添加 JWT Token
const apiRequest = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };
  
  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }
  
  try {
    const response = await fetch(`${API_BASE}${url}`, config);
    
    if (response.status === 401) {
      // Token 过期，尝试刷新
      const refreshed = await refreshToken();
      if (refreshed) {
        // 重试原请求
        return apiRequest(url, options);
      } else {
        // 刷新失败，跳转登录
        window.location.href = '/#/login';
        throw new Error('Session expired');
      }
    }
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
    
    // 204 No Content
    if (response.status === 204) return null;
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// Token 刷新
const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;
  
  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      return true;
    }
    return false;
  } catch {
    return false;
  }
};

/**
 * 认证 API
 */
const authAPI = {
  login: (email, password) => apiRequest('/auth/login', {
    method: 'POST',
    body: { email, password },
  }),
  
  register: (email, username, password) => apiRequest('/auth/register', {
    method: 'POST',
    body: { email, username, password },
  }),
  
  refresh: () => apiRequest('/auth/refresh', {
    method: 'POST',
    body: { refresh_token: localStorage.getItem('refresh_token') },
  }),
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    return Promise.resolve();
  },
  
  me: () => apiRequest('/auth/me'),
};

/**
 * 课程 API
 */
const coursesAPI = {
  // 获取课程列表
  getList: (params = {}) => {
    const query = new URLSearchParams({
      page: params.page || 1,
      per_page: params.perPage || 20,
      ...(params.category && { category: params.category }),
      ...(params.level && { level: params.level }),
    }).toString();
    return apiRequest(`/courses?${query}`);
  },
  
  // 获取课程详情
  getDetail: (courseId) => apiRequest(`/courses/${courseId}`),
  
  // 获取课程章节
  getChapters: (courseId) => apiRequest(`/courses/${courseId}/chapters`),
  
  // 获取章节详情
  getChapter: (chapterId) => apiRequest(`/courses/chapters/${chapterId}`),
  
  // 获取章节的实验
  getChapterLab: (chapterId) => apiRequest(`/courses/chapters/${chapterId}/lab`),
};

/**
 * 实验 API
 */
const labsAPI = {
  // 获取实验详情
  getDetail: (labId) => apiRequest(`/labs/${labId}`),
  
  // 提交实验代码
  submit: (labId, code) => apiRequest(`/labs/${labId}/submit`, {
    method: 'POST',
    body: { code },
  }),
  
  // 执行代码（沙盒）
  execute: (code, language = 'python', timeout = 30) => 
    apiRequest('/labs/execute', {
      method: 'POST',
      body: { code, language, timeout },
    }),
  
  // 获取提交历史
  getSubmissions: (labId) => apiRequest(`/labs/${labId}/submissions`),
};

/**
 * 学习进度 API
 */
const progressAPI = {
  // 获取总体进度
  getStats: () => apiRequest('/progress/stats'),
  
  // 获取课程进度
  getCourseProgress: (courseId) => apiRequest(`/progress/courses/${courseId}`),
  
  // 更新章节进度
  updateChapter: (chapterId, progress) => apiRequest(`/progress/chapters/${chapterId}`, {
    method: 'POST',
    body: { progress_percent: progress },
  }),
  
  // 获取最近活动
  getRecent: () => apiRequest('/progress/recent'),
  
  // 获取连续学习天数
  getStreak: () => apiRequest('/progress/streak'),
};

/**
 * 讨论区 API
 */
const discussionsAPI = {
  // 获取章节讨论
  getChapterDiscussions: (chapterId, params = {}) => {
    const query = new URLSearchParams({
      page: params.page || 1,
      per_page: params.perPage || 20,
    }).toString();
    return apiRequest(`/chapters/${chapterId}/discussions?${query}`);
  },
  
  // 发布讨论
  create: (chapterId, content) => apiRequest('/discussions', {
    method: 'POST',
    body: { chapter_id: chapterId, content },
  }),
  
  // 回复讨论
  reply: (discussionId, content) => apiRequest(`/discussions/${discussionId}/replies`, {
    method: 'POST',
    body: { content },
  }),
};

// 导出 API
window.api = {
  auth: authAPI,
  courses: coursesAPI,
  labs: labsAPI,
  progress: progressAPI,
  discussions: discussionsAPI,
};
