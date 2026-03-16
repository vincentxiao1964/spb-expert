from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import TimeStampedModel

class ServiceCategory(TimeStampedModel):
    """
    Service Category (e.g., Dry Docking, Voyage Repair, Survey)
    Supports hierarchical structure.
    """
    name = models.CharField(_('Category Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True, max_length=100)
    parent = models.ForeignKey(
        'self', 
        verbose_name=_('Parent Category'),
        on_delete=models.CASCADE, 
        related_name='children', 
        null=True, 
        blank=True
    )
    description = models.TextField(_('Description'), blank=True)
    icon = models.ImageField(_('Category Icon'), upload_to='categories/services/', blank=True, null=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    order = models.PositiveIntegerField(_('Display Order'), default=0)

    class Meta:
        verbose_name = _('Service Category')
        verbose_name_plural = _('Service Categories')
        ordering = ['order', 'name']

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

class ServiceListing(TimeStampedModel):
    """
    Service Listing (e.g., "Professional Engine Overhaul Service in Shanghai")
    """
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name=_('Service Provider')
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name='services',
        verbose_name=_('Category')
    )
    title = models.CharField(_('Service Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    
    service_area = models.CharField(_('Service Area'), max_length=200, help_text=_('e.g. Global, China Ports, Shanghai'))
    price_range = models.CharField(_('Price Range'), max_length=100, blank=True, help_text=_('e.g. Negotiable, $100-$500/day'))
    
    is_active = models.BooleanField(_('Is Active'), default=True)
    view_count = models.PositiveIntegerField(_('View Count'), default=0)

    class Meta:
        verbose_name = _('Service Listing')
        verbose_name_plural = _('Service Listings')
        ordering = ['-created_at']

    def __str__(self):
        return self.title
