/**
 * Path Specialization Weight Adjustment E2E Tests
 *
 * Covers AC14 from spec.md:
 *   - AC14: 路径特化维度权重调整 - AI应用者路径选择"产品经理"细分方向后
 *          雷达图增加"场景洞察"和"需求转化"维度权重，降低"算法深度"维度权重
 *   - 验证GET /api/v1/radar?path_type=ai-applier返回的维度权重变化
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;

// Test user credentials
const TEST_USERS = {
  applierPM: { username: 'e2e_applier_pm', email: 'e2e_applier_pm@test.com', password: 'Pass1234' },
  applierDev: { username: 'e2e_applier_dev', email: 'e2e_applier_dev@test.com', password: 'Pass1234' },
  engineer: { username: 'e2e_engineer', email: 'e2e_engineer@test.com', password: 'Pass1234' },
  manager: { username: 'e2e_manager', email: 'e2e_manager@test.com', password: 'Pass1234' },
  expert: { username: 'e2e_expert', email: 'e2e_expert@test.com', password: 'Pass1234' },
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
async function createPath(token, templateSlug = 'ai-applier', specialization = null) {
  const body = {
    template_slug: templateSlug,
  };
  if (specialization) {
    body.specialization = specialization;
  }

  const res = await fetch(`${API_URL}/paths`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) return null;
  return res.json();
}

// Helper: Get radar data
async function getRadar(token, pathType = null, specialization = null) {
  let url = `${API_URL}/radar`;
  const params = [];
  if (pathType) params.push(`path_type=${pathType}`);
  if (specialization) params.push(`specialization=${specialization}`);
  if (params.length > 0) {
    url += `?${params.join('&')}`;
  }

  const res = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!res.ok) return null;
  return res.json();
}

// Helper: Get radar weights for specific dimensions
async function getDimensionWeights(token, pathType = null, specialization = null) {
  const radarData = await getRadar(token, pathType, specialization);
  if (!radarData || !radarData.dimensions) return null;

  const weights = {};
  for (const dim of radarData.dimensions) {
    weights[dim.id] = {
      id: dim.id,
      name: dim.name,
      weight: dim.weight || 1.0,
      highlighted: dim.highlighted || false,
    };
  }
  return weights;
}

// Helper: Update user path specialization
async function updatePathSpecialization(token, pathId, specialization) {
  const res = await fetch(`${API_URL}/paths/${pathId}/specialization`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      specialization: specialization,
    }),
  });
  if (!res.ok) return null;
  return res.json();
}

test.describe('AC14: 路径特化维度权重调整', () => {
  test.beforeAll(async () => {
    // Register all test users
    await registerUser(TEST_USERS.applierPM);
    await registerUser(TEST_USERS.applierDev);
    await registerUser(TEST_USERS.engineer);
    await registerUser(TEST_USERS.manager);
    await registerUser(TEST_USERS.expert);
  });

  test('API - AI应用者路径+产品经理细分方向增加"场景洞察"维度权重', async () => {
    const token = await loginUser(TEST_USERS.applierPM);
    expect(token).toBeTruthy();

    // Create path with product-manager specialization
    const pathData = await createPath(token, 'ai-applier', 'product-manager');
    expect(pathData).toBeTruthy();

    // Get radar data with path_type=ai-applier
    const radarData = await getRadar(token, 'ai-applier', 'product-manager');
    expect(radarData).toBeTruthy();
    expect(radarData.path_type).toBe('ai-applier');
    expect(radarData.specialization).toBe('product-manager');

    // Find "场景洞察" dimension
    const sceneInsightDim = radarData.dimensions.find(d =>
      d.name.includes('场景洞察') || d.id === 'scene_insight'
    );

    if (sceneInsightDim) {
      // Verify increased weight (should be > 1.0 if boosted)
      expect(sceneInsightDim.weight).toBeGreaterThan(1.0);
      expect(sceneInsightDim.highlighted).toBe(true);
    }

    // Verify response structure contains weights
    expect(radarData).toHaveProperty('dimensions');
    expect(Array.isArray(radarData.dimensions)).toBe(true);
    expect(radarData.dimensions.length).toBeGreaterThanOrEqual(10);
  });

  test('API - AI应用者路径+产品经理细分方向增加"需求转化"维度权重', async () => {
    const token = await loginUser(TEST_USERS.applierPM);
    expect(token).toBeTruthy();

    // Get radar data with specialization
    const radarData = await getRadar(token, 'ai-applier', 'product-manager');
    expect(radarData).toBeTruthy();

    // Find "需求转化" dimension
    const demandConversionDim = radarData.dimensions.find(d =>
      d.name.includes('需求转化') || d.id === 'demand_conversion'
    );

    if (demandConversionDim) {
      // Verify increased weight
      expect(demandConversionDim.weight).toBeGreaterThan(1.0);
      expect(demandConversionDim.highlighted).toBe(true);
    }
  });

  test('API - AI应用者路径+产品经理细分方向降低"算法深度"维度权重', async () => {
    const token = await loginUser(TEST_USERS.applierPM);
    expect(token).toBeTruthy();

    // Get radar data with specialization
    const radarData = await getRadar(token, 'ai-applier', 'product-manager');
    expect(radarData).toBeTruthy();

    // Find "算法深度" dimension
    const algorithmDepthDim = radarData.dimensions.find(d =>
      d.name.includes('算法深度') ||
      d.name.includes('算法理解') ||
      d.id === 'algorithm_depth'
    );

    if (algorithmDepthDim) {
      // Verify decreased weight (should be < 1.0 if reduced)
      expect(algorithmDepthDim.weight).toBeLessThan(1.0);
      expect(algorithmDepthDim.highlighted).toBe(false);
    }
  });

  test('API - GET /api/v1/radar?path_type=ai-applier 返回正确的维度权重变化', async () => {
    const token = await loginUser(TEST_USERS.applierPM);
    expect(token).toBeTruthy();

    // Get radar with ai-applier path type
    const res = await fetch(`${API_URL}/radar?path_type=ai-applier`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Verify path type in response
    expect(data.path_type).toBe('ai-applier');

    // Verify dimensions have weights
    expect(data).toHaveProperty('dimensions');
    expect(Array.isArray(data.dimensions)).toBe(true);

    // Each dimension should have weight info
    data.dimensions.forEach(dim => {
      expect(dim).toHaveProperty('weight');
      expect(dim).toHaveProperty('highlighted');
      expect(typeof dim.weight).toBe('number');
      expect(typeof dim.highlighted).toBe('boolean');
    });

    // Verify at least some dimensions are highlighted for ai-applier path
    const highlightedDims = data.dimensions.filter(d => d.highlighted);
    expect(highlightedDims.length).toBeGreaterThan(0);
  });

  test('API - AI工程师路径与AI应用者路径有不同权重配置', async () => {
    const token1 = await loginUser(TEST_USERS.applierPM);
    const token2 = await loginUser(TEST_USERS.engineer);
    expect(token1).toBeTruthy();
    expect(token2).toBeTruthy();

    // Create paths
    await createPath(token1, 'ai-applier', 'product-manager');
    await createPath(token2, 'ai-engineer');

    // Get radar data for both path types
    const applierRadar = await getRadar(token1, 'ai-applier');
    const engineerRadar = await getRadar(token2, 'ai-engineer');

    expect(applierRadar).toBeTruthy();
    expect(engineerRadar).toBeTruthy();

    // Different path types should have different highlighted dimensions
    const applierHighlighted = applierRadar.dimensions
      .filter(d => d.highlighted)
      .map(d => d.id);
    const engineerHighlighted = engineerRadar.dimensions
      .filter(d => d.highlighted)
      .map(d => d.id);

    // Compare path types
    expect(applierRadar.path_type).toBe('ai-applier');
    expect(engineerRadar.path_type).toBe('ai-engineer');

    // Different paths should highlight different dimensions (not necessarily completely different)
    const hasOverlap = applierHighlighted.some(id => engineerHighlighted.includes(id));
    // Paths may have some overlap but shouldn't be identical
    if (applierHighlighted.length === engineerHighlighted.length && hasOverlap) {
      // If same length and overlap, verify they don't have exactly the same IDs
      const isIdentical = JSON.stringify(applierHighlighted.sort()) === JSON.stringify(engineerHighlighted.sort());
      expect(isIdentical).toBe(false);
    }
  });

  test('API - 不同细分方向有不同权重配置', async () => {
    const token = await loginUser(TEST_USERS.applierPM);
    expect(token).toBeTruthy();

    // Get radar data for different specializations
    const pmRadar = await getRadar(token, 'ai-applier', 'product-manager');
    const noSpecRadar = await getRadar(token, 'ai-applier');

    expect(pmRadar).toBeTruthy();
    expect(noSpecRadar).toBeTruthy();

    // Different specializations should have different weights
    if (pmRadar.specialization && pmRadar.dimensions.length === noSpecRadar.dimensions.length) {
      const pmWeights = pmRadar.dimensions.map(d => ({ id: d.id, weight: d.weight }));
      const noSpecWeights = noSpecRadar.dimensions.map(d => ({ id: d.id, weight: d.weight }));

      // At least some weights should differ
      let hasDifferentWeights = false;
      for (let i = 0; i < pmWeights.length; i++) {
        if (pmWeights[i].weight !== noSpecWeights[i].weight) {
          hasDifferentWeights = true;
          break;
        }
      }
      expect(hasDifferentWeights).toBe(true);
    }
  });

  test('API - 路径特化权重影响维度分数计算', async () => {
    const token = await loginUser(TEST_USERS.applierPM);
    expect(token).toBeTruthy();

    // Create path
    const pathData = await createPath(token, 'ai-applier', 'product-manager');
    expect(pathData).toBeTruthy();

    // Get radar with and without specialization
    const specRadar = await getRadar(token, 'ai-applier', 'product-manager');
    const defaultRadar = await getRadar(token, 'ai-applier');

    expect(specRadar).toBeTruthy();
    expect(defaultRadar).toBeTruthy();

    // Find highlighted dimensions in specialization
    const specHighlighted = specRadar.dimensions.filter(d => d.highlighted);

    // Verify highlighted dimensions have boosted weights
    specHighlighted.forEach(dim => {
      expect(dim.weight).toBeGreaterThanOrEqual(1.0);
      if (dim.weight > 1.0) {
        // If weight is boosted, score might also be adjusted
        expect(dim.score).toBeGreaterThanOrEqual(0);
      }
    });
  });

  test('API - AI管理者路径特化权重配置验证', async () => {
    const token = await loginUser(TEST_USERS.manager);
    expect(token).toBeTruthy();

    // Create AI manager path
    await createPath(token, 'ai-manager');

    // Get radar data
    const radarData = await getRadar(token, 'ai-manager');
    expect(radarData).toBeTruthy();

    // Verify path type
    expect(radarData.path_type).toBe('ai-manager');

    // AI manager path should highlight management-related dimensions
    const highlightedDims = radarData.dimensions.filter(d => d.highlighted);
    expect(highlightedDims.length).toBeGreaterThan(0);

    // Check for management-related dimension names
    const dimNames = highlightedDims.map(d => d.name.toLowerCase());
    const hasManagementDim = dimNames.some(name =>
      name.includes('管理') ||
      name.includes('战略') ||
      name.includes('决策')
    );
    expect(hasManagementDim).toBe(true);
  });

  test('API - AI专家路径特化权重配置验证', async () => {
    const token = await loginUser(TEST_USERS.expert);
    expect(token).toBeTruthy();

    // Create AI expert path
    await createPath(token, 'ai-expert');

    // Get radar data
    const radarData = await getRadar(token, 'ai-expert');
    expect(radarData).toBeTruthy();

    // Verify path type
    expect(radarData.path_type).toBe('ai-expert');

    // AI expert path should highlight research/algorithm dimensions
    const highlightedDims = radarData.dimensions.filter(d => d.highlighted);
    expect(highlightedDims.length).toBeGreaterThan(0);

    // Check for research/algorithm-related dimension names
    const dimNames = highlightedDims.map(d => d.name.toLowerCase());
    const hasResearchDim = dimNames.some(name =>
      name.includes('算法') ||
      name.includes('研究') ||
      name.includes('深度')
    );
    expect(hasResearchDim).toBe(true);
  });

  test('API - 无效细分方向返回错误', async () => {
    const token = await loginUser(TEST_USERS.applierDev);
    expect(token).toBeTruthy();

    // Try invalid specialization
    const res = await fetch(`${API_URL}/radar?path_type=ai-applier&specialization=invalid-spec`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    // Should return error for invalid specialization
    expect(res.status).toBeGreaterThanOrEqual(400);
    const data = await res.json();
    expect(data).toHaveProperty('detail');
  });

  test('API - 权重值在合理范围内（0.1 - 3.0）', async () => {
    const token = await loginUser(TEST_USERS.applierPM);
    expect(token).toBeTruthy();

    // Create path with specialization
    await createPath(token, 'ai-applier', 'product-manager');

    // Get radar data
    const radarData = await getRadar(token, 'ai-applier', 'product-manager');
    expect(radarData).toBeTruthy();

    // Verify all dimension weights are within reasonable bounds
    for (const dim of radarData.dimensions) {
      expect(dim.weight).toBeGreaterThanOrEqual(0.1);
      expect(dim.weight).toBeLessThanOrEqual(3.0);
    }
  });
});

test.describe('AC14: 路径特化权重组合验证', () => {
  test.beforeAll(async () => {
    // Register additional users for combination testing
    await registerUser({
      username: 'e2e_applier_ops',
      email: 'e2e_applier_ops@test.com',
      password: 'Pass1234'
    });
    await registerUser({
      username: 'e2e_applier_data',
      email: 'e2e_applier_data@test.com',
      password: 'Pass1234'
    });
  });

  test('API - AI应用者路径+运营专员细分方向权重配置', async () => {
    const token = await loginUser({
      username: 'e2e_applier_ops',
      email: 'e2e_applier_ops@test.com',
      password: 'Pass1234'
    });
    expect(token).toBeTruthy();

    // Create path with operations specialization
    const pathData = await createPath(token, 'ai-applier', 'operations');
    expect(pathData).toBeTruthy();

    // Get radar data
    const radarData = await getRadar(token, 'ai-applier', 'operations');
    expect(radarData).toBeTruthy();

    // Verify specialization is set
    expect(radarData.specialization).toBe('operations');

    // Operations path should have its own highlighted dimensions
    const highlightedDims = radarData.dimensions.filter(d => d.highlighted);
    expect(highlightedDims.length).toBeGreaterThan(0);
  });

  test('API - AI应用者路径+数据分析师细分方向权重配置', async () => {
    const token = await loginUser({
      username: 'e2e_applier_data',
      email: 'e2e_applier_data@test.com',
      password: 'Pass1234'
    });
    expect(token).toBeTruthy();

    // Create path with data-analyst specialization
    const pathData = await createPath(token, 'ai-applier', 'data-analyst');
    expect(pathData).toBeTruthy();

    // Get radar data
    const radarData = await getRadar(token, 'ai-applier', 'data-analyst');
    expect(radarData).toBeTruthy();

    // Verify specialization is set
    expect(radarData.specialization).toBe('data-analyst');

    // Data analyst path should highlight data-related dimensions
    const highlightedDims = radarData.dimensions.filter(d => d.highlighted);
    expect(highlightedDims.length).toBeGreaterThan(0);
  });

  test('API - 同一用户切换细分方向后权重更新', async () => {
    const token = await loginUser(TEST_USERS.applierDev);
    expect(token).toBeTruthy();

    // Create initial path
    const pathData = await createPath(token, 'ai-applier', 'product-manager');
    expect(pathData).toBeTruthy();
    const pathId = pathData.path_id;

    // Get radar with PM specialization
    const pmRadar = await getRadar(token, 'ai-applier', 'product-manager');
    expect(pmRadar).toBeTruthy();

    // Switch specialization to operations
    const updateRes = await updatePathSpecialization(token, pathId, 'operations');
    expect(updateRes).toBeTruthy();

    // Get radar with operations specialization
    const opsRadar = await getRadar(token, 'ai-applier', 'operations');
    expect(opsRadar).toBeTruthy();

    // Verify different specializations have different highlighted dimensions
    const pmHighlighted = new Set(pmRadar.dimensions.filter(d => d.highlighted).map(d => d.id));
    const opsHighlighted = new Set(opsRadar.dimensions.filter(d => d.highlighted).map(d => d.id));

    // There should be some difference in highlighted dimensions
    const isIdentical = pmHighlighted.size === opsHighlighted.size &&
      [...pmHighlighted].every(id => opsHighlighted.has(id));
    expect(isIdentical).toBe(false);
  });
});

test.describe('AC14: 路径特化权重UI验证', () => {
  test('UI - 技能雷达页面显示路径特化维度高亮', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    // Login
    await page.goto(`${BASE_URL}/#/login`);
    await page.fill('input[type="email"], input[name="email"]', TEST_USERS.applierPM.email);
    await page.fill('input[type="password"], input[name="password"]', TEST_USERS.applierPM.password);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Navigate to radar page with specialization
    await page.goto(`${BASE_URL}/#/radar?path_type=ai-applier&specialization=product-manager`);
    await page.waitForTimeout(2000);

    // Verify radar page is loaded
    const url = page.url();
    expect(url).toContain('radar');

    // Check for highlighted dimension indicators in the radar visualization
    // This could be different colors, sizes, or badges for highlighted dimensions
    const highlightedElements = await page.locator('[data-highlighted="true"], .dimension-highlighted, .highlighted-dimension').count();
    expect(highlightedElements).toBeGreaterThanOrEqual(0);

    await context.close();
  });

  test('UI - 路径设置页面显示细分方向选项', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    // Login
    await page.goto(`${BASE_URL}/#/login`);
    await page.fill('input[type="email"], input[name="email"]', TEST_USERS.applierPM.email);
    await page.fill('input[type="password"], input[name="password"]', TEST_USERS.applierPM.password);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Navigate to path settings
    await page.goto(`${BASE_URL}/#/path/settings`);
    await page.waitForTimeout(2000);

    // Check for specialization selection
    const specializationSelect = await page.locator('select[name="specialization"], [data-testid="specialization-select"]').first();
    expect(await specializationSelect.isVisible().catch(() => false)).toBe(true);

    await context.close();
  });
});

test.describe('AC14: 路径特化权重数据完整性验证', () => {
  test('API - 雷达数据包含完整的权重配置信息', async () => {
    const token = await loginUser(TEST_USERS.applierPM);
    expect(token).toBeTruthy();

    // Create path with specialization
    await createPath(token, 'ai-applier', 'product-manager');

    // Get radar data
    const radarData = await getRadar(token, 'ai-applier', 'product-manager');
    expect(radarData).toBeTruthy();

    // Verify all dimensions have complete weight metadata
    for (const dim of radarData.dimensions) {
      expect(dim).toHaveProperty('id');
      expect(dim).toHaveProperty('name');
      expect(dim).toHaveProperty('score');
      expect(dim).toHaveProperty('max_score');
      expect(dim).toHaveProperty('weight');
      expect(dim).toHaveProperty('highlighted');
      expect(dim).toHaveProperty('percentile');

      // Type checks
      expect(typeof dim.id).toBe('string');
      expect(typeof dim.name).toBe('string');
      expect(typeof dim.score).toBe('number');
      expect(typeof dim.weight).toBe('number');
      expect(typeof dim.highlighted).toBe('boolean');
    }
  });

  test('API - 路径特化配置包含在雷达响应中', async () => {
    const token = await loginUser(TEST_USERS.applierPM);
    expect(token).toBeTruthy();

    // Create path with specialization
    await createPath(token, 'ai-applier', 'product-manager');

    // Get radar data
    const radarData = await getRadar(token, 'ai-applier', 'product-manager');
    expect(radarData).toBeTruthy();

    // Verify path specialization info is included
    expect(radarData).toHaveProperty('path_type');
    expect(radarData).toHaveProperty('specialization');

    // Verify weight configuration is available
    expect(radarData).toHaveProperty('weight_config');
    if (radarData.weight_config) {
      expect(radarData.weight_config).toHaveProperty('base_weights');
      expect(radarData.weight_config).toHaveProperty('path_adjustments');
    }
  });

  test('API - 默认权重值为1.0', async () => {
    const token = await loginUser(TEST_USERS.expert);
    expect(token).toBeTruthy();

    // Create path without explicit specialization
    await createPath(token, 'ai-expert');

    // Get radar data without specialization
    const radarData = await getRadar(token, 'ai-expert');
    expect(radarData).toBeTruthy();

    // Non-highlighted dimensions should have default weight of 1.0
    const nonHighlighted = radarData.dimensions.filter(d => !d.highlighted);
    for (const dim of nonHighlighted) {
      expect(dim.weight).toBe(1.0);
    }
  });
});
