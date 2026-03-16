
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
    print(f"ID: {l.id} | DWT: {l.dwt} | UniqueID: '{l.unique_id}'")

print("\nChecking for specific DWT 8000 and 12000:")
for l in ShipListing.objects.filter(dwt__in=[8000, 12000]):
    print(f"ID: {l.id} | DWT: {l.dwt} | UniqueID: '{l.unique_id}'")
