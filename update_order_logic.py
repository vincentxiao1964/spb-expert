import os

# Update apps/store/views.py
views_path = r'D:\spb-expert11\apps\store\views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add transaction import
if "from django.db import transaction" not in content:
    content = "from django.db import transaction\n" + content

# 2. Add cancel action to OrderViewSet
# Find end of receive method
receive_end = """        order.status = 'completed'
        order.save()
        return Response({'status': 'completed'})"""

cancel_method = """
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        # Permission check
        is_owner = order.user == request.user
        # Check if user is the merchant of this order
        is_merchant = hasattr(request.user, 'merchant_profile') and order.merchant == request.user.merchant_profile
        
        if not (is_owner or is_merchant):
             return Response({'error': 'Permission denied'}, status=403)
             
        if order.status in ['completed', 'cancelled', 'shipped']:
             return Response({'error': 'Order cannot be cancelled in current status'}, status=400)
             
        with transaction.atomic():
            # Restore stock
            for order_item in order.items.all():
                product = order_item.product
                product.stock += order_item.quantity
                product.save()
                
            order.status = 'cancelled'
            order.save()
            
        return Response({'status': 'cancelled'})
"""

if receive_end in content and "def cancel(self" not in content:
    content = content.replace(receive_end, receive_end + cancel_method)

# 3. Update create method for stock deduction
# We'll replace the loop "for merchant, items in orders_by_merchant.items():"
# This requires careful matching.
old_loop_start = """        for merchant, items in orders_by_merchant.items():
            item_total = sum(item.product.price * item.quantity for item in items)"""

new_loop_start = """        # 1. Check stock first (Global check)
        for merchant, items in orders_by_merchant.items():
            for item in items:
                if item.product.stock < item.quantity:
                    return Response(
                        {'error': f'Insufficient stock for {item.product.name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        with transaction.atomic():
            for merchant, items in orders_by_merchant.items():
                item_total = sum(item.product.price * item.quantity for item in items)"""

if old_loop_start in content:
    content = content.replace(old_loop_start, new_loop_start)
    
# 4. Deduct stock inside the loop
# Find "OrderItem.objects.create(" block
old_order_item_create = """                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                    product_image=img_url
                )"""

new_order_item_create = """                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                    product_image=img_url
                )
                # Deduct stock
                item.product.stock -= item.quantity
                item.product.save()"""

if old_order_item_create in content:
    content = content.replace(old_order_item_create, new_order_item_create)

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated apps/store/views.py with Cancel & Stock Logic")
