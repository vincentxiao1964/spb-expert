
import os

VIEWS_PATH = r"D:\spb-expert11\apps\store\views.py"

PAY_METHOD = """
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
             return Response({'error': 'Order is not pending'}, status=400)
        
        # Simulate payment
        order.status = 'paid'
        order.save()
        return Response({'status': 'paid'})
"""

with open(VIEWS_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Check if pay method already exists to avoid duplication
if "def pay(self, request, pk=None):" in content:
    print("Pay method already exists.")
else:
    # Find the insertion point: before MerchantOrderViewSet
    target = "class MerchantOrderViewSet"
    if target in content:
        new_content = content.replace(target, PAY_METHOD + "\n" + target)
        with open(VIEWS_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully added pay action.")
    else:
        print("Could not find insertion point (MerchantOrderViewSet).")
