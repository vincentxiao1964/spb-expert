from rest_framework import viewsets, permissions, decorators, status, parsers, serializers
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer, ReviewListSerializer
from orders.models import OrderItem, Order
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import ReviewLike, ReviewReport, ReviewAppeal, SensitiveWord, ViolationCase, Punishment, ViolationReason, ViolationSeverity, get_violation_severity_for_reason
from django.db.models import Count, Q, Sum
from rest_framework import viewsets
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from core.models import Notification
from django.http import HttpResponse
import csv
from io import StringIO
from django.utils import timezone
from datetime import timedelta
from store.models import Product
from services.models import ServiceListing


def get_auto_punishment_type_and_days(case):
    policy = getattr(settings, 'MODERATION_PUNISHMENT_POLICY', {}) or {}
    key = case.severity
    raw = policy.get(key) or policy.get(str(key).lower()) or policy.get(str(key).upper()) or {}
    enabled = raw.get('enabled', True)
    if not enabled:
        return None, None
    type_value = raw.get('type')
    valid_types = [c[0] for c in Punishment.Type.choices]
    if type_value not in valid_types:
        if case.severity == ViolationSeverity.CRITICAL:
            type_value = Punishment.Type.BAN
        elif case.severity == ViolationSeverity.MAJOR:
            type_value = Punishment.Type.MUTE
        else:
            type_value = Punishment.Type.WARNING
    days = raw.get('days')
    if days is None:
        if type_value == Punishment.Type.BAN:
            days = 30
        elif type_value == Punishment.Type.MUTE:
            days = 7
        elif type_value == Punishment.Type.WARNING:
            days = 0
        else:
            days = 0
    return type_value, int(days)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        service_id = self.request.query_params.get('service_id')
        only_public = self.request.query_params.get('public')
        status_q = self.request.query_params.get('status')
        sort = self.request.query_params.get('sort')
        q = self.request.query_params.get('q')
        deleted_q = self.request.query_params.get('deleted')
        reviewer_q = self.request.query_params.get('reviewer')
        owner_q = self.request.query_params.get('owner')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        rating_min = self.request.query_params.get('rating_min')
        rating_max = self.request.query_params.get('rating_max')
        has_images = self.request.query_params.get('has_images')
        has_reply = self.request.query_params.get('has_reply')
        liked_by_me = self.request.query_params.get('liked_by_me')
        liked_by = self.request.query_params.get('liked_by')
        is_pinned = self.request.query_params.get('is_pinned')
        if product_id:
            qs = qs.filter(order_item__product_id=product_id)
        if service_id:
            qs = qs.filter(order_item__service_id=service_id)
        if only_public == '1':
            qs = qs.filter(is_public=True)
        if reviewer_q == 'me' and self.request.user.is_authenticated:
            qs = qs.filter(reviewer=self.request.user)
        if owner_q == 'me' and self.request.user.is_authenticated:
            qs = qs.filter(Q(order_item__product__owner=self.request.user) | Q(order_item__service__owner=self.request.user))
        if status_q:
            statuses = [s.strip() for s in status_q.split(',') if s.strip()]
            if 'all' in statuses:
                pass
            else:
                status_map = {
                    'deleted': Q(is_deleted=True),
                    'unpublished': Q(is_public=False, is_deleted=False),
                    'hidden': Q(hidden_by_owner=True, is_deleted=False),
                    'sensitive': Q(flagged_sensitive=True, is_deleted=False),
                    'normal': Q(is_public=True, hidden_by_owner=False, flagged_sensitive=False, is_deleted=False),
                }
                combined = Q()
                for s in statuses:
                    if s in status_map:
                        combined |= status_map[s]
                if combined:
                    qs = qs.filter(combined)
        else:
            if deleted_q == '1':
                qs = qs.filter(is_deleted=True)
            else:
                qs = qs.filter(is_deleted=False)
        if not self.request.user.is_staff:
            qs = qs.filter(
                Q(hidden_by_owner=False) |
                Q(order_item__product__owner=self.request.user) |
                Q(order_item__service__owner=self.request.user)
            )
        if q:
            qs = qs.filter(Q(comment__icontains=q) | Q(reviewer__username__icontains=q))
        if self.request.query_params.get('sensitive') == '1':
            qs = qs.filter(flagged_sensitive=True)
        if deleted_q == '1':
            qs = qs.filter(is_deleted=True)
        else:
            qs = qs.filter(is_deleted=False)
        if has_images == '1':
            qs = qs.filter(images__isnull=False)
        if has_reply == '1':
            qs = qs.filter(Q(reply__isnull=False) & ~Q(reply=''))
        if liked_by_me == '1' and self.request.user.is_authenticated:
            qs = qs.filter(likes__user=self.request.user)
        if liked_by:
            try:
                qs = qs.filter(likes__user_id=int(liked_by))
            except ValueError:
                pass
        if is_pinned == '1':
            qs = qs.filter(is_pinned=True)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)
        if rating_min:
            try:
                qs = qs.filter(rating__gte=int(rating_min))
            except ValueError:
                pass
        if rating_max:
            try:
                qs = qs.filter(rating__lte=int(rating_max))
            except ValueError:
                pass
        if has_images == '1' or liked_by_me == '1' or liked_by:
            qs = qs.distinct()
        if sort == 'hot':
            qs = qs.annotate(like_count=Count('likes')).order_by('-is_pinned', '-like_count', '-created_at')
        elif sort == 'rating_high':
            qs = qs.order_by('-is_pinned', '-rating', '-created_at')
        elif sort == 'rating_low':
            qs = qs.order_by('-is_pinned', 'rating', '-created_at')
        else:
            qs = qs.order_by('-is_pinned', '-created_at')
        limit = self.request.query_params.get('limit')
        offset = int(self.request.query_params.get('offset') or 0)
        if limit:
            try:
                limit = int(limit)
                qs = qs[offset: offset + limit]
            except ValueError:
                pass
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ReviewListSerializer
        return ReviewSerializer
    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        fields_param = request.query_params.get('fields')
        if fields_param and isinstance(resp.data, list):
            allow = {f.strip() for f in fields_param.split(',') if f.strip()}
            resp.data = [{k: v for k, v in item.items() if k in allow} for item in resp.data]
        return resp
    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        fields_param = request.query_params.get('fields')
        if fields_param and isinstance(resp.data, dict):
            allow = {f.strip() for f in fields_param.split(',') if f.strip()}
            resp.data = {k: v for k, v in resp.data.items() if k in allow}
        return resp
    def perform_create(self, serializer):
        order_item = serializer.validated_data['order_item']
        order = order_item.order
        if order.status != Order.Status.COMPLETED:
            raise ValidationError('order not completed')
        if order.buyer_user != self.request.user:
            raise PermissionDenied('permission denied')
        comment = serializer.validated_data.get('comment', '') or ''
        words = list(SensitiveWord.objects.filter(is_active=True).values_list('word', flat=True)) or getattr(settings, 'SENSITIVE_WORDS', [])
        matches = [w for w in words if w and w.lower() in comment.lower()]
        serializer.save(
            reviewer=self.request.user,
            flagged_sensitive=len(matches) > 0,
            sensitive_terms=','.join(matches)
        )

    @decorators.action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        review = self.get_object()
        oi = review.order_item
        owner = oi.product.owner if oi.product else (oi.service.owner if oi.service else None)
        if not (owner and owner == request.user) and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        review.reply = request.data.get('reply', '')
        review.save()
        return Response({'status': 'replied'})

    @decorators.action(detail=True, methods=['post'], parser_classes=[parsers.MultiPartParser])
    def upload_image(self, request, pk=None):
        review = self.get_object()
        if review.reviewer != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': 'no image'}, status=400)
        from .models import ReviewImage
        ReviewImage.objects.create(review=review, image=image_file)
        ser = self.get_serializer(review)
        return Response(ser.data)

    @decorators.action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        review = self.get_object()
        if not request.user.is_authenticated:
            return Response({'error': 'auth required'}, status=401)
        ReviewLike.objects.get_or_create(review=review, user=request.user)
        ser = self.get_serializer(review)
        return Response(ser.data)

    @decorators.action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        review = self.get_object()
        if not request.user.is_authenticated:
            return Response({'error': 'auth required'}, status=401)
        ReviewLike.objects.filter(review=review, user=request.user).delete()
        ser = self.get_serializer(review)
        return Response(ser.data)

    @decorators.action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        review = self.get_object()
        if not request.user.is_authenticated:
            return Response({'error': 'auth required'}, status=401)
        if review.reviewer == request.user and not request.user.is_staff:
            return Response({'error': 'cannot report own review'}, status=403)
        reason = request.data.get('reason', '')
        reason_category = request.data.get('reason_category') or request.data.get('category') or ViolationReason.OTHER
        if reason_category not in [c[0] for c in ViolationReason.choices]:
            reason_category = ViolationReason.OTHER
        ReviewReport.objects.get_or_create(
            review=review,
            reporter=request.user,
            defaults={'reason': reason, 'reason_category': reason_category},
        )
        return Response({'status': 'reported'})

    @decorators.action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        review = self.get_object()
        review.is_pinned = True
        review.save()
        return Response(self.get_serializer(review).data)

    @decorators.action(detail=True, methods=['post'])
    def unpin(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        review = self.get_object()
        review.is_pinned = False
        review.save()
        return Response(self.get_serializer(review).data)

    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='batch-pin')
    def batch_pin(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'error': 'ids required'}, status=400)
        Review.objects.filter(id__in=ids).update(is_pinned=True)
        return Response({'updated': len(ids)})

    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='batch-unpin')
    def batch_unpin(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'error': 'ids required'}, status=400)
        Review.objects.filter(id__in=ids).update(is_pinned=False)
        return Response({'updated': len(ids)})

    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='batch-unhide')
    def batch_unhide(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'error': 'ids required'}, status=400)
        Review.objects.filter(id__in=ids).update(hidden_by_owner=False)
        return Response({'updated': len(ids)})

    @decorators.action(detail=True, methods=['post'])
    def hide(self, request, pk=None):
        review = self.get_object()
        oi = review.order_item
        owner = oi.product.owner if oi.product else (oi.service.owner if oi.service else None)
        if not (owner and owner == request.user) and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        review.hidden_by_owner = True
        review.save()
        return Response(self.get_serializer(review).data)

    @decorators.action(detail=True, methods=['post'])
    def unhide(self, request, pk=None):
        review = self.get_object()
        oi = review.order_item
        owner = oi.product.owner if oi.product else (oi.service.owner if oi.service else None)
        if not (owner and owner == request.user) and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        review.hidden_by_owner = False
        review.save()
        return Response(self.get_serializer(review).data)

    @decorators.action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        review = self.get_object()
        review.is_public = True
        review.save()
        oi = review.order_item
        owner = oi.product.owner if oi.product else (oi.service.owner if oi.service else None)
        if owner:
            Notification.objects.create(
                recipient=owner,
                type=Notification.Type.SYSTEM,
                title='Review republished',
                message=f'Review #{review.id} has been republished by admin.',
                content_type=ContentType.objects.get_for_model(review),
                object_id=review.id,
            )
        if review.reviewer_id:
            Notification.objects.create(
                recipient=review.reviewer,
                type=Notification.Type.SYSTEM,
                title='Your review is republished',
                message=f'Your review #{review.id} is now public again.',
                content_type=ContentType.objects.get_for_model(review),
                object_id=review.id,
            )
        return Response(self.get_serializer(review).data)

    @decorators.action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        review = self.get_object()
        review.is_public = False
        review.save()
        oi = review.order_item
        owner = oi.product.owner if oi.product else (oi.service.owner if oi.service else None)
        if owner:
            Notification.objects.create(
                recipient=owner,
                type=Notification.Type.SYSTEM,
                title='Review unpublished',
                message=f'Review #{review.id} was unpublished by admin.',
                content_type=ContentType.objects.get_for_model(review),
                object_id=review.id,
            )
        if review.reviewer_id:
            Notification.objects.create(
                recipient=review.reviewer,
                type=Notification.Type.SYSTEM,
                title='Your review was unpublished',
                message=f'Your review #{review.id} was unpublished by admin.',
                content_type=ContentType.objects.get_for_model(review),
                object_id=review.id,
            )
        return Response(self.get_serializer(review).data)

    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='batch-publish')
    def batch_publish(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'error': 'ids required'}, status=400)
        qs = Review.objects.filter(id__in=ids)
        for review in qs:
            review.is_public = True
            review.save()
            oi = review.order_item
            owner = oi.product.owner if oi.product else (oi.service.owner if oi.service else None)
            if owner:
                Notification.objects.create(
                    recipient=owner,
                    type=Notification.Type.SYSTEM,
                    title='Review republished',
                    message=f'Review #{review.id} has been republished by admin.',
                    content_type=ContentType.objects.get_for_model(review),
                    object_id=review.id,
                )
            if review.reviewer_id:
                Notification.objects.create(
                    recipient=review.reviewer,
                    type=Notification.Type.SYSTEM,
                    title='Your review is republished',
                    message=f'Your review #{review.id} is now public again.',
                    content_type=ContentType.objects.get_for_model(review),
                    object_id=review.id,
                )
        return Response({'updated': qs.count()})

    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='batch-unpublish')
    def batch_unpublish(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'error': 'ids required'}, status=400)
        qs = Review.objects.filter(id__in=ids)
        for review in qs:
            review.is_public = False
            review.save()
            oi = review.order_item
            owner = oi.product.owner if oi.product else (oi.service.owner if oi.service else None)
            if owner:
                Notification.objects.create(
                    recipient=owner,
                    type=Notification.Type.SYSTEM,
                    title='Review unpublished',
                    message=f'Review #{review.id} was unpublished by admin.',
                    content_type=ContentType.objects.get_for_model(review),
                    object_id=review.id,
                )
            if review.reviewer_id:
                Notification.objects.create(
                    recipient=review.reviewer,
                    type=Notification.Type.SYSTEM,
                    title='Your review was unpublished',
                    message=f'Your review #{review.id} was unpublished by admin.',
                    content_type=ContentType.objects.get_for_model(review),
                    object_id=review.id,
                )
        return Response({'updated': qs.count()})
    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='batch-hide')
    def batch_hide(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'error': 'ids required'}, status=400)
        Review.objects.filter(id__in=ids).update(hidden_by_owner=True)
        return Response({'updated': len(ids)})

    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser], url_path='export')
    def export(self, request):
        qs = self.get_queryset().select_related('order_item', 'reviewer')
        output = StringIO()
        writer = csv.writer(output)
        include_images = request.query_params.get('include_images') == '1'
        include_likes = request.query_params.get('include_likes') == '1'
        include_reply = request.query_params.get('include_reply') == '1'
        fields_param = request.query_params.get('fields')
        default_header = ['id', 'reviewer', 'reviewer_id', 'owner', 'owner_id', 'object_type', 'object_id', 'rating', 'comment', 'is_public', 'is_pinned', 'hidden_by_owner', 'flagged_sensitive', 'status', 'sensitive_terms', 'created_at']
        if include_images:
            default_header.append('image_urls')
        if include_likes:
            default_header.append('like_count')
        if include_reply:
            default_header.append('reply')
        header = default_header
        if fields_param:
            requested = [f.strip() for f in fields_param.split(',') if f.strip()]
            if requested:
                header = requested
        writer.writerow(header)
        for r in qs:
            status_val = 'deleted' if getattr(r, 'is_deleted', False) else ('unpublished' if not getattr(r, 'is_public', True) else ('hidden' if getattr(r, 'hidden_by_owner', False) else ('sensitive' if getattr(r, 'flagged_sensitive', False) else 'normal')))
            oi = r.order_item
            obj_type = 'product' if oi and oi.product_id else ('service' if oi and oi.service_id else '')
            obj_id = oi.product_id if oi and oi.product_id else (oi.service_id if oi and oi.service_id else '')
            owner = oi.product.owner if oi and oi.product_id else (oi.service.owner if oi and oi.service_id else None)
            base = {
                'id': r.id,
                'reviewer': r.reviewer.username if r.reviewer_id else '',
                'reviewer_id': r.reviewer_id or '',
                'owner': owner.username if owner else '',
                'owner_id': owner.id if owner else '',
                'object_type': obj_type,
                'object_id': obj_id,
                'rating': r.rating,
                'comment': (r.comment or '').replace('\n', ' ').replace('\r', ' '),
                'is_public': r.is_public,
                'is_pinned': r.is_pinned,
                'hidden_by_owner': r.hidden_by_owner,
                'flagged_sensitive': r.flagged_sensitive,
                'status': status_val,
                'sensitive_terms': r.sensitive_terms,
                'created_at': r.created_at.isoformat(),
                'image_urls': ';'.join([request.build_absolute_uri(img.image.url) for img in r.images.all()]) if include_images else '',
                'like_count': r.likes.count() if include_likes else '',
                'reply': (r.reply or '').replace('\n', ' ').replace('\r', ' ') if include_reply else '',
            }
            row = [base.get(col, '') for col in header]
            writer.writerow(row)
        resp = HttpResponse(output.getvalue(), content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="reviews_export.csv"'
        return resp

    @decorators.action(detail=False, methods=['get'], url_path='status-counts')
    def status_counts(self, request, *args, **kwargs):
        qs = Review.objects.all()
        product_id = request.query_params.get('product_id')
        service_id = request.query_params.get('service_id')
        only_public = request.query_params.get('public')
        reviewer_q = request.query_params.get('reviewer')
        owner_q = request.query_params.get('owner')
        status_q = request.query_params.get('status')
        q = request.query_params.get('q')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        rating_min = request.query_params.get('rating_min')
        rating_max = request.query_params.get('rating_max')
        trend_days = request.query_params.get('trend_days') or request.query_params.get('trend')
        trend_status = request.query_params.get('trend_status')
        if product_id:
            qs = qs.filter(order_item__product_id=product_id)
        if service_id:
            qs = qs.filter(order_item__service_id=service_id)
        if only_public == '1':
            qs = qs.filter(is_public=True)
        if reviewer_q == 'me' and request.user.is_authenticated:
            qs = qs.filter(reviewer=request.user)
        if owner_q == 'me' and request.user.is_authenticated:
            qs = qs.filter(Q(order_item__product__owner=request.user) | Q(order_item__service__owner=request.user))
        if not request.user.is_staff:
            qs = qs.filter(
                Q(hidden_by_owner=False) |
                Q(order_item__product__owner=request.user) |
                Q(order_item__service__owner=request.user)
            )
        if q:
            qs = qs.filter(Q(comment__icontains=q) | Q(reviewer__username__icontains=q))
        if status_q:
            statuses = [s.strip() for s in status_q.split(',') if s.strip()]
            if 'all' in statuses:
                pass
            else:
                status_map = {
                    'deleted': Q(is_deleted=True),
                    'unpublished': Q(is_public=False, is_deleted=False),
                    'hidden': Q(hidden_by_owner=True, is_deleted=False),
                    'sensitive': Q(flagged_sensitive=True, is_deleted=False),
                    'normal': Q(is_public=True, hidden_by_owner=False, flagged_sensitive=False, is_deleted=False),
                }
                combined = Q()
                for s in statuses:
                    if s in status_map:
                        combined |= status_map[s]
                if combined:
                    qs = qs.filter(combined)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)
        if rating_min:
            try:
                qs = qs.filter(rating__gte=int(rating_min))
            except ValueError:
                pass
        if rating_max:
            try:
                qs = qs.filter(rating__lte=int(rating_max))
            except ValueError:
                pass
        data = {
            'deleted': qs.filter(is_deleted=True).count(),
            'unpublished': qs.filter(is_deleted=False, is_public=False).count(),
            'hidden': qs.filter(is_deleted=False, hidden_by_owner=True).count(),
            'sensitive': qs.filter(is_deleted=False, flagged_sensitive=True).count(),
            'normal': qs.filter(is_deleted=False, is_public=True, hidden_by_owner=False, flagged_sensitive=False).count(),
        }
        total = sum(data.values())
        if total > 0:
            percentages = {k: round(v * 100.0 / total, 2) for k, v in data.items()}
        else:
            percentages = {k: 0.0 for k in data.keys()}
        resp = {**data, 'total': total, 'percentages': percentages}
        if trend_days:
            try:
                days = int(trend_days)
            except ValueError:
                days = 7
            days = max(1, min(days, 30))
            trend = []
            today = timezone.now().date()
            ts_list = [s.strip() for s in (trend_status or '').split(',') if s.strip()]
            for i in range(days):
                day = today - timedelta(days=i)
                day_qs = qs.filter(created_at__date=day)
                if len(ts_list) == 1 and ts_list[0] in ['deleted','unpublished','hidden','sensitive','normal']:
                    cur = ts_list[0]
                    if cur == 'deleted':
                        cnt = day_qs.filter(is_deleted=True).count()
                    elif cur == 'unpublished':
                        cnt = day_qs.filter(is_deleted=False, is_public=False).count()
                    elif cur == 'hidden':
                        cnt = day_qs.filter(is_deleted=False, hidden_by_owner=True).count()
                    elif cur == 'sensitive':
                        cnt = day_qs.filter(is_deleted=False, flagged_sensitive=True).count()
                    else:
                        cnt = day_qs.filter(is_deleted=False, is_public=True, hidden_by_owner=False, flagged_sensitive=False).count()
                    trend.append({'date': day.isoformat(), 'status': cur, 'count': cnt})
                elif len(ts_list) >= 1:
                    sel = {}
                    for s in ts_list:
                        if s == 'deleted':
                            sel[s] = day_qs.filter(is_deleted=True).count()
                        elif s == 'unpublished':
                            sel[s] = day_qs.filter(is_deleted=False, is_public=False).count()
                        elif s == 'hidden':
                            sel[s] = day_qs.filter(is_deleted=False, hidden_by_owner=True).count()
                        elif s == 'sensitive':
                            sel[s] = day_qs.filter(is_deleted=False, flagged_sensitive=True).count()
                        elif s == 'normal':
                            sel[s] = day_qs.filter(is_deleted=False, is_public=True, hidden_by_owner=False, flagged_sensitive=False).count()
                    trend.append({'date': day.isoformat(), 'selected_counts': sel, 'selected_total': sum(sel.values())})
                else:
                    day_data = {
                        'deleted': day_qs.filter(is_deleted=True).count(),
                        'unpublished': day_qs.filter(is_deleted=False, is_public=False).count(),
                        'hidden': day_qs.filter(is_deleted=False, hidden_by_owner=True).count(),
                        'sensitive': day_qs.filter(is_deleted=False, flagged_sensitive=True).count(),
                        'normal': day_qs.filter(is_deleted=False, is_public=True, hidden_by_owner=False, flagged_sensitive=False).count(),
                    }
                    trend.append({'date': day.isoformat(), **day_data, 'total': sum(day_data.values())})
            trend = list(reversed(trend))
            trend_compare = request.query_params.get('trend_compare')
            if trend_compare == 'prev':
                prev_sum = 0
                for j in range(days, 2*days):
                    day = today - timedelta(days=j)
                    day_qs = qs.filter(created_at__date=day)
                    if len(ts_list) == 1 and ts_list[0] in ['deleted','unpublished','hidden','sensitive','normal']:
                        cur = ts_list[0]
                        if cur == 'deleted':
                            cnt = day_qs.filter(is_deleted=True).count()
                        elif cur == 'unpublished':
                            cnt = day_qs.filter(is_deleted=False, is_public=False).count()
                        elif cur == 'hidden':
                            cnt = day_qs.filter(is_deleted=False, hidden_by_owner=True).count()
                        elif cur == 'sensitive':
                            cnt = day_qs.filter(is_deleted=False, flagged_sensitive=True).count()
                        else:
                            cnt = day_qs.filter(is_deleted=False, is_public=True, hidden_by_owner=False, flagged_sensitive=False).count()
                        prev_sum += cnt
                    elif len(ts_list) >= 1:
                        sel = 0
                        for s in ts_list:
                            if s == 'deleted':
                                sel += day_qs.filter(is_deleted=True).count()
                            elif s == 'unpublished':
                                sel += day_qs.filter(is_deleted=False, is_public=False).count()
                            elif s == 'hidden':
                                sel += day_qs.filter(is_deleted=False, hidden_by_owner=True).count()
                            elif s == 'sensitive':
                                sel += day_qs.filter(is_deleted=False, flagged_sensitive=True).count()
                            elif s == 'normal':
                                sel += day_qs.filter(is_deleted=False, is_public=True, hidden_by_owner=False, flagged_sensitive=False).count()
                        prev_sum += sel
                    else:
                        prev_sum += day_qs.filter(is_deleted=False).count() + day_qs.filter(is_deleted=True).count()
                if len(ts_list) == 1 and ts_list[0] in ['deleted','unpublished','hidden','sensitive','normal']:
                    cur_sum = sum([t['count'] for t in trend])
                elif len(ts_list) >= 1:
                    cur_sum = sum([t['selected_total'] for t in trend])
                else:
                    cur_sum = sum([t['total'] for t in trend])
                delta = cur_sum - prev_sum
                delta_pct = round((delta * 100.0 / prev_sum), 2) if prev_sum > 0 else None
                resp['compare'] = {
                    'period_days': days,
                    'current_total': cur_sum,
                    'previous_total': prev_sum,
                    'delta': delta,
                    'delta_pct': delta_pct
                }
            trend_ma = request.query_params.get('trend_ma')
            if trend_ma:
                try:
                    w = int(trend_ma)
                except ValueError:
                    w = 3
                w = max(2, min(w, 30))
                if len(ts_list) == 1 and ts_list[0] in ['deleted','unpublished','hidden','sensitive','normal']:
                    vals = [t['count'] for t in trend]
                    for i in range(len(trend)):
                        start = max(0, i - w + 1)
                        window_vals = vals[start:i+1]
                        ma = round(sum(window_vals) / len(window_vals), 2)
                        trend[i]['ma'] = ma
                elif len(ts_list) >= 1:
                    vals = [t['selected_total'] for t in trend]
                    for i in range(len(trend)):
                        start = max(0, i - w + 1)
                        window_vals = vals[start:i+1]
                        ma = round(sum(window_vals) / len(window_vals), 2)
                        trend[i]['ma_selected_total'] = ma
                else:
                    vals = [t['total'] for t in trend]
                    for i in range(len(trend)):
                        start = max(0, i - w + 1)
                        window_vals = vals[start:i+1]
                        ma = round(sum(window_vals) / len(window_vals), 2)
                        trend[i]['ma_total'] = ma
            resp['trend'] = trend
        return Response(resp)
    @decorators.action(detail=False, methods=['get'], url_path='rating-stats')
    def rating_stats(self, request, *args, **kwargs):
        qs = Review.objects.filter(is_deleted=False)
        product_id = request.query_params.get('product_id')
        service_id = request.query_params.get('service_id')
        group_by = request.query_params.get('group_by')
        only_public = request.query_params.get('public')
        reviewer_q = request.query_params.get('reviewer')
        owner_q = request.query_params.get('owner')
        q = request.query_params.get('q')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if product_id:
            qs = qs.filter(order_item__product_id=product_id)
        if service_id:
            qs = qs.filter(order_item__service_id=service_id)
        if only_public == '1':
            qs = qs.filter(is_public=True)
        if reviewer_q == 'me' and request.user.is_authenticated:
            qs = qs.filter(reviewer=request.user)
        if owner_q == 'me' and request.user.is_authenticated:
            qs = qs.filter(Q(order_item__product__owner=request.user) | Q(order_item__service__owner=request.user))
        if not request.user.is_staff:
            qs = qs.filter(
                Q(hidden_by_owner=False) |
                Q(order_item__product__owner=request.user) |
                Q(order_item__service__owner=request.user)
            )
        if q:
            qs = qs.filter(Q(comment__icontains=q) | Q(reviewer__username__icontains=q))
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)
        data = {str(i): qs.filter(rating=i).count() for i in range(1, 6)}
        total = sum(data.values())
        avg = 0.0
        if total > 0:
            avg = round(sum(int(k) * v for k, v in data.items()) / total, 2)
            percentages = {k: round(v * 100.0 / total, 2) for k, v in data.items()}
        else:
            percentages = {k: 0.0 for k in data.keys()}
        resp = {**data, 'total': total, 'average': avg, 'percentages': percentages}
        if group_by == 'object':
            objects = []
            objects_owner = request.query_params.get('objects_owner')
            objects_owner_id = request.query_params.get('objects_owner_id')
            objects_type = request.query_params.get('objects_type')
            objects_sort = request.query_params.get('objects_sort') or 'total'
            objects_limit = request.query_params.get('objects_limit')
            objects_offset = int(request.query_params.get('objects_offset') or 0)
            recent_days = request.query_params.get('objects_recent_days')
            objects_fields = request.query_params.get('objects_fields')
            objects_min_total = request.query_params.get('objects_min_total')
            objects_min_recent = request.query_params.get('objects_min_recent')
            fields_allow = {'type','id','name','owner_id','owner_name','rating_counts','total','recent_total','average','percentages','recent_average'}
            fields = None
            if objects_fields:
                fields = [f.strip() for f in objects_fields.split(',') if f.strip()]
                fields = [f for f in fields if f in fields_allow]
            try:
                recent_days = int(recent_days) if recent_days else 30
            except ValueError:
                recent_days = 30
            recent_cutoff = timezone.now() - timedelta(days=max(1, min(recent_days, 365)))
            product_ids = list(qs.filter(order_item__product_id__isnull=False).values_list('order_item__product_id', flat=True).distinct())
            service_ids = list(qs.filter(order_item__service_id__isnull=False).values_list('order_item__service_id', flat=True).distinct())
            prod_meta = {p['id']: p for p in Product.objects.filter(id__in=product_ids).values('id', 'title', 'owner_id', 'owner__username')}
            serv_meta = {s['id']: s for s in ServiceListing.objects.filter(id__in=service_ids).values('id', 'title', 'owner_id', 'owner__username')}
            for pid in product_ids:
                sub = qs.filter(order_item__product_id=pid)
                counts = {str(i): sub.filter(rating=i).count() for i in range(1, 6)}
                subt = sum(counts.values())
                recent_total = sub.filter(created_at__gte=recent_cutoff).count()
                recent_sum = sub.filter(created_at__gte=recent_cutoff).aggregate(s=Sum('rating')).get('s') or 0
                recent_avg = round(recent_sum / recent_total, 2) if recent_total > 0 else 0.0
                if subt > 0:
                    s_avg = round(sum(int(k) * v for k, v in counts.items()) / subt, 2)
                    s_pct = {k: round(v * 100.0 / subt, 2) for k, v in counts.items()}
                else:
                    s_avg = 0.0
                    s_pct = {k: 0.0 for k in counts.keys()}
                meta = prod_meta.get(pid, {})
                objects.append({
                    'type': 'product',
                    'id': pid,
                    'name': meta.get('title', ''),
                    'owner_id': meta.get('owner_id', None),
                    'owner_name': meta.get('owner__username', ''),
                    'rating_counts': counts,
                    'total': subt,
                    'recent_total': recent_total,
                    'recent_average': recent_avg,
                    'average': s_avg,
                    'percentages': s_pct
                })
            for sid in service_ids:
                sub = qs.filter(order_item__service_id=sid)
                counts = {str(i): sub.filter(rating=i).count() for i in range(1, 6)}
                subt = sum(counts.values())
                recent_total = sub.filter(created_at__gte=recent_cutoff).count()
                recent_sum = sub.filter(created_at__gte=recent_cutoff).aggregate(s=Sum('rating')).get('s') or 0
                recent_avg = round(recent_sum / recent_total, 2) if recent_total > 0 else 0.0
                if subt > 0:
                    s_avg = round(sum(int(k) * v for k, v in counts.items()) / subt, 2)
                    s_pct = {k: round(v * 100.0 / subt, 2) for k, v in counts.items()}
                else:
                    s_avg = 0.0
                    s_pct = {k: 0.0 for k in counts.keys()}
                meta = serv_meta.get(sid, {})
                objects.append({
                    'type': 'service',
                    'id': sid,
                    'name': meta.get('title', ''),
                    'owner_id': meta.get('owner_id', None),
                    'owner_name': meta.get('owner__username', ''),
                    'rating_counts': counts,
                    'total': subt,
                    'recent_total': recent_total,
                    'recent_average': recent_avg,
                    'average': s_avg,
                    'percentages': s_pct
                })
            if objects_owner == 'me' and request.user.is_authenticated:
                objects = [o for o in objects if o.get('owner_id') == request.user.id]
            elif objects_owner_id:
                try:
                    oid = int(objects_owner_id)
                    objects = [o for o in objects if o.get('owner_id') == oid]
                except ValueError:
                    pass
            if objects_type in ['product', 'service']:
                objects = [o for o in objects if o.get('type') == objects_type]
            min_total = None
            min_recent = None
            if objects_min_total:
                try:
                    min_total = int(objects_min_total)
                except ValueError:
                    min_total = None
            if objects_min_recent:
                try:
                    min_recent = int(objects_min_recent)
                except ValueError:
                    min_recent = None
            if min_total is not None:
                objects = [o for o in objects if o.get('total', 0) >= min_total]
            if min_recent is not None:
                objects = [o for o in objects if o.get('recent_total', 0) >= min_recent]
            objects_total = len(objects)
            if objects_sort == 'average':
                objects = sorted(objects, key=lambda x: x['average'], reverse=True)
            elif objects_sort == 'recent':
                objects = sorted(objects, key=lambda x: x.get('recent_total', 0), reverse=True)
            elif objects_sort == 'recent_avg':
                objects = sorted(objects, key=lambda x: x.get('recent_average', 0.0), reverse=True)
            else:
                objects = sorted(objects, key=lambda x: x['total'], reverse=True)
            if objects_limit:
                try:
                    objects_limit = int(objects_limit)
                    objects = objects[objects_offset: objects_offset + objects_limit]
                except ValueError:
                    pass
            if fields:
                objects = [{k: v for k, v in o.items() if k in fields} for o in objects]
            resp['objects'] = objects
            resp['objects_total'] = objects_total
            resp['objects_limit'] = objects_limit if objects_limit else None
            resp['objects_offset'] = objects_offset
        return Response(resp)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        review = self.get_object()
        review.is_deleted = True
        review.save()
        return Response(status=204)

    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='batch-delete')
    def batch_delete(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'error': 'ids required'}, status=400)
        Review.objects.filter(id__in=ids).update(is_deleted=True)
        return Response({'updated': len(ids)})

    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='batch-restore')
    def batch_restore(self, request):
        ids = request.data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return Response({'error': 'ids required'}, status=400)
        Review.objects.filter(id__in=ids).update(is_deleted=False)
        return Response({'updated': len(ids)})

    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='restore')
    def restore(self, request, pk=None):
        review = self.get_object()
        review.is_deleted = False
        review.save()
        return Response(self.get_serializer(review).data)

