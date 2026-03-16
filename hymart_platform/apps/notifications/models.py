from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel

class Notification(TimeStampedModel):
    class NotificationType(models.TextChoices):
        ORDER_UPDATE = 'ORDER', _('Order Update')
        INQUIRY_UPDATE = 'INQUIRY', _('Inquiry Update')
        MESSAGE = 'MESSAGE', _('Message')
        SYSTEM = 'SYSTEM', _('System Notification')

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Recipient')
    )
    type = models.CharField(
        _('Type'),
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    title = models.CharField(_('Title'), max_length=255)
    message = models.TextField(_('Message'))
    is_read = models.BooleanField(_('Is Read'), default=False)
    
    # Generic Foreign Key to link to Order, Inquiry, etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def __str__(self):
        return f"{self.get_type_display()} - {self.recipient}"
