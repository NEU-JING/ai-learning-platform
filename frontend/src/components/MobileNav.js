/**
 * 移动端导航组件
 */

export class MobileNav {
  constructor() {
    this.isOpen = false;
    this.element = null;
  }

  /**
   * 渲染移动端导航
   */
  render() {
    const nav = document.createElement('div');
    nav.className = 'mobile-nav';
    nav.innerHTML = `
      <button class="mobile-menu-toggle" id="mobile-menu-toggle">
        <span class="hamburger"></span>
      </button>
      
      <div class="mobile-menu-overlay" id="mobile-menu-overlay"></div>
      
      <nav class="mobile-menu" id="mobile-menu">
        <div class="mobile-menu-header">
          <span class="mobile-menu-title">AI学习平台</span>
          <button class="mobile-menu-close" id="mobile-menu-close">&times;</button>
        </div>
        
        <ul class="mobile-menu-list">
          <li><a href="#" data-nav="/">🏠 首页</a></li>
          <li><a href="#" data-nav="/courses">📚 全部课程</a></li>
          <li><a href="#" data-nav="/progress">📊 学习进度</a></li>
          <li><a href="#" data-nav="/profile/settings">🌐 我的公开主页</a></li>
        </ul>
        
        <div class="mobile-menu-footer">
          ${window.$store?.state?.user ? `
            <div class="mobile-user-info">
              <span>${window.$store.state.user.email}</span>
              <button class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout')">退出</button>
            </div>
          ` : `
            <a href="#" class="btn btn-primary" data-nav="/login">登录</a>
            <a href="#" class="btn btn-secondary" data-nav="/register">注册</a>
          `}
        </div>
      </nav>
    `;

    this.element = nav;
    this.bindEvents();
    
    return nav;
  }

  /**
   * 绑定事件
   */
  bindEvents() {
    const toggle = this.element.querySelector('#mobile-menu-toggle');
    const close = this.element.querySelector('#mobile-menu-close');
    const overlay = this.element.querySelector('#mobile-menu-overlay');
    const menu = this.element.querySelector('#mobile-menu');

    toggle?.addEventListener('click', () => this.open());
    close?.addEventListener('click', () => this.close());
    overlay?.addEventListener('click', () => this.close());

    // 导航链接点击后关闭菜单
    menu?.querySelectorAll('a[data-nav]').forEach(link => {
      link.addEventListener('click', () => {
        this.close();
      });
    });

    // ESC键关闭
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });
  }

  /**
   * 打开菜单
   */
  open() {
    this.isOpen = true;
    document.body.classList.add('mobile-menu-open');
    this.element.querySelector('#mobile-menu')?.classList.add('open');
    this.element.querySelector('#mobile-menu-overlay')?.classList.add('visible');
    
    // 禁止背景滚动
    document.body.style.overflow = 'hidden';
  }

  /**
   * 关闭菜单
   */
  close() {
    this.isOpen = false;
    document.body.classList.remove('mobile-menu-open');
    this.element.querySelector('#mobile-menu')?.classList.remove('open');
    this.element.querySelector('#mobile-menu-overlay')?.classList.remove('visible');
    
    // 恢复滚动
    document.body.style.overflow = '';
  }

  /**
   * 切换菜单
   */
  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }
}

/**
 * 底部导航栏（移动端）
 */
export class BottomNav {
  constructor() {
    this.element = null;
  }

  render() {
    const nav = document.createElement('nav');
    nav.className = 'bottom-nav';
    nav.innerHTML = `
      <a href="#" class="bottom-nav-item ${this.isActive('/')}" data-nav="/">
        <span class="bottom-nav-icon">🏠</span>
        <span class="bottom-nav-label">首页</span>
      </a>
      <a href="#" class="bottom-nav-item ${this.isActive('/courses')}" data-nav="/courses">
        <span class="bottom-nav-icon">📚</span>
        <span class="bottom-nav-label">课程</span>
      </a>
      <a href="#" class="bottom-nav-item ${this.isActive('/progress')}" data-nav="/progress">
        <span class="bottom-nav-icon">📊</span>
        <span class="bottom-nav-label">进度</span>
      </a>
      <a href="#" class="bottom-nav-item ${this.isActive('/profile')}" data-nav="/profile/settings">
        <span class="bottom-nav-icon">👤</span>
        <span class="bottom-nav-label">我的</span>
      </a>
    `;

    this.element = nav;
    return nav;
  }

  isActive(path) {
    const currentPath = window.location.hash.replace('#', '') || '/';
    return currentPath === path || currentPath.startsWith(path + '/') ? 'active' : '';
  }
}

export default MobileNav;
