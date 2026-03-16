import os
import json

# 1. Create pages/merchant/dashboard.vue
dashboard_path = r'D:\spb-expert11\frontend\pages\merchant\dashboard.vue'
dashboard_dir = os.path.dirname(dashboard_path)
if not os.path.exists(dashboard_dir):
    os.makedirs(dashboard_dir)

dashboard_content = """<template>
	<view class="container">
        <view class="header">
            <text class="title">Merchant Dashboard</text>
        </view>
        
        <view class="stats-grid">
            <view class="stat-card">
                <text class="stat-num">0</text>
                <text class="stat-label">Today's Orders</text>
            </view>
            <view class="stat-card">
                <text class="stat-num">0</text>
                <text class="stat-label">Pending Ship</text>
            </view>
        </view>
        
        <view class="menu-list">
            <view class="menu-item" @click="goToOrders">
                <view class="menu-icon icon-order"></view>
                <text>Order Management</text>
                <text class="arrow">></text>
            </view>
            <view class="menu-item">
                <view class="menu-icon icon-product"></view>
                <text>Product Management</text>
                <text class="arrow">></text>
            </view>
        </view>
	</view>
</template>

<script>
	export default {
		methods: {
            goToOrders() {
                uni.navigateTo({ url: '/pages/merchant/order_list' });
            }
		}
	}
</script>

<style>
	.container {
		background-color: #f5f5f5;
        min-height: 100vh;
        padding: 20rpx;
	}
    .header {
        margin-bottom: 30rpx;
    }
    .title {
        font-size: 36rpx;
        font-weight: bold;
    }
    .stats-grid {
        display: flex;
        justify-content: space-between;
        margin-bottom: 30rpx;
    }
    .stat-card {
        width: 48%;
        background-color: #fff;
        padding: 30rpx;
        border-radius: 10rpx;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .stat-num {
        font-size: 40rpx;
        font-weight: bold;
        color: #ff5000;
        margin-bottom: 10rpx;
    }
    .stat-label {
        font-size: 24rpx;
        color: #666;
    }
    .menu-list {
        background-color: #fff;
        border-radius: 10rpx;
        overflow: hidden;
    }
    .menu-item {
        padding: 30rpx;
        border-bottom: 1rpx solid #eee;
        display: flex;
        align-items: center;
    }
    .menu-icon {
        width: 40rpx;
        height: 40rpx;
        background-color: #eee;
        margin-right: 20rpx;
        border-radius: 50%;
    }
    .icon-order { background-color: #4cd964; }
    .icon-product { background-color: #007aff; }
    .arrow {
        margin-left: auto;
        color: #ccc;
    }
</style>
"""
with open(dashboard_path, 'w', encoding='utf-8') as f:
    f.write(dashboard_content)
print(f"Created {dashboard_path}")


