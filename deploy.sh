#!/bin/bash

# AI学习平台 - 生产环境部署脚本
# 版本: 1.0.0
# 使用方法: chmod +x deploy.sh && ./deploy.sh [命令]

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="ailearning"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
LOG_DIR="./logs"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖项..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装。请访问 https://docs.docker.com/get-docker/ 安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装。请访问 https://docs.docker.com/compose/install/ 安装"
        exit 1
    fi
    
    print_success "所有依赖项已就绪"
}

# 检查环境文件
check_env_file() {
    print_info "检查环境配置文件..."
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.example" ]; then
            print_warning ".env 文件不存在，从 .env.example 复制..."
            cp .env.example .env
            print_warning "请编辑 .env 文件，设置正确的配置值后再运行部署"
            exit 1
        else
            print_error ".env 文件和 .env.example 都不存在！"
            exit 1
        fi
    fi
    
    # 检查关键环境变量
    source .env
    
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-change-in-production" ]; then
        print_error "SECRET_KEY 未设置或使用的是默认值！"
        print_info "请生成强密钥: openssl rand -hex 32"
        exit 1
    fi
    
    if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "changeme" ]; then
        print_error "DB_PASSWORD 未设置或使用的是默认值！"
        exit 1
    fi
    
    if [ -z "$REDIS_PASSWORD" ] || [ "$REDIS_PASSWORD" = "changeme" ]; then
        print_error "REDIS_PASSWORD 未设置或使用的是默认值！"
        exit 1
    fi
    
    if [[ "$CORS_ORIGINS" == *"*"* ]]; then
        print_warning "CORS_ORIGINS 包含通配符 '*'，生产环境建议设置具体域名"
    fi
    
    print_success "环境配置检查通过"
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"/{nginx,backend,sandbox}
    mkdir -p ./ssl
    mkdir -p redis
    mkdir -p scripts
    
    # 创建数据库初始化脚本（如果不存在）
    if [ ! -f "scripts/init-db.sql" ]; then
        cat > scripts/init-db.sql << 'EOF'
-- 数据库初始化脚本
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 用于全文搜索

-- 设置时区
SET timezone = 'Asia/Shanghai';
EOF
        print_success "创建数据库初始化脚本"
    fi
    
    # 创建Redis配置文件（如果不存在）
    if [ ! -f "redis/redis.conf" ]; then
        cat > redis/redis.conf << 'EOF'
# Redis生产环境配置
maxmemory 512mb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
save 900 1
save 300 10
save 60 10000
EOF
        print_success "创建Redis配置文件"
    fi
    
    print_success "目录创建完成"
}

# 数据库备份
backup_database() {
    print_info "备份数据库..."
    
    BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "db"; then
        source .env
        docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump \
            -U "${DB_USER:-ailearning}" \
            -d "${DB_NAME:-ailearning}" > "$BACKUP_FILE"
        print_success "数据库备份完成: $BACKUP_FILE"
    else
        print_warning "数据库服务未运行，跳过备份"
    fi
}

# 清理旧备份（保留最近7天）
cleanup_backups() {
    print_info "清理旧备份..."
    find "$BACKUP_DIR" -name "db_backup_*.sql" -mtime +7 -delete
    print_success "旧备份清理完成"
}

# 构建镜像
build_images() {
    print_info "构建Docker镜像..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    print_success "镜像构建完成"
}

# 启动服务
start_services() {
    print_info "启动服务..."
    docker-compose -f "$COMPOSE_FILE" up -d
    print_success "服务启动完成"
}

# 停止服务
stop_services() {
    print_info "停止服务..."
    docker-compose -f "$COMPOSE_FILE" down
    print_success "服务已停止"
}

# 查看服务状态
show_status() {
    print_info "服务状态:"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    print_info "资源使用:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# 查看日志
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
    else
        docker-compose -f "$COMPOSE_FILE" logs -f --tail=100 "$service"
    fi
}

# 数据库迁移
run_migrations() {
    print_info "运行数据库迁移..."
    
    # 等待数据库就绪
    print_info "等待数据库就绪..."
    sleep 5
    
    # 在容器中运行迁移
    docker-compose -f "$COMPOSE_FILE" exec backend python -c "
from app.core.database import init_db
init_db()
print('✅ 数据库迁移完成')
"
    
    print_success "数据库迁移完成"
}

