/**
 * ProfileSettingsPage — /#/profile/settings
 *
 * AC3:  First-time onboarding card + one-click enable
 * AC4:  Preview + copy link
 * AC11: Close profile with warning message
 *
 * States:
 *   1. Not enabled → ProfileOnboarding
 *   2. Enabled → master toggle, profile link, dimension toggles, preview, batch buttons
 *   3. Just closed → warning banner "你的能力主页已关闭，他人将无法访问"
 */

import { getProfileSettings, updateProfileSettings, batchProfileSettings } from '../api/profile.js';
import { showToast } from './Toast.js';
import { ProfileOnboarding } from './ProfileOnboarding.js';
import { CopyLinkButton } from './CopyLinkButton.js';

// Dimension definitions (field key → display label)
const DIMENSIONS = [
  { key: 'show_basic_info',    label: '基本信息',   icon: '👤' },
  { key: 'show_skill_radar',   label: '技能雷达',   icon: '🎯' },
  { key: 'show_labs',          label: '实验记录',   icon: '🧪' },
  { key: 'show_certificates',  label: '认证证书',   icon: '🏆' },
];

export default async function ProfileSettingsPage() {
  const store = window.$store;

  // Must be authenticated
  if (!store?.state?.token) {
    window.$router?.push('/login');
    return '<div class="loading">正在跳转...</div>';
  }

  // Load current settings
  let settings;
  try {
    settings = await getProfileSettings();
  } catch (err) {
    if (err.message && err.message.includes('401')) {
      window.$router?.push('/login');
      return '<div class="loading">正在跳转...</div>';
    }
    return _renderError(err.message || '加载设置失败');
  }

  // Determine initial state
  if (!settings.is_public) {
    return _renderOnboarding(settings);
  }

  return _renderSettings(settings);
}

// ── Onboarding state ────────────────────────────────────────────────────────

function _renderOnboarding(currentSettings) {
  const onboarding = ProfileOnboarding({
    onEnabled: (data) => {
      // Re-render the whole page with settings view
      _rerender(data);
    },
  });

  return {
    template: `
      <div class="page profile-settings-page">
        ${_renderNavbar()}
        <div class="container">
          <div class="page-header">
            <h1>🎨 我的公开主页</h1>
          </div>
          ${onboarding.template}
        </div>
      </div>
    `,
    onMount: () => {
      onboarding.onMount();
    },
  };
}

// ── Settings state (enabled) ────────────────────────────────────────────────

function _renderSettings(settings) {
  const uid = 'ps-' + Date.now();
  const profileUrl = settings.profile_url || '';
  // Build the full preview URL from profile_url
  const previewUrl = _buildPreviewUrl(settings);

  // Dimension toggle rows
  const dimensionRows = DIMENSIONS.map(d => {
    const checked = settings[d.key] ? 'checked' : '';
    return `
      <div class="setting-row">
        <div class="setting-row-label">
          <span class="setting-icon">${d.icon}</span>
          <span>${d.label}</span>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" ${checked}
                 data-field="${d.key}"
                 class="${uid}-dim-toggle" />
          <span class="toggle-slider"></span>
        </label>
      </div>
    `;
  }).join('');

  return {
    template: `
      <div class="page profile-settings-page" id="${uid}">
        ${_renderNavbar()}
        <div class="container">
          <div class="page-header">
            <h1>🎨 我的公开主页</h1>
          </div>

          <!-- Master toggle -->
          <div class="settings-card">
            <div class="setting-row setting-row-master">
              <div class="setting-row-label">
                <span class="setting-icon">🌐</span>
                <span>公开主页</span>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" checked
                       id="${uid}-master-toggle" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <!-- Profile link + actions -->
          <div class="settings-card">
            <div class="profile-link-section">
              <div class="profile-link-row">
                <span class="profile-link-url">${_escapeHtml(profileUrl)}</span>
                <span id="${uid}-copy-btn-slot"></span>
              </div>
              <div class="profile-actions">
                <a href="${_escapeAttr(previewUrl)}" target="_blank" rel="noopener noreferrer"
                   class="btn btn-secondary btn-sm">
                  👁️ 预览主页
                </a>
              </div>
            </div>
          </div>

          <!-- Dimension toggles -->
          <div class="settings-card">
            <div class="settings-card-header">
              <h3>展示维度</h3>
              <div class="batch-actions">
                <button class="btn btn-sm btn-outline ${uid}-batch-btn" data-action="show_all">
                  一键开启全部
                </button>
                <button class="btn btn-sm btn-outline ${uid}-batch-btn" data-action="hide_all">
                  一键隐藏全部
                </button>
              </div>
            </div>
            ${dimensionRows}
          </div>
        </div>
      </div>
    `,
    onMount: () => {
      _bindSettingsEvents(uid, settings);
    },
  };
}

// ── Closed state ────────────────────────────────────────────────────────────

function _renderClosedBanner(settings) {
  const profileUrl = settings.profile_url || '';
  const previewUrl = _buildPreviewUrl(settings);

  return `
    <div class="settings-card settings-closed-banner">
      <div class="closed-banner-icon">🔒</div>
      <p class="closed-banner-text">你的能力主页已关闭，他人将无法访问</p>
      <div class="setting-row setting-row-master">
        <div class="setting-row-label">
          <span class="setting-icon">🌐</span>
          <span>公开主页</span>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" id="ps-master-toggle-closed" />
          <span class="toggle-slider"></span>
        </label>
      </div>
    </div>
  `;
}

// ── Event binding ───────────────────────────────────────────────────────────

