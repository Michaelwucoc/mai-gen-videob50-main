# mai-chu 分表视频生成器 - Docker 镜像
# 支持在服务器上部署并通过端口映射访问

FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖：ffmpeg（视频处理）、tk（B站二维码登录）、curl（健康检查）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    python3-tk \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p cred_datas videos config

# 入口脚本：首次运行初始化持久化配置
RUN chmod +x scripts/docker_entrypoint.sh

# 暴露 Streamlit 端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 启动命令：通过入口脚本初始化配置后启动 Streamlit
# --server.address=0.0.0.0 确保外部可访问
ENTRYPOINT ["/app/scripts/docker_entrypoint.sh"]
CMD ["streamlit", "run", "st_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless", "true"]
