from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Inquiry, InquiryMessage
from apps.store.models import Product
from apps.services.models import ServiceListing
from apps.store.serializers import ProductSerializer
from apps.services.serializers import ServiceListingSerializer

class InquiryMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.SerializerMethodField()

    class Meta:
        model = InquiryMessage
        fields = [
            'id', 'inquiry', 'sender', 'sender_name', 'sender_avatar',
            'message', 'is_quote', 'price', 'currency', 'valid_until', 
            'attachment', 'created_at'
        ]
        read_only_fields = ['id', 'inquiry', 'sender', 'created_at']

    def get_sender_avatar(self, obj):
        # Placeholder, implement if User profile has avatar
        return None

class InquirySerializer(serializers.ModelSerializer):
    # Write fields
    item_type = serializers.ChoiceField(choices=['product', 'service'], write_only=True)
    item_id = serializers.IntegerField(write_only=True)
    initial_message = serializers.CharField(write_only=True)
    
    # Read fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    product = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = Inquiry
        fields = [
            'id', 'buyer', 'buyer_name', 'seller', 'seller_name',
            'status', 'status_display', 'subject', 
            'item_type', 'item_id', 'initial_message',
            'product', 'service', 'item_name', 'last_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'buyer', 'seller', 'status', 'subject', 
            'product', 'service', 'item_name', 'created_at', 'updated_at'
        ]

    def get_product(self, obj):
        if isinstance(obj.content_object, Product):
            return ProductSerializer(obj.content_object).data
        return None

    def get_service(self, obj):
        if isinstance(obj.content_object, ServiceListing):
            return ServiceListingSerializer(obj.content_object).data
        return None

    def get_item_name(self, obj):
        return str(obj.content_object)

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return InquiryMessageSerializer(last_msg).data
        return None

    def create(self, validated_data):
        item_type = validated_data.pop('item_type')
        item_id = validated_data.pop('item_id')
        initial_message = validated_data.pop('initial_message')
        buyer = self.context['request'].user
        
        # Determine content object and seller
        content_object = None
        seller = None
        
        if item_type == 'product':
            try:
                content_object = Product.objects.get(id=item_id)
                seller = content_object.seller
            except Product.DoesNotExist:
                raise serializers.ValidationError("Product not found")
        elif item_type == 'service':
            try:
                content_object = ServiceListing.objects.get(id=item_id)
                seller = content_object.provider
            except ServiceListing.DoesNotExist:
                raise serializers.ValidationError("Service not found")
        
        if buyer == seller:
            raise serializers.ValidationError("You cannot inquire about your own item.")

        # Create Inquiry
        inquiry = Inquiry.objects.create(
            buyer=buyer,
            seller=seller,
            content_object=content_object,
            subject=f"Inquiry about {content_object}",
            status=Inquiry.Status.PENDING
        )
        
        # Create Initial Message
        InquiryMessage.objects.create(
            inquiry=inquiry,
            sender=buyer,
            message=initial_message
        )
        
        return inquiry

class InquiryDetailSerializer(InquirySerializer):
    messages = InquiryMessageSerializer(many=True, read_only=True)
    
    class Meta(InquirySerializer.Meta):
        fields = InquirySerializer.Meta.fields + ['messages']
