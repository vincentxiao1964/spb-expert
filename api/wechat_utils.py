import json
import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def _is_strict_mode():
    strict = getattr(settings, 'WECHAT_CONTENT_SECURITY_STRICT', None)
    if strict is None:
        return not getattr(settings, 'DEBUG', False)
    return bool(strict)

def get_wechat_access_token():
    """
    Get WeChat Mini Program Access Token, using cache.
    """
    token = cache.get('wechat_access_token')
    if token:
        return token

    appid = getattr(settings, 'WECHAT_MINI_PROGRAM_APP_ID', None)
    secret = getattr(settings, 'WECHAT_MINI_PROGRAM_APP_SECRET', None)

    if not appid or not secret:
        logger.error("WeChat credentials not configured")
        return None

    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    try:
        response = requests.get(url)
        data = response.json()
        if 'access_token' in data:
            token = data['access_token']
            expires_in = data.get('expires_in', 7200)
            # Cache for slightly less than expiration time
            cache.set('wechat_access_token', token, expires_in - 200)
            return token
        else:
            logger.error(f"Error getting WeChat access token: {data}")
            return None
    except Exception as e:
        logger.error(f"Exception getting WeChat access token: {e}")
        return None

def check_msg_sec(content, openid):
    """
    Check text content for security violations using WeChat msg_sec_check (v2).
    Returns (True, None) if safe.
    Returns (False, reason) if risky.
    """
    if not content:
        return True, None
        
    token = get_wechat_access_token()
    if not token:
        logger.error("WeChat access token missing")
        if _is_strict_mode():
            return False, "Content security check is temporarily unavailable. Please try again."
        return True, None 
        
    url = f"https://api.weixin.qq.com/wxa/msg_sec_check?access_token={token}"
    
    openid = (openid or '').strip()
    use_v2 = bool(openid)
    
    try:
        if use_v2:
            data = {
                "version": 2,
                "openid": openid,
                "scene": 2,
                "content": content
            }
            response = requests.post(url, json=data, timeout=8)
            res_data = response.json()
            if res_data.get('errcode') == 0:
                result = res_data.get('result', {})
                label = result.get('label')
                if label == 100:
                    return True, None
                return False, "Content contains sensitive information"
            if res_data.get('errcode') == 87014:
                return False, "Content contains sensitive information"
            logger.error(f"WeChat msg_sec_check v2 error: {res_data}")
            if _is_strict_mode():
                return False, "Content security check is temporarily unavailable. Please try again."
            return True, None

        data = { "content": content }
        response = requests.post(url, json=data, timeout=8)
        res_data = response.json()
        if res_data.get('errcode') == 0:
            result = res_data.get('result')
            if isinstance(result, dict) and 'label' in result:
                label = result.get('label')
                if label == 100:
                    return True, None
                return False, "Content contains sensitive information"
            return True, None
        if res_data.get('errcode') == 87014:
            return False, "Content contains sensitive information"
        logger.error(f"WeChat msg_sec_check v1 error: {res_data}")
        if _is_strict_mode():
            return False, "Content security check is temporarily unavailable. Please try again."
        return True, None
    except Exception as e:
        logger.error(f"Exception in msg_sec_check: {e}")
        if _is_strict_mode():
            return False, "Content security check is temporarily unavailable. Please try again."
        return True, None


def check_img_sec(file_bytes, filename='image.jpg'):
    if not file_bytes:
        return True, None

    token = get_wechat_access_token()
    if not token:
        logger.error("WeChat access token missing (img check)")
        if _is_strict_mode():
            return False, "Content security check is temporarily unavailable. Please try again."
        return True, None

    url = f"https://api.weixin.qq.com/wxa/img_sec_check?access_token={token}"
    try:
        files = {'media': (filename, file_bytes)}
        response = requests.post(url, files=files, timeout=15)
        res_data = response.json()
        if res_data.get('errcode') == 0:
            return True, None
        if res_data.get('errcode') == 87014:
            return False, "Image contains sensitive information"
        logger.error(f"WeChat img_sec_check error: {res_data}")
        if _is_strict_mode():
            return False, "Content security check is temporarily unavailable. Please try again."
        return True, None
    except Exception as e:
        logger.error(f"Exception in img_sec_check: {e}")
        if _is_strict_mode():
            return False, "Content security check is temporarily unavailable. Please try again."
        return True, None


def submit_media_check_async(media_url, media_type=2, openid='', scene=2):
    media_url = (media_url or '').strip()
    openid = (openid or '').strip()

    if not media_url:
        return None, "Missing media_url"

    token = get_wechat_access_token()
    if not token:
        if _is_strict_mode():
            return None, "Content security check is temporarily unavailable. Please try again."
        return None, "WeChat access token missing"

    url = f"https://api.weixin.qq.com/wxa/media_check_async?access_token={token}"

    try:
        if openid:
            payload = {
                "openid": openid,
                "scene": int(scene),
                "version": 2,
                "media_url": media_url,
                "media_type": int(media_type),
            }
        else:
            payload = {
                "media_url": media_url,
                "media_type": int(media_type),
            }

        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        if res_data.get('errcode') == 0 and res_data.get('trace_id'):
            return res_data.get('trace_id'), None
        logger.error(f"WeChat media_check_async error: {res_data}")
        if _is_strict_mode():
            return None, "Content security check is temporarily unavailable. Please try again."
        return None, res_data.get('errmsg') or 'media_check_async error'
    except Exception as e:
        logger.error(f"Exception in media_check_async: {e}")
        if _is_strict_mode():
            return None, "Content security check is temporarily unavailable. Please try again."
        return None, "media_check_async error"
