
import os

file_path = r'd:\spb-expert11\apps\store\serializers.py'

# I need to read the file first to find where to insert or replace.
# Since the file is large, I'll use a robust replacement for OrderSerializer.

new_class_def = """class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    merchant_name = serializers.CharField(source='merchant.company_name', read_only=True)
    merchant_user_id = serializers.IntegerField(source='merchant.user.id', read_only=True)
    shipment = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'merchant', 'order_no', 'status', 'total_amount', 'original_amount', 'coupon_discount']

    def get_shipment(self, obj):
        if hasattr(obj, 'shipment'):
            from apps.logistics.serializers import ShipmentSerializer
            return ShipmentSerializer(obj.shipment).data
        return None"""

old_class_def_start = "class OrderSerializer(serializers.ModelSerializer):"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_class = False
replaced = False

for line in lines:
    if line.strip().startswith("class OrderSerializer(serializers.ModelSerializer):"):
        in_class = True
        new_lines.append(new_class_def + "\n")
        replaced = True
        continue
    
    if in_class:
        # Check if we are still inside the class (indentation)
        # Assuming 4 spaces indentation for class content
        if line.startswith("    ") or line.strip() == "":
            continue
        else:
            in_class = False
            new_lines.append(line)
    else:
        new_lines.append(line)

if replaced:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Successfully updated OrderSerializer in store/serializers.py")
else:
    print("Could not find OrderSerializer to replace")
