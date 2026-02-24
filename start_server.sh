#!/bin/bash
# mai-chu 分表视频生成器 - 服务器启动脚本
# 用于在服务器上运行并对外提供 Web 访问

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.10+"
    exit 1
fi

# 检查 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "警告: 未找到 ffmpeg，视频生成功能可能无法使用"
    echo "请安装: apt-get install ffmpeg (Debian/Ubuntu) 或 yum install ffmpeg (CentOS)"
fi

# 创建必要目录
mkdir -p cred_datas videos

# 设置环境变量（可选）
# export STREAMLIT_SERVER_PORT=8501
# export STREAMLIT_SERVER_ADDRESS=0.0.0.0

echo "=========================================="
echo "  mai-chu 分表视频生成器 - Web 服务"
echo "=========================================="
echo ""
echo "  访问地址: http://<服务器IP>:8501"
echo "  端口映射: 确保防火墙已开放 8501 端口"
echo ""
echo "  启动中..."
echo "=========================================="

# 使用 streamlit 运行，配置已在 .streamlit/config.toml 中
exec streamlit run st_app.py --server.headless true
