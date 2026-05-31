/**
 * Path Visualization E2E Tests
 *
 * Covers AC6 from spec.md:
 *   - AC6: 路径可视化数据接口 - 返回包含阶段节点、课程依赖、里程碑标记的JSON数据
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;

// Test user credentials
const TEST_USERS = {
  visualization: { username: 'e2e_visualization', email: 'e2e_visualization@test.com', password: 'Pass1234' },
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

test.describe('AC6: 路径可视化数据接口', () => {
  test.beforeAll(async () => {
    await registerUser(TEST_USERS.visualization);
  });

  test('API - 获取路径可视化数据返回正确结构', async () => {
    const token = await loginUser(TEST_USERS.visualization);
    expect(token).toBeTruthy();

    // First create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();
    expect(pathData).toHaveProperty('path_id');

    const pathId = pathData.path_id;

    // Get path visualization data
    const res = await fetch(`${API_URL}/paths/${pathId}/visualization`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Verify response structure
    expect(data).toHaveProperty('path_id');
    expect(data).toHaveProperty('path_name');
    expect(data).toHaveProperty('nodes');
    expect(data).toHaveProperty('edges');
    expect(data).toHaveProperty('milestones');

    // Verify path_id matches
    expect(data.path_id).toBe(pathId);
  });

  test('API - nodes数组包含阶段节点数据', async () => {
    const token = await loginUser(TEST_USERS.visualization);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/visualization`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify nodes is an array
    expect(Array.isArray(data.nodes)).toBe(true);
    expect(data.nodes.length).toBeGreaterThan(0);

    // Each node should have required fields for visualization
    data.nodes.forEach(node => {
      expect(node).toHaveProperty('id');
      expect(node).toHaveProperty('type'); // 'phase', 'course', 'milestone'
      expect(node).toHaveProperty('label');
      expect(node).toHaveProperty('position');
      expect(node.position).toHaveProperty('x');
      expect(node.position).toHaveProperty('y');
      expect(node).toHaveProperty('data');
    });

    // Verify phase nodes exist
    const phaseNodes = data.nodes.filter(n => n.type === 'phase');
    expect(phaseNodes.length).toBeGreaterThan(0);

    // Phase nodes should have phase-specific data
    phaseNodes.forEach(phase => {
      expect(phase.data).toHaveProperty('phase_id');
      expect(phase.data).toHaveProperty('phase_name');
      expect(phase.data).toHaveProperty('order');
      expect(phase.data).toHaveProperty('status'); // 'completed', 'in_progress', 'locked'
    });
  });

  test('API - edges数组包含课程依赖关系', async () => {
    const token = await loginUser(TEST_USERS.visualization);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/visualization`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify edges is an array
    expect(Array.isArray(data.edges)).toBe(true);

    // Each edge should represent a dependency relationship
    data.edges.forEach(edge => {
      expect(edge).toHaveProperty('id');
      expect(edge).toHaveProperty('source'); // Source node ID
      expect(edge).toHaveProperty('target'); // Target node ID
      expect(edge).toHaveProperty('type'); // 'prerequisite', 'next', 'milestone_link'
      expect(['prerequisite', 'next', 'milestone_link']).toContain(edge.type);
    });

    // Verify edges connect existing nodes
    const nodeIds = new Set(data.nodes.map(n => n.id));
    data.edges.forEach(edge => {
      expect(nodeIds.has(edge.source)).toBe(true);
      expect(nodeIds.has(edge.target)).toBe(true);
    });
  });

  test('API - 验证里程碑标记数据', async () => {
    const token = await loginUser(TEST_USERS.visualization);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/visualization`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify milestones is an array
    expect(Array.isArray(data.milestones)).toBe(true);

    // Each milestone should have complete marker data
    data.milestones.forEach(milestone => {
      expect(milestone).toHaveProperty('id');
      expect(milestone).toHaveProperty('name');
      expect(milestone).toHaveProperty('description');
      expect(milestone).toHaveProperty('order');
      expect(milestone).toHaveProperty('status'); // 'completed', 'available', 'locked'
      expect(['completed', 'available', 'locked']).toContain(milestone.status);
      expect(milestone).toHaveProperty('node_id'); // Reference to corresponding node
      expect(milestone).toHaveProperty('criteria'); // Completion criteria
    });

    // Milestone node references should exist in nodes array
    const nodeIds = new Set(data.nodes.map(n => n.id));
    data.milestones.forEach(milestone => {
      expect(nodeIds.has(milestone.node_id)).toBe(true);
    });
  });

  test('API - 可视化数据包含课程节点详情', async () => {
    const token = await loginUser(TEST_USERS.visualization);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/visualization`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify course nodes exist
    const courseNodes = data.nodes.filter(n => n.type === 'course');

    // Course nodes should have course-specific data
    courseNodes.forEach(course => {
      expect(course.data).toHaveProperty('course_id');
      expect(course.data).toHaveProperty('course_name');
      expect(course.data).toHaveProperty('chapter_count');
      expect(course.data).toHaveProperty('completed_chapters');
      expect(course.data).toHaveProperty('status'); // 'completed', 'in_progress', 'locked'
      expect(['completed', 'in_progress', 'locked', 'available']).toContain(course.data.status);
      expect(course.data).toHaveProperty('estimated_hours');
    });
  });

  test('API - 验证节点位置布局合理性', async () => {
    const token = await loginUser(TEST_USERS.visualization);
    const pathData = await createPath(token, 'ai-engineer');
    const pathId = pathData.path_id;

    const res = await fetch(`${API_URL}/paths/${pathId}/visualization`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify all nodes have valid positions
    data.nodes.forEach(node => {
      expect(Number.isFinite(node.position.x)).toBe(true);
      expect(Number.isFinite(node.position.y)).toBe(true);
      expect(node.position.x).toBeGreaterThanOrEqual(0);
      expect(node.position.y).toBeGreaterThanOrEqual(0);
    });

    // Phase nodes should be arranged in order (left to right or top to bottom)
    const phaseNodes = data.nodes.filter(n => n.type === 'phase');
    phaseNodes.sort((a, b) => a.data.order - b.data.order);

    // Verify phases are positioned sequentially
    for (let i = 1; i < phaseNodes.length; i++) {
      const prev = phaseNodes[i - 1];
      const curr = phaseNodes[i];
      // X position should generally increase for sequential phases
      expect(curr.position.x).toBeGreaterThanOrEqual(prev.position.x);
    }
  });

  test('API - 未授权访问返回 403', async () => {
    // Create a second user
    const otherUser = {
      username: 'e2e_other_visualization',
      email: 'e2e_other_visualization@test.com',
      password: 'Pass1234'
    };
    await registerUser(otherUser);

    const token1 = await loginUser(TEST_USERS.visualization);
    const token2 = await loginUser(otherUser);

    // User 1 creates a path
    const pathData = await createPath(token1, 'ai-engineer');
    const pathId = pathData.path_id;

    // User 2 tries to access User 1's visualization data
    const res = await fetch(`${API_URL}/paths/${pathId}/visualization`, {
      headers: {
        'Authorization': `Bearer ${token2}`,
      },
    });

    expect(res.status).toBe(403);
  });

  test('API - 不存在路径返回 404', async () => {
    const token = await loginUser(TEST_USERS.visualization);

    const res = await fetch(`${API_URL}/paths/99999/visualization`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(404);
  });

  test('API - 验证不同路径模板的可视化数据', async () => {
    const token = await loginUser(TEST_USERS.visualization);

    // Test AI Expert path
    const expertPath = await createPath(token, 'ai-expert', 'standard');
    expect(expertPath).toBeTruthy();

    const res = await fetch(`${API_URL}/paths/${expertPath.path_id}/visualization`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // AI Expert path should have more phases/courses
    const phaseNodes = data.nodes.filter(n => n.type === 'phase');
    expect(phaseNodes.length).toBeGreaterThanOrEqual(4);

    // Should have all required structure
    expect(data).toHaveProperty('nodes');
    expect(data).toHaveProperty('edges');
    expect(data).toHaveProperty('milestones');
  });
});

test.describe('路径可视化 UI 测试', () => {
  test('页面加载无错误', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    page.on('pageerror', err => errors.push(`Uncaught: ${err.message}`));

    // Navigate to path visualization page
    await page.goto(`${BASE_URL}/#/path/visualization`);
    await page.waitForTimeout(2000);

    // No JS errors (excluding auth-related)
    expect(errors.filter(e => !e.includes('401') && !e.includes('403'))).toEqual([]);

    await context.close();
  });

  test('可视化组件渲染检查', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    await page.goto(`${BASE_URL}/#/path/visualization`);
    await page.waitForTimeout(2000);

    // Check for visualization container
    const container = await page.locator('.path-visualization, [data-testid="path-visualization"], .visualization-container').first();
    expect(await container.isVisible().catch(() => false)).toBe(true);

    await context.close();
  });
});
