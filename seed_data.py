import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append(r'd:\spb-expert11')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import MerchantProfile
from apps.procurement.models import ProcurementRequest, Quotation
from apps.logistics.models import Shipment, LogisticsProvider, ShipmentEvent
from apps.store.models import Order

User = get_user_model()

def seed_data():
    print("Seeding data...")
    
    # Ensure we have a user
    user, created = User.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com'})
    if created:
        user.set_password('password123')
        user.save()
        print(f"Created user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")

    # Ensure we have a merchant profile
    merchant_user, _ = User.objects.get_or_create(username='merchant_user', defaults={'email': 'merchant@example.com'})
    if _:
        merchant_user.set_password('password123')
        merchant_user.save()
    
    merchant_profile, _ = MerchantProfile.objects.get_or_create(
        user=merchant_user,
        defaults={'company_name': 'Global Marine Supplies', 'description': 'Best marine parts'}
    )
    
    # 1. Seed Procurement (Buyer Shop)
    print("Seeding Procurement Requests...")
    titles = ["Need 500kg Marine Paint", "Urgent: Engine Spare Parts", "Looking for Safety Equipment"]
    for i, title in enumerate(titles):
        req, created = ProcurementRequest.objects.get_or_create(
            title=title,
            defaults={
                'user': user,
                'description': f"We need high quality {title.lower()}. Please provide samples first.",
                'budget': 1000 + (i * 500),
                'status': 'open',
                'is_sample_required': True,
                'deadline': timezone.now() + timedelta(days=7)
            }
        )
        if created:
            print(f"Created Request: {req.title}")
            
    # 2. Seed Logistics
    print("Seeding Logistics...")
    provider, _ = LogisticsProvider.objects.get_or_create(
        name="Global Marine Logistics",
        defaults={'phone': '+1-555-0199', 'contact_person': 'John Doe'}
    )
    
    # Create a dummy order first
    order_no = f"ORD-{int(timezone.now().timestamp())}"
    order, created = Order.objects.get_or_create(
        user=user,
        status='shipped',
        defaults={
            'order_no': order_no,
            'merchant': merchant_profile,
            'total_amount': 2500.00,
            'address': '123 Port Road, Singapore',
            'recipient_name': 'Captain Jack',
            'phone': '+65 9123 4567'
        }
    )
    if created:
        print(f"Created Order: {order.order_no}")

    # Create shipment linked to order
    shipment, created = Shipment.objects.get_or_create(
        order=order,
        defaults={
            'tracking_number': "TRK123456789",
            'provider': provider,
            'status': 'in_transit',
            'customs_status': 'cleared',
            'estimated_delivery': timezone.now() + timedelta(days=5)
        }
    )
    
    if created:
        print(f"Created Shipment: {shipment.tracking_number}")
        # Add events
        events = [
            ('picked_up', 'Cargo picked up at Shanghai', -2),
            ('departed', 'Vessel departed from Shanghai Port', -1),
            ('customs', 'Customs clearance completed', 0)
        ]
        
        for status_code, desc, days_offset in events:
            ShipmentEvent.objects.create(
                shipment=shipment,
                status=status_code,
                location='Shanghai',
                description=desc
            ) # timestamp is auto_now_add
            
    print("Seeding completed successfully.")

if __name__ == '__main__':
    try:
        seed_data()
    except Exception as e:
        print(f"Error seeding data: {e}")
