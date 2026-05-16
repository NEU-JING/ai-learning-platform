/**
 * Loading indicator — top progress bar + overlay spinner.
 * Controlled via showLoading() / hideLoading() with ref counting.
 */

let _refCount = 0;
let _bar = null;
let _animFrame = null;

function _ensureBar() {
  if (_bar) return _bar;
  _bar = document.createElement('div');
  _bar.id = 'loading-bar';
  Object.assign(_bar.style, {
    position: 'fixed', top: '0', left: '0', height: '3px',
    background: 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
    zIndex: '10000', width: '0%', transition: 'width 0.3s ease',
  });
  document.body.appendChild(_bar);
  return _bar;
}

export function showLoading() {
  _refCount++;
  if (_refCount === 1) {
    const bar = _ensureBar();
    bar.style.display = 'block';
    _animateBar(bar);
  }
}

export function hideLoading() {
  _refCount = Math.max(0, _refCount - 1);
  if (_refCount === 0) {
    cancelAnimationFrame(_animFrame);
    const bar = _ensureBar();
    bar.style.width = '100%';
    setTimeout(() => {
      bar.style.display = 'none';
      bar.style.width = '0%';
    }, 300);
  }
}

function _animateBar(bar) {
  let width = 0;
  function step() {
    // Ease: fast start, slow near end, never reaches 100% until done
    width += (90 - width) * 0.05;
    if (width > 90) width = 90;
    bar.style.width = width + '%';
    _animFrame = requestAnimationFrame(step);
  }
  step();
}