class ReviewReportSerializer(serializers.ModelSerializer):
    review_id = serializers.PrimaryKeyRelatedField(queryset=Review.objects.all(), source='review')
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)

    class Meta:
        model = ReviewReport
        fields = ['id', 'review_id', 'reporter_name', 'reason_category', 'reason', 'status', 'created_at', 'resolved_at', 'resolved_by', 'case']
        read_only_fields = ['created_at', 'resolved_at', 'resolved_by']


class ReviewReportViewSet(viewsets.ModelViewSet):
    queryset = ReviewReport.objects.all().order_by('-created_at')
    serializer_class = ReviewReportSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        status_q = self.request.query_params.get('status')
        if status_q:
            qs = qs.filter(status=status_q)
        return qs.order_by('-created_at')

    @decorators.action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        report = self.get_object()
        status_to = request.data.get('status')
        if status_to not in ['accepted', 'rejected']:
            return Response({'error': 'invalid status'}, status=400)
        report.status = status_to
        report.resolved_at = timezone.now()
        report.resolved_by = request.user
        if status_to == 'accepted':
            review = report.review
            review.flagged_sensitive = True
            review.is_public = False
            review.save()
            oi = review.order_item
            owner = oi.product.owner if oi.product else (oi.service.owner if oi.service else None)
            if owner:
                Notification.objects.create(
                    recipient=owner,
                type=Notification.Type.SYSTEM,
                    title='Review unpublished after report acceptance',
                message=f'Review #{review.id} was unpublished due to accepted report.',
                content_type=ContentType.objects.get_for_model(review),
                object_id=review.id,
                )
            if review.reviewer_id:
                Notification.objects.create(
                    recipient=review.reviewer,
                type=Notification.Type.SYSTEM,
                    title='Your review is under moderation',
                message=f'Your review #{review.id} was flagged and unpublished for moderation.',
                content_type=ContentType.objects.get_for_model(review),
                object_id=review.id,
                )
            User = get_user_model()
            admins = User.objects.filter(is_staff=True)
            for admin in admins:
                Notification.objects.create(
                    recipient=admin,
                type=Notification.Type.SYSTEM,
                    title='Review report accepted',
                message=f'Review #{review.id} flagged by moderation. Reason: {(report.reason or "")[:120]}',
                content_type=ContentType.objects.get_for_model(review),
                object_id=review.id,
                )
            reason_code = report.reason_category or ViolationReason.OTHER
            severity = get_violation_severity_for_reason(reason_code)
            oi = review.order_item
            owner = oi.product.owner if oi.product else (oi.service.owner if oi.service else None)
            if reason_code == ViolationReason.MALICIOUS_REVIEW:
                target_user = review.reviewer
            else:
                target_user = owner
            if report.case:
                case = report.case
            else:
                case = ViolationCase.objects.create(
                    content_type=ContentType.objects.get_for_model(review),
                    object_id=review.id,
                    target_user=target_user,
                    primary_reason=reason_code,
                    source=ViolationCase.Source.REPORT,
                    severity=severity,
                )
                report.case = case
        report.save()
        return Response(self.get_serializer(report).data)

