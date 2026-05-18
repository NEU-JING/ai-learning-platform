/**
 * 前端冒烟测试 (E2E Smoke Tests)
 *
 * 修改 frontend/ 下任何 JS/CSS/HTML 文件后必须执行：
 *   cd /root/workspace/ai-learning-platform && npx playwright test tests/e2e/smoke.spec.js
 *
 * 检查项：
 *   1. 核心页面正常加载（/、/#/courses、/#/login、/#/register）
 *   2. 浏览器控制台无 console.error 或 JS 运行时异常
 *   3. 页面 title 符合预期
 *
 * 已知过滤的噪声：
 *   - favicon.ico 404（浏览器自动请求，标准行为）
 */
const { test, expect, chromium } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

/** favicon.ico 404 是标准浏览器行为，不计为错误 */
function isRealError(msg) {
  return !msg.location()?.url?.includes('favicon.ico');
}

/**
 * 收集指定 page 的所有控制台错误和 JS 运行时异常
 */
function captureErrors(page) {
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error' && isRealError(msg)) {
      errors.push(msg.text());
    }
  });
  page.on('pageerror', err => {
    errors.push(`Uncaught: ${err.message}`);
  });
  return errors;
}

/**
 * 通用页面检测：加载页面 → 检查内容 → 检查控制台 → 检查title
 */
async function checkPage(page, path, titleSubstring) {
  const errors = captureErrors(page);
  const url = `${BASE_URL}${path}`;

  await page.goto(url, { waitUntil: 'load', timeout: 20000 });
  // 给 SPA 模块加载 + 渲染留时间
  await page.waitForTimeout(1500);

  // 有实际内容（非空白页）
  const bodyText = await page.evaluate(() => document.body?.innerText || '');
  expect(bodyText.length).toBeGreaterThan(0);

  // 控制台无真实错误
  expect(errors).toEqual([]);

  // title 符合预期
  const title = await page.title();
  expect(title).toContain(titleSubstring);
}

test.describe('前端冒烟测试', () => {

  let firstCourseId;

  test.beforeAll(async () => {
    // 动态获取第一个可用课程 ID（避免硬编码 1 导致 404）
    const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'], executablePath: '/root/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome' });
    const page = await browser.newPage();
    const errors = [];
    page.on('response', resp => {
      if (resp.url().includes('/api/v1/courses/') && !resp.url().includes('/chapters')) {
        errors.push(resp.url());
      }
    });
    await page.goto(`${BASE_URL}/#/courses`, { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(1500);

    // 从课程列表页的 DOM 中提取第一个课程链接
    const links = await page.evaluate(() => {
      // 尝试多种 selector 找到课程卡片中的链接
      const anchors = document.querySelectorAll('a[href*="/courses/"]');
      return Array.from(anchors).map(a => a.getAttribute('href')).filter(Boolean);
    });
    if (links.length > 0) {
      const match = links[0].match(/\/courses\/(\d+)/);
      if (match) firstCourseId = match[1];
    }
    if (!firstCourseId) {
      // fallback: 从 API 返回值获取
      try {
        const resp = await page.evaluate(() => fetch('/api/v1/courses/').then(r => r.json()));
        const items = resp.items || resp;
        if (items.length > 0) firstCourseId = String(items[0].id);
      } catch (e) {
        console.warn('Failed to fetch course list:', e.message);
      }
    }
    if (!firstCourseId) firstCourseId = '5'; // last resort fallback
    await browser.close();
  });

  test('首页可加载且无控制台错误', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    await checkPage(page, '/', 'AI学习平台');
    await context.close();
  });

  test('课程列表页可加载且无控制台错误', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    await checkPage(page, '/#/courses', '全部课程');
    await context.close();
  });

  test('课程详情页可加载且无控制台错误', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    await checkPage(page, `/#/courses/${firstCourseId}`, '课程详情');
    await context.close();
  });

  test('登录页可加载且无控制台错误', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    await checkPage(page, '/#/login', '登录');
    await context.close();
  });

  test('注册页可加载且无控制台错误', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    await checkPage(page, '/#/register', '注册');
    await context.close();
  });

  test('学习进度页（未登录）应重定向到登录页', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    const errors = captureErrors(page);

    await page.goto(`${BASE_URL}/#/progress`, { waitUntil: 'load', timeout: 20000 });
    await page.waitForTimeout(1500);

    // 未登录应重定向到 login 路由
    const url = page.url();
    expect(url).toContain('login');

    // 无真实控制台错误
    expect(errors).toEqual([]);

    await context.close();
  });
});
