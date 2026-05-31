# Design: 公开能力主页

> 版本：V1.0
> 日期：2026-05-23
> 作者：Architect Agent
> 前置 Spec：`/docs/changes/001-public-profile/spec.md`
>
> 本文档定义"怎么实现"Spec 中描述的系统行为。

---

## 技术方案探索（Brainstorming）

### 方案 A: 独立 UserProfile 表

- **怎么做**：新增 `user_profiles` 表，1:1 关联 `users`，存储公开主页总开关（`is_public`）和四个维度的可见性布尔字段（`show_basic_info`、`show_skill_radar`、`show_labs`、`show_certificates`）。同时存储 `display_name` 和 `bio`（一句话简介），这些字段在 User 模型中尚不存在。User 表不做任何修改。
- **优点**：
  - 职责分离：隐私/展示设置与认证/身份数据解耦，符合 Constitution 1.1 分层原则
  - 扩展性好：未来增加新维度（如"项目经历"）只需加列，不污染 User 表
  - 零风险：不动 User 表，不影响现有注册/登录/Auth 逻辑
  - 可选字段天然适配：用户从未配置 = 表中无记录 = BR1 隐私默认隐藏自动满足
- **缺点/风险**：
  - 多一张表，查询公开主页时需要 JOIN（但 1:1 JOIN 性能无问题）
  - 需要处理 UserProfile 记录不存在的情况（等同于未开启主页）
- **与 Constitution 是否冲突**：无冲突。符合 1.1 分层（Model 层职责清晰）、1.3 数据迁移（Alembic 管理）、2.3 数据契约（新表独立，不影响现有契约断言）。

### 方案 B: 复用 User 表 + JSON 字段

- **怎么做**：在 `users` 表新增 `privacy_settings` JSON 列，存储 `{"is_public": false, "show_basic_info": false, "show_skill_radar": false, "show_labs": false, "show_certificates": false}`。同时在 User 表新增 `display_name` 和 `bio` 列。
- **优点**：
  - 无 JOIN，查询简单：一个 User 对象即可拿到全部数据
  - 实现最快：一次迁移，无需新增 Service/Model
- **缺点/风险**：
  - 违反 SRP：User 表承担认证+展示双重职责，未来隐私维度膨胀时 JSON 越来越臃肿
  - JSON 字段无 Schema 约束：Pydantic 校验在 API 层，但数据库层可写入任意结构，数据一致性靠应用层保证
  - 修改 User 表有连锁风险：影响 UserResponse Schema → 影响前端所有消费 User 的组件 → Constitution 1.2 Schema 是唯一真相源，修改需同步前端
  - 与现有 `_assert_data_contract` 断言耦合：User 表结构变更可能影响启动校验
  - SQLite 的 JSON 查询能力弱：无法建索引（PostgreSQL 可用 GIN，但当前开发用 SQLite）
- **与 Constitution 是否冲突**：存在风险。1.2 要求 Schema 是唯一真相源，JSON 内部字段不受 Pydantic Schema 强约束；2.3 数据契约断言可能需要更新；1.1 分层原则暗示模型职责应清晰。

### 推荐方案与理由

**推荐方案 A（独立 UserProfile 表）**。

关键 trade-off：多一张表的 JOIN 开销 vs. 零风险的隔离性。在 SQLite/PostgreSQL 环境下，1:1 JOIN 的性能完全可接受（主键关联，微秒级）。而方案 B 修改 User 表带来的连锁风险（Schema 同步、契约断言、前端消费）是实质性的。

方案 A 还天然实现了 BR1（隐私默认隐藏）：UserProfile 记录不存在 = 未开启。无需在 User 模型中设默认值，也无需在迁移中回填现有用户数据。

---

## 接口定义

### 1. 获取公开主页数据（匿名可访问）

