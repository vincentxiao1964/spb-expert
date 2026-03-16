from rest_framework import serializers
from .models import Category, Product, Cart, CartItem
from services.models import ServiceListing
from reviews.models import Review
from orders.models import OrderItem

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'description', 'is_active', 'order', 'children']

    def get_children(self, obj):
        qs = obj.children.filter(is_active=True).order_by('order', 'id')
        return CategorySerializer(qs, many=True).data

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    rating_avg = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    reviews_preview = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'category', 'category_id', 'title', 'slug', 'description', 'price', 'stock', 'is_active', 'is_approved', 'approved_at', 'approved_by', 'approval_note', 'owner', 'rating_avg', 'rating_count', 'reviews_preview', 'created_at', 'updated_at']
        read_only_fields = ['approved_at', 'approved_by']

    def get_rating_avg(self, obj):
        item_ids = OrderItem.objects.filter(product=obj).values_list('id', flat=True)
        qs = Review.objects.filter(order_item_id__in=list(item_ids))
        count = qs.count()
        if count == 0:
            return 0
        total = sum(r.rating for r in qs)
        return round(total / count, 2)

    def get_rating_count(self, obj):
        item_ids = OrderItem.objects.filter(product=obj).values_list('id', flat=True)
        return Review.objects.filter(order_item_id__in=list(item_ids)).count()

    def get_reviews_preview(self, obj):
        item_ids = OrderItem.objects.filter(product=obj).values_list('id', flat=True)
        qs = Review.objects.filter(order_item_id__in=list(item_ids), is_public=True).order_by('-created_at')[:3]
        data = []
        for r in qs:
            images = [img.image.url for img in getattr(r, 'images').all()]
            data.append({
                'id': r.id,
                'rating': r.rating,
                'comment': r.comment,
                'reviewer_name': r.reviewer.username,
                'created_at': r.created_at,
                'images': images,
            })
        return data

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', required=False, allow_null=True, write_only=True)
    service_id = serializers.PrimaryKeyRelatedField(queryset=ServiceListing.objects.all(), source='service', required=False, allow_null=True, write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'service', 'product_id', 'service_id', 'quantity']

    def validate(self, data):
        if not data.get('product') and not data.get('service'):
            raise serializers.ValidationError('product_id or service_id required')
        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
