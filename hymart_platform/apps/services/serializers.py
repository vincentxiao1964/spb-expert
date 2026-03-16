from rest_framework import serializers
from .models import ServiceCategory, ServiceListing
from django.contrib.auth import get_user_model

User = get_user_model()

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'company_name', 'avatar']

class ServiceCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'slug', 'parent', 'description', 'icon', 'is_active', 'order', 'children']

    def get_children(self, obj):
        if obj.children.exists():
            return ServiceCategorySerializer(obj.children.all(), many=True).data
        return []

class ServiceListingSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer(read_only=True)
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(), source='category', write_only=True
    )
    
    class Meta:
        model = ServiceListing
        fields = [
            'id', 'provider', 'category', 'category_id', 'title', 'description',
            'service_area', 'price_range', 'is_active', 'view_count', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['provider', 'view_count', 'created_at', 'updated_at']
