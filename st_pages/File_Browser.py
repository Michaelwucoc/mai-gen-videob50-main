"""
Web 文件浏览 - 在网页中查看生成的图片、视频等，无需打开系统文件夹
"""
import streamlit as st
import os
from utils.PathUtils import get_user_media_dir
from utils.PageUtils import get_game_type_text

st.set_page_config(page_title="文件浏览", page_icon="📂", layout="wide")

st.header("📂 文件浏览")
st.markdown("在网页中查看生成的成绩图片、下载的视频、导出的视频等。")

# 支持浏览的目录类型
FOLDER_TYPES = {
    "images": ("成绩背景图片", "根据当前存档生成的所有成绩展示图片"),
    "output_videos": ("生成的视频", "合成后的视频片段和完整视频"),
    "downloads": ("下载的谱面视频", "从 B站/YouTube 下载的谱面确认视频"),
}

username = st.session_state.get("username")
archive_name = st.session_state.get("archive_name")
G_type = st.session_state.get("game_type", "maimai")

# 获取要浏览的目录（支持 query 参数 ?folder=xxx）
folder = st.query_params.get("folder") or st.session_state.get("file_browser_folder", "images")
if folder not in FOLDER_TYPES:
    folder = "images"
st.session_state.file_browser_folder = folder

title, desc = FOLDER_TYPES[folder]
st.subheader(f"📁 {title}")
st.caption(desc)

# 确定路径
if folder == "images":
    if not username:
        st.warning("请先在首页加载存档。")
        st.stop()
    paths = get_user_media_dir(username, game_type=G_type)
    browse_path = paths["image_dir"]
elif folder == "output_videos":
    if not username:
        st.warning("请先在首页加载存档。")
        st.stop()
    paths = get_user_media_dir(username, game_type=G_type)
    browse_path = paths["output_video_dir"]
else:  # downloads
    browse_path = "./videos/downloads"

abs_path = os.path.abspath(browse_path)

# 显示路径
st.code(abs_path, language=None)
st.caption("💡 上述路径为文件在服务器上的实际位置")

if not os.path.exists(browse_path):
    st.warning(f"目录不存在或为空：{browse_path}")
    st.info("请先完成对应的生成步骤（如生成成绩图片、下载视频）。")
    st.stop()

# 列出文件
files = sorted([f for f in os.listdir(browse_path) if not f.startswith(".")])
if not files:
    st.info("此目录为空。")
    st.stop()

# 按类型分组
img_ext = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
vid_ext = {".mp4", ".mov", ".avi", ".webm", ".mkv"}

images = [f for f in files if os.path.splitext(f)[1].lower() in img_ext]
videos = [f for f in files if os.path.splitext(f)[1].lower() in vid_ext]
others = [f for f in files if f not in images and f not in videos]

# 显示图片
if images:
    st.markdown("### 🖼️ 图片预览")
    cols = st.columns(min(4, len(images)))
    for i, f in enumerate(images[:20]):  # 最多显示 20 张
        with cols[i % 4]:
            fp = os.path.join(browse_path, f)
            try:
                st.image(fp, caption=f, use_container_width=True)
            except Exception:
                st.caption(f)
    if len(images) > 20:
        st.caption(f"共 {len(images)} 张图片，仅展示前 20 张")

# 显示视频
if videos:
    st.markdown("### 🎬 视频列表")
    for f in videos:
        fp = os.path.join(browse_path, f)
        with st.expander(f"▶️ {f}"):
            try:
                st.video(fp)
            except Exception:
                st.caption(f"路径: {fp}")
                with open(fp, "rb") as vf:
                    st.download_button("下载视频", vf, file_name=f, key=f"dl_{f}")

# 其他文件
if others:
    st.markdown("### 📄 其他文件")
    st.write(", ".join(others))

# 快捷切换
st.divider()
st.markdown("📂 切换浏览目录")
selected = st.radio(
    "选择要浏览的目录",
    options=list(FOLDER_TYPES.keys()),
    format_func=lambda k: FOLDER_TYPES[k][0],
    index=list(FOLDER_TYPES.keys()).index(folder),
    horizontal=True,
    key="file_browser_folder_select"
)
if selected != folder:
    st.session_state.file_browser_folder = selected
    st.rerun()
