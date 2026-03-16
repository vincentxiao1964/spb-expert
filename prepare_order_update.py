import os

# Update apps/store/views.py with Stock Management and Cancel Action
views_path = r'D:\spb-expert11\apps\store\views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Import transaction
if "from django.db import transaction" not in content:
    content = "from django.db import transaction\n" + content

# 2. Update create method for stock deduction
# Find the loop where items are processed
# "for merchant, items in orders_by_merchant.items():"
# We need to wrap the whole create process in atomic

if "@transaction.atomic" not in content:
    # We can't easily decorate the existing method via string replacement if we don't know the signature exactly or if it's too long.
    # But we can look for "def create(self, request):" and add the decorator or "with transaction.atomic():" inside.
    pass

# Strategy: Replace the entire 'create' method logic? It's long.
# Better: Look for "cart_items = cart.items.all()" and verify stock there.
# Then inside "for item in items:" (line 252 in previous read), deduct stock.

# Let's write a script that reads the file, parses it (or regex), and inserts the logic.
# Since I have the file content in memory (conceptually), I can try to construct the replacement.

# Logic for stock deduction:
# Inside "for item in items:" loop (creating OrderItem):
# item.product.stock -= item.quantity
# item.product.save()

# Logic for stock check (before creating order):
# Loop all items, check if item.product.stock < item.quantity. If so, raise Error.

# Let's implement 'cancel' action first, and 'stock' logic second.

# Add 'cancel' action
new_cancel = """    @action(detail=True, methods=['post'])
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

if "def cancel(self, request, pk=None):" not in content:
    # Append to OrderViewSet
    # Find the last method (receive) and append after it.
    # "def receive(self, request, pk=None):" ... "order.status = 'completed'"
    # Look for the end of receive method.
    pass

# We will read the file again to be sure where to insert.
