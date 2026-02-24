"""
系统设置页面 - 在 Web 中配置所有全局参数
支持服务器部署时无需编辑配置文件
"""
import streamlit as st
import os
import yaml
from utils.PageUtils import read_global_config, write_global_config, get_game_type_text

st.set_page_config(page_title="系统设置", page_icon="⚙️", layout="wide")

st.header("⚙️ 系统设置")
st.markdown("在此页面配置所有全局参数，无需手动编辑 `global_config.yaml`。配置会立即生效。")

try:
    G_config = read_global_config()
except FileNotFoundError as e:
    st.error(f"未找到配置文件：{e}")
    st.stop()

# 检测运行环境
is_docker = os.path.exists("/.dockerenv")
if is_docker:
    st.info("🐳 检测到 Docker 环境，配置已持久化到卷中。")

# ========== 视频源与下载 ==========
st.subheader("📥 视频源与下载")
col1, col2 = st.columns(2)

with col1:
    downloader = st.selectbox(
        "默认下载器",
        ["bilibili", "youtube"],
        index=["bilibili", "youtube"].index(G_config.get("DOWNLOADER", "bilibili")),
        help="选择视频来源：B站 或 YouTube"
    )
    download_high_res = st.checkbox(
        "下载高分辨率视频",
        value=G_config.get("DOWNLOAD_HIGH_RES", True),
        help="开启后尽可能下载 1080p，否则最高 480p"
    )
    no_bilibili_credential = st.checkbox(
        "B站：不使用账号登录",
        value=G_config.get("NO_BILIBILI_CREDENTIAL", False),
        help="服务器/无头模式下，若无法弹出二维码，可勾选此项；或上传下方凭证文件"
    )

with col2:
    search_max_results = st.number_input(
        "单曲最多搜索结果数",
        min_value=1,
        max_value=10,
        value=G_config.get("SEARCH_MAX_RESULTS", 3)
    )
    search_wait_min, search_wait_max = st.slider(
        "搜索间隔（秒）",
        min_value=0,
        max_value=10,
        value=(G_config.get("SEARCH_WAIT_TIME", [1, 3])[0], G_config.get("SEARCH_WAIT_TIME", [1, 3])[1]),
        help="每次 API 调用后等待时间，减少风控"
    )

# B站凭证上传（服务器部署时使用）
st.markdown("#### B站登录凭证（可选）")
st.caption("在服务器/无头模式下，无法弹出二维码。您可以在本地电脑登录一次，将生成的凭证文件上传到此。")
cred_path = "./cred_datas/bilibili_cred.pkl"
uploaded_cred = st.file_uploader("上传 bilibili_cred.pkl", type=["pkl"], help="从本地 cred_datas 目录选择")
if uploaded_cred:
    os.makedirs(os.path.dirname(cred_path), exist_ok=True)
    with open(cred_path, "wb") as f:
        f.write(uploaded_cred.getvalue())
    st.success("✅ 凭证已上传，可尝试使用 B站 下载。")

# ========== 代理 ==========
st.subheader("🌐 代理设置")
use_proxy = st.checkbox("启用代理", value=G_config.get("USE_PROXY", False))
proxy_address = st.text_input(
    "代理地址",
    value=G_config.get("PROXY_ADDRESS", "127.0.0.1:7890"),
    disabled=not use_proxy,
    placeholder="127.0.0.1:7890"
)

# ========== YouTube ==========
st.subheader("📺 YouTube 设置")
use_youtube_api = st.checkbox(
    "使用 YouTube Data API v3 搜索",
    value=G_config.get("USE_YOUTUBE_API", True),
    help="更稳定，需申请 API Key"
)
youtube_api_key = st.text_input(
    "YouTube API Key",
    value=G_config.get("YOUTUBE_API_KEY") or "",
    type="password",
    placeholder="留空则从配置读取",
    help="在 Google Cloud Console 申请"
)

# YouTube PO Token（非 API 模式）
st.markdown("##### YouTube 非 API 模式（可选）")
use_oauth = st.checkbox("使用 OAuth 登录", value=G_config.get("USE_OAUTH", True), key="use_oauth")
use_custom_po_token = st.checkbox("使用自定义 PO Token", value=G_config.get("USE_CUSTOM_PO_TOKEN", False), key="use_custom")
use_auto_po_token = st.checkbox("自动获取 PO Token", value=G_config.get("USE_AUTO_PO_TOKEN", False), key="use_auto")
po_token = st.text_input("PO Token", value=G_config.get("CUSTOMER_PO_TOKEN", {}).get("po_token", ""), type="password")
visitor_data = st.text_input("Visitor Data", value=G_config.get("CUSTOMER_PO_TOKEN", {}).get("visitor_data", ""), type="password")

