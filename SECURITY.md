# 安全指南

## 敏感信息保护

### ⚠️ 绝不要提交到代码仓库的内容

- [ ] GitHub/GitLab 个人访问令牌 (PAT)
- [ ] JWT Secret Key
- [ ] 数据库密码
- [ ] API 密钥
- [ ] 私钥文件

### ✅ 正确的配置方式

1. **本地开发**: 使用 `.env` 文件
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的配置
   ```

2. **生产环境**: 使用环境变量
   ```bash
   export SECRET_KEY=$(openssl rand -hex 32)
   export DB_PASSWORD=your_strong_password
   export GITHUB_TOKEN=ghp_xxxxxxxx
   ```

3. **Docker**: 使用环境变量或 secrets
   ```yaml
   # docker-compose.yml
   services:
     backend:
       environment:
         - SECRET_KEY=${SECRET_KEY}
   ```

### 🔐 生成强密钥

```bash
# JWT Secret Key
openssl rand -hex 32

# 密码
openssl rand -base64 32
```

### 🚨 如果意外提交了敏感信息

1. **立即撤销/更换令牌**
   - GitHub: Settings -> Developer settings -> Personal access tokens
   - 删除旧的，生成新的

2. **从 Git 历史中移除**
   ```bash
   # 方式1: 使用 git-filter-repo (推荐)
   git filter-repo --replace-text <(echo 'OLD_TOKEN==>NEW_TOKEN')
   
   # 方式2: 使用 BFG
   bfg --replace-text tokens.txt
   
   # 强制推送 (谨慎！)
   git push --force
   ```

3. **通知相关人员**

## CORS 配置

### 开发环境
允许所有来源:
```bash
CORS_ORIGINS=*
```

### 生产环境
只允许特定域名:
```bash
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## 代码沙箱安全

沙箱已配置以下安全限制:
- ✅ 禁止访问文件系统
- ✅ 禁止网络访问
- ✅ 限制内存使用 (256MB)
- ✅ 限制 CPU 使用 (0.5核)
- ✅ 超时限制 (30秒)
- ✅ 危险代码静态检测

## 密码策略

用户密码必须满足:
- 至少8个字符
- 包含字母和数字
- 支持中文用户名

## 报告安全问题

如果发现安全漏洞，请立即联系管理员。
