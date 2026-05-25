/**
 * ProfileOnboarding — shown when profile is not yet enabled.
 *
 * AC3: "开启你的能力主页，让雇主发现你" + one-click enable button.
 * After enable: is_public=true, all dimensions true, show profile link + copy.
 */

import { getProfileSettings, updateProfileSettings } from '../api/profile.js';
import { showToast } from './Toast.js';

/**
 * Render the onboarding card.
 * @param {Function} onEnabled - callback after profile is enabled (receives settings data)
 * @returns {{ template: string, onMount: Function }}
 */
export function ProfileOnboarding({ onEnabled }) {
  const id = 'profile-onboarding-' + Date.now();

  return {
    template: `
      <div class="profile-onboarding" id="${id}">
        <div class="profile-onboarding-card">
          <div class="profile-onboarding-icon">🌟</div>
          <h2 class="profile-onboarding-title">开启你的能力主页</h2>
          <p class="profile-onboarding-desc">让雇主发现你</p>
          <button class="btn btn-primary btn-lg profile-onboarding-btn"
                  id="${id}-enable-btn"
                  data-action="enable">
            一键开启
          </button>
        </div>
      </div>
    `,
    onMount: () => {
      const btn = document.getElementById(`${id}-enable-btn`);
      if (!btn) return;

      btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.textContent = '开启中...';
        try {
          const data = await updateProfileSettings({ is_public: true });
          showToast('能力主页已开启！', 'success');
          if (onEnabled) onEnabled(data);
        } catch (err) {
          showToast(err.message || '开启失败，请重试', 'error');
          btn.disabled = false;
          btn.textContent = '一键开启';
        }
      });
    },
  };
}

export default ProfileOnboarding;
