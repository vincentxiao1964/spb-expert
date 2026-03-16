import json
import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

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
        logger.warning("Skipping content check due to missing access token")
        return True, None 
        
    url = f"https://api.weixin.qq.com/wxa/msg_sec_check?access_token={token}"
    
    # version 2
    data = {
        "version": 2,
        "openid": openid,
        "scene": 2, # 2: Comment/Reply
        "content": content
    }
    
    try:
        response = requests.post(url, json=data)
        res_data = response.json()
        
        if res_data.get('errcode') == 0:
            result = res_data.get('result', {})
            label = result.get('label')
            if label == 100: # 100 is Normal
                return True, None
            else:
                return False, f"Content contains sensitive information (Label: {label})"
        elif res_data.get('errcode') == 87014:
             return False, "Content contains sensitive information"
        else:
            logger.error(f"WeChat msg_sec_check error: {res_data}")
            return True, None # Fail open on technical error
    except Exception as e:
        logger.error(f"Exception in msg_sec_check: {e}")
        return True, None
