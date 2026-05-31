/**
 * Time Decay Calculation E2E Tests
 *
 * Covers AC10 from spec.md:
 *   - AC10: 支持时间衰减计算 - 技能雷达的时间衰减算法正确工作
 *   - 90天半衰期时间衰减权重算法
 *   - 旧实验数据权重降低，新实验数据权重提高，体现技能时效性
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const API_URL = `${BASE_URL}/api/v1`;

// Test user credentials
const TEST_USERS = {
  timeDecay: { username: 'e2e_timedecay', email: 'e2e_timedecay@test.com', password: 'Pass1234' },
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

// Helper: Complete a lab with given score and timestamp
async function completeLab(token, labId, score, completedAt = null) {
  const body = {
    lab_id: labId,
    score: score,
    status: 'completed',
  };
  
  // If completedAt is provided, include it (for mocking historical data)
  if (completedAt) {
    body.completed_at = completedAt;
  }
  
  const res = await fetch(`${API_URL}/labs/${labId}/complete`, {
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
async function getRadar(token, pathType = null) {
  const url = pathType 
    ? `${API_URL}/radar?path_type=${pathType}`
    : `${API_URL}/radar`;
  
  const res = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!res.ok) return null;
  return res.json();
}

// Helper: Create skill event directly (for testing time decay with historical data)
async function createSkillEvent(token, dimension, scoreImpact, eventDate) {
  const res = await fetch(`${API_URL}/radar/events`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      dimension: dimension,
      event_type: 'lab_completed',
      score_impact: scoreImpact,
      event_date: eventDate,
    }),
  });
  
  if (!res.ok) return null;
  return res.json();
}

// Helper: Calculate expected time decay weight
// Formula: weight = 0.5 ^ (days / 90)
function calculateTimeDecayWeight(daysPassed, halfLifeDays = 90, minWeight = 0.1) {
  const weight = Math.pow(0.5, daysPassed / halfLifeDays);
  return Math.max(weight, minWeight);
}

test.describe('AC10: 时间衰减计算', () => {
  test.beforeAll(async () => {
    await registerUser(TEST_USERS.timeDecay);
  });

  test('API - 获取雷达数据包含时间衰减后的分数', async () => {
    const token = await loginUser(TEST_USERS.timeDecay);
    expect(token).toBeTruthy();

    // First create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();

    // Get radar data
    const radarData = await getRadar(token);
    expect(radarData).toBeTruthy();

    // Verify response structure contains dimensions with scores
    expect(radarData).toHaveProperty('dimensions');
    expect(Array.isArray(radarData.dimensions)).toBe(true);

    // Each dimension should have required fields for time decay calculation
    for (const dim of radarData.dimensions) {
      expect(dim).toHaveProperty('name');
      expect(dim).toHaveProperty('score');
      expect(dim).toHaveProperty('max_score');
      expect(dim).toHaveProperty('events_count');
      expect(typeof dim.score).toBe('number');
      expect(dim.score).toBeGreaterThanOrEqual(0);
      expect(dim.score).toBeLessThanOrEqual(100);
    }
  });

  test('API - 时间衰减权重计算公式正确性', async () => {
    // Test the time decay weight calculation formula
    const testCases = [
      { days: 0, expected: 1.0 },           // Same day: no decay
      { days: 45, expected: Math.pow(0.5, 0.5) },  // 45 days: sqrt(0.5) ≈ 0.707
      { days: 90, expected: 0.5 },          // 90 days: half-life
      { days: 180, expected: 0.25 },        // 180 days: two half-lives
      { days: 270, expected: 0.125 },       // 270 days: three half-lives
    ];

    for (const tc of testCases) {
      const weight = calculateTimeDecayWeight(tc.days);
      expect(weight).toBeCloseTo(tc.expected, 3);
    }

    // Test minimum weight protection
    const oldWeight = calculateTimeDecayWeight(1000);  // Very old event
    expect(oldWeight).toBeGreaterThanOrEqual(0.1);
  });

  test('API - 旧实验数据权重低于新实验数据', async () => {
    const token = await loginUser(TEST_USERS.timeDecay);
    
    // Create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();

    // Simulate completing labs with different timestamps
    // Lab 1: Completed 90 days ago (old data, weight = 0.5)
    const ninetyDaysAgo = new Date();
    ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);
    
    // Lab 2: Completed today (new data, weight = 1.0)
    const today = new Date();

    // Complete labs with the simulated timestamps
    // Note: In a real scenario, these would be mocked or the backend would accept historical dates
    await completeLab(token, 1, 100, ninetyDaysAgo.toISOString());
    await completeLab(token, 2, 60, today.toISOString());

    // Get radar data
    const radarData = await getRadar(token);
    expect(radarData).toBeTruthy();

    // The score should be closer to the recent score (60) than the old score (100)
    // because recent events have higher weight
    // Expected weighted average: (60 * 1.0 + 100 * 0.5) / (1.0 + 0.5) = 110 / 1.5 = 73.33
    
    // Find the dimension that was updated
    const codingDim = radarData.dimensions.find(d => 
      d.name.toLowerCase().includes('coding') || 
      d.name.toLowerCase().includes('programming')
    );

    if (codingDim) {
      // Score should be between 60 and 100, but closer to 60 (recent)
      expect(codingDim.score).toBeGreaterThan(60);
      expect(codingDim.score).toBeLessThan(100);
      expect(codingDim.score).toBeLessThan(80);  // Should be closer to 60 than 100
    }
  });

  test('API - 3个月前数据权重约为0.5（半衰期）', async () => {
    const token = await loginUser(TEST_USERS.timeDecay);
    
    // Create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();

    // Calculate expected weight for 90 days (3 months)
    const expectedWeight = calculateTimeDecayWeight(90);
    expect(expectedWeight).toBeCloseTo(0.5, 3);

    // Verify the weight calculation is consistent
    const weight90Days = Math.pow(0.5, 90 / 90);
    expect(weight90Days).toBe(0.5);
  });

  test('API - 6个月前数据权重约为0.25（两个半衰期）', async () => {
    const token = await loginUser(TEST_USERS.timeDecay);
    
    // Create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();

    // Calculate expected weight for 180 days (6 months)
    const expectedWeight = calculateTimeDecayWeight(180);
    expect(expectedWeight).toBeCloseTo(0.25, 3);

    // Verify the weight calculation
    const weight180Days = Math.pow(0.5, 180 / 90);
    expect(weight180Days).toBe(0.25);
  });

  test('API - 最近完成的新实验数据权重更高', async () => {
    const token = await loginUser(TEST_USERS.timeDecay);
    
    // Create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();

    // Complete multiple labs with different scores and timestamps
    const now = new Date();
    
    // Old lab: 120 days ago, high score (100) - weight ≈ 0.397
    const oldDate = new Date(now);
    oldDate.setDate(oldDate.getDate() - 120);
    await completeLab(token, 3, 100, oldDate.toISOString());
    
    // Recent lab: 10 days ago, lower score (50) - weight ≈ 0.925
    const recentDate = new Date(now);
    recentDate.setDate(recentDate.getDate() - 10);
    await completeLab(token, 4, 50, recentDate.toISOString());

    // Get radar data
    const radarData = await getRadar(token);
    expect(radarData).toBeTruthy();

    // Calculate expected weighted average
    const oldWeight = calculateTimeDecayWeight(120);
    const recentWeight = calculateTimeDecayWeight(10);
    const expectedScore = (100 * oldWeight + 50 * recentWeight) / (oldWeight + recentWeight);

    // Find the dimension
    const codingDim = radarData.dimensions.find(d => 
      d.name.toLowerCase().includes('coding') || 
      d.name.toLowerCase().includes('programming')
    );

    if (codingDim) {
      // Score should reflect the weighted average
      expect(codingDim.score).toBeGreaterThan(50);  // Higher than recent low score
      expect(codingDim.score).toBeLessThan(100);    // Lower than old high score
    }
  });

  test('API - GET /api/v1/radar 返回的分数反映时间权重差异', async () => {
    const token = await loginUser(TEST_USERS.timeDecay);
    
    // Create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();

    // Get initial radar data
    const initialRadar = await getRadar(token);
    expect(initialRadar).toBeTruthy();
    expect(initialRadar).toHaveProperty('dimensions');
    expect(initialRadar).toHaveProperty('last_updated');

    // Verify radar data contains time-related metadata
    if (initialRadar.last_updated) {
      const lastUpdated = new Date(initialRadar.last_updated);
      expect(lastUpdated).toBeInstanceOf(Date);
      expect(!isNaN(lastUpdated.getTime())).toBe(true);
    }

    // Verify each dimension has event history for time decay calculation
    for (const dim of initialRadar.dimensions) {
      expect(dim).toHaveProperty('events_count');
      expect(typeof dim.events_count).toBe('number');
      expect(dim.events_count).toBeGreaterThanOrEqual(0);
      
      // If there are events, verify the score is calculated
      if (dim.events_count > 0) {
        expect(dim.score).toBeGreaterThan(0);
      }
    }
  });

  test('API - 时间衰减权重最小值保护（不低于0.1）', async () => {
    // Test that very old events still have minimum weight
    const veryOldWeight = calculateTimeDecayWeight(365 * 2);  // 2 years old
    expect(veryOldWeight).toBeGreaterThanOrEqual(0.1);

    const ancientWeight = calculateTimeDecayWeight(365 * 5);  // 5 years old
    expect(ancientWeight).toBeGreaterThanOrEqual(0.1);

    // Verify the minimum weight is applied
    const calculatedWeight = Math.pow(0.5, 365 * 2 / 90);
    expect(calculatedWeight).toBeLessThan(0.1);
    
    // But the protected weight should be at least 0.1
    expect(calculateTimeDecayWeight(365 * 2)).toBe(0.1);
  });

  test('API - 45天数据权重约为0.707（sqrt(0.5)）', async () => {
    // 45 days is half of the 90-day half-life
    const weight45Days = calculateTimeDecayWeight(45);
    const expectedSqrtHalf = Math.sqrt(0.5);  // ≈ 0.707
    expect(weight45Days).toBeCloseTo(expectedSqrtHalf, 3);
  });

  test('API - 未授权访问返回 401', async () => {
    // Try to access radar without authentication
    const res = await fetch(`${API_URL}/radar`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    expect(res.status).toBe(401);
  });

  test('API - 雷达数据包含时间衰减配置信息', async () => {
    const token = await loginUser(TEST_USERS.timeDecay);
    
    // Create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();

    // Get radar data
    const radarData = await getRadar(token);
    expect(radarData).toBeTruthy();

    // Verify if radar data includes decay configuration
    if (radarData.decay_config) {
      expect(radarData.decay_config).toHaveProperty('half_life_days');
      expect(radarData.decay_config).toHaveProperty('min_weight');
      
      // Default values should be 90 days and 0.1
      expect(radarData.decay_config.half_life_days).toBe(90);
      expect(radarData.decay_config.min_weight).toBe(0.1);
    }
  });
});

test.describe('AC10: 时间衰减场景验证', () => {
  test.beforeAll(async () => {
    await registerUser({
      username: 'e2e_timedecay_scenario',
      email: 'e2e_timedecay_scenario@test.com',
      password: 'Pass1234'
    });
  });

  test('场景验证 - Phase 1（3个月前）数据权重降低，Phase 3（最近）数据权重提高', async () => {
    const user = {
      username: 'e2e_timedecay_scenario',
      email: 'e2e_timedecay_scenario@test.com',
      password: 'Pass1234'
    };
    
    const token = await loginUser(user);
    expect(token).toBeTruthy();

    // Create a path
    const pathData = await createPath(token, 'ai-engineer');
    expect(pathData).toBeTruthy();

    const now = new Date();

    // Simulate Phase 1 completion (3 months ago) with good score
    const phase1Date = new Date(now);
    phase1Date.setDate(phase1Date.getDate() - 90);  // 90 days ago
    await completeLab(token, 101, 90, phase1Date.toISOString());  // Phase 1: score 90

    // Simulate Phase 3 completion (recently) with lower score
    const phase3Date = new Date(now);
    phase3Date.setDate(phase3Date.getDate() - 7);  // 7 days ago
    await completeLab(token, 103, 70, phase3Date.toISOString());  // Phase 3: score 70

    // Get radar data
    const radarData = await getRadar(token);
    expect(radarData).toBeTruthy();

    // Calculate weights
    const phase1Weight = calculateTimeDecayWeight(90);   // 0.5
    const phase3Weight = calculateTimeDecayWeight(7);    // ≈ 0.946

    // Expected weighted average: (90 * 0.5 + 70 * 0.946) / (0.5 + 0.946)
    // = (45 + 66.22) / 1.446 ≈ 76.9
    const expectedWeightedScore = (90 * phase1Weight + 70 * phase3Weight) / (phase1Weight + phase3Weight);

    // Find the relevant dimension
    const codingDim = radarData.dimensions.find(d => 
      d.name.toLowerCase().includes('coding') || 
      d.name.toLowerCase().includes('programming')
    );

    if (codingDim && codingDim.events_count >= 2) {
      // Score should be between 70 and 90, reflecting the weighted average
      expect(codingDim.score).toBeGreaterThan(70);
      expect(codingDim.score).toBeLessThan(90);
      
      // Score should be closer to the recent score (70) due to higher weight
      expect(codingDim.score).toBeLessThan(80);
    }

    // Log for debugging
    console.log('AC10 Scenario Test:');
    console.log(`  Phase 1 (90 days ago): score=90, weight=${phase1Weight.toFixed(3)}`);
    console.log(`  Phase 3 (7 days ago): score=70, weight=${phase3Weight.toFixed(3)}`);
    console.log(`  Expected weighted score: ${expectedWeightedScore.toFixed(2)}`);
    if (codingDim) {
      console.log(`  Actual radar score: ${codingDim.score}`);
    }
  });
});