function _bindSettingsEvents(uid, settings) {
  // Copy link button
  const copySlot = document.getElementById(`${uid}-copy-btn-slot`);
  if (copySlot && settings.profile_url) {
    const copyBtn = CopyLinkButton(settings.profile_url);
    copySlot.innerHTML = copyBtn.template;
    // Mount the copy button events after DOM update
    requestAnimationFrame(() => copyBtn.onMount());
  }

  // Master toggle
  const masterToggle = document.getElementById(`${uid}-master-toggle`);
  if (masterToggle) {
    masterToggle.addEventListener('change', async () => {
      const newVal = masterToggle.checked;
      try {
        const data = await updateProfileSettings({ is_public: newVal });
        if (!newVal) {
          showToast('你的能力主页已关闭，他人将无法访问', 'warning');
        } else {
          showToast('能力主页已开启！', 'success');
        }
        _rerender(data);
      } catch (err) {
        showToast(err.message || '操作失败', 'error');
        masterToggle.checked = !newVal; // revert
      }
    });
  }

  // Dimension toggles
  document.querySelectorAll(`.${uid}-dim-toggle`).forEach(toggle => {
    toggle.addEventListener('change', async () => {
      const field = toggle.dataset.field;
      const newVal = toggle.checked;
      try {
        const data = await updateProfileSettings({ [field]: newVal });
        // Don't full re-render for dimension toggles — just update state
        settings[field] = newVal;
      } catch (err) {
        showToast(err.message || '操作失败', 'error');
        toggle.checked = !newVal; // revert
      }
    });
  });

  // Batch buttons
  document.querySelectorAll(`.${uid}-batch-btn`).forEach(btn => {
    btn.addEventListener('click', async () => {
      const action = btn.dataset.action;
      try {
        btn.disabled = true;
        const data = await batchProfileSettings(action);
        showToast(action === 'show_all' ? '已开启全部维度' : '已隐藏全部维度', 'success');
        _rerender(data);
      } catch (err) {
        showToast(err.message || '操作失败', 'error');
        btn.disabled = false;
      }
    });
  });
}

// ── Re-render helper ────────────────────────────────────────────────────────

function _rerender(settings) {
  const app = document.getElementById('app');
  if (!app) return;

  let result;
  if (!settings.is_public) {
    // Closed state — show banner + onboarding
    result = _renderClosedWithOnboarding(settings);
  } else {
    result = _renderSettings(settings);
  }

  if (typeof result === 'string') {
    app.innerHTML = result;
  } else if (result && result.template) {
    app.innerHTML = result.template;
    if (result.onMount) result.onMount();
  }
}

function _renderClosedWithOnboarding(settings) {
  const profileUrl = settings.profile_url || '';

  // Show closed banner at top, then onboarding card below
  const onboarding = ProfileOnboarding({
    onEnabled: (data) => {
      _rerender(data);
    },
  });

  return {
    template: `
      <div class="page profile-settings-page">
        ${_renderNavbar()}
        <div class="container">
          <div class="page-header">
            <h1>🎨 我的公开主页</h1>
          </div>
          ${_renderClosedBanner(settings)}
        </div>
      </div>
    `,
    onMount: () => {
      // Bind the closed state master toggle
      const closedToggle = document.getElementById('ps-master-toggle-closed');
      if (closedToggle) {
        closedToggle.addEventListener('change', async () => {
          const newVal = closedToggle.checked;
          try {
            const data = await updateProfileSettings({ is_public: newVal });
            if (newVal) {
              showToast('能力主页已开启！', 'success');
            }
            _rerender(data);
          } catch (err) {
            showToast(err.message || '操作失败', 'error');
            closedToggle.checked = !newVal;
          }
        });
      }
    },
  };
}

// ── Navbar ──────────────────────────────────────────────────────────────────

function _renderNavbar() {
  const store = window.$store;
  const userEmail = store?.state?.user?.email || '';

  return `
    <nav class="navbar">
      <a href="#/" class="navbar-brand">
        <div class="navbar-logo">AI</div>
        <span>AI学习平台</span>
      </a>
      <ul class="navbar-nav">
        <li><a href="#/">首页</a></li>
        <li><a href="#/courses">课程</a></li>
        <li><a href="#/progress">学习进度</a></li>
        <li><a href="#/profile/settings" class="active">我的公开主页</a></li>
      </ul>
      <div class="navbar-right">
        <span class="user-name">${_escapeHtml(userEmail)}</span>
        <a href="#" class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout'); return false;">退出</a>
      </div>
    </nav>
  `;
}

// ── Helpers ─────────────────────────────────────────────────────────────────

function _buildPreviewUrl(settings) {
  // profile_url is like "ailp.com/p/username" — we need full URL
  const profileUrl = settings.profile_url || '';
  if (profileUrl.startsWith('http://') || profileUrl.startsWith('https://')) {
    return profileUrl;
  }
  // Construct from current origin + /p/{username}
  // Extract username from profile_url (last segment)
  const parts = profileUrl.split('/');
  const username = parts[parts.length - 1] || '';
  if (username) {
    return `${window.location.origin}/p/${encodeURIComponent(username)}`;
  }
  return profileUrl;
}

function _renderError(message) {
  return `
    <div class="page profile-settings-page">
      ${_renderNavbar()}
      <div class="container">
        <div class="error-state">
          <div class="error-icon">⚠️</div>
          <h2>加载失败</h2>
          <p>${_escapeHtml(message)}</p>
          <button class="btn btn-primary" onclick="location.reload()">重试</button>
        </div>
      </div>
    </div>
  `;
}

function _escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

function _escapeAttr(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
