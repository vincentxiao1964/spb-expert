import os

# 1. coupon_list.vue
coupon_list_content = """<template>
	<view class="container">
		<view class="header">
			<text class="title">Coupon Management</text>
			<view class="btn-add" @click="goCreate">+ Create</view>
		</view>
		
		<view class="coupon-list">
			<view class="coupon-item" v-for="(item, index) in coupons" :key="index">
				<view class="left">
					<view class="value">
						<text v-if="item.discount_type === 'amount'">¥{{ item.discount_value }}</text>
						<text v-else>{{ item.discount_value }}% OFF</text>
					</view>
					<view class="condition">Min spend ¥{{ item.min_spend }}</view>
				</view>
				<view class="right">
					<view class="code">{{ item.code }}</view>
					<view class="date">{{ formatDate(item.start_date) }} - {{ formatDate(item.end_date) }}</view>
					<view class="stock">Claimed: {{ item.claimed_quantity }} / {{ item.total_quantity }}</view>
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
				coupons: []
			}
		},
		onShow() {
			this.loadCoupons();
		},
		methods: {
			loadCoupons() {
				const userInfo = uni.getStorageSync('userInfo');
                // Ensure we have merchant_id. If not, maybe fetch profile first?
                // For now assuming userInfo has it or we can't filter.
                let url = '/store/coupons/';
                if (userInfo && userInfo.merchant_id) {
                    url += '?merchant_id=' + userInfo.merchant_id;
                }
				request(url, 'GET').then(res => {
					this.coupons = res;
				});
			},
			goCreate() {
				uni.navigateTo({
					url: '/pages/merchant/coupon_create'
				});
			},
			formatDate(dateStr) {
				if (!dateStr) return '';
				return dateStr.split('T')[0];
			}
		}
	}
</script>

<style>
	.container { padding: 20rpx; }
	.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
	.title { font-size: 32rpx; font-weight: bold; }
	.btn-add { background-color: #007aff; color: #fff; padding: 10rpx 20rpx; border-radius: 10rpx; }
	
	.coupon-item { display: flex; background-color: #fff; margin-bottom: 20rpx; border-radius: 10rpx; overflow: hidden; box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1); }
	.left { width: 200rpx; background-color: #ff9900; color: #fff; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20rpx; }
	.value { font-size: 40rpx; font-weight: bold; }
	.condition { font-size: 24rpx; }
	.right { flex: 1; padding: 20rpx; display: flex; flex-direction: column; justify-content: space-between; }
	.code { font-weight: bold; font-size: 32rpx; }
	.date { font-size: 24rpx; color: #666; }
	.stock { font-size: 24rpx; color: #999; }
</style>
"""

# 2. coupon_create.vue
coupon_create_content = """<template>
	<view class="container">
		<view class="form-item">
			<text class="label">Code</text>
			<input class="input" v-model="form.code" placeholder="Unique Code" />
		</view>
		<view class="form-item">
			<text class="label">Type</text>
			<radio-group @change="typeChange" class="radio-group">
				<label class="radio"><radio value="amount" checked="true" />Fixed Amount</label>
				<label class="radio"><radio value="percent" />Percentage</label>
			</radio-group>
		</view>
		<view class="form-item">
			<text class="label">Value</text>
			<input class="input" type="number" v-model="form.discount_value" placeholder="Amount or %" />
		</view>
		<view class="form-item">
			<text class="label">Min Spend</text>
			<input class="input" type="number" v-model="form.min_spend" placeholder="0 for no limit" />
		</view>
		<view class="form-item">
			<text class="label">Total Quantity</text>
			<input class="input" type="number" v-model="form.total_quantity" />
		</view>
        <view class="form-item">
            <text class="label">Start Date</text>
            <picker mode="date" :value="form.start_date" @change="bindStartDateChange">
                <view class="uni-input">{{form.start_date || 'Select Date'}}</view>
            </picker>
        </view>
        <view class="form-item">
            <text class="label">End Date</text>
            <picker mode="date" :value="form.end_date" @change="bindEndDateChange">
                <view class="uni-input">{{form.end_date || 'Select Date'}}</view>
            </picker>
        </view>
		
		<button class="btn-submit" @click="submit">Create Coupon</button>
	</view>
</template>

<script>
	import { request } from '../../common/api.js';
	
	export default {
		data() {
			return {
				form: {
					code: '',
					discount_type: 'amount',
					discount_value: '',
					min_spend: 0,
					total_quantity: 100,
                    start_date: '',
                    end_date: ''
				}
			}
		},
		methods: {
			typeChange(e) {
				this.form.discount_type = e.detail.value;
			},
            bindStartDateChange(e) {
                this.form.start_date = e.target.value;
            },
            bindEndDateChange(e) {
                this.form.end_date = e.target.value;
            },
			submit() {
                // Validation
                if (!this.form.code || !this.form.discount_value || !this.form.start_date || !this.form.end_date) {
                    uni.showToast({ title: 'Please fill all fields', icon: 'none' });
                    return;
                }
                
                // Format dates to ISO? API expects DateTime.
                // We append T00:00:00Z for simplicity
                const data = {
                    ...this.form,
                    start_date: this.form.start_date + 'T00:00:00Z',
                    end_date: this.form.end_date + 'T23:59:59Z'
                };
                
				request('/store/coupons/', 'POST', data).then(res => {
					uni.showToast({ title: 'Created Success' });
					setTimeout(() => {
						uni.navigateBack();
					}, 1500);
				}).catch(err => {
                    // Error handling
                });
			}
		}
	}
</script>

<style>
	.container { padding: 30rpx; }
	.form-item { margin-bottom: 30rpx; }
	.label { display: block; margin-bottom: 10rpx; font-weight: bold; }
	.input { border: 1rpx solid #ddd; padding: 20rpx; border-radius: 10rpx; }
	.radio-group { display: flex; gap: 30rpx; }
	.btn-submit { background-color: #007aff; color: #fff; margin-top: 50rpx; }
    .uni-input { border: 1rpx solid #ddd; padding: 20rpx; border-radius: 10rpx; }
</style>
"""