# ========== 视频生成 ==========
st.subheader("🎬 视频生成")
col_v1, col_v2 = st.columns(2)
with col_v1:
    video_res_w = st.number_input("输出宽度", min_value=720, max_value=3840, value=G_config.get("VIDEO_RES", [1920, 1080])[0])
    video_res_h = st.number_input("输出高度", min_value=480, max_value=2160, value=G_config.get("VIDEO_RES", [1920, 1080])[1])
    video_bitrate = st.number_input("视频码率 (kbps)", min_value=1000, max_value=20000, value=G_config.get("VIDEO_BITRATE", 5000))
with col_v2:
    clip_play_time = st.number_input("每段时长 (秒)", min_value=3, max_value=30, value=G_config.get("CLIP_PLAY_TIME", 10))
    video_trans_enable = st.checkbox("启用过渡效果", value=G_config.get("VIDEO_TRANS_ENABLE", True))
    video_trans_time = st.number_input("过渡时间 (秒)", min_value=0.5, max_value=5.0, step=0.5, value=G_config.get("VIDEO_TRANS_TIME", 1.5))

clip_start_min = st.number_input("片段开始时间随机范围 - 最小值 (秒)", min_value=0, value=G_config.get("CLIP_START_INTERVAL", [15, 75])[0])
clip_start_max = st.number_input("片段开始时间随机范围 - 最大值 (秒)", min_value=0, value=G_config.get("CLIP_START_INTERVAL", [15, 75])[1])

# ========== 其他 ==========
st.subheader("📋 其他")
use_all_cache = st.checkbox("使用本地缓存", value=G_config.get("USE_ALL_CACHE", False), help="跳过重新生成，使用已有缓存")
only_generate_clips = st.checkbox("仅生成片段", value=G_config.get("ONLY_GENERATE_CLIPS", False), help="不合成完整视频")
full_last_clip = st.checkbox("最后一段完整播放", value=G_config.get("FULL_LAST_CLIP", False))
default_comment_placeholders = st.checkbox("默认评论占位符", value=G_config.get("DEFAULT_COMMENT_PLACEHOLDERS", False))

# ========== 保存 ==========
st.divider()
if st.button("💾 保存所有配置", type="primary", use_container_width=True):
    G_config["DOWNLOADER"] = downloader
    G_config["DOWNLOAD_HIGH_RES"] = download_high_res
    G_config["NO_BILIBILI_CREDENTIAL"] = no_bilibili_credential
    G_config["SEARCH_MAX_RESULTS"] = search_max_results
    G_config["SEARCH_WAIT_TIME"] = (search_wait_min, search_wait_max)
    G_config["USE_PROXY"] = use_proxy
    G_config["PROXY_ADDRESS"] = proxy_address
    G_config["USE_YOUTUBE_API"] = use_youtube_api
    G_config["YOUTUBE_API_KEY"] = youtube_api_key if youtube_api_key else None
    G_config["USE_OAUTH"] = use_oauth
    G_config["USE_CUSTOM_PO_TOKEN"] = use_custom_po_token
    G_config["USE_AUTO_PO_TOKEN"] = use_auto_po_token
    G_config["CUSTOMER_PO_TOKEN"] = {"po_token": po_token, "visitor_data": visitor_data}
    G_config["VIDEO_RES"] = (video_res_w, video_res_h)
    G_config["VIDEO_BITRATE"] = video_bitrate
    G_config["CLIP_PLAY_TIME"] = clip_play_time
    G_config["VIDEO_TRANS_ENABLE"] = video_trans_enable
    G_config["VIDEO_TRANS_TIME"] = video_trans_time
    G_config["CLIP_START_INTERVAL"] = [clip_start_min, clip_start_max]
    G_config["USE_ALL_CACHE"] = use_all_cache
    G_config["ONLY_GENERATE_CLIPS"] = only_generate_clips
    G_config["FULL_LAST_CLIP"] = full_last_clip
    G_config["DEFAULT_COMMENT_PLACEHOLDERS"] = default_comment_placeholders
    write_global_config(G_config)
    st.success("✅ 配置已保存！")
    st.rerun()
