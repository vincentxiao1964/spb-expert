import os

# 1. Update apps/users/views.py (Add UserMeView)
users_views_path = r'D:\spb-expert11\apps\users\views.py'
users_views_append = """
from .serializers import UserSerializer

class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
"""
with open(users_views_path, 'a', encoding='utf-8') as f:
    f.write(users_views_append)
print(f"Appended UserMeView to {users_views_path}")

# 2. Update apps/users/urls.py (Add 'me/' path)
users_urls_path = r'D:\spb-expert11\apps\users\urls.py'
# We need to import UserMeView first
# Reading content to handle imports and path list properly
with open(users_urls_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import
if "from .views import" in content:
    content = content.replace("from .views import", "from .views import UserMeView,")
else:
    content = "from .views import UserMeView\n" + content

# Add path
if "path('me/', UserMeView.as_view()" not in content:
    content = content.replace(
        "urlpatterns = [",
        "urlpatterns = [\n    path('me/', UserMeView.as_view(), name='user-me'),"
    )

with open(users_urls_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Updated {users_urls_path}")


# 3. Update apps/store/views.py (Add MerchantOrderViewSet)
store_views_path = r'D:\spb-expert11\apps\store\views.py'
store_views_append = """
class MerchantOrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        # Only return orders where the current user is the merchant
        try:
            merchant = self.request.user.merchant_profile
            return Order.objects.filter(merchant=merchant)
        except MerchantProfile.DoesNotExist:
            return Order.objects.none()
            
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        order = self.get_object()
        if order.status != 'paid':
             return Response({'error': 'Order is not paid yet'}, status=400)
        
        order.status = 'shipped'
        order.save()
        return Response({'status': 'shipped'})
"""
with open(store_views_path, 'a', encoding='utf-8') as f:
    f.write(store_views_append)
print(f"Appended MerchantOrderViewSet to {store_views_path}")


# 4. Update apps/store/urls.py
store_urls_path = r'D:\spb-expert11\apps\store\urls.py'
with open(store_urls_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "MerchantOrderViewSet" not in content:
    # Add import (simplified, assuming wildcard or specific import exists, but let's be safe)
    content = content.replace("from .views import", "from .views import MerchantOrderViewSet,")
    
    # Add router register
    content = content.replace(
        "router.register(r'orders', OrderViewSet, basename='order')",
        "router.register(r'orders', OrderViewSet, basename='order')\nrouter.register(r'merchant/orders', MerchantOrderViewSet, basename='merchant-order')"
    )

with open(store_urls_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Updated {store_urls_path}")
