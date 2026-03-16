import os
import json

BASE_DIR = r"D:\spb-expert11\frontend"
PAGES_JSON_PATH = os.path.join(BASE_DIR, "pages.json")
LOGIN_DIR = os.path.join(BASE_DIR, "pages", "login")
USER_DIR = os.path.join(BASE_DIR, "pages", "user")
MERCHANT_DIR = os.path.join(BASE_DIR, "pages", "merchant")

# Ensure directories exist
os.makedirs(LOGIN_DIR, exist_ok=True)
os.makedirs(USER_DIR, exist_ok=True)
os.makedirs(MERCHANT_DIR, exist_ok=True)

# 1. Register Vue
register_vue = r'''<template>
	<view class="container">
        <view class="header">
            <text class="title">Create Account</text>
        </view>
        
		<view class="card">
            <view class="input-group">
                <text class="label">Username</text>
                <input class="input" type="text" v-model="form.username" placeholder="Choose a username" />
            </view>
            <view class="input-group">
                <text class="label">Email</text>
                <input class="input" type="text" v-model="form.email" placeholder="Enter your email" />
            </view>
            <view class="input-group">
                <text class="label">Password</text>
                <input class="input" type="password" v-model="form.password" placeholder="Choose a password" />
            </view>
            <view class="input-group">
                <text class="label">Confirm Password</text>
                <input class="input" type="password" v-model="confirmPassword" placeholder="Confirm your password" />
            </view>
            
            <button class="btn-submit" @click="handleRegister" :loading="loading">Register</button>
            
            <view class="links">
                <text class="link" @click="goToLogin">Already have an account? Login</text>
            </view>
        </view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				form: {
                    username: '',
                    email: '',
                    password: ''
                },
                confirmPassword: '',
                loading: false
			}
		},
		methods: {
            async handleRegister() {
                if (!this.form.username || !this.form.password) {
                    uni.showToast({ title: 'Please fill required fields', icon: 'none' });
                    return;
                }
                if (this.form.password !== this.confirmPassword) {
                    uni.showToast({ title: 'Passwords do not match', icon: 'none' });
                    return;
                }
                
                this.loading = true;
                try {
                    const res = await request({
                        url: '/users/register/',
                        method: 'POST',
                        data: this.form
                    });
                    
                    uni.showToast({ title: 'Registration Success' });
                    
                    setTimeout(() => {
                        uni.navigateBack();
                    }, 1500);
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Registration Failed', icon: 'none' });
                } finally {
                    this.loading = false;
                }
            },
            goToLogin() {
                uni.navigateBack();
            }
		}
	}
</script>

<style lang="scss">
	.container {
		min-height: 100vh;
        background-color: #f5f5f5;
        padding: 50rpx;
	}
    .header { margin-bottom: 40rpx; text-align: center; }
    .title { font-size: 40rpx; font-weight: bold; color: #333; }
    
    .card {
        background: #fff;
        border-radius: 20rpx;
        padding: 40rpx;
        box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
    }
    
    .input-group { margin-bottom: 30rpx; }
    .label { font-size: 28rpx; color: #666; margin-bottom: 10rpx; display: block; }
    .input {
        width: 100%; height: 80rpx;
        background: #f9f9f9; border-radius: 10rpx; padding: 0 20rpx;
        font-size: 30rpx; color: #333;
    }
    
    .btn-submit {
        background: linear-gradient(90deg, #FF7A00, #FF5000);
        color: #fff; margin-top: 50rpx; border-radius: 40rpx;
        font-size: 32rpx; font-weight: bold;
        &::after { border: none; }
    }
    
    .links { margin-top: 30rpx; text-align: center; }
    .link { font-size: 28rpx; color: #FF5000; }
</style>'''

