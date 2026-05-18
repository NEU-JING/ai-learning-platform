/**
 * 登录视图 - v2.0 优化交互
 * - 实时表单校验
 * - 加载状态
 * - 错误内联显示（取代 alert）
 * - 登录后跳回来源页
 */
import { Store } from '../core/store.js';

const store = Store.getInstance();

export default function Login() {
  const container = document.createElement('div');
  container.className = 'page page-enter';
  
  container.innerHTML = `
    <nav class="navbar">
      <a href="#/" class="navbar-brand">
        <div class="navbar-logo">AI</div>
        <span>AI学习平台</span>
      </a>
      <ul class="navbar-nav">
        <li><a href="#/">首页</a></li>
        <li><a href="#/courses">课程</a></li>
      </ul>
      <div class="navbar-right">
        <a href="#/register" class="btn btn-secondary btn-sm">注册</a>
      </div>
    </nav>
    <div class="auth-page">
      <div class="auth-card">
        <h2>🔐 登录</h2>
        <p class="auth-subtitle">欢迎回来，继续你的学习之旅</p>
        <form id="login-form">
          <div class="form-group">
            <label>邮箱</label>
            <input type="email" name="email" class="form-input" required placeholder="your@email.com" autocomplete="email">
          </div>
          <div class="form-group">
            <label>密码</label>
            <input type="password" name="password" class="form-input" required placeholder="••••••••" autocomplete="current-password">
          </div>
          <div id="login-error" style="display:none;padding:10px 14px;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:var(--radius-sm);color:var(--danger);font-size:0.85rem;margin-bottom:16px;"></div>
          <button type="submit" id="login-btn" class="form-submit" style="position:relative;">
            <span id="login-btn-text">登录</span>
            <span id="login-btn-loading" style="display:none;position:absolute;right:16px;top:50%;transform:translateY(-50%);">⏳</span>
          </button>
        </form>
        <div class="auth-links">
          还没有账号？<a href="#/register">立即注册</a>
        </div>
      </div>
    </div>`;

  // Bind form submit
  setTimeout(() => {
    const form = container.querySelector('#login-form');
    const errorDiv = container.querySelector('#login-error');
    const btn = container.querySelector('#login-btn');
    const btnText = container.querySelector('#login-btn-text');
    const btnLoading = container.querySelector('#login-btn-loading');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errorDiv.style.display = 'none';
      btn.disabled = true;
      btnText.textContent = '登录中...';
      btnLoading.style.display = 'inline';

      const formData = new FormData(form);
      const credentials = {
        email: formData.get('email'),
        password: formData.get('password')
      };

      try {
        const result = await store.dispatch('login', credentials);
        if (result.success) {
          // Redirect back to previous page or home
          const from = new URLSearchParams(window.location.hash.split('?')[1] || '').get('from') || '/';
          window.$router.push(from);
        } else {
          showError(errorDiv, result.error || '邮箱或密码错误');
        }
      } catch (err) {
        showError(errorDiv, err.message || '网络错误，请重试');
      }

      btn.disabled = false;
      btnText.textContent = '登录';
      btnLoading.style.display = 'none';
    });
  }, 50);

  return container;
}

function showError(el, msg) {
  el.textContent = msg;
  el.style.display = 'block';
}
