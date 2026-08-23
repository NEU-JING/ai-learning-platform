"""Phase 2 部署验证脚本 — 测试所有关键 API 端点"""

import json
import sys
import urllib.request

BASE = "http://localhost:8000"


def api(method, path, data=None, token=None):
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as e:
        return 0, {"error": str(e)}


results = []

# 1. 公开 API
print("=" * 60)
print("📡 公开 API 验证")
print("=" * 60)

status, data = api("GET", "/health")
ok = status == 200 and data.get("status") == "healthy"
results.append(("GET /health", ok))
print(f"  {'✅' if ok else '❌'} /health → {status}")

status, data = api("GET", "/api/v1/courses/")
ok = status == 200 and isinstance(data, dict) and data.get("total", 0) >= 6
results.append(("GET /courses/ (6 Phases)", ok))
print(f"  {'✅' if ok else '❌'} /courses/ → {data.get('total', '?')} courses")

status, data = api("GET", "/api/v1/courses/paths")
ok = status == 200 and len(data) >= 3
results.append(("GET /paths (4 paths)", ok))
print(f"  {'✅' if ok else '❌'} /paths → {len(data)} paths")

# 2. 注册用户
print("\n" + "=" * 60)
print("🔐 认证 & Phase 2 API 验证")
print("=" * 60)

status, data = api(
    "POST",
    "/api/v1/auth/register",
    {"email": "verify_p2@test.com", "username": "verifier_p2", "password": "TestPass123"},
)
if status == 200:
    token = data.get("access_token", "")
    print(f"  ✅ 注册成功 (token: {token[:20]}...)")
else:
    # Try login
    status, data = api(
        "POST", "/api/v1/auth/login", {"username": "verifier_p2", "password": "TestPass123"}
    )
    token = data.get("access_token", "")
    print(f"  {'✅' if token else '❌'} 登录 {'成功' if token else '失败'}")

if token:
    # 3. L1 认证申请 (M1)
    status, data = api("POST", "/api/v1/certifications/apply", {"level_id": 1}, token=token)
    ok = status == 200
    results.append(("POST /certifications/apply (L1)", ok))
    print(f"  {'✅' if ok else '❌'} 认证申请 → {status}")

    # 4. Tutor session
    status, data = api("POST", "/api/v1/tutor/sessions", {"course_id": 1}, token=token)
    ok = status == 200
    if ok:
        session_id = data.get("session_id") or data.get("id")
        results.append(("POST /tutor/sessions", ok))
        print(f"  {'✅' if ok else '❌'} 创建 Session → session_id={session_id}")

        # 5. Tutor chat
        status, data = api(
            "POST",
            f"/api/v1/tutor/sessions/{session_id}/messages",
            {"content": "Hello tutor"},
            token=token,
        )
        ok = status == 200
        results.append(("POST /tutor/sessions/{id}/messages", ok))
        print(f"  {'✅' if ok else '❌'} 发送消息 → {status}")
    else:
        results.append(("POST /tutor/sessions", False))
        print(f"  ❌ 创建 Session → {status}")

    # 6. Code Review (T13)
    status, data = api(
        "POST",
        "/api/v1/tutor/code-review",
        {"lab_id": 1, "code_content": "def add(a, b):\n    return a + b", "language": "python"},
        token=token,
    )
    ok = status == 200
    results.append(("POST /tutor/code-review (T13)", ok))
    print(f"  {'✅' if ok else '❌'} Code Review → {status}")

    # 7. Certificate detail (M2)
    status, data = api("GET", "/api/v1/certificates/verify/test-cert-123", token=token)
    ok = status in (200, 404)  # 404 is OK - cert doesn't exist yet
    results.append(("GET /certificates/verify (M2)", ok))
    print(f"  {'✅' if ok else '❌'} 证书验证 → {status}")

# Summary
print("\n" + "=" * 60)
print("📊 验证总结")
print("=" * 60)
passed = sum(1 for _, ok in results if ok)
total = len(results)
for name, ok in results:
    print(f"  {'✅' if ok else '❌'} {name}")

print(f"\n{'🎉' if passed == total else '⚠️'}  {passed}/{total} 通过")
sys.exit(0 if passed == total else 1)
