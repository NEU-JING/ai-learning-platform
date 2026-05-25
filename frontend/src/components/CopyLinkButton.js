/**
 * CopyLinkButton — copy profile URL to clipboard.
 *
 * Uses navigator.clipboard API with fallback.
 * Shows "复制失败，请手动复制链接" on failure.
 */

import { showToast } from './Toast.js';

/**
 * Render a copy-link button.
 * @param {string} url - the URL to copy
 * @returns {{ template: string, onMount: Function }}
 */
export function CopyLinkButton(url) {
  const id = 'copy-link-' + Date.now();

  return {
    template: `
      <button class="btn btn-secondary btn-sm copy-link-btn" id="${id}"
              title="复制链接">
        📋 复制链接
      </button>
    `,
    onMount: () => {
      const btn = document.getElementById(id);
      if (!btn) return;

      btn.addEventListener('click', async () => {
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(url);
            showToast('链接已复制！', 'success');
          } else {
            // Fallback: create a temporary textarea
            _fallbackCopy(url);
          }
        } catch (_err) {
          showToast('复制失败，请手动复制链接', 'warning');
        }
      });
    },
  };
}

function _fallbackCopy(text) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.left = '-9999px';
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand('copy');
    showToast('链接已复制！', 'success');
  } catch (_err) {
    showToast('复制失败，请手动复制链接', 'warning');
  }
  document.body.removeChild(ta);
}

export default CopyLinkButton;
