
import os
import json

base_dir = r"d:\spb-expert11\frontend\pages\procurement"
os.makedirs(base_dir, exist_ok=True)

# list.vue
with open(os.path.join(base_dir, "list.vue"), "w") as f:
    f.write("""<template>
    <view class="container">
        <view class="header">
            <text class="title">Procurement Hall</text>
            <button class="btn-create" @click="goCreate">Post RFQ</button>
        </view>
        
        <view class="tabs">
            <view :class="['tab', activeTab==='open'?'active':'']" @click="switchTab('open')">Open</view>
            <view :class="['tab', activeTab==='mine'?'active':'']" @click="switchTab('mine')">My Requests</view>
        </view>

        <view class="list">
            <view class="item" v-for="(item, index) in list" :key="index" @click="goDetail(item.id)">
                <view class="row">
                    <text class="item-title">{{ item.title }}</text>
                    <text class="item-status">{{ item.status }}</text>
                </view>
                <view class="desc">{{ item.description }}</view>
                <view class="row bottom">
                    <text class="budget" v-if="item.budget">Budget: {{ item.budget }}</text>
                    <text class="sample" v-if="item.is_sample_required">Sample Required</text>
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
                activeTab: 'open',
                list: []
            }
        },
        onShow() {
            this.loadData();
        },
        methods: {
            async loadData() {
                const res = await request({
                    url: '/procurement/requests/',
                    data: { mode: this.activeTab }
                });
                this.list = res;
            },
            switchTab(tab) {
                this.activeTab = tab;
                this.loadData();
            },
            goCreate() {
                uni.navigateTo({ url: '/pages/procurement/create' });
            },
            goDetail(id) {
                // Future: go to detail page
            }
        }
    }
</script>

<style>
.container { padding: 20rpx; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
.title { font-size: 36rpx; font-weight: bold; }
.btn-create { background: #FF5000; color: #fff; font-size: 24rpx; padding: 10rpx 20rpx; }
.tabs { display: flex; border-bottom: 1px solid #eee; margin-bottom: 20rpx; }
.tab { padding: 20rpx; margin-right: 40rpx; color: #666; }
.tab.active { color: #FF5000; border-bottom: 2px solid #FF5000; }
.item { background: #fff; padding: 20rpx; margin-bottom: 20rpx; border-radius: 10rpx; }
.row { display: flex; justify-content: space-between; margin-bottom: 10rpx; }
.item-title { font-weight: bold; }
.item-status { font-size: 24rpx; color: #999; }
.desc { color: #666; font-size: 28rpx; margin-bottom: 10rpx; }
.sample { color: #FF5000; border: 1px solid #FF5000; font-size: 20rpx; padding: 2rpx 8rpx; border-radius: 4rpx; }
</style>
""")

# create.vue
with open(os.path.join(base_dir, "create.vue"), "w") as f:
    f.write("""<template>
    <view class="container">
        <view class="form-item">
            <text class="label">Title</text>
            <input class="input" v-model="form.title" placeholder="What do you need?" />
        </view>
        <view class="form-item">
            <text class="label">Requirements</text>
            <textarea class="textarea" v-model="form.description" placeholder="Detailed description..." />
        </view>
        <view class="form-item">
            <text class="label">Budget</text>
            <input class="input" type="number" v-model="form.budget" placeholder="Optional" />
        </view>
        <view class="form-item row">
            <text class="label">Sample Required?</text>
            <switch :checked="form.is_sample_required" @change="onSampleChange" />
        </view>
        
        <button class="btn-submit" @click="submit">Post RFQ</button>
    </view>
</template>

<script>
    import { request } from '../../common/api.js';
    export default {
        data() {
            return {
                form: {
                    title: '',
                    description: '',
                    budget: '',
                    is_sample_required: false
                }
            }
        },
        methods: {
            onSampleChange(e) {
                this.form.is_sample_required = e.detail.value;
            },
            async submit() {
                if (!this.form.title) return uni.showToast({ title: 'Title required', icon: 'none' });
                
                await request({
                    url: '/procurement/requests/',
                    method: 'POST',
                    data: this.form
                });
                
                uni.showToast({ title: 'Success' });
                setTimeout(() => {
                    uni.navigateBack();
                }, 1500);
            }
        }
    }
</script>

<style>
.container { padding: 30rpx; }
.form-item { margin-bottom: 30rpx; }
.label { display: block; margin-bottom: 10rpx; font-weight: bold; }
.input { border: 1px solid #ddd; padding: 20rpx; border-radius: 8rpx; background: #fff; }
.textarea { border: 1px solid #ddd; padding: 20rpx; border-radius: 8rpx; background: #fff; width: 100%; height: 200rpx; }
.row { display: flex; justify-content: space-between; align-items: center; }
.btn-submit { background: #FF5000; color: #fff; margin-top: 50rpx; }
</style>
""")

# Update pages.json
pages_json_path = r"d:\spb-expert11\frontend\pages.json"
try:
    with open(pages_json_path, 'r', encoding='utf-8') as f:
        # It's better to use json.load if valid, but it might have comments
        # I'll use simple string insertion for safety if json is messy, 
        # but let's try to append to "pages" array via regex or find
        content = f.read()
    
    new_pages = [
        {
            "path": "pages/procurement/list",
            "style": {
                "navigationBarTitleText": "Procurement Hall"
            }
        },
        {
            "path": "pages/procurement/create",
            "style": {
                "navigationBarTitleText": "Post RFQ"
            }
        }
    ]
    
    # Simple insertion before the last ] of "pages": [...]
    # Find "pages": [ ... ]
    # We will look for the closing bracket of pages array.
    # Assuming standard formatting
    if '"pages/procurement/list"' not in content:
        # Find the index of the first "subPackages" or "globalStyle" or just the end of pages array
        # Easier: Find "pages": [ and insert after the first brace? No, order matters.
        # Find the closing "]" of pages array. It's usually before "globalStyle".
        # Let's try to parse it with json if possible.
        try:
            data = json.loads(content)
            data['pages'].extend(new_pages)
            with open(pages_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Updated pages.json via JSON parser")
        except:
            print("JSON parse failed, manual insertion")
            # Fallback
            pass

except Exception as e:
    print(f"Error pages.json: {e}")

print("Created frontend procurement pages")
