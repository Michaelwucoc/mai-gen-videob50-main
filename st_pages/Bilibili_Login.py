"""
B站 Web 登录 - 在网页中显示二维码扫码登录
"""
import streamlit as st
import pickle
import os
from utils.bilibili_web_login import (
    fetch_qrcode_info,
    get_qrcode_image,
    poll_login_status,
    cookies_to_credential,
)
from utils.PageUtils import read_global_config

st.set_page_config(page_title="B站登录", page_icon="📱", layout="centered")

st.header("📱 B站扫码登录")
st.markdown("使用 B站 App 扫描下方二维码完成登录，登录后可正常搜索和下载 B站 视频。")

# 获取代理配置
try:
    config = read_global_config()
    proxy = None
    if config.get("USE_PROXY"):
        addr = config.get("PROXY_ADDRESS", "127.0.0.1:7890")
        proxy = f"http://{addr}"
except Exception:
    proxy = None

credential_path = "./cred_datas/bilibili_cred.pkl"
os.makedirs(os.path.dirname(credential_path), exist_ok=True)

# 初始化 session state
if "bili_qrcode_key" not in st.session_state:
    st.session_state.bili_qrcode_key = None
if "bili_qrcode_url" not in st.session_state:
    st.session_state.bili_qrcode_url = None
if "bili_login_success" not in st.session_state:
    st.session_state.bili_login_success = False

# 获取二维码
if st.session_state.bili_qrcode_key is None and not st.session_state.bili_login_success:
    with st.spinner("正在获取二维码..."):
        url, key, err_msg = fetch_qrcode_info(proxy)
    if url and key:
        st.session_state.bili_qrcode_url = url
        st.session_state.bili_qrcode_key = key
    else:
        st.error("获取二维码失败，请检查网络或代理设置后重试。")
        if err_msg:
            st.code(err_msg, language=None)
        st.markdown("**排查建议：** 若在海外或无法直连 B站，请在「系统设置」中开启代理并填写正确的 `PROXY_ADDRESS`。")
        st.stop()

# 显示二维码（仅在未登录成功时）
if not st.session_state.bili_login_success:
    qr_bytes = get_qrcode_image(st.session_state.bili_qrcode_url)
    st.image(qr_bytes, caption="请使用 B站 App 扫描", width=256)

    # 轮询登录状态（使用 fragment 每 2 秒自动检查）
    @st.fragment(run_every="2s")
    def poll_login():
        if st.session_state.bili_login_success or st.session_state.bili_qrcode_key is None:
            return
        result = poll_login_status(st.session_state.bili_qrcode_key, proxy)
        if result["status"] == "success":
            cred, err = cookies_to_credential(result["cookies"])
            if cred:
                with open(credential_path, "wb") as f:
                    pickle.dump(cred, f)
                from bilibili_api import user, sync
                name = sync(user.get_self_info(cred))["name"]
                st.success(f"✅ 登录成功！欢迎，{name}")
                st.session_state.bili_qrcode_key = None
                st.session_state.bili_qrcode_url = None
                st.session_state.bili_login_success = True
                st.rerun()
            else:
                st.error(f"登录失败: {err}")
        elif result["status"] == "expired":
            st.warning("二维码已过期，请点击下方按钮重新获取")
            st.session_state.bili_qrcode_key = None
            st.session_state.bili_qrcode_url = None
        else:
            st.info("⏳ 等待扫码中... 请使用 B站 App 扫描上方二维码")

    poll_login()

    if st.button("🔄 刷新二维码"):
        st.session_state.bili_qrcode_key = None
        st.session_state.bili_qrcode_url = None
        st.rerun()
else:
    st.success("您已登录 B站，可前往「搜索谱面确认视频」页面使用。")

st.caption("登录凭证将保存到本地，下次无需重新登录。")
