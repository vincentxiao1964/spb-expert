import os
import django
import sys
from django.utils.crypto import get_random_string

# Add project root to sys.path
sys.path.append(r'd:\spb-expert11')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.store.models import Order
from apps.logistics.models import Shipment, LogisticsProvider
from apps.users.models import MerchantProfile

User = get_user_model()

def run():
    print("Starting Logistics Flow Test...")

    # 1. Get or Create User (Customer)
    username = 'logistics_test_user'
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        u = User.objects.create_user(username=username, password='password123')
        print(f"Created customer user: {username}")

    # 2. Get or Create Merchant User and Profile
    merchant_username = 'merchant_test_user'
    try:
        m_user = User.objects.get(username=merchant_username)
    except User.DoesNotExist:
        m_user = User.objects.create_user(username=merchant_username, password='password123', is_merchant=True)
        print(f"Created merchant user: {merchant_username}")

    merchant_profile, created = MerchantProfile.objects.get_or_create(
        user=m_user,
        defaults={'company_name': 'Global Shipping Supplies Ltd.'}
    )
    if created:
        print(f"Created merchant profile for: {merchant_username}")

    # 3. Create dummy order
    order_no = f"ORD-{get_random_string(8)}"
    o = Order.objects.create(
        user=u, 
        merchant=merchant_profile,
        order_no=order_no,
        total_amount=100.00,
        status='shipped'
    )
    print(f"Created Order: {o.order_no}")

    # 4. Create provider
    p, _ = LogisticsProvider.objects.get_or_create(
        name='Maersk Line',
        defaults={'contact_person': 'Agent Smith', 'phone': '1234567890'}
    )

    # 5. Create shipment
    s = Shipment.objects.create(
        order=o,
        provider=p,
        tracking_number=f"TRK-{get_random_string(8)}",
        status='in_transit',
        customs_status='Cleared'
    )
    print(f"Created Shipment ID {s.id} for Order {o.order_no}")

    # 6. Verify Access
    print("-" * 20)
    print(f"Verifying Logistics Access for User: {u.username}")
    shipments = Shipment.objects.filter(order__user=u)
    print(f"Found {shipments.count()} shipments.")
    for sh in shipments:
        print(f" - Shipment {sh.tracking_number}: {sh.status} (Customs: {sh.customs_status})")
        
    print("Logistics Flow Test Completed Successfully.")

if __name__ == '__main__':
    run()
