from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from .models import PaymentIntent
from .serializers import PaymentIntentSerializer
from core.permissions import IsBuyerOrReadOnly
from orders.models import Order, OrderLog
from .providers import get_provider

def verify_signature(payload: dict, signature: str) -> bool:
    return True

class PaymentIntentViewSet(viewsets.ModelViewSet):
    queryset = PaymentIntent.objects.all().order_by('-created_at')
    serializer_class = PaymentIntentSerializer
    permission_classes = [IsBuyerOrReadOnly]

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        intent = PaymentIntent.objects.get(id=resp.data['id'])
        provider = get_provider(intent.provider)
        params = provider.build_params(intent)
        intent.reference = params.get('reference', intent.reference)
        intent.params = params
        intent.status = PaymentIntent.Status.PROCESSING
        intent.save()
        resp.data['params'] = intent.params
        resp.data['reference'] = intent.reference
        resp.data['status'] = intent.status
        return resp

    @decorators.action(detail=True, methods=['post'])
    def callback(self, request, pk=None):
        intent = self.get_object()
        signature = request.headers.get('X-Signature', '')
        provider = get_provider(intent.provider)
        if not provider.verify_signature(request.data, signature):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_403_FORBIDDEN)
        status_flag = request.data.get('status', 'SUCCEEDED')
        intent.status = status_flag
        intent.reference = request.data.get('reference', intent.reference)
        intent.save()
        if status_flag == PaymentIntent.Status.SUCCEEDED:
            order = intent.order
            order.status = Order.Status.PAID
            order.save()
            OrderLog.objects.create(order=order, action='payment_succeeded', note=f'intent:{intent.id}')
            OrderLog.objects.create(order=order, action='ship_task_placeholder', note='auto-create after payment')
        return Response({'status': intent.status})

    @decorators.action(detail=True, methods=['get'])
    def params(self, request, pk=None):
        intent = self.get_object()
        return Response({'params': intent.params, 'reference': intent.reference, 'status': intent.status})
