
import os

# 1. apps/logistics/serializers.py
serializers_content = """from rest_framework import serializers
from .models import Shipment, LogisticsProvider
from apps.store.serializers import OrderSerializer

class LogisticsProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogisticsProvider
        fields = ['id', 'name', 'contact_person', 'phone']

class ShipmentSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    # Simple order summary
    order_amount = serializers.DecimalField(source='order.total_amount', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Shipment
        fields = ['id', 'order', 'order_no', 'order_amount', 'provider', 'provider_name', 
                  'tracking_number', 'status', 'customs_status', 'estimated_delivery', 
                  'created_at', 'updated_at']
        read_only_fields = ['status', 'customs_status', 'updated_at']
"""

with open(r"d:\spb-expert11\apps\logistics\serializers.py", "w", encoding="utf-8") as f:
    f.write(serializers_content)

# 2. apps/logistics/views.py
views_content = """from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Shipment, LogisticsProvider
from .serializers import ShipmentSerializer, LogisticsProviderSerializer

class ShipmentViewSet(viewsets.ReadOnlyModelViewSet):
    # For now, users can only view their shipments. 
    # Creation usually happens via Merchant or Admin when fulfilling order.
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Users see shipments for their orders
        # Merchants see shipments for orders of their products (a bit complex if order is split, 
        # but current Order model is per-merchant-ish? Let's assume Order is linked to User)
        # If Order has merchant field, we could filter. 
        # Checking Order model... assuming Order has 'user' field.
        return Shipment.objects.filter(order__user=user).order_by('-created_at')

    @action(detail=True, methods=['get'])
    def track(self, request, pk=None):
        shipment = self.get_object()
        # Mock tracking timeline
        timeline = [
            {'status': 'Created', 'time': shipment.created_at, 'location': 'System'},
        ]
        if shipment.status != 'pending':
            timeline.append({'status': 'Picked Up', 'time': shipment.updated_at, 'location': 'Warehouse'})
        
        if shipment.tracking_number:
            timeline.append({'status': 'In Transit', 'time': shipment.updated_at, 'location': 'En Route'})
            
        return Response({
            'shipment': ShipmentSerializer(shipment).data,
            'timeline': timeline
        })

class LogisticsProviderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogisticsProvider.objects.filter(is_active=True)
    serializer_class = LogisticsProviderSerializer
    permission_classes = [permissions.AllowAny]
"""

with open(r"d:\spb-expert11\apps\logistics\views.py", "w", encoding="utf-8") as f:
    f.write(views_content)

# 3. apps/logistics/urls.py
urls_content = """from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShipmentViewSet, LogisticsProviderViewSet

router = DefaultRouter()
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'providers', LogisticsProviderViewSet, basename='provider')

urlpatterns = [
    path('', include(router.urls)),
]
"""

with open(r"d:\spb-expert11\apps\logistics\urls.py", "w", encoding="utf-8") as f:
    f.write(urls_content)

print("Created apps/logistics API files")
