import os

# Update merchant/dashboard.vue (Modern Dashboard UI)
merchant_vue_path = r'D:\spb-expert11\frontend\pages\merchant\dashboard.vue'
merchant_vue_content = """<template>
	<view class="container">
        <!-- Header Background -->
        <view class="dashboard-header">
            <view class="shop-info">
                <view class="shop-avatar">🏪</view>
                <view class="shop-text">
                    <text class="shop-name">My Shop</text>
                    <text class="shop-status">Open for Business</text>
                </view>
            </view>
        </view>
        
        <!-- Stats Card -->
        <view class="stats-panel">
            <view class="stats-header">
                <text class="stats-title">Overview</text>
                <text class="stats-date">{{ currentDate }}</text>
            </view>
            <view class="stats-grid">
                <view class="stat-item">
                    <text class="stat-num">{{ stats.today_orders || 0 }}</text>
                    <text class="stat-label">Today's Orders</text>
                </view>
                <view class="stat-item">
                    <text class="stat-num">{{ stats.pending_ship || 0 }}</text>
                    <text class="stat-label">To Ship</text>
                </view>
                <view class="stat-item">
                    <text class="stat-num">¥{{ stats.today_sales || '0.00' }}</text>
                    <text class="stat-label">Today's Sales</text>
                </view>
            </view>
        </view>
        
        <!-- Menu Grid -->
        <view class="menu-panel">
            <view class="panel-title">Management</view>
            <view class="menu-grid">
                <view class="menu-item" @click="goToOrders">
                    <view class="menu-icon bg-blue">📦</view>
                    <text class="menu-text">Orders</text>
                </view>
                <view class="menu-item" @click="goToProducts">
                    <view class="menu-icon bg-orange">🛍️</view>
                    <text class="menu-text">Products</text>
                </view>
                <view class="menu-item" @click="goToCoupons">
                    <view class="menu-icon bg-red">🎫</view>
                    <text class="menu-text">Coupons</text>
                </view>
                <view class="menu-item" @click="goToRefunds">
                    <view class="menu-icon bg-purple">💸</view>
                    <text class="menu-text">Refunds</text>
                </view>
                <view class="menu-item" @click="goToShopSettings">
                    <view class="menu-icon bg-green">⚙️</view>
                    <text class="menu-text">Settings</text>
                </view>
            </view>
        </view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';
    
	export default {
        data() {
            return {
                stats: {
                    today_orders: 0,
                    pending_ship: 0,
                    today_sales: 0
                },
                currentDate: new Date().toLocaleDateString()
            }
        },
		onShow() {
            this.loadStats();
        },
        methods: {
            async loadStats() {
                try {
                    const res = await request({ url: '/store/merchant/orders/stats/' });
                    this.stats = res;
                } catch (e) {
                    console.error(e);
                }
            },
            goToProducts() {
                uni.navigateTo({ url: '/pages/merchant/product_list' }); 
            },
            goToCoupons() {
                uni.navigateTo({ url: '/pages/merchant/coupon_list' });
            },
            goToOrders() {
                uni.navigateTo({ url: '/pages/merchant/order_list' });
            },
            goToRefunds() {
                uni.navigateTo({ url: '/pages/merchant/refund_list' });
            },
            goToShopSettings() {
                uni.showToast({ title: 'Settings (Coming Soon)', icon: 'none' });
            }
		}
	}
</script>

<style lang="scss">
	.container {
		padding-bottom: 40rpx;
	}
    
    .dashboard-header {
        background: linear-gradient(135deg, #2b32b2, #1488cc); /* Blue Professional Gradient */
        height: 280rpx;
        padding: 40rpx 30rpx;
        color: #fff;
    }
    .shop-info {
        display: flex;
        align-items: center;
    }
    .shop-avatar {
        width: 100rpx;
        height: 100rpx;
        background-color: rgba(255,255,255,0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 50rpx;
        margin-right: 20rpx;
    }
    .shop-name { font-size: 36rpx; font-weight: bold; display: block; }
    .shop-status { font-size: 24rpx; opacity: 0.8; }
    
    .stats-panel {
        background-color: #fff;
        margin: -80rpx 20rpx 20rpx;
        border-radius: 16rpx;
        padding: 30rpx;
        box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.05);
    }
    .stats-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20rpx;
        border-bottom: 1rpx solid #f0f0f0;
        padding-bottom: 10rpx;
    }
    .stats-title { font-size: 30rpx; font-weight: bold; color: #333; }
    .stats-date { font-size: 24rpx; color: #999; }
    
    .stats-grid {
        display: flex;
        justify-content: space-between;
    }
    .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 33%;
    }
    .stat-num { font-size: 36rpx; font-weight: bold; color: #333; margin-bottom: 6rpx; }
    .stat-label { font-size: 24rpx; color: #666; }
    
    .menu-panel {
        background-color: #fff;
        margin: 20rpx;
        border-radius: 16rpx;
        padding: 30rpx;
    }
    .panel-title { font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 30rpx; }
    
    .menu-grid {
        display: flex;
        flex-wrap: wrap;
    }
    .menu-item {
        width: 25%;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 30rpx;
    }
    .menu-icon {
        width: 90rpx;
        height: 90rpx;
        border-radius: 30rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40rpx;
        margin-bottom: 10rpx;
        color: #fff;
    }
    .menu-text { font-size: 24rpx; color: #333; }
    
    /* Icon Colors */
    .bg-blue { background-color: #448aff; }
    .bg-orange { background-color: #ff9100; }
    .bg-red { background-color: #ff5252; }
    .bg-purple { background-color: #7c4dff; }
    .bg-green { background-color: #00c853; }
</style>
"""

with open(merchant_vue_path, 'w', encoding='utf-8') as f:
    f.write(merchant_vue_content)
print("Updated merchant/dashboard.vue")
