import os

# 1. Update models.py with Coupon and UserCoupon
models_path = r'D:\spb-expert11\apps\store\models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "class Coupon(models.Model):" not in content:
    new_models = """
class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('amount', _('Fixed Amount')),
        ('percent', _('Percentage')),
    )
    
    code = models.CharField(_("Code"), max_length=20, unique=True)
    merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='coupons', null=True, blank=True)
    discount_type = models.CharField(_("Type"), max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='amount')
    discount_value = models.DecimalField(_("Value"), max_digits=10, decimal_places=2, help_text=_("Amount (e.g. 10) or Percentage (e.g. 20 for 20%)"))
    min_spend = models.DecimalField(_("Min Spend"), max_digits=10, decimal_places=2, default=0)
    
    start_date = models.DateTimeField(_("Start Date"))
    end_date = models.DateTimeField(_("End Date"))
    
    total_quantity = models.PositiveIntegerField(_("Total Quantity"), default=100)
    claimed_quantity = models.PositiveIntegerField(_("Claimed Quantity"), default=0)
    
    is_active = models.BooleanField(_("Is Active"), default=True)
    
    class Meta:
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")
        ordering = ['-end_date']

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()} {self.discount_value}"

class UserCoupon(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='claims')
    is_used = models.BooleanField(_("Is Used"), default=False)
    used_at = models.DateTimeField(_("Used At"), null=True, blank=True)
    claimed_at = models.DateTimeField(_("Claimed At"), auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'coupon')
        verbose_name = _("User Coupon")
        verbose_name_plural = _("User Coupons")
        ordering = ['-claimed_at']

    def __str__(self):
        return f"{self.user} - {self.coupon}"
"""
    content += new_models
    
    # Update Order model to include coupon info
    if "coupon_discount = models.DecimalField" not in content:
        target = "total_amount = models.DecimalField(_(\"Total Amount\"), max_digits=10, decimal_places=2)"
        replacement = """total_amount = models.DecimalField(_("Total Amount"), max_digits=10, decimal_places=2)
    original_amount = models.DecimalField(_("Original Amount"), max_digits=10, decimal_places=2, default=0)
    coupon_discount = models.DecimalField(_("Coupon Discount"), max_digits=10, decimal_places=2, default=0)"""
        content = content.replace(target, replacement)
    
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated models.py with Coupon models")

# 2. Update serializers.py
serializers_path = r'D:\spb-expert11\apps\store\serializers.py'
with open(serializers_path, 'r', encoding='utf-8') as f:
    s_content = f.read()

if "class CouponSerializer" not in s_content:
    # Add imports
    if "from .models import Favorite" in s_content:
        s_content = s_content.replace(
            "from .models import Favorite",
            "from .models import Favorite, Coupon, UserCoupon"
        )
    
    new_serializers = """
class CouponSerializer(serializers.ModelSerializer):
    is_claimed = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['merchant', 'claimed_quantity']
        
    def get_is_claimed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserCoupon.objects.filter(user=request.user, coupon=obj).exists()
        return False

class UserCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)
    
    class Meta:
        model = UserCoupon
        fields = '__all__'
        read_only_fields = ['user', 'is_used', 'used_at', 'claimed_at']
"""
    s_content += new_serializers
    
    # Update OrderSerializer to include new fields
    # fields = '__all__' handles it, but maybe we want to be explicit or readonly
    # 'original_amount', 'coupon_discount' should be readonly
    if "read_only_fields = ['user', 'merchant', 'order_no', 'status', 'total_amount']" in s_content:
        s_content = s_content.replace(
            "read_only_fields = ['user', 'merchant', 'order_no', 'status', 'total_amount']",
            "read_only_fields = ['user', 'merchant', 'order_no', 'status', 'total_amount', 'original_amount', 'coupon_discount']"
        )
        
    # Update CreateOrderSerializer to accept coupon_id
    if "address_id = serializers.IntegerField()" in s_content:
        s_content = s_content.replace(
            "address_id = serializers.IntegerField()",
            "address_id = serializers.IntegerField()\n    coupon_id = serializers.IntegerField(required=False)"
        )
        
    with open(serializers_path, 'w', encoding='utf-8') as f:
        f.write(s_content)
    print("Updated serializers.py")

# 3. Update views.py
views_path = r'D:\spb-expert11\apps\store\views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    v_content = f.read()

if "class CouponViewSet" not in v_content:
    # Add imports
    if "from .models import Favorite" in v_content:
        v_content = v_content.replace(
            "from .models import Favorite",
            "from .models import Favorite, Coupon, UserCoupon"
        )
    if "from .serializers import FavoriteSerializer" in v_content:
        v_content = v_content.replace(
            "from .serializers import FavoriteSerializer",
            "from .serializers import FavoriteSerializer, CouponSerializer, UserCouponSerializer"
        )
        
    new_views = """
class CouponViewSet(viewsets.ModelViewSet):
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        # Active coupons
        queryset = Coupon.objects.filter(is_active=True, end_date__gte=timezone.now())
        
        # Filter by merchant
        merchant_id = self.request.query_params.get('merchant_id')
        if merchant_id:
            queryset = queryset.filter(merchant_id=merchant_id)
            
        return queryset
        
    def perform_create(self, serializer):
        # Only merchants can create coupons
        if not self.request.user.is_merchant:
            raise permissions.exceptions.PermissionDenied("Only merchants can create coupons.")
        serializer.save(merchant=self.request.user.merchant_profile)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def claim(self, request, pk=None):
        coupon = self.get_object()
        
        # Check if already claimed
        if UserCoupon.objects.filter(user=request.user, coupon=coupon).exists():
            return Response({'error': 'Already claimed'}, status=400)
            
        # Check stock
        if coupon.claimed_quantity >= coupon.total_quantity:
            return Response({'error': 'Out of stock'}, status=400)
            
        # Claim
        UserCoupon.objects.create(user=request.user, coupon=coupon)
        coupon.claimed_quantity += 1
        coupon.save()
        
        return Response({'status': 'claimed'})

class UserCouponViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserCouponSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # My coupons (unused by default, or filter by status)
        queryset = UserCoupon.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status')
        if status == 'unused':
            queryset = queryset.filter(is_used=False)
        elif status == 'used':
            queryset = queryset.filter(is_used=True)
        return queryset
"""
    v_content += new_views
    
    # Update OrderViewSet create logic to handle coupon
    # This is tricky as we need to find where OrderViewSet is and inject logic
    # Or overwrite perform_create?
    # Actually, we should look at how order is created.
    # It seems we haven't implemented full order creation logic in views.py in previous turns?
    # Let's check OrderViewSet.
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(v_content)
    print("Updated views.py")

# 4. Create separate script to update OrderViewSet logic
# because it requires careful replacement
