from django.db.models import Count, Sum
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Coupon, UserCoupon
from .serializers import CouponSerializer, UserCouponSerializer, CouponClaimSerializer
from core.models import Notification


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class CouponViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing coupons.
    - Admins can perform any action.
    - Other users can only view coupons.
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request, pk=None):
        coupon = self.get_object()
        user_coupons = coupon.user_coupons.all()
        total_claimed = user_coupons.count()
        total_used = user_coupons.filter(status=UserCoupon.Status.USED).count()
        from orders.models import Order
        orders = Order.objects.filter(coupon=coupon)
        total_discount_amount = orders.aggregate(total=Sum('coupon_discount_amount'))['total'] or 0
        total_order_amount = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        return Response({
            'coupon_id': coupon.id,
            'code': coupon.code,
            'title': coupon.title,
            'total_claimed': total_claimed,
            'total_used': total_used,
            'total_discount_amount': total_discount_amount,
            'total_order_amount': total_order_amount,
        })

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def claim(self, request):
        serializer = CouponClaimSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user_coupon = serializer.save()
            Notification.objects.create(
                recipient=request.user,
                type=Notification.Type.SYSTEM,
                title='优惠券领取成功',
                message=f'您已成功领取优惠券：{user_coupon.coupon.title}',
                content_object=user_coupon.coupon,
            )
            return Response(UserCouponSerializer(user_coupon).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCouponViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user's coupons.
    """
    serializer_class = UserCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the coupons
        for the currently authenticated user.
        """
        return UserCoupon.objects.filter(user=self.request.user)
