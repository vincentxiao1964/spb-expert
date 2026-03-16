
import os

file_path = r'd:\spb-expert11\frontend\src\pages\login\login.vue'

new_content = """<template>
	<view class="container">
        <!-- Background Image -->
        <image class="bg-image" src="/static/login_bg.jpg" mode="aspectFill"></image>
        <view class="bg-overlay"></view>
        
        <!-- Live Ticker / Prosperity Stats -->
        <view class="ticker-bar">
            <text class="ticker-text">🚀 Live: 12,450 Ships Listed | 💰 Today's Volume: $45M | 🌍 85 Countries Connected</text>
        </view>

        <!-- Logo Area -->
        <view class="header">
            <image src="/static/logo.png" mode="aspectFit" class="logo"></image>
            <view class="header-text">
                <text class="title">Marine Mall</text>
                <text class="subtitle">Global Maritime Trading Hub</text>
            </view>
        </view>
        
		<view class="login-card glass-effect">
            <!-- Tabs -->
            <view class="tabs">
                <view class="tab-item" :class="{active: method==='pwd'}" @click="method='pwd'">
                    <text class="tab-text">Password</text>
                    <view class="tab-line" v-if="method==='pwd'"></view>
                </view>
                <view class="tab-item" :class="{active: method==='sms'}" @click="method='sms'">
                    <text class="tab-text">SMS Login</text>
                    <view class="tab-line" v-if="method==='sms'"></view>
                </view>
            </view>
            
            <!-- Password Form -->
            <view class="form-area" v-if="method==='pwd'">
                <view class="input-item">
                    <text class="input-icon">👤</text>
                    <input class="input" type="text" v-model="username" placeholder="Username / Email / Mobile" placeholder-class="ph-color" />
                </view>
                <view class="input-item">
                    <text class="input-icon">🔒</text>
                    <input class="input" type="password" v-model="password" placeholder="Enter Password" placeholder-class="ph-color" @confirm="handleLogin" />
                </view>
            </view>

            <!-- SMS Form -->
            <view class="form-area" v-else>
                <view class="input-item">
                    <text class="input-icon">📱</text>
                    <input class="input" type="number" v-model="mobile" placeholder="Mobile Number" placeholder-class="ph-color" maxlength="11" />
                </view>
                <view class="input-item code-item">
                    <text class="input-icon">🛡️</text>
                    <input class="input" type="number" v-model="code" placeholder="Verification Code" placeholder-class="ph-color" maxlength="6" />
                    <text class="code-btn" :class="{disabled: codeTimer > 0}" @click="sendCode">
                        {{ codeTimer > 0 ? codeTimer + 's' : 'Get Code' }}
                    </text>
                </view>
            </view>
            
            <button class="btn-login" @click="handleLogin" :loading="loading">Login</button>
            
            <view class="links">
                <text class="link highlight" @click="goToRegister">Register Free</text>
                <text class="divider">|</text>
                <text class="link">Forgot Password?</text>
            </view>
            
            <!-- Guest Mode -->
            <view class="guest-entry" @click="goHome">
                <text>Just Browsing? Go to Market ></text>
            </view>
        </view>
        
        <view class="footer">
            <text class="copyright">Trusted by 50,000+ Maritime Professionals</text>
        </view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
                method: 'pwd', // pwd | sms
				username: '',
                password: '',
                mobile: '',
                code: '',
                codeTimer: 0,
                loading: false
			}
		},
		methods: {
            goHome() {
                uni.switchTab({ url: '/pages/index/index' });
            },
            sendCode() {
                if (this.codeTimer > 0) return;
                if (!this.mobile || this.mobile.length !== 11) {
                    uni.showToast({ title: 'Invalid Mobile Number', icon: 'none' });
                    return;
                }
                
                // Mock Send Code
                uni.showLoading({ title: 'Sending...' });
                setTimeout(() => {
                    uni.hideLoading();
                    uni.showToast({ title: 'Code Sent: 123456', icon: 'none' });
                    this.codeTimer = 60;
                    let timer = setInterval(() => {
                        this.codeTimer--;
                        if (this.codeTimer <= 0) clearInterval(timer);
                    }, 1000);
                }, 1000);
            },
            async handleLogin() {
                if (this.method === 'pwd') {
                    if (!this.username || !this.password) {
                        uni.showToast({ title: 'Please fill all fields', icon: 'none' });
                        return;
                    }
                } else {
                    if (!this.mobile || !this.code) {
                        uni.showToast({ title: 'Please fill all fields', icon: 'none' });
                        return;
                    }
                    if (this.code !== '123456') {
                        uni.showToast({ title: 'Invalid Code', icon: 'none' });
                        return;
                    }
                }
                
                this.loading = true;
                try {
                    let res;
                    if (this.method === 'pwd') {
                        res = await request({
                            url: '/users/login/',
                            method: 'POST',
                            data: {
                                username: this.username,
                                password: this.password
                            }
                        });
                    } else {
                        // Mock SMS Login success
                        await new Promise(r => setTimeout(r, 1000));
                        res = {
                            access: 'mock_sms_token_' + Date.now(),
                            user: { username: 'MobileUser_' + this.mobile.slice(-4) }
                        };
                    }
                    
                    if (res.access) {
                        uni.setStorageSync('token', res.access);
                        uni.showToast({ title: 'Login Success' });
                        
                        if (this.method === 'pwd') {
                            try {
                                const userRes = await request({ url: '/users/me/' });
                                uni.setStorageSync('userInfo', userRes);
                            } catch(e) {}
                        } else {
                             uni.setStorageSync('userInfo', res.user || {username: 'User'});
                        }

                        setTimeout(() => {
                            uni.switchTab({ url: '/pages/index/index' });
                        }, 1000);
                    }
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Login Failed', icon: 'none' });
                } finally {
                    this.loading = false;
                }
            },
            goToRegister() {
                uni.navigateTo({ url: '/pages/login/register' });
            }
		}
	}
</script>

<style lang="scss">
	.container {
		min-height: 100vh;
        display: flex; flex-direction: column; align-items: center;
        padding: 50rpx 40rpx;
        position: relative;
        overflow: hidden;
	}
    
    /* Background */
    .bg-image {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -2;
        background-color: #1a237e; /* Fallback deep blue */
    }
    .bg-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1;
        background: rgba(0,0,0,0.5); /* Darken bg for readability */
        backdrop-filter: blur(3px);
    }
    
    /* Ticker */
    .ticker-bar {
        position: absolute; top: 60rpx; width: 100%; 
        background: rgba(255, 80, 0, 0.8); padding: 10rpx 0;
        overflow: hidden; white-space: nowrap;
    }
    .ticker-text {
        color: #fff; font-size: 24rpx; font-weight: bold;
        animation: ticker 15s linear infinite; display: inline-block; padding-left: 100%;
    }
    @keyframes ticker {
        0% { transform: translateX(0); }
        100% { transform: translateX(-100%); }
    }
    
    .header {
        margin-top: 120rpx; margin-bottom: 50rpx;
        display: flex; flex-direction: column; align-items: center; z-index: 1;
        .logo { width: 140rpx; height: 140rpx; margin-bottom: 20rpx; border-radius: 24rpx; background: #fff; }
        .header-text { text-align: center; }
        .title { font-size: 48rpx; font-weight: bold; color: #fff; letter-spacing: 2rpx; text-shadow: 0 2rpx 4rpx rgba(0,0,0,0.5); display: block;}
        .subtitle { font-size: 28rpx; color: #eee; margin-top: 10rpx; display: block;}
    }
    
    .login-card {
        width: 100%; background: rgba(255, 255, 255, 0.95); border-radius: 24rpx; padding: 40rpx 30rpx;
        box-shadow: 0 20rpx 60rpx rgba(0,0,0,0.3); z-index: 1;
    }
    .glass-effect {
        backdrop-filter: blur(10px);
    }
    
    /* Tabs */
    .tabs { display: flex; margin-bottom: 40rpx; padding: 0 20rpx; }
    .tab-item { margin-right: 40rpx; position: relative; padding-bottom: 10rpx; cursor: pointer; }
    .tab-text { font-size: 32rpx; color: #666; transition: all 0.3s; }
    .tab-item.active .tab-text { font-size: 36rpx; font-weight: bold; color: #333; }
    .tab-line {
        position: absolute; bottom: 0; left: 0; right: 0;
        height: 6rpx; background: linear-gradient(90deg, #FF7A00, #FF5000);
        border-radius: 3rpx;
    }
    
    /* Inputs */
    .form-area { margin-bottom: 40rpx; }
    .input-item {
        display: flex; align-items: center;
        border-bottom: 1px solid #ddd;
        padding: 20rpx 0;
        margin-bottom: 20rpx;
    }
    .input-icon { font-size: 36rpx; width: 60rpx; text-align: center; color: #666; }
    .input { flex: 1; height: 60rpx; font-size: 30rpx; color: #333; }
    .ph-color { color: #999; }
    
    .code-item { position: relative; }
    .code-btn {
        font-size: 26rpx; color: #FF5000; padding: 10rpx 20rpx;
        border-left: 1px solid #ddd;
    }
    .code-btn.disabled { color: #ccc; }
    
    .btn-login {
        background: linear-gradient(90deg, #FF7A00, #FF5000);
        color: #fff; margin-top: 40rpx; border-radius: 45rpx;
        font-size: 34rpx; font-weight: bold;
        box-shadow: 0 6rpx 16rpx rgba(255, 80, 0, 0.3);
        &::after { border: none; }
    }
    
    .links {
        margin-top: 30rpx; display: flex; justify-content: center; align-items: center;
        font-size: 26rpx; color: #666;
    }
    .link { padding: 0 16rpx; }
    .highlight { color: #FF5000; font-weight: bold; }
    .divider { color: #ccc; }
    
    .guest-entry {
        margin-top: 40rpx; text-align: center;
        padding-top: 20rpx; border-top: 1px solid #eee;
        font-size: 28rpx; color: #555;
    }
    
    .footer { margin-top: auto; padding-bottom: 20rpx; z-index: 1; }
    .copyright { font-size: 24rpx; color: rgba(255,255,255,0.8); text-shadow: 0 1px 2px rgba(0,0,0,0.5); }
</style>
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Successfully updated login.vue with Immersive Background and Prosperity Stats")
