import os

# 1. pages/login/login.vue
login_vue_path = r'D:\spb-expert11\frontend\pages\login'
os.makedirs(login_vue_path, exist_ok=True)

login_vue_content = """<template>
	<view class="container">
		<view class="input-group">
            <input class="input" type="text" v-model="username" placeholder="Username" />
        </view>
        <view class="input-group">
            <input class="input" type="password" v-model="password" placeholder="Password" />
        </view>
        <button class="btn-login" @click="handleLogin">Login</button>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				username: '',
                password: ''
			}
		},
		methods: {
            async handleLogin() {
                if (!this.username || !this.password) {
                    uni.showToast({ title: 'Please fill all fields', icon: 'none' });
                    return;
                }
                
                try {
                    const res = await request({
                        url: '/users/login/',
                        method: 'POST',
                        data: {
                            username: this.username,
                            password: this.password
                        }
                    });
                    
                    if (res.access) {
                        uni.setStorageSync('token', res.access);
                        uni.showToast({ title: 'Login Success' });
                        
                        // Navigate back or to user center
                        setTimeout(() => {
                            uni.switchTab({ url: '/pages/user/user' });
                        }, 1000);
                    }
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Login Failed', icon: 'none' });
                }
            }
		}
	}
</script>

<style>
	.container {
		padding: 50rpx;
	}
    .input-group {
        margin-bottom: 30rpx;
        border-bottom: 1px solid #eee;
        padding: 20rpx 0;
    }
    .input {
        width: 100%;
        height: 60rpx;
    }
    .btn-login {
        background-color: #007aff;
        color: #fff;
        margin-top: 50rpx;
    }
</style>
"""

with open(os.path.join(login_vue_path, 'login.vue'), 'w', encoding='utf-8') as f:
    f.write(login_vue_content)
print(f"Created {login_vue_path}\\login.vue")


# 2. Update pages.json to include login page
pages_json_path = r'D:\spb-expert11\frontend\pages.json'
with open(pages_json_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "pages/login/login" not in content:
    # Insert before the first page
    content = content.replace('"pages": [', '"pages": [\n\t\t{\n\t\t\t"path": "pages/login/login",\n\t\t\t"style": {\n\t\t\t\t"navigationBarTitleText": "Login"\n\t\t\t}\n\t\t},')
    with open(pages_json_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated pages.json")


# 3. Update pages/user/user.vue
user_vue_path = r'D:\spb-expert11\frontend\pages\user\user.vue'
user_vue_content = """<template>
	<view class="content">
        <view class="header" v-if="isLoggedIn">
            <view class="avatar">
                <image src="/static/avatar_placeholder.png" mode="aspectFill"></image>
            </view>
            <view class="info">
                <text class="username">User</text>
                <text class="role">Member</text>
            </view>
        </view>
        <view class="header-login" v-else @click="goToLogin">
            <text>Click to Login</text>
        </view>

        <view class="menu-list">
            <view class="menu-item" @click="handleMerchantApply">
                <text>Merchant Application</text>
                <text class="arrow">></text>
            </view>
            <view class="menu-item">
                <text>My Orders</text>
                <text class="arrow">></text>
            </view>
            <view class="menu-item" v-if="isLoggedIn" @click="handleLogout">
                <text>Logout</text>
                <text class="arrow">></text>
            </view>
        </view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				isLoggedIn: false
			}
		},
		onShow() {
            this.checkLogin();
		},
		methods: {
            checkLogin() {
                const token = uni.getStorageSync('token');
                this.isLoggedIn = !!token;
            },
            goToLogin() {
                uni.navigateTo({ url: '/pages/login/login' });
            },
            handleLogout() {
                uni.removeStorageSync('token');
                this.isLoggedIn = false;
                uni.showToast({ title: 'Logged out', icon: 'none' });
            },
            async handleMerchantApply() {
                if (!this.isLoggedIn) {
                    this.goToLogin();
                    return;
                }
                
                try {
                    const res = await request({
                        url: '/users/merchant/apply/',
                        method: 'POST',
                        header: {
                            'Authorization': 'Bearer ' + uni.getStorageSync('token')
                        },
                        data: {
                            company_name: "My New Company", // Simplification for demo
                            business_license: "http://example.com/license.jpg"
                        }
                    });
                    uni.showToast({ title: 'Application Submitted!' });
                } catch (e) {
                    // Already applied
                    uni.showToast({ title: e.data.detail || 'Error', icon: 'none' });
                }
            }
		}
	}
</script>

<style>
    .content {
        background-color: #f8f8f8;
        min-height: 100vh;
    }
    .header {
        background-color: #fff;
        padding: 40rpx;
        display: flex;
        align-items: center;
        margin-bottom: 20rpx;
    }
    .header-login {
        background-color: #fff;
        padding: 60rpx;
        text-align: center;
        font-size: 32rpx;
        font-weight: bold;
        color: #007aff;
        margin-bottom: 20rpx;
    }
    .avatar {
        width: 100rpx;
        height: 100rpx;
        border-radius: 50%;
        background-color: #eee;
        margin-right: 20rpx;
        overflow: hidden;
    }
    .info {
        display: flex;
        flex-direction: column;
    }
    .username {
        font-size: 32rpx;
        font-weight: bold;
    }
    .role {
        font-size: 24rpx;
        color: #999;
    }
    .menu-list {
        background-color: #fff;
    }
    .menu-item {
        padding: 30rpx;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        font-size: 30rpx;
    }
    .arrow {
        color: #ccc;
    }
</style>
"""

with open(user_vue_path, 'w', encoding='utf-8') as f:
    f.write(user_vue_content)
print(f"Updated {user_vue_path}")
