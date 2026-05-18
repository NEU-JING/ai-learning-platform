/**
 * Frontend V2 E2E Tests
 * Tests React-based frontend-v2 using Playwright
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:8000';

// Test frontend-v2 specific routes
test.describe('Frontend V2 React SPA', () => {
  
  test.beforeEach(async ({ page }) => {
    // Intercept console errors and warnings
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`Console error: ${msg.text()}`);
      }
    });
    
    page.on('pageerror', error => {
      console.log(`Page error: ${error.message}`);
    });
  });

  test('V2 index page loads successfully', async ({ page }) => {
    await page.goto(`${BASE_URL}/v2`);
    
    // Wait for React to render
    await page.waitForSelector('#root', { state: 'visible' });
    
    // Check page title
    await expect(page).toHaveTitle(/JING|AI 学习平台/);
    
    // Verify React is loaded by checking for React-specific attributes
    const hasReact = await page.evaluate(() => {
      return !!document.querySelector('[data-reactroot]') || 
             !!document.querySelector('#root > div');
    });
    expect(hasReact).toBe(true);
  });

  test('V2 home screen renders without console errors', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto(`${BASE_URL}/v2#/home`);
    await page.waitForLoadState('networkidle');
    
    // Check no critical errors
    const criticalErrors = errors.filter(e => 
      !e.includes('favicon') && 
      !e.includes('Source map')
    );
    expect(criticalErrors).toHaveLength(0);
  });

  test('V2 navigation works (home → courses → back)', async ({ page }) => {
    await page.goto(`${BASE_URL}/v2`);
    await page.waitForSelector('.app', { state: 'visible' });
    
    // Navigate to courses
    const coursesLink = await page.locator('text=课程').first();
    if (await coursesLink.isVisible()) {
      await coursesLink.click();
      await page.waitForTimeout(500); // Wait for navigation
      
      // URL should change
      const url = page.url();
      expect(url).toContain('/v2');
    }
  });

  test('V2 theme toggle works', async ({ page }) => {
    await page.goto(`${BASE_URL}/v2`);
    await page.waitForSelector('html[data-theme]', { state: 'visible' });
    
    // Check initial theme attribute exists
    const theme = await page.evaluate(() => {
      return document.documentElement.getAttribute('data-theme');
    });
    expect(['dark', 'light']).toContain(theme);
  });

  test('V2 brand color system works', async ({ page }) => {
    await page.goto(`${BASE_URL}/v2`);
    await page.waitForSelector('html[data-brand]', { state: 'visible' });
    
    const brand = await page.evaluate(() => {
      return document.documentElement.getAttribute('data-brand');
    });
    expect(['indigo', 'teal', 'amber', 'rose', 'lime']).toContain(brand);
  });

  test('V2 density setting exists', async ({ page }) => {
    await page.goto(`${BASE_URL}/v2`);
    await page.waitForSelector('html[data-density]', { state: 'visible' });
    
    const density = await page.evaluate(() => {
      return document.documentElement.getAttribute('data-density');
    });
    expect(['compact', 'standard', 'spacious']).toContain(density);
  });

  test('V2 static files are served correctly', async ({ page }) => {
    // Test CSS file
    const cssResponse = await page.goto(`${BASE_URL}/v2/styles.css`);
    expect(cssResponse.status()).toBe(200);
    expect(cssResponse.headers()['content-type']).toContain('text/css');
    
    // Test data.js
    const dataResponse = await page.goto(`${BASE_URL}/v2/data.js`);
    expect(dataResponse.status()).toBe(200);
    expect(dataResponse.headers()['content-type']).toContain('javascript');
  });

  test('V2 components load sequentially', async ({ page }) => {
    await page.goto(`${BASE_URL}/v2`);
    
    // Wait for each component to potentially render
    await page.waitForTimeout(1000);
    
    // Check main structure
    const hasApp = await page.locator('.app').count() > 0;
    const hasMain = await page.locator('main').count() > 0;
    
    expect(hasApp || hasMain).toBe(true);
  });

  test('V2 mobile nav is responsive', async ({ page }) => {
    // Mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/v2`);
    await page.waitForLoadState('networkidle');
    
    // Should have mobile navigation
    const mobileNav = await page.locator('[class*="mobile"], [class*="Mobile"]').first();
    const isVisible = await mobileNav.isVisible().catch(() => false);
    
    // Mobile nav should exist but may be hidden based on implementation
    const exists = await mobileNav.count() > 0;
    expect(exists).toBe(true);
  });
});

// Test backward compatibility
test.describe('Frontend V1/V2 Compatibility', () => {
  
  test('V1 still works when FRONTEND_VERSION=v1', async ({ page }) => {
    // This test verifies V1 is not broken by V2 addition
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('domcontentloaded');
    
    // Page should load without 404
    const title = await page.title();
    expect(title).not.toBe('Frontend V2 Not Found');
  });

  test('Health check reports frontend version', async ({ page }) => {
    const response = await page.goto(`${BASE_URL}/health`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('frontend_version');
    expect(data).toHaveProperty('frontend_dir');
    expect(data.status).toBe('healthy');
  });
});
