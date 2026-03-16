
path = r"d:\spb-expert11\apps\procurement\serializers.py"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_ro = "read_only_fields = ['supplier', 'status']"
new_ro = "read_only_fields = ['supplier', 'status', 'procurement']"

if old_ro in content:
    content = content.replace(old_ro, new_ro)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed QuotationSerializer read_only_fields")
else:
    print("Could not find pattern to fix")
