import os

# 1. Update common/api.js to include Auth header
api_js_path = r'D:\spb-expert11\frontend\common\api.js'
api_js_content = """const BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const request = (options) => {
	return new Promise((resolve, reject) => {
        // Auto-inject token
        const token = uni.getStorageSync('token');
        const header = options.header || {};
        if (token) {
            header['Authorization'] = 'Bearer ' + token;
        }

		uni.request({
			url: BASE_URL + options.url,
			method: options.method || 'GET',
			data: options.data || {},
            header: header,
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data);
				} else {
                    // Handle 401 Unauthorized -> redirect to login?
                    if (res.statusCode === 401) {
                        uni.removeStorageSync('token');
                        // Optional: Redirect to login if needed, or let the caller handle
                    }
					reject(res);
				}
			},
			fail: (err) => {
				reject(err);
			}
		});
	});
}
"""
with open(api_js_path, 'w', encoding='utf-8') as f:
    f.write(api_js_content)
print(f"Updated {api_js_path}")


# 2. Update pages/index/index.vue (Add to Cart)
index_vue_path = r'D:\spb-expert11\frontend\pages\index\index.vue'
index_vue_content = """<template>
	<view class="container">
		<!-- Search Bar -->
		<view class="search-bar">
			<input type="text" placeholder="Search ships, parts, services..." class="search-input" />
		</view>

		<!-- Banners -->
		<swiper class="swiper" circular indicator-dots autoplay>
			<swiper-item v-for="(item, index) in banners" :key="index">
				<view class="swiper-item">
                    <!-- Placeholder for image -->
                    <view class="banner-placeholder">Banner {{ index + 1 }}</view>
                </view>
			</swiper-item>
		</swiper>

		<!-- Categories -->
		<view class="category-grid">
			<view class="category-item" v-for="(item, index) in categories" :key="index">
				<view class="cat-icon"></view>
				<text>{{ item.name }}</text>
			</view>
		</view>

		<!-- Recommended Products -->
		<view class="section-title">Recommended</view>
		<view class="product-list">
			<view class="product-item" v-for="(item, index) in products" :key="index">
				<view class="product-img"></view>
				<view class="product-info">
					<text class="product-name">{{ item.name }}</text>
					<text class="product-price">¥{{ item.price }}</text>
                    <view class="btn-add-cart" @click="addToCart(item)">+ Cart</view>
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
				banners: [],
				categories: [],
				products: []
			}
		},
		onLoad() {
            this.loadData();
		},
		methods: {
            async loadData() {
                try {
                    const res = await request({ url: '/store/home/' });
                    this.banners = res.banners;
                    this.categories = res.categories;
                    this.products = res.recommended_products;
                } catch (e) {
                    console.error(e);
                }
            },
            async addToCart(product) {
                if (!uni.getStorageSync('token')) {
                    uni.navigateTo({ url: '/pages/login/login' });
                    return;
                }
                
                try {
                    await request({
                        url: '/store/cart/',
                        method: 'POST',
                        data: {
                            product_id: product.id,
                            quantity: 1
                        }
                    });
                    uni.showToast({ title: 'Added to Cart' });
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Failed to add', icon: 'none' });
                }
            }
		}
	}
</script>

<style>
	.container {
		padding: 20rpx;
	}
	.search-bar {
		margin-bottom: 20rpx;
	}
	.search-input {
		background-color: #f5f5f5;
		padding: 15rpx;
		border-radius: 10rpx;
	}
	.swiper {
		height: 300rpx;
		background-color: #eee;
        margin-bottom: 30rpx;
	}
    .swiper-item {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #ddd;
    }
	.category-grid {
		display: flex;
		flex-wrap: wrap;
		margin-bottom: 30rpx;
	}
	.category-item {
		width: 20%;
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-bottom: 20rpx;
	}
	.cat-icon {
		width: 80rpx;
		height: 80rpx;
		background-color: #eee;
		border-radius: 50%;
		margin-bottom: 10rpx;
	}
	.section-title {
		font-size: 32rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
	}
	.product-list {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
	}
	.product-item {
		width: 48%;
		background-color: #fff;
		margin-bottom: 20rpx;
		border-radius: 10rpx;
		overflow: hidden;
        box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
	}
	.product-img {
		height: 200rpx;
		background-color: #eee;
	}
	.product-info {
		padding: 15rpx;
        position: relative;
	}
	.product-name {
		font-size: 28rpx;
		margin-bottom: 10rpx;
		display: block;
	}
	.product-price {
		color: #ff5000;
		font-weight: bold;
	}
    .btn-add-cart {
        position: absolute;
        right: 15rpx;
        bottom: 15rpx;
        background-color: #ff5000;
        color: white;
        padding: 5rpx 15rpx;
        border-radius: 20rpx;
        font-size: 24rpx;
    }
</style>
"""
with open(index_vue_path, 'w', encoding='utf-8') as f:
    f.write(index_vue_content)
print(f"Updated {index_vue_path}")


