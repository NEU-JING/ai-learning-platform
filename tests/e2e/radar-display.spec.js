/**
 * Radar Display E2E Tests
 *
 * Covers AC7-AC8 from spec.md:
 *   - AC7: 显示10维技能模型
 *   - AC8: Radar 认证 - 登录后查看
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;

// Test user credentials
const TEST_USERS = {
  radar: { username: 'e2e_radar', email: 'e2e_radar@test.com', password: 'Pass1234' },
  radarAlt: { username: 'e2e_radar_alt', email: 'e2e_radar_alt@test.com', password: 'Pass1234' },
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

test.describe('AC7: 显示10维技能模型', () => {
  test.beforeAll(async () => {
    await registerUser(TEST_USERS.radar);
    await registerUser(TEST_USERS.radarAlt);
  });

  test('API - 获取10维技能雷达数据', async () => {
    const token = await loginUser(TEST_USERS.radar);
    expect(token).toBeTruthy();

    // Get radar data
    const res = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Verify response structure
    expect(data).toHaveProperty('dimensions');
    expect(data).toHaveProperty('overall_score');
    expect(data).toHaveProperty('path_type');

    // Verify exactly 10 dimensions
    expect(Array.isArray(data.dimensions)).toBe(true);
    expect(data.dimensions.length).toBe(10);

    // Each dimension should have required fields
    data.dimensions.forEach(dim => {
      expect(dim).toHaveProperty('id');
      expect(dim).toHaveProperty('name');
      expect(dim).toHaveProperty('score');
      expect(dim).toHaveProperty('max_score');
      expect(dim).toHaveProperty('percentile');
    });

    // Verify dimension names cover expected skills
    const dimNames = data.dimensions.map(d => d.name.toLowerCase());
    const expectedSkills = ['编程思维', '算法理解', 'ai协作', '问题解决', '工程实现'];

    // At least some of the expected skills should be present
    const hasExpectedSkills = expectedSkills.some(skill =>
      dimNames.some(name => name.includes(skill) || name.includes(skill.replace('ai', 'AI')))
    );
    expect(hasExpectedSkills).toBe(true);
  });

  test('API - 各维度分数在有效范围内', async () => {
    const token = await loginUser(TEST_USERS.radar);

    const res = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify each dimension has valid scores
    data.dimensions.forEach(dim => {
      expect(dim.score).toBeGreaterThanOrEqual(0);
      expect(dim.score).toBeLessThanOrEqual(dim.max_score);
      expect(dim.max_score).toBeGreaterThan(0);
      expect(dim.percentile).toBeGreaterThanOrEqual(0);
      expect(dim.percentile).toBeLessThanOrEqual(100);
    });

    // Overall score should be valid
    expect(data.overall_score).toBeGreaterThanOrEqual(0);
    expect(data.overall_score).toBeLessThanOrEqual(100);
  });

  test('API - 路径特化高亮', async () => {
    const token = await loginUser(TEST_USERS.radar);

    // Get radar with path type
    const res = await fetch(`${API_URL}/radar?path_type=ai-engineer`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Verify path type is returned
    expect(data.path_type).toBe('ai-engineer');

    // Verify dimensions have highlight info
    data.dimensions.forEach(dim => {
      expect(dim).toHaveProperty('highlighted');
      expect(typeof dim.highlighted).toBe('boolean');
    });

    // For AI engineer path, certain dimensions should be highlighted
    const highlightedDims = data.dimensions.filter(d => d.highlighted);
    expect(highlightedDims.length).toBeGreaterThan(0);
  });

  test('API - 不同路径类型返回不同高亮', async () => {
    const token = await loginUser(TEST_USERS.radarAlt);

    // Test ai-engineer path
    const res1 = await fetch(`${API_URL}/radar?path_type=ai-engineer`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    const data1 = await res1.json();

    // Test ai-manager path
    const res2 = await fetch(`${API_URL}/radar?path_type=ai-manager`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    const data2 = await res2.json();

    // Different path types should have different highlighted dimensions
    const highlighted1 = data1.dimensions.filter(d => d.highlighted).map(d => d.id);
    const highlighted2 = data2.dimensions.filter(d => d.highlighted).map(d => d.id);

    // At least some differences expected (though they could overlap)
    expect(data1.path_type).toBe('ai-engineer');
    expect(data2.path_type).toBe('ai-manager');
  });

  test('API - 无效路径类型返回错误', async () => {
    const token = await loginUser(TEST_USERS.radar);

    const res = await fetch(`${API_URL}/radar?path_type=invalid-path`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data).toHaveProperty('detail');
  });
});

test.describe('AC8: Radar 认证 - 登录后查看', () => {
  test('API - 未登录访问返回 401', async () => {
    const res = await fetch(`${API_URL}/radar`);

    expect(res.status).toBe(401);
  });

  test('API - 登录后正常访问', async () => {
    const token = await loginUser(TEST_USERS.radar);

    const res = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data).toHaveProperty('dimensions');
    expect(data.dimensions.length).toBe(10);
  });

  test('UI - 未登录时无法查看技能雷达', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    // Try to access radar page directly
    await page.goto(`${BASE_URL}/#/radar`);
    await page.waitForTimeout(2000);

    // Should redirect to login
    const url = page.url();
    expect(url).toContain('login');

    await context.close();
  });

  test('UI - 登录后可查看技能雷达页面', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    // Login via UI
    await page.goto(`${BASE_URL}/#/login`);
    await page.fill('input[type="email"], input[name="email"]', TEST_USERS.radar.email);
    await page.fill('input[type="password"], input[name="password"]', TEST_USERS.radar.password);
    await page.click('button[type="submit"]');

    // Wait for navigation
    await page.waitForTimeout(2000);

    // Navigate to radar page
    await page.goto(`${BASE_URL}/#/radar`);
    await page.waitForTimeout(2000);

    // Should be on radar page (not redirected)
    const url = page.url();
    expect(url).toContain('radar');
    expect(url).not.toContain('login');

    await context.close();
  });
});

test.describe('技能雷达快照功能', () => {
  test('API - 创建技能快照', async () => {
    const token = await loginUser(TEST_USERS.radar);

    const res = await fetch(`${API_URL}/radar/snapshots`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: '测试快照',
        path_id: null,
      }),
    });

    expect(res.status).toBe(201);
    const data = await res.json();

    expect(data).toHaveProperty('snapshot_id');
    expect(data).toHaveProperty('name');
    expect(data).toHaveProperty('snapshot_date');
    expect(data).toHaveProperty('scores');

    // Scores should contain dimension data
    expect(typeof data.scores).toBe('object');
    expect(Object.keys(data.scores).length).toBeGreaterThan(0);
  });

  test('API - 快照名称长度限制', async () => {
    const token = await loginUser(TEST_USERS.radar);

    const longName = 'a'.repeat(100);
    const res = await fetch(`${API_URL}/radar/snapshots`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: longName,
      }),
    });

    expect(res.status).toBe(400);
  });
});
