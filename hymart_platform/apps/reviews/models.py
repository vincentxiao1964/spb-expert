from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.core.models import TimeStampedModel
from apps.orders.models import OrderItem

class Review(TimeStampedModel):
    # Linked to the specific order item being reviewed
    order_item = models.OneToOneField(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name=_('Order Item')
    )
    
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Reviewer')
    )
    
    # Target (Product or Service) derived from OrderItem
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    rating = models.PositiveSmallIntegerField(
        _('Rating'),
        choices=[(i, str(i)) for i in range(1, 6)],
        default=5
    )
    
    comment = models.TextField(_('Comment'), blank=True)
    
    # Seller's Reply
    reply = models.TextField(_('Seller Reply'), blank=True)
    replied_at = models.DateTimeField(_('Replied At'), null=True, blank=True)
    
    is_public = models.BooleanField(_('Is Public'), default=True)

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ by {self.reviewer} on {self.content_object}"

    def save(self, *args, **kwargs):
        # Auto-fill content_type/object_id from order_item if not set
        if not self.content_type_id or not self.object_id:
            self.content_type = self.order_item.content_type
            self.object_id = self.order_item.object_id
        super().save(*args, **kwargs)

class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/images/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Review Image')
        verbose_name_plural = _('Review Images')
