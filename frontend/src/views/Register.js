/**
 * 注册视图
 */

export default function Register() {
  const onMount = () => {
    const form = document.getElementById('register-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formData = new FormData(form);
      const password = formData.get('password');
      const confirmPassword = formData.get('confirm_password');
      
      if (password !== confirmPassword) {
        alert('两次输入的密码不一致');
        return;
      }
      
      const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: password
      };
      
      try {
        await window.$api.auth.register(data);
        alert('注册成功，请登录');
        window.$router.push('/login');
      } catch (error) {
        alert(error.message || '注册失败');
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
          <a href="#/login" class="btn btn-secondary btn-sm">登录</a>
        </div>
      </nav>

      <div class="auth-container">
        <div class="auth-card">
          <h2>📝 注册</h2>
          <form id="register-form">
            <div class="form-group">
              <label>用户名</label>
              <input type="text" name="username" required placeholder="yourname">
            </div>
            <div class="form-group">
              <label>邮箱</label>
              <input type="email" name="email" required placeholder="your@email.com">
            </div>
            <div class="form-group">
              <label>密码</label>
              <input type="password" name="password" required placeholder="••••••••">
            </div>
            <div class="form-group">
              <label>确认密码</label>
              <input type="password" name="confirm_password" required placeholder="••••••••">
            </div>
            <button type="submit" class="btn btn-primary btn-block">注册</button>
          </form>
          <p class="auth-link">
            已有账号？<a href="#/login">立即登录</a>
          </p>
        </div>
      </div>
    </div>
  `;

  return { template, onMount };
}
