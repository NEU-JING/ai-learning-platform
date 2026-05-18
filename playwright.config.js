// @ts-check
const { defineConfig } = require('@playwright/test');

// CI 中无需设置：npx playwright install 会自动安装并发现浏览器
// 本地开发：通过环境变量 PLAYWRIGHT_CHROMIUM_PATH 指定，或留空自动发现
const CHROMIUM_PATH = process.env.PLAYWRIGHT_CHROMIUM_PATH;

// 本地回退：如果指定了路径或已有安装则使用，否则自动发现
const launchOptions = {
  headless: true,
  args: ['--no-sandbox'],
};
if (CHROMIUM_PATH) {
  launchOptions.executablePath = CHROMIUM_PATH;
}

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: 1,
  use: {
    launchOptions,
  },
});
