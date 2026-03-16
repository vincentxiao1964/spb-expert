<template>
    <view class="container">
        <view class="order-info">
            <text class="label">Order No:</text>
            <text class="val">{{ order.order_no }}</text>
        </view>
        <view class="order-info">
            <text class="label">Amount:</text>
            <text class="val">¥{{ order.total_amount }}</text>
        </view>

        <view class="form-item">
            <text class="title">Reason for Refund</text>
            <textarea v-model="reason" placeholder="Please describe why you want to refund..." class="textarea" />
        </view>

        <view class="form-item">
            <text class="title">Proof Image (Optional)</text>
            <view class="upload-box" @click="chooseImage">
                <image v-if="imagePath" :src="imagePath" mode="aspectFill" class="preview-img"></image>
                <text v-else class="placeholder">+</text>
            </view>
        </view>

        <button class="btn-submit" @click="submitRefund" :disabled="submitting">Submit Request</button>
    </view>
</template>

<script>
    import { request, uploadFile } from '../../common/api.js';

    export default {
        data() {
            return {
                orderId: null,
                order: {},
                reason: '',
                imagePath: '',
                submitting: false
            }
        },
        onLoad(options) {
            this.orderId = options.order_id;
            this.loadOrder();
        },
        methods: {
            async loadOrder() {
                try {
                    const res = await request({ url: `/store/orders/${this.orderId}/` });
                    this.order = res;
                } catch (e) {
                    uni.showToast({ title: 'Failed to load order', icon: 'none' });
                }
            },
            chooseImage() {
                uni.chooseImage({
                    count: 1,
                    success: (res) => {
                        this.imagePath = res.tempFilePaths[0];
                    }
                });
            },
            async submitRefund() {
                if (!this.reason) {
                    uni.showToast({ title: 'Please enter a reason', icon: 'none' });
                    return;
                }

                this.submitting = true;
                try {
                    let url = '/store/refunds/';
                    
                    if (this.imagePath) {
                        const token = uni.getStorageSync('token');
                        uni.uploadFile({
                            url: 'http://127.0.0.1:8000/api/v1' + url,
                            filePath: this.imagePath,
                            name: 'image',
                            header: {
                                'Authorization': 'Bearer ' + token
                            },
                            formData: {
                                'order': this.orderId,
                                'reason': this.reason
                            },
                            success: (res) => {
                                if (res.statusCode === 201) {
                                    uni.showToast({ title: 'Refund Requested' });
                                    setTimeout(() => uni.navigateBack(), 1500);
                                } else {
                                    uni.showToast({ title: 'Failed', icon: 'none' });
                                }
                            },
                            fail: (err) => {
                                uni.showToast({ title: 'Network Error', icon: 'none' });
                            },
                            complete: () => {
                                this.submitting = false;
                            }
                        });
                    } else {
                        await request({
                            url: url,
                            method: 'POST',
                            data: {
                                order: this.orderId,
                                reason: this.reason
                            }
                        });
                        uni.showToast({ title: 'Refund Requested' });
                        setTimeout(() => uni.navigateBack(), 1500);
                        this.submitting = false;
                    }
                    
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Submission Failed', icon: 'none' });
                    this.submitting = false;
                }
            }
        }
    }
</script>

<style>
    .container {
        padding: 30rpx;
    }
    .order-info {
        display: flex;
        justify-content: space-between;
        padding: 20rpx 0;
        border-bottom: 1rpx solid #eee;
    }
    .form-item {
        margin-top: 30rpx;
    }
    .title {
        display: block;
        margin-bottom: 20rpx;
        font-weight: bold;
    }
    .textarea {
        width: 100%;
        height: 200rpx;
        background-color: #f9f9f9;
        padding: 20rpx;
        border-radius: 10rpx;
    }
    .upload-box {
        width: 160rpx;
        height: 160rpx;
        background-color: #eee;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 10rpx;
    }
    .placeholder {
        font-size: 60rpx;
        color: #999;
    }
    .preview-img {
        width: 100%;
        height: 100%;
        border-radius: 10rpx;
    }
    .btn-submit {
        margin-top: 60rpx;
        background-color: #ff5000;
        color: white;
        border-radius: 40rpx;
    }
</style>
