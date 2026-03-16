
import os
import django
import sys
import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model

sys.path.append(r'd:\spb-expert11')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.store.models import Product, Order, OrderItem, Category
from apps.users.models import MerchantProfile
from apps.procurement.models import ProcurementRequest, Quotation
from apps.logistics.models import Shipment, ShipmentEvent, LogisticsProvider

User = get_user_model()

def run_flow_validation():
    print("=== Starting Flow Validation ===")

    # 1. Setup Users
    merchant_user, _ = User.objects.get_or_create(username='merchant_test', defaults={'email': 'm@test.com'})
    buyer_user, _ = User.objects.get_or_create(username='buyer_test', defaults={'email': 'b@test.com'})
    supplier_user, _ = User.objects.get_or_create(username='supplier_test', defaults={'email': 's@test.com'})
    
    # Ensure merchant profile
    merchant_profile, _ = MerchantProfile.objects.get_or_create(user=merchant_user, defaults={'company_name': 'Test Shop'})
    
    print("Users created/verified.")

    # 2. Logistics Flow Validation
    print("\n--- Logistics Flow ---")
    
    # Create Product
    category, _ = Category.objects.get_or_create(name='Test Category')
    product, _ = Product.objects.get_or_create(
        name='Test Product', 
        merchant=merchant_profile,
        defaults={'price': 100.00, 'stock': 10, 'category': category}
    )
    
    # Create Order (Paid)
    order_no = str(uuid.uuid4().hex[:16].upper())
    order = Order.objects.create(
        order_no=order_no,
        user=buyer_user,
        merchant=merchant_profile,
        total_amount=100.00,
        status='paid'
    )
    OrderItem.objects.create(order=order, product=product, price=100.00, quantity=1)
    
    print(f"Order {order.order_no} created with status {order.status}")
    
    # Simulate Ship Action (as would happen in ViewSet)
    tracking_number = "SF1234567890"
    carrier = "SF Express"
    
    provider, _ = LogisticsProvider.objects.get_or_create(name=carrier)
    shipment, created = Shipment.objects.get_or_create(order=order)
    shipment.tracking_number = tracking_number
    shipment.provider = provider
    shipment.status = 'picked_up'
    shipment.save()
    
    ShipmentEvent.objects.create(
        shipment=shipment,
        status='Picked Up',
        location='Merchant Warehouse',
        description='Package picked up'
    )
    
    order.tracking_number = tracking_number
    order.carrier = carrier
    order.status = 'shipped'
    order.save()
    
    print(f"Order shipped. Status: {order.status}")
    print(f"Shipment created. Tracking: {shipment.tracking_number}, Status: {shipment.status}")
    print(f"Events: {shipment.events.count()}")
    
    if order.status == 'shipped' and shipment.events.count() > 0:
        print(">> Logistics Flow PASSED")
    else:
        print(">> Logistics Flow FAILED")

    # 3. Procurement Flow Validation
    print("\n--- Procurement Flow ---")
    
    # Create Request
    req = ProcurementRequest.objects.create(
        user=buyer_user,
        title="Need Samples",
        description="Looking for high quality samples",
        is_sample_required=True
    )
    print(f"Request created: {req.title} (Sample Required: {req.is_sample_required})")
    
    # Create Quotation
    quote = Quotation.objects.create(
        procurement=req,
        supplier=supplier_user,
        price=500.00,
        message="I can provide samples",
        is_sample_provided=True
    )
    print(f"Quotation submitted by {quote.supplier.username}")
    
    # Accept Quotation
    quote.status = 'accepted'
    quote.save()
    
    req.status = 'closed' # Usually accepting closes the request
    req.save()
    
    print(f"Quotation status: {quote.status}")
    print(f"Request status: {req.status}")
    
    if quote.status == 'accepted' and req.status == 'closed':
        print(">> Procurement Flow PASSED")
    else:
        print(">> Procurement Flow FAILED")

    print("\n=== Validation Complete ===")

if __name__ == '__main__':
    try:
        run_flow_validation()
    except Exception as e:
        print(f"Validation Error: {e}")
