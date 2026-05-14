/**
 * 环境配置管理
 * 支持开发/生产环境自动切换
 */

// 检测当前环境
const detectEnvironment = () => {
  // 优先从 window.ENV 读取（可由外部配置注入）
  if (window.ENV && window.ENV.NODE_ENV) {
    return window.ENV.NODE_ENV;
  }
  
  // 根据hostname检测
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'development';
  }
  
  // 默认生产环境
  return 'production';
};

// 默认配置
const defaultConfig = {
  API_BASE_URL: 'http://localhost:8000/api/v1',
  API_TIMEOUT: 30000,
  ENABLE_DEBUG: false,
  ENABLE_MOCK: false,
  VERSION: '1.0.0'
};

// 开发环境配置
const developmentConfig = {
  ...defaultConfig,
  API_BASE_URL: window.ENV?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  ENABLE_DEBUG: true,
  ENABLE_MOCK: window.ENV?.VITE_ENABLE_MOCK === 'true' || false
};

// 生产环境配置
const productionConfig = {
  ...defaultConfig,
  API_BASE_URL: window.ENV?.VITE_API_BASE_URL || `${window.location.origin}/api/v1`,
  ENABLE_DEBUG: false,
  ENABLE_MOCK: false
};

// 测试环境配置
const testConfig = {
  ...defaultConfig,
  API_BASE_URL: 'http://localhost:8000/api/v1',
  ENABLE_DEBUG: true,
  ENABLE_MOCK: true
};

// 配置映射
const configs = {
  development: developmentConfig,
  production: productionConfig,
  test: testConfig
};

// 获取当前环境
const currentEnv = detectEnvironment();

// 导出配置
export const ENV = {
  ...configs[currentEnv] || defaultConfig,
  NODE_ENV: currentEnv,
  IS_DEV: currentEnv === 'development',
  IS_PROD: currentEnv === 'production',
  IS_TEST: currentEnv === 'test'
};

// 调试输出
if (ENV.IS_DEV) {
  console.log('[Config] 当前环境:', currentEnv, ENV);
}

export default ENV;
