import os

BASE_DIR = r"D:\spb-expert11\frontend"
USER_VUE_PATH = os.path.join(BASE_DIR, "pages", "user", "user.vue")
LOGIN_VUE_PATH = os.path.join(BASE_DIR, "pages", "login", "login.vue")
PAY_VUE_PATH = os.path.join(BASE_DIR, "pages", "order", "pay.vue")
PAGES_JSON_PATH = os.path.join(BASE_DIR, "pages.json")

# 1. Update User Vue
user_vue_content = r'''<template>
	<view class="container">
        <!-- Header Background -->
        <view class="user-header-bg">
            <view class="header-tools">
                <view class="btn-settings" @click="goToSettings">
                    <text class="icon-settings">⚙️</text>
                </view>
            </view>
        </view>
        
        <!-- User Info Card -->
		<view class="user-card">
            <view class="user-info-row" v-if="isLoggedIn" @click="goToProfile">
                <view class="avatar-box">
                    <image :src="userInfo.avatar || '/static/avatar_placeholder.png'" mode="aspectFill" class="avatar"></image>
                </view>
                <view class="info-box">
                    <text class="username">{{ userInfo.username || 'User' }}</text>
                    <view class="user-tags">
                        <text class="tag" v-if="userInfo.is_merchant">Merchant</text>
                        <text class="tag" v-else>Member</text>
                    </view>
                </view>
                <view class="arrow-right">></view>
            </view>
            <view class="user-info-row" v-else @click="goToLogin">
                <view class="avatar-box">
                    <view class="avatar-placeholder">Login</view>
                </view>
                <view class="info-box">
                    <text class="username">Login / Register</text>
                    <text class="sub-text">Click to login for more features</text>
                </view>
            </view>
            
            <!-- Stats Row -->
            <view class="stats-row">
                <view class="stat-item" @click="goToFavorites">
                    <text class="stat-num">{{ stats.favorites || 0 }}</text>
                    <text class="stat-label">Favorites</text>
                </view>
                <view class="stat-item" @click="goToCoupons">
                    <text class="stat-num">{{ stats.coupons || 0 }}</text>
                    <text class="stat-label">Coupons</text>
                </view>
                <view class="stat-item">
                    <text class="stat-num">0</text>
                    <text class="stat-label">Footprint</text>
                </view>
            </view>
        </view>

        <!-- Order Panel -->
        <view class="panel">
            <view class="panel-header" @click="goToOrders">
                <text class="panel-title">My Orders</text>
                <text class="panel-more">View All ></text>
            </view>
            <view class="order-grid">
                <view class="order-item" @click="goToOrders(1)">
                    <view class="order-icon">💳</view>
                    <text class="order-label">Pending</text>
                </view>
                <view class="order-item" @click="goToOrders(2)">
                    <view class="order-icon">📦</view>
                    <text class="order-label">To Ship</text>
                </view>
                <view class="order-item" @click="goToOrders(3)">
                    <view class="order-icon">🚚</view>
                    <text class="order-label">To Receive</text>
                </view>
                <view class="order-item" @click="goToOrders(4)">
                    <view class="order-icon">💬</view>
                    <text class="order-label">To Review</text>
                </view>
                <view class="order-item" @click="goToRefunds">
                    <view class="order-icon">💰</view>
                    <text class="order-label">Refunds</text>
                </view>
            </view>
        </view>

        <!-- Tools Panel -->
        <view class="panel">
            <view class="panel-header">
                <text class="panel-title">Services</text>
            </view>
            <view class="tools-grid">
                <view class="tool-item" @click="goToMessages">
                    <view class="tool-icon" style="background-color: #e1f5fe; color: #03a9f4;">💬</view>
                    <text class="tool-label">Messages</text>
                </view>
                <view class="tool-item" @click="goToAddresses">
                    <view class="tool-icon" style="background-color: #e8f5e9; color: #4caf50;">📍</view>
                    <text class="tool-label">Addresses</text>
                </view>
                <view class="tool-item" v-if="isLoggedIn && userInfo.is_merchant" @click="goToMerchantDashboard">
                    <view class="tool-icon" style="background-color: #fff3e0; color: #ff9800;">🏪</view>
                    <text class="tool-label">Merchant</text>
                </view>
                <view class="tool-item" v-if="isLoggedIn && !userInfo.is_merchant" @click="handleMerchantApply">
                    <view class="tool-icon" style="background-color: #f3e5f5; color: #9c27b0;">📝</view>
                    <text class="tool-label">Apply</text>
                </view>
                <view class="tool-item" v-if="isLoggedIn" @click="handleLogout">
                    <view class="tool-icon" style="background-color: #ffebee; color: #f44336;">🚪</view>
                    <text class="tool-label">Logout</text>
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
				isLoggedIn: false,
                userInfo: {},
                stats: {
                    favorites: 0,
                    coupons: 0
                }
			}
		},
		onShow() {
            this.checkLogin();
		},
		methods: {
            goToLogin() {
                uni.navigateTo({ url: '/pages/login/login' });
            },
            goToSettings() {
                uni.navigateTo({ url: '/pages/user/settings' });
            },
            goToProfile() {
                uni.navigateTo({ url: '/pages/user/settings' });
            },
            goToMessages() {
                uni.navigateTo({ url: '/pages/chat/list' });
            },
            goToFavorites() {
                uni.navigateTo({ url: '/pages/user/favorites' });
            },
            goToCoupons() {
                uni.navigateTo({ url: '/pages/user/coupon_list' });
            },
            goToAddresses() {
                uni.navigateTo({ url: '/pages/address/list' });
            },
            goToOrders(tabIndex) {
                // Pass tab index if supported by order page
                uni.navigateTo({ url: '/pages/order/order?tab=' + (tabIndex || 0) });
            },
            goToRefunds() {
                uni.navigateTo({ url: '/pages/user/refund_list' });
            },
            goToMerchantDashboard() {
                uni.navigateTo({ url: '/pages/merchant/dashboard' });
            },
            handleMerchantApply() {
                uni.navigateTo({ url: '/pages/merchant/dashboard' }); // Redirect to dashboard which handles apply/status
            },
            handleLogout() {
                uni.removeStorageSync('token');
                this.isLoggedIn = false;
                this.userInfo = {};
                this.stats = { favorites: 0, coupons: 0 };
                uni.showToast({ title: 'Logged out' });
            },

            checkLogin() {
                const token = uni.getStorageSync('token');
                this.isLoggedIn = !!token;
                if (this.isLoggedIn) {
                    this.fetchUserInfo();
                    this.fetchStats();
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
                    // If 401, logout
                    // this.handleLogout();
                }
            },
            async fetchStats() {
                // Placeholder for stats API
                // In real app, we would fetch counts
            }
		}
	}
</script>

<style lang="scss">
    .container {
        padding-bottom: 40rpx;
        background-color: #f5f5f5;
        min-height: 100vh;
    }
    
    .user-header-bg {
        height: 300rpx;
        background: linear-gradient(to right, #FF5000, #ff8c00);
        border-bottom-left-radius: 40rpx;
        border-bottom-right-radius: 40rpx;
        padding-top: 60rpx;
        /* #ifdef H5 */
        padding-top: 20rpx;
        /* #endif */
        position: relative;
    }

    .header-tools {
        position: absolute;
        top: 60rpx;
        right: 30rpx;
        /* #ifdef H5 */
        top: 20rpx;
        /* #endif */
        z-index: 10;
    }
    .btn-settings {
        padding: 10rpx;
    }
    .icon-settings {
        font-size: 40rpx;
        color: #fff;
    }
    
    .user-card {
        margin: -160rpx 20rpx 20rpx;
        background-color: #fff;
        border-radius: 20rpx;
        padding: 30rpx;
        box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.08);
        position: relative;
        z-index: 2;
    }
    
    .user-info-row {
        display: flex;
        align-items: center;
        margin-bottom: 40rpx;
    }
    
    .avatar-box {
        margin-right: 20rpx;
    }
    .avatar {
        width: 120rpx;
        height: 120rpx;
        border-radius: 50%;
        border: 4rpx solid #fff;
        box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
    }
    .avatar-placeholder {
        width: 120rpx;
        height: 120rpx;
        border-radius: 50%;
        background-color: #f0f0f0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24rpx;
        color: #999;
        border: 4rpx solid #fff;
        box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
    }
    
    .info-box {
        flex: 1;
    }
    .username {
        font-size: 36rpx;
        font-weight: bold;
        color: #333;
        display: block;
        margin-bottom: 10rpx;
    }
    .sub-text {
        font-size: 24rpx;
        color: #999;
    }
    .user-tags {
        display: flex;
    }
    .tag {
        font-size: 20rpx;
        background-color: #FFF0E5;
        color: #FF5000;
        padding: 4rpx 12rpx;
        border-radius: 20rpx;
        border: 1px solid rgba(255,80,0,0.2);
    }
    .arrow-right {
        color: #ccc;
        font-size: 32rpx;
    }
    
    .stats-row {
        display: flex;
        justify-content: space-around;
    }
    .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .stat-num {
        font-size: 32rpx;
        font-weight: bold;
        color: #333;
    }
    .stat-label {
        font-size: 24rpx;
        color: #666;
        margin-top: 6rpx;
    }
    
    /* Panels */
    .panel {
        background-color: #fff;
        border-radius: 20rpx;
        margin: 20rpx;
        padding: 20rpx;
        box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.03);
    }
    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 20rpx;
        border-bottom: 1px solid #f5f5f5;
        margin-bottom: 20rpx;
    }
    .panel-title { font-size: 30rpx; font-weight: bold; color: #333; }
    .panel-more { font-size: 24rpx; color: #999; }

    .order-grid {
        display: flex;
        justify-content: space-between;
    }
    .order-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 20%;
    }
    .order-icon { font-size: 48rpx; margin-bottom: 10rpx; }
    .order-label { font-size: 24rpx; color: #666; }

    .tools-grid {
        display: flex;
        flex-wrap: wrap;
    }
    .tool-item {
        width: 25%;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 30rpx;
    }
    .tool-icon {
        width: 80rpx; height: 80rpx;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 40rpx;
        margin-bottom: 10rpx;
    }
    .tool-label { font-size: 24rpx; color: #666; }
</style>'''

