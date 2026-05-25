# Tasks: 公开能力主页

> 版本：V1.0
> 日期：2026-05-24
> 前置 Design：`/docs/changes/001-public-profile/design.md`
> 预估总工时：26 小时

---

## 拆分原则

- **按业务场景拆分**，不按技术层次拆分
- **每个 Task 完成 → 可独立上线运行**（最小可部署单元）
- Task 按照依赖关系排序

---

## 依赖关系图

```
Task-1 (数据模型+设置API) ──→ Task-2 (公开主页数据API) ──→ Task-3 (公开主页前端) ──→ Task-5 (集成验证)
          │                                                   ↑                       ↑
          └──────────────────────────────────→ Task-4 (设置前端) ─────────────────────┘
```

---

## 任务列表

### Task-1: 公开主页数据模型与设置 API

- **估时**：6 小时
- **依赖**：无
- **业务场景**：AC3（首次开启）、AC4（调整可见性·后端）、AC5（一键隐藏·后端）、AC11（关闭主页·后端）
- **描述**：建立 UserProfile 数据模型和迁移，实现用户公开主页的开关与可见性设置的完整 CRUD API。包含 BR5 核心逻辑：is_public 从 false→true 时自动全部置 true。部署后用户可通过 API 配置主页设置。
- **涉及文件**：
  - `backend/app/models/user_profile.py`（新增）
  - `backend/app/schemas/profile.py`（新增）
  - `backend/app/services/profile_service.py`（新增）
  - `backend/app/api/v1/profile.py`（新增）
  - `backend/app/models/__init__.py`（修改：导入 UserProfile）
  - `backend/app/api/v1/__init__.py`（修改：注册 profile router）
  - `backend/alembic/versions/001_add_user_profiles.py`（新增）
- **Done 条件**：
  - [ ] Alembic 迁移成功，`user_profiles` 表创建，现有数据不受影响
  - [ ] TDD：先写测试后写实现，覆盖以下场景——
    - 首次开启主页（无 UserProfile → 创建，is_public=true，四维度自动全 true）
    - 关闭主页（is_public true→false，维度设置保留不动）
    - 重新开启主页（is_public 再次 true，四维度再次全 true）
    - 单独修改维度开关不影响 is_public
    - 一键开启全部 / 一键隐藏全部（show_all / hide_all）
    - 未开启主页时执行 batch 操作返回 400
    - display_name 空字符串→null、bio 超 200 字符校验
  - [ ] GET/PUT /api/v1/profile/me/settings、POST /api/v1/profile/me/settings/batch 三个端点可用
  - [ ] 契约测试通过（Schema 字段名与 Design 定义一致）
  - [ ] 可独立部署（API 可通过 curl 测试完整流程）

---

### Task-2: 公开主页数据 API（聚合 + 隐私过滤）

- **估时**：7 小时
- **依赖**：Task-1
- **业务场景**：AC1（全部维度可见）、AC2（部分维度隐藏）、AC6（用户不存在）、AC7（未开启主页）、AC8（零实验零认证）、AC12（并发访问）
- **描述**：实现匿名可访问的 GET /api/v1/profile/{username}，聚合用户技能雷达、实验列表、认证列表，并在 Service 层强制执行隐私过滤（_apply_visibility）。部署后任何人可通过 API 查看已开启的公开主页数据。
- **涉及文件**：
  - `backend/app/services/profile_service.py`（修改：新增 get_public_profile、_apply_visibility）
  - `backend/app/schemas/profile.py`（修改：新增 PublicProfileResponse、ProfileLabItem、ProfileCertificateItem、ProfileVisibility）
  - `backend/app/api/v1/profile.py`（修改：新增 GET /profile/{username}）
  - `backend/app/services/skill_radar_service.py`（修改或调用：获取技能雷达数据）
  - `backend/app/services/certificate_service.py`（修改或调用：认证列表聚合）
- **Done 条件**：
  - [ ] TDD：先写测试后写实现，覆盖以下场景——
    - 全部维度可见：返回完整数据（display_name、bio、avatar_url、skill_radar、labs、certificates）
    - 部分维度隐藏：隐藏字段返回 null/[]，其他字段正常
    - 用户不存在：返回 404 + "该用户不存在"
    - UserProfile 不存在（从未配置）：返回 403 + "该用户尚未公开能力主页"
    - is_public=false：返回 403，与 AC7 一致
    - 零实验零认证：labs=[]、certificates=[]，雷达图返回 0 分
    - 已删除/禁用用户（is_active=false）：返回 404 (BR9)
    - 大量实验数据（200+）：响应时间 < 3s
  - [ ] `_apply_visibility` 在 Service 层强制执行，不依赖前端隐藏
  - [ ] 实验列表按 completed_at 倒序，取每个 lab 最高分
  - [ ] 认证列表从 LearningProgress 反推已完成课程，生成 cert_id 和 verify_url
  - [ ] 契约测试通过（PublicProfileResponse 字段与 Design 一致）
  - [ ] 可独立部署（curl GET /api/v1/profile/{username} 返回正确数据或错误）

---

### Task-3: 公开主页前端页面

