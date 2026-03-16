from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import time
from .models import PaymentTransaction
from .utils import WeChatPay
from apps.orders.models import Order

logger = logging.getLogger(__name__)

# Initialize WeChat Pay (Should be in settings)
# For now, use placeholders if not set
WECHAT_CONFIG = getattr(settings, 'WECHAT_PAY', {
    'appid': 'your_appid',
    'mch_id': 'your_mch_id',
    'api_key': 'your_api_key',
    'notify_url': 'https://www.barge-expert.com/api/payments/notify/'
})

wx_pay = WeChatPay(
    appid=WECHAT_CONFIG.get('appid'),
    mch_id=WECHAT_CONFIG.get('mch_id'),
    api_key=WECHAT_CONFIG.get('api_key'),
    notify_url=WECHAT_CONFIG.get('notify_url')
)

class PaymentViewSet(viewsets.ViewSet):
    """
    Handle Payment Operations
    """
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """
        Create a WeChat Pay order for a given system Order ID.
        """
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'error': 'Order ID required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            
        if order.status != Order.Status.PENDING:
            return Response({'error': 'Order is not pending payment'}, status=status.HTTP_400_BAD_REQUEST)
            
        if request.user != order.buyer:
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # Generate unique out_trade_no
        out_trade_no = f"{order.order_number}_{int(time.time())}"
        
        # Calculate amount in cents
        total_fee = int(order.total_amount * 100)
        
        # Get user openid (assuming stored in social_auth or profile)
        # For MVP, we might need to pass it or get from user model if we integrated login
        # Assuming request.user.openid exists or passed in body
        openid = request.data.get('openid')
        # Try to find openid on user object if not provided
        if not openid and hasattr(request.user, 'openid'):
            openid = request.user.openid
        
        # Fallback for testing/mock
        if not openid:
            # If we are in mock mode, we can use a fake openid
            if getattr(settings, 'MOCK_PAYMENT', True):
                openid = 'test_openid'
            else:
                return Response({'error': 'OpenID required for payment'}, status=status.HTTP_400_BAD_REQUEST)

        # Call Unified Order
        result = wx_pay.unified_order(
            out_trade_no=out_trade_no,
            total_fee=total_fee,
            body=f"Order {order.order_number}",
            openid=openid,
            spbill_create_ip=request.META.get('REMOTE_ADDR', '127.0.0.1')
        )
        
        if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
            prepay_id = result.get('prepay_id')
            
            # Save Transaction Record
            PaymentTransaction.objects.create(
                order=order,
                out_trade_no=out_trade_no,
                amount=order.total_amount,
                request_data=str(result),
                status=PaymentTransaction.Status.PENDING
            )
            
            # Get JSAPI params for frontend
            jsapi_params = wx_pay.get_jsapi_params(prepay_id)
            return Response(jsapi_params)
        else:
             return Response({'error': 'Payment creation failed', 'detail': result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], authentication_classes=[], permission_classes=[])
    def notify(self, request):
        """
        WeChat Pay Callback
        """
        try:
            xml_data = request.body.decode('utf-8')
            data = wx_pay.parse_xml(xml_data)
            
            if wx_pay.verify_notify(data):
                if data.get('result_code') == 'SUCCESS':
                    out_trade_no = data.get('out_trade_no')
                    transaction_id = data.get('transaction_id')
                    
                    try:
                        txn = PaymentTransaction.objects.get(out_trade_no=out_trade_no)
                        if txn.status != PaymentTransaction.Status.SUCCESS:
                            txn.status = PaymentTransaction.Status.SUCCESS
                            txn.transaction_id = transaction_id
                            txn.response_data = xml_data
                            txn.save()
                            
                            # Update Order Status
                            order = txn.order
                            if order.status == Order.Status.PENDING:
                                order.status = Order.Status.PAID
                                order.save()
                                
                    except PaymentTransaction.DoesNotExist:
                        logger.error(f"Payment notification for unknown transaction: {out_trade_no}")
                        
                    return HttpResponse('<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>', content_type='text/xml')
            
            return HttpResponse('<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[SIGNERROR]]></return_msg></xml>', content_type='text/xml')
            
        except Exception as e:
            logger.error(f"Payment notify error: {e}")
            return HttpResponse('<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[ERROR]]></return_msg></xml>', content_type='text/xml')
