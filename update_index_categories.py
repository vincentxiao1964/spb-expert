
path = r"d:\spb-expert11\frontend\pages\index\index.vue"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add click handler to category-item
if '@click="onCategoryClick(item)"' not in content:
    content = content.replace('class="category-item" v-for=', '@click="onCategoryClick(item)" class="category-item" v-for=')

# 2. Add onCategoryClick method and update loadData
# We'll replace the methods block
if 'methods: {' in content:
    # We find the existing loadData and replace/augment it, but it's risky to regex replace a whole block.
    # Let's insert onCategoryClick before loadData
    new_method = """            onCategoryClick(item) {
                if (item.name === 'Procurement' || item.name === 'Buyer Shop') {
                    uni.navigateTo({ url: '/pages/procurement/list' });
                } else if (item.name === 'Logistics') {
                    uni.showToast({ title: 'Logistics coming soon', icon: 'none' });
                } else {
                    // Default behavior (e.g. search or category page)
                    uni.navigateTo({ url: `/pages/category/category?id=${item.id}` });
                }
            },
"""
    if 'onCategoryClick' not in content:
        content = content.replace('methods: {', 'methods: {\n' + new_method)

    # 3. Update loadData to inject Procurement category
    # We look for "this.categories = res.categories || ..."
    # We will modify the fallback and the assignment
    old_assign = "this.categories = res.categories || [{name:'Ships'}, {name:'Parts'}, {name:'Crew'}, {name:'Fuel'}];"
    new_assign = "this.categories = res.categories || [{name:'Ships'}, {name:'Parts'}, {name:'Procurement', icon:'/static/procurement.png'}, {name:'Logistics', icon:'/static/logistics.png'}, {name:'Crew'}];"
    
    # Also if res.categories IS returned, we might want to append it. But for now let's just rely on fallback or explicit injection if API returns empty.
    # Actually, let's just force inject it for this demo if it's missing.
    injection_code = """
                    if (!this.categories.find(c => c.name === 'Procurement')) {
                        this.categories.splice(2, 0, { name: 'Procurement', icon: '' });
                    }
"""
    # But replacing the line is safer for the fallback scenario
    if old_assign in content:
        content = content.replace(old_assign, new_assign)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.vue with Procurement navigation")
