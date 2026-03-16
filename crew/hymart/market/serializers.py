from rest_framework import serializers
from .models import Coupon, UserCoupon


class CouponSerializer(serializers.ModelSerializer):
    remaining_quantity = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'title', 'type', 'value', 'min_amount',
            'valid_from', 'valid_until', 'total_quantity', 'used_quantity',
            'remaining_quantity', 'is_global', 'status', 'created_at', 'is_valid'
        ]
        read_only_fields = ['id', 'created_at', 'used_quantity']


class UserCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = UserCoupon
        fields = ['id', 'coupon', 'status', 'used_at', 'order_id', 'created_at', 'is_available']
        read_only_fields = ['id', 'created_at', 'used_at', 'order_id']


class CouponClaimSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50, help_text='优惠券代码')

    def validate_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError('优惠券不存在')

        if not coupon.is_valid:
            raise serializers.ValidationError('优惠券无效或已过期')

        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        code = self.validated_data['code']
        coupon = Coupon.objects.get(code=code)
        
        # Check if user already has this coupon
        if UserCoupon.objects.filter(user=user, coupon=coupon).exists():
            raise serializers.ValidationError('您已经领取过此优惠券')
        
        # Create user coupon
        user_coupon = UserCoupon.objects.create(
            user=user,
            coupon=coupon
        )
        
        return user_coupon