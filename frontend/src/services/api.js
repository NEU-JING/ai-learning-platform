/**
 * API客户端 - 统一封装HTTP请求
 * 支持拦截器、错误处理、Token管理
 * 从环境变量读取API配置
 */

import { ENV } from '../config/env.js';
import { showToast } from '../components/Toast.js';
import { showLoading, hideLoading } from '../components/Loading.js';

// 使用环境配置中的API基础URL，支持开发/生产环境自动切换
const API_BASE_URL = ENV.API_BASE_URL || 'http://localhost:8000/api/v1';

// 请求拦截器
const requestInterceptors = [];
// 响应拦截器
const responseInterceptors = [];

class APIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // 添加请求拦截器
  addRequestInterceptor(interceptor) {
    requestInterceptors.push(interceptor);
  }

  // 添加响应拦截器
  addResponseInterceptor(interceptor) {
    responseInterceptors.push(interceptor);
  }

  // 获取Token
  getToken() {
    return localStorage.getItem('access_token');
  }

  // 构建请求配置
  async buildConfig(options = {}) {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    // 添加认证头
    const token = this.getToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // 执行请求拦截器
    for (const interceptor of requestInterceptors) {
      await interceptor(config);
    }

    return config;
  }

  // 处理响应
  async handleResponse(response) {
    // 执行响应拦截器
    for (const interceptor of responseInterceptors) {
      await interceptor(response);
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`
      }));
      
      // 处理特定错误
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        showToast('登录已过期，请重新登录', 'warning');
        window.location.hash = '#/login';
      } else {
        showToast(error.detail || '请求失败', 'error');
      }
      
      throw new Error(error.detail || error.message || '请求失败');
    }

    // 204 No Content
    if (response.status === 204) {
      return null;
    }

    return response.json();
  }

  // GET请求
  async get(endpoint, params = {}) {
    showLoading();
    try {
      const url = new URL(this.baseURL + endpoint, window.location.origin);
      
      // 添加查询参数
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          url.searchParams.append(key, params[key]);
        }
      });

      const config = await this.buildConfig({
        method: 'GET'
      });

      const response = await fetch(url.toString(), config);
      return this.handleResponse(response);
    } catch (e) {
      if (e.name === 'TypeError') {
        showToast('网络异常，请检查连接', 'error');
      }
      throw e;
    } finally {
      hideLoading();
    }
  }

  // POST请求
  async post(endpoint, data = {}) {
    showLoading();
    try {
      const config = await this.buildConfig({
        method: 'POST',
        body: JSON.stringify(data)
      });

      const response = await fetch(this.baseURL + endpoint, config);
      return this.handleResponse(response);
    } catch (e) {
      if (e.name === 'TypeError') {
        showToast('网络异常，请检查连接', 'error');
      }
      throw e;
    } finally {
      hideLoading();
    }
  }

  // PUT请求
  async put(endpoint, data = {}) {
    showLoading();
    try {
      const config = await this.buildConfig({
        method: 'PUT',
        body: JSON.stringify(data)
      });
      const response = await fetch(this.baseURL + endpoint, config);
      return this.handleResponse(response);
    } catch (e) {
      if (e.name === 'TypeError') showToast('网络异常，请检查连接', 'error');
      throw e;
    } finally {
      hideLoading();
    }
  }

  // DELETE请求
  async delete(endpoint) {
    showLoading();
    try {
      const config = await this.buildConfig({
        method: 'DELETE'
      });
      const response = await fetch(this.baseURL + endpoint, config);
      return this.handleResponse(response);
    } catch (e) {
      if (e.name === 'TypeError') showToast('网络异常，请检查连接', 'error');
      throw e;
    } finally {
      hideLoading();
    }
  }

  // PATCH请求
  async patch(endpoint, data = {}) {
    showLoading();
    try {
      const config = await this.buildConfig({
        method: 'PATCH',
        body: JSON.stringify(data)
      });
      const response = await fetch(this.baseURL + endpoint, config);
      return this.handleResponse(response);
    } catch (e) {
      if (e.name === 'TypeError') showToast('网络异常，请检查连接', 'error');
      throw e;
    } finally {
      hideLoading();
    }
  }
}

// 创建API客户端实例
const client = new APIClient();

// 默认请求拦截器 - 添加时间戳防止缓存
client.addRequestInterceptor((config) => {
  config.headers['X-Request-Time'] = new Date().toISOString();
});

// 默认响应拦截器 - 日志记录
client.addResponseInterceptor((response) => {
  if (ENV.IS_DEV) {
    console.log(`[API] ${response.url} - ${response.status}`);
  }
});

// API模块定义
export const API = {
  // 认证相关
  auth: {
    login: (credentials) => client.post('/auth/login', credentials),
    register: (data) => client.post('/auth/register', data),
    me: () => client.get('/auth/me'),
    logout: () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  // 课程相关
  courses: {
    list: (params = {}) => client.get('/courses/', params),
    get: (id) => client.get(`/courses/${id}`),
    getChapters: (courseId) => client.get(`/courses/${courseId}/chapters`),
    getChapter: (id) => client.get(`/courses/chapters/${id}`),
    getChapterLab: (chapterId) => client.get(`/courses/chapters/${chapterId}/lab`)
  },

    // 实验相关
  labs: {
    execute: (code, language = 'python', timeout = 30) =>
      client.post('/labs/execute', { code, language, timeout }),
    submit: (labId, code) =>
      client.post(`/labs/${labId}/submit`, { code }),
    getSubmissions: (labId) => client.get(`/labs/${labId}/submissions`),
    getSubmission: (id) => client.get(`/labs/submissions/${id}`)
  },

  // 进度相关
  progress: {
    list: () => client.get('/progress/'),
    getCourseProgress: (courseId) => client.get(`/progress/courses/${courseId}`),
    update: (chapterId, data) => client.post(`/progress/chapters/${chapterId}`, data),
    getStats: () => client.get('/progress/stats/summary'),
    getLearningPath: () => client.get('/progress/learning-path')
  },

  // 讨论区相关
  discussions: {
    list: (courseId, sort = 'newest') => client.get(`/courses/${courseId}/discussions`, { sort }),
    create: (courseId, data) => client.post(`/courses/${courseId}/discussions`, data),
    get: (id) => client.get(`/discussions/${id}`),
    update: (id, data) => client.put(`/discussions/${id}`, data),
    delete: (id) => client.delete(`/discussions/${id}`),
    createComment: (id, content, parentId) => client.post(`/discussions/${id}/comments`, { content, parent_id: parentId }),
    like: (id) => client.post(`/discussions/${id}/like`)
  }
};

export default API;
