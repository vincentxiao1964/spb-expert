from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel

class Inquiry(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Quote')
        QUOTED = 'QUOTED', _('Quoted')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')
        CLOSED = 'CLOSED', _('Closed')

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inquiries_sent',
        verbose_name=_('Buyer')
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inquiries_received',
        verbose_name=_('Seller')
    )

    # Linked Item (Product or Service)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField(_('Quantity'), default=1)

    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    subject = models.CharField(_('Subject'), max_length=200, blank=True)

    class Meta:
        verbose_name = _('Inquiry')
        verbose_name_plural = _('Inquiries')
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry #{self.id} - {self.content_object}"

class InquiryMessage(TimeStampedModel):
    inquiry = models.ForeignKey(
        Inquiry,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Inquiry')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inquiry_messages',
        verbose_name=_('Sender')
    )
    message = models.TextField(_('Message'))
    
    # Quotation details (if this message is a quote)
    is_quote = models.BooleanField(_('Is Quote'), default=False)
    price = models.DecimalField(_('Quoted Price'), max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(_('Currency'), max_length=10, default='CNY')
    valid_until = models.DateField(_('Valid Until'), null=True, blank=True)
    
    # Attachment
    attachment = models.FileField(_('Attachment'), upload_to='inquiries/attachments/', null=True, blank=True)

    class Meta:
        verbose_name = _('Inquiry Message')
        verbose_name_plural = _('Inquiry Messages')
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender} on Inquiry #{self.inquiry.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-update inquiry status if quote
        if self.is_quote:
            self.inquiry.status = Inquiry.Status.QUOTED
            self.inquiry.save()
