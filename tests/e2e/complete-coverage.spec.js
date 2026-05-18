/**
 * Complete E2E Coverage - All Pages
 * 覆盖所有前端页面的端到端测试
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

/**
 * 收集页面错误
 */
function captureErrors(page) {
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      const text = msg.text();
      // 过滤非关键错误
      if (!text.includes('favicon') && 
          !text.includes('Source map') &&
          !text.includes('[HMR]')) {
        errors.push(text);
      }
    }
  });
  page.on('pageerror', err => {
    errors.push(`PageError: ${err.message}`);
  });
  return errors;
}

/**
 * 通用页面检查
 */
async function checkPageLoad(page, path, options = {}) {
  const errors = captureErrors(page);
  const url = `${BASE_URL}${path}`;
  
  await page.goto(url, { 
    waitUntil: 'networkidle',
    timeout: options.timeout || 30000 
  });
  
  // 等待渲染
  await page.waitForTimeout(options.waitTime || 2000);
  
  // 检查页面有内容
  const bodyText = await page.evaluate(() => document.body?.innerText?.trim() || '');
  expect(bodyText.length).toBeGreaterThan(10);
  
  // 检查无错误
  if (!options.allowErrors) {
    expect(errors).toEqual([]);
  }
  
  return { errors, bodyText };
}