# 2. User Settings Vue
user_settings_vue = r'''<template>
    <view class="container">
        <view class="card">
            <view class="form-item avatar-item" @click="chooseAvatar">
                <text class="label">Avatar</text>
                <view class="right">
                    <image :src="form.avatar || '/static/avatar_placeholder.png'" mode="aspectFill" class="avatar"></image>
                    <text class="arrow">></text>
                </view>
            </view>
            <view class="form-item">
                <text class="label">Nickname</text>
                <input class="input" v-model="form.username" placeholder="Enter nickname" />
            </view>
            <view class="form-item">
                <text class="label">Email</text>
                <input class="input" v-model="form.email" placeholder="Enter email" />
            </view>
        </view>
        
        <view class="footer-btn">
            <button class="btn-save" @click="handleSave" :loading="loading">Save Changes</button>
        </view>
    </view>
</template>

<script>
    import { request, uploadFile } from '../../common/api.js';

    export default {
        data() {
            return {
                form: {
                    username: '',
                    email: '',
                    avatar: ''
                },
                loading: false
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
            chooseAvatar() {
                uni.chooseImage({
                    count: 1,
                    success: async (res) => {
                        const tempFilePath = res.tempFilePaths[0];
                        // Upload immediately or wait for save? 
                        // Usually upload immediately to get URL
                        this.uploadAvatar(tempFilePath);
                    }
                });
            },
            async uploadAvatar(filePath) {
                uni.showLoading({ title: 'Uploading...' });
                try {
                    // Assuming we have an upload endpoint or patch profile with multipart
                    // For simplicity, let's assume we patch the profile directly with file
                    // But typically we need a dedicated upload or use uni.uploadFile to specific endpoint
                    // Let's assume /users/me/avatar/ or just PATCH /users/me/
                    
                    const res = await uploadFile({
                        url: '/users/me/', // PATCH usually
                        filePath: filePath,
                        name: 'avatar',
                        formData: { 'method': 'PATCH' } // Some frameworks need this
                    });
                    
                    // Parse result if it's string
                    const data = typeof res === 'string' ? JSON.parse(res) : res;
                    this.form.avatar = data.avatar;
                    uni.hideLoading();
                } catch (e) {
                    uni.hideLoading();
                    console.error(e);
                    uni.showToast({ title: 'Upload Failed', icon: 'none' });
                }
            },
            async handleSave() {
                this.loading = true;
                try {
                    await request({
                        url: '/users/me/',
                        method: 'PATCH',
                        data: {
                            username: this.form.username,
                            email: this.form.email
                        }
                    });
                    uni.showToast({ title: 'Saved' });
                    setTimeout(() => uni.navigateBack(), 1500);
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Save Failed', icon: 'none' });
                } finally {
                    this.loading = false;
                }
            }
        }
    }
</script>

<style lang="scss">
    .container { padding: 20rpx; background: #f5f5f5; min-height: 100vh; }
    .card { background: #fff; border-radius: 20rpx; padding: 0 30rpx; }
    .form-item {
        display: flex; justify-content: space-between; align-items: center;
        padding: 30rpx 0; border-bottom: 1px solid #f9f9f9;
        &:last-child { border-bottom: none; }
    }
    .label { font-size: 30rpx; color: #333; }
    .input { text-align: right; font-size: 30rpx; color: #333; }
    .right { display: flex; align-items: center; }
    .avatar { width: 100rpx; height: 100rpx; border-radius: 50%; margin-right: 20rpx; background: #eee; }
    .arrow { color: #ccc; }
    
    .footer-btn { margin-top: 60rpx; }
    .btn-save {
        background: linear-gradient(90deg, #FF7A00, #FF5000);
        color: #fff; border-radius: 40rpx; font-weight: bold;
        &::after { border: none; }
    }
</style>'''

