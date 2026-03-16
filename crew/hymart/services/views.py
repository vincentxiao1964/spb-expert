from django.db.models import Sum, Count, Avg
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import IsMerchantOrReadOnly
from .models import ServiceCategory, ServiceListing
from .serializers import ServiceCategorySerializer, ServiceListingSerializer
from django.utils import timezone
from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from core.models import Notification
from reviews.models import ViolationCase, ViolationReason, get_violation_severity_for_reason, Review
from orders.models import Order, OrderItem

class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True).order_by('order', 'id')
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsMerchantOrReadOnly]

class ServiceListingViewSet(viewsets.ModelViewSet):
    queryset = ServiceListing.objects.filter(is_active=True, is_approved=True).order_by('-created_at')
    serializer_class = ServiceListingSerializer
    permission_classes = [IsMerchantOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        qs = ServiceListing.objects.filter(owner=request.user).order_by('-created_at')
        try:
            limit = int(request.query_params.get('limit', 20))
            offset = int(request.query_params.get('offset', 0))
        except ValueError:
            limit, offset = 20, 0
        serializer = self.get_serializer(qs[offset:offset+limit], many=True)
        return Response(serializer.data)

    def _check_owner_permission(self, request, obj):
        u = request.user
        if not u.is_authenticated:
            return False
        if u.is_staff:
            return True
        return getattr(obj, 'owner_id', None) == u.id

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self._check_owner_permission(request, obj):
            return Response({'error': 'Permission denied'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self._check_owner_permission(request, obj):
            return Response({'error': 'Permission denied'}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self._check_owner_permission(request, obj):
            return Response({'error': 'Permission denied'}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def stats(self, request, pk=None):
        service = self.get_object()
        items_qs = OrderItem.objects.filter(order__status=Order.Status.COMPLETED, service=service)
        agg = items_qs.aggregate(
            total_quantity=Sum('quantity'),
            orders_count=Count('order', distinct=True),
        )
        total_quantity = agg['total_quantity'] or 0
        orders_count = agg['orders_count'] or 0
        total_amount = 0
        for oi in items_qs:
            total_amount += oi.price * oi.quantity
        reviews_qs = Review.objects.filter(order_item__service=service, is_deleted=False)
        reviews_agg = reviews_qs.aggregate(avg_rating=Avg('rating'))
        avg_rating = reviews_agg['avg_rating']
        return Response({
            'service_id': service.id,
            'title': service.title,
            'total_quantity': total_quantity,
            'orders_count': orders_count,
            'total_amount': str(total_amount),
            'avg_rating': avg_rating,
            'reviews_count': reviews_qs.count(),
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        obj = self.get_object()
        obj.is_approved = True
        obj.approved_at = timezone.now()
        obj.approved_by = request.user
        obj.approval_note = request.data.get('note', '')
        obj.save()
        # Notification
        from core.models import Notification
        if obj.owner:
            Notification.objects.create(
                recipient=obj.owner,
                type=Notification.Type.APPROVAL,
                title=f"服务审核通过：{obj.title}",
                message=obj.approval_note or '',
                content_object=obj
            )
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def unapprove(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        obj = self.get_object()
        obj.is_approved = False
        obj.approved_at = None
        obj.approved_by = request.user
        obj.approval_note = request.data.get('note', '')
        obj.save()
        # Notification
        from core.models import Notification
        if obj.owner:
            Notification.objects.create(
                recipient=obj.owner,
                type=Notification.Type.APPROVAL,
                title=f"服务审核撤销：{obj.title}",
                message=obj.approval_note or '',
                content_object=obj
            )
        return Response({'status': 'unapproved'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def report(self, request, pk=None):
        service = self.get_object()
        if service.owner_id == request.user.id and not request.user.is_staff:
            return Response({'error': 'cannot report own service'}, status=403)
        reason = request.data.get('reason') or ''
        reason_category = request.data.get('reason_category') or request.data.get('category') or ViolationReason.OTHER
        valid_codes = [c[0] for c in ViolationReason.choices]
        if reason_category not in valid_codes:
            reason_category = ViolationReason.OTHER
        if not reason:
            return Response({'error': 'reason required'}, status=400)
        severity = get_violation_severity_for_reason(reason_category)
        owner = service.owner
        target_user = owner
        case = ViolationCase.objects.create(
            content_type=ContentType.objects.get_for_model(service),
            object_id=service.id,
            target_user=target_user,
            primary_reason=reason_category,
            source=ViolationCase.Source.REPORT,
            severity=severity,
        )
        if owner:
            Notification.objects.create(
                recipient=owner,
                type=Notification.Type.SYSTEM,
                title='Your service was reported',
                message=f'Service "{service.title}" was reported for {reason_category}.',
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
            )
        User = get_user_model()
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                type=Notification.Type.SYSTEM,
                title='Service reported',
                message=f'Service "{service.title}" (ID {service.id}) was reported. Reason: {(reason or "")[:120]}',
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
            )
        return Response({'status': 'reported', 'case_id': case.id})
