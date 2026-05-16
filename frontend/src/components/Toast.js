/**
 * Toast notification component — success/error/warning feedback.
 * Auto-dismisses after 3 seconds. Singleton pattern — only one toast at a time.
 */

const TOAST_STYLES = {
  success: { bg: '#10b981', icon: '✅' },
  error:   { bg: '#ef4444', icon: '❌' },
  warning: { bg: '#f59e0b', icon: '⚠️' },
  info:    { bg: '#3b82f6', icon: 'ℹ️' },
};

let _toastEl = null;
let _toastTimer = null;

function _ensureContainer() {
  if (_toastEl) return _toastEl;
  _toastEl = document.createElement('div');
  _toastEl.id = 'toast-container';
  Object.assign(_toastEl.style, {
    position: 'fixed', top: '20px', right: '20px', zIndex: '9999',
    display: 'flex', flexDirection: 'column', gap: '8px',
    pointerEvents: 'none',
  });
  document.body.appendChild(_toastEl);
  return _toastEl;
}

export function showToast(message, type = 'info', duration = 3000) {
  const container = _ensureContainer();
  const style = TOAST_STYLES[type] || TOAST_STYLES.info;

  const toast = document.createElement('div');
  Object.assign(toast.style, {
    background: style.bg, color: '#fff', padding: '12px 20px',
    borderRadius: '8px', fontSize: '14px', fontWeight: '500',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    transform: 'translateX(120%)', transition: 'transform 0.3s ease',
    pointerEvents: 'auto', cursor: 'pointer', maxWidth: '360px',
    display: 'flex', alignItems: 'center', gap: '8px',
  });
  toast.innerHTML = `<span>${style.icon}</span><span>${message}</span>`;

  // Click to dismiss
  toast.addEventListener('click', () => _dismiss(toast));

  container.appendChild(toast);

  // Animate in
  requestAnimationFrame(() => {
    toast.style.transform = 'translateX(0)';
  });

  // Auto dismiss
  const timer = setTimeout(() => _dismiss(toast), duration);
  toast._timer = timer;
}

function _dismiss(toast) {
  clearTimeout(toast._timer);
  toast.style.transform = 'translateX(120%)';
  setTimeout(() => toast.remove(), 300);
}
