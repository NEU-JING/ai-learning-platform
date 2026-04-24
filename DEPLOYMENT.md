# AI学习平台部署指南

本文档详细介绍AI学习平台的部署方法，包括开发环境、Docker部署和云服务器部署。

## 目录

- [快速开始](#快速开始)
- [环境要求](#环境要求)
- [开发环境部署](#开发环境部署)
- [Docker部署](#docker部署)
- [云服务器部署](#云服务器部署)
- [SSL证书配置](#ssl证书配置)
- [备份与恢复](#备份与恢复)

## 快速开始

使用一键启动脚本：

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

访问：
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- API文档: http://localhost:8000/docs

## 环境要求

### 开发环境
- Python 3.9+
- Node.js 16+ (可选)
- Docker (用于代码沙箱)

### 生产环境
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM (推荐)
- 20GB 磁盘空间

## 开发环境部署

### 1. 克隆项目

```bash
cd /root/.openclaw/workspace/projects/ai-learning-platform
```

### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，配置必要参数
```

### 3. 启动服务

```bash
# 使用启动脚本
./start.sh

# 或手动启动
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend
python -m http.server 3000
```

## Docker部署

### 1. 生产环境配置

```bash
# 复制生产环境配置
cp backend/.env.example backend/.env

# 编辑 .env，设置生产环境参数
DEBUG=false
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-domain.com
DATABASE_URL=postgresql://postgres:password@postgres:5432/ai_learning
```

### 2. 启动服务

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. 数据库迁移

```bash
# 创建迁移
docker-compose -f docker-compose.prod.yml exec backend alembic revision --autogenerate -m "initial"

# 执行迁移
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 4. 查看日志

```bash
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

## 云服务器部署

以Ubuntu 22.04为例：

### 1. 安装Docker

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt install docker-compose-plugin

# 添加到docker组
sudo usermod -aG docker $USER
newgrp docker
```

### 2. 部署应用

```bash
# 创建应用目录
mkdir -p /opt/ai-learning-platform
cd /opt/ai-learning-platform

# 复制项目文件
# 使用scp或git clone

# 配置环境变量
cp backend/.env.example backend/.env
nano backend/.env

# 启动服务
docker-compose -f docker-compose.prod.yml up -d
```

### 3. 配置nginx

```bash
sudo apt install nginx

# 复制nginx配置
sudo cp nginx.conf /etc/nginx/sites-available/ai-learning-platform

# 创建符号链接
sudo ln -s /etc/nginx/sites-available/ai-learning-platform /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启nginx
sudo systemctl restart nginx
```

## SSL证书配置

使用Let's Encrypt免费证书：

### 1. 安装Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. 申请证书

```bash
sudo certbot --nginx -d your-domain.com
```

### 3. 自动续期

Certbot会自动配置systemd定时任务。测试续期：

```bash
sudo certbot renew --dry-run
```

### 4. 更新nginx配置

编辑 `/etc/nginx/sites-available/ai-learning-platform`：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... 其他配置
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 备份与恢复

### 数据库备份

```bash
# PostgreSQL备份
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres ai_learning > backup.sql

# SQLite备份 (开发环境)
cp backend/ai_learning.db backup/ai_learning.db.$(date +%Y%m%d)
```

### 数据库恢复

```bash
# PostgreSQL恢复
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres ai_learning < backup.sql

# SQLite恢复
cp backup/ai_learning.db.20260101 backend/ai_learning.db
```

### 完整系统备份

```bash
# 备份整个项目目录
tar -czvf ai-learning-platform-backup-$(date +%Y%m%d).tar.gz /opt/ai-learning-platform

# 备份Docker卷
docker run --rm -v ai-learning-platform_postgres_data:/data -v $(pwd):/backup alpine tar czvf /backup/postgres-backup.tar.gz -C /data .
```

## 故障排除

### 服务无法启动

```bash
# 检查日志
docker-compose logs backend

# 检查端口占用
sudo lsof -i :8000
sudo lsof -i :3000

# 重启服务
docker-compose restart
```

### 数据库连接失败

```bash
# 检查数据库状态
docker-compose ps

# 查看数据库日志
docker-compose logs postgres

# 重置数据库 (谨慎操作！)
docker-compose down -v
docker-compose up -d
```

### 沙箱镜像问题

```bash
# 重建沙箱镜像
cd sandbox
docker build -t ai-learning-platform-sandbox .

# 或自动检查
./start.sh
```

## 性能优化

### 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_learning_progress_user ON learning_progress(user_id);
CREATE INDEX idx_learning_progress_course ON learning_progress(course_id);
CREATE INDEX idx_lab_submission_user ON lab_submission(user_id);
```

### 缓存配置

在 `.env` 中启用Redis缓存：

```bash
REDIS_URL=redis://localhost:6379/0
```

## 监控与日志

### 查看实时日志

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
```

### 设置日志轮转

```bash
sudo apt install logrotate

# 创建配置
sudo tee /etc/logrotate.d/ai-learning-platform << EOF
/opt/ai-learning-platform/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
```

## 更新部署

```bash
# 拉取最新代码
git pull

# 重建镜像
docker-compose -f docker-compose.prod.yml build

# 数据库迁移
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 重启服务
docker-compose -f docker-compose.prod.yml up -d
```

## 联系支持

如有问题，请提交Issue到项目仓库。
