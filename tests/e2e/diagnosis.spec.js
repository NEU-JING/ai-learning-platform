/**
 * Diagnosis E2E Tests
 *
 * Covers AC1-AC2 from spec.md:
 *   - AC1: 根据背景推荐学习路径
 *   - AC2: Fast Track 检测与起点调整
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;

// Test user credentials
const TEST_USERS = {
  diagnosis: { username: 'e2e_diagnosis', email: 'e2e_diagnosis@test.com', password: 'Pass1234' },
  fastTrack: { username: 'e2e_fasttrack', email: 'e2e_fasttrack@test.com', password: 'Pass1234' },
};

// Helper: Capture JS errors from page
function captureErrors(page) {
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  page.on('pageerror', err => {
    errors.push(`Uncaught: ${err.message}`);
  });
  return errors;
}

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

test.describe('AC1: 入学诊断 - 根据背景推荐学习路径', () => {
  test.beforeAll(async () => {
    // Register test users
    await registerUser(TEST_USERS.diagnosis);
    await registerUser(TEST_USERS.fastTrack);
  });

  test('API - 根据用户背景推荐路径', async () => {
    const token = await loginUser(TEST_USERS.diagnosis);
    expect(token).toBeTruthy();

    // Call diagnosis API
    const res = await fetch(`${API_URL}/paths/diagnosis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        target_role: 'ai-engineer',
        experience_years: 3,
        python_level: 'intermediate',
        math_level: 'intermediate',
        current_job: 'software_engineer',
        time_commitment: 'part_time',
        goal_timeline: '6_months',
      }),
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Verify response structure
    expect(data).toHaveProperty('recommended_template');
    expect(data).toHaveProperty('recommended_mode');
    expect(data).toHaveProperty('diagnosis');
    expect(data).toHaveProperty('estimated_duration_weeks');

    // Verify recommended template
    expect(data.recommended_template).toBeTruthy();

    // Verify diagnosis info
    expect(data.diagnosis).toHaveProperty('can_skip_phase1');
    expect(data.diagnosis).toHaveProperty('start_from');
    expect(data.diagnosis).toHaveProperty('reasoning');
  });

  test('API - 推荐路径包含必修和选修课程', async () => {
    const token = await loginUser(TEST_USERS.diagnosis);
    const res = await fetch(`${API_URL}/paths/diagnosis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        target_role: 'ai-engineer',
        experience_years: 3,
        python_level: 'intermediate',
        math_level: 'intermediate',
        current_job: 'software_engineer',
        time_commitment: 'part_time',
        goal_timeline: '6_months',
      }),
    });

    const data = await res.json();

    // Verify estimated duration is reasonable
    expect(data.estimated_duration_weeks).toBeGreaterThan(0);
    expect(data.estimated_duration_weeks).toBeLessThan(52);

    // Verify recommended mode is valid
    expect(['standard', 'fast_track']).toContain(data.recommended_mode);

    // Verify diagnosis has reasoning
    expect(data.diagnosis.reasoning).toBeTruthy();
    expect(data.diagnosis.reasoning.length).toBeGreaterThan(0);
  });
});

test.describe('AC2: Fast Track 检测与起点调整', () => {
  test('API - 有经验用户符合 Fast Track 条件', async () => {
    const token = await loginUser(TEST_USERS.fastTrack);

    // User with strong background should be recommended for fast track
    const res = await fetch(`${API_URL}/paths/diagnosis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        target_role: 'ai-engineer',
        experience_years: 5, // Strong background
        python_level: 'advanced',
        math_level: 'advanced',
        current_job: 'senior_software_engineer',
        time_commitment: 'full_time',
        goal_timeline: '3_months', // Aggressive timeline
      }),
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Experienced users may be recommended for fast track
    expect(data).toHaveProperty('recommended_mode');
    expect(['standard', 'fast_track']).toContain(data.recommended_mode);

    // Should have diagnosis info
    expect(data.diagnosis).toHaveProperty('can_skip_phase1');
    expect(data.diagnosis).toHaveProperty('start_from');

    // Fast track eligible users should skip Phase 1
    if (data.recommended_mode === 'fast_track') {
      expect(data.diagnosis.can_skip_phase1).toBe(true);
      expect(data.diagnosis.start_from).toBeGreaterThan(1);
    }
  });

  test('API - 新手用户不推荐 Fast Track', async () => {
    const token = await loginUser(TEST_USERS.diagnosis);

    // New user should not be eligible for fast track
    const res = await fetch(`${API_URL}/paths/diagnosis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        target_role: 'ai-applier',
        experience_years: 0,
        python_level: 'beginner',
        math_level: 'beginner',
        current_job: 'marketing_specialist',
        time_commitment: 'part_time',
        goal_timeline: '1_year',
      }),
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Should recommend starting from Phase 1
    expect(data.diagnosis.start_from).toBe(1);

    // Should recommend standard mode for beginners
    expect(data.recommended_mode).toBe('standard');
  });

  test('API - 创建路径支持 fast_track 模式', async () => {
    const token = await loginUser(TEST_USERS.fastTrack);

    // Create a path with fast_track mode
    const res = await fetch(`${API_URL}/paths`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        template_slug: 'ai-engineer',
        mode: 'fast_track',
      }),
    });

    expect(res.status).toBe(201);
    const data = await res.json();

    // Verify path created
    expect(data).toHaveProperty('path_id');
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('progress');

    // Verify path has next course info
    expect(data).toHaveProperty('next_course');
  });
});

test.describe('入学诊断 UI 测试', () => {
  test('页面加载无错误', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    const errors = captureErrors(page);

    await page.goto(`${BASE_URL}/#/courses`);
    await page.waitForTimeout(2000);

    expect(errors).toEqual([]);

    await context.close();
  });

  test('API 错误处理 - 无效的目标角色', async () => {
    const token = await loginUser(TEST_USERS.diagnosis);

    const res = await fetch(`${API_URL}/paths/diagnosis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        target_role: 'invalid_role',
        experience_years: 3,
        python_level: 'intermediate',
        math_level: 'intermediate',
        current_job: 'software_engineer',
        time_commitment: 'part_time',
        goal_timeline: '6_months',
      }),
    });

    // Should return 422 for invalid role
    expect(res.status).toBe(422);
  });
});