# 配置SSL证书
setup_ssl() {
    print_info "配置SSL证书..."
    
    if [ -f "./ssl/fullchain.pem" ] && [ -f "./ssl/privkey.pem" ]; then
        print_success "SSL证书文件已存在"
        print_info "证书路径:"
        print_info "  - 证书: ./ssl/fullchain.pem"
        print_info "  - 私钥: ./ssl/privkey.pem"
        return
    fi
    
    print_warning "SSL证书文件不存在"
    echo ""
    echo "请选择SSL配置方式:"
    echo "  1) Let's Encrypt自动证书 (需要域名指向此服务器)"
    echo "  2) 手动配置证书 (将证书放置到 ./ssl/ 目录)"
    echo "  3) 跳过SSL配置 (使用HTTP，不推荐用于生产环境)"
    echo ""
    read -p "请选择 [1/2/3]: " ssl_choice
    
    case $ssl_choice in
        1)
            setup_letsencrypt
            ;;
        2)
            print_info "请将SSL证书文件放置到以下位置:"
            print_info "  - 证书链: ./ssl/fullchain.pem"
            print_info "  - 私钥:   ./ssl/privkey.pem"
            print_info "然后重新运行部署脚本"
            ;;
        3)
            print_warning "跳过SSL配置。请尽快配置SSL以确保安全！"
            # 创建自签名证书用于测试
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout ./ssl/privkey.pem \
                -out ./ssl/fullchain.pem \
                -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
            print_warning "已创建自签名证书（仅用于测试）"
            ;;
        *)
            print_error "无效选择"
            exit 1
            ;;
    esac
}

# Let's Encrypt证书配置
setup_letsencrypt() {
    print_info "配置Let's Encrypt证书..."
    
    read -p "请输入域名 (例如: example.com): " domain
    read -p "请输入邮箱 (用于证书过期提醒): " email
    
    if [ -z "$domain" ] || [ -z "$email" ]; then
        print_error "域名和邮箱不能为空"
        exit 1
    fi
    
    # 创建临时Nginx配置用于ACME挑战
    mkdir -p ./ssl
    
    print_info "申请证书..."
    docker run -it --rm \
        -v "$(pwd)/ssl:/etc/letsencrypt" \
        -v "$(pwd)/frontend:/var/www/html" \
        -p 80:80 \
        certbot/certbot certonly \
        --standalone \
        --preferred-challenges http \
        --agree-tos \
        --email "$email" \
        -d "$domain"
    
    # 复制证书到正确位置
    cp "./ssl/live/$domain/fullchain.pem" ./ssl/fullchain.pem
    cp "./ssl/live/$domain/privkey.pem" ./ssl/privkey.pem
    
    print_success "Let's Encrypt证书配置完成"
    print_info "证书将自动续期 (每12小时检查一次)"
}

# 完整部署流程
full_deploy() {
    print_info "========== AI学习平台生产部署 =========="
    print_info "开始时间: $(date)"
    echo ""
    
    check_dependencies
    check_env_file
    create_directories
    backup_database
    cleanup_backups
    setup_ssl
    build_images
    start_services
    
    print_info "等待服务启动..."
    sleep 10
    
    run_migrations
    show_status
    
    echo ""
    print_success "========== 部署完成 =========="
    print_info "结束时间: $(date)"
    echo ""
    print_info "访问地址:"
    print_info "  - 网站: http://your-domain.com (或 https://your-domain.com)"
    print_info "  - API文档: http://your-domain.com/docs"
    print_info "  - 健康检查: http://your-domain.com/health"
    print_info "  - Grafana: http://localhost:3000 (仅本地访问)"
    print_info "  - Prometheus: http://localhost:9090 (仅本地访问)"
}

# 更新部署（不重建镜像）
update_deploy() {
    print_info "执行更新部署..."
    backup_database
    docker-compose -f "$COMPOSE_FILE" pull
    docker-compose -f "$COMPOSE_FILE" up -d
    run_migrations
    print_success "更新完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
AI学习平台部署脚本 - 使用方法

命令:
    deploy      执行完整部署 (首次部署使用)
    update      更新部署 (保留数据，更新服务)
    start       启动服务
    stop        停止服务
    restart     重启服务
    status      查看服务状态
    logs [svc]  查看日志 (svc: 可选，指定服务名)
    backup      备份数据库
    migrate     运行数据库迁移
    ssl         配置SSL证书
    cleanup     清理旧备份和日志
    help        显示此帮助信息

示例:
    ./deploy.sh deploy          # 首次完整部署
    ./deploy.sh update          # 更新部署
    ./deploy.sh logs backend    # 查看后端日志
    ./deploy.sh status          # 查看服务状态

环境要求:
    - Docker 20.10+
    - Docker Compose 2.0+
    - 至少 2GB 可用内存
    - 至少 10GB 可用磁盘空间

配置文件:
    .env        - 环境变量配置
    nginx.conf  - Nginx配置
EOF
}

# 清理旧日志和备份
cleanup() {
    print_info "清理旧备份和日志..."
    cleanup_backups
    find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true
    docker system prune -f --volumes
    print_success "清理完成"
}

# 主命令处理
case "${1:-help}" in
    deploy|full)
        full_deploy
        ;;
    update)
        update_deploy
        ;;
    start|up)
        start_services
        show_status
        ;;
    stop|down)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        show_status
        ;;
    status|ps)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    backup)
        backup_database
        ;;
    migrate|migration)
        run_migrations
        ;;
    ssl|https)
        setup_ssl
        ;;
    cleanup|clean)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "未知命令: $1"
        show_help
        exit 1
        ;;
esac
