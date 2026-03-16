from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Port(models.Model):
    name_en = models.CharField(_("Port Name (EN)"), max_length=100, unique=True)
    name_zh = models.CharField(_("Port Name (ZH)"), max_length=100, blank=True)
    country_en = models.CharField(_("Country (EN)"), max_length=100)
    country_zh = models.CharField(_("Country (ZH)"), max_length=100, blank=True)
    latitude = models.FloatField(_("Latitude"))
    longitude = models.FloatField(_("Longitude"))
    
    class Meta:
        verbose_name = _("Port")
        verbose_name_plural = _("Port Library")
        ordering = ['name_en']

    def __str__(self):
        if self.name_zh:
            return f"{self.name_en} / {self.name_zh}"
        return self.name_en

class BunkerPrice(models.Model):
    FUEL_TYPES = (
        ('VLSFO', 'VLSFO (0.5%)'),
        ('LSMGO', 'LSMGO (0.1%)'),
        ('IFO380', 'IFO 380'),
        ('MGO', 'MGO'),
        ('RME180', 'RME 180'),
        ('DIESEL0', '0# Diesel'),
    )
    port = models.ForeignKey(Port, on_delete=models.CASCADE, related_name='bunker_prices', verbose_name=_("Port"))
    date = models.DateField(_("Date"), default=timezone.now)
    fuel_type = models.CharField(_("Fuel Type"), max_length=10, choices=FUEL_TYPES)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2, help_text=_("USD/MT or CNY/MT"))
    currency = models.CharField(_("Currency"), max_length=3, default='USD', choices=(('USD', 'USD'), ('CNY', 'CNY')))
    change = models.DecimalField(_("Change"), max_digits=10, decimal_places=2, default=0, help_text=_("Change from previous day"))
    source = models.CharField(_("Source"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("Bunker Price")
        verbose_name_plural = _("Bunker Prices")
        ordering = ['-date', 'port__name_en']
        unique_together = ['port', 'date', 'fuel_type']

    def __str__(self):
        return f"{self.port} - {self.fuel_type} - {self.date}: {self.price} {self.currency}"

class ContractTemplate(models.Model):
    class Category(models.TextChoices):
        SALE_PURCHASE = 'SNP', _('Sale & Purchase')
        CHARTER_PARTY = 'CP', _('Charter Party')

    class Scope(models.TextChoices):
        DOMESTIC = 'DOMESTIC', _('Domestic (China)')
        INTERNATIONAL = 'INTERNATIONAL', _('International')

    class SubType(models.TextChoices):
        SNP_GENERAL = 'SNP_GEN', _('General S&P')
        TIME_CHARTER = 'TC', _('Time Charter')
        BAREBOAT_CHARTER = 'BB', _('Bareboat Charter')
        VOYAGE_CHARTER = 'VC', _('Voyage Charter')
    
    title = models.CharField(_("Title"), max_length=255)
    category = models.CharField(_("Category"), max_length=10, choices=Category.choices)
    scope = models.CharField(_("Scope"), max_length=20, choices=Scope.choices)
    sub_type = models.CharField(_("Type"), max_length=20, choices=SubType.choices)
    
    description = models.TextField(_("Description"), blank=True)
    file = models.FileField(_("Template File"), upload_to='contract_templates/', blank=True, null=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Contract Template")
        verbose_name_plural = _("Contract Templates")
        ordering = ['category', 'scope', 'sub_type']

    def __str__(self):
        return f"{self.title} ({self.get_scope_display()})"
