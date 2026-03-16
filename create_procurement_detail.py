
import os
import json

base_dir = r"d:\spb-expert11\frontend\pages\procurement"
os.makedirs(base_dir, exist_ok=True)

# detail.vue
detail_content = """<template>
    <view class="container">
        <view v-if="item" class="card">
            <view class="header">
                <text class="title">{{ item.title }}</text>
                <text class="status">{{ item.status }}</text>
            </view>
            <view class="meta">
                <text>Budget: {{ item.budget || 'Negotiable' }}</text>
                <text>Deadline: {{ formatDate(item.deadline) }}</text>
            </view>
            <view class="desc">
                <text class="label">Requirements:</text>
                <text class="content">{{ item.description }}</text>
            </view>
            <view class="sample-badge" v-if="item.is_sample_required">
                Sample Required
            </view>
            
            <view class="owner-info">
                <image :src="item.user_avatar || '/static/default-avatar.png'" class="avatar"></image>
                <text class="username">{{ item.user_name }}</text>
            </view>
        </view>

        <!-- For Supplier: Quote Form -->
        <view v-if="!isOwner && item.status === 'open' && !myQuotation" class="card quote-form">
            <view class="section-title">Submit Quotation</view>
            <input class="input" type="number" v-model="quoteForm.price" placeholder="Your Price" />
            <textarea class="textarea" v-model="quoteForm.message" placeholder="Message to buyer (e.g. delivery time, specs)" />
            <view class="row">
                <text>Sample Provided?</text>
                <switch :checked="quoteForm.is_sample_provided" @change="onSampleChange" />
            </view>
            <button class="btn-primary" @click="submitQuote">Submit Quote</button>
        </view>

        <!-- For Supplier: My Quote Status -->
        <view v-if="myQuotation" class="card my-quote">
            <view class="section-title">Your Quotation</view>
            <view class="row"><text>Price:</text><text>{{ myQuotation.price }}</text></view>
            <view class="row"><text>Status:</text><text class="status-tag">{{ myQuotation.status }}</text></view>
            <view class="msg">{{ myQuotation.message }}</view>
        </view>

        <!-- For Buyer: Received Quotations -->
        <view v-if="isOwner && item.quotations && item.quotations.length" class="card list">
            <view class="section-title">Received Quotations ({{ item.quotations.length }})</view>
            <view v-for="(q, index) in item.quotations" :key="index" class="quote-item">
                <view class="q-header">
                    <text class="q-supplier">{{ q.supplier_name }}</text>
                    <text class="q-price">{{ q.price }}</text>
                </view>
                <view class="q-msg">{{ q.message }}</view>
                <view class="q-status">Status: {{ q.status }}</view>
                <view class="q-actions" v-if="q.status === 'pending'">
                    <!-- Future: Accept/Reject buttons -->
                    <button size="mini" @click="handleQuote(q.id, 'accepted')">Accept</button>
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
                item: {},
                quoteForm: {
                    price: '',
                    message: '',
                    is_sample_provided: false
                },
                currentUser: null
            }
        },
        onLoad(options) {
            this.id = options.id;
            this.loadData();
            // Get current user info (simplified, assuming stored or fetched)
            // Ideally should fetch /users/me/ to get ID to compare with item.user
            this.loadCurrentUser();
        },
        computed: {
            isOwner() {
                // This is a loose check. Better to check IDs. 
                // item.user is the ID of the owner. 
                return this.currentUser && this.item.user === this.currentUser.id;
            },
            myQuotation() {
                return this.item.my_quotation;
            }
        },
        methods: {
            async loadCurrentUser() {
                try {
                    const res = await request({ url: '/users/me/' });
                    this.currentUser = res;
                } catch(e) {}
            },
            async loadData() {
                const res = await request({
                    url: `/procurement/requests/${this.id}/`
                });
                this.item = res;
            },
            formatDate(dateStr) {
                if (!dateStr) return 'No Deadline';
                return new Date(dateStr).toLocaleDateString();
            },
            onSampleChange(e) {
                this.quoteForm.is_sample_provided = e.detail.value;
            },
            async submitQuote() {
                if (!this.quoteForm.price) return uni.showToast({ title: 'Price required', icon: 'none' });
                
                try {
                    await request({
                        url: `/procurement/requests/${this.id}/quote/`,
                        method: 'POST',
                        data: this.quoteForm
                    });
                    uni.showToast({ title: 'Quote Sent' });
                    this.loadData(); // Refresh to show my quote
                } catch (e) {
                    uni.showToast({ title: e.data?.detail || 'Failed', icon: 'none' });
                }
            },
            async handleQuote(quoteId, status) {
                // Implement accept logic
                uni.showToast({ title: 'Feature coming soon', icon: 'none' });
            }
        }
    }
</script>

<style>
.container { padding: 20rpx; background: #f5f5f5; min-height: 100vh; }
.card { background: #fff; padding: 30rpx; border-radius: 12rpx; margin-bottom: 20rpx; }
.header { display: flex; justify-content: space-between; margin-bottom: 20rpx; border-bottom: 1px solid #eee; padding-bottom: 20rpx; }
.title { font-size: 36rpx; font-weight: bold; }
.status { color: #FF5000; font-weight: bold; }
.meta { display: flex; gap: 30rpx; color: #666; font-size: 26rpx; margin-bottom: 20rpx; }
.label { font-weight: bold; display: block; margin-bottom: 10rpx; }
.content { color: #333; line-height: 1.5; }
.sample-badge { display: inline-block; background: #fff0e6; color: #FF5000; padding: 6rpx 12rpx; border-radius: 4rpx; font-size: 24rpx; margin-top: 20rpx; }
.owner-info { display: flex; align-items: center; margin-top: 30rpx; border-top: 1px solid #eee; padding-top: 20rpx; }
.avatar { width: 60rpx; height: 60rpx; border-radius: 50%; margin-right: 20rpx; }

.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 20rpx; border-left: 8rpx solid #FF5000; padding-left: 20rpx; }
.input, .textarea { background: #f9f9f9; padding: 20rpx; border-radius: 8rpx; margin-bottom: 20rpx; width: 100%; box-sizing: border-box; }
.textarea { height: 160rpx; }
.btn-primary { background: #FF5000; color: #fff; margin-top: 20rpx; }

.quote-item { border-bottom: 1px solid #f0f0f0; padding: 20rpx 0; }
.q-header { display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 10rpx; }
.q-price { color: #FF5000; }
.q-msg { color: #666; font-size: 28rpx; }
</style>
"""

with open(os.path.join(base_dir, "detail.vue"), "w", encoding="utf-8") as f:
    f.write(detail_content)


# Update pages.json to include detail page
pages_json_path = r"d:\spb-expert11\frontend\pages.json"
try:
    with open(pages_json_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '"pages/procurement/detail"' not in content:
        # Use simple insertion again as it worked or we want to be safe
        # Find the closing bracket of pages array
        # Just insert it before "pages/procurement/list" if it exists, or append
        # Let's try json manipulation which is safer
        data = json.loads(content)
        new_page = {
            "path": "pages/procurement/detail",
            "style": {
                "navigationBarTitleText": "Request Details"
            }
        }
        # Check if already exists
        exists = any(p['path'] == 'pages/procurement/detail' for p in data['pages'])
        if not exists:
            data['pages'].append(new_page)
            with open(pages_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Added detail page to pages.json")
        else:
            print("Detail page already in pages.json")

except Exception as e:
    print(f"Error updating pages.json: {e}")

print("Created procurement detail page")