- **估时**：7 小时
- **依赖**：Task-2
- **业务场景**：AC1（全部维度可见页面）、AC2（部分维度隐藏页面）、AC5（所有维度隐藏页面）、AC8（空状态展示）、AC9（大量数据折叠/展开）、AC10（OG 富媒体卡片）
- **描述**：实现公开主页前端页面 `/p/:username`，包含 SPA 路由集成、技能雷达图（recharts）、实验列表（折叠/展开）、认证列表、移动端适配、服务端 OG 标签注入。部署后访问者可在浏览器中查看公开主页。
- **涉及文件**：
  - `frontend/src/pages/PublicProfilePage.jsx`（新增）
  - `frontend/src/components/ProfileRadarChart.jsx`（新增）
  - `frontend/src/components/ProfileLabList.jsx`（新增）
  - `frontend/src/components/ProfileCertificateList.jsx`（新增）
  - `frontend/src/main.jsx`（修改：新增 /p/:username 路由）
  - `backend/app/api/v1/spa.py` 或 `backend/app/main.py`（修改：新增 /p/{full_path:path} SPA fallback + OG 标签注入）
  - `frontend/src/api/profile.js`（新增：调用 /api/v1/profile/{username}）
- **Done 条件**：
  - [ ] 访问 `/p/{username}` 正确渲染公开主页，无需登录
  - [ ] 技能雷达图：桌面端 RadarChart，移动端（<768px）降级为水平 BarChart
  - [ ] 实验列表：默认展示前 5 条 + "展开全部（N 个实验）" 按钮，展开后按时间倒序
  - [ ] 认证列表：全量展示，verify_url 链接 target="_blank"
  - [ ] 隐藏维度不渲染（不出现空白占位），所有维度隐藏时仅显示用户名 + AILP 品牌标识
  - [ ] 零数据空状态："暂无实验记录" / "暂无认证记录"（中性口吻）
  - [ ] 页面底部 "✅ 数据由 AILP 平台验证" + "在 AILP 上学习 AI 课程" 链接
  - [ ] OG 标签：FastAPI 端预查询用户数据，动态注入 og:title、og:description、og:image
  - [ ] 未开启主页/不存在用户：前端根据 403/404 渲染对应提示页
  - [ ] Playwright 冒烟测试通过：页面加载、雷达图渲染、列表折叠/展开
  - [ ] 可独立部署（浏览器访问 /p/{username} 完整可用）

---

### Task-4: 公开主页设置前端页面

- **估时**：4 小时
- **依赖**：Task-1, Task-3
- **业务场景**：AC3（首次开启引导）、AC4（预览+复制链接）、AC11（关闭主页前端）
- **描述**：实现公开主页设置页面（`/#/profile/settings`），包含引导卡片（未开启时）、总开关、四维度独立开关、一键开启/隐藏、预览按钮（新标签页打开实际主页）、复制链接按钮。部署后用户可通过 UI 完整管理公开主页。
- **涉及文件**：
  - `frontend/src/pages/ProfileSettingsPage.jsx`（新增）
  - `frontend/src/components/ProfileOnboarding.jsx`（新增）
  - `frontend/src/components/CopyLinkButton.jsx`（新增）
  - `frontend/src/main.jsx`（修改：新增 /profile/settings hash 路由）
  - `frontend/src/api/profile.js`（修改：新增 settings CRUD 调用）
  - `frontend/src/components/UserCenter.jsx` 或对应导航组件（修改：新增"我的公开主页"入口）
- **Done 条件**：
  - [ ] 未开启时显示引导卡片 + "开启你的能力主页，让雇主发现你" + 一键开启按钮
  - [ ] 点击一键开启后：is_public=true，四维度全开，显示主页链接 + 复制按钮
  - [ ] 已开启时显示：总开关、主页链接、四维度独立开关、预览按钮
  - [ ] 一键开启全部 / 一键隐藏全部按钮正常工作
  - [ ] 关闭主页时提示 "你的能力主页已关闭，他人将无法访问"
  - [ ] 预览按钮：新标签页打开 `/p/{username}`（所见即所得，与 Task-3 页面完全一致）
  - [ ] 复制链接：navigator.clipboard API + 降级提示 "复制失败，请手动复制链接"
  - [ ] 个人中心导航新增"我的公开主页"入口
  - [ ] Playwright 冒烟测试通过：设置页渲染、开关切换、复制链接
  - [ ] 可独立部署（登录用户可完整操作设置页）

---

### Task-5: 集成测试与 AC 验证

- **估时**：2 小时
- **依赖**：Task-3, Task-4
- **业务场景**：全场景集成验证（AC1-AC12）
- **描述**：端到端集成测试，确保所有 Spec AC 场景在前端+后端联调下全部通过。补充 AC 覆盖矩阵，执行 post-coding-review。
- **涉及文件**：
  - `backend/tests/test_profile_integration.py`（新增：后端集成测试）
  - `frontend/tests/profile.spec.js`（新增：Playwright E2E 测试）
  - `docs/changes/001-public-profile/ac-coverage.md`（新增：AC 覆盖矩阵）
- **Done 条件**：
  - [ ] AC1-AC12 每个场景有对应测试用例且全部通过
  - [ ] 集成测试覆盖：开启→访问→调整可见性→预览→分享→关闭→访问失效 完整链路
  - [ ] 安全测试：未开启主页的用户数据不可通过 API 探测获取
  - [ ] 前端冒烟测试通过（Playwright：公开主页渲染、设置页操作）
  - [ ] post-coding-review 三阶段通过
  - [ ] 可部署到生产
