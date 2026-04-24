/**
 * 404 页面未找到
 */

export default function NotFound() {
  return `
    <div class="page error-page">
      <nav class="navbar">
        <a href="#" class="navbar-brand" data-nav="/">
          <div class="navbar-logo">AI</div>
          <span>AI学习平台</span>
        </a>
      </nav>

      <div class="error-container">
        <div class="error-content">
          <div class="error-code">404</div>
          <h1 class="error-title">页面未找到</h1>
          <p class="error-description">
            抱歉，您访问的页面不存在或已被移除。
          </p>
          <div class="error-suggestions">
            <p>您可以尝试：</p>
            <ul>
              <li>检查网址是否正确</li>
              <li>返回首页浏览课程</li>
              <li>查看学习进度</li>
            </ul>
          </div>
          <div class="error-actions">
            <a href="#" class="btn btn-primary" data-nav="/">🏠 返回首页</a>
            <a href="#" class="btn btn-secondary" data-nav="/courses">📚 浏览课程</a>
          </div>
        </div>
        
        <div class="error-illustration">
          <svg viewBox="0 0 200 200" class="error-robot">
            <circle cx="100" cy="80" r="40" fill="#667eea" opacity="0.2"/>
            <circle cx="100" cy="80" r="30" fill="#667eea"/>
            <circle cx="90" cy="75" r="5" fill="white"/>
            <circle cx="110" cy="75" r="5" fill="white"/>
            <circle cx="90" cy="75" r="2" fill="#2d3748"/>
            <circle cx="110" cy="75" r="2" fill="#2d3748"/>
            <path d="M 90 90 Q 100 95 110 90" stroke="white" stroke-width="2" fill="none"/>
            <rect x="85" y="110" width="30" height="20" rx="5" fill="#667eea"/>
            <text x="100" y="124" text-anchor="middle" fill="white" font-size="10">404</text>
            <path d="M 70 100 L 50 90" stroke="#667eea" stroke-width="3" stroke-linecap="round"/>
            <path d="M 130 100 L 150 90" stroke="#667eea" stroke-width="3" stroke-linecap="round"/>
            <circle cx="50" cy="90" r="5" fill="#667eea"/>
            <circle cx="150" cy="90" r="5" fill="#667eea"/>
          </svg>
        </div>
      </div>
    </div>
  `;
}
