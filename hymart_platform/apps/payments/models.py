from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order

class PaymentTransaction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SUCCESS = 'SUCCESS', _('Success')
        FAILED = 'FAILED', _('Failed')

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True) # WeChat Transaction ID
    out_trade_no = models.CharField(max_length=100, unique=True) # Our unique order ID for payment
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='CNY')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Debugging fields
    request_data = models.TextField(blank=True)
    response_data = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.out_trade_no} - {self.status}"