# 3. user_coupon_list.vue (My Coupons)
user_coupon_list_content = """<template>
	<view class="container">
		<view class="tabs">
			<view class="tab" :class="{active: status==='unused'}" @click="switchTab('unused')">Unused</view>
			<view class="tab" :class="{active: status==='used'}" @click="switchTab('used')">Used</view>
		</view>
		
		<view class="coupon-list">
			<view class="coupon-item" v-for="(item, index) in coupons" :key="index">
				<view class="left" :class="{used: status==='used'}">
					<view class="value">
						<text v-if="item.coupon.discount_type === 'amount'">¥{{ item.coupon.discount_value }}</text>
						<text v-else>{{ item.coupon.discount_value }}% OFF</text>
					</view>
					<view class="condition">Min spend ¥{{ item.coupon.min_spend }}</view>
				</view>
				<view class="right">
					<view class="code">{{ item.coupon.code }}</view>
					<view class="date">Valid until {{ formatDate(item.coupon.end_date) }}</view>
                    <view v-if="status==='used'" class="used-mark">USED</view>
				</view>
			</view>
            <view v-if="coupons.length === 0" class="empty">No coupons</view>
		</view>
	</view>
</template>

<script>
	import { request } from '../../common/api.js';
	
	export default {
		data() {
			return {
				status: 'unused',
				coupons: []
			}
		},
		onShow() {
			this.loadCoupons();
		},
		methods: {
			switchTab(status) {
				this.status = status;
				this.loadCoupons();
			},
			loadCoupons() {
				request('/store/my-coupons/?status=' + this.status, 'GET').then(res => {
					this.coupons = res;
				});
			},
			formatDate(dateStr) {
				if (!dateStr) return '';
				return dateStr.split('T')[0];
			}
		}
	}
</script>

<style>
	.container { padding: 20rpx; }
	.tabs { display: flex; background: #fff; margin-bottom: 20rpx; }
	.tab { flex: 1; text-align: center; padding: 20rpx; border-bottom: 2rpx solid transparent; }
	.tab.active { color: #007aff; border-bottom-color: #007aff; }
	
	.coupon-item { display: flex; background-color: #fff; margin-bottom: 20rpx; border-radius: 10rpx; overflow: hidden; box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1); }
	.left { width: 200rpx; background-color: #ff5500; color: #fff; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20rpx; }
    .left.used { background-color: #ccc; }
	.value { font-size: 40rpx; font-weight: bold; }
	.condition { font-size: 24rpx; }
	.right { flex: 1; padding: 20rpx; display: flex; flex-direction: column; justify-content: space-between; position: relative; }
	.code { font-weight: bold; font-size: 32rpx; }
	.date { font-size: 24rpx; color: #666; }
    .used-mark { position: absolute; right: 20rpx; bottom: 20rpx; color: #ccc; font-weight: bold; border: 2rpx solid #ccc; padding: 5rpx 10rpx; transform: rotate(-10deg); }
    .empty { text-align: center; color: #999; margin-top: 50rpx; }
</style>
"""

# Write files
base_dir = r'D:\spb-expert11\frontend\pages'
merchant_dir = os.path.join(base_dir, 'merchant')
user_dir = os.path.join(base_dir, 'user')

with open(os.path.join(merchant_dir, 'coupon_list.vue'), 'w', encoding='utf-8') as f:
    f.write(coupon_list_content)

with open(os.path.join(merchant_dir, 'coupon_create.vue'), 'w', encoding='utf-8') as f:
    f.write(coupon_create_content)

with open(os.path.join(user_dir, 'coupon_list.vue'), 'w', encoding='utf-8') as f:
    f.write(user_coupon_list_content)

print("Created 3 Vue files")
