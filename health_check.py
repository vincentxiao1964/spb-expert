
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spb_expert.settings')
django.setup()

from django.contrib.auth import get_user_model
from market.models import ShipListing
from news.models import Article

User = get_user_model()

print("--- HEALTH CHECK START ---")

# 1. Check User Model
try:
    user_count = User.objects.count()
    first_user = User.objects.first()
    print(f"[OK] User Model: {user_count} users found.")
    if first_user:
        # Access new fields to ensure columns exist
        print(f"    First user: {first_user.username}")
        # Try accessing potentially problematic fields if they were added recently
        # print(f"    Business Content: {getattr(first_user, 'business_content', 'N/A')}")
except Exception as e:
    print(f"[ERROR] User Model: {e}")

# 2. Check ShipListing Model
try:
    ship_count = ShipListing.objects.count()
    print(f"[OK] ShipListing Model: {ship_count} listings found.")
except Exception as e:
    print(f"[ERROR] ShipListing Model: {e}")

# 3. Check News Article Model (New App)
try:
    article_count = Article.objects.count()
    print(f"[OK] Article Model: {article_count} articles found.")
except Exception as e:
    print(f"[ERROR] Article Model: {e}")

print("--- HEALTH CHECK END ---")
