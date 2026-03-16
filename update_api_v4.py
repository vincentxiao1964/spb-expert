import os

# 1. Update apps/users/serializers.py
users_serializers_path = r'D:\spb-expert11\apps\users\serializers.py'
with open(users_serializers_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "AddressSerializer" not in content:
    content += """
from .models import Address
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
"""
    with open(users_serializers_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {users_serializers_path}")

# 2. Update apps/users/views.py
users_views_path = r'D:\spb-expert11\apps\users\views.py'
with open(users_views_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "AddressViewSet" not in content:
    # Add imports
    if "from rest_framework import viewsets" not in content:
        content = "from rest_framework import viewsets\n" + content
    
    # Add ViewSet
    content += """
from .models import Address
from .serializers import AddressSerializer

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
"""
    with open(users_views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {users_views_path}")

# 3. Update apps/store/serializers.py
store_serializers_path = r'D:\spb-expert11\apps\store\serializers.py'
with open(store_serializers_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "CartSerializer" not in content:
    content += """
from .models import Cart, CartItem, Order, OrderItem

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'items', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'price', 'quantity', 'product_image']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    merchant_name = serializers.CharField(source='merchant.company_name', read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'merchant', 'order_no', 'status', 'total_amount']

class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
"""
    with open(store_serializers_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {store_serializers_path}")

# 4. Update apps/store/views.py
store_views_path = r'D:\spb-expert11\apps\store\views.py'
with open(store_views_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "CartViewSet" not in content:
    # Imports
    imports = """
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer, CreateOrderSerializer
from apps.users.models import Address
import uuid
from django.db import transaction
"""
    content = imports + content
    
    content += """
class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=400)
        
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
            item.save()
        else:
            item.quantity = quantity
            item.save()
            
        return Response({'status': 'added', 'cart_item_id': item.id})

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity'))
        
        if quantity <= 0:
             CartItem.objects.filter(id=item_id, cart__user=request.user).delete()
        else:
             CartItem.objects.filter(id=item_id, cart__user=request.user).update(quantity=quantity)
             
        return Response({'status': 'updated'})
        
    @action(detail=False, methods=['post'])
    def remove(self, request):
        item_id = request.data.get('item_id')
        CartItem.objects.filter(id=item_id, cart__user=request.user).delete()
        return Response({'status': 'removed'})

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request):
        # Checkout logic
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address_id = serializer.validated_data['address_id']
        
        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({'error': 'Address not found'}, status=400)
            
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product', 'product__merchant').all()
        
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=400)
            
        # Group by merchant
        orders_by_merchant = {}
        
        for item in cart_items:
            merchant = item.product.merchant
            if merchant not in orders_by_merchant:
                orders_by_merchant[merchant] = []
            orders_by_merchant[merchant].append(item)
            
        created_orders = []
        
        for merchant, items in orders_by_merchant.items():
            total_amount = sum(item.product.price * item.quantity for item in items)
            order_no = str(uuid.uuid4().hex[:16].upper())
            
            order = Order.objects.create(
                order_no=order_no,
                user=request.user,
                merchant=merchant,
                recipient_name=address.recipient_name,
                phone=address.phone,
                address=f"{address.province} {address.city} {address.district} {address.detail_address}",
                total_amount=total_amount
            )
            
            for item in items:
                # Get main image
                main_img = item.product.images.filter(is_main=True).first()
                img_url = main_img.image.url if main_img else ""
                
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                    product_image=img_url
                )
            
            created_orders.append(order)
            
        # Clear cart
        cart.items.all().delete()
        
        return Response(OrderSerializer(created_orders, many=True).data, status=201)
"""
    with open(store_views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {store_views_path}")
