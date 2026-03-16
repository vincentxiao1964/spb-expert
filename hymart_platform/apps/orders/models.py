import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.core.models import TimeStampedModel

class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Payment')
        PAID = 'PAID', _('Paid')
        PROCESSING = 'PROCESSING', _('Processing')
        SHIPPED = 'SHIPPED', _('Shipped')  # Applicable for products
        IN_SERVICE = 'IN_SERVICE', _('In Service')  # Applicable for services
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    order_number = models.CharField(_('Order Number'), max_length=20, unique=True, editable=False)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders_bought',
        verbose_name=_('Buyer')
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders_sold',
        verbose_name=_('Seller'),
        null=True, # Allow null temporarily for migration, but logic should enforce it
        blank=True
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    total_amount = models.DecimalField(_('Total Amount'), max_digits=12, decimal_places=2, default=0.00)
    
    # Contact & Shipping Info
    contact_name = models.CharField(_('Contact Name'), max_length=100)
    contact_phone = models.CharField(_('Contact Phone'), max_length=20)
    shipping_address = models.TextField(_('Shipping Address'), blank=True, help_text=_('Required for physical products'))
    
    note = models.TextField(_('Order Note'), blank=True)

    class Meta:
        verbose_name=_('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_number} - {self.buyer} -> {self.seller}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number: YYYYMMDD-UUID (shortened)
            # Example: 20260213-A1B2C3D4
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            uid = str(uuid.uuid4())[:8].upper()
            self.order_number = f"{date_str}-{uid}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Order')
    )
    
    # Generic Foreign Key to support both Product and ServiceListing
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2, help_text=_('Price at the time of order'))
    
    @property
    def subtotal(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f"{self.quantity} x {self.content_object} (Order {self.order.order_number})"
