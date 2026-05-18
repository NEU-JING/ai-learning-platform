/**
 * 状态管理 - 简化版Vuex/Pinia实现
 * 支持响应式状态、mutations和actions
 */

export class Store {
  static _instance = null;

  static getInstance() {
    if (!Store._instance) {
      throw new Error('Store not initialized. Call Store.setInstance() from main.js first.');
    }
    return Store._instance;
  }

  static setInstance(store) {
    Store._instance = store;
  }

  constructor(options = {}) {
    this.state = this._makeReactive(options.state || {});
    this.mutations = options.mutations || {};
    this.actions = options.actions || {};
    this.subscribers = [];
  }

  // 创建响应式对象
  _makeReactive(obj) {
    const store = this;
    
    return new Proxy(obj, {
      set(target, key, value) {
        const oldValue = target[key];
        target[key] = value;
        
        // 通知订阅者
        store._notifySubscribers(key, value, oldValue);
        
        return true;
      },
      
      get(target, key) {
        const value = target[key];
        
        // 递归处理嵌套对象
        if (typeof value === 'object' && value !== null) {
          return store._makeReactive(value);
        }
        
        return value;
      }
    });
  }

  _notifySubscribers(key, newValue, oldValue) {
    this.subscribers.forEach(callback => {
      callback(key, newValue, oldValue);
    });
  }

  // 订阅状态变化
  subscribe(callback) {
    this.subscribers.push(callback);
    
    // 返回取消订阅函数
    return () => {
      const index = this.subscribers.indexOf(callback);
      if (index > -1) {
        this.subscribers.splice(index, 1);
      }
    };
  }

  // 提交mutation
  commit(mutationName, payload) {
    const mutation = this.mutations[mutationName];
    
    if (!mutation) {
      console.error(`未知的mutation: ${mutationName}`);
      return;
    }

    mutation(this.state, payload);
  }

  // 分发action
  async dispatch(actionName, payload) {
    const action = this.actions[actionName];
    
    if (!action) {
      console.error(`未知的action: ${actionName}`);
      return;
    }

    const context = {
      state: this.state,
      commit: this.commit.bind(this),
      dispatch: this.dispatch.bind(this)
    };

    return await action(context, payload);
  }

  // 创建计算属性
  getter(fn) {
    return fn(this.state);
  }
}
