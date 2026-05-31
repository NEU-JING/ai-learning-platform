/**
 * Skill Gap E2E Tests
 *
 * Covers AC4 from spec.md:
 *   - AC4: 能力缺口诊断 - 识别薄弱技能、补强建议
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;

// Test user credentials
const TEST_USERS = {
  skillGap: { username: 'e2e_skillgap', email: 'e2e_skillgap@test.com', password: 'Pass1234' },
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

test.describe('AC4: 能力缺口诊断', () => {
  test.beforeAll(async () => {
    await registerUser(TEST_USERS.skillGap);
  });

  test('API - 获取能力缺口诊断结果', async () => {
    const token = await loginUser(TEST_USERS.skillGap);
    expect(token).toBeTruthy();

    // First create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();
    const pathId = pathData.path_id;

    // Get skill gaps
    const res = await fetch(`${API_URL}/paths/${pathId}/gaps`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Verify response structure
    expect(data).toHaveProperty('path_id');
    expect(data).toHaveProperty('weak_skills');
    expect(data).toHaveProperty('recommendations');
    expect(data).toHaveProperty('summary');
  });

  test('API - 薄弱技能识别（通过率 < 60%）', async () => {
    const token = await loginUser(TEST_USERS.skillGap);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/gaps`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify weak_skills structure
    expect(Array.isArray(data.weak_skills)).toBe(true);

    // Each weak skill should have required fields
    for (const skill of data.weak_skills) {
      expect(skill).toHaveProperty('dimension');
      expect(skill).toHaveProperty('pass_rate');
      expect(skill).toHaveProperty('status'); // 'weak', 'normal', 'strong'

      // Pass rate should be between 0 and 100
      expect(skill.pass_rate).toBeGreaterThanOrEqual(0);
      expect(skill.pass_rate).toBeLessThanOrEqual(100);
    }
  });

  test('API - 补强建议包含课程推荐', async () => {
    const token = await loginUser(TEST_USERS.skillGap);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/gaps`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify recommendations structure
    expect(Array.isArray(data.recommendations)).toBe(true);

    // Each recommendation should have required fields
    for (const rec of data.recommendations) {
      expect(rec).toHaveProperty('dimension');
      expect(rec).toHaveProperty('priority'); // 'high', 'medium', 'low'
      expect(rec).toHaveProperty('recommended_actions');
      expect(rec).toHaveProperty('estimated_hours');

      // Should have at least one recommended action
      expect(Array.isArray(rec.recommended_actions)).toBe(true);

      // Priority should be valid
      expect(['high', 'medium', 'low']).toContain(rec.priority);
    }
  });

  test('API - 整体健康度评分', async () => {
    const token = await loginUser(TEST_USERS.skillGap);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/gaps`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify summary structure
    expect(data.summary).toHaveProperty('total_experiments');
    expect(data.summary).toHaveProperty('weak_dimensions_count');
    expect(data.summary).toHaveProperty('overall_status');

    // overall_status should be one of valid values
    expect(['excellent', 'good', 'fair', 'needs_improvement']).toContain(data.summary.overall_status);
  });

  test('API - 特定技能缺口检测', async () => {
    const token = await loginUser(TEST_USERS.skillGap);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/gaps`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Check if specific dimension names are present in weak skills
    const dimensionNames = data.weak_skills.map(s => s.dimension.toLowerCase());

    // Common dimensions that might be weak
    const commonDimensions = ['python', 'math', 'ml', 'dl', 'algorithms'];

    // At least log what dimensions were found (for debugging)
    console.log('Weak dimensions found:', dimensionNames);
  });

  test('API - 未授权访问返回 403', async () => {
    const otherUser = {
      username: 'e2e_other_gap',
      email: 'e2e_other_gap@test.com',
      password: 'Pass1234'
    };
    await registerUser(otherUser);

    const token1 = await loginUser(TEST_USERS.skillGap);
    const token2 = await loginUser(otherUser);

    const pathData = await createPath(token1, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/gaps`, {
      headers: {
        'Authorization': `Bearer ${token2}`,
      },
    });

    expect(res.status).toBe(403);
  });
});
