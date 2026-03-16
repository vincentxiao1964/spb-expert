
import os
import django
import sys

sys.path.append('d:\\spb-expert9')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spb_expert.settings')
django.setup()

from market.models import ShipListing

print("Checking ShipListing unique_ids...")
listings = ShipListing.objects.all().order_by('-updated_at')[:5]
for l in listings:
    print(f"ID: {l.id} | Type: {l.get_listing_type_display()} | Category: {l.get_ship_category_display()} | DWT: {l.dwt} | UniqueID: '{l.unique_id}'")

print("\nChecking specific listing from screenshot (8000t or 12000t)...")
l1 = ShipListing.objects.filter(dwt=8000).first()
if l1:
    print(f"Found 8000t: ID={l1.id}, UniqueID='{l1.unique_id}'")
else:
    print("8000t not found")

l2 = ShipListing.objects.filter(dwt=12000).first()
if l2:
    print(f"Found 12000t: ID={l2.id}, UniqueID='{l2.unique_id}'")
else:
    print("12000t not found")
