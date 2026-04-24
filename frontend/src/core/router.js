/**
 * 路由系统 - 原生JavaScript实现
 * 支持hash模式和history模式
 */

export class Router {
  constructor(options = {}) {
    this.routes = options.routes || [];
    this.mode = options.mode || 'hash'; // 'hash' or 'history'
    this.beforeEach = options.beforeEach || (() => {});
    this.afterEach = options.afterEach || (() => {});
    this.currentRoute = null;
    this.params = {};
    this.query = {};
    
    // 路由缓存
    this.cache = new Map();
  }

  init() {
    // 监听路由变化
    window.addEventListener(this.mode === 'hash' ? 'hashchange' : 'popstate', () => {
      this.handleRouteChange();
    });

    // 初始路由
    this.handleRouteChange();
  }

  handleRouteChange() {
    const path = this.getCurrentPath();
    this.navigate(path, false);
  }

  getCurrentPath() {
    if (this.mode === 'hash') {
      return window.location.hash.slice(1) || '/';
    }
    return window.location.pathname + window.location.search;
  }

  async navigate(path, pushState = true) {
    // 解析路径
    const { pathname, query } = this.parsePath(path);
    this.query = query;

    // 匹配路由
    const route = this.matchRoute(pathname);
    
    if (!route) {
      // 404处理
      const notFoundRoute = this.routes.find(r => r.path === '*');
      if (notFoundRoute) {
        await this.renderRoute(notFoundRoute);
      }
      return;
    }

    // 导航守卫
    let canProceed = true;
    await this.beforeEach(route, this.currentRoute, (nextPath) => {
      if (nextPath === false) {
        canProceed = false;
      } else if (typeof nextPath === 'string') {
        this.navigate(nextPath);
        canProceed = false;
      }
    });

    if (!canProceed) return;

    // 更新历史记录
    if (pushState) {
      if (this.mode === 'hash') {
        window.location.hash = path;
      } else {
        window.history.pushState({}, '', path);
      }
    }

    // 渲染组件
    await this.renderRoute(route);
    
    // 更新当前路由
    this.currentRoute = route;
    
    // 后置钩子
    this.afterEach(route);
  }

  parsePath(path) {
    const [pathname, search] = path.split('?');
    const query = {};
    
    if (search) {
      search.split('&').forEach(param => {
        const [key, value] = param.split('=');
        query[decodeURIComponent(key)] = decodeURIComponent(value || '');
      });
    }
    
    return { pathname, query };
  }

  matchRoute(path) {
    for (const route of this.routes) {
      if (route.path === '*') continue;
      
      const match = this.matchPath(path, route.path);
      if (match) {
        this.params = match.params;
        return { ...route, params: match.params };
      }
    }
    return null;
  }

  matchPath(path, routePath) {
    // 将路由路径转换为正则
    const paramNames = [];
    const regexPattern = routePath.replace(/:([^/]+)/g, (match, name) => {
      paramNames.push(name);
      return '([^/]+)';
    });

    const regex = new RegExp(`^${regexPattern}$`);
    const match = path.match(regex);

    if (!match) return null;

    const params = {};
    paramNames.forEach((name, index) => {
      params[name] = match[index + 1];
    });

    return { params };
  }

  async renderRoute(route) {
    const app = document.getElementById('app');
    
    if (!app) {
      console.error('找不到 #app 元素');
      return;
    }

    // 显示加载状态
    app.innerHTML = '<div class="loading">加载中...</div>';

    try {
      // 动态导入组件
      let component;
      if (route.component) {
        if (typeof route.component === 'function') {
          const module = await route.component();
          component = module.default || module;
        } else {
          component = route.component;
        }
      }

      if (component) {
        const content = await component({
          params: this.params,
          query: this.query,
          route
        });
        app.innerHTML = content;
        
        // 执行组件的挂载钩子
        if (component.onMount) {
          component.onMount();
        }
      }
    } catch (error) {
      console.error('路由渲染失败:', error);
      app.innerHTML = `
        <div class="error-page">
          <h1>页面加载失败</h1>
          <p>${error.message}</p>
          <a href="#/" class="btn btn-primary">返回首页</a>
        </div>
      `;
    }
  }

  push(path) {
    this.navigate(path, true);
  }

  replace(path) {
    if (this.mode === 'hash') {
      window.location.replace(`#${path}`);
    } else {
      window.history.replaceState({}, '', path);
    }
    this.handleRouteChange();
  }

  go(n) {
    window.history.go(n);
  }

  back() {
    this.go(-1);
  }
}
