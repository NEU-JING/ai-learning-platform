/**
 * 代码自动保存服务
 * 使用localStorage存储代码草稿
 */

const AUTOSAVE_PREFIX = 'ai-learning-autosave-';
const AUTOSAVE_INTERVAL = 30000; // 30秒

class AutoSaveService {
  constructor() {
    this.timers = new Map();
    this.listeners = new Map();
  }

  /**
   * 获取存储键
   */
  getStorageKey(key) {
    return `${AUTOSAVE_PREFIX}${key}`;
  }

  /**
   * 保存草稿
   */
  save(key, content) {
    try {
      const data = {
        content,
        timestamp: Date.now(),
        version: 1
      };
      localStorage.setItem(this.getStorageKey(key), JSON.stringify(data));
      this.notifyListeners(key, content);
      return true;
    } catch (e) {
      console.error('AutoSave save error:', e);
      return false;
    }
  }

  /**
   * 读取草稿
   */
  load(key) {
    try {
      const stored = localStorage.getItem(this.getStorageKey(key));
      if (!stored) return null;
      
      const data = JSON.parse(stored);
      return {
        content: data.content,
        timestamp: data.timestamp,
        savedAt: new Date(data.timestamp).toLocaleString()
      };
    } catch (e) {
      console.error('AutoSave load error:', e);
      return null;
    }
  }

  /**
   * 删除草稿
   */
  remove(key) {
    try {
      localStorage.removeItem(this.getStorageKey(key));
      return true;
    } catch (e) {
      console.error('AutoSave remove error:', e);
      return false;
    }
  }

  /**
   * 启动自动保存
   */
  start(key, getContentFn, interval = AUTOSAVE_INTERVAL) {
    // 停止之前的定时器
    this.stop(key);

    // 启动新的定时器
    const timer = setInterval(() => {
      const content = getContentFn();
      if (content) {
        this.save(key, content);
      }
    }, interval);

    this.timers.set(key, timer);

    // 页面关闭前保存
    const beforeUnloadHandler = () => {
      const content = getContentFn();
      if (content) {
        this.save(key, content);
      }
    };

    window.addEventListener('beforeunload', beforeUnloadHandler);
    this.listeners.set(key, beforeUnloadHandler);

    return true;
  }

  /**
   * 停止自动保存
   */
  stop(key) {
    // 清除定时器
    const timer = this.timers.get(key);
    if (timer) {
      clearInterval(timer);
      this.timers.delete(key);
    }

    // 移除事件监听
    const listener = this.listeners.get(key);
    if (listener) {
      window.removeEventListener('beforeunload', listener);
      this.listeners.delete(key);
    }

    return true;
  }

  /**
   * 清理所有自动保存
   */
  stopAll() {
    this.timers.forEach((timer, key) => {
      clearInterval(timer);
    });
    this.timers.clear();

    this.listeners.forEach((listener, key) => {
      window.removeEventListener('beforeunload', listener);
    });
    this.listeners.clear();
  }

  /**
   * 清理过期草稿（超过7天）
   */
  cleanupExpired(maxAge = 7 * 24 * 60 * 60 * 1000) {
    const now = Date.now();
    
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(AUTOSAVE_PREFIX)) {
          const stored = localStorage.getItem(key);
          if (stored) {
            const data = JSON.parse(stored);
            if (now - data.timestamp > maxAge) {
              localStorage.removeItem(key);
            }
          }
        }
      }
    } catch (e) {
      console.error('AutoSave cleanup error:', e);
    }
  }

  /**
   * 获取所有草稿
   */
  getAllDrafts() {
    const drafts = [];
    
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(AUTOSAVE_PREFIX)) {
          const stored = localStorage.getItem(key);
          if (stored) {
            const data = JSON.parse(stored);
            drafts.push({
              key: key.replace(AUTOSAVE_PREFIX, ''),
              content: data.content,
              timestamp: data.timestamp,
              savedAt: new Date(data.timestamp).toLocaleString()
            });
          }
        }
      }
    } catch (e) {
      console.error('AutoSave getAllDrafts error:', e);
    }

    return drafts.sort((a, b) => b.timestamp - a.timestamp);
  }

  /**
   * 监听保存事件
   */
  onSave(key, callback) {
    if (!this.listeners.has(key)) {
      this.listeners.set(key, []);
    }
    this.listeners.get(key).push(callback);
  }

  /**
   * 通知监听器
   */
  notifyListeners(key, content) {
    const callbacks = this.listeners.get(key);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(content);
        } catch (e) {
          console.error('AutoSave listener error:', e);
        }
      });
    }
  }

  /**
   * 显示恢复提示
   */
  showRestoreNotification(key, onRestore, onDiscard) {
    const draft = this.load(key);
    if (!draft) return;

    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = 'autosave-notification';
    notification.innerHTML = `
      <div class="autosave-message">
        <span>💾 发现未保存的草稿 (${draft.savedAt})</span>
      </div>
      <div class="autosave-actions">
        <button class="btn-restore">恢复</button>
        <button class="btn-discard">丢弃</button>
      </div>
    `;

    // 绑定事件
    notification.querySelector('.btn-restore').addEventListener('click', () => {
      onRestore(draft.content);
      notification.remove();
    });

    notification.querySelector('.btn-discard').addEventListener('click', () => {
      this.remove(key);
      onDiscard();
      notification.remove();
    });

    // 添加到页面
    document.body.appendChild(notification);

    // 5秒后自动隐藏
    setTimeout(() => {
      notification.classList.add('fade-out');
      setTimeout(() => notification.remove(), 500);
    }, 5000);
  }
}

// 导出单例
export const autoSaveService = new AutoSaveService();

// 默认导出
export default autoSaveService;