# 3. Update pages/cart/cart.vue (Full Logic)
cart_vue_path = r'D:\spb-expert11\frontend\pages\cart\cart.vue'
cart_vue_content = """<template>
	<view class="container">
		<view class="cart-list" v-if="cartItems.length > 0">
            <view class="cart-item" v-for="(item, index) in cartItems" :key="index">
                <view class="item-img"></view>
                <view class="item-info">
                    <text class="item-name">{{ item.product_name }}</text>
                    <text class="item-price">¥{{ item.product_price }}</text>
                    <view class="quantity-ctrl">
                        <text class="btn-qty" @click="updateQty(item, -1)">-</text>
                        <text class="qty">{{ item.quantity }}</text>
                        <text class="btn-qty" @click="updateQty(item, 1)">+</text>
                    </view>
                </view>
                <view class="btn-remove" @click="removeItem(item)">x</view>
            </view>
        </view>
        <view class="empty-cart" v-else>
            <text>Your cart is empty</text>
            <button class="btn-go-shop" @click="goShop">Go Shopping</button>
        </view>

        <!-- Bottom Bar -->
        <view class="bottom-bar" v-if="cartItems.length > 0">
            <view class="total-info">
                <text>Total: </text>
                <text class="total-price">¥{{ totalPrice }}</text>
            </view>
            <view class="btn-checkout" @click="checkout">Checkout</view>
        </view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				cartItems: []
			}
		},
		onShow() {
            this.loadCart();
		},
        computed: {
            totalPrice() {
                return this.cartItems.reduce((sum, item) => {
                    return sum + (parseFloat(item.product_price) * item.quantity);
                }, 0).toFixed(2);
            }
        },
		methods: {
            async loadCart() {
                if (!uni.getStorageSync('token')) return;
                try {
                    const res = await request({ url: '/store/cart/' });
                    this.cartItems = res;
                } catch (e) {
                    console.error(e);
                }
            },
            goShop() {
                uni.switchTab({ url: '/pages/index/index' });
            },
            async updateQty(item, change) {
                const newQty = item.quantity + change;
                if (newQty < 1) return;

                try {
                    // Assuming API supports PATCH /store/cart/{id}/
                    // But based on our implementation, we might need to check views.
                    // Let's use the standard detail endpoint if available, or just reuse create/update logic?
                    // Actually, ViewSet standard update is PUT/PATCH on /store/cart/{id}/
                    
                    await request({
                        url: `/store/cart/${item.id}/`,
                        method: 'PATCH',
                        data: { quantity: newQty }
                    });
                    item.quantity = newQty;
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Update failed', icon: 'none' });
                }
            },
            async removeItem(item) {
                try {
                    await request({
                        url: `/store/cart/${item.id}/`,
                        method: 'DELETE'
                    });
                    this.cartItems = this.cartItems.filter(i => i.id !== item.id);
                } catch (e) {
                    console.error(e);
                }
            },
            async checkout() {
                // 1. Get Address (Mocking: fetch list and pick first)
                let addressId = null;
                try {
                    const addresses = await request({ url: '/users/addresses/' });
                    if (addresses && addresses.length > 0) {
                        addressId = addresses[0].id;
                    } else {
                        // Create a default address for testing if none
                        const newAddr = await request({
                            url: '/users/addresses/',
                            method: 'POST',
                            data: {
                                recipient_name: "Test User",
                                phone: "13800000000",
                                province: "Shanghai",
                                city: "Shanghai",
                                district: "Pudong",
                                detail_address: "Test Address 123",
                                is_default: true
                            }
                        });
                        addressId = newAddr.id;
                    }
                } catch (e) {
                    uni.showToast({ title: 'Address Error', icon: 'none' });
                    return;
                }

                // 2. Create Order
                try {
                    const res = await request({
                        url: '/store/orders/',
                        method: 'POST',
                        data: {
                            address_id: addressId
                        }
                    });
                    uni.showToast({ title: 'Order Created!' });
                    this.cartItems = []; // Clear local cart
                    // Navigate to Order List (TODO)
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Checkout Failed', icon: 'none' });
                }
            }
		}
	}
</script>

<style>
	.container {
		padding-bottom: 120rpx;
        background-color: #f8f8f8;
        min-height: 100vh;
	}
    .cart-list {
        padding: 20rpx;
    }
    .cart-item {
        background-color: #fff;
        padding: 20rpx;
        margin-bottom: 20rpx;
        border-radius: 10rpx;
        display: flex;
        align-items: center;
        position: relative;
    }
    .item-img {
        width: 120rpx;
        height: 120rpx;
        background-color: #eee;
        margin-right: 20rpx;
    }
    .item-info {
        flex: 1;
    }
    .item-name {
        font-size: 28rpx;
        margin-bottom: 10rpx;
        display: block;
    }
    .item-price {
        color: #ff5000;
        font-weight: bold;
    }
    .quantity-ctrl {
        display: flex;
        align-items: center;
        margin-top: 10rpx;
    }
    .btn-qty {
        width: 50rpx;
        height: 50rpx;
        background-color: #f5f5f5;
        text-align: center;
        line-height: 50rpx;
        font-size: 32rpx;
    }
    .qty {
        margin: 0 20rpx;
    }
    .btn-remove {
        position: absolute;
        top: 10rpx;
        right: 10rpx;
        color: #999;
        padding: 10rpx;
    }
    .empty-cart {
        text-align: center;
        padding-top: 100rpx;
        color: #999;
    }
    .btn-go-shop {
        margin-top: 40rpx;
        width: 200rpx;
        font-size: 28rpx;
    }
    .bottom-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 100rpx;
        background-color: #fff;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20rpx;
        box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
        /* Adjust for tabbar if needed, but in H5 usually tabbar is separate. 
           In Uni-app, standard tabbar covers bottom. We might need specific window-bottom handling.
           For now, let's assume it sits above tabbar or floats. */
        bottom: var(--window-bottom); 
    }
    .total-info {
        font-size: 32rpx;
    }
    .total-price {
        color: #ff5000;
        font-weight: bold;
    }
    .btn-checkout {
        background-color: #ff5000;
        color: #fff;
        padding: 20rpx 60rpx;
        border-radius: 40rpx;
    }
</style>
"""
with open(cart_vue_path, 'w', encoding='utf-8') as f:
    f.write(cart_vue_content)
print(f"Updated {cart_vue_path}")
