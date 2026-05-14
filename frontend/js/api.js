/**
 * API client — unified HTTP request wrapper.
 * Uses storage.js for token management (DESIGN.md §9 Red Line).
 * All endpoints use /api/v1/ prefix matching backend routers.
 */

const API_BASE_URL = window.API_BASE_URL || `${window.location.origin}/api/v1`;

/**
 * Core request function with auth, error handling, and 401 auto-redirect.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    ...options,
    headers: {
      ...storage.getAuthHeaders(),
      ...options.headers,
    },
  };

  // Stringify body if object
  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }

  try {
    const response = await fetch(url, config);

    // 401 → clear token & redirect
    if (response.status === 401) {
      storage.clearAll();
      const redirect = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `/login.html?redirect=${redirect}`;
      return null;
    }

    // 204 No Content
    if (response.status === 204) {
      return null;
    }

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.detail || data.message || `请求失败 (${response.status})`;
      throw new Error(errorMsg);
    }

    return data;
  } catch (error) {
    if (error.name !== 'Error' || !error.message.includes('请求失败')) {
      console.error('[API] Request failed:', error);
    }
    throw error;
  }
}

// ── API modules ─────────────────────────────────────────

const api = {
  // Auth
  auth: {
    login: (email, password) =>
      request('/auth/login', { method: 'POST', body: { email, password } }),
    register: (username, email, password) =>
      request('/auth/register', { method: 'POST', body: { username, email, password } }),
    me: () => request('/auth/me'),
  },

  // Courses
  courses: {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/courses/${qs ? '?' + qs : ''}`);
    },
    get: (id) => request(`/courses/${id}`),
    getChapters: (courseId) => request(`/courses/${courseId}/chapters`),
    getChapter: (id) => request(`/courses/chapters/${id}`),
    getChapterLab: (chapterId) => request(`/courses/chapters/${chapterId}/lab`),
  },

  // Labs (code execution & submission)
  labs: {
    execute: (code, language = 'python', timeout = 30) =>
      request('/labs/execute', { method: 'POST', body: { code, language, timeout } }),
    submit: (labId, code) =>
      request(`/courses/labs/${labId}/submit`, { method: 'POST', body: { code } }),
    getSubmissions: (labId) => request(`/labs/${labId}/submissions`),
    getSubmission: (id) => request(`/labs/submissions/${id}`),
  },

  // Progress
  progress: {
    list: () => request('/progress/'),
    getCourseProgress: (courseId) => request(`/progress/courses/${courseId}`),
    update: (chapterId, data) =>
      request(`/progress/chapters/${chapterId}`, { method: 'POST', body: data }),
    getStats: () => request('/progress/stats/summary'),
    getLearningPath: () => request('/progress/learning-path'),
  },
};

window.api = api;
