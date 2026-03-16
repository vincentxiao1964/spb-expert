<template>
    <view class="container">
        <view class="list">
            <view class="card" v-for="(item, index) in refunds" :key="index">
                <view class="header">
                    <text class="order-no">Order: {{ item.order_no }}</text>
                    <text class="status" :class="item.status">{{ item.status }}</text>
                </view>
                <view class="body">
                    <view class="merchant">Merchant: {{ item.merchant_name }}</view>
                    <view class="products">
                        <text v-for="(p, i) in item.product_names" :key="i">{{ p }} </text>
                    </view>
                    <view class="reason">Reason: {{ item.reason }}</view>
                    <image v-if="item.image" :src="item.image" mode="aspectFit" class="proof-img" @click="previewImage(item.image)"></image>
                </view>
                <view class="footer" v-if="item.merchant_response">
                    <text class="response">Merchant Response: {{ item.merchant_response }}</text>
                </view>
            </view>
            <view v-if="refunds.length === 0" class="empty">No refund requests found.</view>
        </view>
    </view>
</template>

<script>
    import { request } from '../../common/api.js';

    export default {
        data() {
            return {
                refunds: []
            }
        },
        onShow() {
            this.loadRefunds();
        },
        methods: {
            async loadRefunds() {
                try {
                    const res = await request({ url: '/store/refunds/' });
                    this.refunds = res.results || res;
                } catch (e) {
                    console.error(e);
                }
            },
            previewImage(url) {
                uni.previewImage({ urls: [url] });
            }
        }
    }
</script>

<style>
    .container { padding: 20rpx; background-color: #f5f5f5; min-height: 100vh; }
    .card { background: #fff; padding: 20rpx; margin-bottom: 20rpx; border-radius: 10rpx; }
    .header { display: flex; justify-content: space-between; border-bottom: 1rpx solid #eee; padding-bottom: 10rpx; margin-bottom: 10rpx; }
    .status { font-weight: bold; }
    .status.pending { color: #ff9900; }
    .status.approved { color: #00cc00; }
    .status.rejected { color: #ff0000; }
    .merchant { font-size: 26rpx; color: #666; margin-bottom: 6rpx; }
    .products { color: #333; font-weight: bold; margin-bottom: 10rpx; }
    .reason { color: #666; margin-bottom: 10rpx; }
    .proof-img { width: 100rpx; height: 100rpx; background: #eee; border-radius: 8rpx; }
    .response { color: #666; font-size: 24rpx; margin-top: 10rpx; display: block; background: #f9f9f9; padding: 10rpx; border-radius: 4rpx;}
    .empty { text-align: center; padding: 50rpx; color: #999; }
</style>
