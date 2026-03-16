
import os

def update_file(file_path, replacements):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        for old, new in replacements.items():
            new_content = new_content.replace(old, new)
            
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {file_path}")
        else:
            print(f"No changes needed for {file_path}")
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

# 1. Update Product Detail
detail_path = r"d:\spb-expert11\frontend\pages\product\detail.vue"
detail_replacements = {
    "url: `/pages/chat/chat?targetId=${this.product.merchant}`": "url: `/pages/chat/chat?targetId=${this.product.merchant_user_id}`"
}
update_file(detail_path, detail_replacements)

# 2. Update Merchant Dashboard
dashboard_path = r"d:\spb-expert11\frontend\pages\merchant\dashboard.vue"
dashboard_replacements = {
    "background: linear-gradient(135deg, #2b32b2, #1488cc);": "background: linear-gradient(135deg, #FF5000, #FF8C00);",
    "uni.showToast({ title: 'Settings (Coming Soon)', icon: 'none' });": "uni.navigateTo({ url: '/pages/merchant/settings' });"
}
update_file(dashboard_path, dashboard_replacements)