```
Method:  GET
Path:    /api/v1/profile/{username}
Auth:    public（无需登录）

Request:
  - username: str, path parameter

Response (200):
  {
    "username": "zhangsan",
    "display_name": "张三",             // null if show_basic_info=false
    "bio": "专注 CV 方向的 AI 工程师",  // null if show_basic_info=false
    "avatar_url": "https://...",         // null if show_basic_info=false
    "is_public": true,
    "visibility": {
      "show_basic_info": true,
      "show_skill_radar": true,
      "show_labs": true,
      "show_certificates": true
    },
    "skill_radar": {                     // null if show_skill_radar=false
      "skills": {"python": {"score": 85.0, "label": "Python基础", "trend": "+15"}, ...},
      "overall_score": 45.2,
      "strongest": ["python", "math"],
      "weakest": ["llm", "engineering"]
    },
    "labs": [                            // [] if show_labs=false
      {
        "lab_id": 1,
        "lab_title": "Python 基础练习",
        "course_title": "Python基础",
        "score": 95.0,
        "completed_at": "2026-05-01T10:30:00Z"
      }
    ],
    "labs_total": 8,
    "certificates": [                    // [] if show_certificates=false
      {
        "cert_id": "AI-5-1-20260501",
        "course_title": "Python基础",
        "level": "beginner",
        "level_label": "入门认证",
        "issue_date": "2026-05-01T00:00:00Z",
        "verify_url": "/api/v1/certificates/verify/AI-5-1-20260501"
      }
    ]
  }

Error Responses:
  - 404: {"detail": "该用户不存在"}     — 用户名不存在或用户已删除 (AC6, BR9)
  - 403: {"detail": "该用户尚未公开能力主页"} — 用户存在但未开启公开主页 (AC7, BR1)
```

### 2. 获取当前用户的公开主页设置（需登录）

```
Method:  GET
Path:    /api/v1/profile/me/settings
Auth:    required

Request: 无额外参数

Response (200):
  {
    "is_public": false,
    "show_basic_info": false,
    "show_skill_radar": false,
    "show_labs": false,
    "show_certificates": false,
    "profile_url": "ailp.com/p/zhangsan",
    "display_name": "张三",
    "bio": "专注 CV 方向的 AI 工程师",
    "avatar_url": "https://..."
  }

Error Responses:
  - 401: 未提供认证凭证
```

### 3. 更新公开主页设置（需登录）

```
Method:  PUT
Path:    /api/v1/profile/me/settings
Auth:    required

Request:
  {
    "is_public": true,                   // optional, bool
    "show_basic_info": true,             // optional, bool
    "show_skill_radar": true,            // optional, bool
    "show_labs": true,                   // optional, bool
    "show_certificates": true,           // optional, bool
    "display_name": "张三",              // optional, str, max 50 chars
    "bio": "专注 CV 方向的 AI 工程师"     // optional, str, max 200 chars
  }

Response (200):
  {
    "is_public": true,
    "show_basic_info": true,
    "show_skill_radar": true,
    "show_labs": true,
    "show_certificates": true,
    "profile_url": "ailp.com/p/zhangsan",
    "display_name": "张三",
    "bio": "专注 CV 方向的 AI 工程师",
    "avatar_url": "https://..."
  }

Error Responses:
  - 400: {"detail": "开启公开主页时，所有维度默认设为可见"} — is_public 从 false→true 时自动设置 (BR5)
  - 401: 未提供认证凭证
  - 422: Pydantic 校验失败（字段类型/长度）
```

**关键业务逻辑（BR5 实现）**：
- 当 `is_public` 从 `false` 变为 `true` 时，Service 层自动将四个维度全部置为 `true`，无论请求体中是否传了维度字段。
- 当 `is_public` 从 `true` 变为 `false` 时（关闭主页），维度设置保留不动——下次重新开启时再次全部置 `true`。
- 单独修改维度开关不影响 `is_public` 状态。

### 4. 一键操作（需登录）

```
Method:  POST
Path:    /api/v1/profile/me/settings/batch
Auth:    required

Request:
  {
    "action": "show_all" | "hide_all"
  }

Response (200):
  {
    "is_public": true,
    "show_basic_info": true/false,
    "show_skill_radar": true/false,
    "show_labs": true/false,
    "show_certificates": true/false,
    "profile_url": "ailp.com/p/zhangsan",
    "display_name": "张三",
    "bio": "...",
    "avatar_url": "https://..."
  }

Error Responses:
  - 400: {"detail": "主页未开启，无法调整可见性"}
  - 401: 未提供认证凭证
```

