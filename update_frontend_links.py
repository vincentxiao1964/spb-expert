import os

# 1. Update merchant/dashboard.vue
dashboard_path = r'D:\spb-expert11\frontend\pages\merchant\dashboard.vue'
with open(dashboard_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Coupon Management button
if "Coupon Management" not in content:
    # Look for Product Management block
    target = """<view class="menu-item" @click="goToProducts">
                <view class="menu-icon icon-product"></view>
                <text>Product Management</text>
                <text class="arrow">></text>
            </view>"""
            
    replacement = """<view class="menu-item" @click="goToProducts">
                <view class="menu-icon icon-product"></view>
                <text>Product Management</text>
                <text class="arrow">></text>
            </view>
            <view class="menu-item" @click="goToCoupons">
                <view class="menu-icon icon-coupon"></view>
                <text>Coupon Management</text>
                <text class="arrow">></text>
            </view>"""
            
    content = content.replace(target, replacement)
    
    # Add goToCoupons method
    method_target = """goToProducts() {
                uni.navigateTo({ url: '/pages/merchant/product_list' }); 
            },"""
    method_replacement = """goToProducts() {
                uni.navigateTo({ url: '/pages/merchant/product_list' }); 
            },
            goToCoupons() {
                uni.navigateTo({ url: '/pages/merchant/coupon_list' });
            },"""
            
    content = content.replace(method_target, method_replacement)
    
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated merchant/dashboard.vue")

# 2. Update user/user.vue
user_path = r'D:\spb-expert11\frontend\pages\user\user.vue'
with open(user_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "My Coupons" not in content:
    # Add My Coupons button
    target = """<view class="menu-item" @click="goToFavorites">
                <text>My Favorites</text>
                <text class="arrow">></text>
            </view>"""
            
    replacement = """<view class="menu-item" @click="goToFavorites">
                <text>My Favorites</text>
                <text class="arrow">></text>
            </view>
            <view class="menu-item" @click="goToCoupons">
                <text>My Coupons</text>
                <text class="arrow">></text>
            </view>"""
            
    content = content.replace(target, replacement)
    
    # Add goToCoupons method
    method_target = """goToFavorites() {
                uni.navigateTo({ url: '/pages/user/favorites' });
            },"""
    method_replacement = """goToFavorites() {
                uni.navigateTo({ url: '/pages/user/favorites' });
            },
            goToCoupons() {
                uni.navigateTo({ url: '/pages/user/coupon_list' });
            },"""
            
    content = content.replace(method_target, method_replacement)
    
    with open(user_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated user/user.vue")
