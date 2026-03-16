from rest_framework import serializers, status
from django.contrib.contenttypes.models import ContentType
import decimal
from .models import Order, OrderItem
from apps.store.models import Product
from apps.services.models import ServiceListing
from apps.store.serializers import ProductSerializer
from apps.services.serializers import ServiceListingSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    item_type = serializers.ChoiceField(choices=['product', 'service'], write_only=True)
    item_id = serializers.IntegerField(write_only=True)
    
    # Read-only fields
    item_detail = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    is_reviewed = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'item_type', 'item_id', 'quantity', 'price', 'subtotal', 'item_detail', 'item_name', 'is_reviewed']
        read_only_fields = ['price', 'item_detail', 'subtotal', 'item_name', 'is_reviewed']

    def get_is_reviewed(self, obj):
        return hasattr(obj, 'review')

    def get_item_detail(self, obj):
        if isinstance(obj.content_object, Product):
            # Use a simplified serializer or full one
            return ProductSerializer(obj.content_object).data
        elif isinstance(obj.content_object, ServiceListing):
            return ServiceListingSerializer(obj.content_object).data
        return None

    def get_item_name(self, obj):
        return str(obj.content_object)

    def get_subtotal(self, obj):
        return obj.price * obj.quantity

    def validate(self, data):
        item_type = data.get('item_type')
        item_id = data.get('item_id')
        
        if item_type == 'product':
            try:
                product = Product.objects.get(id=item_id, is_active=True)
                if product.stock < data.get('quantity', 1):
                    raise serializers.ValidationError(f"Insufficient stock for product '{product.title}'.")
                data['content_object'] = product
                data['price'] = product.price
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {item_id} not found or inactive.")
        elif item_type == 'service':
            try:
                service = ServiceListing.objects.get(id=item_id, is_active=True)
                # For services, price is negotiable (0.00) for now
                data['content_object'] = service
                data['price'] = decimal.Decimal('0.00')
            except ServiceListing.DoesNotExist:
                raise serializers.ValidationError(f"Service with ID {item_id} not found or inactive.")
        
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'buyer', 'seller', 'status', 'status_display', 
            'total_amount', 'contact_name', 'contact_phone', 
            'shipping_address', 'note', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'buyer', 'seller', 'status', 'status_display', 'total_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        buyer = self.context['request'].user
        
        # Calculate total amount
        total_amount = 0
        order_items_payload = []
        
        # Determine seller from first item (Assuming all items in one order belong to one seller)
        # In a real multi-vendor system, this logic should split orders.
        seller = None
        
        for item_data in items_data:
            content_object = item_data['content_object']
            price = item_data['price']
            quantity = item_data['quantity']
            
            # Determine seller
            item_seller = None
            if hasattr(content_object, 'seller'):
                item_seller = content_object.seller
            elif hasattr(content_object, 'provider'): # For ServiceListing
                item_seller = content_object.provider
            
            if seller is None:
                seller = item_seller
            elif seller != item_seller:
                 # If mixed sellers, we default to the first one or raise error. 
                 # Ideally, we should split orders, but for now we raise error to keep data integrity.
                 raise serializers.ValidationError("All items in an order must belong to the same seller/provider.")

            total_amount += price * quantity
            
            order_items_payload.append({
                'content_object': content_object,
                'price': price,
                'quantity': quantity
            })
        
        # Create Order
        order = Order.objects.create(
            buyer=buyer, 
            seller=seller,
            total_amount=total_amount, 
            **validated_data
        )
        
        # Create OrderItems
        for payload in order_items_payload:
            content_object = payload['content_object']
            OrderItem.objects.create(
                order=order,
                content_type=ContentType.objects.get_for_model(content_object),
                object_id=content_object.id,
                quantity=payload['quantity'],
                price=payload['price']
            )
            
            # Update stock for products
            if isinstance(content_object, Product):
                content_object.stock -= payload['quantity']
                content_object.save()
                
        return order
