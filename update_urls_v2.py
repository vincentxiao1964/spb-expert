import os

# 1. Update apps/users/urls.py
users_urls_path = r'D:\spb-expert11\apps\users\urls.py'
with open(users_urls_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "AddressViewSet" not in content:
    new_content = """from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MerchantApplicationView, MerchantProfileDetailView, AddressViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('merchant/apply/', MerchantApplicationView.as_view(), name='merchant-apply'),
    path('merchant/me/', MerchantProfileDetailView.as_view(), name='merchant-detail'),
    path('', include(router.urls)),
]
"""
    with open(users_urls_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated {users_urls_path}")

# 2. Update apps/store/urls.py
store_urls_path = r'D:\spb-expert11\apps\store\urls.py'
with open(store_urls_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "CartViewSet" not in content:
    # Add imports
    content = content.replace("from .views import CategoryViewSet, ProductViewSet, HomeViewSet", 
                              "from .views import CategoryViewSet, ProductViewSet, HomeViewSet, CartViewSet, OrderViewSet")
    
    # Add registrations
    if "router.register(r'home', HomeViewSet, basename='home')" in content:
        content = content.replace("router.register(r'home', HomeViewSet, basename='home')", 
                                  "router.register(r'home', HomeViewSet, basename='home')\nrouter.register(r'cart', CartViewSet, basename='cart')\nrouter.register(r'orders', OrderViewSet, basename='order')")
    
    with open(store_urls_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {store_urls_path}")
