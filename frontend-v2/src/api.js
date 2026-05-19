/**
 * API Client - 连接后端真实数据
 */
const API_BASE = '/api/v1';

const apiRequest = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${url}`, { ...options, headers });

  if (response.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.dispatchEvent(new Event('auth:expired'));
    throw new Error('登录已过期，请重新登录');
  }

  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || '请求失败');
  return data;
};

export const api = {
  auth: {
    login: (email, password) => apiRequest('/auth/login', {
      method: 'POST', body: JSON.stringify({ email, password })
    }),
    register: (email, username, password) => apiRequest('/auth/register', {
      method: 'POST', body: JSON.stringify({ email, username, password })
    }),
    me: () => apiRequest('/auth/me'),
  },
  courses: {
    list: (page = 1, perPage = 20) => apiRequest(`/courses/?page=${page}&per_page=${perPage}`),
    get: (id) => apiRequest(`/courses/${id}`),
    chapters: (courseId) => apiRequest(`/courses/${courseId}/chapters`),
  },
  labs: {
    get: (id) => apiRequest(`/labs/${id}`),
    submit: (id, code) => apiRequest(`/courses/labs/${id}/submit`, {
      method: 'POST', body: JSON.stringify({ code })
    }),
  },
  progress: {
    get: () => apiRequest('/progress/'),
  },
};
