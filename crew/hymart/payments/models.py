from django.db import models
from orders.models import Order

class PaymentIntent(models.Model):
    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        PROCESSING = 'PROCESSING', 'Processing'
        SUCCEEDED = 'SUCCEEDED', 'Succeeded'
        FAILED = 'FAILED', 'Failed'

    order = models.ForeignKey(Order, related_name='payment_intents', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider = models.CharField(max_length=50, default='mock')
    reference = models.CharField(max_length=100, blank=True)
    params = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Intent #{self.id} - {self.status}"
