
import os

serializers_path = r"d:\spb-expert11\apps\procurement\serializers.py"

old_code = """    class Meta:
        model = Quotation
        fields = ['id', 'procurement', 'supplier', 'supplier_name', 'supplier_avatar', 
                  'price', 'message', 'is_sample_provided', 'status', 'created_at']
        read_only_fields = ['supplier', 'status', 'procurement']"""

new_code = """    class Meta:
        model = Quotation
        fields = ['id', 'procurement', 'supplier', 'supplier_name', 'supplier_avatar', 
                  'price', 'message', 'is_sample_provided', 'status', 'created_at']
        read_only_fields = ['supplier', 'procurement']"""

try:
    with open(serializers_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if old_code in content:
        new_content = content.replace(old_code, new_code)
        with open(serializers_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {serializers_path}")
    else:
        print("Could not find old code block to replace")

except Exception as e:
    print(f"Error updating serializers.py: {e}")
