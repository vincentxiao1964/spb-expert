from rest_framework import serializers
from .models import ServiceCategory, ServiceListing
from reviews.models import Review
from orders.models import OrderItem

class ServiceCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'slug', 'parent', 'description', 'is_active', 'order', 'children']

    def get_children(self, obj):
        qs = obj.children.filter(is_active=True).order_by('order', 'id')
        return ServiceCategorySerializer(qs, many=True).data

class ServiceListingSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all(), source='category', write_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    rating_avg = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    reviews_preview = serializers.SerializerMethodField()

    class Meta:
        model = ServiceListing
        fields = ['id', 'category', 'category_id', 'title', 'slug', 'description', 'price', 'is_active', 'is_approved', 'approved_at', 'approved_by', 'approval_note', 'owner', 'rating_avg', 'rating_count', 'reviews_preview', 'created_at', 'updated_at']
        read_only_fields = ['approved_at', 'approved_by']

    def get_rating_avg(self, obj):
        item_ids = OrderItem.objects.filter(service=obj).values_list('id', flat=True)
        qs = Review.objects.filter(order_item_id__in=list(item_ids))
        count = qs.count()
        if count == 0:
            return 0
        total = sum(r.rating for r in qs)
        return round(total / count, 2)

    def get_rating_count(self, obj):
        item_ids = OrderItem.objects.filter(service=obj).values_list('id', flat=True)
        return Review.objects.filter(order_item_id__in=list(item_ids)).count()

    def get_reviews_preview(self, obj):
        item_ids = OrderItem.objects.filter(service=obj).values_list('id', flat=True)
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
