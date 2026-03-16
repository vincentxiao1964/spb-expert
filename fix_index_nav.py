
path = r"d:\spb-expert11\frontend\pages\index\index.vue"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix methods block
if "onCategoryClick(item)" not in content:
    # If method is missing, we need to add it.
    # Find "methods: {"
    if "methods: {" in content:
        new_method = """            onCategoryClick(item) {
                if (item.name === 'Procurement' || item.name === 'Buyer Shop') {
                    uni.navigateTo({ url: '/pages/procurement/list' });
                } else if (item.name === 'Logistics') {
                    uni.navigateTo({ url: '/pages/logistics/list' });
                } else {
                    uni.navigateTo({ url: `/pages/category/category?id=${item.id}` });
                }
            },
"""
        content = content.replace("methods: {", "methods: {\n" + new_method)
else:
    # If method exists, update the Logistics logic
    # We'll use regex or simple string replacement if we know the exact string
    # But since I suspect it's missing (based on previous Read), I will rely on the first branch.
    # Wait, if it exists but I want to change 'coming soon' to navigateTo
    if "uni.showToast({ title: 'Logistics coming soon'" in content:
        content = content.replace("uni.showToast({ title: 'Logistics coming soon', icon: 'none' });", 
                                  "uni.navigateTo({ url: '/pages/logistics/list' });")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed index.vue navigation")