---

## 数据模型

```python
# models/user_profile.py (new file, imported in models/__init__.py)

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models import Base, _utcnow


class UserProfile(Base):
    """公开能力主页设置 — 每个用户最多一条记录（1:1 with users）。
    
    记录不存在 = 用户从未配置公开主页 = BR1 隐私默认隐藏。
    """

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # 主页总开关
    is_public = Column(Boolean, default=False, nullable=False)
    
    # 维度可见性（独立控制，BR4）
    show_basic_info = Column(Boolean, default=False, nullable=False)
    show_skill_radar = Column(Boolean, default=False, nullable=False)
    show_labs = Column(Boolean, default=False, nullable=False)
    show_certificates = Column(Boolean, default=False, nullable=False)
    
    # 展示信息（可独立于 User 表修改，不影响认证数据）
    display_name = Column(String(50), nullable=True)   # 昵称，null 时回退到 username
    bio = Column(String(200), nullable=True)            # 一句话简介
    
    timestamps
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    user = relationship("User", backref="profile")
```

### Schema 定义（唯一真相源，Constitution 1.2）

```python
# schemas/profile.py (new file)

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Public profile page response ──────────────────────────────────────────

class ProfileLabItem(BaseModel):
    """Single lab entry on public profile."""
    lab_id: int
    lab_title: str
    course_title: str
    score: float
    completed_at: Optional[datetime] = None


class ProfileCertificateItem(BaseModel):
    """Single certificate entry on public profile."""
    cert_id: str
    course_title: str
    level: str
    level_label: str
    issue_date: datetime
    verify_url: str


class ProfileVisibility(BaseModel):
    """Visibility flags for profile modules."""
    show_basic_info: bool
    show_skill_radar: bool
    show_labs: bool
    show_certificates: bool


class PublicProfileResponse(BaseModel):
    """Response for GET /api/v1/profile/{username} — public view."""
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_public: bool
    visibility: ProfileVisibility
    skill_radar: Optional[dict] = None   # SkillRadarResponse subset, null if hidden
    labs: Optional[list[ProfileLabItem]] = None
    labs_total: Optional[int] = None
    certificates: Optional[list[ProfileCertificateItem]] = None


# ── Settings (authenticated user) ─────────────────────────────────────────

class ProfileSettingsResponse(BaseModel):
    """Response for GET/PUT /api/v1/profile/me/settings."""
    is_public: bool = False
    show_basic_info: bool = False
    show_skill_radar: bool = False
    show_labs: bool = False
    show_certificates: bool = False
    profile_url: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfileSettingsUpdate(BaseModel):
    """Request body for PUT /api/v1/profile/me/settings."""
    is_public: Optional[bool] = None
    show_basic_info: Optional[bool] = None
    show_skill_radar: Optional[bool] = None
    show_labs: Optional[bool] = None
    show_certificates: Optional[bool] = None
    display_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=200)

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) == 0:
            return None  # empty string → null
        return v


class ProfileBatchAction(BaseModel):
    """Request body for POST /api/v1/profile/me/settings/batch."""
    action: str  # "show_all" | "hide_all"

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ("show_all", "hide_all"):
            raise ValueError("action must be 'show_all' or 'hide_all'")
        return v
```

### 数据库迁移

```
Alembic revision: 001_add_user_profiles
新增表: user_profiles
新增列:
  - id (INTEGER, PK, AUTOINCREMENT)
  - user_id (INTEGER, FK→users.id, UNIQUE, NOT NULL)
  - is_public (BOOLEAN, DEFAULT 0, NOT NULL)
  - show_basic_info (BOOLEAN, DEFAULT 0, NOT NULL)
  - show_skill_radar (BOOLEAN, DEFAULT 0, NOT NULL)
  - show_labs (BOOLEAN, DEFAULT 0, NOT NULL)
  - show_certificates (BOOLEAN, DEFAULT 0, NOT NULL)
  - display_name (VARCHAR(50), NULLABLE)
  - bio (VARCHAR(200), NULLABLE)
  - created_at (DATETIME)
  - updated_at (DATETIME)

downgrade(): DROP TABLE user_profiles
无需回填：现有用户无记录 = 未开启主页 (BR1)
```

