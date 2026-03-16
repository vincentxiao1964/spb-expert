from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import TimeStampedModel

class JobPosition(TimeStampedModel):
    """
    Crew Job Position (e.g., Deck Department -> Captain)
    """
    name = models.CharField(_('Position Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True, max_length=100)
    parent = models.ForeignKey(
        'self', 
        verbose_name=_('Department/Category'),
        on_delete=models.CASCADE, 
        related_name='positions', 
        null=True, 
        blank=True
    )
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    order = models.PositiveIntegerField(_('Display Order'), default=0)

    class Meta:
        verbose_name = _('Job Position')
        verbose_name_plural = _('Job Positions')
        ordering = ['order', 'name']

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

class JobListing(TimeStampedModel):
    """
    Job Listing posted by Companies (e.g. "Captain needed for Bulk Carrier")
    """
    class ShipType(models.TextChoices):
        BULK_CARRIER = 'BULK', _('Bulk Carrier')
        CONTAINER = 'CONTAINER', _('Container Ship')
        TANKER = 'TANKER', _('Tanker')
        GENERAL_CARGO = 'GENERAL', _('General Cargo')
        OTHER = 'OTHER', _('Other')

    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_listings',
        verbose_name=_('Employer')
    )
    position = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT,
        related_name='listings',
        verbose_name=_('Position')
    )
    title = models.CharField(_('Job Title'), max_length=200)
    ship_type = models.CharField(_('Ship Type'), max_length=20, choices=ShipType.choices, default=ShipType.BULK_CARRIER)
    salary_range = models.CharField(_('Salary Range'), max_length=100, help_text=_('e.g. $3000-$5000'))
    contract_duration = models.CharField(_('Contract Duration'), max_length=100, help_text=_('e.g. 6 months'))
    
    requirements = models.TextField(_('Requirements'), blank=True)
    description = models.TextField(_('Job Description'), blank=True)
    
    is_active = models.BooleanField(_('Is Active'), default=True)
    view_count = models.PositiveIntegerField(_('View Count'), default=0)

    class Meta:
        verbose_name = _('Job Listing')
        verbose_name_plural = _('Job Listings')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.employer.username})"
