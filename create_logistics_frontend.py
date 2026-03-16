
import os
import json

base_dir = r"d:\spb-expert11\frontend\pages\logistics"
os.makedirs(base_dir, exist_ok=True)

# 1. list.vue
list_vue = """<template>
    <view class="container">
        <view class="header">
            <text class="title">My Shipments</text>
        </view>
        
        <view v-if="loading" class="loading">Loading...</view>
        <view v-else-if="list.length === 0" class="empty">No active shipments</view>
        
        <view class="list">
            <view class="card" v-for="(item, index) in list" :key="index" @click="goDetail(item.id)">
                <view class="row top">
                    <text class="order-no">Order #{{ item.order_no }}</text>
                    <text class="status">{{ item.status }}</text>
                </view>
                <view class="row">
                    <text class="provider" v-if="item.provider_name">{{ item.provider_name }}</text>
                    <text class="tracking" v-if="item.tracking_number">Tracking: {{ item.tracking_number }}</text>
                </view>
                <view class="row bottom">
                    <text class="date">{{ formatDate(item.updated_at) }}</text>
                    <button size="mini" class="btn-track">Track</button>
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
                list: [],
                loading: true
            }
        },
        onShow() {
            this.loadData();
        },
        methods: {
            async loadData() {
                this.loading = true;
                try {
                    const res = await request({ url: '/logistics/shipments/' });
                    this.list = res;
                } catch (e) {
                    console.error(e);
                }
                this.loading = false;
            },
            formatDate(dateStr) {
                return new Date(dateStr).toLocaleDateString();
            },
            goDetail(id) {
                uni.navigateTo({ url: `/pages/logistics/detail?id=${id}` });
            }
        }
    }
</script>

<style>
.container { padding: 20rpx; background: #f5f5f5; min-height: 100vh; }
.header { margin-bottom: 20rpx; }
.title { font-size: 36rpx; font-weight: bold; }
.card { background: #fff; padding: 20rpx; border-radius: 10rpx; margin-bottom: 20rpx; }
.row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10rpx; }
.top { border-bottom: 1px solid #eee; padding-bottom: 10rpx; margin-bottom: 15rpx; }
.order-no { font-weight: bold; }
.status { color: #FF5000; }
.provider { color: #666; font-size: 26rpx; }
.tracking { color: #666; font-size: 26rpx; }
.date { color: #999; font-size: 24rpx; }
.btn-track { background: #FF5000; color: #fff; margin: 0; }
.empty { text-align: center; color: #999; margin-top: 100rpx; }
</style>
"""

with open(os.path.join(base_dir, "list.vue"), "w", encoding="utf-8") as f:
    f.write(list_vue)

# 2. detail.vue
detail_vue = """<template>
    <view class="container">
        <view class="card info" v-if="shipment">
            <view class="row">
                <text class="label">Tracking Number:</text>
                <text class="value">{{ shipment.tracking_number || 'Pending' }}</text>
            </view>
            <view class="row">
                <text class="label">Carrier:</text>
                <text class="value">{{ shipment.provider_name || 'Assigned soon' }}</text>
            </view>
            <view class="row">
                <text class="label">Current Status:</text>
                <text class="value status">{{ shipment.status }}</text>
            </view>
            <view class="row" v-if="shipment.customs_status">
                <text class="label">Customs:</text>
                <text class="value">{{ shipment.customs_status }}</text>
            </view>
        </view>

        <view class="timeline" v-if="timeline.length">
            <view class="timeline-title">Shipment Progress</view>
            <view class="timeline-item" v-for="(item, index) in timeline" :key="index">
                <view class="dot"></view>
                <view class="content">
                    <view class="time">{{ formatDate(item.time) }}</view>
                    <view class="status-text">{{ item.status }}</view>
                    <view class="location">{{ item.location }}</view>
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
                id: null,
                shipment: {},
                timeline: []
            }
        },
        onLoad(options) {
            this.id = options.id;
            this.loadData();
        },
        methods: {
            async loadData() {
                try {
                    const res = await request({ url: `/logistics/shipments/${this.id}/track/` });
                    this.shipment = res.shipment;
                    this.timeline = res.timeline;
                } catch (e) {
                    uni.showToast({ title: 'Load failed', icon: 'none' });
                }
            },
            formatDate(dateStr) {
                if (!dateStr) return '';
                return new Date(dateStr).toLocaleString();
            }
        }
    }
</script>

<style>
.container { padding: 20rpx; background: #f5f5f5; min-height: 100vh; }
.card { background: #fff; padding: 30rpx; border-radius: 12rpx; margin-bottom: 30rpx; }
.row { display: flex; justify-content: space-between; margin-bottom: 20rpx; border-bottom: 1px solid #f9f9f9; padding-bottom: 10rpx; }
.label { color: #666; }
.value { font-weight: bold; }
.status { color: #FF5000; }

.timeline { background: #fff; padding: 30rpx; border-radius: 12rpx; }
.timeline-title { font-weight: bold; font-size: 32rpx; margin-bottom: 30rpx; }
.timeline-item { display: flex; margin-bottom: 40rpx; position: relative; }
.dot { width: 20rpx; height: 20rpx; background: #FF5000; border-radius: 50%; margin-right: 30rpx; margin-top: 10rpx; z-index: 2; }
.timeline-item:not(:last-child)::after {
    content: ''; position: absolute; left: 9rpx; top: 30rpx; bottom: -20rpx; width: 2rpx; background: #eee;
}
.time { color: #999; font-size: 24rpx; margin-bottom: 4rpx; }
.status-text { font-weight: bold; font-size: 28rpx; margin-bottom: 4rpx; }
.location { color: #666; font-size: 26rpx; }
</style>
"""

with open(os.path.join(base_dir, "detail.vue"), "w", encoding="utf-8") as f:
    f.write(detail_vue)

# 3. Update pages.json
pages_json_path = r"d:\spb-expert11\frontend\pages.json"
try:
    with open(pages_json_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '"pages/logistics/list"' not in content:
        data = json.loads(content)
        new_pages = [
            {
                "path": "pages/logistics/list",
                "style": { "navigationBarTitleText": "My Shipments" }
            },
            {
                "path": "pages/logistics/detail",
                "style": { "navigationBarTitleText": "Shipment Tracking" }
            }
        ]
        data['pages'].extend(new_pages)
        with open(pages_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Updated pages.json with logistics pages")
    else:
        print("Logistics pages already in pages.json")

except Exception as e:
    print(f"Error updating pages.json: {e}")

# 4. Update index.vue (Enable Logistics button)
index_path = r"d:\spb-expert11\frontend\pages\index\index.vue"
with open(index_path, 'r', encoding='utf-8') as f:
    index_content = f.read()

# Replace the coming soon toast with actual navigation
old_toast = "uni.showToast({ title: 'Logistics coming soon', icon: 'none' });"
new_nav = "uni.navigateTo({ url: '/pages/logistics/list' });"

if old_toast in index_content:
    index_content = index_content.replace(old_toast, new_nav)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print("Enabled Logistics navigation in index.vue")
else:
    print("Could not find logistics toast in index.vue")

