// @ts-check
const { defineConfig } = require('@playwright/test');

const EXISTING_CHROMIUM = '/root/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome';

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: 1,
  // 使用已存在的 Chromium v1217（网络差，下载新版本会超时）
  use: {
    launchOptions: {
      executablePath: EXISTING_CHROMIUM,
      headless: true,
      args: ['--no-sandbox'],
    },
  },
});
