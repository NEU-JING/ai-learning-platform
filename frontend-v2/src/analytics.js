/* Analytics SDK — zero-dependency event tracking
 * Singleton pattern. Init once, track everywhere.
 * POST /api/v1/analytics/events
 */

// ── UUID v4 (no deps) ────────────────────────────────────
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

// ── Privacy sanitizer ────────────────────────────────────
const SENSITIVE = ['password', 'token', 'secret', 'credit_card', 'ssn'];

function sanitize(properties) {
  if (!properties || typeof properties !== 'object') return {};
  const out = {};
  for (const [k, v] of Object.entries(properties)) {
    const lower = k.toLowerCase();
    if (SENSITIVE.some(s => lower.includes(s))) {
      out[k] = '[REDACTED]';
    } else if (v && typeof v === 'object' && !Array.isArray(v)) {
      out[k] = sanitize(v);
    } else {
      out[k] = v;
    }
  }
  return out;
}

// ── Constants ────────────────────────────────────────────
const ENDPOINT = '/api/v1/analytics/events';
const FLUSH_MS = 5000;
const BATCH_MAX = 10;
const FAILED_CAP = 100;
const KEY_SESSION = '_asid';
const KEY_FAILED = '_afailed';

// ── Analytics singleton ──────────────────────────────────
class Analytics {
  constructor() {
    this._userId = null;
    this._sessionId = null;
    this._debug = false;
    this._queue = [];
    this._timer = null;
    this._initDone = false;
    this._flushing = false;
  }

  /**
   * Initialize analytics. Idempotent — safe to call multiple times.
   * @param {number|null} userId
   * @param {string}    sessionId
   * @param {boolean}   debug
   */
  init({ userId, sessionId, debug = false } = {}) {
    if (this._initDone) {
      if (debug !== undefined) this._debug = debug;
      if (sessionId) this.setSessionId(sessionId);
      if (userId !== undefined) this._userId = userId || null;
      return;
    }
    this._initDone = true;
    this._debug = debug;
    this._userId = userId || null;
    this._sessionId = sessionId || this._loadOrCreateSessionId();
    this._startTimer();
    this._retryFailed();
  }

  // ── Public API ───────────────────────────────────────

  /** Send a custom event */
  track(event, properties = {}) {
    if (!this._sessionId) this._sessionId = this._loadOrCreateSessionId();
    const evt = {
      event,
      properties: sanitize(properties),
      session_id: this._sessionId,
      timestamp: new Date().toISOString(),
    };
    if (this._userId) evt.user_id = this._userId;

    this._queue.push(evt);
    this._log('track', evt.event, evt.properties);

    if (this._queue.length >= BATCH_MAX) this.flush();
  }

  /** Shorthand for page_view event */
  page(pageName) {
    this.track('page_view', { page: pageName });
  }

  /**
   * Associate events with a user identity.
   * Call on login / user change. Pass null to clear.
   */
  identify(userId, traits = {}) {
    this._userId = userId || null;
    if (Object.keys(traits).length > 0) {
      this.track('identify', { user_id: userId, ...sanitize(traits) });
    }
  }

  /** Override session id (and persist to sessionStorage) */
  setSessionId(id) {
    if (id) {
      this._sessionId = id;
      try { sessionStorage.setItem(KEY_SESSION, id); } catch { /* noop */ }
    }
  }

  /** Force-send all queued events immediately */
  async flush() {
    if (this._queue.length === 0 || this._flushing) return;
    this._flushing = true;

    const batch = this._queue.splice(0, this._queue.length);

    try {
      const res = await fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ events: batch }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      this._log('flushed', batch.length, 'events');
    } catch (err) {
      this._log('flush failed:', err.message);
      this._saveFailed(batch);
    } finally {
      this._flushing = false;
    }
  }

  // ── Internals ────────────────────────────────────────

  _loadOrCreateSessionId() {
    try {
      let sid = sessionStorage.getItem(KEY_SESSION);
      if (!sid) {
        sid = uuidv4();
        sessionStorage.setItem(KEY_SESSION, sid);
      }
      return sid;
    } catch {
      return uuidv4();
    }
  }

  _startTimer() {
    this._stopTimer();
    this._timer = setInterval(() => this.flush(), FLUSH_MS);
  }

  _stopTimer() {
    if (this._timer) { clearInterval(this._timer); this._timer = null; }
  }

  _saveFailed(events) {
    try {
      const existing = JSON.parse(localStorage.getItem(KEY_FAILED) || '[]');
      existing.push(...events);
      if (existing.length > FAILED_CAP) existing.splice(0, existing.length - FAILED_CAP);
      localStorage.setItem(KEY_FAILED, JSON.stringify(existing));
    } catch { /* localStorage full or unavailable */ }
  }

  _retryFailed() {
    try {
      const raw = localStorage.getItem(KEY_FAILED);
      if (!raw) return;
      const failed = JSON.parse(raw);
      if (!failed.length) return;
      localStorage.removeItem(KEY_FAILED);
      this._queue.push(...failed);
      this.flush();
    } catch {
      try { localStorage.removeItem(KEY_FAILED); } catch { /* noop */ }
    }
  }

  _log(...args) {
    if (this._debug) console.log('[Analytics]', ...args);
  }
}

const analytics = new Analytics();
export default analytics;
