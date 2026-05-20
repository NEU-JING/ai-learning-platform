/* Data layer — real API with minimal fallback */

// ── API helpers ──────────────────────────────────────────
const API_BASE = '/api/v1';

async function fetchAPI(path) {
  try {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`API ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn(`[data] API error for ${path}:`, e.message);
    return null;
  }
}

// ── Maps ─────────────────────────────────────────────────
const LEVEL_MAP = {
  beginner: { label: '入门', color: 'var(--brand)' },
  intermediate: { label: '进阶', color: '#f5b342' },
  advanced: { label: '高级', color: '#fb7185' },
  expert: { label: '专家', color: '#a3e635' },
};

const CATEGORY_MAP = {
  python: 'Python',
  math: '数学',
  ml: '机器学习',
  dl: '深度学习',
  llm: '大语言模型',
  engineering: '工程化',
};

// ── Course loading ───────────────────────────────────────
async function loadCourses() {
  const data = await fetchAPI('/courses/');
  if (data?.items?.length) {
    return data.items.map(c => apiCourseToUI(c));
  }
  return [];
}

async function loadCourseDetail(courseId) {
  const data = await fetchAPI('/courses/' + courseId);
  if (data) return apiCourseToUI(data);
  return null;
}

// ── Chapter loading ──────────────────────────────────────
async function loadChapter(chapterId) {
  const data = await fetchAPI(`/courses/chapters/${chapterId}`);
  if (data) return apiChapterToUI(data);
  return null;
}

// ── Lab loading ──────────────────────────────────────────
async function loadLab(labId, chapterId) {
  if (chapterId) {
    const data = await fetchAPI(`/courses/chapters/${chapterId}/lab`);
    if (data) return apiLabToUI(data);
  }
  return null;
}

// ── Progress loading ─────────────────────────────────────
async function loadProgressStats() {
  const data = await fetchAPI('/progress/stats');
  if (data) return data;
  return null;
}

async function loadUserProgress() {
  const data = await fetchAPI('/progress/');
  if (data) return data;
  return null;
}

// ── Stats loading ────────────────────────────────────────
async function loadPlatformStats() {
  const data = await fetchAPI('/stats/');
  if (data) return data;
  return null;
}

// ── API → UI transforms ──────────────────────────────────
function apiCourseToUI(c) {
  const phase = c.order_index ?? c.id;
  const level = c.level || 'beginner';
  const categoryMap = { 1:'python', 2:'math', 3:'ml', 4:'dl', 5:'llm', 6:'engineering' };
  const accentMap = { 1:'indigo', 2:'teal', 3:'amber', 4:'rose', 5:'lime', 6:'indigo' };
  const iconMap = { 1:'python', 2:'sigma', 3:'brain', 4:'cpu', 5:'sparkles', 6:'terminal' };

  return {
    id: c.id,
    phase,
    title: c.title,
    subtitle: `Phase ${phase} · ${c.description?.substring(0, 30) || ''}`,
    description: c.description || '',
    level,
    category: categoryMap[c.id] || 'python',
    duration_hours: c.estimated_hours || 0,
    chapters_total: c.chapters_count || c.chapter_count || c.chapters?.length || 0,
    chapters_done: c.progress?.chapters_done || 0,
    lab_total: c.labs_count || c.lab_count || c.labs?.length || 0,
    accent: accentMap[c.id] || 'indigo',
    icon: iconMap[c.id] || 'book',
    students: c.enrollment_count || 0,
    rating: c.rating || 4.8,
    chapters: (c.chapters || []).map(apiChapterBriefToUI),
    labs: (c.labs || []).map(apiLabBriefToUI),
  };
}

function apiChapterBriefToUI(ch) {
  return {
    id: ch.id,
    num: ch.order_index ?? ch.id,
    title: ch.title,
    duration: ch.estimated_minutes || 30,
    type: ch.is_lab ? 'lab' : 'text',
    status: ch.is_completed ? 'completed' : 'not_started',
  };
}

function apiLabBriefToUI(lab) {
  return {
    id: lab.id,
    title: lab.title,
    duration: lab.estimated_minutes || 60,
  };
}

function apiChapterToUI(ch) {
  const sections = parseContentToSections(ch.content);
  const blocks = sections.map(s => ({ type: "callout", kind: "info", title: s.title, text: s.content }));
  return {
    id: ch.id,
    title: ch.title,
    num: ch.order_index ?? ch.id,
    course_id: ch.course_id,
    order_index: ch.order_index,
    content: ch.content,
    toc: ch.toc || [],
    sections,
    blocks,
  };
}

function apiLabToUI(lab) {
  return {
    id: lab.id,
    title: lab.title,
    description: lab.description || '',
    starter_code: lab.starter_code || lab.starter || '',
    test_cases: lab.test_cases || lab.tests || [],
    time_limit: lab.time_limit_seconds || lab.time_limit || 30,
    difficulty: lab.difficulty || 'medium',
    duration: lab.estimated_minutes || lab.duration || 60,
    course_title: lab.course_title || '实验课程',
    hints: lab.hints || [],
  };
}

function parseContentToSections(content) {
  if (!content) return [];
  const lines = content.split('\n');
  const sections = [];
  let current = null;
  for (const line of lines) {
    const h2 = line.match(/^##\s+(.+)/);
    if (h2) {
      if (current) sections.push(current);
      current = { title: h2[1], content: '' };
    } else if (current) {
      current.content += line + '\n';
    }
  }
  if (current) sections.push(current);
  return sections.length ? sections : [{ title: '概述', content }];
}

// ── Current learning position (loaded from API or localStorage) ──
let CURRENT = {
  course_id: null,
  chapter_id: null,
  last_accessed: null,
};

// Try to load from localStorage on init
try {
  const saved = localStorage.getItem('ailp_current');
  if (saved) {
    const parsed = JSON.parse(saved);
    CURRENT = { ...CURRENT, ...parsed };
  }
} catch {}

// ── Auth API ─────────────────────────────────────────────
const TOKEN_KEY = 'ailp_token';
const USER_KEY = 'ailp_user';

function getToken() {
  try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
}

function setToken(token) {
  try { localStorage.setItem(TOKEN_KEY, token); } catch {}
}

function clearToken() {
  try { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); } catch {}
}

async function registerUser({ email, username, password }) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, username, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || '注册失败');
  return data;
}

async function loginUser({ email, password }) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || '登录失败');
  setToken(data.access_token);
  return data;
}

function getCurrentUser() {
  try {
    const user = localStorage.getItem(USER_KEY);
    const token = getToken();
    if (!token) return { isLoggedIn: false, user: null };
    return { isLoggedIn: true, user: user ? JSON.parse(user) : null };
  } catch {
    return { isLoggedIn: false, user: null };
  }
}

function logout() {
  clearToken();
}

// ── Auth ─────────────────────────────────────────────────
const CURRENT_USER = getCurrentUser();

// ── Test data exports (for testing only) ─────────────────
// These are only exported for unit tests, NOT for production use
const TEST_DATA = {
  LEVEL_MAP,
  CATEGORY_MAP,
};

export {
  loadCourses,
  loadCourseDetail,
  loadChapter,
  loadLab,
  loadProgressStats,
  loadUserProgress,
  loadPlatformStats,
  CURRENT,
  LEVEL_MAP,
  CATEGORY_MAP,
  CURRENT_USER,
  registerUser,
  loginUser,
  logout,
  getCurrentUser,
  getToken,
  TEST_DATA,
};
