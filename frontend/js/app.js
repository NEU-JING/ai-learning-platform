/**
 * 通用应用逻辑
 */

const app = {
    // 显示提示消息
    toast(message, type = 'success', duration = 3000) {
        // 创建容器
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        // 创建toast
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // 图标
        const icons = {
            success: '✓',
            error: '✗',
            warning: '!'
        };
        
        toast.innerHTML = `
            <span style="font-weight: bold;">${icons[type] || '•'}</span>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        // 自动移除
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },
    
    // 显示加载状态
    showLoading(container, message = '加载中...') {
        const el = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
            
        if (el) {
            el.innerHTML = `
                <div class="loading">
                    <div style="text-align: center;">
                        <div class="spinner" style="margin: 0 auto 1rem;"></div>
                        <p>${message}</p>
                    </div>
                </div>
            `;
        }
    },
    
    // 显示空状态
    showEmpty(container, title = '暂无数据', message = '') {
        const el = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
            
        if (el) {
            el.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <h3>${title}</h3>
                    ${message ? `<p>${message}</p>` : ''}
                </div>
            `;
        }
    },
    
    // 显示错误状态
    showError(container, message = '加载失败，请重试', onRetry = null) {
        const el = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
            
        if (el) {
            el.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <h3>出错了</h3>
                    <p>${message}</p>
                    ${onRetry ? `<button class="btn btn-primary" style="margin-top: 1rem;" onclick="(${onRetry})()">重试</button>` : ''}
                </div>
            `;
        }
    },
    
    // 从URL获取参数
    getUrlParam(name) {
        const params = new URLSearchParams(window.location.search);
        return params.get(name);
    },
    
    // 设置页面标题
    setTitle(title) {
        document.title = title ? `${title} - AI学习平台` : 'AI学习平台';
    },
    
    // 格式化日期
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    // 防抖
    debounce(fn, delay = 300) {
        let timer = null;
        return function(...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    },
    
    // 节流
    throttle(fn, limit = 300) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                fn.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // 初始化导航栏
    initNavbar() {
        // 高亮当前页面
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        document.querySelectorAll('.navbar-nav a').forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPage || (currentPage === '' && href === 'index.html')) {
                link.classList.add('active');
            }
        });
        
        // 用户菜单下拉
        const userMenu = document.querySelector('.user-menu');
        if (userMenu) {
            const trigger = userMenu.querySelector('.user-menu-trigger');
            const dropdown = userMenu.querySelector('.dropdown-menu');
            
            if (trigger && dropdown) {
                trigger.addEventListener('click', (e) => {
                    e.stopPropagation();
                    dropdown.classList.toggle('show');
                });
                
                document.addEventListener('click', () => {
                    dropdown.classList.remove('show');
                });
            }
        }
    },
    
    // Markdown渲染配置
    initMarked() {
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        return hljs.highlight(code, { language: lang }).value;
                    }
                    return hljs.highlightAuto(code).value;
                },
                langPrefix: 'hljs language-',
                breaks: true,
                gfm: true
            });
        }
    },
    
    // 渲染Markdown
    renderMarkdown(content) {
        if (typeof marked !== 'undefined') {
            return marked.parse(content || '');
        }
        return content || '';
    }
};

// 导出
window.app = app;

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    app.initNavbar();
    app.initMarked();
});
