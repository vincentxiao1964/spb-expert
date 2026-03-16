from typing import Dict
from .models import PaymentIntent
from django.conf import settings

class BaseProvider:
    name = 'mock'
    def build_params(self, intent: PaymentIntent) -> Dict:
        ref = f"MOCK-{intent.id}"
        url = f"https://hymartt.com/mockpay?intent={intent.id}&ref={ref}"
        return {'redirect_url': url, 'reference': ref, 'provider': intent.provider, 'amount': str(intent.amount)}
    def verify_signature(self, payload: dict, signature: str) -> bool:
        return True

class WeChatProvider(BaseProvider):
    name = 'wechat'
    def build_params(self, intent: PaymentIntent) -> Dict:
        ref = f"WX-{intent.id}"
        return {'appId': '', 'timeStamp': '0', 'nonceStr': ref, 'package': f'prepay_id={ref}', 'signType': 'RSA', 'paySign': '', 'reference': ref, 'provider': intent.provider}
    def verify_signature(self, payload: dict, signature: str) -> bool:
        return True

class AlipayProvider(BaseProvider):
    name = 'alipay'
    def build_params(self, intent: PaymentIntent) -> Dict:
        ref = f"ALI-{intent.id}"
        return {'trade_no': ref, 'timestamp': '0', 'sign_type': 'RSA2', 'sign': '', 'provider': intent.provider, 'reference': ref}
    def verify_signature(self, payload: dict, signature: str) -> bool:
        return True

_providers = {
    'mock': BaseProvider(),
    'wechat': WeChatProvider(),
    'alipay': AlipayProvider(),
}

def get_provider(name: str) -> BaseProvider:
    return _providers.get(name, _providers['mock'])