# 2. Update Login Vue
login_vue_content = r'''<template>
	<view class="container">
        <view class="header">
            <image src="/static/logo.png" mode="aspectFit" class="logo"></image>
            <text class="title">Marine Mall</text>
        </view>
        
		<view class="login-card">
            <view class="title-bar">
                <text class="card-title">Login</text>
            </view>
            
            <view class="input-group">
                <text class="label">Username</text>
                <input class="input" type="text" v-model="username" placeholder="Enter your username" />
            </view>
            <view class="input-group">
                <text class="label">Password</text>
                <input class="input" type="password" v-model="password" placeholder="Enter your password" />
            </view>
            
            <button class="btn-login" @click="handleLogin" :loading="loading">Login</button>
            
            <view class="links">
                <text class="link" @click="goToRegister">Register Account</text>
                <text class="divider">|</text>
                <text class="link">Forgot Password?</text>
            </view>
        </view>
        
        <view class="footer">
            <text class="copyright">© 2026 Marine Mall</text>
        </view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				username: '',
                password: '',
                loading: false
			}
		},
		methods: {
            async handleLogin() {
                if (!this.username || !this.password) {
                    uni.showToast({ title: 'Please fill all fields', icon: 'none' });
                    return;
                }
                
                this.loading = true;
                try {
                    const res = await request({
                        url: '/users/login/',
                        method: 'POST',
                        data: {
                            username: this.username,
                            password: this.password
                        }
                    });
                    
                    if (res.access) {
                        uni.setStorageSync('token', res.access);
                        uni.showToast({ title: 'Login Success' });
                        
                        // Fetch user info immediately to update state
                        try {
                            const userRes = await request({ url: '/users/me/' });
                            uni.setStorageSync('userInfo', userRes);
                        } catch(e) {}

                        // Navigate back or to user center
                        setTimeout(() => {
                            uni.switchTab({ url: '/pages/user/user' });
                        }, 1000);
                    }
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Login Failed: ' + (e.detail || 'Error'), icon: 'none' });
                } finally {
                    this.loading = false;
                }
            },
            goToRegister() {
                uni.navigateTo({ url: '/pages/login/register' });
            }
		}
	}
</script>

<style lang="scss">
	.container {
		min-height: 100vh;
        background-color: #f5f5f5;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 50rpx;
	}
    
    .header {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 80rpx;
        margin-bottom: 60rpx;
        .logo { width: 120rpx; height: 120rpx; margin-bottom: 20rpx; background: #ddd; border-radius: 20rpx; }
        .title { font-size: 40rpx; font-weight: bold; color: #333; }
    }
    
    .login-card {
        width: 100%;
        background: #fff;
        border-radius: 20rpx;
        padding: 40rpx;
        box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
    }
    
    .title-bar { margin-bottom: 40rpx; }
    .card-title { font-size: 36rpx; font-weight: bold; color: #333; position: relative; padding-left: 20rpx; }
    .card-title::before {
        content: ''; position: absolute; left: 0; top: 8rpx; bottom: 8rpx; width: 8rpx;
        background: #FF5000; border-radius: 4rpx;
    }

    .input-group {
        margin-bottom: 30rpx;
    }
    .label { font-size: 28rpx; color: #666; margin-bottom: 10rpx; display: block; }
    .input {
        width: 100%;
        height: 80rpx;
        background: #f9f9f9;
        border-radius: 10rpx;
        padding: 0 20rpx;
        font-size: 30rpx;
        color: #333;
    }
    
    .btn-login {
        background: linear-gradient(90deg, #FF7A00, #FF5000);
        color: #fff;
        margin-top: 50rpx;
        border-radius: 40rpx;
        font-size: 32rpx;
        font-weight: bold;
        &::after { border: none; }
    }
    
    .links {
        margin-top: 30rpx;
        display: flex;
        justify-content: center;
        font-size: 26rpx;
        color: #999;
    }
    .link { color: #666; padding: 0 10rpx; }
    .divider { color: #ddd; }
    
    .footer {
        margin-top: auto;
        padding-bottom: 30rpx;
        .copyright { font-size: 24rpx; color: #ccc; }
    }
</style>'''

