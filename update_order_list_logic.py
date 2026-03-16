
import os

file_path = r'D:\spb-expert11\frontend\src\pages\order\order.vue'

content = r'''<template>
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
                    <text class="order-status">{{ order.statusText || order.status }}</text>
                </view>
                
                <view class="card-body">
                    <view class="product-row" v-for="(item, idx) in order.items" :key="idx">
                        <image :src="item.product_image || '/static/product_placeholder.jpg'" mode="aspectFill" class="p-img"></image>
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
                        <view class="btn btn-primary" v-if="order.status === 'paid'" @click.stop="remindShip(order)">Remind Ship</view>
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
                    4: 'completed'
                }
			}
		},
        onLoad(options) {
            if (options.tab) {
                this.currentTab = parseInt(options.tab);
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
                return this.orders.filter(o => o.status === targetStatus);
            }
        },
        methods: {
            changeTab(index) {
                this.currentTab = index;
            },
            async loadOrders() {
                // Try fetching real data if API is available
                try {
                    const res = await request({ url: '/store/orders/' });
                    if (res) {
                         // Map results to local structure if needed, or use directly
                         this.orders = Array.isArray(res) ? res : (res.results || []);
                         // Ensure statusText is set if missing (or handle in template)
                         return;
                    }
                } catch (e) {
                    console.log('API failed, using mock data');
                }

                // Mock Data for Demo (Fallback)
                const mockOrders = [
                    {
                        id: 'ORD-1718900001',
                        status: 'paid',
                        statusText: 'To Ship',
                        total_amount: '200.00',
                        items: [
                            { product_name: 'Steel Plate', quantity: 1, price: '200.00', product_image: '' }
                        ]
                    },
                    {
                        id: 'ORD-1718900002',
                        status: 'pending',
                        statusText: 'Pending Payment',
                        total_amount: '99.00',
                        items: [
                            { product_name: 'Safety Helmet', quantity: 2, price: '49.50', product_image: '' }
                        ]
                    },
                     {
                        id: 'ORD-1718900003',
                        status: 'shipped',
                        statusText: 'Shipped',
                        total_amount: '1500.00',
                        items: [
                            { product_name: 'Marine Radar', quantity: 1, price: '1500.00', product_image: '' }
                        ]
                    }
                ];
                this.orders = mockOrders;
            },
            goToDetail(order) {
                uni.navigateTo({
                   url: `/pages/order/detail?id=${order.id}`
                });
            },
            async cancelOrder(order) {
                try {
                    await request({ url: `/store/orders/${order.id}/cancel/`, method: 'POST' });
                    uni.showToast({ title: 'Cancelled' });
                    this.loadOrders();
                } catch(e) {
                    uni.showToast({ title: 'Cancelled (Mock)' });
                    order.status = 'cancelled';
                    order.statusText = 'Cancelled';
                }
            },
            payOrder(order) {
                uni.navigateTo({ url: `/pages/order/pay?id=${order.id}` });
            },
            remindShip(order) {
                uni.showToast({ title: 'Reminded Merchant' });
            },
            async confirmOrder(order) {
                try {
                    await request({
                        url: `/store/orders/${order.id}/receive/`,
                        method: 'POST'
                    });
                    uni.showToast({ title: 'Order Confirmed!' });
                    this.loadOrders(); // Refresh
                } catch (e) {
                    // Fallback for demo
                    uni.showToast({ title: 'Confirmed (Mock)', icon: 'success' });
                    // Update local status
                    order.status = 'completed';
                    order.statusText = 'Completed';
                }
            },
            reviewOrder(order) {
                // uni.navigateTo({ url: `/pages/order/review?id=${order.id}` });
                uni.showToast({ title: 'Review feature coming soon', icon: 'none' });
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
        cursor: pointer;
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
        cursor: pointer;
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
    .p-name { font-size: 28rpx; color: #333; margin-bottom: 10rpx; }
    .p-sku { font-size: 24rpx; color: #999; }
    .p-price { font-size: 28rpx; font-weight: bold; color: #333; }
    
    .card-footer {
        border-top: 1rpx solid #f0f0f0;
        padding-top: 20rpx;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
    }
    .total-text { font-size: 26rpx; color: #666; margin-bottom: 20rpx; }
    .total-price { font-size: 32rpx; font-weight: bold; color: #333; margin-left: 10rpx; }
    
    .btn-row { display: flex; }
    .btn {
        padding: 0 30rpx;
        height: 60rpx;
        line-height: 60rpx;
        border-radius: 30rpx;
        font-size: 26rpx;
        margin-left: 20rpx;
        cursor: pointer;
    }
    .btn-default { border: 1rpx solid #ccc; color: #666; }
    .btn-primary { border: 1rpx solid #FF5000; color: #FF5000; }
    
    .empty-tip { text-align: center; padding: 100rpx 0; color: #999; font-size: 28rpx; }
</style>
'''

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated frontend/src/pages/order/order.vue")
