#!/bin/bash
# Docker 入口脚本：首次运行时初始化持久化配置

set -e
CONFIG_DIR="/app/config"
CONFIG_FILE="$CONFIG_DIR/global_config.yaml"
DEFAULT_CONFIG="/app/global_config.yaml"

mkdir -p "$CONFIG_DIR"

# 首次运行：若持久化配置不存在，从镜像复制默认配置
if [ ! -f "$CONFIG_FILE" ] && [ -f "$DEFAULT_CONFIG" ]; then
    echo "首次运行：初始化配置文件到 $CONFIG_DIR"
    cp "$DEFAULT_CONFIG" "$CONFIG_FILE"
fi

# 容器内需监听 0.0.0.0 以便 Docker 端口映射；是否公网由 docker-compose ports 控制
exec streamlit run st_app.py --server.address=0.0.0.0 --server.port=8501 --server.headless true
