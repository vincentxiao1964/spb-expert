import os

SERIALIZERS_PATH = r"D:\spb-expert11\apps\store\serializers.py"
VIEWS_PATH = r"D:\spb-expert11\apps\store\views.py"

def update_serializers():
    try:
        with open(SERIALIZERS_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            
        old_code = '''class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    coupon_id = serializers.IntegerField(required=False)'''
    
        new_code = '''class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    coupon_id = serializers.IntegerField(required=False)
    items = serializers.ListField(child=serializers.IntegerField(), required=False)'''
    
        if old_code in content:
            new_content = content.replace(old_code, new_code)
            with open(SERIALIZERS_PATH, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Updated serializers.py")
        else:
            print("Could not find CreateOrderSerializer in serializers.py")
            
    except Exception as e:
        print(f"Error updating serializers.py: {e}")

def update_views():
    try:
        with open(VIEWS_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Update fetching cart items
        old_fetch = "cart_items = cart.items.select_related('product', 'product__merchant').all()"
        new_fetch = """item_ids = serializer.validated_data.get('items', [])
        
        if item_ids:
            cart_items = cart.items.select_related('product', 'product__merchant').filter(id__in=item_ids)
        else:
            cart_items = cart.items.select_related('product', 'product__merchant').all()"""
            
        if old_fetch in content:
            content = content.replace(old_fetch, new_fetch)
        else:
            print("Could not find cart item fetching logic in views.py")
            
        # 2. Update cleanup logic (cart.items.all().delete())
        # We need to be careful not to replace other deletes if any
        # The specific line is usually at the end of the method
        old_delete = "cart.items.all().delete()"
        new_delete = "cart_items.delete()"
        
        # There might be multiple occurrences? No, CartViewSet has one but this is OrderViewSet
        # In OrderViewSet.create, it's inside transaction.atomic
        
        if old_delete in content:
            # We only want to replace the one in OrderViewSet.create
            # But simple replace might be risky if CartViewSet uses it too.
            # Let's check context.
            # CartViewSet uses: CartItem.objects.filter(...).delete() or item.delete()
            # It doesn't use cart.items.all().delete() typically, unless for clearing cart?
            # CartViewSet doesn't seem to have clear cart method in what I read.
            # So it should be safe to replace.
            content = content.replace(old_delete, new_delete)
        else:
            print("Could not find cart cleanup logic in views.py")
            
        with open(VIEWS_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated views.py")
            
    except Exception as e:
        print(f"Error updating views.py: {e}")

if __name__ == "__main__":
    update_serializers()
    update_views()
