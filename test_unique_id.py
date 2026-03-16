
import os
import django
import sys

# Add project root to path
sys.path.append('d:\\spb-expert9')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spb_expert.settings')
django.setup()

from market.models import ShipListing

print("--- Checking ShipListing Unique IDs ---")
count = 0
for listing in ShipListing.objects.all().order_by('-id')[:10]:
    print(f"ID: {listing.id}, UniqueID: '{listing.unique_id}'")
    if not listing.unique_id:
        print(f"WARNING: Listing {listing.id} has empty unique_id!")
    count += 1

print(f"Checked {count} listings.")
