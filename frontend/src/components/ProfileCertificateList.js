/**
 * ProfileCertificateList — certificates on public profile
 *
 * Features:
 *   - Full list display (no pagination)
 *   - verify_url links open in new tab (target="_blank")
 *   - Empty state: "暂无认证记录"
 *   - Level labels with color coding
 */

/**
 * @param {Array|null} certificates - Array of certificate items, null if hidden
 * @param {string} containerId
 * @returns {string} HTML string
 */
export function ProfileCertificateList(certificates, containerId = 'profile-certs') {
  // If null, the dimension is hidden — render nothing
  if (certificates === null || certificates === undefined) {
    return '';
  }

  const isEmpty = certificates.length === 0;

  if (isEmpty) {
    return `
      <div id="${containerId}" class="profile-certs-container">
        <h3 class="profile-section-title">认证记录</h3>
        <div class="profile-empty-state">暂无认证记录</div>
      </div>
    `;
  }

  const levelColors = {
    beginner: { bg: '#c6f6d5', color: '#22543d', text: '入门' },
    intermediate: { bg: '#feebc8', color: '#744210', text: '进阶' },
    advanced: { bg: '#fed7d7', color: '#742a2a', text: '高级' },
    expert: { bg: '#e9d8fd', color: '#553c9a', text: '专家' },
  };

  const certItems = certificates.map(cert => {
    const level = levelColors[cert.level] || { bg: '#e2e8f0', color: '#4a5568', text: cert.level };
    const date = cert.issue_date ? new Date(cert.issue_date).toLocaleDateString('zh-CN') : '';
    return `
      <div class="profile-cert-item">
        <div class="profile-cert-level" style="background:${level.bg}; color:${level.color}">
          ${level.text}
        </div>
        <div class="profile-cert-info">
          <span class="profile-cert-title">${_escapeHtml(cert.course_title)}</span>
          <span class="profile-cert-detail">
            ${cert.level_label} · ${date}
          </span>
        </div>
        <div class="profile-cert-verify">
          <a href="${_escapeHtml(cert.verify_url)}" target="_blank" rel="noopener noreferrer"
             class="profile-cert-verify-link" title="验证此认证">
            验证
          </a>
        </div>
      </div>
    `;
  }).join('');

  return `
    <div id="${containerId}" class="profile-certs-container">
      <h3 class="profile-section-title">认证记录</h3>
      <div class="profile-cert-list">
        ${certItems}
      </div>
    </div>
  `;
}

function _escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

export default ProfileCertificateList;
