from django.db.models import Sum, Count
from django.utils import timezone
from django.http import HttpResponse
from io import StringIO
import csv
from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from .models import Order, OrderLog, OrderRefund, Shipment
from .serializers import OrderSerializer, OrderRefundSerializer, ShipmentSerializer
from core.permissions import IsBuyerOrReadOnly
from core.permissions import IsMerchantOrReadOnly
from payments.models import PaymentIntent
from payments.providers import get_provider

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsBuyerOrReadOnly]

    def perform_create(self, serializer):
        buyer_user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(buyer_user=buyer_user)

    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def stats(self, request):
        qs = Order.objects.all()
        status_param = request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        created_from = request.query_params.get('created_from')
        created_to = request.query_params.get('created_to')
        if created_from:
            qs = qs.filter(created_at__gte=created_from)
        if created_to:
            qs = qs.filter(created_at__lte=created_to)
        total_orders = qs.count()
        total_amount = qs.aggregate(total=Sum('total_amount'))['total'] or 0
        by_status = qs.values('status').annotate(count=Count('id'), amount=Sum('total_amount')).order_by()
        return Response({
            'total_orders': total_orders,
            'total_amount': total_amount,
            'by_status': list(by_status),
        })

    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser], url_path='export')
    def export(self, request):
        qs = Order.objects.all().select_related('buyer_user', 'coupon')
        status_param = request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        created_from = request.query_params.get('created_from')
        created_to = request.query_params.get('created_to')
        if created_from:
            qs = qs.filter(created_at__gte=created_from)
        if created_to:
            qs = qs.filter(created_at__lte=created_to)
        output = StringIO()
        writer = csv.writer(output)
        header = [
            'id',
            'status',
            'buyer_name',
            'contact_phone',
            'buyer_user_id',
            'buyer_username',
            'total_amount',
            'coupon_code',
            'coupon_discount_amount',
            'created_at',
            'updated_at',
        ]
        writer.writerow(header)
        for o in qs:
            buyer_username = o.buyer_user.username if o.buyer_user_id else ''
            coupon_code = o.coupon.code if o.coupon_id else ''
            row = [
                o.id,
                o.status,
                o.buyer_name,
                o.contact_phone,
                o.buyer_user_id or '',
                buyer_username,
                str(o.total_amount),
                coupon_code,
                str(o.coupon_discount_amount),
                o.created_at.isoformat(),
                o.updated_at.isoformat(),
            ]
            writer.writerow(row)
        resp = HttpResponse(output.getvalue(), content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
        return resp

    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        qs = Order.objects.filter(buyer_user=request.user).order_by('-created_at')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({'error': 'No status provided'}, status=status.HTTP_400_BAD_REQUEST)
        blocked = [Order.Status.COMPLETED]
        if order.status in blocked and new_status != Order.Status.COMPLETED:
            return Response({'error': 'Completed order immutable'}, status=status.HTTP_403_FORBIDDEN)
        order.status = new_status
        order.save()
        OrderLog.objects.create(order=order, action=f'status:{new_status}', note=request.data.get('note', ''))
        return Response({'status': 'updated', 'new_status': order.status})

    @decorators.action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        order.status = Order.Status.PAID
        order.save()
        OrderLog.objects.create(order=order, action='pay', note=request.data.get('note', ''))
        return Response({'status': 'paid'})

    @decorators.action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        order = self.get_object()
        order.status = Order.Status.SHIPPED
        order.save()
        OrderLog.objects.create(order=order, action='ship', note=request.data.get('note', ''))
        return Response({'status': 'shipped'})

    @decorators.action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        order = self.get_object()
        order.status = Order.Status.COMPLETED
        order.save()
        OrderLog.objects.create(order=order, action='complete', note=request.data.get('note', ''))
        return Response({'status': 'completed'})

    @decorators.action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        order.status = Order.Status.CANCELLED
        order.save()
        OrderLog.objects.create(order=order, action='cancel', note=request.data.get('note', ''))
        return Response({'status': 'cancelled'})

    @decorators.action(detail=True, methods=['post'])
    def confirm_receive(self, request, pk=None):
        order = self.get_object()
        order.status = Order.Status.COMPLETED
        order.save()
        OrderLog.objects.create(order=order, action='confirm_receive', note=request.data.get('note', ''))
        from core.models import Notification
        Notification.objects.create(
            recipient=request.user,
            type=Notification.Type.MESSAGE,
            title='请评价订单',
            message='订单已完成，请前往评价',
            content_object=order
        )
        return Response({'status': 'completed'})

    @decorators.action(detail=True, methods=['post'])
    def create_intent(self, request, pk=None):
        order = self.get_object()
        provider = request.data.get('provider', 'mock')
        intent = PaymentIntent.objects.create(order=order, amount=order.total_amount, provider=provider)
        provider_obj = get_provider(intent.provider)
        params = provider_obj.build_params(intent)
        intent.reference = params.get('reference', intent.reference)
        intent.params = params
        intent.status = PaymentIntent.Status.PROCESSING
        intent.save()
        OrderLog.objects.create(order=order, action='payment_intent_created', note=f'intent:{intent.id}')
        return Response({'intent_id': intent.id, 'provider': intent.provider, 'reference': intent.reference, 'params': intent.params, 'status': intent.status})

    @decorators.action(detail=True, methods=['get'])
    def payment_intents(self, request, pk=None):
        order = self.get_object()
        intents = order.payment_intents.order_by('-created_at').values('id', 'provider', 'reference', 'status', 'created_at')
        return Response({'items': list(intents)})

    @decorators.action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        order = self.get_object()
        logs = order.logs.order_by('-created_at').values('id', 'action', 'note', 'created_at')
        return Response({'items': list(logs)})

    @decorators.action(detail=True, methods=['get'])
    def shipments(self, request, pk=None):
        order = self.get_object()
        shipments = order.shipments.order_by('-created_at').values('id', 'status', 'carrier', 'tracking_number', 'shipped_at', 'delivered_at', 'created_at')
        return Response({'items': list(shipments)})

class OrderRefundViewSet(viewsets.ModelViewSet):
    queryset = OrderRefund.objects.all().order_by('-created_at')
    serializer_class = OrderRefundSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        refund = serializer.save()
        OrderLog.objects.create(order=refund.order, action='refund_request', note=str(refund.amount))

    @decorators.action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        refund = self.get_object()
        u = request.user
        if not (hasattr(u, 'profile') and u.profile.is_merchant):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        refund.status = OrderRefund.Status.APPROVED
        refund.save()
        OrderLog.objects.create(order=refund.order, action='refund_approve', note=str(refund.amount))
        return Response({'status': 'approved'})

    @decorators.action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        refund = self.get_object()
        u = request.user
        if not (hasattr(u, 'profile') and u.profile.is_merchant):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        refund.status = OrderRefund.Status.REJECTED
        refund.save()
        OrderLog.objects.create(order=refund.order, action='refund_reject', note=request.data.get('note', ''))
        return Response({'status': 'rejected'})

    @decorators.action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        refund = self.get_object()
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        refund.status = OrderRefund.Status.PROCESSED
        refund.save()
        OrderLog.objects.create(order=refund.order, action='refund_process', note=str(refund.amount))
        return Response({'status': 'processed'})

class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all().order_by('-created_at')
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        shipment = serializer.save()
        OrderLog.objects.create(order=shipment.order, action='shipment_create', note=shipment.tracking_number or '')

    @decorators.action(detail=True, methods=['post'])
    def dispatch(self, request, pk=None):
        shipment = self.get_object()
        shipment.status = Shipment.Status.DISPATCHED
        shipment.shipped_at = timezone.now()
        shipment.save()
        order = shipment.order
        order.status = Order.Status.SHIPPED
        order.save()
        OrderLog.objects.create(order=order, action='shipment_dispatch', note=shipment.tracking_number or '')
        return Response({'status': 'dispatched'})

    @decorators.action(detail=True, methods=['post'])
    def delivered(self, request, pk=None):
        shipment = self.get_object()
        shipment.status = Shipment.Status.DELIVERED
        shipment.delivered_at = timezone.now()
        shipment.save()
        order = shipment.order
        OrderLog.objects.create(order=order, action='shipment_delivered', note=shipment.tracking_number or '')
        from core.models import Notification
        if order.buyer_user:
            Notification.objects.create(
                recipient=order.buyer_user,
                type=Notification.Type.MESSAGE,
                title='包裹已妥投，请确认收货',
                message='请前往订单详情页确认收货',
                content_object=order
            )
        return Response({'status': 'delivered'})