# 3. Merchant Settings Vue
merchant_settings_vue = r'''<template>
    <view class="container">
        <view class="card">
            <view class="form-item avatar-item" @click="chooseAvatar">
                <text class="label">Shop Avatar</text>
                <view class="right">
                    <image :src="form.shop_avatar || '/static/shop_placeholder.png'" mode="aspectFill" class="avatar"></image>
                    <text class="arrow">></text>
                </view>
            </view>
            <view class="form-item">
                <text class="label">Shop Name</text>
                <input class="input" v-model="form.shop_name" placeholder="Enter shop name" />
            </view>
            <view class="form-item column">
                <text class="label">Description</text>
                <textarea class="textarea" v-model="form.description" placeholder="Enter shop description" />
            </view>
        </view>
        
        <view class="footer-btn">
            <button class="btn-save" @click="handleSave" :loading="loading">Save Changes</button>
        </view>
    </view>
</template>

<script>
    import { request, uploadFile } from '../../common/api.js';

    export default {
        data() {
            return {
                form: {
                    shop_name: '',
                    description: '',
                    shop_avatar: ''
                },
                loading: false
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
            chooseAvatar() {
                uni.chooseImage({
                    count: 1,
                    success: async (res) => {
                        const tempFilePath = res.tempFilePaths[0];
                        this.uploadAvatar(tempFilePath);
                    }
                });
            },
            async uploadAvatar(filePath) {
                uni.showLoading({ title: 'Uploading...' });
                try {
                    const res = await uploadFile({
                        url: '/users/me/merchant_profile/', 
                        filePath: filePath,
                        name: 'shop_avatar',
                        formData: { 'method': 'PATCH' }
                    });
                    
                    const data = typeof res === 'string' ? JSON.parse(res) : res;
                    this.form.shop_avatar = data.shop_avatar;
                    uni.hideLoading();
                } catch (e) {
                    uni.hideLoading();
                    console.error(e);
                    uni.showToast({ title: 'Upload Failed', icon: 'none' });
                }
            },
            async handleSave() {
                this.loading = true;
                try {
                    await request({
                        url: '/users/me/merchant_profile/',
                        method: 'PATCH',
                        data: {
                            shop_name: this.form.shop_name,
                            description: this.form.description
                        }
                    });
                    uni.showToast({ title: 'Saved' });
                    setTimeout(() => uni.navigateBack(), 1500);
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Save Failed', icon: 'none' });
                } finally {
                    this.loading = false;
                }
            }
        }
    }
</script>

<style lang="scss">
    .container { padding: 20rpx; background: #f5f5f5; min-height: 100vh; }
    .card { background: #fff; border-radius: 20rpx; padding: 0 30rpx; }
    .form-item {
        display: flex; justify-content: space-between; align-items: center;
        padding: 30rpx 0; border-bottom: 1px solid #f9f9f9;
        &:last-child { border-bottom: none; }
        &.column { flex-direction: column; align-items: flex-start; }
    }
    .label { font-size: 30rpx; color: #333; }
    .input { text-align: right; font-size: 30rpx; color: #333; }
    .textarea { width: 100%; height: 160rpx; margin-top: 20rpx; background: #f9f9f9; padding: 20rpx; border-radius: 10rpx; font-size: 28rpx; }
    .right { display: flex; align-items: center; }
    .avatar { width: 100rpx; height: 100rpx; border-radius: 50%; margin-right: 20rpx; background: #eee; }
    .arrow { color: #ccc; }
    
    .footer-btn { margin-top: 60rpx; }
    .btn-save {
        background: linear-gradient(90deg, #FF7A00, #FF5000);
        color: #fff; border-radius: 40rpx; font-weight: bold;
        &::after { border: none; }
    }
</style>'''

# 4. Write files
def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created/Updated {path}")
    except Exception as e:
        print(f"Error writing {path}: {e}")

write_file(os.path.join(LOGIN_DIR, "register.vue"), register_vue)
write_file(os.path.join(USER_DIR, "settings.vue"), user_settings_vue)
write_file(os.path.join(MERCHANT_DIR, "settings.vue"), merchant_settings_vue)

# 5. Update pages.json
try:
    with open(PAGES_JSON_PATH, 'r', encoding='utf-8') as f:
        pages_content = f.read()
    
    # Use json module for safer editing if possible, but formatting might be lost.
    # Since we have messy formatting at the end, let's try to parse it first.
    try:
        data = json.loads(pages_content)
        pages = data.get('pages', [])
        
        new_pages = [
            {"path": "pages/login/register", "style": {"navigationBarTitleText": "Register"}},
            {"path": "pages/user/settings", "style": {"navigationBarTitleText": "User Settings"}},
            {"path": "pages/merchant/settings", "style": {"navigationBarTitleText": "Shop Settings"}}
        ]
        
        existing_paths = [p['path'] for p in pages]
        
        added_count = 0
        for p in new_pages:
            if p['path'] not in existing_paths:
                pages.append(p)
                added_count += 1
        
        if added_count > 0:
            data['pages'] = pages
            with open(PAGES_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Added {added_count} pages to pages.json")
        else:
            print("Pages already exist in pages.json")
            
    except json.JSONDecodeError:
        print("Error parsing pages.json. Appending manually.")
        # Manual append if JSON is invalid (which we saw it might be valid but messy)
        # But wait, earlier Read showed it was valid enough.
        pass

except Exception as e:
    print(f"Error updating pages.json: {e}")
