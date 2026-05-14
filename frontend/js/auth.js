/**
 * Auth service — login state management via storage.js.
 * No direct localStorage calls — all go through window.storage.
 */

const auth = {
  isLoggedIn() {
    return storage.isAuthenticated();
  },

  getUser() {
    return storage.getUser();
  },

  getToken() {
    return storage.getToken();
  },

  /**
   * Set auth state after login/register.
   * @param {string} accessToken
   * @param {string} refreshToken
   * @param {object} user
   */
  setAuth(accessToken, refreshToken, user) {
    storage.setToken(accessToken, refreshToken);
    if (user) storage.setUser(user);
  },

  /**
   * Clear auth state and redirect to login.
   */
  logout() {
    storage.clearAll();
    window.location.href = '/login.html';
  },

  /**
   * Update UI elements based on auth state.
   * Uses data-auth / data-guest attributes for show/hide.
   */
  updateUI() {
    const user = this.getUser();
    const authElements = document.querySelectorAll('[data-auth]');
    const guestElements = document.querySelectorAll('[data-guest]');

    if (this.isLoggedIn() && user) {
      authElements.forEach(el => el.style.display = '');
      guestElements.forEach(el => el.style.display = 'none');

      document.querySelectorAll('.user-name').forEach(el => {
        el.textContent = user.username || user.email;
      });
      document.querySelectorAll('.user-avatar').forEach(el => {
        el.textContent = (user.username || user.email || '?').charAt(0).toUpperCase();
      });
    } else {
      authElements.forEach(el => el.style.display = 'none');
      guestElements.forEach(el => el.style.display = '');
    }
  },

  /**
   * Guard: redirect to login if not authenticated.
   */
  requireAuth() {
    return storage.requireAuth();
  },

  /**
   * Redirect away from login/register if already authenticated.
   */
  redirectIfLoggedIn(url = '/index.html') {
    if (this.isLoggedIn()) {
      window.location.href = url;
      return true;
    }
    return false;
  }
};

window.auth = auth;

document.addEventListener('DOMContentLoaded', () => {
  auth.updateUI();
});
