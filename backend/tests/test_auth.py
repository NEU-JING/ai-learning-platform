"""Tests for authentication API endpoints."""

import pytest


class TestRegister:
    def test_register_success(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "new@example.com", "username": "newuser", "password": "Pass1234"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@example.com"
        assert data["username"] == "newuser"
        assert "password" not in data
        assert data["role"] == "student"

    def test_register_duplicate_email(self, client, test_user):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "testuser@example.com", "username": "other", "password": "Pass1234"},
        )
        assert resp.status_code == 400
        assert "已被注册" in resp.json()["detail"]

    def test_register_duplicate_username(self, client, test_user):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "other@example.com", "username": "testuser", "password": "Pass1234"},
        )
        assert resp.status_code == 400

    def test_register_weak_password(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "weak@example.com", "username": "weakuser", "password": "short"},
        )
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "username": "bademail", "password": "Pass1234"},
        )
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client, test_user):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "TestPass123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "WrongPass1"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "Pass1234"},
        )
        assert resp.status_code == 401


class TestGetMe:
    def test_get_me_authenticated(self, client, auth_headers, test_user):
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "testuser@example.com"

    def test_get_me_no_token(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_get_me_invalid_token(self, client):
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401
