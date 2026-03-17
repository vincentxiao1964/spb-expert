import random
import string
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

def generate_unique_id(prefix):
    """Generates a unique ID with the given prefix. e.g. SH-20231024-XXXX"""
    import datetime
    today = datetime.date.today().strftime('%Y%m%d')
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{today}-{suffix}"

class CrawledShip(models.Model):
    source_id = models.CharField(_('Source ID'), max_length=100, unique=True)
    source = models.CharField(_('Source'), max_length=50, default='sol')
    source_url = models.URLField(_('Source URL'))
    ship_category = models.CharField(_('Category'), max_length=50, blank=True)
    dwt = models.CharField(_('DWT'), max_length=50, blank=True)
    build_year = models.IntegerField(_('Build Year'), null=True, blank=True)
    width = models.CharField(_('Width'), max_length=50, blank=True)
    length = models.CharField(_('Length'), max_length=50, blank=True)
    depth = models.CharField(_('Depth'), max_length=50, blank=True)
    full_description = models.TextField(_('Full Description'))
    
    # New structured fields
    remark = models.TextField(_('Remark'), blank=True, help_text=_('Extracted remark content'))
    contact_info = models.TextField(_('Contact Info'), blank=True, help_text=_('Extracted contact info'))
    images = models.JSONField(_('Images'), default=list, blank=True, help_text=_('List of image URLs'))
    
    crawled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Crawled Ship Data')
        verbose_name_plural = _('Crawled Ship Data Library')

    def __str__(self):
        return f"{self.source_id} - {self.dwt} DWT"

class CrawledShipSOL(CrawledShip):
    class Meta:
        proxy = True
        verbose_name = _('SOL Data')
        verbose_name_plural = _('SOL Data Library')

class CrawledShipEship(CrawledShip):
    class Meta:
        proxy = True
        verbose_name = _('Eship Data')
        verbose_name_plural = _('Eship Data Library')

class CrawledShipHorizon(CrawledShip):
    class Meta:
        proxy = True
        verbose_name = _('Horizon Data')
        verbose_name_plural = _('Horizon Data Library')

class ShipListing(models.Model):
    class ListingType(models.TextChoices):
        SELL = 'SELL', _('Sell Ship')
        BUY = 'BUY', _('Buy Ship')
        CHARTER_OFFER = 'CHARTER_OFFER', _('For Lease')
        CHARTER_REQUEST = 'CHARTER_REQUEST', _('Lease Wanted')

    class ShipCategory(models.TextChoices):
        SELF_PROPELLED = 'SELF_PROPELLED', _('Self-propelled Deck Barge')
        NON_SELF_PROPELLED = 'NON_SELF_PROPELLED', _('Non-self-propelled Deck Barge')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Approval')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    listing_type = models.CharField(_('Listing Type'), max_length=20, choices=ListingType.choices)
    ship_category = models.CharField(_('Ship Category'), max_length=20, choices=ShipCategory.choices)

    # Unique Identifier
    unique_id = models.CharField(_('Unique ID'), max_length=30, unique=True, blank=True, null=True)

    # Dimensions
    length = models.CharField(_('Length (m)'), max_length=50, blank=True)
    width = models.CharField(_('Width (m)'), max_length=50, blank=True)
    depth = models.CharField(_('Depth (m)'), max_length=50, blank=True)

    dwt = models.CharField(_('Deadweight Tonnage (DWT)'), max_length=50, blank=True)
    build_year = models.IntegerField(_('Year of Build'), null=True, blank=True)
    class_society = models.CharField(_('Classification Society'), max_length=100, blank=True)
    flag_state = models.CharField(_('Flag State'), max_length=100, blank=True)
    delivery_area = models.CharField(_('Delivery Area'), max_length=200, blank=True)

    # For chartering
    start_time = models.DateField(_('Start Time'), null=True, blank=True)

    # Description / Remarks
    description = models.TextField(_('Description (Chinese)'), blank=True,
                                   help_text=_('Additional details about the ship.'))
    description_en = models.TextField(_('Description (English)'), blank=True,
                                      help_text=_('English translation of the description.'))

    contact_info = models.TextField(_('Contact Information'))

    # Stats
    view_count = models.IntegerField(_('View Count'), default=0)
    contact_count = models.IntegerField(_('Contact Count'), default=0)

    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Admin fields
    admin_notes = models.TextField(_('Admin Notes'), blank=True)

    def __str__(self):
        return f"{self.get_listing_type_display()} - {self.get_ship_category_display()} ({self.dwt} DWT)"

    # 必须添加这个方法！
    def get_absolute_url(self):
        return reverse('market:detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if not self.unique_id:
            prefix_map = {
                self.ListingType.SELL: 'SL', # Sell
                self.ListingType.BUY: 'BY', # Buy
                self.ListingType.CHARTER_OFFER: 'CO', # Charter Offer
                self.ListingType.CHARTER_REQUEST: 'CR', # Charter Request
            }
            prefix = prefix_map.get(self.listing_type, 'SH')
            self.unique_id = generate_unique_id(prefix)
            
            # Ensure uniqueness
            while ShipListing.objects.filter(unique_id=self.unique_id).exists():
                self.unique_id = generate_unique_id(prefix)

        # If user is level 2, auto approve?
        # Requirement: "When a member has accumulated 10 approved posts, they will be automatically upgraded to Level 2 Member, enabling them to publish content independently without administrative review."
        if not self.pk:  # Only on creation
            if self.user.membership_level == 2 or self.user.is_superuser or self.user.is_staff:
                self.status = self.Status.APPROVED
        super().save(*args, **kwargs)


class ListingImage(models.Model):
    listing = models.ForeignKey(ShipListing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/')
    is_schematic = models.BooleanField(default=True, help_text=_('Is this a placeholder/schematic image?'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing}"


class MarketNews(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Approval')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news')
    title = models.CharField(_('Title'), max_length=200)
    title_en = models.CharField(_('Title (English)'), max_length=200, blank=True)
    content = models.TextField(_('Content'))
    content_en = models.TextField(_('Content (English)'), blank=True)
    image = models.ImageField(_('Image'), upload_to='news_images/', blank=True, null=True)
    
    # Crawler Fields
    source_url = models.URLField(_('Source URL'), blank=True, null=True)
    original_source = models.CharField(_('Original Source Name'), max_length=100, blank=True)
    
    # Unique Identifier
    unique_id = models.CharField(_('Unique ID'), max_length=30, unique=True, blank=True, null=True, editable=False)

    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Market News')

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = generate_unique_id('NW') # News
            while MarketNews.objects.filter(unique_id=self.unique_id).exists():
                self.unique_id = generate_unique_id('NW')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('market:news_detail', kwargs={'pk': self.pk})


class ListingMatch(models.Model):
    listing_source = models.ForeignKey(ShipListing, on_delete=models.CASCADE, related_name='matches_as_source')
    listing_target = models.ForeignKey(ShipListing, on_delete=models.CASCADE, related_name='matches_as_target')
    score = models.FloatField(default=0.0)
    is_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('listing_source', 'listing_target')
        ordering = ['-score', '-created_at']

    def __str__(self):
        return f"Match: {self.listing_source} -> {self.listing_target} ({self.score})"

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} likes {self.content_object}"


class DailyBriefing(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PUBLISHED = 'PUBLISHED', _('Published')

    content = models.TextField(_('Briefing Content'))
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Daily Market Briefing')
        verbose_name_plural = _('Daily Market Briefings')
        ordering = ['-created_at']

    def __str__(self):
        return f"Briefing {self.created_at.strftime('%Y-%m-%d')}"
