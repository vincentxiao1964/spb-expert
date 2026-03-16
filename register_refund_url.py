import os

# Register RefundViewSet in apps/store/urls.py
urls_path = r'D:\spb-expert11\apps\store\urls.py'
with open(urls_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Import
if "from .views import" in content:
    # Append RefundViewSet to imports
    if "RefundViewSet" not in content:
        # We can just replace the import line or add it separately
        content = content.replace("from .views import FavoriteViewSet", "from .views import RefundViewSet, FavoriteViewSet")

# 2. Register Router
if "router.register(r'refunds', RefundViewSet)" not in content:
    content = content.replace("router.register(r'favorites', FavoriteViewSet, basename='favorite')", 
                              "router.register(r'favorites', FavoriteViewSet, basename='favorite')\nrouter.register(r'refunds', RefundViewSet, basename='refund')")

with open(urls_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated apps/store/urls.py with RefundViewSet")
