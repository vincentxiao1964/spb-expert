import os

# 1. Update category/category.vue (Split Layout)
category_vue_path = r'D:\spb-expert11\frontend\pages\category\category.vue'
category_vue_content = """<template>
	<view class="container">
		<!-- Left Sidebar -->
        <scroll-view scroll-y class="left-aside">
            <view v-for="(item, index) in categories" :key="item.id" class="f-item" :class="{active: currentId === item.id}" @click="tabtap(item)">
                {{ item.name }}
            </view>
        </scroll-view>

        <!-- Right Content -->
        <scroll-view scroll-y class="right-aside">
            <view class="content-header">
                <text class="content-title">{{ currentName }}</text>
            </view>
            <view class="product-grid" v-if="currentProducts.length > 0">
                <view class="product-item" v-for="(prod, index) in currentProducts" :key="index" @click="goToProduct(prod)">
                    <image :src="prod.image || '/static/logo.png'" mode="aspectFill" class="p-img"></image>
                    <text class="p-name">{{ prod.name }}</text>
                    <text class="p-price">¥{{ prod.price }}</text>
                </view>
            </view>
            <view class="empty-tip" v-else>
                <text>No products in this category</text>
            </view>
        </scroll-view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				categories: [],
                currentId: null,
                currentName: '',
                currentProducts: []
			}
		},
        onLoad() {
            this.loadCategories();
        },
        methods: {
            async loadCategories() {
                try {
                    const res = await request({ url: '/store/categories/' });
                    this.categories = res.results || res;
                    if (this.categories.length > 0) {
                        this.tabtap(this.categories[0]);
                    }
                } catch (e) {
                    console.error(e);
                }
            },
            async tabtap(item) {
                this.currentId = item.id;
                this.currentName = item.name;
                this.loadProducts(item.id);
            },
            async loadProducts(catId) {
                try {
                    // Assuming API supports filtering by category
                    // If not, we might need to filter client side or update API
                    const res = await request({ url: `/store/products/?category=${catId}` });
                    this.currentProducts = res.results || res;
                } catch (e) {
                    console.error(e);
                    this.currentProducts = [];
                }
            },
            goToProduct(item) {
                uni.navigateTo({ url: `/pages/product/detail?id=${item.id}` });
            }
        }
	}
</script>

<style lang="scss">
	page, .container {
		height: 100%;
        background-color: #f5f5f5;
	}
    .container {
        display: flex;
    }
    
    /* Left Sidebar */
    .left-aside {
        width: 200rpx;
        height: 100%;
        background-color: #fff;
    }
    .f-item {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100rpx;
        font-size: 28rpx;
        color: #606266;
        position: relative;
    }
    .f-item.active {
        color: #FF5000;
        background-color: #f5f5f5;
        font-weight: bold;
    }
    .f-item.active:before {
        content: '';
        position: absolute;
        left: 0;
        top: 30rpx;
        bottom: 30rpx;
        width: 8rpx;
        background-color: #FF5000;
        border-radius: 0 4rpx 4rpx 0;
    }
    
    /* Right Content */
    .right-aside {
        flex: 1;
        height: 100%;
        padding: 20rpx;
    }
    .content-header {
        margin-bottom: 20rpx;
    }
    .content-title {
        font-size: 32rpx;
        font-weight: bold;
        color: #333;
    }
    
    .product-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
    }
    .product-item {
        width: 48%;
        background-color: #fff;
        border-radius: 12rpx;
        margin-bottom: 20rpx;
        overflow: hidden;
        padding-bottom: 10rpx;
    }
    .p-img {
        width: 100%;
        height: 200rpx;
        background-color: #eee;
    }
    .p-name {
        font-size: 24rpx;
        color: #333;
        padding: 10rpx;
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .p-price {
        font-size: 28rpx;
        color: #FF5000;
        padding: 0 10rpx;
        font-weight: bold;
    }
    
    .empty-tip {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 400rpx;
        color: #999;
        font-size: 28rpx;
    }
</style>
"""

with open(category_vue_path, 'w', encoding='utf-8') as f:
    f.write(category_vue_content)
print("Updated category/category.vue")

