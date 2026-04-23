/**
 * API请求封装
 * 后端地址: http://localhost:8000
 */

const API_BASE_URL = 'http://localhost:8000';

// 请求拦截 - 添加认证头
function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    const token = localStorage.getItem('token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}

// 通用请求方法
async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config = {
        ...options,
        headers: {
            ...getAuthHeaders(),
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, config);
        
        // 处理401未授权
        if (response.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login.html';
            return null;
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || data.detail || '请求失败');
        }
        
        return data;
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

// API方法
const api = {
    // 课程相关
    courses: {
        // 获取课程列表
        list: () => request('/api/courses'),
        
        // 获取课程详情
        get: (id) => request(`/api/courses/${id}`),
    },
    
    // 章节相关
    chapters: {
        // 获取章节内容
        get: (id) => request(`/api/chapters/${id}`),
    },
    
    // 代码执行
    code: {
        // 执行代码
        execute: (code, language = 'python') => 
            request('/api/code/execute', {
                method: 'POST',
                body: JSON.stringify({ code, language })
            }),
    },
    
    // 认证相关
    auth: {
        // 登录
        login: (email, password) => 
            request('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            }),
        
        // 注册
        register: (username, email, password) => 
            request('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            }),
        
        // 获取当前用户
        me: () => request('/api/auth/me'),
    }
};

// 导出
window.api = api;
