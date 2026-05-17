/**
 * Analytics SDK — lightweight event tracking
 * Auto-tracks page views; exposes track() for custom events
 * Batches events and sends every 5 seconds
 */

const BATCH_INTERVAL = 5000;
const MAX_BATCH_SIZE = 20;

let eventQueue = [];
let sessionId = null;
let timer = null;

function getSessionId() {
  if (sessionId) return sessionId;
  // persist across page navigations within a session
  const key = '_ailp_sid';
  sessionId = sessionStorage.getItem(key);
  if (!sessionId) {
    sessionId = crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2);
    sessionStorage.setItem(key, sessionId);
  }
  return sessionId;
}

function getToken() {
  return localStorage.getItem('access_token');
}

async function flush() {
  if (eventQueue.length === 0) return;
  const batch = eventQueue.splice(0, MAX_BATCH_SIZE);
  try {
    const headers = { 'Content-Type': 'application/json' };
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const resp = await fetch('/api/v1/analytics/events/batch', {
      method: 'POST',
      headers,
      body: JSON.stringify({ events: batch }),
    });
    if (!resp.ok) {
      // silently fail — analytics should never break the app
      console.warn('[analytics] batch send failed:', resp.status);
    }
  } catch (e) {
    // network error — silently ignore
    console.warn('[analytics] network error:', e.message);
  }
}

export function track(eventType, eventData = null) {
  eventQueue.push({
    event_type: eventType,
    event_data: eventData,
    path: window.location.hash || window.location.pathname,
    referrer: document.referrer || null,
    session_id: getSessionId(),
  });

  // auto-flush if batch is full
  if (eventQueue.length >= MAX_BATCH_SIZE) {
    flush();
  }
}

// Auto page view tracking
let lastHash = null;
function trackPageView() {
  const currentHash = window.location.hash;
  if (currentHash === lastHash) return;
  lastHash = currentHash;
  track('page_view', { hash: currentHash, title: document.title });
}

// Start auto-tracking
export function initAnalytics() {
  // track initial page view
  trackPageView();

  // track hash changes
  window.addEventListener('hashchange', () => {
    setTimeout(trackPageView, 100); // slight delay for route to settle
  });

  // batch flush every N seconds
  timer = setInterval(flush, BATCH_INTERVAL);

  // flush on page unload
  window.addEventListener('beforeunload', () => {
    if (eventQueue.length > 0) {
      // use sendBeacon for reliability on unload
      const payload = JSON.stringify({ events: eventQueue.splice(0) });
      navigator.sendBeacon('/api/v1/analytics/events/batch', payload);
    }
  });
}

// Convenience helpers
export function trackChapterStart(chapterId, courseId) {
  track('chapter_start', { chapter_id: chapterId, course_id: courseId });
}

export function trackChapterComplete(chapterId, courseId) {
  track('chapter_complete', { chapter_id: chapterId, course_id: courseId });
}

export function trackLabSubmit(labId, passed) {
  track('lab_submit', { lab_id: labId, passed });
}

export function trackExerciseAttempt(chapterId, exerciseIndex, correct) {
  track('exercise_attempt', { chapter_id: chapterId, exercise_index: exerciseIndex, correct });
}
