from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, decorators
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from orders.models import Order, OrderItem
from store.models import Product
from services.models import ServiceListing
from market.models import Coupon, UserCoupon

def health(request):
    return JsonResponse({"status": "ok", "app": "hymart"})


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        User = get_user_model()
        total_users = User.objects.count()
        merchants = User.objects.filter(profile__is_merchant=True).count()
        buyers = User.objects.filter(profile__is_buyer=True).count()
        created_from = request.query_params.get('created_from')
        created_to = request.query_params.get('created_to')
        orders_qs = Order.objects.all()
        if created_from:
            orders_qs = orders_qs.filter(created_at__gte=created_from)
        if created_to:
            orders_qs = orders_qs.filter(created_at__lte=created_to)
        orders_total = orders_qs.count()
        orders_amount = orders_qs.aggregate(total=Sum('total_amount'))['total'] or 0
        completed_qs = orders_qs.filter(status=Order.Status.COMPLETED)
        completed_total = completed_qs.count()
        completed_amount = completed_qs.aggregate(total=Sum('total_amount'))['total'] or 0
        products_active = Product.objects.filter(is_active=True, is_approved=True).count()
        services_active = ServiceListing.objects.filter(is_active=True, is_approved=True).count()
        coupons_total = Coupon.objects.count()
        coupons_active = Coupon.objects.filter(status=Coupon.Status.ACTIVE).count()
        user_coupons_qs = UserCoupon.objects.all()
        if created_from:
            user_coupons_qs = user_coupons_qs.filter(created_at__gte=created_from)
        if created_to:
            user_coupons_qs = user_coupons_qs.filter(created_at__lte=created_to)
        user_coupons_total = user_coupons_qs.count()
        user_coupons_used = user_coupons_qs.filter(status=UserCoupon.Status.USED).count()
        coupons_discount_sum = orders_qs.aggregate(total=Sum('coupon_discount_amount'))['total'] or 0
        return Response({
            'users': {
                'total': total_users,
                'merchants': merchants,
                'buyers': buyers,
            },
            'orders': {
                'total': orders_total,
                'total_amount': orders_amount,
                'completed': completed_total,
                'completed_amount': completed_amount,
            },
            'catalog': {
                'products_active': products_active,
                'services_active': services_active,
            },
            'coupons': {
                'total': coupons_total,
                'active': coupons_active,
                'claimed': user_coupons_total,
                'used': user_coupons_used,
                'total_discount_amount': coupons_discount_sum,
            },
        })


class MerchantDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        u = request.user
        profile = getattr(u, 'profile', None)
        if not (profile and profile.is_merchant):
            return Response({'error': 'not_merchant'}, status=403)
        created_from = request.query_params.get('created_from')
        created_to = request.query_params.get('created_to')
        products_qs = Product.objects.filter(owner=u, is_active=True)
        services_qs = ServiceListing.objects.filter(owner=u, is_active=True)
        products_count = products_qs.count()
        services_count = services_qs.count()
        items_qs = OrderItem.objects.filter(
            Q(product__owner=u) | Q(service__owner=u)
        ).select_related('order')
        if created_from:
            items_qs = items_qs.filter(order__created_at__gte=created_from)
        if created_to:
            items_qs = items_qs.filter(order__created_at__lte=created_to)
        total_orders_ids = set()
        completed_orders_ids = set()
        total_sales_amount = 0
        completed_sales_amount = 0
        for it in items_qs:
            order = it.order
            line_total = it.price * it.quantity
            total_orders_ids.add(order.id)
            total_sales_amount += line_total
            if order.status == Order.Status.COMPLETED:
                completed_orders_ids.add(order.id)
                completed_sales_amount += line_total
        total_orders = len(total_orders_ids)
        completed_orders = len(completed_orders_ids)
        return Response({
            'catalog': {
                'products_active': products_count,
                'services_active': services_count,
            },
            'sales': {
                'orders_total': total_orders,
                'orders_completed': completed_orders,
                'amount_total': total_sales_amount,
                'amount_completed': completed_sales_amount,
            },
        })


class UserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        u = request.user
        profile = getattr(u, 'profile', None)
        is_merchant = bool(profile and profile.is_merchant)
        is_buyer = bool(profile and profile.is_buyer)
        created_from = request.query_params.get('created_from')
        created_to = request.query_params.get('created_to')
        orders_qs = Order.objects.filter(buyer_user=u)
        if created_from:
            orders_qs = orders_qs.filter(created_at__gte=created_from)
        if created_to:
            orders_qs = orders_qs.filter(created_at__lte=created_to)
        orders_total = orders_qs.count()
        by_status = orders_qs.values('status').annotate(count=Count('id')).order_by()
        status_map = {row['status']: row['count'] for row in by_status}
        coupons_qs = UserCoupon.objects.filter(user=u)
        if created_from:
            coupons_qs = coupons_qs.filter(created_at__gte=created_from)
        if created_to:
            coupons_qs = coupons_qs.filter(created_at__lte=created_to)
        coupons_total = coupons_qs.count()
        coupons_unused = coupons_qs.filter(status=UserCoupon.Status.UNUSED).count()
        coupons_used = coupons_qs.filter(status=UserCoupon.Status.USED).count()
        coupons_expired = coupons_qs.filter(status=UserCoupon.Status.EXPIRED).count()
        available_count = sum(1 for c in coupons_qs if c.is_available)
        unread_notifications = Notification.objects.filter(recipient=u, is_read=False).count()
        return Response({
            'profile': {
                'is_merchant': is_merchant,
                'is_buyer': is_buyer,
            },
            'orders': {
                'total': orders_total,
                'by_status': status_map,
            },
            'coupons': {
                'total': coupons_total,
                'unused': coupons_unused,
                'used': coupons_used,
                'expired': coupons_expired,
                'available': available_count,
            },
            'notifications': {
                'unread': unread_notifications,
            },
        })

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            val = is_read.lower()
            if val in ['true', '1']:
                qs = qs.filter(is_read=True)
            elif val in ['false', '0']:
                qs = qs.filter(is_read=False)
        notif_type = self.request.query_params.get('type')
        if notif_type:
            qs = qs.filter(type=notif_type)
        return qs

    @decorators.action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': 'read'})

    @decorators.action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread': count})

    @decorators.action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all_read'})

    @decorators.action(detail=False, methods=['post'])
    def batch_mark_read(self, request):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list) or not ids:
            return Response({'error': 'ids required'}, status=400)
        Notification.objects.filter(recipient=request.user, id__in=ids).update(is_read=True)
        return Response({'status': 'batch_read', 'count': len(ids)})
