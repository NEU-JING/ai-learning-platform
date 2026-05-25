# AI学习平台 - 运维手册

## 目录
- [日常运维](#日常运维)
- [监控告警](#监控告警)
- [备份恢复](#备份恢复)
- [故障处理](#故障处理)
- [性能优化](#性能优化)
- [安全维护](#安全维护)

## 日常运维

### 每日检查清单

```bash
#!/bin/bash
# daily_check.sh - 每日检查脚本

echo "========== AI学习平台 - 每日检查 $(date) =========="

# 1. 检查服务状态
echo "[1/6] 检查服务状态..."
docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml ps

# 2. 检查磁盘空间
echo -e "\n[2/6] 检查磁盘空间..."
df -h | grep -E "(Filesystem|/dev/)"

# 3. 检查内存使用
echo -e "\n[3/6] 检查内存使用..."
free -h

# 4. 检查容器资源使用
echo -e "\n[4/6] 检查容器资源使用..."
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# 5. 检查日志错误
echo -e "\n[5/6] 检查最近错误日志..."
docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml logs --tail=50 backend 2>&1 | grep -i error | tail -10

# 6. 检查数据库连接数
echo -e "\n[6/6] 检查数据库状态..."
docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml exec -T db psql -U ailearning -c "SELECT count(*) as connections FROM pg_stat_activity;"

echo -e "\n========== 检查完成 =========="
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f db
docker-compose -f docker-compose.prod.yml logs -f sandbox

# 查看最近100行日志
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

# 查看特定时间范围的日志
docker-compose -f docker-compose.prod.yml logs --since="2024-01-01T00:00:00" backend
```

### 服务管理

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart backend

# 停止服务
docker-compose -f docker-compose.prod.yml stop

# 启动服务
docker-compose -f docker-compose.prod.yml start

# 完全停止并移除容器
docker-compose -f docker-compose.prod.yml down

# 完全停止并移除容器和卷（会丢失数据！）
docker-compose -f docker.prod.yml down -v
```

## 监控告警

### 关键指标监控

| 指标 | 告警阈值 | 检查命令 |
|------|----------|----------|
| CPU使用率 | > 80% | `docker stats` |
| 内存使用率 | > 85% | `free -m` |
| 磁盘使用率 | > 80% | `df -h` |
| 数据库连接数 | > 80 | `psql -c "SELECT count(*) FROM pg_stat_activity;"`
| API响应时间 | > 2s | 应用内置metrics
| 错误率 | > 5% | 日志分析

### 告警脚本示例

```bash
#!/bin/bash
# alert.sh - 告警检查脚本

ALERT_FILE="/var/log/ailearning_alerts.log"
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

send_alert() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] $message" >> $ALERT_FILE
    
    # 发送到Slack（可选）
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"[$level] AI学习平台告警: $message\"}" \
        $SLACK_WEBHOOK
}

# 检查磁盘空间
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ $DISK_USAGE -gt 80 ]; then
    send_alert "CRITICAL" "磁盘使用率超过80%: ${DISK_USAGE}%"
fi

# 检查内存
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ $MEM_USAGE -gt 85 ]; then
    send_alert "WARNING" "内存使用率超过85%: ${MEM_USAGE}%"
fi

# 检查服务状态
if ! docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml ps | grep -q "Up"; then
    send_alert "CRITICAL" "服务异常，请立即检查！"
fi
```

### 健康检查API

```bash
# 检查API健康状态
curl http://localhost:8000/health

# 预期返回
{
    "status": "healthy",
    "version": "1.0.0",
    "database": "connected",
    "redis": "connected",
    "sandbox": "connected"
}
```

## 备份恢复

### 数据库备份

```bash
#!/bin/bash
# backup.sh - 数据库备份脚本

BACKUP_DIR="/backups/ailearning"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

echo "开始备份数据库..."
docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml exec -T db pg_dump -U ailearning -d ailearning > $BACKUP_FILE

if [ $? -eq 0 ]; then
    gzip $BACKUP_FILE
    echo "✅ 备份成功: ${BACKUP_FILE}.gz"
    
    # 清理旧备份
    find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo "🗑️  已清理 ${RETENTION_DAYS} 天前的备份"
else
    echo "❌ 备份失败"
    exit 1
fi
```

### 数据库恢复

```bash
#!/bin/bash
# restore.sh - 数据库恢复脚本

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <backup_file>"
    exit 1
fi

echo "⚠️  警告: 这将覆盖当前数据库！"
read -p "确定要继续吗? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "已取消"
    exit 0
fi

# 停止后端服务
docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml stop backend

# 恢复数据库
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml exec -T db psql -U ailearning -d ailearning
else
    cat $BACKUP_FILE | docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml exec -T db psql -U ailearning -d ailearning
fi

# 重启服务
docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml start backend

echo "✅ 数据库恢复完成"
```

### 完整系统备份

```bash
#!/bin/bash
# full_backup.sh - 完整系统备份

BACKUP_DIR="/backups/ailearning/full"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="full_backup_$DATE"

mkdir -p $BACKUP_DIR/$BACKUP_NAME

echo "开始完整备份..."

# 1. 备份数据库
echo "[1/4] 备份数据库..."
docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml exec -T db pg_dump -U ailearning -d ailearning | gzip > $BACKUP_DIR/$BACKUP_NAME/database.sql.gz

# 2. 备份配置文件
echo "[2/4] 备份配置文件..."
cp -r /opt/ai-learning-platform/.env $BACKUP_DIR/$BACKUP_NAME/
cp -r /opt/ai-learning-platform/nginx.conf $BACKUP_DIR/$BACKUP_NAME/
cp -r /opt/ai-learning-platform/docker-compose.prod.yml $BACKUP_DIR/$BACKUP_NAME/

# 3. 备份用户上传文件（如果有）
echo "[3/4] 备份用户文件..."
# 根据实际存储位置修改
# cp -r /opt/ai-learning-platform/uploads $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || true

# 4. 打包
echo "[4/4] 打包备份..."
tar czf $BACKUP_DIR/${BACKUP_NAME}.tar.gz -C $BACKUP_DIR $BACKUP_NAME
rm -rf $BACKUP_DIR/$BACKUP_NAME

echo "✅ 完整备份完成: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
```

## 故障处理

### 常见故障排查流程

```
1. 检查服务状态
   ↓
2. 查看日志
   ↓
3. 检查资源使用
   ↓
4. 检查网络连接
   ↓
5. 检查数据库状态
   ↓
6. 重启服务
   ↓
7. 联系技术支持
```

### 数据库连接池耗尽

**症状**: API响应缓慢，日志显示连接超时

**处理**:
```bash
# 1. 查看当前连接
psql -h localhost -U ailearning -c "SELECT * FROM pg_stat_activity;"

# 2. 终止空闲连接
psql -h localhost -U ailearning -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < NOW() - INTERVAL '1 hour';"

# 3. 重启后端服务
docker-compose -f docker-compose.prod.yml restart backend
```

**预防**: 在代码中正确关闭数据库连接，使用连接池

### 内存泄漏

**症状**: 内存持续增长，最终OOM

**处理**:
```bash
# 1. 找出内存占用最高的容器
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}" | sort -k2 -h

# 2. 重启问题服务
docker-compose -f docker-compose.prod.yml restart <service>

# 3. 检查内存限制
docker update --memory=2g --memory-swap=2g <container>
```

### 沙箱执行卡死

**症状**: 代码执行无响应

**处理**:
```bash
# 1. 重启沙箱服务
docker-compose -f docker-compose.prod.yml restart sandbox

# 2. 清理沙箱容器
docker ps -a | grep sandbox- | awk '{print $1}' | xargs docker rm -f

# 3. 清理沙箱临时文件
docker-compose -f docker-compose.prod.yml exec sandbox rm -rf /tmp/sandbox/*
```

## 性能优化

### 数据库优化

```sql
-- 添加索引
CREATE INDEX CONCURRENTLY idx_learning_progress_user_chapter ON learning_progress(user_id, chapter_id);
CREATE INDEX CONCURRENTLY idx_lab_submission_user ON lab_submissions(user_id);

-- 定期清理
DELETE FROM lab_submissions WHERE created_at < NOW() - INTERVAL '90 days';

-- 表分析
ANALYZE learning_progress;
ANALYZE lab_submissions;
```

### Redis优化
```bash
# 查看内存使用
redis-cli INFO memory

# 设置内存上限
redis-cli CONFIG SET maxmemory 512mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 清理缓存
redis-cli FLUSHDB
```
### 代码执行优化
```bash
# 调整沙箱资源配置
docker-compose -f docker-compose.prod.yml up -d --scale sandbox=3

# 调整超时时间
export SANDBOX_TIMEOUT=60
```
## 安全维护

### 定期安全检查
```bash
#!/bin/bash
# security_check.sh - 安全检查脚本

echo "========== 安全检查 $(date) =========="

# 1. 检查异常登录
echo "[1/5] 检查异常登录..."
last | grep -v "wtmp begins"

# 2. 检查开放的端口
echo -e "\n[2/5] 检查开放端口..."
netstat -tlnp

# 3. 检查Docker容器权限
echo -e "\n[3/5] 检查容器权限..."
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"

# 4. 检查文件权限
echo -e "\n[4/5] 检查敏感文件权限..."
ls -la /opt/ai-learning-platform/.env
ls -la /opt/ai-learning-platform/ssl/

# 5. 检查日志中的异常
echo -e "\n[5/5] 检查异常日志..."
docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml logs --since="24h" | grep -i "error\|exception\|attack" | tail -20

echo -e "\n========== 检查完成 =========="
```

### 安全更新
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 更新Docker镜像
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# 清理旧镜像
docker image prune -f

# 重启服务
docker-compose -f docker-compose.prod.yml restart
```

### 访问日志分析
```bash
# 查看访问最多的IP
docker-compose -f docker-compose.prod.yml logs nginx | awk '{print $1}' | sort | uniq -c | sort -rn | head -20

# 查看404错误
docker-compose -f docker-compose.prod.yml logs nginx | grep '" 404 '

# 查看慢请求
docker-compose -f docker-compose.prod.yml logs nginx | awk -F'"' '{print $NF}' | awk '{if($1>2)print}' | head -20
```

## 应急联系

| 角色 | 联系人 | 联系方式 |
|------|--------|----------|
| 运维负责人 | - | - |
| 开发团队 | - | - |
| DBA | - | - |
| 安全团队 | - | - |

## 附录

### 常用命令速查

```bash
# 快速检查
status() { docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml ps; }
logs() { docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml logs -f $1; }
restart() { docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml restart $1; }

# 数据库操作
db_exec() { docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml exec db psql -U ailearning -c "$1"; }
db_backup() { docker-compose -f /opt/ai-learning-platform/docker-compose.prod.yml exec -T db pg_dump -U ailearning -d ailearning | gzip > backup_$(date +%Y%m%d).sql.gz; }
```

### 问题上报模板

```
【问题描述】
[简要描述问题]

【影响范围】
[影响的用户/功能]

【发生时间】
[YYYY-MM-DD HH:MM:SS]

【错误信息】
[关键日志/错误截图]

【已尝试的解决方案】
[已尝试的操作]

【当前状态】
[服务状态/影响程度]
```