---

## 技术选型

| 决策点 | 选择 | 理由 |
|-------|------|------|
| 隐私设置存储 | 独立 user_profiles 表 | 方案 A 的结论：职责分离、零风险、扩展性好 |
| 隐私过滤执行层 | Service 层 | Constitution 3.1：不可信任前端。后端根据 visibility 标志裁剪响应字段，前端只负责渲染 |
| 技能雷达图前端渲染 | recharts（RadarChart） | 轻量 React 图表库，与 Vite + React 18 兼容，支持响应式。已在 npm 生态成熟 |
| 公开主页路由 | `/p/:username` (SPA route) | PRD 要求的 URL 格式，与现有 hash 路由共存。公开主页用 history 模式以支持 OG 标签 |
| SPA fallback 策略 | FastAPI 端 `/p/{username}` 返回 index.html | 使 OG meta 标签可被社交平台爬虫读取（服务端渲染 meta，客户端 hydrate） |
| 认证列表数据源 | CertificateService + Course 数据 | 当前证书为动态生成（无持久化表），需从 LabSubmission + LearningProgress 反推已完成课程 |
| 实验列表数据源 | LabSubmission + Lab + Course JOIN | 用户已通过的实验提交，取每个 lab 最高分，关联课程名称 |

---

## 关键流程

### 1. 访问者查看公开主页

```
访问者 GET /p/zhangsan
  │
  ├─ FastAPI 路由匹配 → 返回 index.html（含动态 OG meta 标签）
  │   └─ 服务端预查询 UserProfile + User → 注入 OG 标签到 HTML 模板
  │
  └─ React SPA 加载 → 前端路由匹配 /p/:username
      │
      └─ GET /api/v1/profile/zhangsan
          │
          ├─ ProfileService.get_public_profile(username)
          │   ├─ 1. 查 User by username → 不存在 → 404 (AC6)
          │   ├─ 2. 查 UserProfile by user_id → 不存在 → 403 (AC7)
          │   ├─ 3. 检查 is_public → false → 403 (AC7, AC11)
          │   ├─ 4. 根据 visibility 裁剪响应字段：
          │   │     show_basic_info=false → display_name/bio/avatar_url 置 null
          │   │     show_skill_radar=false → skill_radar 置 null
          │   │     show_labs=false → labs 置 null, labs_total 置 null
          │   │     show_certificates=false → certificates 置 null
          │   ├─ 5. 聚合数据：
          │   │     skill_radar ← SkillRadarService.get_skill_radar()
          │   │     labs ← LabSubmission JOIN Lab JOIN Course (passed only, best score per lab)
          │   │     certificates ← 从 completed courses 反推 (CertificateService)
          │   └─ 6. 返回 PublicProfileResponse
          │
          └─ React 组件渲染：
              visibility.show_basic_info → 渲染头像+昵称+简介
              visibility.show_skill_radar → 渲染雷达图
              visibility.show_labs → 渲染实验列表
              visibility.show_certificates → 渲染认证列表
              全部隐藏 → 仅渲染用户名 + AILP 品牌标识 (AC5)
```

### 2. 用户首次开启主页（AC3）

```
用户点击「一键开启」
  │
  └─ PUT /api/v1/profile/me/settings { is_public: true }
      │
      ├─ ProfileService.update_settings(user_id, data)
      │   ├─ 1. 查 UserProfile → 不存在 → 创建新记录
      │   ├─ 2. is_public 从 false→true：
      │   │     自动设置 show_basic_info/show_skill_radar/show_labs/show_certificates = true (BR5)
      │   ├─ 3. 如果 display_name 为 null → 默认取 user.username
      │   ├─ 4. 写入 DB → commit
      │   └─ 5. 记录埋点：profile_enabled
      │
      └─ 前端显示成功提示 + profile_url + 复制链接按钮
```

