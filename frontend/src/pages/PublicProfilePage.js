/**
 * PublicProfilePage — /p/:username
 *
 * Public-facing profile page that renders skill radar, lab list, certificates.
 * No login required. Handles 403/404 from API gracefully.
 *
 * AC5: All dimensions hidden → username + AILP brand only
 * AC8: Zero data → empty state messages
 * AC9: Lab list preview 5 + expand
 * BR10: Certificate verify_url links target="_blank"
 */

import { fetchPublicProfile } from '../api/profile.js';
import { ProfileRadarChart, initRadarResize } from '../components/ProfileRadarChart.js';
import { ProfileLabList } from '../components/ProfileLabList.js';
import { ProfileCertificateList } from '../components/ProfileCertificateList.js';

export default async function PublicProfilePage({ params }) {
  const username = params?.username || '';

  if (!username) {
    return _renderErrorPage('用户名不能为空', 400);
  }

  let profile;
  try {
    profile = await fetchPublicProfile(username);
  } catch (err) {
    if (err.status === 404) {
      return _renderErrorPage('该用户不存在', 404);
    }
    if (err.status === 403) {
      return _renderErrorPage('该用户尚未公开能力主页', 403);
    }
    return _renderErrorPage('加载失败，请稍后重试', 500);
  }

  const vis = profile.visibility || {};
  const hasAnyDimension = vis.show_basic_info || vis.show_skill_radar || vis.show_labs || vis.show_certificates;

  // ── Header section ──────────────────────────────────────────────────
  let headerHtml = '';
  if (vis.show_basic_info && (profile.display_name || profile.bio || profile.avatar_url)) {
    const avatarHtml = profile.avatar_url
      ? `<img src="${_escapeAttr(profile.avatar_url)}" alt="${_escapeAttr(profile.display_name || username)}"
              class="profile-avatar" onerror="this.style.display='none'" />`
      : `<div class="profile-avatar-placeholder">${(profile.display_name || username).charAt(0).toUpperCase()}</div>`;
    headerHtml = `
      <div class="profile-header">
        ${avatarHtml}
        <div class="profile-header-info">
          <h1 class="profile-display-name">${_escapeHtml(profile.display_name || username)}</h1>
          ${profile.bio ? `<p class="profile-bio">${_escapeHtml(profile.bio)}</p>` : ''}
        </div>
      </div>
    `;
  } else {
    // AC5: Even without basic_info, show username
    headerHtml = `
      <div class="profile-header">
        <div class="profile-header-info">
          <h1 class="profile-display-name">${_escapeHtml(username)}</h1>
        </div>
      </div>
    `;
  }

  // ── Content sections ────────────────────────────────────────────────
  let contentHtml = '';

  // Skill radar
  if (vis.show_skill_radar && profile.skill_radar !== null) {
    contentHtml += ProfileRadarChart(profile.skill_radar);
  }

  // Lab list
  if (vis.show_labs) {
    contentHtml += ProfileLabList(profile.labs, profile.labs_total);
  }

  // Certificates
  if (vis.show_certificates) {
    contentHtml += ProfileCertificateList(profile.certificates);
  }

  // ── All dimensions hidden (AC5) ─────────────────────────────────────
  if (!hasAnyDimension) {
    contentHtml = `
      <div class="profile-all-hidden-notice">
        该用户尚未展示任何信息
      </div>
    `;
  }

  // ── Footer ──────────────────────────────────────────────────────────
  const footerHtml = `
    <div class="profile-footer">
      <div class="profile-verification">
        ✅ 数据由 AILP 平台验证
      </div>
      <div class="profile-cta">
        <a href="/" class="profile-cta-link">在 AILP 上学习 AI 课程</a>
      </div>
    </div>
  `;

  // ── Assemble ────────────────────────────────────────────────────────
  const pageHtml = `
    <div class="public-profile-page">
      <div class="profile-brand-bar">
        <a href="/" class="profile-brand-link">
          <span class="profile-brand-logo">AI</span>
          <span class="profile-brand-text">AILP</span>
        </a>
      </div>
      <div class="profile-content">
        ${headerHtml}
        ${contentHtml}
      </div>
      ${footerHtml}
    </div>
  `;

  return {
    template: pageHtml,
    onMount: () => {
      // Initialize radar chart responsive behavior
      initRadarResize();
    },
  };
}

// ── Error page ────────────────────────────────────────────────────────

function _renderErrorPage(message, statusCode) {
  const errorTitle = statusCode === 404 ? '用户不存在'
    : statusCode === 403 ? '主页未公开'
    : '加载失败';

  const errorDesc = statusCode === 404
    ? '你访问的用户不存在或已被删除。'
    : statusCode === 403
    ? '该用户尚未公开能力主页。'
    : message;

  return `
    <div class="public-profile-page">
      <div class="profile-brand-bar">
        <a href="/" class="profile-brand-link">
          <span class="profile-brand-logo">AI</span>
          <span class="profile-brand-text">AILP</span>
        </a>
      </div>
      <div class="profile-error-container">
        <div class="profile-error-icon">${statusCode === 404 ? '🔍' : statusCode === 403 ? '🔒' : '⚠️'}</div>
        <h2 class="profile-error-title">${errorTitle}</h2>
        <p class="profile-error-desc">${errorDesc}</p>
        <a href="/" class="profile-error-btn">返回首页</a>
      </div>
    </div>
  `;
}

// ── Helpers ───────────────────────────────────────────────────────────

function _escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

function _escapeAttr(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}


