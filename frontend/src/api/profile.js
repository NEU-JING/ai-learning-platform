/**
 * Profile API client — calls /api/v1/profile/{username} and /api/v1/profile/me/settings
 *
 * Public profile data is fetched without authentication.
 * Settings CRUD requires auth token (handled by API client in services/api.js).
 * Error responses (403/404) are returned as-is so the UI can
 * render appropriate messages.
 */

import { ENV } from '../config/env.js';

const API_BASE = ENV.API_BASE_URL || `${window.location.origin}/api/v1`;

/**
 * Fetch public profile data for a given username.
 * No auth token required — this is an anonymous endpoint.
 *
 * @param {string} username
 * @returns {Promise<Object>} Profile data on success
 * @throws {Error} With status code and detail on 403/404/5xx
 */
export async function fetchPublicProfile(username) {
  const url = `${API_BASE}/profile/${encodeURIComponent(username)}`;
  const resp = await fetch(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({
      detail: `HTTP ${resp.status}: ${resp.statusText}`,
    }));
    const err = new Error(error.detail || '请求失败');
    err.status = resp.status;
    err.detail = error.detail;
    throw err;
  }

  return resp.json();
}

// ── Settings CRUD (requires auth) ───────────────────────────────────────

function _getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function _handleResponse(resp) {
  if (!resp.ok) {
    const error = await resp.json().catch(() => ({
      detail: `HTTP ${resp.status}: ${resp.statusText}`,
    }));
    const err = new Error(error.detail || '请求失败');
    err.status = resp.status;
    err.detail = error.detail;
    throw err;
  }
  return resp.json();
}

/**
 * Get current user's profile settings.
 * Requires auth token.
 *
 * @returns {Promise<Object>} Settings data
 */
export async function getProfileSettings() {
  const resp = await fetch(`${API_BASE}/profile/me/settings`, {
    method: 'GET',
    headers: _getAuthHeaders(),
  });
  return _handleResponse(resp);
}

/**
 * Update current user's profile settings.
 * Requires auth token.
 *
 * @param {Object} data - { is_public?, show_basic_info?, show_skill_radar?, show_labs?, show_certificates?, display_name?, bio? }
 * @returns {Promise<Object>} Updated settings
 */
export async function updateProfileSettings(data) {
  const resp = await fetch(`${API_BASE}/profile/me/settings`, {
    method: 'PUT',
    headers: _getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return _handleResponse(resp);
}

/**
 * Batch operation on profile settings.
 * Requires auth token.
 *
 * @param {string} action - "show_all" or "hide_all"
 * @returns {Promise<Object>} Updated settings
 */
export async function batchProfileSettings(action) {
  const resp = await fetch(`${API_BASE}/profile/me/settings/batch`, {
    method: 'POST',
    headers: _getAuthHeaders(),
    body: JSON.stringify({ action }),
  });
  return _handleResponse(resp);
}

export default {
  fetchPublicProfile,
  getProfileSettings,
  updateProfileSettings,
  batchProfileSettings,
};