// ============================================
// V1 前端测试
// ============================================
test.describe('V1 Frontend - All Pages', () => {
  
  test('首页 /', async ({ page }) => {
    await checkPageLoad(page, '/', { 
      expectTitle: 'AI学习平台' 
    });
  });

  test('课程列表 /#/courses', async ({ page }) => {
    await checkPageLoad(page, '/#/courses', { 
      expectTitle: '全部课程' 
    });
    
    // 验证课程列表加载
    const hasCourses = await page.evaluate(() => {
      const cards = document.querySelectorAll('.course-card, [class*="course"], .card');
      return cards.length > 0;
    });
    expect(hasCourses).toBe(true);
  });

  test('课程详情 /#/courses/:id', async ({ page }) => {
    // 先获取第一个课程ID
    await page.goto(`${BASE_URL}/#/courses`);
    await page.waitForTimeout(1500);
    
    const firstCourseLink = await page.locator('a[href*="/courses/"]').first();
    if (await firstCourseLink.isVisible()) {
      await firstCourseLink.click();
      await page.waitForTimeout(2000);
      
      // 检查课程详情页加载
      const url = page.url();
      expect(url).toMatch(/\/courses\/\d+/);
      
      const hasContent = await page.evaluate(() => {
        return document.body.innerText.length > 100;
      });
      expect(hasContent).toBe(true);
    }
  });

  test('章节详情 /#/chapters/:id', async ({ page }) => {
    // 从API获取第一个章节
    const chaptersResp = await page.evaluate(() => 
      fetch('/api/v1/courses/5/chapters').then(r => r.json())
    );
    
    if (chaptersResp && chaptersResp.length > 0) {
      const chapterId = chaptersResp[0].id;
      await checkPageLoad(page, `/#/chapters/${chapterId}`, {
        timeout: 30000,
        waitTime: 3000
      });
      
      // 验证章节内容
      const hasChapterContent = await page.evaluate(() => {
        return document.querySelector('.chapter-content, [class*="chapter"], article') !== null ||
               document.body.innerText.includes('第') && document.body.innerText.includes('章');
      });
      expect(hasChapterContent).toBe(true);
    }
  });

  test('实验页面 /#/labs/:id', async ({ page }) => {
    // 从API获取第一个实验
    const labsResp = await page.evaluate(() => 
      fetch('/api/v1/labs/').then(r => r.json())
    );
    
    const labs = labsResp.items || labsResp;
    if (labs && labs.length > 0) {
      const labId = labs[0].id;
      await checkPageLoad(page, `/#/labs/${labId}`, {
        timeout: 30000,
        waitTime: 3000
      });
      
      // 验证实验页面元素
      const hasLabElements = await page.evaluate(() => {
        return document.querySelector('textarea, [class*="editor"], [class*="lab"]') !== null ||
               document.body.innerText.includes('实验') ||
               document.body.innerText.includes('代码');
      });
      expect(hasLabElements).toBe(true);
    }
  });

  test('登录页 /#/login', async ({ page }) => {
    const { errors } = await checkPageLoad(page, '/#/login');
    
    // 验证登录表单
    const hasForm = await page.locator('input[type="email"], input[name="email"], input[type="password"]').count() > 0;
    expect(hasForm).toBe(true);
  });

  test('注册页 /#/register', async ({ page }) => {
    await checkPageLoad(page, '/#/register');
    
    // 验证注册表单
    const hasForm = await page.locator('input[type="email"], input[name="username"], input[type="password"]').count() > 0;
    expect(hasForm).toBe(true);
  });

  test('进度页 /#/progress (未登录跳转)', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/progress`);
    await page.waitForTimeout(2000);
    
    const url = page.url();
    // 未登录应重定向到登录页
    expect(url).toContain('login');
  });

  test('证书页 /#/certificates', async ({ page }) => {
    await checkPageLoad(page, '/#/certificates', { 
      allowErrors: true // 可能未登录
    });
  });

  test('个人资料 /#/profile', async ({ page }) => {
    await checkPageLoad(page, '/#/profile', { 
      allowErrors: true 
    });
  });

  test('API 文档页 /docs', async ({ page }) => {
    const resp = await page.goto(`${BASE_URL}/docs`);
    expect(resp.status()).toBe(200);
    
    const title = await page.title();
    expect(title).toContain('AI');
  });
});

// ============================================
// V2 前端测试
// ============================================
test.describe('V2 Frontend - All Pages', () => {
  
  test('V2 首页 /v2', async ({ page }) => {
    const errors = captureErrors(page);
    
    await page.goto(`${BASE_URL}/v2`);
    await page.waitForSelector('#root', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // 验证 React 渲染
    const hasReact = await page.evaluate(() => {
      return !!document.querySelector('#root > div') ||
             !!document.querySelector('[data-reactroot]');
    });
    expect(hasReact).toBe(true);
    
    // 检查关键错误
    const criticalErrors = errors.filter(e => 
      !e.includes('favicon') && !e.includes('Source map')
    );
    expect(criticalErrors).toEqual([]);
  });

  test('V2 课程列表 /v2#/courses', async ({ page }) => {
    const errors = captureErrors(page);
    
    await page.goto(`${BASE_URL}/v2#/courses`);
    await page.waitForTimeout(3000);
    
    // 验证页面内容
    const hasContent = await page.evaluate(() => {
      return document.body.innerText.length > 50;
    });
    expect(hasContent).toBe(true);
    
    expect(errors.filter(e => !e.includes('favicon'))).toEqual([]);
  });

  test('V2 课程详情 /v2#/courses/:id', async ({ page }) => {
    const errors = captureErrors(page);
    
    await page.goto(`${BASE_URL}/v2#/courses/5`);
    await page.waitForTimeout(3000);
    
    const url = page.url();
    expect(url).toContain('/v2');
    
    expect(errors.filter(e => !e.includes('favicon'))).toEqual([]);
  });

  test('V2 章节详情 /v2#/chapters/:id', async ({ page }) => {
    // 获取章节ID
    const resp = await page.evaluate(() => 
      fetch('/api/v1/courses/5/chapters').then(r => r.json())
    );
    
    if (resp && resp.length > 0) {
      const chapterId = resp[0].id;
      const errors = captureErrors(page);
      
      await page.goto(`${BASE_URL}/v2#/chapters/${chapterId}`);
      await page.waitForTimeout(3000);
      
      expect(errors.filter(e => !e.includes('favicon'))).toEqual([]);
    }
  });

  test('V2 实验页面 /v2#/labs/:id', async ({ page }) => {
    // 获取实验ID
    const resp = await page.evaluate(() => 
      fetch('/api/v1/labs/').then(r => r.json())
    );
    
    const labs = resp.items || resp;
    if (labs && labs.length > 0) {
      const labId = labs[0].id;
      const errors = captureErrors(page);
      
      await page.goto(`${BASE_URL}/v2#/labs/${labId}`);
      await page.waitForTimeout(3000);
      
      expect(errors.filter(e => !e.includes('favicon'))).toEqual([]);
    }
  });

  test('V2 学习进度 /v2#/progress', async ({ page }) => {
    const errors = captureErrors(page);
    
    await page.goto(`${BASE_URL}/v2#/progress`);
    await page.waitForTimeout(3000);
    
    expect(errors.filter(e => !e.includes('favicon'))).toEqual([]);
  });

  test('V2 静态资源', async ({ page }) => {
    // 测试 CSS
    const cssResp = await page.goto(`${BASE_URL}/v2/styles.css`);
    expect(cssResp.status()).toBe(200);
    expect(cssResp.headers()['content-type']).toContain('css');
    
    // 测试 JS
    const jsResp = await page.goto(`${BASE_URL}/v2/data.js`);
    expect(jsResp.status()).toBe(200);
    
    // 测试 api.js
    const apiResp = await page.goto(`${BASE_URL}/v2/api.js`);
    expect(apiResp.status()).toBe(200);
    
    // 测试 store.js
    const storeResp = await page.goto(`${BASE_URL}/v2/store.js`);
    expect(storeResp.status()).toBe(200);
  });
});

