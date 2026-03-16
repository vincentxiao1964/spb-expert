from rest_framework import serializers
from .models import PaymentIntent
from orders.models import Order

class PaymentIntentSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), source='order', write_only=True)

    class Meta:
        model = PaymentIntent
        fields = ['id', 'order', 'order_id', 'amount', 'provider', 'reference', 'status', 'created_at', 'updated_at']
        read_only_fields = ['status', 'created_at', 'updated_at']

    def create(self, validated_data):
        intent = super().create(validated_data)
        return intent
