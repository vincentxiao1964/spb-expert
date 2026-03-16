from django.db import models
from django.utils.translation import gettext_lazy as _
from market.models import ShipListing

class ShipExtendedInfo(models.Model):
    """
    Extension of ShipListing to store technical details for Hymart Big Data module.
    """
    ship_listing = models.OneToOneField(
        ShipListing, 
        on_delete=models.CASCADE, 
        related_name='extended_info',
        verbose_name=_('Related Ship')
    )
    
    # Technical Specs
    draft_laden = models.FloatField(_('Laden Draft (m)'), null=True, blank=True)
    draft_ballast = models.FloatField(_('Ballast Draft (m)'), null=True, blank=True)
    
    hatch_size = models.CharField(_('Hatch Size'), max_length=100, blank=True, help_text=_('L x W'))
    hatch_count = models.IntegerField(_('Hatch Count'), default=1)
    
    main_engine_power = models.CharField(_('Main Engine Power (kW)'), max_length=50, blank=True)
    speed_laden = models.FloatField(_('Speed Laden (knots)'), null=True, blank=True)
    speed_ballast = models.FloatField(_('Speed Ballast (knots)'), null=True, blank=True)
    
    fuel_consumption_sea = models.FloatField(_('Fuel Consumption at Sea (t/day)'), null=True, blank=True)
    fuel_consumption_port = models.FloatField(_('Fuel Consumption in Port (t/day)'), null=True, blank=True)
    
    # Capacities
    grain_capacity = models.FloatField(_('Grain Capacity (cbm)'), null=True, blank=True)
    bale_capacity = models.FloatField(_('Bale Capacity (cbm)'), null=True, blank=True)
    deck_strength = models.CharField(_('Deck Strength (t/m2)'), max_length=50, blank=True)

    # Classification
    imo_number = models.CharField(_('IMO Number'), max_length=20, blank=True, unique=True, null=True)
    call_sign = models.CharField(_('Call Sign'), max_length=20, blank=True)
    mmsi = models.CharField(_('MMSI'), max_length=20, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Extended Info for {self.ship_listing}"

class VoyageHistory(models.Model):
    """
    Historical voyage records for big data analysis.
    """
    ship_listing = models.ForeignKey(
        ShipListing, 
        on_delete=models.CASCADE, 
        related_name='voyage_history'
    )
    
    departure_port = models.CharField(_('Departure Port'), max_length=100)
    arrival_port = models.CharField(_('Arrival Port'), max_length=100)
    
    departure_date = models.DateField(_('Departure Date'))
    arrival_date = models.DateField(_('Arrival Date'), null=True, blank=True)
    
    cargo_description = models.CharField(_('Cargo'), max_length=200, blank=True)
    quantity = models.FloatField(_('Quantity (MT)'), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-departure_date']

    def __str__(self):
        return f"{self.ship_listing} : {self.departure_port} -> {self.arrival_port}"
