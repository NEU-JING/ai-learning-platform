/**
 * Storage utility — centralized token & user state management.
 * DESIGN.md §9 Red Line: all token ops go through this module.
 *
 * Features:
 * - Token with expiry check (auto-clear expired tokens)
 * - User info caching with structure validation
 * - Auto-redirect to login on 401
 */

const TOKEN_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';
const USER_KEY = 'user_info';

const storage = {
  // ── Token ─────────────────────────────────────────────

  getToken() {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return null;

    // Check expiry without library — decode JWT payload
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      if (payload.exp && payload.exp * 1000 < Date.now()) {
        this.clearAll();
        return null;
      }
    } catch {
      // Not a valid JWT — clear it
      this.clearAll();
      return null;
    }
    return token;
  },

  setToken(accessToken, refreshToken) {
    localStorage.setItem(TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(REFRESH_KEY, refreshToken);
    }
  },

  getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY);
  },

  // ── User ──────────────────────────────────────────────

  getUser() {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      const user = JSON.parse(raw);
      if (!user.id || !user.email) {
        this.clearAll();
        return null;
      }
      return user;
    } catch {
      this.clearAll();
      return null;
    }
  },

  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  // ── Auth state ────────────────────────────────────────

  isAuthenticated() {
    return !!this.getToken();
  },

  clearAll() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
  },

  /**
   * Redirect to login if not authenticated.
   * @returns {boolean} true if authenticated
   */
  requireAuth() {
    if (!this.isAuthenticated()) {
      const redirect = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `/login.html?redirect=${redirect}`;
      return false;
    }
    return true;
  },

  /**
   * Get auth headers for fetch().
   */
  getAuthHeaders() {
    const token = this.getToken();
    return token
      ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
      : { 'Content-Type': 'application/json' };
  }
};

window.storage = storage;
