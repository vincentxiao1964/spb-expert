import os
import django
import sys

sys.path.append(r'D:\spb-expert11')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.models import Banner
from apps.store.models import Product, Category
from apps.users.models import User, MerchantProfile

# Create Banner
if not Banner.objects.exists():
    Banner.objects.create(title="Summer Sale", link_url="/sale", order=1)
    print("Created Banner")

# Ensure Merchant and Category exist (from previous steps)
# Create Recommended Product
user = User.objects.first()
if user and hasattr(user, 'merchant_profile'):
    merchant = user.merchant_profile
    category = Category.objects.first()
    
    p, created = Product.objects.get_or_create(
        name="Recommended Engine",
        defaults={
            'merchant': merchant,
            'category': category,
            'price': 5000.00,
            'stock': 10,
            'is_recommended': True
        }
    )
    if not created:
        p.is_recommended = True
        p.save()
    print("Created/Updated Recommended Product")
else:
    print("No merchant found, skipping product creation")
