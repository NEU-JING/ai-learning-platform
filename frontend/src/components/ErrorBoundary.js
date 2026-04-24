/**
 * 错误边界组件 - 捕获和处理组件渲染错误
 */

export class ErrorBoundary {
  constructor(options = {}) {
    this.options = {
      fallback: null, // 自定义错误UI
      onError: null,  // 错误回调
      retry: true,    // 是否显示重试按钮
      ...options
    };
    
    this.error = null;
    this.errorInfo = null;
  }

  /**
   * 捕获错误
   */
  catch(error, errorInfo = {}) {
    this.error = error;
    this.errorInfo = errorInfo;
    
    // 调用错误回调
    if (this.options.onError) {
      this.options.onError(error, errorInfo);
    }
    
    // 上报错误
    this.reportError(error, errorInfo);
    
    return this;
  }

  /**
   * 重置错误状态
   */
  reset() {
    this.error = null;
    this.errorInfo = null;
    return this;
  }

  /**
   * 渲染错误UI
   */
  render() {
    if (!this.error) return null;

    // 使用自定义fallback
    if (this.options.fallback) {
      return this.options.fallback(this.error, this);
    }

    // 默认错误UI
    return this.renderDefaultError();
  }

  /**
   * 默认错误UI
   */
  renderDefaultError() {
    const container = document.createElement('div');
    container.className = 'error-boundary';
    
    const isDev = process?.env?.NODE_ENV === 'development' || 
                  window.location.hostname === 'localhost';
    
    container.innerHTML = `
      <div class="error-boundary-content">
        <div class="error-icon">⚠️</div>
        <h2 class="error-title">出错了</h2>
        <p class="error-message">${this.error.message || '页面加载失败'}</p>
        ${isDev && this.error.stack ? `
          <details class="error-details">
            <summary>错误详情</summary>
            <pre class="error-stack">${this.error.stack}</pre>
          </details>
        ` : ''}
        ${this.options.retry !== false ? `
          <div class="error-actions">
            <button class="btn btn-primary" id="error-retry-btn">重试</button>
            <button class="btn btn-secondary" id="error-back-btn">返回首页</button>
          </div>
        ` : ''}
      </div>
    `;

    // 绑定事件
    const retryBtn = container.querySelector('#error-retry-btn');
    if (retryBtn) {
      retryBtn.addEventListener('click', () => {
        this.reset();
        window.location.reload();
      });
    }

    const backBtn = container.querySelector('#error-back-btn');
    if (backBtn) {
      backBtn.addEventListener('click', () => {
        window.$router?.push('/') || (window.location.hash = '#/');
      });
    }

    return container;
  }

  /**
   * 上报错误
   */
  reportError(error, errorInfo) {
    // 控制台输出
    console.error('ErrorBoundary caught error:', error, errorInfo);

    // 可以在这里集成错误上报服务
    // 例如: Sentry, LogRocket, 等
    if (window.Sentry) {
      window.Sentry.captureException(error, {
        extra: errorInfo
      });
    }

    // 发送到后端日志
    this.sendToServer(error, errorInfo);
  }

  /**
   * 发送错误到服务器
   */
  async sendToServer(error, errorInfo) {
    try {
      await fetch('/api/v1/logs/error', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          url: window.location.href,
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString()
        })
      });
    } catch (e) {
      // 静默失败
    }
  }

  /**
   * 包装函数组件
   */
  static wrap(fn, options = {}) {
    const boundary = new ErrorBoundary(options);
    
    return async function(...args) {
      try {
        return await fn.apply(this, args);
      } catch (error) {
        boundary.catch(error, { args });
        return boundary.render();
      }
    };
  }

  /**
   * 创建Promise错误处理器
   */
  static async handle(promise, options = {}) {
    const boundary = new ErrorBoundary(options);
    
    try {
      return { data: await promise, error: null };
    } catch (error) {
      boundary.catch(error);
      return { data: null, error, boundary };
    }
  }
}

/**
 * 全局错误处理器
 */
export function initGlobalErrorHandler() {
  // 捕获未处理的Promise错误
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection:', event.reason);
    
    // 显示全局错误提示
    showGlobalError('请求失败，请稍后重试');
  });

  // 捕获全局JS错误
  window.addEventListener('error', (event) => {
    console.error('Global Error:', event.error);
    
    // 防止递归错误
    if (event.message?.includes('ErrorBoundary')) {
      return;
    }
    
    showGlobalError('页面出现错误，请刷新重试');
  });

  // 资源加载错误
  window.addEventListener('error', (event) => {
    const target = event.target;
    if (target && (target.tagName === 'IMG' || target.tagName === 'SCRIPT' || target.tagName === 'LINK')) {
      console.error('Resource load error:', target.src || target.href);
    }
  }, true);
}

/**
 * 显示全局错误提示
 */
export function showGlobalError(message, options = {}) {
  const {
    type = 'error', // error, warning, info
    duration = 5000,
    closable = true
  } = options;

  // 移除已存在的错误提示
  const existing = document.querySelector('.global-error-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `global-error-toast global-error-${type}`;
  toast.innerHTML = `
    <span class="error-toast-icon">${type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}</span>
    <span class="error-toast-message">${message}</span>
    ${closable ? '<button class="error-toast-close">&times;</button>' : ''}
  `;

  // 样式
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: ${type === 'error' ? '#f56565' : type === 'warning' ? '#ed8936' : '#4299e1'};
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    display: flex;
    align-items: center;
    gap: 10px;
    z-index: 9999;
    animation: slideDown 0.3s ease;
  `;

  // 关闭按钮
  const closeBtn = toast.querySelector('.error-toast-close');
  if (closeBtn) {
    closeBtn.style.cssText = `
      background: none;
      border: none;
      color: white;
      font-size: 20px;
      cursor: pointer;
      padding: 0 0 0 10px;
    `;
    closeBtn.addEventListener('click', () => toast.remove());
  }

  document.body.appendChild(toast);

  // 自动关闭
  if (duration > 0) {
    setTimeout(() => {
      toast.style.animation = 'slideUp 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  return toast;
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
  @keyframes slideDown {
    from { transform: translate(-50%, -100%); opacity: 0; }
    to { transform: translate(-50%, 0); opacity: 1; }
  }
  @keyframes slideUp {
    from { transform: translate(-50%, 0); opacity: 1; }
    to { transform: translate(-50%, -100%); opacity: 0; }
  }
`;
document.head.appendChild(style);

export default ErrorBoundary;
