import os
import sys
import django
from datetime import date

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spb_expert.settings")
django.setup()

from django.contrib.auth import get_user_model
from market.models import ShipListing, MarketNews, ShipListing
from core.models import MemberMessage

User = get_user_model()

def create_test_data():
    print("Creating test data...")

    # 1. Create User
    username = "admin"
    password = "admin123"
    email = "admin@example.com"
    
    user, created = User.objects.get_or_create(username=username, defaults={
        'email': email,
        'is_staff': True,
        'is_superuser': True,
        'phone_number': '13800138000'
    })
    
    if created:
        user.set_password(password)
        user.save()
        print(f"Created superuser: {username} / {password}")
    else:
        print(f"User {username} already exists")

    # 2. Create Ship Listings
    if ShipListing.objects.count() == 0:
        ShipListing.objects.create(
            user=user,
            listing_type=ShipListing.ListingType.SELL,
            ship_category=ShipListing.ShipCategory.SELF_PROPELLED,
            dwt="5000",
            length="100",
            width="20",
            depth="5",
            build_year=2020,
            description="Test Ship 1 - High quality vessel",
            contact_info="13800138000",
            status=ShipListing.Status.APPROVED
        )
        ShipListing.objects.create(
            user=user,
            listing_type=ShipListing.ListingType.BUY,
            ship_category=ShipListing.ShipCategory.NON_SELF_PROPELLED,
            dwt="3000",
            description="Looking for a barge",
            contact_info="13800138000",
            status=ShipListing.Status.APPROVED
        )
        print("Created 2 ship listings")
    else:
        print("Ship listings already exist")

    # 3. Create Market News
    if MarketNews.objects.count() == 0:
        MarketNews.objects.create(
            user=user,
            title="Market Analysis 2026",
            content="The shipping market is recovering steadily...",
            status=MarketNews.Status.APPROVED
        )
        MarketNews.objects.create(
            user=user,
            title="New Regulations Update",
            content="New environmental regulations coming into effect...",
            status=MarketNews.Status.APPROVED
        )
        print("Created 2 market news")
    else:
        print("Market news already exist")
        
    # 4. Create Forum Posts
    if MemberMessage.objects.count() == 0:
        MemberMessage.objects.create(
            user=user,
            content="Hello everyone! This is the first post in the local environment."
        )
        print("Created 1 forum post")
    else:
        print("Forum posts already exist")

if __name__ == "__main__":
    create_test_data()
