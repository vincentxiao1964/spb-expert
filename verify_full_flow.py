
import os
import sys
import django
from django.utils import timezone
import json

# Setup Django environment
sys.path.append(r'd:\spb-expert11')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.procurement.models import ProcurementRequest, Quotation
from apps.logistics.models import Shipment, LogisticsProvider, ShipmentEvent
from apps.store.models import Order, OrderItem
from apps.users.models import MerchantProfile
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.procurement.views import ProcurementRequestViewSet, QuotationViewSet
from apps.store.views import MerchantOrderViewSet

User = get_user_model()
factory = APIRequestFactory()

def run_verification():
    print("--- Starting Full Flow Verification ---")
    
    # 1. Setup Users
    buyer_user, _ = User.objects.get_or_create(username='test_buyer_v2', defaults={'email': 'buyer@test.com'})
    supplier_user, _ = User.objects.get_or_create(username='test_supplier_v2', defaults={'email': 'supplier@test.com'})
    
    # Ensure supplier has merchant profile
    MerchantProfile.objects.get_or_create(user=supplier_user, defaults={'company_name': 'Supplier Co.'})
    
    print(f"Users ready: Buyer={buyer_user.username}, Supplier={supplier_user.username}")

    # 2. Buyer creates Procurement Request
    req_data = {
        'title': 'Need 1000 Steel Pipes',
        'description': 'High quality steel pipes required.',
        'budget': 5000.00,
        'is_sample_required': True
    }
    
    request = factory.post('/api/v1/procurement/requests/', req_data)
    force_authenticate(request, user=buyer_user)
    view = ProcurementRequestViewSet.as_view({'post': 'create'})
    response = view(request)
    
    if response.status_code == 201:
        procurement_id = response.data['id']
        print(f"Procurement Request created: ID {procurement_id}")
    else:
        print(f"Failed to create request: {response.data}")
        return

    # 3. Supplier creates Quotation
    quote_data = {
        'price': 4500.00,
        'message': 'We can supply this.',
        'is_sample_provided': True
    }
    
    request = factory.post(f'/api/v1/procurement/requests/{procurement_id}/quote/', quote_data)
    force_authenticate(request, user=supplier_user)
    view = ProcurementRequestViewSet.as_view({'post': 'quote'})
    response = view(request, pk=procurement_id)
    
    if response.status_code == 201:
        quotation_id = response.data['id']
        print(f"Quotation created: ID {quotation_id}")
    else:
        print(f"Failed to create quotation: {response.data}")
        return

    # 4. Buyer Accepts Quotation (PATCH)
    patch_data = {'status': 'accepted'}
    request = factory.patch(f'/api/v1/procurement/quotations/{quotation_id}/', patch_data)
    force_authenticate(request, user=buyer_user)
    view = QuotationViewSet.as_view({'patch': 'partial_update'})
    response = view(request, pk=quotation_id)
    
    if response.status_code == 200:
        print("Quotation accepted successfully.")
    else:
        print(f"Failed to accept quotation: {response.data}")
        return

    # 5. Verify Status Updates
    procurement = ProcurementRequest.objects.get(id=procurement_id)
    quotation = Quotation.objects.get(id=quotation_id)
    
    print(f"Procurement Status: {procurement.status} (Expected: closed)")
    print(f"Quotation Status: {quotation.status} (Expected: accepted)")
    
    if procurement.status != 'closed' or quotation.status != 'accepted':
        print("ERROR: Status update logic failed!")
        return

    # 6. Create Order and Ship (Logistics)
    # Create dummy order first
    order = Order.objects.create(
        user=buyer_user,
        merchant=supplier_user.merchant_profile,
        total_amount=100.00,
        status='paid',
        order_no='TESTORDER002'
    )
    print(f"Order created: {order.order_no}")

    # Ship Order
    ship_data = {
        'tracking_number': 'TRACK123456',
        'carrier': 'DHL'
    }
    
    request = factory.post(f'/api/v1/merchant/orders/{order.id}/ship/', ship_data)
    force_authenticate(request, user=supplier_user)
    view = MerchantOrderViewSet.as_view({'post': 'ship'})
    response = view(request, pk=order.id)
    
    if response.status_code == 200:
        print("Order shipped successfully.")
        shipment_id = response.data.get('shipment_id') or Shipment.objects.get(order=order).id
        
        # Verify Shipment and Events
        shipment = Shipment.objects.get(id=shipment_id)
        events = ShipmentEvent.objects.filter(shipment=shipment)
        
        print(f"Shipment Provider: {shipment.provider.name}")
        print(f"Shipment Status: {shipment.status}")
        print(f"Events Count: {events.count()}")
        if events.exists():
             print(f"First Event: {events.first().description}")
    else:
        print(f"Failed to ship order: {response.data}")

if __name__ == '__main__':
    run_verification()
