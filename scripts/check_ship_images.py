import os
import django
import sys
import json

# Add project root and apps to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'apps'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spb_expert.settings')
django.setup()

from market.models import ShipListing, ListingImage
from api.serializers import ShipListingSerializer

def check_listing_images(listing_id):
    try:
        listing = ShipListing.objects.get(pk=listing_id)
        print(f"Listing ID: {listing.id}, Title: {listing.title if hasattr(listing, 'title') else 'No Title'}")
        
        images = ListingImage.objects.filter(listing=listing)
        print(f"Image Count (DB): {images.count()}")
        
        for img in images:
            print(f"  Image ID: {img.id}, Path: {img.image.path}, URL: {img.image.url}")
            if os.path.exists(img.image.path):
                print(f"  [OK] File exists: {img.image.path}")
            else:
                print(f"  [MISSING] File does not exist: {img.image.path}")
                
        # Check Serializer Output
        serializer = ShipListingSerializer(listing)
        serialized_data = serializer.data
        print(f"\nSerialized Images: {json.dumps(serialized_data.get('images', []), indent=2)}")
        
    except ShipListing.DoesNotExist:
        print(f"Listing {listing_id} does not exist.")

if __name__ == "__main__":
    check_listing_images(25)
