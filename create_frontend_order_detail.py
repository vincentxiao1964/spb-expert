
import os

file_path = r'd:\spb-expert11\frontend\src\pages\order\detail.vue'

content = """<template>
    <view class="container">
        <!-- Order Status -->
        <view class="status-card">
            <text class="status-text">{{ order.status }}</text>
            <text class="order-no">No: {{ order.order_no }}</text>
        </view>

        <!-- Address -->
        <view class="address-card">
            <view class="user-info">
                <text class="name">{{ order.recipient_name }}</text>
                <text class="phone">{{ order.phone }}</text>
            </view>
            <view class="addr">{{ order.address }}</view>
        </view>

        <!-- Logistics / Shipment -->
        <view class="logistics-card" v-if="order.shipment">
            <view class="l-header">
                <text class="l-title">Logistics Info</text>
                <text class="l-status">{{ order.shipment.status }}</text>
            </view>
            <view class="l-row">
                <text>Carrier: {{ order.shipment.provider_name || 'Unknown' }}</text>
                <text>Track #: {{ order.shipment.tracking_number }}</text>
            </view>
            <view class="l-row" v-if="order.shipment.customs_status">
                <text>Customs: {{ order.shipment.customs_status }}</text>
            </view>
            
            <!-- Timeline -->
            <view class="timeline" v-if="order.shipment.events && order.shipment.events.length">
                <view class="timeline-item" v-for="(event, index) in order.shipment.events" :key="index">
                    <view class="t-dot" :class="{active: index === 0}"></view>
                    <view class="t-content">
                        <view class="t-status">{{ event.status }}</view>
                        <view class="t-desc">{{ event.description }}</view>
                        <view class="t-time">{{ formatDate(event.timestamp) }}</view>
                    </view>
                </view>
            </view>
            <view v-else class="no-events">No tracking events yet.</view>
        </view>

        <!-- Items -->
        <view class="items-card">
            <view class="item" v-for="(item, index) in order.items" :key="index">
                <image :src="item.product_image" class="img" mode="aspectFill"></image>
                <view class="info">
                    <text class="name">{{ item.product_name }}</text>
                    <text class="sku">x{{ item.quantity }}</text>
                    <text class="price">¥{{ item.price }}</text>
                </view>
            </view>
        </view>

        <!-- Summary -->
        <view class="summary-card">
            <view class="row">
                <text>Original Total</text>
                <text>¥{{ order.original_amount }}</text>
            </view>
            <view class="row" v-if="order.coupon_discount > 0">
                <text>Discount</text>
                <text>-¥{{ order.coupon_discount }}</text>
            </view>
            <view class="row total">
                <text>Final Total</text>
                <text class="price">¥{{ order.total_amount }}</text>
            </view>
        </view>
    </view>
</template>

<script>
    import { request } from '../../common/api.js';
    
    export default {
        data() {
            return {
                id: null,
                order: {}
            }
        },
        onLoad(options) {
            this.id = options.id;
            this.loadOrder();
        },
        methods: {
            async loadOrder() {
                try {
                    const res = await request({ url: `/store/orders/${this.id}/` });
                    this.order = res;
                } catch (e) {
                    uni.showToast({ title: 'Load failed', icon: 'none' });
                }
            },
            formatDate(str) {
                if (!str) return '';
                return new Date(str).toLocaleString();
            }
        }
    }
</script>

<style>
    .container { padding: 20rpx; background: #f5f5f5; min-height: 100vh; }
    .status-card, .address-card, .logistics-card, .items-card, .summary-card {
        background: #fff; padding: 20rpx; border-radius: 12rpx; margin-bottom: 20rpx;
    }
    .status-card { background: #FF5000; color: #fff; }
    .status-text { font-size: 36rpx; font-weight: bold; display: block; }
    .order-no { font-size: 24rpx; opacity: 0.9; }
    
    .user-info { font-weight: bold; margin-bottom: 10rpx; font-size: 30rpx; }
    .addr { color: #666; font-size: 26rpx; }
    
    .l-title { font-weight: bold; border-left: 6rpx solid #FF5000; padding-left: 14rpx; margin-bottom: 10rpx; }
    .l-header { display: flex; justify-content: space-between; margin-bottom: 10rpx; }
    .l-status { color: #FF5000; font-weight: bold; }
    .l-row { color: #666; font-size: 26rpx; margin-bottom: 6rpx; }
    
    .timeline { margin-top: 20rpx; padding-left: 20rpx; border-left: 2rpx solid #eee; }
    .timeline-item { position: relative; padding-bottom: 30rpx; padding-left: 30rpx; }
    .t-dot { position: absolute; left: -11rpx; top: 10rpx; width: 20rpx; height: 20rpx; background: #ddd; border-radius: 50%; }
    .t-dot.active { background: #FF5000; box-shadow: 0 0 0 4rpx rgba(255,80,0,0.2); }
    .t-status { font-weight: bold; font-size: 28rpx; }
    .t-desc { color: #666; font-size: 24rpx; margin: 4rpx 0; }
    .t-time { color: #999; font-size: 22rpx; }
    
    .item { display: flex; margin-bottom: 20rpx; }
    .img { width: 140rpx; height: 140rpx; border-radius: 8rpx; margin-right: 20rpx; }
    .info { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .name { font-size: 28rpx; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .sku { color: #999; font-size: 24rpx; }
    .price { color: #FF5000; font-weight: bold; }
    
    .row { display: flex; justify-content: space-between; margin-bottom: 10rpx; font-size: 28rpx; color: #333; }
    .total { border-top: 1px solid #eee; padding-top: 20rpx; margin-top: 10rpx; font-weight: bold; font-size: 32rpx; }
    .total .price { color: #FF5000; }
</style>
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
    print("Successfully created detail.vue")
