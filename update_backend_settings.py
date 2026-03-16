import os
import sys
import django

# Setup Django environment (for migration later, but here just file ops)
sys.path.append(r'D:\spb-expert11')

# 1. Update apps/users/models.py
models_path = r'D:\spb-expert11\apps\users\models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'shop_avatar' not in content:
    old_str = 'company_name = models.CharField(_("Company Name"), max_length=100)'
    new_str = 'company_name = models.CharField(_("Company Name"), max_length=100)\n    description = models.TextField(_("Shop Description"), blank=True)\n    shop_avatar = models.URLField(_("Shop Avatar URL"), blank=True)'
    content = content.replace(old_str, new_str)
    
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated models.py")

# 2. Update apps/users/serializers.py
serializers_path = r'D:\spb-expert11\apps\users\serializers.py'
with open(serializers_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update UserSerializer to include avatar
if "'avatar'" not in content and "'id', 'username'" in content:
    content = content.replace("'id', 'username'", "'id', 'username', 'avatar'")

# Update MerchantProfileSerializer to include new fields
if "'shop_avatar'" not in content:
    old_fields = "['company_name', 'business_license', 'is_verified', 'rating', 'created_at']"
    new_fields = "['company_name', 'description', 'shop_avatar', 'business_license', 'is_verified', 'rating', 'created_at']"
    content = content.replace(old_fields, new_fields)

with open(serializers_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated serializers.py")
