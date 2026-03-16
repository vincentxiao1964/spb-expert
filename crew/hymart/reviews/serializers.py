from rest_framework import serializers
from .models import Review, ReviewImage, ReviewLike, ReviewReport
from orders.models import OrderItem

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'created_at']

class ReviewListSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    image_urls = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    is_pinned = serializers.BooleanField(read_only=True)
    hidden_by_owner = serializers.BooleanField(read_only=True)
    flagged_sensitive = serializers.BooleanField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewer_name', 'rating', 'comment', 'reply', 'is_public', 'is_pinned', 'hidden_by_owner', 'flagged_sensitive', 'is_deleted', 'status', 'image_urls', 'like_count', 'created_at', 'updated_at']
        read_only_fields = ['reviewer', 'reply', 'created_at', 'updated_at']

    def get_like_count(self, obj):
        request = self.context.get('request') if self.context else None
        if request and request.query_params.get('include_likes') == '1':
            return obj.likes.count()
        return None
    def get_reply(self, obj):
        request = self.context.get('request') if self.context else None
        if request and request.query_params.get('include_reply') == '1':
            return obj.reply
        return None

    def get_status(self, obj):
        if getattr(obj, 'is_deleted', False):
            return 'deleted'
        if not getattr(obj, 'is_public', True):
            return 'unpublished'
        if getattr(obj, 'hidden_by_owner', False):
            return 'hidden'
        if getattr(obj, 'flagged_sensitive', False):
            return 'sensitive'
        return 'normal'

    def get_image_urls(self, obj):
        request = self.context.get('request') if self.context else None
        if not request or request.query_params.get('include_images') != '1':
            return []
        return [request.build_absolute_uri(img.image.url) for img in obj.images.all()]

class ReviewSerializer(serializers.ModelSerializer):
    order_item_id = serializers.PrimaryKeyRelatedField(queryset=OrderItem.objects.all(), source='order_item', write_only=True)
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    image_urls = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    report_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_pinned = serializers.BooleanField(read_only=True)
    hidden_by_owner = serializers.BooleanField(read_only=True)
    flagged_sensitive = serializers.BooleanField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'order_item', 'order_item_id', 'reviewer', 'reviewer_name', 'rating', 'comment', 'reply', 'is_public', 'is_pinned', 'hidden_by_owner', 'flagged_sensitive', 'is_deleted', 'status', 'images', 'image_urls', 'like_count', 'report_count', 'is_liked', 'created_at', 'updated_at']
        read_only_fields = ['order_item', 'reviewer', 'reply', 'created_at', 'updated_at']

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_report_count(self, obj):
        return obj.reports.count()

    def get_is_liked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return False
        return ReviewLike.objects.filter(review=obj, user=user).exists()

    def get_image_urls(self, obj):
        request = self.context.get('request') if self.context else None
        if not request:
            return []
        include = request.query_params.get('include_images') == '1' or request.query_params.get('include_abs') == '1'
        if not include:
            return []
        return [request.build_absolute_uri(img.image.url) for img in obj.images.all()]

    def get_status(self, obj):
        if getattr(obj, 'is_deleted', False):
            return 'deleted'
        if not getattr(obj, 'is_public', True):
            return 'unpublished'
        if getattr(obj, 'hidden_by_owner', False):
            return 'hidden'
        if getattr(obj, 'flagged_sensitive', False):
            return 'sensitive'
        return 'normal'
