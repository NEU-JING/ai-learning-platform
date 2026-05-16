/**
 * Common app utilities — Toast, Loading, URL helpers.
 */

const app = {
  // ── Toast ─────────────────────────────────────────────

  /**
   * Show a toast notification.
   * @param {string} message
   * @param {'success'|'error'|'warning'|'info'} type
   * @param {number} duration ms
   */
  toast(message, type = 'success', duration = 3000) {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      container.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:9999;display:flex;flex-direction:column;gap:0.5rem;pointer-events:none;';
      document.body.appendChild(container);
    }

    const colors = {
      success: { bg: '#10b981', icon: '✓' },
      error:   { bg: '#ef4444', icon: '✗' },
      warning: { bg: '#f59e0b', icon: '⚠' },
      info:    { bg: '#3b82f6', icon: 'ℹ' },
    };

    const { bg, icon } = colors[type] || colors.info;

    const toast = document.createElement('div');
    toast.style.cssText = `
      display:flex;align-items:center;gap:0.5rem;
      padding:0.75rem 1.25rem;border-radius:0.5rem;
      color:#fff;font-size:0.875rem;font-weight:500;
      background:${bg};box-shadow:0 4px 12px rgba(0,0,0,0.15);
      pointer-events:auto;opacity:1;transform:translateX(0);
      transition:all 0.3s ease;max-width:360px;word-break:break-word;
    `;
    toast.innerHTML = `<span style="font-weight:bold;font-size:1rem;">${icon}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  // ── Loading ───────────────────────────────────────────

  /**
   * Show loading state in a container.
   * @param {HTMLElement|string} target — selector or element
   * @param {string} message
   * @returns {Function} dismiss function
   */
  showLoading(target, message = '加载中...') {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) return () => {};

    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.style.cssText = `
      display:flex;align-items:center;justify-content:center;
      padding:2rem;flex-direction:column;gap:0.75rem;
    `;
    overlay.innerHTML = `
      <div class="spinner" style="width:2rem;height:2rem;border:3px solid #e5e7eb;border-top-color:#3b82f6;border-radius:50%;animation:spin 0.8s linear infinite;"></div>
      <p style="color:#6b7280;font-size:0.875rem;">${message}</p>
    `;

    // Add spin animation if not exists
    if (!document.getElementById('spin-keyframe')) {
      const style = document.createElement('style');
      style.id = 'spin-keyframe';
      style.textContent = '@keyframes spin{to{transform:rotate(360deg)}}';
      document.head.appendChild(style);
    }

    el.innerHTML = '';
    el.appendChild(overlay);

    return () => {
      if (overlay.parentNode) overlay.remove();
    };
  },

  /**
   * Show empty state.
   */
  showEmpty(target, title = '暂无数据', message = '') {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) return;
    el.innerHTML = `
      <div style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">📭</div>
        <h3 style="color:#374151;margin:0 0 0.5rem;">${title}</h3>
        ${message ? `<p style="color:#6b7280;">${message}</p>` : ''}
      </div>
    `;
  },

  /**
   * Show error state with retry.
   */
  showError(target, message = '加载失败，请重试', onRetry = null) {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) return;
    el.innerHTML = `
      <div style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">⚠️</div>
        <h3 style="color:#374151;margin:0 0 0.5rem;">出错了</h3>
        <p style="color:#6b7280;">${message}</p>
        ${onRetry ? `<button class="btn btn-primary" style="margin-top:1rem;" id="retry-btn">重试</button>` : ''}
      </div>
    `;
    if (onRetry) {
      el.querySelector('#retry-btn')?.addEventListener('click', onRetry);
    }
  },

  // ── Utilities ─────────────────────────────────────────

  getUrlParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  },

  setTitle(title) {
    document.title = title ? `${title} - AI学习平台` : 'AI学习平台';
  },

  formatDate(dateStr) {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric', month: 'long', day: 'numeric'
    });
  },

  debounce(fn, delay = 300) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  },

  escapeHtml(text) {
    if (!text) return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },

  // ── Navbar & Markdown ─────────────────────────────────

  /**
   * Render breadcrumb navigation.
   * @param {Array<{label:string, href?:string}>} items — last item is current page (no link)
   */
  renderBreadcrumb(items) {
    const existing = document.getElementById('breadcrumb');
    if (existing) existing.remove();

    const nav = document.createElement('nav');
    nav.id = 'breadcrumb';
    nav.setAttribute('aria-label', 'breadcrumb');
    nav.style.cssText = 'padding:0.75rem 1.5rem;font-size:0.875rem;color:#6b7280;border-bottom:1px solid #e5e7eb;';

    const links = items.map((item, i) => {
      const isLast = i === items.length - 1;
      if (isLast) {
        return `<span style="color:#111827;font-weight:500;">${item.label}</span>`;
      }
      return `<a href="${item.href || '#'}" style="color:#3b82f6;text-decoration:none;">${item.label}</a><span style="margin:0 0.5rem;">/</span>`;
    });

    nav.innerHTML = links.join('');
    // Insert after navbar
    const navbar = document.querySelector('.navbar');
    if (navbar && navbar.nextSibling) {
      navbar.parentNode.insertBefore(nav, navbar.nextSibling);
    } else if (navbar) {
      navbar.after(nav);
    }
  },

  initNavbar() {
    const page = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.navbar-nav a').forEach(link => {
      const href = link.getAttribute('href');
      if (href === page || (page === '' && href === 'index.html')) {
        link.classList.add('active');
      }
    });

    // User dropdown
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
      const trigger = userMenu.querySelector('.user-menu-trigger');
      const dropdown = userMenu.querySelector('.dropdown-menu');
      if (trigger && dropdown) {
        trigger.addEventListener('click', (e) => {
          e.stopPropagation();
          dropdown.classList.toggle('show');
        });
        document.addEventListener('click', () => dropdown.classList.remove('show'));
      }
    }
  },

  initMarked() {
    if (typeof marked !== 'undefined') {
      marked.setOptions({
        highlight: (code, lang) => {
          if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
          }
          return typeof hljs !== 'undefined' ? hljs.highlightAuto(code).value : code;
        },
        langPrefix: 'hljs language-',
        breaks: true,
        gfm: true
      });
    }
  },

  renderMarkdown(content) {
    if (typeof marked !== 'undefined') {
      return marked.parse(content || '');
    }
    return content || '';
  }
};

window.app = app;

document.addEventListener('DOMContentLoaded', () => {
  app.initNavbar();
  app.initMarked();
});
