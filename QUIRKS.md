# QUIRKS.md — AILP（AI Learning Platform）

> 项目陷阱与怪癖记录。随着开发过程持续更新，避免踩同样的坑。

---

## 已知陷阱

### JWT sub 必须 string

**现象**：JWT decode 返回 None，认证失败
**原因**：python-jose 按 RFC 7519 要求 sub 是 string，传 int 导致解码失败
**修复方式**：`user_id` 转为 string 后再传入 JWT payload
**预防措施**：类型检查和单元测试覆盖 JWT encode/decode

### bcrypt < 5.0 版本锁定

**现象**：bcrypt 5.0+ 默认禁止 >72 字节密码，长密码验证失败
**原因**：bcrypt 5.0+ 的默认 truncation 策略变更
**修复方式**：锁定 `bcrypt<5.0` 版本
**预防措施**：密码哈希测试覆盖边界长度

### SQLite 内存 DB 测试需 StaticPool

**现象**：pytest 中不同测试函数看到不同的数据库
**原因**：普通 `sqlite://` 每个连接是独立空 DB
**修复方式**：测试 DB 使用 `StaticPool` 确保单连接共享
**预防措施**：conftest.py 中固定使用 StaticPool

### courses_extended_fixed.py 不可直接 pop

**现象**：`init_phase3_6_data` 调用后，后续调用获取不到数据
**原因**：Python 模块级列表被 `pop()` 破坏，多次 import 共享同一对象
**修复方式**：使用 `copy.deepcopy()` 防止修改模块级数据
**预防措施**：数据加载函数不应修改入参

### Redis 缓存需手动清理

**现象**：修改种子数据后前端仍显示旧数据
**原因**：Redis 缓存未自动失效
**修复方式**：`redis-cli FLUSHDB` 或重启服务（lifespan 中有自动清理）
**预防措施**：修改种子数据后验证缓存已清理

---

## 环境怪癖

| 怪癖 | 影响 | 处理方式 |
|------|------|---------|
| Docker 不可用 | 沙盒运行在 subprocess fallback 模式，Phase 3+ 需要 4核8G+ | 生产环境升级服务器配置 |
| venv 在 `/tmp/ailp-venv` | 系统重启后 venv 可能丢失 | 重建：`python3.11 -m venv /tmp/ailp-venv` |
| 静态文件由后端直接服务 | 前端部署时需确认 `SERVE_STATIC=True` | 生产环境建议用 nginx 反向代理静态文件 |
| GitHub push 网络不稳定 | HTTPS 连接间歇性超时 | 使用 `gh auth setup-git` + 重试 |

---

## 工具链注意事项

| 工具 | 版本 | 注意事项 |
|------|------|---------|
| Python | 3.11 | venv 路径 `/tmp/ailp-venv` |
| FastAPI | — | `SERVE_STATIC=True` 时由 uvicorn 直接服务 |
| SQLite | — | 生产环境迁移至 PostgreSQL（Schema 兼容） |
| pytest | — | 契约测试 `test_data_contract.py` 为 CI 门禁 |
| Playwright | — | 前端冒烟测试 `smoke.spec.js`，E2E 走 CI |

---

## 更新规则

- 每发现一个新陷阱 → 添加到本文档
- 每修复一个陷阱 → 更新状态（✓ 已修复）
- post-commit hook 自动检测本次 commit 是否包含 fix/修复/ bug 关键词 → 提示更新 QUIRKS.md
