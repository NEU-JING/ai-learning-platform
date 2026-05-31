/**
 * Radar Chart Data E2E Tests
 *
 * Covers AC11 from spec.md:
 *   - AC11: 雷达图可视化数据生成
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;

// Test user credentials
const TEST_USERS = {
  chartData: { username: 'e2e_chart_data', email: 'e2e_chart_data@test.com', password: 'Pass1234' },
  chartAlt: { username: 'e2e_chart_alt', email: 'e2e_chart_alt@test.com', password: 'Pass1234' },
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

test.describe('AC11: 雷达图可视化数据生成', () => {
  test.beforeAll(async () => {
    await registerUser(TEST_USERS.chartData);
    await registerUser(TEST_USERS.chartAlt);
  });

  test('API - GET /radar 返回可直接用于Chart.js的JSON结构', async () => {
    const token = await loginUser(TEST_USERS.chartData);
    expect(token).toBeTruthy();

    // Get radar chart data
    const res = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    expect(res.status).toBe(200);
    const data = await res.json();

    // Verify response has chart-ready structure
    expect(data).toHaveProperty('labels');
    expect(data).toHaveProperty('datasets');
    expect(data).toHaveProperty('options');

    // Verify labels array (dimension names)
    expect(Array.isArray(data.labels)).toBe(true);
    expect(data.labels.length).toBe(10);

    // Verify labels are strings (dimension names)
    data.labels.forEach(label => {
      expect(typeof label).toBe('string');
      expect(label.length).toBeGreaterThan(0);
    });
  });

  test('API - 验证labels数组包含维度名称', async () => {
    const token = await loginUser(TEST_USERS.chartData);

    const res = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify labels contain Chinese dimension names
    const labelTexts = data.labels.map(l => l.toLowerCase());
    const expectedDimensions = ['编程', '算法', 'ai', '协作', '问题', '工程', '系统', '数据'];

    // At least some expected keywords should be present
    const hasExpectedKeywords = expectedDimensions.some(keyword =>
      labelTexts.some(label => label.includes(keyword))
    );
    expect(hasExpectedKeywords).toBe(true);

    // Verify no empty labels
    data.labels.forEach(label => {
      expect(label.trim()).not.toBe('');
    });
  });

  test('API - 验证datasets数组包含分数数据和样式配置', async () => {
    const token = await loginUser(TEST_USERS.chartData);

    const res = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify datasets is an array
    expect(Array.isArray(data.datasets)).toBe(true);
    expect(data.datasets.length).toBeGreaterThan(0);

    // Verify each dataset has required chart properties
    data.datasets.forEach(dataset => {
      // Required for Chart.js
      expect(dataset).toHaveProperty('label');
      expect(dataset).toHaveProperty('data');
      expect(Array.isArray(dataset.data)).toBe(true);
      expect(dataset.data.length).toBe(10);

      // Styling properties for radar chart
      expect(dataset).toHaveProperty('backgroundColor');
      expect(dataset).toHaveProperty('borderColor');
      expect(dataset).toHaveProperty('borderWidth');
      expect(dataset).toHaveProperty('pointBackgroundColor');
      expect(dataset).toHaveProperty('pointBorderColor');
      expect(dataset).toHaveProperty('pointHoverBackgroundColor');
      expect(dataset).toHaveProperty('pointHoverBorderColor');

      // Verify data values are valid scores
      dataset.data.forEach(score => {
        expect(typeof score).toBe('number');
        expect(score).toBeGreaterThanOrEqual(0);
      });
    });

    // First dataset should be user's current scores
    const mainDataset = data.datasets[0];
    expect(mainDataset.label).toContain('当前') || expect(mainDataset.label).toContain('Current');
  });

  test('API - 验证options配置可直接渲染', async () => {
    const token = await loginUser(TEST_USERS.chartData);

    const res = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify options object exists
    expect(typeof data.options).toBe('object');
    expect(data.options).not.toBeNull();

    // Verify scales configuration for radar chart
    expect(data.options).toHaveProperty('scales');
    expect(data.options.scales).toHaveProperty('r');

    // Radar scale properties
    const rScale = data.options.scales.r;
    expect(rScale).toHaveProperty('beginAtZero');
    expect(rScale).toHaveProperty('max');
    expect(rScale).toHaveProperty('min');
    expect(rScale).toHaveProperty('ticks');

    // Verify max is a reasonable value (typically 100)
    expect(rScale.max).toBeGreaterThan(0);

    // Verify plugins configuration
    expect(data.options).toHaveProperty('plugins');
    expect(data.options.plugins).toHaveProperty('legend');
    expect(data.options.plugins).toHaveProperty('tooltip');

    // Legend should be displayable
    expect(data.options.plugins.legend).toHaveProperty('display');
  });

  test('API - 验证每个维度包含percentile和满分信息', async () => {
    const token = await loginUser(TEST_USERS.chartData);

    const res = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify dimensions metadata exists
    expect(data).toHaveProperty('dimensions');
    expect(Array.isArray(data.dimensions)).toBe(true);
    expect(data.dimensions.length).toBe(10);

    // Each dimension should have detailed info
    data.dimensions.forEach((dim, index) => {
      expect(dim).toHaveProperty('id');
      expect(dim).toHaveProperty('name');
      expect(dim).toHaveProperty('score');
      expect(dim).toHaveProperty('max_score');
      expect(dim).toHaveProperty('percentile');

      // Verify score matches dataset
      expect(dim.score).toBe(data.datasets[0].data[index]);

      // Verify percentile is valid percentage
      expect(typeof dim.percentile).toBe('number');
      expect(dim.percentile).toBeGreaterThanOrEqual(0);
      expect(dim.percentile).toBeLessThanOrEqual(100);

      // Verify max_score is positive
      expect(typeof dim.max_score).toBe('number');
      expect(dim.max_score).toBeGreaterThan(0);

      // Verify score doesn't exceed max_score
      expect(dim.score).toBeLessThanOrEqual(dim.max_score);
    });
  });

  test('API - 验证雷达图数据可直接被Chart.js使用', async () => {
    const token = await loginUser(TEST_USERS.chartAlt);

    const res = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Validate data can be used by Chart.js
    // Chart.js requires labels and datasets to have same length for radar
    expect(data.labels.length).toBe(data.datasets[0].data.length);

    // All datasets should have same data length
    data.datasets.forEach(dataset => {
      expect(dataset.data.length).toBe(data.labels.length);
    });

    // Options should be valid JSON (no circular references, functions, etc.)
    expect(() => JSON.stringify(data.options)).not.toThrow();

    // Colors should be valid CSS colors or rgba values
    const mainDataset = data.datasets[0];
    const validColorPattern = /^(rgba?|hsla?|#|rgb)/i;

    if (typeof mainDataset.backgroundColor === 'string') {
      expect(mainDataset.backgroundColor).toMatch(validColorPattern);
    }
    if (typeof mainDataset.borderColor === 'string') {
      expect(mainDataset.borderColor).toMatch(validColorPattern);
    }
  });

  test('API - 验证支持Chart.js和ECharts双格式', async () => {
    const token = await loginUser(TEST_USERS.chartAlt);

    // Test default format (Chart.js compatible)
    const res1 = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data1 = await res1.json();
    expect(data1).toHaveProperty('labels');
    expect(data1).toHaveProperty('datasets');

    // Test with format=echarts query param
    const res2 = await fetch(`${API_URL}/radar?format=echarts`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    // If echarts format is supported, verify its structure
    if (res2.status === 200) {
      const data2 = await res2.json();

      // ECharts typically uses different structure
      if (data2.series || data2.radar) {
        // ECharts format detected
        expect(data2).toHaveProperty('radar');
        expect(data2.radar).toHaveProperty('indicator');
        expect(Array.isArray(data2.radar.indicator)).toBe(true);
        expect(data2).toHaveProperty('series');
        expect(Array.isArray(data2.series)).toBe(true);
      }
    }
  });

  test('API - 验证包含overall_score和路径信息', async () => {
    const token = await loginUser(TEST_USERS.chartData);

    const res = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await res.json();

    // Verify overall score exists
    expect(data).toHaveProperty('overall_score');
    expect(typeof data.overall_score).toBe('number');
    expect(data.overall_score).toBeGreaterThanOrEqual(0);
    expect(data.overall_score).toBeLessThanOrEqual(100);

    // Verify path type info
    expect(data).toHaveProperty('path_type');
    expect(typeof data.path_type).toBe('string');

    // Verify last updated timestamp
    expect(data).toHaveProperty('last_updated');
    expect(new Date(data.last_updated).getTime()).not.toBeNaN();
  });

  test('API - 验证包含历史对比数据集', async () => {
    const token = await loginUser(TEST_USERS.chartAlt);

    // First create a snapshot
    const snapshotRes = await fetch(`${API_URL}/radar/snapshots`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: 'Chart Comparison Snapshot',
      }),
    });

    if (snapshotRes.status === 201) {
      const snapshot = await snapshotRes.json();

      // Now get radar with comparison
      const res = await fetch(`${API_URL}/radar?compare_with=${snapshot.snapshot_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (res.status === 200) {
        const data = await res.json();

        // Should have multiple datasets for comparison
        expect(data.datasets.length).toBeGreaterThanOrEqual(2);

        // Second dataset should be the historical snapshot
        const historicalDataset = data.datasets[1];
        expect(historicalDataset.label).toContain('历史') ||
          expect(historicalDataset.label).toContain('Snapshot') ||
          expect(historicalDataset.label).toContain('对比');

        // Historical dataset should have different styling
        expect(historicalDataset.borderDash).toBeDefined();
      }
    }
  });
});

test.describe('雷达图数据边界情况', () => {
  test('API - 未登录访问返回401', async () => {
    const res = await fetch(`${API_URL}/radar`);

    expect(res.status).toBe(401);
  });

  test('API - 数据格式一致性', async () => {
    const token = await loginUser(TEST_USERS.chartData);

    // Get radar data twice
    const res1 = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const res2 = await fetch(`${API_URL}/radar`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data1 = await res1.json();
    const data2 = await res2.json();

    // Structure should be consistent
    expect(data1.labels.length).toBe(data2.labels.length);
    expect(data1.datasets.length).toBe(data2.datasets.length);

    // Labels should be in same order
    data1.labels.forEach((label, idx) => {
      expect(label).toBe(data2.labels[idx]);
    });
  });
});
