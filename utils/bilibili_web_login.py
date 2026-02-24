"""
B站 Web 登录 - 在网页中显示二维码，无需 tkinter 或终端
使用 Bilibili 官方 API 实现二维码登录
"""
import requests
import qrcode
import io
import time
from typing import Optional, Tuple
from bilibili_api import Credential, user, sync

# B站二维码登录 API（Web 端，新版）
API_QR_GENERATE = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
API_QR_POLL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
# 备用旧版 API
API_QR_GENERATE_OLD = "https://passport.bilibili.com/qrcode/getLoginUrl"
API_QR_POLL_OLD = "https://passport.bilibili.com/qrcode/getLoginInfo"


def get_qrcode_image(url: str, size: int = 256) -> bytes:
    """生成二维码图片的 bytes"""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def fetch_qrcode_info(proxy: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    获取二维码登录信息
    Returns: (url, qrcode_key) 或 (None, None)
    """
    proxies = {"http": proxy, "https": proxy} if proxy else None
    # 优先尝试新版 API
    try:
        r = requests.get(API_QR_GENERATE, timeout=10, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        if data.get("code") == 0:
            return data["data"]["url"], data["data"]["qrcode_key"]
    except Exception as e:
        print(f"新版 API 获取二维码失败: {e}")
    # 备用：旧版 API
    try:
        r = requests.get(API_QR_GENERATE_OLD, timeout=10, proxies=proxies)
        r.raise_for_status()
        data = r.json()
        if data.get("code") == 0:
            return data["data"]["url"], data["data"]["oauthKey"]
    except Exception as e:
        print(f"旧版 API 获取二维码失败: {e}")
    return None, None


def poll_login_status(qrcode_key: str, proxy: Optional[str] = None) -> dict:
    """
    轮询登录状态
    Returns: {"status": "success"|"waiting"|"expired", "cookies": {...} or None}
    """
    proxies = {"http": proxy, "https": proxy} if proxy else None
    # 新版 API (GET)
    try:
        r = requests.get(
            API_QR_POLL,
            params={"qrcode_key": qrcode_key},
            timeout=10,
            proxies=proxies)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 0:
            return {"status": "error", "message": data.get("message", "未知错误")}
        d = data["data"]
        if d.get("code") == 0:
            cookies = d.get("cookie_info", {}).get("cookies", [])
            cookie_dict = {c["name"]: c["value"] for c in cookies}
            return {"status": "success", "cookies": cookie_dict}
        elif d.get("code") == 86038:
            return {"status": "expired"}
        return {"status": "waiting"}
    except Exception:
        pass
    # 备用：旧版 API (POST, oauthKey)
    try:
        r = requests.post(
            API_QR_POLL_OLD,
            data={"oauthKey": qrcode_key},
            timeout=10,
            proxies=proxies)
        r.raise_for_status()
        data = r.json()
        if data.get("status") is True:
            # 旧版返回 Set-Cookie 或 data 中的 cookies
            cookies = data.get("data", {}).get("cookie_info", {}).get("cookies", [])
            if not cookies and "url" in data.get("data", {}):
                return {"status": "success", "cookies": data["data"]}
            cookie_dict = {c["name"]: c["value"] for c in cookies}
            return {"status": "success", "cookies": cookie_dict}
        elif data.get("data") == -2:
            return {"status": "expired"}
        return {"status": "waiting"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def cookies_to_credential(cookie_dict: dict) -> Tuple[Optional[Credential], Optional[str]]:
    """
    将 B站 cookies 转为 bilibili-api 的 Credential
    Returns: (Credential, error_message)
    """
    sessdata = cookie_dict.get("SESSDATA")
    bili_jct = cookie_dict.get("bili_jct")
    buvid3 = cookie_dict.get("buvid3", "")
    dedeuserid = cookie_dict.get("DedeUserID", "")
    ac_time_value = cookie_dict.get("ac_time_value", "")

    if not sessdata or not bili_jct:
        return None, "缺少必要 cookie (SESSDATA, bili_jct)"

    try:
        cred = Credential(
            sessdata=sessdata,
            bili_jct=bili_jct,
            buvid3=buvid3 or None,
            dedeuserid=dedeuserid or None,
            ac_time_value=ac_time_value or None
        )
        # 验证
        if not sync(cred.check_valid()):
            return None, "凭证无效或已过期"
        return cred, None
    except Exception as e:
        return None, str(e)
