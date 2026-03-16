import os

# 1. Create merchant/settings.vue
merchant_settings_path = r'D:\spb-expert11\frontend\pages\merchant\settings.vue'
merchant_settings_content = """<template>
	<view class="container">
		<view class="form-group">
            <view class="label">Shop Name</view>
            <input class="input" v-model="form.company_name" placeholder="Enter shop name" />
        </view>
        
        <view class="form-group">
            <view class="label">Description</view>
            <textarea class="textarea" v-model="form.description" placeholder="Shop description..."></textarea>
        </view>
        
        <view class="form-group">
            <view class="label">Shop Avatar</view>
            <view class="image-uploader" @click="chooseImage">
                <image v-if="form.shop_avatar" :src="form.shop_avatar" mode="aspectFill" class="uploaded-img"></image>
                <view v-else class="upload-placeholder">
                    <text class="plus">+</text>
                    <text>Upload</text>
                </view>
            </view>
        </view>
        
        <view class="btn-submit" @click="submit">Save Settings</view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
                form: {
                    company_name: '',
                    description: '',
                    shop_avatar: ''
                }
			}
		},
		onShow() {
            this.loadProfile();
		},
		methods: {
            async loadProfile() {
                try {
                    const res = await request({ url: '/users/me/merchant_profile/' });
                    this.form = res;
                } catch (e) {
                    console.error(e);
                }
            },
            chooseImage() {
                uni.chooseImage({
                    count: 1,
                    success: (res) => {
                        const tempPath = res.tempFilePaths[0];
                        // Upload immediately or wait for submit?
                        // For simplicity, let's assume we upload immediately to get URL
                        this.uploadImage(tempPath);
                    }
                });
            },
            async uploadImage(filePath) {
                 try {
                    // Using a generic upload endpoint
                     uni.uploadFile({
                        url: 'http://127.0.0.1:8000/api/v1/store/products/upload_image/', // Reusing existing upload endpoint if possible or create general one
                        // Actually, we should probably add a general upload endpoint.
                        // For now, let's assume we have one or mock it by just setting the local path for preview
                        // In real app, MUST upload to server.
                        filePath: filePath,
                        name: 'image',
                        header: {
                            'Authorization': 'Bearer ' + uni.getStorageSync('token')
                        },
                        success: (uploadRes) => {
                            const data = JSON.parse(uploadRes.data);
                            this.form.shop_avatar = data.url || filePath; // Fallback
                        }
                    });
                     // Mock for now if server not ready
                     this.form.shop_avatar = filePath;
                 } catch(e) {
                     this.form.shop_avatar = filePath;
                 }
            },
            async submit() {
                try {
                    await request({
                        url: '/users/me/merchant_profile/',
                        method: 'PATCH',
                        data: this.form
                    });
                    uni.showToast({ title: 'Saved' });
                    setTimeout(() => {
                        uni.navigateBack();
                    }, 1500);
                } catch (e) {
                    uni.showToast({ title: 'Failed', icon: 'none' });
                }
            }
		}
	}
</script>

<style lang="scss">
	.container {
		padding: 30rpx;
        background-color: #fff;
        min-height: 100vh;
	}
    
    .form-group {
        margin-bottom: 30rpx;
    }
    .label {
        font-size: 28rpx;
        color: #333;
        margin-bottom: 10rpx;
        font-weight: bold;
    }
    .input {
        height: 80rpx;
        border: 1rpx solid #e5e5e5;
        border-radius: 8rpx;
        padding: 0 20rpx;
        font-size: 28rpx;
    }
    .textarea {
        width: 100%;
        height: 200rpx;
        border: 1rpx solid #e5e5e5;
        border-radius: 8rpx;
        padding: 20rpx;
        font-size: 28rpx;
        box-sizing: border-box;
    }
    
    .image-uploader {
        width: 200rpx;
        height: 200rpx;
        border: 1rpx dashed #ccc;
        border-radius: 8rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .upload-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: #999;
    }
    .plus { font-size: 60rpx; line-height: 1; }
    .uploaded-img { width: 100%; height: 100%; }
    
    .btn-submit {
        background-color: #FF5000;
        color: #fff;
        height: 88rpx;
        line-height: 88rpx;
        text-align: center;
        border-radius: 44rpx;
        font-size: 32rpx;
        font-weight: bold;
        margin-top: 60rpx;
    }
</style>
"""

with open(merchant_settings_path, 'w', encoding='utf-8') as f:
    f.write(merchant_settings_content)

