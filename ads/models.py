from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

class Advertisement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'), null=True, blank=True)
    title = models.CharField(_('Title'), max_length=100)
    # Use 'banners' instead of 'ads' to avoid ad blocker issues
    image = models.ImageField(_('Image'), upload_to='banners/', blank=True, null=True)
    link = models.URLField(_('Link'), blank=True)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(_('Activated At'), null=True, blank=True)

    class Meta:
        ordering = ['created_at'] # FIFO for queue
        verbose_name = _('Advertisement')
        verbose_name_plural = _('Advertisements')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_active and not self.activated_at:
             self.activated_at = timezone.now()
        super().save(*args, **kwargs)