# 2. Create pages/merchant/order_list.vue
order_list_path = r'D:\spb-expert11\frontend\pages\merchant\order_list.vue'
order_list_content = """<template>
	<view class="container">
        <view class="order-list">
            <view class="order-card" v-for="(order, index) in orders" :key="index">
                <view class="card-header">
                    <text class="order-no">Order: {{ order.order_no }}</text>
                    <text class="order-status">{{ order.status }}</text>
                </view>
                
                <view class="card-body">
                    <view class="info-row">
                        <text class="label">Recipient:</text>
                        <text>{{ order.recipient_name }} ({{ order.phone }})</text>
                    </view>
                    <view class="info-row">
                        <text class="label">Address:</text>
                        <text>{{ order.address }}</text>
                    </view>
                    <view class="product-summary">
                        <text>{{ order.items.length }} items</text>
                        <text class="total-price">Total: ¥{{ order.total_amount }}</text>
                    </view>
                </view>
                
                <view class="card-footer">
                    <view class="btn btn-ship" v-if="order.status === 'paid'" @click="shipOrder(order)">Ship Now</view>
                    <view class="btn disabled" v-if="order.status === 'shipped'">Shipped</view>
                </view>
            </view>
             <view class="empty-state" v-if="orders.length === 0">
                <text>No orders received.</text>
            </view>
        </view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				orders: []
			}
		},
		onShow() {
            this.loadOrders();
		},
		methods: {
            async loadOrders() {
                try {
                    const res = await request({ url: '/store/merchant/orders/' });
                    this.orders = res;
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Load failed', icon: 'none' });
                }
            },
            async shipOrder(order) {
                try {
                    await request({
                        url: `/store/merchant/orders/${order.id}/ship/`,
                        method: 'POST'
                    });
                    uni.showToast({ title: 'Order Shipped!' });
                    this.loadOrders(); // Refresh
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Operation failed', icon: 'none' });
                }
            }
		}
	}
</script>

<style>
	.container {
		background-color: #f5f5f5;
        min-height: 100vh;
        padding: 20rpx;
	}
    .order-card {
        background-color: #fff;
        border-radius: 12rpx;
        margin-bottom: 20rpx;
        padding: 20rpx;
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20rpx;
        border-bottom: 1rpx solid #eee;
        padding-bottom: 10rpx;
    }
    .order-no {
        font-size: 24rpx;
        color: #666;
    }
    .order-status {
        color: #ff5000;
        font-weight: bold;
    }
    .info-row {
        font-size: 26rpx;
        margin-bottom: 10rpx;
        display: flex;
    }
    .label {
        color: #999;
        width: 140rpx;
    }
    .product-summary {
        display: flex;
        justify-content: space-between;
        margin-top: 20rpx;
        padding-top: 10rpx;
        border-top: 1rpx dashed #eee;
        font-weight: bold;
    }
    .total-price {
        color: #ff5000;
    }
    .card-footer {
        margin-top: 20rpx;
        display: flex;
        justify-content: flex-end;
    }
    .btn {
        padding: 10rpx 30rpx;
        border-radius: 30rpx;
        font-size: 24rpx;
        background-color: #eee;
        color: #666;
    }
    .btn-ship {
        background-color: #007aff;
        color: #fff;
    }
    .empty-state {
        text-align: center;
        padding-top: 100rpx;
        color: #999;
    }
</style>
"""
with open(order_list_path, 'w', encoding='utf-8') as f:
    f.write(order_list_content)
print(f"Created {order_list_path}")


