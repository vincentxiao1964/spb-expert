import os
import django
import sys
from django.utils.crypto import get_random_string

# Add project root to sys.path
sys.path.append(r'd:\spb-expert11')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.procurement.models import ProcurementRequest, Quotation

User = get_user_model()

def run():
    print("Starting Procurement Flow Test (Buyer Shop)...")

    # 1. Get or Create Buyer
    buyer_username = 'buyer_test_user'
    try:
        buyer = User.objects.get(username=buyer_username)
    except User.DoesNotExist:
        buyer = User.objects.create_user(username=buyer_username, password='password123')
        print(f"Created buyer user: {buyer_username}")

    # 2. Get or Create Supplier
    supplier_username = 'supplier_test_user'
    try:
        supplier = User.objects.get(username=supplier_username)
    except User.DoesNotExist:
        supplier = User.objects.create_user(username=supplier_username, password='password123', is_merchant=True)
        print(f"Created supplier user: {supplier_username}")

    # 3. Buyer posts a Procurement Request (Sample Required)
    req = ProcurementRequest.objects.create(
        user=buyer,
        title=f"Need High Quality Valves {get_random_string(4)}",
        description="Looking for 100 units of DN50 valves. Must see sample first.",
        budget=5000.00,
        is_sample_required=True
    )
    print(f"Buyer posted request: {req.title} (Sample Required: {req.is_sample_required})")

    # 4. Supplier submits a Quotation
    quote = Quotation.objects.create(
        procurement=req,
        supplier=supplier,
        price=4800.00,
        message="We have excellent valves. Sample can be sent immediately."
    )
    print(f"Supplier submitted quote: {quote.price}")

    # 5. Simulate Sample Flow
    # Supplier sends sample
    quote.status = 'sample_sent'
    quote.is_sample_provided = True
    quote.save()
    print(f"Supplier sent sample. Quote Status: {quote.status}")

    # Buyer receives and approves sample
    # (In a real app, this would be an API call by the buyer)
    quote.status = 'sample_approved'
    quote.save()
    print(f"Buyer approved sample. Quote Status: {quote.status}")

    # Buyer accepts the quote (Final Deal)
    quote.status = 'accepted'
    quote.save()
    print(f"Buyer accepted quote. Quote Status: {quote.status}")
    
    # Request should be closed or marked as in progress
    req.status = 'closed' # or completed
    req.save()
    print(f"Procurement Request Status: {req.status}")

    print("Procurement Flow Test Completed Successfully.")

if __name__ == '__main__':
    run()
