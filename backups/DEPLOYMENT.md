# AI学习平台 - 部署指南

## 目录
- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [生产环境部署](#生产环境部署)
- [配置说明](#配置说明)
- [故障排查](#故障排查)

## 环境要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **磁盘**: 20GB 可用空间
- **系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### 推荐配置
- **CPU**: 4核心+
- **内存**: 8GB RAM+
- **磁盘**: 50GB+ SSD
- **网络**: 稳定的互联网连接

## 快速部署

### 1. 克隆代码
```bash
git clone <your-repo-url>
cd ai-learning-platform
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env
```

必需的环境变量：
```bash
# 数据库配置
DB_NAME=ailearning
DB_USER=ailearning
DB_PASSWORD=your-secure-password

# Redis配置
REDIS_PASSWORD=your-secure-password

# JWT密钥（生产环境必须修改！）
SECRET_KEY=your-very-secret-key-at-least-32-characters-long

# 环境设置
ENVIRONMENT=production
```

### 3. 启动服务
```bash
# 使用生产环境配置
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. 验证部署
```bash
# 测试API
curl http://localhost:8000/

# 测试前端
open http://localhost
```

## 生产环境部署

### 1. 服务器准备

#### 安装Docker和Docker Compose
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 配置防火墙
```bash
# 开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # API（如果直接暴露）
sudo ufw enable
```

### 2. SSL证书配置

#### 使用Let's Encrypt
```bash
# 安装Certbot
sudo apt install certbot

# 申请证书
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/key.pem
sudo chmod 600 ./ssl/*.pem
```

### 3. 配置Nginx反向代理

编辑 `nginx.conf`：
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # 前端服务
    server {
        listen 80;
        server_name your-domain.com;
        
        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL证书
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # 前端静态文件
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # API反向代理
        location /api/ {
            proxy_pass http://backend:8000/api/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        }
    }
}
```

### 4. 数据库备份策略

创建备份脚本 `scripts/backup.sh`：
```bash
#!/bin/bash

# 数据库备份脚本
BACKUP_DIR="/backups/ailearning"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml exec -T db pg_dump -U ailearning ailearning > $BACKUP_FILE

# 压缩备份
gzip $BACKUP_FILE

# 删除7天前的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

添加定时任务：
```bash
# 编辑crontab
crontab -e

# 添加每日凌晨2点备份
0 2 * * * /opt/ai-learning-platform/scripts/backup.sh >> /var/log/ailearning_backup.log 2>&1
```

### 5. 监控配置

访问监控面板：
- Prometheus: http://your-server-ip:9090
- Grafana: http://your-server-ip:3000 (默认账号: admin/admin)

## 配置说明

### 环境变量详解

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `DB_NAME` | 数据库名称 | ailearning | 是 |
| `DB_USER` | 数据库用户 | ailearning | 是 |
| `DB_PASSWORD` | 数据库密码 | - | 是 |
| `REDIS_PASSWORD` | Redis密码 | - | 是 |
| `SECRET_KEY` | JWT密钥 | - | 是 |
| `ENVIRONMENT` | 环境标识 | production | 是 |
| `LOG_LEVEL` | 日志级别 | INFO | 否 |
| `GRAFANA_PASSWORD` | Grafana管理员密码 | admin | 是 |

### 资源限制配置

修改 `docker-compose.prod.yml` 中的 `deploy.resources` 部分：

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # CPU限制
      memory: 2G       # 内存限制
    reservations:
      cpus: '1.0'      # 预留CPU
      memory: 1G       # 预留内存
```

## 故障排查

### 服务无法启动

1. **检查日志**
```bash
docker-compose -f docker-compose.prod.yml logs <service-name>
```

2. **检查端口占用**
```bash
netstat -tlnp | grep :80
netstat -tlnp | grep :443
```

3. **检查磁盘空间**
```bash
df -h
docker system df
```

### 数据库连接失败

1. 检查数据库服务状态
```bash
docker-compose -f docker-compose.prod.yml ps db
docker-compose -f docker-compose.prod.yml logs db
```

2. 检查环境变量
```bash
cat .env | grep DB_
```

3. 重置数据库（会丢失数据！）
```bash
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d db
```

### 代码执行超时

1. 检查沙箱服务
```bash
docker-compose -f docker-compose.prod.yml logs sandbox
```

2. 调整超时设置
修改环境变量 `SANDBOX_TIMEOUT=60`（秒）

### 性能问题

1. **查看资源使用**
```bash
docker stats
```

2. **重启服务**
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

3. **扩容**
```bash
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose -f docker-compose.prod.yml build

# 无中断更新
docker-compose -f docker-compose.prod.yml up -d

# 清理旧镜像
docker image prune -f
```

## 安全建议

1. **修改默认密码**
   - 数据库密码
   - Redis密码
   - JWT密钥
   - Grafana密码

2. **配置防火墙**
   - 只开放必要端口
   - 限制IP访问

3. **定期更新**
   - Docker镜像
   - 操作系统补丁
   - 依赖包

4. **启用HTTPS**
   - 使用SSL证书
   - 配置HTTP/2

5. **监控告警**
   - 配置邮件/短信告警
   - 监控关键指标

## 技术支持

遇到问题？请检查：
1. 文档和FAQ
2. GitHub Issues
3. 社区论坛
