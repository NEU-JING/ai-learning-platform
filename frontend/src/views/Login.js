/**
 * 登录视图
 */

export default function Login() {
  const onMount = () => {
    const form = document.getElementById('login-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formData = new FormData(form);
      const credentials = {
        email: formData.get('email'),
        password: formData.get('password')
      };
      
      const result = await window.$store.dispatch('login', credentials);
      
      if (result.success) {
        window.$router.push('/');
      } else {
        alert(result.error || '登录失败');
      }
    });
  };

  const template = `
    <div class="page auth-page">
      <nav class="navbar">
        <a href="#/" class="navbar-brand">
          <div class="navbar-logo">AI</div>
          <span>AI学习平台</span>
        </a>
        <div class="navbar-right">
          <a href="#/register" class="btn btn-secondary btn-sm">注册</a>
        </div>
      </nav>

      <div class="auth-container">
        <div class="auth-card">
          <h2>🔐 登录</h2>
          <form id="login-form">
            <div class="form-group">
              <label>邮箱</label>
              <input type="email" name="email" required placeholder="your@email.com">
            </div>
            <div class="form-group">
              <label>密码</label>
              <input type="password" name="password" required placeholder="••••••••">
            </div>
            <button type="submit" class="btn btn-primary btn-block">登录</button>
          </form>
          <p class="auth-link">
            还没有账号？<a href="#/register">立即注册</a>
          </p>
        </div>
      </div>
    </div>
  `;

  return { template, onMount };
}
