from rest_framework import serializers
from .models import Review, ReviewImage
from apps.orders.models import OrderItem, Order

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, read_only=True)
    order_item_id = serializers.PrimaryKeyRelatedField(
        queryset=OrderItem.objects.all(), source='order_item', write_only=True
    )
    
    # Read-only details
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    reviewer_avatar = serializers.ImageField(source='reviewer.avatar', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'order_item', 'order_item_id', 'reviewer', 'reviewer_name', 'reviewer_avatar',
            'rating', 'comment', 'reply', 'replied_at', 'images', 'created_at'
        ]
        read_only_fields = ['id', 'reviewer', 'order_item', 'reply', 'replied_at', 'created_at']

    def validate(self, data):
        request = self.context['request']
        order_item = data.get('order_item')
        
        # 1. Verify Ownership
        if order_item.order.buyer != request.user:
            raise serializers.ValidationError("You can only review items you purchased.")
            
        # 2. Verify Order Status
        if order_item.order.status != Order.Status.COMPLETED:
            raise serializers.ValidationError("You can only review items from completed orders.")
            
        # 3. Verify Duplicate Review
        if hasattr(order_item, 'review'):
            raise serializers.ValidationError("You have already reviewed this item.")
            
        return data

    def create(self, validated_data):
        # reviewer is passed via perform_create -> save(reviewer=user)
        # so it's already in validated_data
        review = Review.objects.create(**validated_data)
        return review

class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['reply']
        
    def update(self, instance, validated_data):
        from django.utils import timezone
        instance.reply = validated_data.get('reply', instance.reply)
        instance.replied_at = timezone.now()
        instance.save()
        return instance
