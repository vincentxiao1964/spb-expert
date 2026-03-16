
import os

CONFIRM_VUE_PATH = r"D:\spb-expert11\frontend\pages\order\confirm.vue"

content = """<template>
    <view class="container">
        <!-- Address Section -->
        <view class="address-section" @click="selectAddress">
            <view v-if="selectedAddress" class="has-address">
                <view class="user-info">
                    <text class="name">{{ selectedAddress.recipient_name }}</text>
                    <text class="phone">{{ selectedAddress.phone }}</text>
                </view>
                <view class="addr-info">
                    {{ selectedAddress.province }} {{ selectedAddress.city }} {{ selectedAddress.district }} {{ selectedAddress.detail_address }}
                </view>
            </view>
            <view v-else class="no-address">
                <text>+ Select Shipping Address</text>
            </view>
            <view class="arrow">></view>
        </view>

        <!-- Order Items -->
        <view class="order-items">
            <view class="item" v-for="(item, index) in cartItems" :key="index">
                <view class="item-name">{{ item.product_name || item.product.name }}</view>
                <view class="item-meta">
                    <text class="price">¥{{ item.product_price || item.product.price }}</text>
                    <text class="qty">x{{ item.quantity }}</text>
                </view>
            </view>
        </view>

        <!-- Summary -->
        <view class="summary">
            <view class="row">
                <text>Total Amount</text>
                <text class="price">¥{{ totalPrice }}</text>
            </view>
        </view>

        <!-- Footer -->
        <view class="footer">
            <view class="total">Total: ¥{{ totalPrice }}</view>
            <view class="btn-pay" @click="submitOrder">Place Order</view>
        </view>
    </view>
</template>

<script>
    import { request } from '../../common/api.js';

    export default {
        data() {
            return {
                cartItems: [],
                selectedAddress: null
            }
        },
        onShow() {
            // Re-fetch cart items or load from storage
            // If we came back from Address Select, this.selectedAddress might be set by page stack manipulation
            // But let's check if we need to load cart
            if (this.cartItems.length === 0) {
                this.loadCart();
            }
            // If no address selected, try to load default
            if (!this.selectedAddress) {
                this.loadDefaultAddress();
            }
        },
        computed: {
            totalPrice() {
                return this.cartItems.reduce((sum, item) => {
                    const price = item.product_price || (item.product ? item.product.price : 0);
                    return sum + (parseFloat(price) * item.quantity);
                }, 0).toFixed(2);
            }
        },
        methods: {
            async loadCart() {
                try {
                    // For now, assuming we are checking out the WHOLE cart
                    // Real world: pass selected item IDs
                    const res = await request({ url: '/store/cart/' });
                    this.cartItems = res.items || res; // Handle if serializer returns object or list
                } catch (e) {
                    console.error(e);
                }
            },
            async loadDefaultAddress() {
                try {
                    const res = await request({ url: '/users/addresses/' });
                    if (res && res.length > 0) {
                        const defaultAddr = res.find(a => a.is_default);
                        this.selectedAddress = defaultAddr || res[0];
                    }
                } catch (e) {
                    console.error(e);
                }
            },
            selectAddress() {
                uni.navigateTo({ url: '/pages/address/list?mode=select' });
            },
            async submitOrder() {
                if (!this.selectedAddress) {
                    uni.showToast({ title: 'Please select an address', icon: 'none' });
                    return;
                }

                try {
                    const res = await request({
                        url: '/store/orders/',
                        method: 'POST',
                        data: {
                            address_id: this.selectedAddress.id
                        }
                    });
                    
                    uni.showToast({ title: 'Order Placed!' });
                    // Navigate to Order List or Payment
                    setTimeout(() => {
                        uni.redirectTo({ url: '/pages/order/order' });
                    }, 1500);
                    
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Order Failed', icon: 'none' });
                }
            }
        }
    }
</script>

<style>
    .container { padding-bottom: 120rpx; background: #f5f5f5; min-height: 100vh; }
    .address-section {
        background: #fff; padding: 30rpx; display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20rpx;
    }
    .user-info { font-weight: bold; margin-bottom: 10rpx; }
    .addr-info { color: #666; font-size: 26rpx; }
    .no-address { color: #f00; }
    .order-items { background: #fff; padding: 20rpx; margin-bottom: 20rpx; }
    .item { display: flex; justify-content: space-between; padding: 20rpx 0; border-bottom: 1px solid #eee; }
    .footer {
        position: fixed; bottom: 0; width: 100%; height: 100rpx; background: #fff;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
    }
    .total { padding-left: 30rpx; font-weight: bold; color: #f00; }
    .btn-pay {
        background: #f00; color: #fff; height: 100%; width: 250rpx;
        display: flex; align-items: center; justify-content: center;
    }
</style>
"""

with open(CONFIRM_VUE_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print("Rewrote confirm.vue with correct URL")
