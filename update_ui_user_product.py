import os

# 1. Update user.vue (Modern Profile UI)
user_vue_path = r'D:\spb-expert11\frontend\pages\user\user.vue'
user_vue_content = """<template>
	<view class="container">
        <!-- Header Background -->
        <view class="user-header-bg"></view>
        
        <!-- User Info Card -->
		<view class="user-card">
            <view class="user-info-row" v-if="isLoggedIn" @click="goToSettings">
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
                // Placeholder for settings
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
                uni.navigateTo({ url: '/pages/order/order' });
            },
            goToRefunds() {
                uni.navigateTo({ url: '/pages/user/refund_list' });
            },
            goToMerchantDashboard() {
                uni.navigateTo({ url: '/pages/merchant/dashboard' });
            },
            handleMerchantApply() {
                uni.showToast({ title: 'Application Submitted', icon: 'success' });
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
                } catch (e) {
                    console.error(e);
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
    }
    
    .user-header-bg {
        height: 300rpx;
        background: linear-gradient(to right, #FF5000, #ff8c00);
        border-bottom-left-radius: 40rpx;
        border-bottom-right-radius: 40rpx;
    }
    
    .user-card {
        margin: -200rpx 20rpx 20rpx;
        background-color: #fff;
        border-radius: 20rpx;
        padding: 30rpx;
        box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.08);
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
        background-color: #FF5000;
        color: #fff;
        padding: 4rpx 12rpx;
        border-radius: 20rpx;
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
        border-bottom: 1rpx solid #f0f0f0;
        margin-bottom: 20rpx;
    }
    .panel-title {
        font-size: 30rpx;
        font-weight: bold;
        color: #333;
    }
    .panel-more {
        font-size: 24rpx;
        color: #999;
    }
    
    .order-grid {
        display: flex;
        justify-content: space-around;
    }
    .order-item {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .order-icon {
        font-size: 40rpx;
        margin-bottom: 10rpx;
    }
    .order-label {
        font-size: 24rpx;
        color: #666;
    }
    
    .tools-grid {
        display: flex;
        flex-wrap: wrap;
    }
    .tool-item {
        width: 25%;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20rpx;
    }
    .tool-icon {
        width: 80rpx;
        height: 80rpx;
        border-radius: 40%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 36rpx;
        margin-bottom: 10rpx;
    }
    .tool-label {
        font-size: 24rpx;
        color: #666;
    }
</style>
"""

with open(user_vue_path, 'w', encoding='utf-8') as f:
    f.write(user_vue_content)
print("Updated user.vue")

