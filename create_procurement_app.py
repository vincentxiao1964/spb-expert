
import os

base_dir = r"d:\spb-expert11\apps\procurement"
os.makedirs(base_dir, exist_ok=True)

# __init__.py
with open(os.path.join(base_dir, "__init__.py"), "w") as f:
    f.write("")

# apps.py
with open(os.path.join(base_dir, "apps.py"), "w") as f:
    f.write("""from django.apps import AppConfig

class ProcurementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.procurement'
""")

# models.py
with open(os.path.join(base_dir, "models.py"), "w") as f:
    f.write("""from django.db import models
from django.contrib.auth import get_user_model
from apps.users.models import MerchantProfile

User = get_user_model()

class ProcurementRequest(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='procurement_requests')
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Detailed requirements")
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    
    is_sample_required = models.BooleanField(default=False, help_text="Require sample before bulk order")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Quotation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sample_sent', 'Sample Sent'),
        ('sample_approved', 'Sample Approved'),
        ('sample_rejected', 'Sample Rejected'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    procurement = models.ForeignKey(ProcurementRequest, on_delete=models.CASCADE, related_name='quotations')
    supplier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotations_sent') # Supplier is a User (who might have a MerchantProfile)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    
    is_sample_provided = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.supplier.username} - {self.procurement.title}"
""")

# admin.py
with open(os.path.join(base_dir, "admin.py"), "w") as f:
    f.write("""from django.contrib import admin
from .models import ProcurementRequest, Quotation

admin.site.register(ProcurementRequest)
admin.site.register(Quotation)
""")

# views.py
with open(os.path.join(base_dir, "views.py"), "w") as f:
    f.write("""from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ProcurementRequest, Quotation
from .serializers import ProcurementRequestSerializer, QuotationSerializer

class ProcurementRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ProcurementRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users see their own requests, Suppliers see all OPEN requests
        # Simplified: Everyone sees all OPEN requests for now, or filter by mode
        if self.action in ['list', 'retrieve']:
             # If filtering by 'mine', show user's requests
             if self.request.query_params.get('mode') == 'mine':
                 return ProcurementRequest.objects.filter(user=self.request.user)
             return ProcurementRequest.objects.filter(status='open')
        return ProcurementRequest.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class QuotationViewSet(viewsets.ModelViewSet):
    serializer_class = QuotationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('mode') == 'mine':
             return Quotation.objects.filter(supplier=self.request.user)
        # Also allow viewing quotations for a specific procurement if I am the owner
        procurement_id = self.request.query_params.get('procurement_id')
        if procurement_id:
             return Quotation.objects.filter(procurement_id=procurement_id, procurement__user=self.request.user)
        return Quotation.objects.filter(supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(supplier=self.request.user)
""")

# serializers.py
with open(os.path.join(base_dir, "serializers.py"), "w") as f:
    f.write("""from rest_framework import serializers
from .models import ProcurementRequest, Quotation
from apps.users.serializers import UserSerializer

class ProcurementRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ProcurementRequest
        fields = '__all__'

class QuotationSerializer(serializers.ModelSerializer):
    supplier = UserSerializer(read_only=True)
    class Meta:
        model = Quotation
        fields = '__all__'
""")

# urls.py
with open(os.path.join(base_dir, "urls.py"), "w") as f:
    f.write("""from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProcurementRequestViewSet, QuotationViewSet

router = DefaultRouter()
router.register(r'requests', ProcurementRequestViewSet, basename='procurement-request')
router.register(r'quotations', QuotationViewSet, basename='quotation')

urlpatterns = [
    path('', include(router.urls)),
]
""")

print("Created procurement app files")