# 3. Update Pay Vue
pay_vue_content = r'''<template>
    <view class="container">
        <view class="status-card" v-if="order">
            <view class="status-icon" v-if="order.status === 'pending'">🕒</view>
            <view class="status-icon success" v-else-if="order.status === 'paid'">✅</view>
            <text class="status-text">{{ order.status === 'pending' ? 'Payment Pending' : 'Paid' }}</text>
            <view class="amount-box">
                <text class="currency">¥</text>
                <text class="amount">{{ order.total_amount }}</text>
            </view>
            <text class="order-no">Order No: {{ order.order_no }}</text>
        </view>

        <view class="method-card" v-if="order && order.status === 'pending'">
            <view class="card-title">Payment Method</view>
            <view class="method-list">
                <view class="method-item" @click="selectMethod('wechat')">
                    <view class="method-left">
                        <view class="icon-wechat">💬</view>
                        <text class="method-name">WeChat Pay</text>
                    </view>
                    <view class="radio" :class="{checked: payMethod === 'wechat'}"></view>
                </view>
                <view class="method-item disabled">
                    <view class="method-left">
                        <view class="icon-alipay">🅰️</view>
                        <text class="method-name">Alipay (Not Available)</text>
                    </view>
                    <view class="radio"></view>
                </view>
            </view>
        </view>

        <view class="footer-btn">
            <button class="btn-pay" @click="handlePay" :loading="loading" :disabled="order && order.status !== 'pending'">
                {{ order && order.status === 'pending' ? 'Pay Now' : 'Payment Completed' }}
            </button>
        </view>
    </view>
</template>

<script>
    import { request } from '../../common/api.js';

    export default {
        data() {
            return {
                orderId: null,
                order: null,
                loading: false,
                payMethod: 'wechat'
            }
        },
        onLoad(options) {
            if (options.order_id || options.id) {
                this.orderId = options.order_id || options.id;
                this.loadOrder();
            }
        },
        methods: {
            async loadOrder() {
                try {
                    const res = await request({ url: '/store/orders/' + this.orderId + '/' });
                    this.order = res;
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Failed to load order', icon: 'none' });
                }
            },
            selectMethod(method) {
                this.payMethod = method;
            },
            async handlePay() {
                if (this.order.status !== 'pending') return;
                
                this.loading = true;
                uni.showLoading({ title: 'Processing...' });
                try {
                    const res = await request({ 
                        url: '/store/orders/' + this.orderId + '/pay/',
                        method: 'POST',
                        data: { method: this.payMethod }
                    });
                    
                    uni.hideLoading();
                    uni.showToast({ title: 'Payment Successful', icon: 'success' });
                    
                    // Refresh order status
                    await this.loadOrder();
                    
                    // Redirect after delay
                    setTimeout(() => {
                        // Go to Order Detail or List
                        uni.redirectTo({ url: '/pages/order/order?tab=2' }); // 2 is "To Ship" (Paid)
                    }, 1500);
                    
                } catch (e) {
                    uni.hideLoading();
                    console.error(e);
                    uni.showToast({ title: 'Payment Failed', icon: 'none' });
                } finally {
                    this.loading = false;
                }
            }
        }
    }
</script>

<style lang="scss">
    .container { 
        padding: 20rpx; 
        background: #f5f5f5; 
        min-height: 100vh; 
        padding-bottom: 120rpx;
    }
    
    .status-card {
        background: #fff;
        border-radius: 20rpx;
        padding: 50rpx 30rpx;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20rpx;
        box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.02);
    }
    .status-icon {
        font-size: 80rpx;
        margin-bottom: 20rpx;
        &.success { color: #4caf50; }
    }
    .status-text { font-size: 32rpx; color: #333; font-weight: bold; margin-bottom: 30rpx; }
    
    .amount-box { margin-bottom: 20rpx; color: #FF5000; }
    .currency { font-size: 40rpx; margin-right: 5rpx; font-weight: bold; }
    .amount { font-size: 72rpx; font-weight: bold; }
    
    .order-no { font-size: 24rpx; color: #999; }
    
    .method-card {
        background: #fff;
        border-radius: 20rpx;
        padding: 30rpx;
        box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.02);
    }
    .card-title { font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 30rpx; }
    
    .method-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20rpx 0;
        border-bottom: 1px solid #f9f9f9;
        &:last-child { border-bottom: none; }
        &.disabled { opacity: 0.5; }
    }
    .method-left { display: flex; align-items: center; }
    .icon-wechat { font-size: 40rpx; margin-right: 20rpx; color: #09bb07; }
    .icon-alipay { font-size: 40rpx; margin-right: 20rpx; color: #00a0e9; }
    .method-name { font-size: 28rpx; color: #333; }
    
    .radio {
        width: 36rpx; height: 36rpx;
        border: 2rpx solid #ccc; border-radius: 50%;
        &.checked {
            background: #FF5000; border-color: #FF5000;
            position: relative;
            &::after {
                content: ''; position: absolute;
                left: 10rpx; top: 6rpx; width: 10rpx; height: 16rpx;
                border: solid #fff; border-width: 0 4rpx 4rpx 0; transform: rotate(45deg);
            }
        }
    }
    
    .footer-btn {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        padding: 20rpx 30rpx;
        background: #fff;
        box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
    }
    .btn-pay {
        background: linear-gradient(90deg, #FF7A00, #FF5000);
        color: #fff;
        border-radius: 40rpx;
        font-size: 32rpx;
        font-weight: bold;
        &::after { border: none; }
        &[disabled] { background: #ccc; color: #fff; }
    }
</style>'''

def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")
    except Exception as e:
        print(f"Error updating {path}: {e}")

# Execute updates
write_file(USER_VUE_PATH, user_vue_content)
write_file(LOGIN_VUE_PATH, login_vue_content)
write_file(PAY_VUE_PATH, pay_vue_content)

print("All login/pay/user updates complete.")
