from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    class Type(models.TextChoices):
        APPROVAL = 'APPROVAL', 'Approval'
        ORDER_UPDATE = 'ORDER_UPDATE', 'Order Update'
        INQUIRY_UPDATE = 'INQUIRY_UPDATE', 'Inquiry Update'
        MESSAGE = 'MESSAGE', 'Message'
        SYSTEM = 'SYSTEM', 'System'

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.type} -> {self.recipient.username}"

# Create your models here.
