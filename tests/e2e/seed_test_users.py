"""
Seed E2E test users and their profile states for CI.

Run AFTER backend server is up:
    python tests/e2e/seed_test_users.py [--base-url http://localhost:8000]
"""

import json
import sys
import urllib.error
import urllib.request

BASE_URL = (
    sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--base-url" else "http://localhost:8000"
)
API = f"{BASE_URL}/api/v1"
PASSWORD = "Pass1234"


def api(method, path, data=None, token=None):
    """Call API endpoint, return (status, body_dict)."""
    url = f"{API}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def register(username, email):
    """Register a user. Ignore 400 (already exists)."""
    status, body = api(
        "POST",
        "/auth/register",
        {
            "username": username,
            "email": email,
            "password": PASSWORD,
        },
    )
    if status in (201, 200):
        print(f"  ✓ registered {username}")
    elif status == 400 and "already" in str(body).lower():
        print(f"  - {username} already exists")
    else:
        print(f"  ✗ register {username}: {status} {body}")


def login(email):
    """Login and return access_token."""
    status, body = api(
        "POST",
        "/auth/login",
        {
            "email": email,
            "password": PASSWORD,
        },
    )
    if status == 200:
        return body.get("access_token")
    print(f"  ✗ login {email}: {status} {body}")
    return None


def set_profile(token, username, is_public=None, display_name=None, bio=None, **dimensions):
    """Update profile settings. If is_public=True, auto-enables all dimensions (BR5)."""
    data = {}
    if is_public is not None:
        data["is_public"] = is_public
    if display_name is not None:
        data["display_name"] = display_name
    if bio is not None:
        data["bio"] = bio
    if dimensions:
        data.update(dimensions)
    if not data:
        return
    status, body = api("PUT", "/profile/me/settings", data, token=token)
    if status == 200:
        print(f"  ✓ profile set for {username}" + (f": {data}" if data else ""))
    else:
        print(f"  ✗ profile {username}: {status} {body}")


def batch_action(token, username, action):
    """POST /me/settings/batch with show_all or hide_all."""
    status, body = api("POST", "/profile/me/settings/batch", {"action": action}, token=token)
    if status == 200:
        print(f"  ✓ {action} for {username}")
    else:
        print(f"  ✗ batch {action} {username}: {status} {body}")


def main():
    users = [
        ("e2e_public", "e2e_public@test.com"),
        ("e2e_partial", "e2e_partial@test.com"),
        ("e2e_hidden_all", "e2e_hidden_all@test.com"),
        ("e2e_disabled", "e2e_disabled@test.com"),
        ("e2e_empty", "e2e_empty@test.com"),
        ("e2e_first_enable", "e2e_first_enable@test.com"),
        ("e2e_adjustable", "e2e_adjustable@test.com"),
        ("e2e_closable", "e2e_closable@test.com"),
    ]

    print("=== Step 1: Register all users ===")
    for username, email in users:
        register(username, email)

    print("\n=== Step 2: Set up profiles ===")
    # e2e_public: all visible, display_name="公开用户", bio="这是公开用户的一句话简介"
    token = login("e2e_public@test.com")
    if token:
        set_profile(
            token,
            "e2e_public",
            is_public=True,
            display_name="公开用户",
            bio="这是公开用户的一句话简介",
        )

    # e2e_partial: only skill_radar visible, display_name="部分隐藏用户"
    # BR5 auto-enables all when is_public first set → need second call to disable
    token = login("e2e_partial@test.com")
    if token:
        set_profile(token, "e2e_partial", is_public=True, display_name="部分隐藏用户")
        # Second call: disable labs, certs; keep basic_info + skill_radar
        set_profile(
            token, "e2e_partial", show_labs=False, show_certificates=False, show_skill_radar=True
        )

    # e2e_hidden_all: profile ON but all dimensions hidden
    token = login("e2e_hidden_all@test.com")
    if token:
        set_profile(token, "e2e_hidden_all", is_public=True)
        batch_action(token, "e2e_hidden_all", "hide_all")

    # e2e_disabled: do NOT enable profile (just registered)

    # e2e_empty: profile ON, zero labs/certs, display_name="空数据用户"
    token = login("e2e_empty@test.com")
    if token:
        set_profile(token, "e2e_empty", is_public=True, display_name="空数据用户")

    # e2e_first_enable: not enabled (for AC3 test)

    # e2e_adjustable: enabled (for AC4 test)
    token = login("e2e_adjustable@test.com")
    if token:
        set_profile(token, "e2e_adjustable", is_public=True)

    # e2e_closable: enabled (for AC11 test)
    token = login("e2e_closable@test.com")
    if token:
        set_profile(token, "e2e_closable", is_public=True)

    print("\n=== Done: all E2E test users seeded ===")


if __name__ == "__main__":
    main()
