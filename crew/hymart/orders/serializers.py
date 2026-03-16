from rest_framework import serializers
from .models import Order, OrderItem, OrderRefund, Shipment
from store.models import Product
from services.models import ServiceListing

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True, required=False, allow_null=True)
    service_id = serializers.PrimaryKeyRelatedField(queryset=ServiceListing.objects.all(), source='service', write_only=True, required=False, allow_null=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'service', 'product_id', 'service_id', 'title', 'price', 'quantity']

    def validate(self, data):
        if not data.get('product') and not data.get('service'):
            raise serializers.ValidationError('product_id or service_id required')
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    coupon_id = serializers.IntegerField(source='coupon.id', read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True, allow_null=True)
    coupon_discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    original_total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'buyer_name', 'contact_phone', 'status', 'status_display', 'total_amount', 'original_total_amount', 'coupon_id', 'coupon_code', 'coupon_discount_amount', 'items', 'created_at', 'updated_at']
        read_only_fields = ['total_amount', 'original_total_amount', 'coupon_id', 'coupon_code', 'coupon_discount_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = super().create(validated_data)
        total = 0
        for item in items_data:
            qty = item.get('quantity', 1)
            price = item['price']
            total += price * qty
            OrderItem.objects.create(order=order, **item)
        order.total_amount = total
        order.save()
        return order

    def get_original_total_amount(self, obj):
        return obj.total_amount + obj.coupon_discount_amount

class OrderRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRefund
        fields = ['id', 'order', 'amount', 'reason', 'status', 'created_at', 'updated_at']
        read_only_fields = ['status', 'created_at', 'updated_at']

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['id', 'order', 'receiver_name', 'receiver_phone', 'address_line', 'city', 'state', 'country', 'postal_code', 'carrier', 'tracking_number', 'status', 'shipped_at', 'delivered_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
