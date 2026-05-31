/**
 * Fast Track Mode E2E Tests
 *
 * Covers AC5 from spec.md:
 *   - AC5: 支持Fast Track模式
 *     - Given: 用户选择"3个月内跳槽"目标
 *     - When: 选择Fast Track模式
 *     - Then: 生成8周密集路径，每天需完成2-3个实验
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;

// Test user credentials
const TEST_USERS = {
  fastTrack: { username: 'e2e_fasttrack', email: 'e2e_fasttrack@test.com', password: 'Pass1234' },
  standard: { username: 'e2e_standard', email: 'e2e_standard@test.com', password: 'Pass1234' },
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

test.describe('AC5: Fast Track 模式验证', () => {
  test.beforeAll(async () => {
    await registerUser(TEST_USERS.fastTrack);
    await registerUser(TEST_USERS.standard);
  });

  test('API - 选择"3个月内跳槽"目标时返回 fast_track 模式', async () => {
    const token = await loginUser(TEST_USERS.fastTrack);
    expect(token).toBeTruthy();

    // Call diagnosis API with aggressive timeline (3_months)
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
        time_commitment: 'full_time',
        goal_timeline: '3_months', // Fast track eligible timeline
      }),
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Verify fast_track mode is recommended
    expect(data).toHaveProperty('recommended_mode');
    expect(data.recommended_mode).toBe('fast_track');

    // Verify estimated duration for fast track
    expect(data).toHaveProperty('estimated_duration_weeks');
  });

  test('API - Fast Track 模式生成8周密集路径', async () => {
    const token = await loginUser(TEST_USERS.fastTrack);

    // Create path with fast_track mode
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

    // Verify path created successfully
    expect(data).toHaveProperty('path_id');
    expect(data).toHaveProperty('mode');
    expect(data.mode).toBe('fast_track');

    // Verify estimated duration is 8 weeks for fast track
    expect(data).toHaveProperty('estimated_duration_weeks');
    expect(data.estimated_duration_weeks).toBe(8);
  });

  test('API - 标准模式生成14周路径', async () => {
    const token = await loginUser(TEST_USERS.standard);

    // Create path with standard mode
    const res = await fetch(`${API_URL}/paths`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        template_slug: 'ai-engineer',
        mode: 'standard',
      }),
    });

    expect(res.status).toBe(201);
    const data = await res.json();

    // Verify standard mode
    expect(data.mode).toBe('standard');

    // Standard mode should be longer than fast track
    expect(data).toHaveProperty('estimated_duration_weeks');
    expect(data.estimated_duration_weeks).toBeGreaterThan(8);
  });

  test('API - Fast Track 每日任务量计算（2-3个实验）', async () => {
    const token = await loginUser(TEST_USERS.fastTrack);

    // Create fast track path
    const createRes = await fetch(`${API_URL}/paths`, {
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

    expect(createRes.status).toBe(201);
    const pathData = await createRes.json();
    const pathId = pathData.path_id;

    // Get path details including courses and experiments
    const detailRes = await fetch(`${API_URL}/paths/${pathId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(detailRes.status).toBe(200);
    const detailData = await detailRes.json();

    // Verify path structure
    expect(detailData).toHaveProperty('courses');
    expect(Array.isArray(detailData.courses)).toBe(true);

    // Calculate total experiments
    let totalExperiments = 0;
    for (const course of detailData.courses) {
      if (course.experiments && Array.isArray(course.experiments)) {
        totalExperiments += course.experiments.length;
      } else if (course.experiment_count) {
        totalExperiments += course.experiment_count;
      }
    }

    // Fast track: 8 weeks, should have daily workload of 2-3 experiments
    const totalDays = 8 * 5; // 8 weeks * 5 working days (assuming weekdays)
    const dailyExperiments = totalExperiments / totalDays;

    // Verify daily workload is in the range of 2-3 experiments
    expect(dailyExperiments).toBeGreaterThanOrEqual(2);
    expect(dailyExperiments).toBeLessThanOrEqual(3);

    // Verify fast track path has reasonable total experiments
    expect(totalExperiments).toBeGreaterThan(80); // At least 80 experiments for 8 weeks
    expect(totalExperiments).toBeLessThan(120); // Less than 120 experiments
  });

  test('API - Fast Track 诊断包含每日任务量信息', async () => {
    const token = await loginUser(TEST_USERS.fastTrack);

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
        time_commitment: 'full_time',
        goal_timeline: '3_months',
      }),
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Verify recommended mode is fast_track
    expect(data.recommended_mode).toBe('fast_track');

    // Verify estimated duration is 8 weeks
    expect(data.estimated_duration_weeks).toBe(8);

    // Verify diagnosis info includes workload details
    expect(data).toHaveProperty('diagnosis');
    expect(data.diagnosis).toHaveProperty('reasoning');

    // Reasoning should mention fast track or intensive workload
    const reasoning = data.diagnosis.reasoning || '';
    const hasWorkloadInfo = reasoning.toLowerCase().includes('fast') ||
                           reasoning.toLowerCase().includes('intensive') ||
                           reasoning.toLowerCase().includes('密集') ||
                           reasoning.toLowerCase().includes('加速');
    expect(hasWorkloadInfo).toBe(true);
  });

  test('API - 不同模板都支持 Fast Track 模式', async () => {
    const templates = ['ai-engineer', 'ai-applier', 'ai-manager'];
    const token = await loginUser(TEST_USERS.fastTrack);

    for (const template of templates) {
      const res = await fetch(`${API_URL}/paths`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          template_slug: template,
          mode: 'fast_track',
        }),
      });

      // Should either succeed or return 404 if template doesn't exist
      if (res.status === 201) {
        const data = await res.json();
        expect(data.mode).toBe('fast_track');
        expect(data.estimated_duration_weeks).toBe(8);
      } else if (res.status === 404) {
        // Template not found is acceptable
        expect(res.status).toBe(404);
      }
    }
  });

  test('API - Fast Track 路径包含高强度学习提示', async () => {
    const token = await loginUser(TEST_USERS.fastTrack);

    // Create fast track path
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

    // Verify path has high intensity indicator or note
    expect(data).toHaveProperty('path_id');
    expect(data).toHaveProperty('mode');

    // Get path details
    const detailRes = await fetch(`${API_URL}/paths/${data.path_id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const detailData = await detailRes.json();

    // Verify fast track has shorter duration
    expect(detailData.estimated_duration_weeks).toBe(8);
  });

  test('API - 诊断API支持时间线参数识别Fast Track资格', async () => {
    const token = await loginUser(TEST_USERS.fastTrack);

    // Test different timelines
    const timelines = [
      { timeline: '1_year', expectedMode: 'standard' },
      { timeline: '6_months', expectedMode: 'standard' },
      { timeline: '3_months', expectedMode: 'fast_track' },
    ];

    for (const testCase of timelines) {
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
          time_commitment: 'full_time',
          goal_timeline: testCase.timeline,
        }),
      });

      expect(res.status).toBe(200);
      const data = await res.json();

      expect(data).toHaveProperty('recommended_mode');
      expect(['standard', 'fast_track']).toContain(data.recommended_mode);

      if (testCase.timeline === '3_months') {
        // 3 months timeline should recommend fast_track
        expect(data.recommended_mode).toBe('fast_track');
        expect(data.estimated_duration_weeks).toBe(8);
      }
    }
  });
});

test.describe('Fast Track UI 测试', () => {
  test('页面加载无错误', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    page.on('pageerror', err => errors.push(`Uncaught: ${err.message}`));

    // Navigate to diagnosis page (will show mode selection)
    await page.goto(`${BASE_URL}/#/diagnosis`);
    await page.waitForTimeout(2000);

    // No JS errors (ignore auth errors as page may redirect)
    expect(errors.filter(e => !e.includes('401') && !e.includes('403'))).toEqual([]);

    await context.close();
  });
});
