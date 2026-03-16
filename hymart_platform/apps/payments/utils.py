import hashlib
import time
import uuid
import requests
import xml.etree.ElementTree as ET
from django.conf import settings

class WeChatPay:
    def __init__(self, appid, mch_id, api_key, notify_url):
        self.appid = appid
        self.mch_id = mch_id
        self.api_key = api_key
        self.notify_url = notify_url
        self.unified_order_url = "https://api.mch.weixin.qq.com/pay/unifiedorder"

    def generate_nonce_str(self):
        return str(uuid.uuid4()).replace('-', '')

    def sign(self, params):
        # Sort keys
        sorted_keys = sorted(params.keys())
        # Create stringA
        stringA = '&'.join([f"{k}={params[k]}" for k in sorted_keys if params[k] is not None])
        # Add key
        stringSignTemp = f"{stringA}&key={self.api_key}"
        # MD5 and Upper
        return hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest().upper()

    def to_xml(self, params):
        xml = "<xml>"
        for k, v in params.items():
            if isinstance(v, (int, float)):
                xml += f"<{k}>{v}</{k}>"
            else:
                xml += f"<{k}><![CDATA[{v}]]></{k}>"
        xml += "</xml>"
        return xml

    def parse_xml(self, xml_str):
        try:
            root = ET.fromstring(xml_str)
            return {child.tag: child.text for child in root}
        except Exception:
            return {}

    def unified_order(self, out_trade_no, total_fee, body, openid, spbill_create_ip):
        params = {
            'appid': self.appid,
            'mch_id': self.mch_id,
            'nonce_str': self.generate_nonce_str(),
            'body': body,
            'out_trade_no': out_trade_no,
            'total_fee': total_fee, # In cents
            'spbill_create_ip': spbill_create_ip,
            'notify_url': self.notify_url,
            'trade_type': 'JSAPI',
            'openid': openid
        }
        params['sign'] = self.sign(params)
        
        xml_data = self.to_xml(params)
        
        # Check if we are in mock mode or test mode
        # Default to True if keys are placeholders
        if self.appid == 'your_appid' or getattr(settings, 'MOCK_PAYMENT', True):
            return {
                'return_code': 'SUCCESS',
                'result_code': 'SUCCESS',
                'prepay_id': f'wx_mock_{int(time.time())}'
            }
            
        try:
            response = requests.post(self.unified_order_url, data=xml_data.encode('utf-8'))
            response.encoding = 'utf-8'
            return self.parse_xml(response.text)
        except Exception as e:
            return {'return_code': 'FAIL', 'return_msg': str(e)}

    def verify_notify(self, data):
        sign = data.pop('sign', None)
        if not sign:
            return False
        calculated_sign = self.sign(data)
        return calculated_sign == sign

    def get_jsapi_params(self, prepay_id):
        params = {
            'appId': self.appid,
            'timeStamp': str(int(time.time())),
            'nonceStr': self.generate_nonce_str(),
            'package': f"prepay_id={prepay_id}",
            'signType': 'MD5'
        }
        params['paySign'] = self.sign(params)
        return params
