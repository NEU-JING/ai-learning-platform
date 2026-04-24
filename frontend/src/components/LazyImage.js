/**
 * 图片懒加载组件
 */

export class LazyImage {
  constructor(options = {}) {
    this.options = {
      rootMargin: '50px 0px',
      threshold: 0.01,
      placeholder: null,
      errorImage: null,
      ...options
    };
    
    this.observer = null;
    this.imageCache = new Set();
    this.init();
  }

  /**
   * 初始化 IntersectionObserver
   */
  init() {
    if (!('IntersectionObserver' in window)) {
      // 浏览器不支持，直接加载所有图片
      this.fallbackLoad();
      return;
    }

    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.loadImage(entry.target);
          this.observer.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: this.options.rootMargin,
      threshold: this.options.threshold
    });
  }

  /**
   * 观察图片元素
   */
  observe(img) {
    if (!img || !this.observer) return;
    
    // 如果图片已经在缓存中，直接显示
    const src = img.dataset.src || img.src;
    if (this.imageCache.has(src)) {
      this.showImage(img, src);
      return;
    }
    
    // 添加占位符
    this.addPlaceholder(img);
    
    // 开始观察
    this.observer.observe(img);
  }

  /**
   * 观察所有懒加载图片
   */
  observeAll(selector = 'img[data-src]') {
    const images = document.querySelectorAll(selector);
    images.forEach(img => this.observe(img));
  }

  /**
   * 添加占位符
   */
  addPlaceholder(img) {
    // 保存原始尺寸
    const width = img.width || img.clientWidth;
    const height = img.height || img.clientHeight;
    
    if (width && height) {
      img.style.minHeight = `${height}px`;
    }
    
    // 添加加载样式
    img.classList.add('lazy-image', 'lazy-loading');
    img.style.backgroundColor = '#f3f4f6';
  }

  /**
   * 加载图片
   */
  loadImage(img) {
    const src = img.dataset.src;
    if (!src) return;

    // 创建预加载图片
    const preloadImg = new Image();
    
    preloadImg.onload = () => {
      this.imageCache.add(src);
      this.showImage(img, src);
    };
    
    preloadImg.onerror = () => {
      this.handleError(img);
    };
    
    preloadImg.src = src;
  }

  /**
   * 显示图片
   */
  showImage(img, src) {
    img.src = src;
    img.classList.remove('lazy-loading');
    img.classList.add('lazy-loaded');
    img.style.backgroundColor = '';
    img.style.minHeight = '';
    
    // 触发动画
    img.style.opacity = '0';
    img.style.transition = 'opacity 0.3s ease';
    
    requestAnimationFrame(() => {
      img.style.opacity = '1';
    });

    // 触发加载完成事件
    img.dispatchEvent(new CustomEvent('lazyloaded', { detail: { src } }));
  }

  /**
   * 处理加载错误
   */
  handleError(img) {
    img.classList.remove('lazy-loading');
    img.classList.add('lazy-error');
    
    if (this.options.errorImage) {
      img.src = this.options.errorImage;
    }
    
    // 触发错误事件
    img.dispatchEvent(new CustomEvent('lazyerror'));
  }

  /**
   * 降级处理（浏览器不支持IntersectionObserver）
   */
  fallbackLoad() {
    const images = document.querySelectorAll('img[data-src]');
    images.forEach(img => {
      const src = img.dataset.src;
      if (src) {
        img.src = src;
      }
    });
  }

  /**
   * 创建懒加载图片元素
   */
  static create(src, options = {}) {
    const {
      alt = '',
      className = '',
      width = null,
      height = null,
      placeholder = null
    } = options;

    const img = document.createElement('img');
    img.dataset.src = src;
    img.alt = alt;
    if (className) img.className = className;
    if (width) img.width = width;
    if (height) img.height = height;
    
    if (placeholder) {
      img.src = placeholder;
    }

    return img;
  }

  /**
   * 创建背景图片懒加载
   */
  static createBackground(element, src, options = {}) {
    if (!element) return;

    const lazyBg = new LazyImage(options);
    
    // 创建占位符
    element.classList.add('lazy-bg', 'lazy-loading');
    element.style.backgroundColor = '#f3f4f6';
    
    // 预加载
    const img = new Image();
    img.onload = () => {
      element.style.backgroundImage = `url(${src})`;
      element.classList.remove('lazy-loading');
      element.classList.add('lazy-loaded');
      element.style.backgroundColor = '';
    };
    img.src = src;

    return lazyBg;
  }

  /**
   * 刷新（重新观察新添加的图片）
   */
  refresh() {
    this.observeAll();
  }

  /**
   * 销毁
   */
  destroy() {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    this.imageCache.clear();
  }
}

// 创建全局实例
export const lazyImage = new LazyImage();

export default LazyImage;
