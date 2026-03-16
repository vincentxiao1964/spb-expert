
import os

base_dir = r"d:\spb-expert11\apps\logistics"
os.makedirs(base_dir, exist_ok=True)

# __init__.py
with open(os.path.join(base_dir, "__init__.py"), "w") as f:
    f.write("")

# apps.py
with open(os.path.join(base_dir, "apps.py"), "w") as f:
    f.write("""from django.apps import AppConfig

class LogisticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.logistics'
""")

# models.py
with open(os.path.join(base_dir, "models.py"), "w") as f:
    f.write("""from django.db import models
from apps.store.models import Order

class LogisticsProvider(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    api_endpoint = models.URLField(blank=True, help_text="Integration endpoint")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Shipment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('customs_processing', 'Customs Processing'),
        ('customs_cleared', 'Customs Cleared'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    provider = models.ForeignKey(LogisticsProvider, on_delete=models.SET_NULL, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    customs_status = models.CharField(max_length=100, blank=True, help_text="e.g. Cleared, Held")
    
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment for {self.order.order_no}"
""")

# admin.py
with open(os.path.join(base_dir, "admin.py"), "w") as f:
    f.write("""from django.contrib import admin
from .models import LogisticsProvider, Shipment

admin.site.register(LogisticsProvider)
admin.site.register(Shipment)
""")

print("Created logistics app files")
