/**
 * 500 服务器错误页面
 */

export default function Error500({ error }) {
  const isDev = window.location.hostname === 'localhost';
  
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
          <div class="error-code">500</div>
          <h1 class="error-title">服务器错误</h1>
          <p class="error-description">
            抱歉，服务器遇到了问题。我们的工程师已经收到通知，正在努力修复。
          </p>
          
          ${isDev && error ? `
            <details class="error-details-dev">
              <summary>开发模式：错误详情</summary>
              <pre class="error-stack-trace">${error.stack || error.message || error}</pre>
            </details>
          ` : ''}
          
          <div class="error-actions">
            <button class="btn btn-primary" onclick="window.location.reload()">
              🔄 刷新页面
            </button>
            <a href="#" class="btn btn-secondary" data-nav="/">
              🏠 返回首页
            </a>
          </div>
          
          <div class="error-contact">
            <p>如果问题持续存在，请<a href="mailto:support@ai-learning.com">联系我们</a></p>
          </div>
        </div>
        
        <div class="error-illustration">
          <svg viewBox="0 0 200 200" class="error-server">
            <rect x="60" y="40" width="80" height="100" rx="5" fill="#667eea" opacity="0.2"/>
            <rect x="65" y="45" width="70" height="90" rx="3" fill="#667eea"/>
            <circle cx="80" cy="60" r="3" fill="#f56565"/>
            <rect x="90" y="57" width="30" height="6" rx="3" fill="white" opacity="0.3"/>
            <rect x="75" y="80" width="50" height="4" rx="2" fill="white" opacity="0.3"/>
            <rect x="75" y="90" width="50" height="4" rx="2" fill="white" opacity="0.3"/>
            <rect x="75" y="100" width="30" height="4" rx="2" fill="white" opacity="0.3"/>
            <text x="100" y="125" text-anchor="middle" fill="white" font-size="12" font-weight="bold">500</text>
            <path d="M 100 140 L 100 160" stroke="#667eea" stroke-width="2"/>
            <path d="M 90 150 L 110 150" stroke="#667eea" stroke-width="2"/>
            <circle cx="100" cy="165" r="8" fill="#f56565" opacity="0.3"/>
            <text x="100" y="168" text-anchor="middle" fill="#f56565" font-size="10">!</text>
          </svg>
        </div>
      </div>
    </div>
  `;
}