### 3. 隐私过滤核心逻辑（Service 层）

```python
# services/profile_service.py — 关键伪代码

def _apply_visibility(response: dict, profile: UserProfile) -> dict:
    """根据 visibility 裁剪响应字段——在 Service 层执行，不可依赖前端隐藏。"""
    if not profile.show_basic_info:
        response["display_name"] = None
        response["bio"] = None
        response["avatar_url"] = None
    if not profile.show_skill_radar:
        response["skill_radar"] = None
    if not profile.show_labs:
        response["labs"] = None
        response["labs_total"] = None
    if not profile.show_certificates:
        response["certificates"] = None
    return response
```

### 4. 实验列表聚合

```
LabSubmission (user_id=X, passed=True)
  JOIN Lab → lab_title, chapter_id
  JOIN Chapter → course_id
  JOIN Course → course_title
  
GROUP BY lab_id → 取最高 score 的那条
ORDER BY completed_at DESC

前端默认展示前 5 条，提供「展开全部」按钮 (AC9)
```

### 5. 认证列表聚合

```
已完成课程 = LearningProgress (user_id=X, status='completed')
  GROUP BY chapter.course_id → HAVING COUNT = total_chapters_per_course
  JOIN Course → course_title, level

对每个已完成课程：
  cert_id = "AI-{course_id}-{user_id}-{date}"
  level_label = 根据课程 level 映射
  verify_url = "/api/v1/certificates/verify/{cert_id}"
```

---

## 前端实现要点

| 页面/组件 | 路由 | 关键交互 | 备注 |
|----------|------|---------|------|
| PublicProfilePage | `/p/:username` | 加载公开主页数据，渲染四个模块 | 无需登录，SSR OG 标签 |
| ProfileSettingsPage | `/#/profile/settings`（hash 模式，需登录） | 总开关、维度开关、预览、复制链接 | 复用现有 hash 路由 |
| ProfileRadarChart | 嵌入 PublicProfilePage | recharts RadarChart，移动端降级为条形图 | 响应式：width<768px 用 BarChart |
| ProfileLabList | 嵌入 PublicProfilePage | 默认 5 条折叠，展开全部 | 虚拟滚动优化 200+ 条 |
| ProfileCertificateList | 嵌入 PublicProfilePage | 全量展示，无折叠 | 认证数量通常 ≤ 50 |
| ProfileOnboarding | 嵌入 ProfileSettingsPage | 未开启时显示引导卡片 + 一键开启 | AC3 |
| CopyLinkButton | 嵌入 ProfileSettingsPage | navigator.clipboard API + 降级提示 | AC4 |

### SPA 路由集成

现有前端使用 hash 模式路由（`/#/courses`），公开主页使用 history 模式（`/p/username`）以支持 OG 标签和社交分享。两者共存：

1. **FastAPI 端**：新增 `GET /p/{full_path:path}` 路由，返回 `index.html`（类似现有 `/v2/{full_path:path}` 的 SPA fallback）
2. **前端**：在 `main.js` 路由表中新增 `/p/:username` 路由，匹配后加载 `PublicProfilePage` 组件
3. **OG 标签**：FastAPI 端在返回 `index.html` 前预查询用户数据，动态替换 `<meta property="og:*">` 标签值

### 移动端适配策略

```
宽度 >= 768px：RadarChart (SVG 雷达图)
宽度 < 768px：  水平 BarChart (各维度条形图，label+分数)
```

---

## 安全与审计

| 维度 | 措施 |
|------|------|
| 权限控制 | GET /profile/{username} 公开访问，但 Service 层强制执行 visibility 过滤。GET/PUT /profile/me/settings 需 JWT 认证 |
| 未授权数据不可见 | Service 层 `_apply_visibility()` 裁剪字段，即使前端被篡改也无法获取隐藏数据。is_public=false 时整个 profile 返回 403 (Spec 安全需求) |
| 数据来源防篡改 | 实验列表/认证列表/技能分数均为只读聚合，用户只能控制 show/hide，不可编辑内容 (BR2) |
| 输入校验 | display_name ≤ 50 字符，bio ≤ 200 字符，action ∈ {show_all, hide_all}。Pydantic schema 校验 (Constitution 3.1) |
| 用户名注入 | username 参数经过 SQLAlchemy 参数化查询，无 SQL 注入风险 (Constitution 3.2) |
| OG 标签泄露 | 服务端渲染 OG 标签时同样检查 is_public，未开启主页返回 noindex meta |
| 审计日志 | 关键操作写入 AnalyticsEvent：profile_enabled / profile_disabled / privacy_toggle / profile_view |
| 删除用户 | User.is_active=false 或 User 被删除时，profile 查询返回 404 (BR9) |

