#!/bin/bash

# =============================================================================
# AI学习平台 - Docker沙箱镜像构建脚本
# =============================================================================
# 用法: ./build.sh [选项]
#   ./build.sh              # 使用默认配置构建
#   ./build.sh -t v1.0.0    # 使用自定义标签
#   ./build.sh --force      # 强制重新构建
#   ./build.sh --no-cache   # 不使用缓存构建
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
IMAGE_NAME="ai-learning-platform-sandbox"
VERSION="${SANDBOX_IMAGE_VERSION:-1.0.0}"
FORCE_REBUILD=false
NO_CACHE=false
DOCKERFILE="Dockerfile"

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 打印帮助信息
print_help() {
    echo -e "${BLUE}AI学习平台 - Docker沙箱镜像构建脚本${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -t, --tag TAG       指定镜像标签 (默认: $VERSION)"
    echo "  -n, --name NAME     指定镜像名称 (默认: $IMAGE_NAME)"
    echo "  -f, --force         强制重新构建（删除旧镜像）"
    echo "      --no-cache      不使用Docker缓存构建"
    echo "      --clean         清理所有相关镜像和容器"
    echo "  -h, --help          显示帮助信息"
    echo ""
    echo "环境变量:"
    echo "  SANDBOX_IMAGE_VERSION   镜像版本号"
    echo "  SANDBOX_IMAGE_NAME      镜像名称"
    echo ""
    echo "示例:"
    echo "  $0                    # 使用默认配置构建"
    echo "  $0 -t 1.1.0          # 构建 v1.1.0 版本"
    echo "  $0 -t latest -f      # 强制重新构建 latest 标签"
    echo "  $0 --clean           # 清理所有沙箱镜像"
}

# 打印信息
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# 打印成功
success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 打印警告
warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 打印错误
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否可用
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        error "Docker 服务未运行，请启动 Docker 服务"
        exit 1
    fi

    success "Docker 环境检查通过"
}

# 清理旧镜像和容器
cleanup() {
    info "清理旧的沙箱镜像和容器..."

    # 停止并删除相关容器
    containers=$(docker ps -aq --filter "name=sandbox-" 2>/dev/null || true)
    if [ -n "$containers" ]; then
        info "停止并删除 $containers 个沙箱容器..."
        docker rm -f $containers 2>/dev/null || true
    fi

    # 删除旧镜像
    images=$(docker images "$IMAGE_NAME" -q 2>/dev/null || true)
    if [ -n "$images" ]; then
        info "删除旧镜像..."
        docker rmi -f $images 2>/dev/null || true
    fi

    # 清理悬空镜像
    dangling=$(docker images -f "dangling=true" -q 2>/dev/null || true)
    if [ -n "$dangling" ]; then
        info "清理悬空镜像..."
        docker rmi $dangling 2>/dev/null || true
    fi

    success "清理完成"
}

# 构建镜像
build_image() {
    local tag="$1"
    local full_tag="${IMAGE_NAME}:${tag}"

    info "开始构建镜像..."
    info "  镜像名称: $IMAGE_NAME"
    info "  镜像标签: $tag"
    info "  完整标签: $full_tag"
    info "  构建目录: $SCRIPT_DIR"

    # 构建参数
    local build_args="--build-arg SANDBOX_VERSION=$tag"
    build_args="$build_args --label sandbox.version=$tag"
    build_args="$build_args --label sandbox.name=ai-learning-platform"
    build_args="$build_args --label sandbox.built_at=$(date +%s)"

    # 不使用缓存
    if [ "$NO_CACHE" = true ]; then
        build_args="$build_args --no-cache"
        info "不使用缓存构建"
    fi

    # 执行构建
    echo ""
    if ! docker build \
        -t "$full_tag" \
        -t "$IMAGE_NAME:latest" \
        $build_args \
        -f "$SCRIPT_DIR/$DOCKERFILE" \
        "$SCRIPT_DIR"; then
        error "镜像构建失败"
        exit 1
    fi

    success "镜像构建成功: $full_tag"
}

# 验证镜像
verify_image() {
    local tag="$1"
    local full_tag="${IMAGE_NAME}:${tag}"

    info "验证镜像..."

    if ! docker image inspect "$full_tag" &> /dev/null; then
        error "镜像验证失败: $full_tag 不存在"
        exit 1
    fi

    # 获取镜像信息
    local image_info=$(docker image inspect "$full_tag" --format='{{.Id}}|{{.Size}}|{{.Config.Labels.sandbox.version}}')
    local image_id=$(echo "$image_info" | cut -d'|' -f1 | cut -d: -f2 | head -c 12)
    local image_size=$(echo "$image_info" | cut -d'|' -f2)
    local image_version=$(echo "$image_info" | cut -d'|' -f3)

    # 转换大小为可读格式
    local size_mb=$((image_size / 1024 / 1024))

    success "镜像验证通过"
    echo ""
    echo -e "  ${GREEN}✓${NC} 镜像ID:   ${image_id}"
    echo -e "  ${GREEN}✓${NC} 大小:     ${size_mb}MB"
    echo -e "  ${GREEN}✓${NC} 版本:     ${image_version:-unknown}"
    echo ""
}

# 测试镜像
test_image() {
    local tag="$1"
    local full_tag="${IMAGE_NAME}:${tag}"

    info "测试镜像..."

    # 运行测试容器
    local test_output
    test_output=$(docker run --rm "$full_tag" python3 -c "
import sys
import numpy as np
print('Python:', sys.version)
print('NumPy:', np.__version__)
print('Test passed!')
" 2>&1) || {
        error "镜像测试失败"
        echo "$test_output"
        exit 1
    }

    success "镜像测试通过"
    echo ""
    echo "$test_output" | sed 's/^/  /'
    echo ""
}

# 显示镜像列表
list_images() {
    info "当前沙箱镜像列表:"
    echo ""
    docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--tag)
                VERSION="$2"
                shift 2
                ;;
            -n|--name)
                IMAGE_NAME="$2"
                shift 2
                ;;
            -f|--force)
                FORCE_REBUILD=true
                shift
                ;;
            --no-cache)
                NO_CACHE=true
                shift
                ;;
            --clean)
                cleanup
                exit 0
                ;;
            -h|--help)
                print_help
                exit 0
                ;;
            *)
                error "未知选项: $1"
                print_help
                exit 1
                ;;
        esac
    done
}

# 主函数
main() {
    # 解析参数
    parse_args "$@"

    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  AI学习平台 - Docker沙箱镜像构建${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # 检查Docker
    check_docker

    # 检查Dockerfile
    if [ ! -f "$SCRIPT_DIR/$DOCKERFILE" ]; then
        error "Dockerfile 不存在: $SCRIPT_DIR/$DOCKERFILE"
        exit 1
    fi

    # 如果需要强制重建，先清理
    if [ "$FORCE_REBUILD" = true ]; then
        warn "强制重新构建模式"
        cleanup
    fi

    # 构建镜像
    build_image "$VERSION"

    # 验证镜像
    verify_image "$VERSION"

    # 测试镜像
    test_image "$VERSION"

    # 显示镜像列表
    list_images

    success "所有操作完成！"
    echo ""
    info "使用镜像: ${IMAGE_NAME}:${VERSION}"
    info "测试命令: docker run --rm ${IMAGE_NAME}:${VERSION} python3 -c 'print(\"Hello, Sandbox!\")'"
    echo ""
}

# 运行主函数
main "$@"
