/**
 * 认证服务 - 处理用户登录态管理
 */

export class AuthService {
  static getToken() {
    return localStorage.getItem('token');
  }

  static setToken(token) {
    localStorage.setItem('token', token);
  }

  static clearToken() {
    localStorage.removeItem('token');
  }

  static isAuthenticated() {
    return !!this.getToken();
  }

  static getAuthHeader() {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
}