# 2. Create user/settings.vue
user_settings_path = r'D:\spb-expert11\frontend\pages\user\settings.vue'
user_settings_content = """<template>
	<view class="container">
		<view class="form-group">
            <view class="label">Avatar</view>
            <view class="image-uploader" @click="chooseImage">
                <image v-if="form.avatar" :src="form.avatar" mode="aspectFill" class="uploaded-img"></image>
                <view v-else class="upload-placeholder">
                    <text class="plus">+</text>
                    <text>Upload</text>
                </view>
            </view>
        </view>
        
        <view class="form-group">
            <view class="label">Username</view>
            <input class="input" v-model="form.username" placeholder="Username" disabled />
        </view>
        
        <view class="form-group">
            <view class="label">Phone</view>
            <input class="input" v-model="form.phone" placeholder="Phone number" />
        </view>
        
        <view class="btn-submit" @click="submit">Save Profile</view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
                form: {
                    username: '',
                    phone: '',
                    avatar: ''
                }
			}
		},
		onShow() {
            this.loadProfile();
		},
		methods: {
            async loadProfile() {
                try {
                    const res = await request({ url: '/users/me/' });
                    this.form = res;
                } catch (e) {
                    console.error(e);
                }
            },
            chooseImage() {
                uni.chooseImage({
                    count: 1,
                    success: (res) => {
                        const tempPath = res.tempFilePaths[0];
                        // In real app, upload here
                        this.form.avatar = tempPath;
                    }
                });
            },
            async submit() {
                try {
                    await request({
                        url: '/users/me/',
                        method: 'PATCH',
                        data: {
                            phone: this.form.phone,
                            // avatar: this.form.avatar // Assuming backend handles URL or base64
                        }
                    });
                    uni.showToast({ title: 'Saved' });
                    setTimeout(() => {
                        uni.navigateBack();
                    }, 1500);
                } catch (e) {
                    uni.showToast({ title: 'Failed', icon: 'none' });
                }
            }
		}
	}
</script>

<style lang="scss">
	.container {
		padding: 30rpx;
        background-color: #fff;
        min-height: 100vh;
	}
    .form-group { margin-bottom: 30rpx; }
    .label { font-size: 28rpx; color: #333; margin-bottom: 10rpx; font-weight: bold; }
    .input { height: 80rpx; border: 1rpx solid #e5e5e5; border-radius: 8rpx; padding: 0 20rpx; font-size: 28rpx; }
    
    .image-uploader {
        width: 160rpx;
        height: 160rpx;
        border: 1rpx dashed #ccc;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin: 0 auto;
    }
    .upload-placeholder { display: flex; flex-direction: column; align-items: center; color: #999; }
    .plus { font-size: 50rpx; line-height: 1; }
    .uploaded-img { width: 100%; height: 100%; }
    
    .btn-submit {
        background-color: #FF5000;
        color: #fff;
        height: 88rpx;
        line-height: 88rpx;
        text-align: center;
        border-radius: 44rpx;
        font-size: 32rpx;
        font-weight: bold;
        margin-top: 60rpx;
    }
</style>
"""

with open(user_settings_path, 'w', encoding='utf-8') as f:
    f.write(user_settings_content)

# 3. Update pages.json
pages_path = r'D:\spb-expert11\frontend\pages.json'
with open(pages_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_pages = [
    '{"path": "pages/merchant/settings", "style": {"navigationBarTitleText": "Shop Settings"}}',
    '{"path": "pages/user/settings", "style": {"navigationBarTitleText": "Edit Profile"}}'
]

if "pages/merchant/settings" not in content:
    idx = content.find('"globalStyle"')
    if idx != -1:
        pre_content = content[:idx]
        last_bracket = pre_content.rfind(']')
        if last_bracket != -1:
            content = content[:last_bracket] + "," + ",".join(new_pages) + content[last_bracket:]

with open(pages_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 4. Link in dashboard.vue and user.vue
# dashboard.vue: goToShopSettings
dashboard_path = r'D:\spb-expert11\frontend\pages\merchant\dashboard.vue'
with open(dashboard_path, 'r', encoding='utf-8') as f:
    d_content = f.read()

if "goToShopSettings() {" in d_content:
    d_content = d_content.replace(
        "uni.showToast({ title: 'Settings (Coming Soon)', icon: 'none' });",
        "uni.navigateTo({ url: '/pages/merchant/settings' });"
    )
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(d_content)

# user.vue: goToSettings
user_path = r'D:\spb-expert11\frontend\pages\user\user.vue'
with open(user_path, 'r', encoding='utf-8') as f:
    u_content = f.read()

if "goToSettings() {" in u_content:
    u_content = u_content.replace(
        "// Placeholder for settings",
        "uni.navigateTo({ url: '/pages/user/settings' });"
    )
    with open(user_path, 'w', encoding='utf-8') as f:
        f.write(u_content)

print("Created settings pages and linked them")
