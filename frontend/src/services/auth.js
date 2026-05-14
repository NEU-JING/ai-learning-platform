/**
 * 认证服务 - 处理用户登录态管理
 * 统一使用 'access_token' 和 'refresh_token' 与传统版 storage.js 保持一致
 */

const TOKEN_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';

export class AuthService {
  static getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  static setToken(accessToken, refreshToken) {
    localStorage.setItem(TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(REFRESH_KEY, refreshToken);
    }
  }

  static getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY);
  }

  static clearToken() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }

  static isAuthenticated() {
    return !!this.getToken();
  }

  static getAuthHeader() {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
}
