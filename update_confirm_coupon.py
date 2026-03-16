import os

# Update order/confirm.vue to include coupon_id in submitOrder
confirm_path = r'D:\spb-expert11\frontend\pages\order\confirm.vue'
with open(confirm_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update submitOrder
old_submit = """data: {
                            address_id: this.selectedAddress.id
                        }"""
                        
new_submit = """data: {
                            address_id: this.selectedAddress.id,
                            coupon_id: this.selectedCoupon ? this.selectedCoupon.id : null
                        }"""

if old_submit in content:
    content = content.replace(old_submit, new_submit)
    
# Add CSS for Coupon Selector
if ".coupon-selector" not in content:
    css = """
    .coupon-selector { background: #fff; padding: 30rpx; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
    .coupon-selector .placeholder { color: #ff5500; font-weight: bold; }
    .coupon-selector .right { display: flex; align-items: center; color: #666; }
"""
    content = content.replace("</style>", css + "\n</style>")
    
with open(confirm_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated order/confirm.vue (Part 2)")
