#!/bin/bash
# mai-chu 分表视频生成器 - 一键部署脚本
# 使用方式: ./deploy.sh [install|start|stop|restart|status]

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT=8501
CONTAINER_NAME="mai-gen-videob50"

# 持久化数据目录
DATA_ROOT="/www/maigen"

# 创建持久化数据目录
init_data_dirs() {
    if ! mkdir -p "$DATA_ROOT"/{db,cred_datas,videos,b50_datas,static_user,user_config,config} 2>/dev/null; then
        echo "创建目录 $DATA_ROOT 需要 sudo 权限"
        sudo mkdir -p "$DATA_ROOT"/{db,cred_datas,videos,b50_datas,static_user,user_config,config}
    fi
    echo "数据目录: $DATA_ROOT/{db,cred_datas,videos,b50_datas,static_user,user_config,config}"
}

# 检查 Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "错误: 未找到 docker，请先安装 Docker"
        exit 1
    fi
    if ! docker info &> /dev/null; then
        echo "错误: Docker 未运行或当前用户无权限"
        exit 1
    fi
}

# 安装/构建并启动
cmd_install() {
    check_docker
    init_data_dirs
    echo "正在构建镜像..."
    docker compose build
    echo ""
    echo "✅ 构建完成。运行 ./deploy.sh start 启动服务"
}

# 启动服务
cmd_start() {
    check_docker
    init_data_dirs
    echo "正在启动服务..."
    docker compose up -d
    echo ""
    echo "=========================================="
    echo "  mai-chu 分表视频生成器 已启动"
    echo "=========================================="
    echo "  访问地址: http://localhost:${PORT}（默认仅本机）"
    echo ""
    echo "  需公网访问时，修改 docker-compose.yml 中 ports 为 \"8501:8501\""
    echo "=========================================="
}

# 停止服务
cmd_stop() {
    check_docker
    docker compose stop 2>/dev/null || docker stop "$CONTAINER_NAME" 2>/dev/null || true
    echo "服务已停止"
}

# 重启服务
cmd_restart() {
    cmd_stop
    sleep 2
    cmd_start
}

# 查看状态
cmd_status() {
    check_docker
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "状态: 运行中"
        echo "访问: http://localhost:${PORT}"
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo "状态: 未运行"
        if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
            echo "容器存在但已停止，运行 ./deploy.sh start 启动"
        fi
    fi
}

# 查看日志
cmd_logs() {
    check_docker
    docker compose logs -f 2>/dev/null || docker logs -f "$CONTAINER_NAME" 2>/dev/null
}

# 主逻辑
case "${1:-install}" in
    install)  cmd_install ;;
    start)    cmd_start ;;
    stop)     cmd_stop ;;
    restart)  cmd_restart ;;
    status)   cmd_status ;;
    logs)     cmd_logs ;;
    *)
        echo "用法: $0 {install|start|stop|restart|status|logs}"
        echo ""
        echo "  install  - 构建 Docker 镜像"
        echo "  start    - 启动服务（默认）"
        echo "  stop     - 停止服务"
        echo "  restart  - 重启服务"
        echo "  status   - 查看运行状态"
        echo "  logs     - 查看日志"
        exit 1
        ;;
esac
