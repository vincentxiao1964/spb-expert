
import os

# 1. apps/procurement/serializers.py
serializers_content = """from rest_framework import serializers
from .models import ProcurementRequest, Quotation
from apps.users.serializers import UserSerializer

class QuotationSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.username', read_only=True)
    supplier_avatar = serializers.CharField(source='supplier.avatar', read_only=True)
    
    class Meta:
        model = Quotation
        fields = ['id', 'procurement', 'supplier', 'supplier_name', 'supplier_avatar', 
                  'price', 'message', 'is_sample_provided', 'status', 'created_at']
        read_only_fields = ['supplier', 'status']

class ProcurementRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.CharField(source='user.avatar', read_only=True)
    quotation_count = serializers.IntegerField(source='quotations.count', read_only=True)
    my_quotation = serializers.SerializerMethodField()

    class Meta:
        model = ProcurementRequest
        fields = ['id', 'user', 'user_name', 'user_avatar', 'title', 'description', 
                  'budget', 'deadline', 'is_sample_required', 'status', 
                  'created_at', 'quotation_count', 'my_quotation']
        read_only_fields = ['user', 'status']

    def get_my_quotation(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if current user has quoted
            quotation = obj.quotations.filter(supplier=request.user).first()
            if quotation:
                return QuotationSerializer(quotation).data
        return None

class ProcurementRequestDetailSerializer(ProcurementRequestSerializer):
    quotations = QuotationSerializer(many=True, read_only=True)
    
    class Meta(ProcurementRequestSerializer.Meta):
        fields = ProcurementRequestSerializer.Meta.fields + ['quotations']
"""

with open(r"d:\spb-expert11\apps\procurement\serializers.py", "w", encoding="utf-8") as f:
    f.write(serializers_content)


# 2. apps/procurement/views.py
views_content = """from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ProcurementRequest, Quotation
from .serializers import ProcurementRequestSerializer, ProcurementRequestDetailSerializer, QuotationSerializer

class ProcurementRequestViewSet(viewsets.ModelViewSet):
    queryset = ProcurementRequest.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProcurementRequestDetailSerializer
        return ProcurementRequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        mode = self.request.query_params.get('mode')
        if mode == 'mine' and self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user)
        elif mode == 'open':
            return queryset.filter(status='open')
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def quote(self, request, pk=None):
        procurement = self.get_object()
        
        # Self-quoting check
        if procurement.user == request.user:
            return Response({"detail": "Cannot quote your own request"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Existing quote check
        if procurement.quotations.filter(supplier=request.user).exists():
            return Response({"detail": "You have already quoted"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuotationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(procurement=procurement, supplier=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users see quotes they sent OR quotes on their requests
        user = self.request.user
        return Quotation.objects.filter(
            Q(supplier=user) | Q(procurement__user=user)
        )
"""

with open(r"d:\spb-expert11\apps\procurement\views.py", "w", encoding="utf-8") as f:
    f.write(views_content)


# 3. apps/procurement/urls.py
urls_content = """from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProcurementRequestViewSet, QuotationViewSet

router = DefaultRouter()
router.register(r'requests', ProcurementRequestViewSet, basename='procurement-request')
router.register(r'quotations', QuotationViewSet, basename='quotation')

urlpatterns = [
    path('', include(router.urls)),
]
"""

with open(r"d:\spb-expert11\apps\procurement\urls.py", "w", encoding="utf-8") as f:
    f.write(urls_content)

print("Created apps/procurement API files")
