/**
 * 触摸手势支持组件
 */

export class TouchGestures {
  constructor(element, options = {}) {
    this.element = element;
    this.options = {
      threshold: 50,        // 触发手势的最小距离
      velocity: 0.3,        // 触发快速滑动的最小速度
      preventDefault: true, // 阻止默认行为
      ...options
    };
    
    this.startX = 0;
    this.startY = 0;
    this.startTime = 0;
    this.isTouching = false;
    
    this.handlers = {
      swipeLeft: [],
      swipeRight: [],
      swipeUp: [],
      swipeDown: [],
      tap: [],
      doubleTap: [],
      longPress: [],
      pinch: [],
      rotate: []
    };
    
    this.longPressTimer = null;
    this.lastTapTime = 0;
    
    this.init();
  }

  init() {
    if (!this.element) return;
    
    this.element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
    this.element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
    this.element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false });
    this.element.addEventListener('touchcancel', this.handleTouchCancel.bind(this), { passive: false });
  }

  handleTouchStart(e) {
    const touch = e.touches[0];
    this.startX = touch.clientX;
    this.startY = touch.clientY;
    this.startTime = Date.now();
    this.isTouching = true;
    
    // 长按检测
    this.longPressTimer = setTimeout(() => {
      if (this.isTouching) {
        this.trigger('longPress', {
          x: this.startX,
          y: this.startY,
          originalEvent: e
        });
      }
    }, 500);
  }

  handleTouchMove(e) {
    if (!this.isTouching) return;
    
    // 取消长按
    clearTimeout(this.longPressTimer);
    
    if (this.options.preventDefault) {
      e.preventDefault();
    }
  }

  handleTouchEnd(e) {
    if (!this.isTouching) return;
    
    this.isTouching = false;
    clearTimeout(this.longPressTimer);
    
    const touch = e.changedTouches[0];
    const endX = touch.clientX;
    const endY = touch.clientY;
    const endTime = Date.now();
    
    const deltaX = endX - this.startX;
    const deltaY = endY - this.startY;
    const deltaTime = endTime - this.startTime;
    
    const velocityX = Math.abs(deltaX) / deltaTime;
    const velocityY = Math.abs(deltaY) / deltaTime;
    
    const gestureData = {
      deltaX,
      deltaY,
      startX: this.startX,
      startY: this.startY,
      endX,
      endY,
      velocityX,
      velocityY,
      duration: deltaTime,
      originalEvent: e
    };

    // 检测双击
    if (deltaTime < 200 && Math.abs(deltaX) < 10 && Math.abs(deltaY) < 10) {
      if (endTime - this.lastTapTime < 300) {
        this.trigger('doubleTap', gestureData);
        this.lastTapTime = 0;
        return;
      }
      this.lastTapTime = endTime;
    }

    // 检测滑动
    const absX = Math.abs(deltaX);
    const absY = Math.abs(deltaY);
    
    if (absX > absY && absX > this.options.threshold) {
      // 水平滑动
      if (deltaX > 0 && velocityX > this.options.velocity) {
        this.trigger('swipeRight', gestureData);
      } else if (deltaX < 0 && velocityX > this.options.velocity) {
        this.trigger('swipeLeft', gestureData);
      }
    } else if (absY > absX && absY > this.options.threshold) {
      // 垂直滑动
      if (deltaY > 0 && velocityY > this.options.velocity) {
        this.trigger('swipeDown', gestureData);
      } else if (deltaY < 0 && velocityY > this.options.velocity) {
        this.trigger('swipeUp', gestureData);
      }
    } else if (absX < 10 && absY < 10 && deltaTime < 200) {
      // 点击
      this.trigger('tap', gestureData);
    }
  }

  handleTouchCancel(e) {
    this.isTouching = false;
    clearTimeout(this.longPressTimer);
  }

  /**
   * 绑定手势事件
   */
  on(event, handler) {
    if (this.handlers[event]) {
      this.handlers[event].push(handler);
    }
    return this;
  }

  /**
   * 解绑手势事件
   */
  off(event, handler) {
    if (this.handlers[event]) {
      this.handlers[event] = this.handlers[event].filter(h => h !== handler);
    }
    return this;
  }

  /**
   * 触发手势事件
   */
  trigger(event, data) {
    if (this.handlers[event]) {
      this.handlers[event].forEach(handler => {
        try {
          handler(data);
        } catch (e) {
          console.error(`Gesture handler error for ${event}:`, e);
        }
      });
    }
  }

  /**
   * 销毁
   */
  destroy() {
    clearTimeout(this.longPressTimer);
    this.element?.removeEventListener('touchstart', this.handleTouchStart);
    this.element?.removeEventListener('touchmove', this.handleTouchMove);
    this.element?.removeEventListener('touchend', this.handleTouchEnd);
    this.element?.removeEventListener('touchcancel', this.handleTouchCancel);
  }
}

/**
 * 代码编辑器触摸增强
 */
export function initCodeEditorTouch(editor) {
  const gestures = new TouchGestures(editor.getDomNode());
  
  // 左右滑动切换标签
  gestures.on('swipeLeft', () => {
    // 切换到下一个文件
    document.dispatchEvent(new CustomEvent('editor:nextFile'));
  });
  
  gestures.on('swipeRight', () => {
    // 切换到上一个文件
    document.dispatchEvent(new CustomEvent('editor:prevFile'));
  });
  
  // 长按显示上下文菜单
  gestures.on('longPress', (e) => {
    editor.trigger('keyboard', 'editor.action.showContextMenu', {});
  });
  
  return gestures;
}

export default TouchGestures;