# 2. Update order/order.vue (Tabbed Order List)
order_vue_path = r'D:\spb-expert11\frontend\pages\order\order.vue'
order_vue_content = """<template>
	<view class="container">
        <!-- Tabs -->
		<view class="tabs">
            <view class="tab-item" :class="{active: currentTab === 0}" @click="changeTab(0)">All</view>
            <view class="tab-item" :class="{active: currentTab === 1}" @click="changeTab(1)">Pending</view>
            <view class="tab-item" :class="{active: currentTab === 2}" @click="changeTab(2)">To Ship</view>
            <view class="tab-item" :class="{active: currentTab === 3}" @click="changeTab(3)">To Receive</view>
            <view class="tab-item" :class="{active: currentTab === 4}" @click="changeTab(4)">Review</view>
        </view>
        
        <!-- Order List -->
        <scroll-view scroll-y class="order-list">
            <view class="order-card" v-for="(order, index) in filteredOrders" :key="order.id" @click="goToDetail(order)">
                <view class="card-header">
                    <text class="shop-name">Order #{{ order.id }}</text>
                    <text class="order-status">{{ order.status }}</text>
                </view>
                
                <view class="card-body">
                    <view class="product-row" v-for="(item, idx) in order.items" :key="idx">
                        <image :src="item.product_image || '/static/logo.png'" mode="aspectFill" class="p-img"></image>
                        <view class="p-info">
                            <text class="p-name">{{ item.product_name }}</text>
                            <text class="p-sku">Qty: {{ item.quantity }}</text>
                        </view>
                        <text class="p-price">¥{{ item.price }}</text>
                    </view>
                </view>
                
                <view class="card-footer">
                    <text class="total-text">Total: <text class="total-price">¥{{ order.total_amount }}</text></text>
                    <view class="btn-row">
                        <view class="btn btn-default" v-if="order.status === 'pending'" @click.stop="cancelOrder(order)">Cancel</view>
                        <view class="btn btn-primary" v-if="order.status === 'pending'" @click.stop="payOrder(order)">Pay Now</view>
                        <view class="btn btn-primary" v-if="order.status === 'shipped'" @click.stop="confirmOrder(order)">Confirm</view>
                        <view class="btn btn-default" v-if="order.status === 'completed'" @click.stop="reviewOrder(order)">Review</view>
                    </view>
                </view>
            </view>
            
            <view class="empty-tip" v-if="filteredOrders.length === 0">
                <text>No orders found</text>
            </view>
        </scroll-view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				currentTab: 0,
                orders: [],
                statusMap: {
                    0: null,
                    1: 'pending',
                    2: 'paid', // paid means to ship
                    3: 'shipped',
                    4: 'completed' // review is part of completed or separate? Let's assume completed
                }
			}
		},
        onShow() {
            this.loadOrders();
        },
        computed: {
            filteredOrders() {
                if (this.currentTab === 0) return this.orders;
                const targetStatus = this.statusMap[this.currentTab];
                if (!targetStatus) return this.orders;
                // Note: backend status might be 'paid' for To Ship, 'shipped' for To Receive
                // Adjust logic as needed.
                return this.orders.filter(o => o.status === targetStatus);
            }
        },
        methods: {
            changeTab(index) {
                this.currentTab = index;
            },
            async loadOrders() {
                try {
                    const res = await request({ url: '/store/orders/' });
                    this.orders = res.results || res;
                } catch (e) {
                    console.error(e);
                }
            },
            goToDetail(order) {
                // Navigate to detail
            },
            async cancelOrder(order) {
                try {
                    await request({ url: `/store/orders/${order.id}/cancel/`, method: 'POST' });
                    uni.showToast({ title: 'Cancelled' });
                    this.loadOrders();
                } catch (e) {
                    uni.showToast({ title: 'Failed', icon: 'none' });
                }
            },
            payOrder(order) {
                uni.navigateTo({ url: `/pages/order/pay?id=${order.id}` });
            },
            async confirmOrder(order) {
                try {
                    await request({ url: `/store/orders/${order.id}/receive/`, method: 'POST' });
                    uni.showToast({ title: 'Confirmed' });
                    this.loadOrders();
                } catch (e) {
                    uni.showToast({ title: 'Failed', icon: 'none' });
                }
            },
            reviewOrder(order) {
                uni.navigateTo({ url: `/pages/order/review?id=${order.id}` });
            }
        }
	}
</script>

<style lang="scss">
	.container {
        height: 100vh;
        display: flex;
        flex-direction: column;
        background-color: #f5f5f5;
    }
    
    .tabs {
        display: flex;
        background-color: #fff;
        height: 88rpx;
        align-items: center;
        box-shadow: 0 1rpx 5rpx rgba(0,0,0,0.05);
    }
    .tab-item {
        flex: 1;
        text-align: center;
        font-size: 28rpx;
        color: #333;
        line-height: 88rpx;
        position: relative;
    }
    .tab-item.active {
        color: #FF5000;
        font-weight: bold;
    }
    .tab-item.active:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 20%;
        width: 60%;
        height: 4rpx;
        background-color: #FF5000;
    }
    
    .order-list {
        flex: 1;
        padding: 20rpx;
        box-sizing: border-box;
    }
    
    .order-card {
        background-color: #fff;
        border-radius: 16rpx;
        margin-bottom: 20rpx;
        padding: 20rpx;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20rpx;
        border-bottom: 1rpx solid #f0f0f0;
        padding-bottom: 10rpx;
    }
    .shop-name { font-size: 28rpx; font-weight: bold; color: #333; }
    .order-status { font-size: 26rpx; color: #FF5000; }
    
    .card-body {
        margin-bottom: 20rpx;
    }
    .product-row {
        display: flex;
        margin-bottom: 10rpx;
    }
    .p-img {
        width: 120rpx;
        height: 120rpx;
        border-radius: 8rpx;
        background-color: #f5f5f5;
        margin-right: 20rpx;
    }
    .p-info {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    .p-name { font-size: 26rpx; color: #333; margin-bottom: 10rpx; }
    .p-sku { font-size: 22rpx; color: #999; }
    .p-price { font-size: 28rpx; color: #333; font-weight: bold; }
    
    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1rpx solid #f0f0f0;
        padding-top: 20rpx;
    }
    .total-text { font-size: 26rpx; color: #333; }
    .total-price { font-size: 32rpx; color: #FF5000; font-weight: bold; }
    
    .btn-row {
        display: flex;
    }
    .btn {
        padding: 10rpx 30rpx;
        font-size: 24rpx;
        border-radius: 30rpx;
        margin-left: 20rpx;
    }
    .btn-default {
        border: 1rpx solid #ccc;
        color: #666;
    }
    .btn-primary {
        background-color: #FF5000;
        color: #fff;
        border: 1rpx solid #FF5000;
    }
    
    .empty-tip {
        text-align: center;
        color: #999;
        margin-top: 100rpx;
    }
</style>
"""

with open(order_vue_path, 'w', encoding='utf-8') as f:
    f.write(order_vue_content)
print("Updated order/order.vue")