# 3. Update pages/user/user.vue (Add Merchant Logic)
user_vue_path = r'D:\spb-expert11\frontend\pages\user\user.vue'
user_vue_content = """<template>
	<view class="content">
        <view class="header" v-if="isLoggedIn">
            <view class="avatar">
                <image src="/static/avatar_placeholder.png" mode="aspectFill"></image>
            </view>
            <view class="info">
                <text class="username">{{ userInfo.username || 'User' }}</text>
                <text class="role" v-if="userInfo.is_merchant">Merchant</text>
                <text class="role" v-else>Member</text>
            </view>
        </view>
        <view class="header-login" v-else @click="goToLogin">
            <text>Click to Login</text>
        </view>

        <view class="menu-list">
            <!-- Merchant Dashboard Entry -->
            <view class="menu-item highlight" v-if="isLoggedIn && userInfo.is_merchant" @click="goToMerchantDashboard">
                <text>Merchant Dashboard</text>
                <text class="arrow">></text>
            </view>

            <view class="menu-item" @click="handleMerchantApply" v-if="isLoggedIn && !userInfo.is_merchant">
                <text>Merchant Application</text>
                <text class="arrow">></text>
            </view>
            <view class="menu-item" @click="goToOrders">
                <text>My Orders</text>
                <text class="arrow">></text>
            </view>
            <view class="menu-item" v-if="isLoggedIn" @click="handleLogout">
                <text>Logout</text>
                <text class="arrow">></text>
            </view>
        </view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				isLoggedIn: false,
                userInfo: {}
			}
		},
		onShow() {
            this.checkLogin();
		},
		methods: {
            checkLogin() {
                const token = uni.getStorageSync('token');
                this.isLoggedIn = !!token;
                if (this.isLoggedIn) {
                    this.fetchUserInfo();
                } else {
                    this.userInfo = {};
                }
            },
            async fetchUserInfo() {
                try {
                    const res = await request({ url: '/users/me/' });
                    this.userInfo = res;
                    uni.setStorageSync('userInfo', res);
                } catch (e) {
                    console.error(e);
                }
            },
            goToLogin() {
                uni.navigateTo({ url: '/pages/login/login' });
            },
            goToOrders() {
                if (!this.isLoggedIn) {
                    this.goToLogin();
                    return;
                }
                uni.navigateTo({ url: '/pages/order/order' });
            },
            goToMerchantDashboard() {
                uni.navigateTo({ url: '/pages/merchant/dashboard' });
            },
            handleLogout() {
                uni.removeStorageSync('token');
                uni.removeStorageSync('userInfo');
                this.isLoggedIn = false;
                this.userInfo = {};
                uni.showToast({ title: 'Logged out', icon: 'none' });
            },
            async handleMerchantApply() {
                if (!this.isLoggedIn) {
                    this.goToLogin();
                    return;
                }
                
                try {
                    const res = await request({
                        url: '/users/merchant/apply/',
                        method: 'POST',
                        header: {
                            'Authorization': 'Bearer ' + uni.getStorageSync('token')
                        },
                        data: {
                            company_name: "My New Company", 
                            business_license: "http://example.com/license.jpg"
                        }
                    });
                    uni.showToast({ title: 'Application Submitted!' });
                    this.fetchUserInfo(); // Refresh to see if status updated immediately
                } catch (e) {
                    uni.showToast({ title: e.data.detail || 'Error', icon: 'none' });
                }
            }
		}
	}
</script>

<style>
    .content {
        background-color: #f8f8f8;
        min-height: 100vh;
    }
    .header {
        background-color: #fff;
        padding: 40rpx;
        display: flex;
        align-items: center;
        margin-bottom: 20rpx;
    }
    .header-login {
        background-color: #fff;
        padding: 60rpx;
        text-align: center;
        margin-bottom: 20rpx;
        font-size: 32rpx;
        color: #ff5000;
    }
    .avatar {
        width: 100rpx;
        height: 100rpx;
        background-color: #eee;
        border-radius: 50%;
        margin-right: 20rpx;
        overflow: hidden;
    }
    .avatar image {
        width: 100%;
        height: 100%;
    }
    .info {
        display: flex;
        flex-direction: column;
    }
    .username {
        font-size: 32rpx;
        font-weight: bold;
    }
    .role {
        font-size: 24rpx;
        color: #666;
        margin-top: 10rpx;
        background-color: #f0f0f0;
        padding: 2rpx 10rpx;
        border-radius: 10rpx;
        align-self: flex-start;
    }
    .menu-list {
        background-color: #fff;
    }
    .menu-item {
        padding: 30rpx;
        border-bottom: 1rpx solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .highlight text {
        color: #ff5000;
        font-weight: bold;
    }
    .arrow {
        color: #ccc;
    }
</style>
"""
with open(user_vue_path, 'w', encoding='utf-8') as f:
    f.write(user_vue_content)
print(f"Updated {user_vue_path}")


# 4. Update pages.json
pages_json_path = r'D:\spb-expert11\frontend\pages.json'
with open(pages_json_path, 'r', encoding='utf-8') as f:
    pages_config = json.load(f)

# Add new pages if not exist
new_pages = [
    {
        "path": "pages/merchant/dashboard",
        "style": {
            "navigationBarTitleText": "Merchant Dashboard"
        }
    },
    {
        "path": "pages/merchant/order_list",
        "style": {
            "navigationBarTitleText": "Order Management"
        }
    }
]

for new_page in new_pages:
    if not any(p['path'] == new_page['path'] for p in pages_config['pages']):
        pages_config['pages'].append(new_page)
    
with open(pages_json_path, 'w', encoding='utf-8') as f:
    json.dump(pages_config, f, indent=4)
print(f"Updated {pages_json_path}")