// ============================================
// API 集成测试
// ============================================
test.describe('API Integration', () => {
  
  test('Health check endpoint', async ({ page }) => {
    const resp = await page.goto(`${BASE_URL}/health`);
    expect(resp.status()).toBe(200);
    
    const data = await resp.json();
    expect(data.status).toBe('healthy');
    expect(data).toHaveProperty('version');
    expect(data).toHaveProperty('frontend_version');
  });

  test('Courses API returns data', async ({ page }) => {
    const resp = await page.evaluate(() => 
      fetch('/api/v1/courses/').then(r => r.json())
    );
    
    const courses = resp.items || resp;
    expect(courses.length).toBeGreaterThan(0);
    expect(courses[0]).toHaveProperty('id');
    expect(courses[0]).toHaveProperty('title');
  });

  test('Chapters API returns data', async ({ page }) => {
    const resp = await page.evaluate(() => 
      fetch('/api/v1/courses/5/chapters').then(r => r.json())
    );
    
    expect(Array.isArray(resp)).toBe(true);
    if (resp.length > 0) {
      expect(resp[0]).toHaveProperty('id');
      expect(resp[0]).toHaveProperty('title');
    }
  });

  test('Labs API returns data', async ({ page }) => {
    const resp = await page.evaluate(() => 
      fetch('/api/v1/labs/').then(r => r.json())
    );
    
    const labs = resp.items || resp;
    expect(Array.isArray(labs)).toBe(true);
  });
});

// ============================================
// 响应式测试
// ============================================
test.describe('Responsive Design', () => {
  
  test('V1 移动端适配', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/#/courses`);
    await page.waitForTimeout(2000);
    
    // 检查页面在移动端正常渲染
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    expect(bodyWidth).toBeLessThanOrEqual(375);
  });

  test('V2 移动端适配', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/v2`);
    await page.waitForTimeout(2000);
    
    const hasMobileClass = await page.evaluate(() => {
      return document.querySelector('[class*="mobile"], [class*="Mobile"]') !== null ||
             document.body.scrollWidth <= 375;
    });
    expect(hasMobileClass).toBe(true);
  });

  test('V1 平板适配', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(`${BASE_URL}/#/courses`);
    await page.waitForTimeout(2000);
    
    const bodyText = await page.evaluate(() => document.body.innerText);
    expect(bodyText.length).toBeGreaterThan(50);
  });

  test('V2 平板适配', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(`${BASE_URL}/v2`);
    await page.waitForTimeout(2000);
    
    const bodyText = await page.evaluate(() => document.body.innerText);
    expect(bodyText.length).toBeGreaterThan(50);
  });
});
