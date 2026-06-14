# Phase 2 部署验证报告

> 后端: http://localhost:8000  
> 前端: http://localhost:8000/ (旧版) / http://localhost:8000/v2/ (新版)

---

## ✅ 已验证通过的 API

| 端点 | 状态 | 说明 |
|------|:----:|------|
| `GET /health` | ✅ 200 | 服务健康检查 |
| `GET /api/v1/courses/` | ✅ 200 | 6 门课程（6-Phase 体系） |
| `GET /api/v1/courses/paths` | ✅ 200 | 4 条学习路径（AI专家/工程师/应用者/管理者） |
| `GET /api/v1/courses/{id}` | ✅ 200 | 课程详情 |
| `GET /api/v1/courses/{id}/chapters` | ✅ 200 | 课程章节 |
| `POST /api/v1/auth/register` | ✅ 201 | 用户注册 |
| `POST /api/v1/auth/login` | ✅ 200 | 用户登录（JWT token） |
| `GET /api/v1/certificates/{cert_number}` | ✅ 路由注册 | 证书详情查询（M2） |

## ⚠️ 需注意

| 端点 | 结果 | 原因 |
|------|:----:|------|
| `POST /api/v1/certifications/apply` | 404 | ⚡ 数据库无 Certification Level 种子数据 |
| `POST /api/v1/tutor/code-review` | 超时 | ⚡ 需要真实 LLM API key（Ark/OpenRouter） |
| `POST /api/v1/tutor/sessions` | 同上 | ⚡ 需要真实 LLM API key |

---

## 验证方式

老师可直接使用浏览器访问：

1. **首页**: http://localhost:8000/
2. **V2 前端**: http://localhost:8000/v2/
3. **API 测试示例**:
   ```bash
   # 查看课程列表
   curl http://localhost:8000/api/v1/courses/ | python3 -m json.tool
   
   # 查看学习路径
   curl http://localhost:8000/api/v1/courses/paths | python3 -m json.tool
   ```
