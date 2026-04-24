# 贡献指南

感谢您对AI学习平台的关注！本文档将帮助您了解如何为项目做出贡献。

## 目录

- [开发环境搭建](#开发环境搭建)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [PR流程](#pr流程)
- [测试要求](#测试要求)

## 开发环境搭建

### 前置要求

- Python 3.9+
- Git
- Docker (用于代码沙箱)
- VS Code (推荐)

### 克隆项目

```bash
cd /root/.openclaw/workspace/projects/ai-learning-platform
```

### 安装依赖

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 安装开发依赖
pip install pytest pytest-asyncio black flake8 mypy
```

### 启动开发服务器

```bash
# 使用启动脚本
./start.sh

# 或手动启动
# 后端
cd backend
python -m uvicorn app.main:app --reload

# 前端
cd frontend
python -m http.server 3000
```

## 代码规范

### Python代码规范

我们使用以下工具保持代码质量：

```bash
# 代码格式化
black backend/app

# 代码检查
flake8 backend/app

# 类型检查
mypy backend/app
```

#### 命名规范

- **模块名**: 小写，下划线分隔 (e.g., `course_service.py`)
- **类名**: 大驼峰 (e.g., `CourseService`)
- **函数名**: 小写，下划线分隔 (e.g., `get_course_by_id`)
- **常量**: 大写，下划线分隔 (e.g., `MAX_UPLOAD_SIZE`)
- **私有成员**: 下划线前缀 (e.g., `_internal_method`)

#### 代码风格

```python
# 正确的示例
def get_user_courses(
    user_id: int,
    include_completed: bool = False,
    limit: int = 10
) -> List[Course]:
    """获取用户的课程列表。
    
    Args:
        user_id: 用户ID
        include_completed: 是否包含已完成的课程
        limit: 返回数量限制
    
    Returns:
        课程列表
    """
    courses = db.query(Course).filter(
        Course.user_id == user_id
    ).limit(limit).all()
    
    if not include_completed:
        courses = [c for c in courses if not c.is_completed]
    
    return courses

# 错误的示例
def getUserCourses(userId,includeCompleted=False,limit=10):
    courses=db.query(Course).filter(Course.user_id==userId).limit(limit).all()
    if not includeCompleted:
        courses=[c for c in courses if not c.is_completed]
    return courses
```

### JavaScript代码规范

```bash
# 代码检查 (需要安装 ESLint)
npx eslint frontend/src
```

#### 命名规范

- **变量/函数**: 小驼峰 (e.g., `getUserData`)
- **类名**: 大驼峰 (e.g., `UserService`)
- **常量**: 大写 (e.g., `API_BASE_URL`)
- **私有方法**: 下划线前缀 (e.g., `_fetchData`)

## 提交规范

### Commit Message格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type

- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更新
- **style**: 代码格式调整
- **refactor**: 重构
- **test**: 测试相关
- **chore**: 构建/工具相关

#### Scope

- `backend`: 后端相关
- `frontend`: 前端相关
- `api`: API相关
- `db`: 数据库相关
- `sandbox`: 沙箱相关
- `docs`: 文档相关

#### 示例

```
feat(api): add discussion forum API

- Add CRUD endpoints for discussions
- Add comment and like functionality
- Add pagination support

Closes #123
```

```
fix(backend): correct CORS configuration

- Remove wildcard from allow_origins
- Add environment variable support

Fixes #456
```

## PR流程

### 1. Fork项目

Fork项目到您的GitHub账号。

### 2. 创建分支

```bash
# 从main分支创建
 git checkout -b feature/your-feature-name

# 或修复分支
 git checkout -b fix/issue-description
```

### 3. 开发和测试

```bash
# 运行测试
pytest backend/tests/

# 代码检查
black backend/app
flake8 backend/app
```

### 4. 提交更改

```bash
git add .
git commit -m "feat(api): add discussion forum API"
```

### 5. 推送到远程

```bash
git push origin feature/your-feature-name
```

### 6. 创建Pull Request

- 填写PR模板
- 关联相关Issue
- 等待代码审查

### PR模板

```markdown
## 描述
简要描述这个PR做了什么。

## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构

## 检查清单
- [ ] 代码通过所有测试
- [ ] 代码符合规范
- [ ] 文档已更新
- [ ] 本地测试通过

## 关联Issue
Fixes #(issue编号)
```

## 测试要求

### 运行测试

```bash
# 所有测试
pytest backend/tests/

# 带覆盖率
pytest --cov=backend/app --cov-report=html

# 特定测试
pytest backend/tests/test_courses.py
```

### 测试覆盖率要求

- 核心功能: >80%
- API路由: >70%
- 工具函数: >60%

### 编写测试

```python
# tests/test_courses.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_courses():
    """测试获取课程列表"""
    response = client.get("/api/v1/courses/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_course_detail():
    """测试获取课程详情"""
    response = client.get("/api/v1/courses/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "title" in data
```

## 项目结构

```
ai-learning-platform/
├── backend/                # FastAPI后端
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── data/          # 课程数据
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # Pydantic模型
│   │   ├── services/      # 业务逻辑
│   │   └── main.py        # 应用入口
│   ├── tests/             # 测试文件
│   └── requirements.txt   # 依赖
├── frontend/              # 前端
│   ├── src/               # 源代码
│   │   ├── core/          # 核心模块
│   │   ├── services/      # API服务
│   │   ├── views/         # 页面组件
│   │   └── main.js        # 应用入口
│   └── spa.html           # SPA入口
├── sandbox/               # 代码沙箱
├── docs/                  # 文档
└── tests/                 # 集成测试
```

## 开发工作流

1. **认领Issue**: 在Issue中留言表示愿意处理
2. **创建分支**: 从main创建feature分支
3. **开发**: 编写代码和测试
4. **自测**: 本地运行所有测试
5. **提交PR**: 创建Pull Request
6. **代码审查**: 等待审查和反馈
7. **合并**: 审查通过后合并到main

## 问题反馈

- **Bug报告**: 使用Bug Report模板
- **功能请求**: 使用Feature Request模板
- **安全问题**: 请直接联系维护者

## 社区准则

- 友善交流，尊重他人
- 接受建设性反馈
- 专注于技术讨论
- 遵守代码规范

感谢您的贡献！
