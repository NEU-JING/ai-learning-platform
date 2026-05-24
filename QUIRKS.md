# QUIRKS.md — AILP 项目已知陷阱

> 每次踩坑后自动追加。Stop Hook 负责维护。
> 开始任何工作前搜索本文档，避免重复踩坑。

---

## 数据库

### 1. JWT sub 必须是 string
- **现象**：python-jose 按 RFC 7519 要求 sub 是 string，传 int 导致 decode 返回 None
- **修复**：`str(user.id)` 而非 `user.id`
- **发现日期**：2026-05-13

### 2. bcrypt 版本锁定 <5.0
- **现象**：bcrypt 5.0+ 默认禁止 >72 字节密码
- **修复**：`pip install "bcrypt<5.0"`
- **发现日期**：2026-05-13

### 3. SQLite 内存 DB 测试需 StaticPool
- **现象**：普通 `sqlite://` 每个连接是独立空 DB
- **修复**：`create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)`
- **发现日期**：2026-05-13

### 4. courses_extended_fixed.py 不可直接 pop
- **现象**：`init_phase3_6_data` 用 `.pop("chapters")` 会破坏模块级数据
- **修复**：使用 `copy.deepcopy()` 后再 pop
- **发现日期**：2026-05-15

### 5. Phase 3-6 DB 为真相源
- **现象**：种子文件内容可能落后于 DB 中的手动深化数据
- **规则**：`create_only` 行为保护 DB 内容，不覆盖
- **发现日期**：2026-05-15

---

## 缓存

### 6. Redis 缓存需手动清理
- **现象**：修改种子数据后 Redis 缓存仍是旧数据
- **修复**：`redis-cli FLUSHDB` 或在 lifespan 中自动清理
- **注意**：Redis 不可用时 lifespan 不报错，但缓存不生效
- **发现日期**：2026-05-15

---

## API & Schema

### 7. 登录用 email 字段
- **现象**：UserLogin schema 要求 email 字段，不是 username
- **注意**：前端提交的字段名必须是 `email`
- **发现日期**：2026-05-13

### 8. 注册不返回 token
- **现象**：注册接口返回 UserResponse，不包含 token
- **注意**：前端需在注册后走登录流程
- **发现日期**：2026-05-13

### 9. 课程列表返回 PaginatedResponse
- **现象**：响应结构是 `{items, total, page, ...}` 而非数组
- **注意**：前端取 `.items` 获取课程列表
- **发现日期**：2026-05-13

---

## 前端

### 10. React 组件缺 prop → 全页崩溃
- **现象**：组件调用遗漏必传的 array/object prop，.reduce()/.map() 在 undefined 上抛 TypeError
- **修复**：组件内部加 `= []` 默认值，或调用方确保传入 prop
- **发现日期**：2026-05-20

### 11. API 路径硬编码 → 生产 404
- **现象**：前端 data.js 硬编码路径与后端路由不匹配
- **修复**：修改 API 路径时同步 grep 前端引用
- **发现日期**：2026-05-20

### 12. V2 构建硬编码 /v2/assets/ 路径
- **现象**：Vite 构建产物引用 /v2/assets/ 路径，需双 mount
- **修复**：浏览器缓存掩码部署需加 cache-bust 参数
- **发现日期**：2026-05-20

---

## 沙箱

### 13. Docker 不可用需回退 Subprocess
- **现象**：2核4G 服务器 Docker 构建超时
- **修复**：code_executor.py 实现 subprocess 回退模式
- **建议**：升级到 4核8G+80GB 后启用 Docker
- **发现日期**：2026-05-13

---

*最后更新：2026-05-21*