---

## 可观测性

| 类型 | 内容 |
|------|------|
| 日志 | profile_view (匿名可触发，记录 username + IP)、profile_settings_update (记录 user_id + 变更字段)、profile_404/403 (记录 username + 原因) |
| 指标 | 公开主页开启率 (is_public=true 的 user_profiles 数 / 活跃用户数)、主页 PV (profile_view 事件计数)、主页加载 P95 延迟 |

---

## 埋点

| 事件名 | 触发时机 | 属性 |
|-------|---------|------|
| profile_view | 匿名/登录用户访问 `/p/{username}` | `target_username`, `is_owner` (是否本人), `referrer` |
| profile_share | 用户点击「复制链接」按钮 | `username`, `share_method` (clipboard) |
| profile_enabled | 用户开启公开主页 (is_public: false→true) | `user_id` |
| profile_disabled | 用户关闭公开主页 (is_public: true→false) | `user_id` |
| privacy_toggle | 用户修改任一维度可见性 | `user_id`, `dimension`, `new_value` |
| profile_preview | 用户点击「预览我的主页」 | `user_id` |
| profile_batch_action | 用户执行一键开启/隐藏 | `user_id`, `action` (show_all/hide_all) |

---

## AC/BR 覆盖矩阵

| AC/BR | 设计覆盖 |
|:---:|------|
| AC1 | GET /profile/{username} + SkillRadarService + LabSubmission 聚合 + CertificateService 聚合 + visibility 全 true |
| AC2 | `_apply_visibility()` 按 visibility 裁剪，隐藏模块对应字段返回 null，前端不渲染 |
| AC3 | PUT /profile/me/settings {is_public: true} → 自动全部置 true + 引导卡片 UI |
| AC4 | 预览按钮 → 新标签页打开 `/p/:username`（与访问者看到完全一致）；CopyLinkButton 组件 |
| AC5 | is_public=true 但所有维度 false → 仅返回 username，前端只渲染用户名 + 品牌标识 |
| AC6 | User 不存在 → 404 + "该用户不存在" |
| AC7 | UserProfile 不存在或 is_public=false → 403 + "该用户尚未公开能力主页" |
| AC8 | 零实验/认证 → 空列表 + 前端空状态提示"暂无实验记录"/"暂无认证记录"；雷达图显示 0 分 |
| AC9 | 实验列表前 5 条 + 展开全部按钮；认证全量展示 |
| AC10 | FastAPI `/p/{username}` 端动态注入 OG meta 标签 |
| AC11 | is_public 改为 false → 访问返回 403，行为同 AC7 |
| AC12 | 无状态 API + SQLite 读并发无锁；技能分数读 user_skill_scores 缓存表 |
| BR1 | UserProfile 记录不存在 = 未开启 = 默认隐藏 |
| BR2 | 数据全部从 LabSubmission/LearningProgress/Course 聚合，用户不可编辑 |
| BR3 | SkillRadarService.get_skill_radar() 实时计算，每次访问取最新 |
| BR4 | 四个 show_* 字段独立布尔值，互不影响 |
| BR5 | is_public false→true 时 Service 层自动全部置 true |
| BR6 | 预览 = 新标签页打开实际主页 URL，所见即所得 |
| BR7 | URL 基于 username 生成，不随状态变化 |
| BR8 | GET /profile/{username} 无需认证 |
| BR9 | User 不存在或 is_active=false → 404 |
| BR10 | certificates[].verify_url 提供跳转链接，target="_blank" |
