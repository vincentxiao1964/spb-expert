from django.db.models import Sum, Count, Avg
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import IsMerchantOrReadOnly
from .models import Category, Product, Cart, CartItem
from .serializers import CategorySerializer, ProductSerializer, CartSerializer, CartItemSerializer
from django.utils import timezone
from rest_framework import permissions
from orders.models import Order, OrderItem, OrderLog
from payments.models import PaymentIntent
from payments.providers import get_provider
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from core.models import Notification
from reviews.models import ViolationCase, ViolationReason, get_violation_severity_for_reason, Review
from market.models import Coupon, UserCoupon
from decimal import Decimal

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True).order_by('order', 'id')
    serializer_class = CategorySerializer
    permission_classes = [IsMerchantOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True, is_approved=True).order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsMerchantOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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
        product = self.get_object()
        items_qs = OrderItem.objects.filter(order__status=Order.Status.COMPLETED, product=product)
        agg = items_qs.aggregate(
            total_quantity=Sum('quantity'),
            orders_count=Count('order', distinct=True),
        )
        total_quantity = agg['total_quantity'] or 0
        orders_count = agg['orders_count'] or 0
        total_amount = 0
        for oi in items_qs:
            total_amount += oi.price * oi.quantity
        reviews_qs = Review.objects.filter(order_item__product=product, is_deleted=False)
        reviews_agg = reviews_qs.aggregate(avg_rating=Avg('rating'))
        avg_rating = reviews_agg['avg_rating']
        return Response({
            'product_id': product.id,
            'title': product.title,
            'total_quantity': total_quantity,
            'orders_count': orders_count,
            'total_amount': str(total_amount),
            'avg_rating': avg_rating,
            'reviews_count': reviews_qs.count(),
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        qs = Product.objects.filter(owner=request.user).order_by('-created_at')
        try:
            limit = int(request.query_params.get('limit', 20))
            offset = int(request.query_params.get('offset', 0))
        except ValueError:
            limit, offset = 20, 0
        serializer = self.get_serializer(qs[offset:offset+limit], many=True)
        return Response(serializer.data)

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
                title=f"商品审核通过：{obj.title}",
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
                title=f"商品审核撤销：{obj.title}",
                message=obj.approval_note or '',
                content_object=obj
            )
        return Response({'status': 'unapproved'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def report(self, request, pk=None):
        product = self.get_object()
        if product.owner_id == request.user.id and not request.user.is_staff:
            return Response({'error': 'cannot report own product'}, status=403)
        reason = request.data.get('reason') or ''
        reason_category = request.data.get('reason_category') or request.data.get('category') or ViolationReason.OTHER
        valid_codes = [c[0] for c in ViolationReason.choices]
        if reason_category not in valid_codes:
            reason_category = ViolationReason.OTHER
        if not reason:
            return Response({'error': 'reason required'}, status=400)
        severity = get_violation_severity_for_reason(reason_category)
        owner = product.owner
        target_user = owner
        case = ViolationCase.objects.create(
            content_type=ContentType.objects.get_for_model(product),
            object_id=product.id,
            target_user=target_user,
            primary_reason=reason_category,
            source=ViolationCase.Source.REPORT,
            severity=severity,
        )
        if owner:
            Notification.objects.create(
                recipient=owner,
                type=Notification.Type.SYSTEM,
                title='Your product was reported',
                message=f'Product "{product.title}" was reported for {reason_category}.',
                content_type=ContentType.objects.get_for_model(product),
                object_id=product.id,
            )
        User = get_user_model()
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                type=Notification.Type.SYSTEM,
                title='Product reported',
                message=f'Product "{product.title}" (ID {product.id}) was reported. Reason: {(reason or "")[:120]}',
                content_type=ContentType.objects.get_for_model(product),
                object_id=product.id,
            )
        return Response({'status': 'reported', 'case_id': case.id})

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=False, methods=['get'])
    def me(self, request):
        cart = self.get_object()
        ser = self.get_serializer(cart)
        return Response(ser.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        cart = self.get_object()
        item_ser = CartItemSerializer(data=request.data)
        item_ser.is_valid(raise_exception=True)
        data = item_ser.validated_data
        product = data.get('product')
        service = data.get('service')
        quantity = data.get('quantity', 1)
        if product:
            if not (product.is_active and product.is_approved):
                return Response({'error': 'product not available'}, status=400)
        if product:
            existing = CartItem.objects.filter(cart=cart, product=product).first()
            if existing:
                existing.quantity = existing.quantity + quantity
                existing.save()
            else:
                CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        elif service:
            if not (service.is_active and service.is_approved):
                return Response({'error': 'service not available'}, status=400)
            existing = CartItem.objects.filter(cart=cart, service=service).first()
            if existing:
                existing.quantity = existing.quantity + quantity
                existing.save()
            else:
                CartItem.objects.create(cart=cart, service=service, quantity=quantity)
        ser = self.get_serializer(cart)
        return Response(ser.data)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        item_id = request.data.get('id')
        qty = request.data.get('quantity')
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            return Response({'error': 'quantity invalid'}, status=400)
        item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()
        if not item:
            return Response({'error': 'item not found'}, status=404)
        item.quantity = max(qty, 1)
        item.save()
        ser = self.get_serializer(self.get_object())
        return Response(ser.data)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        item_id = request.data.get('id')
        item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()
        if not item:
            return Response({'error': 'item not found'}, status=404)
        item.delete()
        ser = self.get_serializer(self.get_object())
        return Response(ser.data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_object()
        cart.items.all().delete()
        ser = self.get_serializer(cart)
        return Response(ser.data)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart = self.get_object()
        if cart.items.count() == 0:
            return Response({'error': 'cart empty'}, status=400)
        buyer_name = request.data.get('buyer_name', request.user.username)
        contact_phone = request.data.get('contact_phone', '')
        provider = request.data.get('provider', 'mock')
        user_coupon_id = request.data.get('user_coupon_id')
        order = Order.objects.create(buyer_name=buyer_name, contact_phone=contact_phone, buyer_user=request.user)
        total = Decimal('0')
        for item in cart.items.all():
            if item.product:
                price = item.product.price
                title = item.product.title
                OrderItem.objects.create(order=order, product=item.product, title=title, price=price, quantity=item.quantity)
                total += price * item.quantity
            elif item.service:
                price = item.service.price
                title = item.service.title
                OrderItem.objects.create(order=order, service=item.service, title=title, price=price, quantity=item.quantity)
                total += price * item.quantity
        discount = Decimal('0')
        if user_coupon_id:
            try:
                user_coupon = UserCoupon.objects.select_related('coupon').get(id=user_coupon_id, user=request.user)
            except UserCoupon.DoesNotExist:
                return Response({'error': 'coupon not found'}, status=400)
            coupon = user_coupon.coupon
            if not user_coupon.is_available:
                return Response({'error': 'coupon not available'}, status=400)
            eligible_total = Decimal('0')
            if coupon.is_global:
                eligible_total = total
            else:
                categories_qs = coupon.applicable_categories.all()
                products_qs = coupon.applicable_products.all()
                services_qs = coupon.applicable_services.all()
                for item in cart.items.all():
                    line_total = Decimal('0')
                    if item.product:
                        line_total = item.product.price * item.quantity
                        in_products = products_qs.filter(id=item.product_id).exists()
                        in_categories = False
                        if item.product.category_id is not None:
                            in_categories = categories_qs.filter(id=item.product.category_id).exists()
                        if in_products or in_categories:
                            eligible_total += line_total
                    elif item.service:
                        line_total = item.service.price * item.quantity
                        in_services = services_qs.filter(id=item.service_id).exists()
                        in_categories = False
                        if item.service.category_id is not None:
                            in_categories = categories_qs.filter(id=item.service.category_id).exists()
                        if in_services or in_categories:
                            eligible_total += line_total
            if eligible_total <= 0:
                return Response({'error': 'coupon not applicable to items'}, status=400)
            if eligible_total < coupon.min_amount:
                return Response({'error': 'eligible amount below coupon minimum'}, status=400)
            if coupon.type == Coupon.Type.FIXED:
                discount = coupon.value
            elif coupon.type == Coupon.Type.PERCENTAGE:
                discount = (eligible_total * coupon.value / Decimal('100')).quantize(Decimal('0.01'))
            elif coupon.type == Coupon.Type.FREE_SHIPPING:
                discount = Decimal('0')
            if discount > total:
                discount = total
            order.coupon = coupon
            order.coupon_discount_amount = discount
            order.total_amount = total - discount
            order.save()
            user_coupon.mark_as_used(order_id=order.id)
            Notification.objects.create(
                recipient=request.user,
                type=Notification.Type.SYSTEM,
                title='优惠券已使用',
                message=f'您的优惠券已用于订单 {order.id}',
                content_object=order,
            )
        else:
            order.total_amount = total
            order.save()
        cart.items.all().delete()
        OrderLog.objects.create(order=order, action='cart_checkout', note=f'items:{order.items.count()}')
        intent = PaymentIntent.objects.create(order=order, amount=order.total_amount, provider=provider)
        provider_obj = get_provider(intent.provider)
        params = provider_obj.build_params(intent)
        intent.reference = params.get('reference', intent.reference)
        intent.params = params
        intent.status = PaymentIntent.Status.PROCESSING
        intent.save()
        OrderLog.objects.create(order=order, action='payment_intent_created', note=f'intent:{intent.id}')
        return Response({
            'order_id': order.id,
            'total_amount': str(order.total_amount),
            'intent_id': intent.id,
            'provider': intent.provider,
            'reference': intent.reference,
            'params': intent.params,
            'status': intent.status,
        })
