
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.store.models import Order
from apps.logistics.models import Shipment, LogisticsProvider

User = get_user_model()
u = User.objects.get(username='logistics_zoahucrl')

# Create dummy order
o = Order.objects.create(
    user=u, 
    order_no='ORD-sponbnij',
    total_amount=100.00,
    status='shipped'
)

# Create provider
p, _ = LogisticsProvider.objects.get_or_create(name='Maersk Line')

# Create shipment
s = Shipment.objects.create(
    order=o,
    provider=p,
    tracking_number='TRK-xotckywb',
    status='in_transit',
    customs_status='Cleared'
)
print(f"Created Shipment ID {s.id} for Order {o.order_no}")
