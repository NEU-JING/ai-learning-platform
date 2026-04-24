/**
 * 骨架屏组件 - 加载状态占位符
 */

export class Skeleton {
  /**
   * 创建骨架屏元素
   * @param {string} variant - 变体类型: text, circular, rectangular, rounded
   * @param {Object} options - 配置选项
   */
  static create(variant = 'text', options = {}) {
    const {
      width = '100%',
      height = null,
      className = '',
      animation = 'pulse' // pulse, wave, none
    } = options;

    const el = document.createElement('div');
    el.className = `skeleton skeleton-${variant} skeleton-${animation} ${className}`;
    
    if (width) el.style.width = typeof width === 'number' ? `${width}px` : width;
    if (height) el.style.height = typeof height === 'number' ? `${height}px` : height;

    return el;
  }

  /**
   * 创建文本骨架
   */
  static text(width = '100%', lines = 1) {
    const container = document.createElement('div');
    container.className = 'skeleton-text-container';
    
    for (let i = 0; i < lines; i++) {
      const line = this.create('text', {
        width: i === lines - 1 && lines > 1 ? '80%' : width,
        className: 'skeleton-text-line'
      });
      container.appendChild(line);
    }
    
    return container;
  }

  /**
   * 创建圆形骨架（头像等）
   */
  static circular(size = 40) {
    return this.create('circular', {
      width: size,
      height: size
    });
  }

  /**
   * 创建矩形骨架
   */
  static rectangular(width = '100%', height = 100) {
    return this.create('rectangular', {
      width,
      height
    });
  }

  /**
   * 创建课程卡片骨架
   */
  static courseCard() {
    const card = document.createElement('div');
    card.className = 'skeleton-card skeleton-course-card';
    
    card.innerHTML = `
      <div class="skeleton-card-image"></div>
      <div class="skeleton-card-content">
        ${this.text('70%', 1).outerHTML}
        ${this.text('100%', 2).outerHTML}
        <div class="skeleton-card-footer">
          ${this.circular(24).outerHTML}
          ${this.text('40%', 1).outerHTML}
        </div>
      </div>
    `;
    
    return card;
  }

  /**
   * 创建课程详情骨架
   */
  static courseDetail() {
    const container = document.createElement('div');
    container.className = 'skeleton-course-detail';
    
    container.innerHTML = `
      <div class="skeleton-course-header">
        ${this.text('60%', 1).outerHTML}
        ${this.text('100%', 3).outerHTML}
      </div>
      <div class="skeleton-chapter-list">
        ${Array(5).fill().map(() => `
          <div class="skeleton-chapter-item">
            ${this.circular(32).outerHTML}
            <div class="skeleton-chapter-info">
              ${this.text('50%', 1).outerHTML}
              ${this.text('80%', 1).outerHTML}
            </div>
          </div>
        `).join('')}
      </div>
    `;
    
    return container;
  }

  /**
   * 创建代码编辑器骨架
   */
  static codeEditor() {
    const container = document.createElement('div');
    container.className = 'skeleton-code-editor';
    
    container.innerHTML = `
      <div class="skeleton-editor-toolbar">
        ${this.rectangular(120, 32).outerHTML}
        <div class="skeleton-toolbar-actions">
          ${this.rectangular(80, 32).outerHTML}
          ${this.rectangular(80, 32).outerHTML}
        </div>
      </div>
      <div class="skeleton-editor-content">
        ${Array(15).fill().map((_, i) => `
          <div class="skeleton-code-line" style="width: ${Math.random() * 40 + 60}%">
            <span class="skeleton-line-number">${i + 1}</span>
            <span class="skeleton-code-text"></span>
          </div>
        `).join('')}
      </div>
    `;
    
    return container;
  }

  /**
   * 创建表格骨架
   */
  static table(rows = 5, columns = 4) {
    const container = document.createElement('div');
    container.className = 'skeleton-table';
    
    // 表头
    const header = document.createElement('div');
    header.className = 'skeleton-table-header';
    header.innerHTML = Array(columns).fill().map(() => 
      this.text('80%', 1).outerHTML
    ).join('');
    container.appendChild(header);
    
    // 表体
    const body = document.createElement('div');
    body.className = 'skeleton-table-body';
    body.innerHTML = Array(rows).fill().map(() => `
      <div class="skeleton-table-row">
        ${Array(columns).fill().map(() => this.text('60%', 1).outerHTML).join('')}
      </div>
    `).join('');
    container.appendChild(body);
    
    return container;
  }

  /**
   * 显示加载状态（替换元素内容）
   */
  static show(element, skeletonGenerator) {
    if (!element) return;
    
    // 保存原始内容
    element.dataset.originalContent = element.innerHTML;
    element.dataset.loading = 'true';
    
    // 清空并显示骨架
    element.innerHTML = '';
    const skeleton = typeof skeletonGenerator === 'function' 
      ? skeletonGenerator() 
      : skeletonGenerator;
    element.appendChild(skeleton);
    
    return {
      hide: () => this.hide(element)
    };
  }

  /**
   * 隐藏加载状态（恢复原始内容）
   */
  static hide(element) {
    if (!element || !element.dataset.loading) return;
    
    element.innerHTML = element.dataset.originalContent || '';
    delete element.dataset.originalContent;
    delete element.dataset.loading;
  }
}

export default Skeleton;
