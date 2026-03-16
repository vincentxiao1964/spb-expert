import os

store_urls_path = r'D:\spb-expert11\apps\store\urls.py'
with open(store_urls_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "HomeViewSet" not in content:
    # Add import
    content = content.replace("from .views import CategoryViewSet, ProductViewSet", "from .views import CategoryViewSet, ProductViewSet, HomeViewSet")
    
    # Add router registration
    if "router.register(r'products', ProductViewSet, basename='product')" in content:
        content = content.replace("router.register(r'products', ProductViewSet, basename='product')", 
                                  "router.register(r'products', ProductViewSet, basename='product')\nrouter.register(r'home', HomeViewSet, basename='home')")
    
    with open(store_urls_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {store_urls_path}")
else:
    print("HomeViewSet already in urls")
