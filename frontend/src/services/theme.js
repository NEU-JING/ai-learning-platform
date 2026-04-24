/**
 * 主题管理器 - 支持暗黑/明亮主题切换
 */

const THEME_KEY = 'ai-learning-theme';

class ThemeManager {
  constructor() {
    this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
    this.listeners = [];
    this.init();
  }

  init() {
    // 初始化主题
    this.applyTheme(this.currentTheme);
    
    // 监听系统主题变化
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', (e) => {
        if (!this.getStoredTheme()) {
          // 如果没有手动设置过主题，跟随系统
          this.applyTheme(e.matches ? 'dark' : 'light');
        }
      });
    }
  }

  /**
   * 获取存储的主题
   */
  getStoredTheme() {
    try {
      return localStorage.getItem(THEME_KEY);
    } catch (e) {
      return null;
    }
  }

  /**
   * 获取系统主题
   */
  getSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  /**
   * 获取当前主题
   */
  getCurrentTheme() {
    return this.currentTheme;
  }

  /**
   * 切换主题
   */
  toggleTheme() {
    const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    this.setTheme(newTheme);
    return newTheme;
  }

  /**
   * 设置主题
   */
  setTheme(theme) {
    if (theme !== 'dark' && theme !== 'light' && theme !== 'auto') {
      console.warn('Invalid theme:', theme);
      return;
    }

    this.currentTheme = theme;
    
    // 存储主题偏好
    if (theme === 'auto') {
      localStorage.removeItem(THEME_KEY);
    } else {
      localStorage.setItem(THEME_KEY, theme);
    }

    // 应用主题
    this.applyTheme(theme === 'auto' ? this.getSystemTheme() : theme);
    
    // 通知监听器
    this.notifyListeners(theme);
  }

  /**
   * 应用主题到DOM
   */
  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    
    // 更新Monaco Editor主题
    if (window.monaco && window.monaco.editor) {
      const editorTheme = theme === 'dark' ? 'vs-dark' : 'vs';
      window.monaco.editor.setTheme(editorTheme);
    }
  }

  /**
   * 添加主题变化监听器
   */
  onThemeChange(callback) {
    this.listeners.push(callback);
  }

  /**
   * 移除主题变化监听器
   */
  offThemeChange(callback) {
    this.listeners = this.listeners.filter(cb => cb !== callback);
  }

  /**
   * 通知所有监听器
   */
  notifyListeners(theme) {
    this.listeners.forEach(callback => {
      try {
        callback(theme);
      } catch (e) {
        console.error('Theme change listener error:', e);
      }
    });
  }

  /**
   * 创建主题切换按钮
   */
  createToggleButton() {
    const button = document.createElement('button');
    button.className = 'theme-toggle-btn';
    button.innerHTML = this.getThemeIcon();
    button.title = '切换主题';
    
    button.addEventListener('click', () => {
      const newTheme = this.toggleTheme();
      button.innerHTML = this.getThemeIcon();
    });

    // 监听主题变化更新图标
    this.onThemeChange(() => {
      button.innerHTML = this.getThemeIcon();
    });

    return button;
  }

  /**
   * 获取主题图标
   */
  getThemeIcon() {
    return this.currentTheme === 'dark' ? '🌙' : '☀️';
  }
}

// 导出单例
export const themeManager = new ThemeManager();

// 默认导出
export default themeManager;
