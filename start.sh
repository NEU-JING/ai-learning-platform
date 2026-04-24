#!/bin/bash
# AI学习平台一键启动脚本
# 支持开发环境快速启动

set -e

# 颜色配置
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# 进程PID文件
BACKEND_PID_FILE="/tmp/ai-learning-backend.pid"
FRONTEND_PID_FILE="/tmp/ai-learning-frontend.pid"

# 打印函数
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
    print_info "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 未安装"
        exit 1
    fi
    
    # 检查Node.js (可选，用于更好的前端开发体验)
    if command -v node &> /dev/null; then
        print_success "Node.js 已安装: $(node --version)"
    else
        print_warning "Node.js 未安装，将使用Python HTTP服务器"
    fi
    
    print_success "依赖检查完成"
}

# 检查并创建虚拟环境
setup_venv() {
    print_info "设置Python虚拟环境..."
    
    cd "$BACKEND_DIR"
    
    if [ ! -d "venv" ]; then
        print_info "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    print_info "安装后端依赖..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    print_success "虚拟环境设置完成"
}

# 启动后端
start_backend() {
    print_info "启动后端服务..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # 检查端口是否被占用
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口8000已被占用，尝试停止现有进程..."
        kill $(lsof -t -i:8000) 2>/dev/null || true
        sleep 2
    fi
    
    # 启动后端
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/ai-learning-backend.log 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
    
    # 等待后端启动
    print_info "等待后端启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "后端服务已启动: http://localhost:8000"
            return 0
        fi
        sleep 1
    done
    
    print_error "后端启动超时，请检查日志: /tmp/ai-learning-backend.log"
    return 1
}

# 启动前端
start_frontend() {
    print_info "启动前端服务..."
    
    cd "$FRONTEND_DIR"
    
    # 检查端口是否被占用
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口3000已被占用，尝试停止现有进程..."
        kill $(lsof -t -i:3000) 2>/dev/null || true
        sleep 2
    fi
    
    # 使用Python HTTP服务器
    nohup python3 -m http.server 3000 > /tmp/ai-learning-frontend.log 2>&1 &
    echo $! > "$FRONTEND_PID_FILE"
    
    print_success "前端服务已启动: http://localhost:3000"
}

# 停止服务
stop_services() {
    print_info "停止服务..."
    
    # 停止后端
    if [ -f "$BACKEND_PID_FILE" ]; then
        PID=$(cat "$BACKEND_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null || true
            print_info "后端服务已停止"
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # 停止前端
    if [ -f "$FRONTEND_PID_FILE" ]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null || true
            print_info "前端服务已停止"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    # 强制清理端口
    kill $(lsof -t -i:8000) 2>/dev/null || true
    kill $(lsof -t -i:3000) 2>/dev/null || true
    
    print_success "所有服务已停止"
}

# 查看状态
status() {
    print_info "服务状态检查..."
    
    # 检查后端
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "后端服务运行中: http://localhost:8000"
        curl -s http://localhost:8000/ | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/
    else
        print_error "后端服务未运行"
    fi
    
    # 检查前端
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "前端服务运行中: http://localhost:3000"
    else
        print_error "前端服务未运行"
    fi
}

# 查看日志
logs() {
    print_info "查看日志 (按Ctrl+C退出)..."
    
    if [ -f "/tmp/ai-learning-backend.log" ]; then
        echo -e "\n${YELLOW}=== 后端日志 ===${NC}"
        tail -f /tmp/ai-learning-backend.log &
        BACKEND_LOG_PID=$!
    fi
    
    if [ -f "/tmp/ai-learning-frontend.log" ]; then
        echo -e "\n${YELLOW}=== 前端日志 ===${NC}"
        tail -f /tmp/ai-learning-frontend.log &
        FRONTEND_LOG_PID=$!
    fi
    
    # 等待Ctrl+C
    trap "kill $BACKEND_LOG_PID $FRONTEND_LOG_PID 2>/dev/null; exit" INT
    wait
}

# 显示帮助
show_help() {
    cat << EOF
AI学习平台启动脚本

用法: ./start.sh [命令]

命令:
    start       启动所有服务（默认）
    stop        停止所有服务
    restart     重启所有服务
    status      查看服务状态
    logs        查看日志
    help        显示帮助信息

示例:
    ./start.sh              # 启动所有服务
    ./start.sh start        # 启动所有服务
    ./start.sh stop         # 停止所有服务
    ./start.sh restart      # 重启所有服务
    ./start.sh status       # 查看服务状态

访问地址:
    前端: http://localhost:3000
    后端: http://localhost:8000
    API文档: http://localhost:8000/docs
EOF
}

# 主函数
main() {
    case "${1:-start}" in
        start)
            print_info "🚀 AI学习平台启动脚本"
            check_dependencies
            setup_venv
            start_backend
            start_frontend
            echo ""
            print_success "所有服务已启动！"
            echo ""
            echo -e "📱 前端地址: ${GREEN}http://localhost:3000${NC}"
            echo -e "🔧 后端地址: ${GREEN}http://localhost:8000${NC}"
            echo -e "📚 API文档: ${GREEN}http://localhost:8000/docs${NC}"
            echo ""
            print_info "使用 './start.sh stop' 停止服务"
            print_info "使用 './start.sh logs' 查看日志"
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            main start
            ;;
        status)
            status
            ;;
        logs)
            logs
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
}

main "$@"
