import os

# Update frontend/pages/user/user.vue to add "My Refunds" link
user_vue_path = r'D:\spb-expert11\frontend\pages\user\user.vue'
with open(user_vue_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add link
# After "My Orders"
my_orders = """<view class="menu-item" @click="goToOrders">
                <text>My Orders</text>
                <text class="arrow">></text>
            </view>"""
            
my_refunds = """
            <view class="menu-item" @click="goToRefunds">
                <text>My Refunds</text>
                <text class="arrow">></text>
            </view>"""
            
if my_orders in content and "goToRefunds" not in content:
    content = content.replace(my_orders, my_orders + my_refunds)
    
# Add method
method_insert = """            goToOrders() {""" # Assuming it exists, wait, the previous read didn't show goToOrders method definition explicitly but it was used in template.
# Ah, the Read showed:
# 36→<view class="menu-item" @click="goToOrders">
# ...
# But in methods:
# 71→            goToMessages() {
# ...
# It didn't show goToOrders definition in the snippet (limit 100).
# It likely exists or is missing. Let's check if it exists in the file content we read or just assume we need to add it if missing.

# Let's add goToRefunds method.
# Insert before goToMessages or similar.
target_method = """            goToMessages() {"""
refund_method = """            goToRefunds() {
                uni.navigateTo({ url: '/pages/user/refund_list' });
            },
"""
if target_method in content and "goToRefunds" not in content:
    content = content.replace(target_method, refund_method + target_method)
    
with open(user_vue_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated user.vue with My Refunds link")

# Update frontend/pages/merchant/dashboard.vue to add "Refund Management" link
merchant_vue_path = r'D:\spb-expert11\frontend\pages\merchant\dashboard.vue'
with open(merchant_vue_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add link
# After "Order Management"
order_mgmt = """            <view class="menu-item" @click="goToOrders">
                <view class="menu-icon icon-order"></view>
                <text>Order Management</text>
                <text class="arrow">></text>
            </view>"""
            
refund_mgmt = """
            <view class="menu-item" @click="goToRefunds">
                <view class="menu-icon icon-refund"></view>
                <text>Refund Management</text>
                <text class="arrow">></text>
            </view>"""

if order_mgmt in content and "goToRefunds" not in content:
    content = content.replace(order_mgmt, order_mgmt + refund_mgmt)
    
# Add method
target_method_m = """            goToOrders() {"""
refund_method_m = """            goToRefunds() {
                uni.navigateTo({ url: '/pages/merchant/refund_list' });
            },
"""
if target_method_m in content and "goToRefunds" not in content:
    content = content.replace(target_method_m, refund_method_m + target_method_m)
    
with open(merchant_vue_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated merchant/dashboard.vue with Refund Management link")
