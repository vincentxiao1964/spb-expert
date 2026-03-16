
import re
import os

file_path = r'D:\spb-expert11\apps\store\views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import for ProductImage
if "from .models import Category, Product" in content and "ProductImage" not in content:
    content = content.replace("from .models import Category, Product", "from .models import Category, Product, ProductImage")

# The method code to insert
upload_method = '''
    @action(detail=True, methods=['post'], parser_classes=[parsers.MultiPartParser])
    def upload_image(self, request, pk=None):
        product = self.get_object()
        # Check ownership
        if product.merchant.user != request.user:
            return Response({'error': 'Permission denied'}, status=403)
            
        image_file = request.FILES.get('image')
        if not image_file:
             return Response({'error': 'No image provided'}, status=400)
             
        # Create ProductImage
        # Check if it's the first image
        is_main = not product.images.exists()
        ProductImage.objects.create(product=product, image=image_file, is_main=is_main)
        
        return Response({'status': 'uploaded'})
'''

if "def upload_image" not in content:
    # Insert before "from apps.core.models import Banner" which follows ProductViewSet
    if "from apps.core.models import Banner" in content:
        content = content.replace("from apps.core.models import Banner", upload_method + "\nfrom apps.core.models import Banner")
    elif "class HomeViewSet" in content:
         # Fallback
         content = content.replace("class HomeViewSet", upload_method + "\nclass HomeViewSet")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Updated {file_path}")
