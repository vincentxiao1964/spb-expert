from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import TimeStampedModel

class Category(TimeStampedModel):
    """
    Product Category (e.g., Main Engine, Auxiliary Engine, Pumps)
    Supports hierarchical structure (Parent -> Child).
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
    image = models.ImageField(_('Category Image'), upload_to='categories/store/', blank=True, null=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    order = models.PositiveIntegerField(_('Display Order'), default=0)

    class Meta:
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        ordering = ['order', 'name']

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

class Product(TimeStampedModel):
    """
    Product Listing (Equipment, Spare Parts, Stores)
    """
    class Condition(models.TextChoices):
        NEW = 'NEW', _('New')
        USED = 'USED', _('Used')
        REFURBISHED = 'REFURBISHED', _('Refurbished')

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Seller')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('Category')
    )
    title = models.CharField(_('Product Title'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True, max_length=200)
    description = models.TextField(_('Description'), blank=True)
    
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2, help_text=_('Currency: CNY'))
    stock = models.PositiveIntegerField(_('Stock Quantity'), default=1)
    condition = models.CharField(_('Condition'), max_length=20, choices=Condition.choices, default=Condition.NEW)
    
    # Main image for list view
    image = models.ImageField(_('Main Image'), upload_to='products/', blank=True, null=True)
    
    is_active = models.BooleanField(_('Is Active'), default=True)
    view_count = models.PositiveIntegerField(_('View Count'), default=0)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    """
    Additional images for a product
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['order']
