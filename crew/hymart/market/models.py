from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Coupon(models.Model):
    class Type(models.TextChoices):
        FIXED = 'FIXED', '固定金额'
        PERCENTAGE = 'PERCENTAGE', '百分比折扣'
        FREE_SHIPPING = 'FREE_SHIPPING', '免运费'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', '有效'
        EXPIRED = 'EXPIRED', '已过期'
        DISABLED = 'DISABLED', '已禁用'

    code = models.CharField(max_length=50, unique=True, verbose_name='优惠券代码')
    title = models.CharField(max_length=200, verbose_name='优惠券标题')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.FIXED, verbose_name='类型')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='优惠值')
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='最低消费金额')
    valid_from = models.DateTimeField(verbose_name='生效时间')
    valid_until = models.DateTimeField(verbose_name='过期时间')
    total_quantity = models.PositiveIntegerField(default=0, verbose_name='总数量（0表示不限）')
    used_quantity = models.PositiveIntegerField(default=0, verbose_name='已使用数量')
    is_global = models.BooleanField(default=True, verbose_name='全场通用')
    applicable_categories = models.ManyToManyField('store.Category', blank=True, verbose_name='适用分类')
    applicable_products = models.ManyToManyField('store.Product', blank=True, verbose_name='适用商品')
    applicable_services = models.ManyToManyField('services.ServiceListing', blank=True, verbose_name='适用服务')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')

    @property
    def is_valid(self):
        if self.status != self.Status.ACTIVE:
            return False
        now = timezone.now()
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.total_quantity > 0 and self.used_quantity >= self.total_quantity:
            return False
        return True

    @property
    def remaining_quantity(self):
        if self.total_quantity == 0:
            return None
        return max(0, self.total_quantity - self.used_quantity)

    def __str__(self):
        return f"{self.code} - {self.title}"

    class Meta:
        verbose_name = '优惠券'
        verbose_name_plural = '优惠券'


class UserCoupon(models.Model):
    class Status(models.TextChoices):
        UNUSED = 'UNUSED', '未使用'
        USED = 'USED', '已使用'
        EXPIRED = 'EXPIRED', '已过期'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_coupons', verbose_name='用户')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='user_coupons', verbose_name='优惠券')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNUSED, verbose_name='状态')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='使用时间')
    order_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='订单ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='领取时间')

    @property
    def is_available(self):
        if self.status != self.Status.UNUSED:
            return False
        return self.coupon.is_valid

    def mark_as_used(self, order_id=None):
        self.status = self.Status.USED
        self.used_at = timezone.now()
        self.order_id = order_id
        self.save()
        
        self.coupon.used_quantity += 1
        self.coupon.save()

    def __str__(self):
        return f"{self.user.username} - {self.coupon.code}"

    class Meta:
        verbose_name = '用户优惠券'
        verbose_name_plural = '用户优惠券'
        unique_together = ['user', 'coupon']