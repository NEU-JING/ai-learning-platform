/**
 * Path Progress E2E Tests
 *
 * Covers AC3 from spec.md:
 *   - AC3: 路径进度追踪 - 查看学习进度、里程碑状态
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;

// Test user credentials
const TEST_USERS = {
  progress: { username: 'e2e_progress', email: 'e2e_progress@test.com', password: 'Pass1234' },
};

// Helper: Register a user via API
async function registerUser(user) {
  try {
    const res = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(user),
    });
    return res.ok || res.status === 400;
  } catch (e) {
    return false;
  }
}

// Helper: Login and get token
async function loginUser(user) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: user.email, password: user.password }),
  });
  if (!res.ok) return null;
  const data = await res.json();
  return data.access_token;
}

// Helper: Create a learning path for user
async function createPath(token, templateSlug = 'ai-engineer', mode = 'standard') {
  const res = await fetch(`${API_URL}/paths`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      template_slug: templateSlug,
      mode: mode,
    }),
  });
  if (!res.ok) return null;
  return res.json();
}

test.describe('AC3: 路径进度追踪', () => {
  test.beforeAll(async () => {
    await registerUser(TEST_USERS.progress);
  });

  test('API - 获取路径进度详情', async () => {
    const token = await loginUser(TEST_USERS.progress);
    expect(token).toBeTruthy();

    // First create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();
    expect(pathData).toHaveProperty('path_id');

    const pathId = pathData.path_id;

    // Get path progress
    const res = await fetch(`${API_URL}/paths/${pathId}/progress`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Verify response structure
    expect(data).toHaveProperty('path_id');
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('progress');
    expect(data).toHaveProperty('milestones');
    expect(data).toHaveProperty('estimated_remaining_days');

    // Verify progress structure
    expect(data.progress).toHaveProperty('percent');
    expect(data.progress).toHaveProperty('completed_courses');
    expect(data.progress).toHaveProperty('total_courses');

    // Verify progress percentage is valid
    expect(data.progress.percent).toBeGreaterThanOrEqual(0);
    expect(data.progress.percent).toBeLessThanOrEqual(100);
  });

  test('API - 里程碑状态检查', async () => {
    const token = await loginUser(TEST_USERS.progress);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/progress`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify milestones structure
    expect(Array.isArray(data.milestones)).toBe(true);

    // Each milestone should have required fields
    data.milestones.forEach(milestone => {
      expect(milestone).toHaveProperty('order');
      expect(milestone).toHaveProperty('name');
      expect(milestone).toHaveProperty('status'); // 'completed', 'in_progress', 'pending'
      expect(['completed', 'in_progress', 'pending']).toContain(milestone.status);
    });
  });

  test('API - 进度计算正确性', async () => {
    const token = await loginUser(TEST_USERS.progress);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/progress`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Calculate expected progress based on courses
    const expectedProgress = data.progress.total_courses > 0
      ? Math.round((data.progress.completed_courses / data.progress.total_courses) * 100)
      : 0;

    // Overall progress should match calculated value
    expect(data.progress.percent).toBe(expectedProgress);

    // Progress should be a percentage
    expect(Number.isFinite(data.progress.percent)).toBe(true);
  });

  test('API - 剩余时间估算', async () => {
    const token = await loginUser(TEST_USERS.progress);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/progress`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify estimated_remaining_days is present
    expect(data).toHaveProperty('estimated_remaining_days');

    // For a new path, remaining days should be positive or zero
    expect(data.estimated_remaining_days).toBeGreaterThanOrEqual(0);

    // Verify ahead/behind schedule status
    expect(data).toHaveProperty('ahead_behind_schedule');
    expect(['ahead', 'on_track', 'behind']).toContain(data.ahead_behind_schedule);
  });

  test('API - 未授权访问返回 403', async () => {
    // Create a second user
    const otherUser = {
      username: 'e2e_other_progress',
      email: 'e2e_other_progress@test.com',
      password: 'Pass1234'
    };
    await registerUser(otherUser);

    const token1 = await loginUser(TEST_USERS.progress);
    const token2 = await loginUser(otherUser);

    // User 1 creates a path
    const pathData = await createPath(token1, 'ai-engineer');
    const pathId = pathData.path_id;

    // User 2 tries to access User 1's path
    const res = await fetch(`${API_URL}/paths/${pathId}/progress`, {
      headers: {
        'Authorization': `Bearer ${token2}`,
      },
    });

    expect(res.status).toBe(403);
  });

  test('API - 不存在路径返回 404', async () => {
    const token = await loginUser(TEST_USERS.progress);

    const res = await fetch(`${API_URL}/paths/99999/progress`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(404);
  });
});

test.describe('路径进度 UI 测试', () => {
  test('页面加载无错误', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    page.on('pageerror', err => errors.push(`Uncaught: ${err.message}`));

    // Navigate to progress page (will redirect to login if not authenticated)
    await page.goto(`${BASE_URL}/#/progress`);
    await page.waitForTimeout(2000);

    // No JS errors
    expect(errors.filter(e => !e.includes('401') && !e.includes('403'))).toEqual([]);

    await context.close();
  });
});
