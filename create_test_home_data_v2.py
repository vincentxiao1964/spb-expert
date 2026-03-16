import os
import django
import sys

sys.path.append(r'D:\spb-expert11')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, MerchantProfile
from apps.store.models import Product, Category

user = User.objects.first()
if user:
    mp, created = MerchantProfile.objects.get_or_create(
        user=user,
        defaults={'company_name': "Test Marine Supply", 'is_verified': True}
    )
    print(f"Merchant Profile: {mp.company_name}")
    
    # Now create product
    category = Category.objects.first()
    if not category:
        category = Category.objects.create(name="Spare Parts")
        
    p, created = Product.objects.get_or_create(
        name="Recommended Engine",
        defaults={
            'merchant': mp,
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
