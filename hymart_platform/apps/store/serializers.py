from rest_framework import serializers
from .models import Category, Product, ProductImage
from django.contrib.auth import get_user_model

User = get_user_model()

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'company_name', 'avatar']

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'description', 'image', 'is_active', 'order', 'children']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order']

class ProductSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'category', 'category_id', 'title', 'slug', 'description', 
            'price', 'stock', 'condition', 'condition_display', 'image', 'images', 
            'is_active', 'view_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['seller', 'slug', 'view_count', 'created_at', 'updated_at']
