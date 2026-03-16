import os

# 1. Write apps/core/serializers.py
core_serializers_path = r'D:\spb-expert11\apps\core\serializers.py'
core_serializers_content = """from rest_framework import serializers
from .models import Banner

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'link_url', 'order']
"""
with open(core_serializers_path, 'w', encoding='utf-8') as f:
    f.write(core_serializers_content)
print(f"Created {core_serializers_path}")

# 2. Append to apps/store/serializers.py
store_serializers_path = r'D:\spb-expert11\apps\store\serializers.py'
with open(store_serializers_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "HomeIndexSerializer" not in content:
    append_content = """
from apps.core.serializers import BannerSerializer

class HomeIndexSerializer(serializers.Serializer):
    banners = BannerSerializer(many=True)
    categories = CategorySerializer(many=True)
    recommended_products = ProductSerializer(many=True)
"""
    with open(store_serializers_path, 'a', encoding='utf-8') as f:
        f.write(append_content)
    print(f"Appended to {store_serializers_path}")

# 3. Append to apps/store/views.py
store_views_path = r'D:\spb-expert11\apps\store\views.py'
with open(store_views_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "HomeViewSet" not in content:
    # Need to import Banner and HomeIndexSerializer
    # We'll inject imports at the top if missing (simple check)
    imports = "from apps.core.models import Banner\nfrom .serializers import HomeIndexSerializer, CategorySerializer, ProductSerializer\n"
    
    # Simple append for the class
    class_content = """
class HomeViewSet(viewsets.ViewSet):
    \"\"\"
    Homepage Aggregation API
    \"\"\"
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        banners = Banner.objects.filter(is_active=True)
        # Top level categories
        categories = Category.objects.filter(parent__isnull=True, is_active=True)
        recommended_products = Product.objects.filter(is_active=True, is_recommended=True)[:10]

        serializer = HomeIndexSerializer({
            'banners': banners,
            'categories': categories,
            'recommended_products': recommended_products
        }, context={'request': request})
        
        return Response(serializer.data)
"""
    # Replace the existing imports or just append imports? 
    # Let's just append the imports and class at the end, Python handles imports anywhere, 
    # though it's not PEP8, it works. Or better, read and insert.
    # For simplicity/safety, I'll append imports and class.
    
    with open(store_views_path, 'a', encoding='utf-8') as f:
        f.write("\n" + imports + class_content)
    print(f"Appended to {store_views_path}")
