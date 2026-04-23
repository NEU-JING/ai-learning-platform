/**
 * 认证相关功能
 */

const auth = {
    // 检查是否已登录
    isLoggedIn() {
        return !!localStorage.getItem('token');
    },
    
    // 获取当前用户
    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },
    
    // 获取token
    getToken() {
        return localStorage.getItem('token');
    },
    
    // 设置登录状态
    setAuth(token, user) {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
    },
    
    // 清除登录状态
    clearAuth() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },
    
    // 登出
    logout() {
        this.clearAuth();
        window.location.href = '/login.html';
    },
    
    // 更新UI显示
    updateUI() {
        const user = this.getUser();
        const authElements = document.querySelectorAll('[data-auth]');
        const guestElements = document.querySelectorAll('[data-guest]');
        
        if (this.isLoggedIn() && user) {
            // 显示需要登录的内容
            authElements.forEach(el => el.style.display = '');
            // 隐藏游客内容
            guestElements.forEach(el => el.style.display = 'none');
            
            // 更新用户名显示
            document.querySelectorAll('.user-name').forEach(el => {
                el.textContent = user.username || user.email;
            });
            
            // 更新头像
            document.querySelectorAll('.user-avatar').forEach(el => {
                const initial = (user.username || user.email || '?').charAt(0).toUpperCase();
                el.textContent = initial;
            });
        } else {
            // 隐藏需要登录的内容
            authElements.forEach(el => el.style.display = 'none');
            // 显示游客内容
            guestElements.forEach(el => el.style.display = '');
        }
    },
    
    // 保护页面 - 未登录则跳转
    requireAuth() {
        if (!this.isLoggedIn()) {
            const currentUrl = encodeURIComponent(window.location.href);
            window.location.href = `/login.html?redirect=${currentUrl}`;
            return false;
        }
        return true;
    },
    
    // 已登录则跳转
    redirectIfLoggedIn(redirectUrl = '/index.html') {
        if (this.isLoggedIn()) {
            window.location.href = redirectUrl;
            return true;
        }
        return false;
    }
};

// 导出
window.auth = auth;

// 页面加载时更新UI
document.addEventListener('DOMContentLoaded', () => {
    auth.updateUI();
});