class ReviewAppealSerializer(serializers.ModelSerializer):
    review_id = serializers.PrimaryKeyRelatedField(queryset=Review.objects.all(), source='review')
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)

    class Meta:
        model = ReviewAppeal
        fields = ['id', 'review_id', 'applicant_name', 'reason', 'status', 'resolution_note', 'created_at', 'resolved_at', 'resolved_by']
        read_only_fields = ['created_at', 'resolved_at', 'resolved_by']

class ReviewAppealViewSet(viewsets.ModelViewSet):
    queryset = ReviewAppeal.objects.all().order_by('-created_at')
    serializer_class = ReviewAppealSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        status_q = self.request.query_params.get('status')
        if status_q:
            qs = qs.filter(status=status_q)
        return qs.order_by('-created_at')

    @decorators.action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        appeal = self.get_object()
        status_to = request.data.get('status')
        if status_to not in ['accepted', 'rejected']:
            return Response({'error': 'invalid status'}, status=400)
        note = request.data.get('note', '')
        appeal.status = status_to
        from django.utils import timezone
        appeal.resolved_at = timezone.now()
        appeal.resolved_by = request.user
        appeal.resolution_note = note
        appeal.save()
        if status_to == 'accepted':
            review = appeal.review
            review.hidden_by_owner = False
            review.save()
        return Response(self.get_serializer(appeal).data)

    @decorators.action(detail=False, methods=['post'], url_path='submit')
    def submit(self, request):
        review_id = request.data.get('review_id')
        reason = request.data.get('reason') or ''
        if not review_id or not reason:
            return Response({'error': 'review_id and reason required'}, status=400)
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({'error': 'review not found'}, status=404)
        oi = review.order_item
        owner = oi.product.owner if oi.product else (oi.service.owner if oi.service else None)
        if not (owner and owner == request.user) and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)
        appeal, _ = ReviewAppeal.objects.get_or_create(review=review, applicant=request.user, defaults={'reason': reason})
        ser = self.get_serializer(appeal)
        return Response(ser.data)

class SensitiveWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensitiveWord
        fields = ['id', 'word', 'is_active', 'created_at']
        read_only_fields = ['created_at']

class SensitiveWordViewSet(viewsets.ModelViewSet):
    queryset = SensitiveWord.objects.all().order_by('word')
    serializer_class = SensitiveWordSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        active = self.request.query_params.get('active')
        if active == '1':
            qs = qs.filter(is_active=True)
        return qs.order_by('word')


class ViolationCaseSerializer(serializers.ModelSerializer):
    target_user_name = serializers.CharField(source='target_user.username', read_only=True)
    primary_reason_display = serializers.CharField(source='get_primary_reason_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    decision_display = serializers.CharField(source='get_decision_display', read_only=True)
    reports_count = serializers.SerializerMethodField()
    latest_report_reason = serializers.SerializerMethodField()
    latest_report_created_at = serializers.SerializerMethodField()

    class Meta:
        model = ViolationCase
        fields = [
            'id',
            'primary_reason',
            'primary_reason_display',
            'source',
            'severity',
            'severity_display',
            'status',
            'status_display',
            'decision',
            'decision_display',
            'decision_note',
            'target_user',
            'target_user_name',
            'reports_count',
            'latest_report_reason',
            'latest_report_created_at',
            'created_at',
            'updated_at',
            'decided_at',
            'content_type',
            'object_id',
        ]
        read_only_fields = ['created_at', 'updated_at', 'decided_at']

    def get_reports_count(self, obj):
        return obj.reports.count()

    def get_latest_report_reason(self, obj):
        r = obj.reports.order_by('-created_at').first()
        return r.reason if r else ''

    def get_latest_report_created_at(self, obj):
        r = obj.reports.order_by('-created_at').first()
        return r.created_at if r else None


class ViolationCaseViewSet(viewsets.ModelViewSet):
    queryset = ViolationCase.objects.all().order_by('-created_at')
    serializer_class = ViolationCaseSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        status_q = self.request.query_params.get('status')
        reason_q = self.request.query_params.get('reason_category')
        severity_q = self.request.query_params.get('severity')
        source_q = self.request.query_params.get('source')
        if status_q:
            qs = qs.filter(status=status_q)
        if reason_q:
            qs = qs.filter(primary_reason=reason_q)
        if severity_q:
            qs = qs.filter(severity=severity_q)
        if source_q:
            qs = qs.filter(source=source_q)
        return qs.order_by('-created_at')

    @decorators.action(detail=True, methods=['post'])
    def decide(self, request, pk=None):
        case = self.get_object()
        decision_to = request.data.get('decision')
        if decision_to not in [c[0] for c in ViolationCase.Decision.choices]:
            return Response({'error': 'invalid decision'}, status=400)
        note = request.data.get('decision_note', '')
        case.decision = decision_to
        case.decision_note = note
        case.status = ViolationCase.Status.CLOSED
        case.decided_by = request.user
        case.decided_at = timezone.now()
        auto_punish = request.data.get('auto_punish')
        should_auto = auto_punish is None or str(auto_punish).lower() in ['1', 'true', 'yes']
        if decision_to == ViolationCase.Decision.VIOLATION and should_auto and case.target_user:
            if not case.punishments.exists():
                p_type, days = get_auto_punishment_type_and_days(case)
                if p_type is not None:
                    now = timezone.now()
                end_at = now + timedelta(days=days) if days > 0 else None
                punishment = Punishment.objects.create(
                    user=case.target_user,
                    case=case,
                    type=p_type,
                    start_at=now,
                    end_at=end_at,
                    operator=request.user,
                    params={
                        'auto': True,
                        'severity': case.severity,
                        'primary_reason': case.primary_reason,
                        'days': days,
                    },
                )
                title = 'Account punishment applied'
                if p_type == Punishment.Type.BAN:
                    message = f'Your account is banned for {days} days due to violation.'
                elif p_type == Punishment.Type.MUTE:
                    message = f'Your account is muted for {days} days due to violation.'
                elif p_type == Punishment.Type.WARNING:
                    message = 'You have received a warning due to violation.'
                else:
                    message = 'A punishment has been applied to your account due to violation.'
                Notification.objects.create(
                    recipient=case.target_user,
                    type=Notification.Type.SYSTEM,
                    title=title,
                    message=message,
                    content_type=ContentType.objects.get_for_model(punishment),
                    object_id=punishment.id,
                )
        case.save()
        return Response(self.get_serializer(case).data)


class PunishmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Punishment
        fields = [
            'id',
            'user',
            'user_name',
            'case',
            'type',
            'type_display',
            'params',
            'start_at',
            'end_at',
            'status',
            'status_display',
            'is_active',
            'operator',
            'operator_name',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def get_is_active(self, obj):
        return obj.is_active()


class PunishmentViewSet(viewsets.ModelViewSet):
    queryset = Punishment.objects.all().order_by('-created_at')
    serializer_class = PunishmentSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get('user')
        case_id = self.request.query_params.get('case')
        status_q = self.request.query_params.get('status')
        type_q = self.request.query_params.get('type')
        if user_id:
            qs = qs.filter(user_id=user_id)
        if case_id:
            qs = qs.filter(case_id=case_id)
        if status_q:
            qs = qs.filter(status=status_q)
        if type_q:
            qs = qs.filter(type=type_q)
        return qs.order_by('-created_at')
