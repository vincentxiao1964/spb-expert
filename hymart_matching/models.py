from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from market.models import ShipListing, generate_unique_id

class CargoRequest(models.Model):
    class CargoType(models.TextChoices):
        BULK = 'BULK', _('Bulk Cargo')
        GENERAL = 'GENERAL', _('General Cargo')
        CONTAINER = 'CONTAINER', _('Container')
        LIQUID = 'LIQUID', _('Liquid Cargo')

    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        MATCHED = 'MATCHED', _('Matched')
        CLOSED = 'CLOSED', _('Closed')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cargo_requests')
    cargo_type = models.CharField(_('Cargo Type'), max_length=20, choices=CargoType.choices)
    weight = models.FloatField(_('Weight (Tons)'), help_text=_('Estimated weight in tons'))
    volume = models.FloatField(_('Volume (CBM)'), null=True, blank=True, help_text=_('Estimated volume in cubic meters'))
    max_draft = models.FloatField(_('Max Draft (m)'), null=True, blank=True, help_text=_('Port restriction for draft'))
    dwt_tolerance_percent = models.FloatField(_('DWT Tolerance (%)'), null=True, blank=True)
    draft_tolerance_percent = models.FloatField(_('Draft Tolerance (%)'), null=True, blank=True)
    
    origin = models.CharField(_('Origin'), max_length=100)
    destination = models.CharField(_('Destination'), max_length=100)

    # Unique Identifier
    unique_id = models.CharField(_('Unique ID'), max_length=30, unique=True, blank=True, null=True, editable=False)

    loading_date = models.DateField(_('Loading Date'))
    
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.OPEN)

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = generate_unique_id('CG') # Cargo
            while CargoRequest.objects.filter(unique_id=self.unique_id).exists():
                self.unique_id = generate_unique_id('CG')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cargo_type} - {self.weight}T ({self.origin} -> {self.destination})"

class MatchResult(models.Model):
    cargo_request = models.ForeignKey(CargoRequest, on_delete=models.CASCADE, related_name='matches')
    ship_listing = models.ForeignKey(ShipListing, on_delete=models.CASCADE, related_name='cargo_matches')
    score = models.FloatField(_('Match Score'), help_text=_('0.0 to 1.0'))
    created_at = models.DateTimeField(auto_now_add=True)
    is_viewed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f"Match: {self.cargo_request.id} <-> {self.ship_listing.id} ({self.score})"
