/**
 * 路由切换进度条组件
 */

export class ProgressBar {
  constructor(options = {}) {
    this.options = {
      color: '#2563eb',
      height: 3,
      showSpinner: true,
      minimum: 0.08,
      easing: 'ease',
      speed: 200,
      trickle: true,
      trickleSpeed: 200,
      ...options
    };
    
    this.progress = 0;
    this.visible = false;
    this.element = null;
    this.spinner = null;
    this.rafId = null;
  }

  /**
   * 创建进度条DOM
   */
  create() {
    if (this.element) return;

    // 进度条容器
    const container = document.createElement('div');
    container.id = 'nprogress';
    container.className = 'nprogress-custom';
    container.style.cssText = `
      pointer-events: none;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 1031;
      transition: opacity 0.3s ease;
    `;

    // 进度条
    const bar = document.createElement('div');
    bar.className = 'bar';
    bar.style.cssText = `
      background: ${this.options.color};
      height: ${this.options.height}px;
      width: 100%;
      position: absolute;
      left: 0;
      top: 0;
      transform: translate3d(-100%, 0, 0);
      transition: transform ${this.options.speed}ms ${this.options.easing};
      box-shadow: 0 0 10px ${this.options.color}, 0 0 5px ${this.options.color};
    `;

    // 右侧光效
    const peg = document.createElement('div');
    peg.className = 'peg';
    peg.style.cssText = `
      display: block;
      position: absolute;
      right: 0;
      width: 100px;
      height: 100%;
      box-shadow: 0 0 10px ${this.options.color}, 0 0 5px ${this.options.color};
      opacity: 1;
      transform: rotate(3deg) translate(0px, -4px);
    `;

    bar.appendChild(peg);
    container.appendChild(bar);

    // 转圈动画
    if (this.options.showSpinner) {
      const spinner = document.createElement('div');
      spinner.className = 'spinner';
      spinner.style.cssText = `
        display: block;
        position: fixed;
        top: 15px;
        right: 15px;
        z-index: 1031;
      `;

      const spinnerIcon = document.createElement('div');
      spinnerIcon.style.cssText = `
        width: 18px;
        height: 18px;
        border: 2px solid transparent;
        border-top-color: ${this.options.color};
        border-left-color: ${this.options.color};
        border-radius: 50%;
        animation: nprogress-spinner 400ms linear infinite;
      `;

      // 添加动画样式
      if (!document.getElementById('nprogress-styles')) {
        const style = document.createElement('style');
        style.id = 'nprogress-styles';
        style.textContent = `
          @keyframes nprogress-spinner {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `;
        document.head.appendChild(style);
      }

      spinner.appendChild(spinnerIcon);
      container.appendChild(spinner);
      this.spinner = spinner;
    }

    this.element = container;
    this.bar = bar;
    document.body.appendChild(container);
  }

  /**
   * 开始加载
   */
  start() {
    if (this.visible) return;
    
    this.create();
    this.progress = 0;
    this.visible = true;
    this.element.style.opacity = '1';
    
    // 初始进度
    this.set(this.options.minimum);
    
    // 开始 trickle
    if (this.options.trickle) {
      this.startTrickle();
    }

    return this;
  }

  /**
   * 设置进度
   */
  set(progress) {
    this.progress = Math.max(0, Math.min(1, progress));
    
    if (!this.element) this.create();
    
    const percentage = this.progress * 100;
    this.bar.style.transform = `translate3d(${percentage - 100}%, 0, 0)`;
    
    // 完成时隐藏
    if (this.progress === 1) {
      setTimeout(() => this.done(), this.options.speed);
    }
    
    return this;
  }

  /**
   * 增加进度
   */
  inc(amount = null) {
    let n = this.progress;
    
    if (!amount) {
      if (n >= 0 && n < 0.2) amount = 0.1;
      else if (n >= 0.2 && n < 0.5) amount = 0.04;
      else if (n >= 0.5 && n < 0.8) amount = 0.02;
      else if (n >= 0.8 && n < 0.99) amount = 0.005;
      else amount = 0;
    }
    
    n = Math.min(0.994, n + amount);
    return this.set(n);
  }

  /**
   * 完成加载
   */
  done(force = false) {
    if (!this.visible && !force) return;
    
    this.progress = 1;
    this.stopTrickle();
    
    if (this.element) {
      this.bar.style.transform = 'translate3d(0%, 0, 0)';
      
      setTimeout(() => {
        if (this.element) {
          this.element.style.opacity = '0';
          setTimeout(() => {
            this.destroy();
          }, 300);
        }
      }, this.options.speed);
    }
    
    this.visible = false;
    return this;
  }

  /**
   * 开始自动递增
   */
  startTrickle() {
    const trickle = () => {
      if (!this.visible) return;
      this.inc();
      this.trickleTimeout = setTimeout(trickle, this.options.trickleSpeed);
    };
    this.trickleTimeout = setTimeout(trickle, this.options.trickleSpeed);
  }

  /**
   * 停止自动递增
   */
  stopTrickle() {
    if (this.trickleTimeout) {
      clearTimeout(this.trickleTimeout);
      this.trickleTimeout = null;
    }
  }

  /**
   * 销毁组件
   */
  destroy() {
    this.stopTrickle();
    if (this.element && this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
    this.element = null;
    this.bar = null;
    this.spinner = null;
  }

  /**
   * 与路由器集成
   */
  static integrate(router) {
    const progressBar = new ProgressBar();
    
    // 路由切换前开始
    router.onBeforeNavigate = () => {
      progressBar.start();
    };
    
    // 路由切换后完成
    router.onNavigateComplete = () => {
      progressBar.done();
    };
    
    // 路由切换错误
    router.onNavigateError = () => {
      progressBar.done(true);
    };
    
    return progressBar;
  }
}

// 创建全局实例
export const progressBar = new ProgressBar();

export default ProgressBar;
