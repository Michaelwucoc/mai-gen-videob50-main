# 生成文件路径说明

本文档说明各类生成/下载文件的存放位置。在 **Docker 部署** 时，所有路径均在 `/www/maigen/` 下。

## 路径总览

| 内容 | 路径 | 说明 |
|------|------|------|
| **成绩背景图片** | `b50_datas/{用户名}/images/` | 步骤 1 生成的成绩展示图 |
| **生成的视频** | `b50_datas/{用户名}/videos/` | 步骤 5 合成的视频片段和完整视频 |
| **下载的谱面视频** | `videos/downloads/` | 步骤 3 从 B站/YouTube 下载的视频 |
| **数据库** | `db/` | SQLite 数据库 |
| **B站凭证** | `cred_datas/` | B站登录缓存 |
| **全局配置** | `config/` | global_config.yaml |

## 详细说明

### 1. 成绩背景图片

- **相对路径**：`b50_datas/{用户名}/images/`
- **Docker 实际路径**：`/www/maigen/b50_datas/{用户名}/images/`
- **文件命名**：`{游戏类型}_{序号}_{曲名}.png`、`{游戏类型}_{chart_id}_bg.png`

### 2. 生成的视频

- **相对路径**：`b50_datas/{用户名}/videos/`
- **Docker 实际路径**：`/www/maigen/b50_datas/{用户名}/videos/`
- **文件**：各片段 `.mp4`、完整视频 `{用户名}_FULL_VIDEO.mp4`

### 3. 下载的谱面视频

- **相对路径**：`videos/downloads/`
- **Docker 实际路径**：`/www/maigen/videos/downloads/`

## Web 文件浏览

在左侧导航进入 **文件浏览**，可在网页中直接查看上述目录内容，无需打开系统文件夹。
