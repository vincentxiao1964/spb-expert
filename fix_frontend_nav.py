import os

file_path = r'd:\spb-expert11\frontend\pages\index\index.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add onCategoryClick method
old_methods = """            goToDetail(item) {
                uni.navigateTo({
                    url: `/pages/product/detail?id=${item.id}`
                });
            },
            async loadData() {"""

new_methods = """            goToDetail(item) {
                uni.navigateTo({
                    url: `/pages/product/detail?id=${item.id}`
                });
            },
            onCategoryClick(item) {
                console.log('Clicked category:', item.name);
                if (item.name === 'Procurement' || item.name === 'Buyer Shop') {
                    uni.navigateTo({ url: '/pages/procurement/list' });
                } else if (item.name === 'Logistics') {
                    uni.navigateTo({ url: '/pages/logistics/list' });
                } else {
                    // Default to category tab for product categories
                    uni.switchTab({ url: '/pages/category/category' });
                }
            },
            async loadData() {"""

content = content.replace(old_methods, new_methods)

# 2. Inject functional modules in loadData
old_load = """                    this.categories = res.categories || [{name:'Ships'}, {name:'Parts'}, {name:'Procurement', icon:'/static/procurement.png'}, {name:'Logistics', icon:'/static/logistics.png'}, {name:'Crew'}];"""

new_load = """                    // Mix backend categories with functional modules
                    let backendCats = res.categories || [];
                    // Add functional modules if not present
                    const functional = [
                        {name: 'Procurement', icon: '/static/procurement.png', id: 'procurement'},
                        {name: 'Logistics', icon: '/static/logistics.png', id: 'logistics'}
                    ];
                    this.categories = [...functional, ...backendCats];
                    
                    if (this.categories.length === 0) {
                         this.categories = [{name:'Ships'}, {name:'Parts'}, ...functional];
                    }"""

content = content.replace(old_load, new_load)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Updated {file_path}")