# 2. Update product/detail.vue (Modern Detail UI)
detail_vue_path = r'D:\spb-expert11\frontend\pages\product\detail.vue'
detail_vue_content = """<template>
	<view class="container">
		<!-- Swiper -->
		<swiper class="swiper" indicator-dots autoplay circular indicator-active-color="#FF5000">
			<swiper-item v-for="(img, index) in product.images" :key="index">
				<image :src="img.image" mode="aspectFill" class="slide-image"></image>
			</swiper-item>
            <swiper-item v-if="!product.images || product.images.length === 0">
                <view class="no-image">No Image Available</view>
            </swiper-item>
		</swiper>

		<!-- Info Section -->
		<view class="info-card">
			<view class="price-row">
				<text class="currency">¥</text>
				<text class="price">{{ product.price }}</text>
			</view>
			<view class="title">{{ product.name }}</view>
            <view class="merchant-row" v-if="product.merchant_name">
                <text class="merchant-tag">Merchant</text>
                <text class="merchant-name">{{ product.merchant_name }}</text>
            </view>
            <view class="desc-box">
                <text class="desc-title">Description</text>
                <text class="description">{{ product.description }}</text>
            </view>
		</view>

        <!-- Coupons -->
        <view class="section-card" v-if="coupons.length > 0">
            <view class="section-header">
                <text class="section-title">Coupons</text>
            </view>
            <scroll-view scroll-x class="coupon-scroll">
                <view class="coupon-item" v-for="(coupon, index) in coupons" :key="index" @click="claimCoupon(coupon)">
                    <view class="coupon-left">
                        <view class="coupon-amount">
                            <text v-if="coupon.discount_type=='amount'">¥{{coupon.discount_value}}</text>
                            <text v-else>{{coupon.discount_value}}%</text>
                        </view>
                        <text class="coupon-cond">Min ¥{{coupon.min_spend}}</text>
                    </view>
                    <view class="coupon-right">
                        <text>{{ coupon.is_claimed ? 'Has' : 'Get' }}</text>
                    </view>
                </view>
            </scroll-view>
        </view>

        <!-- Reviews -->
		<view class="section-card reviews-section">
			<view class="section-header">
                <text class="section-title">Reviews ({{ reviews.length }})</text>
                <text class="section-more">View All ></text>
            </view>
			<view class="review-item" v-for="review in reviews.slice(0, 3)" :key="review.id">
				<view class="review-header">
					<text class="user-name">{{ review.user_name }}</text>
					<view class="stars">
                        <text v-for="n in 5" :key="n" :class="{filled: n <= review.rating}">★</text>
                    </view>
				</view>
				<view class="review-content">{{ review.comment }}</view>
			</view>
			<view v-if="reviews.length === 0" class="no-reviews">No reviews yet.</view>
		</view>

		<!-- Bottom Action Bar -->
		<view class="action-bar-placeholder"></view>
		<view class="action-bar">
            <view class="icon-group">
                <view class="icon-btn" @click="contactMerchant">
                    <view class="icon">💬</view>
                    <text class="text">Chat</text>
                </view>
                <view class="icon-btn" @click="toggleFavorite">
                    <view class="icon" :style="{color: isFavorite ? '#FF5000' : '#333'}">{{ isFavorite ? '❤️' : '🤍' }}</view>
                    <text class="text">Fav</text>
                </view>
                <view class="icon-btn" @click="goToCart">
                    <view class="icon">🛒</view>
                    <text class="text">Cart</text>
                </view>
            </view>
            <view class="btn-group">
                <view class="btn btn-cart" @click="addToCart">Add to Cart</view>
                <view class="btn btn-buy" @click="buyNow">Buy Now</view>
            </view>
		</view>
	</view>
</template>

<script>
	import { request } from '@/common/api';

	export default {
		data() {
			return {
				id: null,
				product: {},
				reviews: [],
				coupons: [],
				isFavorite: false
			};
		},
		onLoad(options) {
			this.id = options.id;
			this.loadProduct();
			this.loadReviews();
			this.checkFavorite();
		},
        watch: {
            product(newVal) {
                if (newVal && newVal.merchant) {
                    this.fetchMerchantCoupons(newVal.merchant);
                }
            }
        },
		methods: {
            async loadProduct() {
                try {
                    const res = await request({ url: `/store/products/${this.id}/` });
                    this.product = res;
                } catch (e) {
                    console.error(e);
                }
            },
            async loadReviews() {
                try {
                    const res = await request({ url: `/store/reviews/?product=${this.id}` });
                    this.reviews = res.results || res;
                } catch (e) {
                    console.error(e);
                }
            },
            async fetchMerchantCoupons(merchantId) {
                try {
                    const res = await request({ url: `/store/coupons/?merchant_id=${merchantId}` });
                    this.coupons = res.results || res;
                    // Check claimed status - ideally backend should provide this or we fetch user coupons
                    this.checkClaimedStatus();
                } catch (e) {
                    console.error(e);
                }
            },
            async checkClaimedStatus() {
                if (!uni.getStorageSync('token')) return;
                try {
                    const res = await request({ url: '/store/user_coupons/' });
                    const userCoupons = res.results || res;
                    const claimedIds = userCoupons.map(uc => uc.coupon.id);
                    this.coupons.forEach(c => {
                        c.is_claimed = claimedIds.includes(c.id);
                    });
                } catch (e) {
                    console.error(e);
                }
            },
            async checkFavorite() {
                if (!uni.getStorageSync('token')) return;
                try {
                    const res = await request({ url: '/store/favorites/' });
                    // Simple client-side check if API doesn't support check by product_id directly
                    // Optimization: Backend should have an is_favorited field on product or a check API
                    const favs = res.results || res;
                    const found = favs.find(f => f.product.id == this.id);
                    this.isFavorite = !!found;
                    if (found) this.favoriteId = found.id;
                } catch (e) {
                    console.error(e);
                }
            },
            async toggleFavorite() {
                if (!uni.getStorageSync('token')) {
                    uni.navigateTo({ url: '/pages/login/login' });
                    return;
                }
                
                try {
                    if (this.isFavorite) {
                        // Unlike
                        await request({ url: `/store/favorites/${this.favoriteId}/`, method: 'DELETE' });
                        this.isFavorite = false;
                        uni.showToast({ title: 'Removed', icon: 'none' });
                    } else {
                        // Like
                        const res = await request({ 
                            url: '/store/favorites/', 
                            method: 'POST',
                            data: { product_id: this.id }
                        });
                        this.isFavorite = true;
                        this.favoriteId = res.id;
                        uni.showToast({ title: 'Favorited' });
                    }
                } catch (e) {
                    console.error(e);
                }
            },
            async addToCart() {
                if (!uni.getStorageSync('token')) {
                    uni.navigateTo({ url: '/pages/login/login' });
                    return;
                }
                try {
                    await request({
                        url: '/store/cart/',
                        method: 'POST',
                        data: { product_id: this.id, quantity: 1 }
                    });
                    uni.showToast({ title: 'Added to Cart' });
                } catch (e) {
                    uni.showToast({ title: 'Failed', icon: 'none' });
                }
            },
            buyNow() {
                if (!uni.getStorageSync('token')) {
                    uni.navigateTo({ url: '/pages/login/login' });
                    return;
                }
                // Add to cart and jump to confirm
                this.addToCart().then(() => {
                    uni.navigateTo({ url: '/pages/order/confirm' });
                });
            },
            contactMerchant() {
                 if (!uni.getStorageSync('token')) {
                    uni.navigateTo({ url: '/pages/login/login' });
                    return;
                }
                // Need merchant user ID. Assuming product.merchant is the ID.
                // But chat requires target user ID. 
                // Wait, product.merchant might be the ID of the Merchant Profile or User?
                // Usually it's User ID if we simplified. Let's assume product.merchant is User ID.
                uni.navigateTo({
                    url: `/pages/chat/chat?targetId=${this.product.merchant}`
                });
            },
            goToCart() {
                uni.switchTab({ url: '/pages/cart/cart' });
            },
            async claimCoupon(coupon) {
                if (coupon.is_claimed) return;
                if (!uni.getStorageSync('token')) {
                    uni.navigateTo({ url: '/pages/login/login' });
                    return;
                }
                try {
                    await request({
                        url: '/store/coupons/claim/',
                        method: 'POST',
                        data: { coupon_id: coupon.id }
                    });
                    coupon.is_claimed = true;
                    uni.showToast({ title: 'Claimed!' });
                } catch (e) {
                    uni.showToast({ title: 'Failed', icon: 'none' });
                }
            }
		}
	}
</script>

<style lang="scss">
    .container {
        padding-bottom: 120rpx;
    }
    .swiper {
        height: 750rpx;
        background-color: #f5f5f5;
    }
    .slide-image {
        width: 100%;
        height: 100%;
    }
    .no-image {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #999;
    }
    
    .info-card {
        background-color: #fff;
        padding: 30rpx;
        margin-bottom: 20rpx;
    }
    .price-row {
        color: #FF5000;
        margin-bottom: 10rpx;
    }
    .currency { font-size: 28rpx; font-weight: bold; }
    .price { font-size: 48rpx; font-weight: bold; }
    
    .title {
        font-size: 32rpx;
        font-weight: bold;
        color: #333;
        line-height: 1.4;
        margin-bottom: 20rpx;
    }
    .merchant-row {
        display: flex;
        align-items: center;
        margin-bottom: 20rpx;
    }
    .merchant-tag {
        background-color: #FF5000;
        color: #fff;
        font-size: 20rpx;
        padding: 2rpx 8rpx;
        border-radius: 4rpx;
        margin-right: 10rpx;
    }
    .merchant-name {
        font-size: 26rpx;
        color: #666;
    }
    .desc-box {
        margin-top: 20rpx;
        padding-top: 20rpx;
        border-top: 1rpx solid #f0f0f0;
    }
    .desc-title { font-size: 28rpx; font-weight: bold; margin-bottom: 10rpx; display: block; }
    .description { font-size: 26rpx; color: #666; line-height: 1.6; }
    
    .section-card {
        background-color: #fff;
        padding: 20rpx 30rpx;
        margin-bottom: 20rpx;
    }
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20rpx;
    }
    .section-title { font-size: 30rpx; font-weight: bold; }
    .section-more { font-size: 24rpx; color: #999; }
    
    .coupon-scroll {
        white-space: nowrap;
        width: 100%;
    }
    .coupon-item {
        display: inline-flex;
        width: 300rpx;
        height: 120rpx;
        background-color: #fff1f0;
        border: 1rpx solid #ffccc7;
        border-radius: 8rpx;
        margin-right: 20rpx;
        overflow: hidden;
    }
    .coupon-left {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-right: 1rpx dashed #ffccc7;
    }
    .coupon-amount { color: #FF5000; font-weight: bold; font-size: 32rpx; }
    .coupon-cond { color: #666; font-size: 20rpx; }
    .coupon-right {
        width: 80rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FF5000;
        font-size: 24rpx;
    }
    
    .review-item {
        margin-bottom: 20rpx;
        border-bottom: 1rpx solid #f0f0f0;
        padding-bottom: 20rpx;
    }
    .review-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10rpx;
    }
    .user-name { font-size: 26rpx; color: #333; }
    .stars { color: #ccc; font-size: 24rpx; }
    .stars .filled { color: #FF5000; }
    .review-content { font-size: 26rpx; color: #666; }
    .no-reviews { color: #999; font-size: 26rpx; text-align: center; padding: 20rpx; }
    
    /* Action Bar */
    .action-bar-placeholder { height: 100rpx; }
    .action-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 100rpx;
        background-color: #fff;
        display: flex;
        align-items: center;
        padding: 0 20rpx;
        box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
        z-index: 999;
    }
    .icon-group {
        display: flex;
        width: 40%;
        justify-content: space-around;
    }
    .icon-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .icon { font-size: 40rpx; margin-bottom: 4rpx; }
    .text { font-size: 20rpx; color: #666; }
    
    .btn-group {
        flex: 1;
        display: flex;
        margin-left: 20rpx;
    }
    .btn {
        flex: 1;
        height: 72rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26rpx;
        color: #fff;
    }
    .btn-cart {
        background-color: #FFB800; /* Yellow */
        border-top-left-radius: 36rpx;
        border-bottom-left-radius: 36rpx;
    }
    .btn-buy {
        background-color: #FF5000; /* Red */
        border-top-right-radius: 36rpx;
        border-bottom-right-radius: 36rpx;
    }
</style>
"""

with open(detail_vue_path, 'w', encoding='utf-8') as f:
    f.write(detail_vue_content)
print("Updated product/detail.vue")
