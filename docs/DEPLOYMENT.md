# 服务器部署指南

本文档说明如何在服务器上部署 mai-chu 分表视频生成器，并通过端口映射对外提供 Web 访问。**所有操作均可在 Web 界面中完成，无需 SSH 编辑配置文件。**

## 快速部署（Docker 推荐）

### 1. 环境要求

- Docker 和 Docker Compose
- 服务器需开放 **8501** 端口

### 2. 一键启动

**方式一：使用部署脚本（推荐）**

```bash
cd mai-gen-videob50-main
chmod +x deploy.sh

./deploy.sh install   # 首次：构建镜像
./deploy.sh start    # 启动服务
./deploy.sh status   # 查看状态
./deploy.sh stop     # 停止服务
./deploy.sh logs     # 查看日志
```

**方式二：直接使用 Docker Compose**

```bash
cd mai-gen-videob50-main
docker compose up -d
docker compose logs -f  # 查看日志
```

### 3. 访问

- **本地访问**：`http://localhost:8501`
- **局域网/公网访问**：`http://<服务器IP或域名>:8501`

确保防火墙已开放 8501 端口，例如：

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 8501
sudo ufw reload

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

---

## 数据持久化

Docker 会将以下目录映射到主机，重启容器后数据不会丢失：

| 主机路径 | 说明 |
|---------|------|
| `./data/db` | 数据库、存档 |
| `./data/cred_datas` | B站登录凭证等 |
| `./data/videos` | 下载和生成的视频 |
| `./data/user_config` | 用户偏好 |
| `./data/config` | 全局配置（`global_config.yaml`） |

首次运行时会自动从镜像复制默认配置到 `./data/config/`。

---

## Web 内完成所有配置

### 系统设置页面

进入 **系统设置** 页面可配置：

- 视频源（B站 / YouTube）
- 代理、YouTube API Key
- 视频分辨率、码率、过渡效果
- B站登录凭证上传（见下）

### B站登录（服务器/无头模式）

在 Docker 或 SSH 无图形界面环境下，无法弹出二维码窗口。可采用以下方式之一：

1. **上传凭证文件**  
   在本地电脑运行一次程序，完成 B站 扫码登录后，将 `cred_datas/bilibili_cred.pkl` 上传到 **系统设置** 页面的「B站登录凭证」处。

2. **使用终端二维码**  
   若可通过 `docker logs -f mai-gen-videob50` 查看容器日志，二维码会以终端字符形式输出，用 B站 App 扫描即可。

3. **不使用 B站登录**  
   在系统设置中勾选「B站：不使用账号登录」，部分功能可能受限。

### YouTube 推荐配置

在服务器上使用 YouTube 时，建议：

- 勾选「使用 YouTube Data API v3 搜索」
- 在 [Google Cloud Console](https://console.cloud.google.com/) 申请 API Key 并填入系统设置

---

## 非 Docker 部署（直接运行）

适用于已有 Python 环境的服务器：

```bash
# 1. 创建环境
conda create -n mai-chu-gen-video python=3.10
conda activate mai-chu-gen-video

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装 ffmpeg
# Ubuntu/Debian: sudo apt-get install ffmpeg
# CentOS: sudo yum install ffmpeg

# 4. 启动（绑定 0.0.0.0 以允许外部访问）
streamlit run st_app.py --server.address=0.0.0.0 --server.port=8501 --server.headless true
```

或使用项目提供的脚本：

```bash
bash start_server.sh
```

---

## 反向代理（可选）

若希望通过域名或 HTTPS 访问，可使用 Nginx 反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

---

## 常见问题

**Q: 端口 8501 无法访问？**  
检查防火墙、安全组是否放行 8501，以及 Docker 端口映射是否正确。

**Q: 视频生成很慢？**  
生成依赖 CPU，建议使用性能较好的服务器，或降低分辨率、缩短片段时长。

**Q: B站搜索/下载失败？**  
可能是风控或网络问题，可尝试配置代理、使用 YouTube API，或上传本地生成的 B站 凭证。
