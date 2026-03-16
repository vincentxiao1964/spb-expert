import os
import json

# 1. Write uni.scss
uni_scss_content = """/* Global Theme Variables */
$uni-color-primary: #FF5000;
$uni-color-success: #4cd964;
$uni-color-warning: #f0ad4e;
$uni-color-error: #dd524d;

$uni-text-color: #333;
$uni-text-color-inverse: #fff;
$uni-text-color-grey: #999;
$uni-text-color-placeholder: #808080;
$uni-text-color-disable: #c0c0c0;

$uni-bg-color: #ffffff;
$uni-bg-color-grey: #f8f8f8;
$uni-bg-color-hover: #f1f1f1;

$uni-border-color: #e5e5e5;

/* Font Sizes */
$uni-font-size-sm: 24rpx;
$uni-font-size-base: 28rpx;
$uni-font-size-lg: 32rpx;
"""
with open(r'D:\spb-expert11\frontend\uni.scss', 'w', encoding='utf-8') as f:
    f.write(uni_scss_content)
print("Created uni.scss")

# 2. Update pages.json (TabBar Color)
pages_json_path = r'D:\spb-expert11\frontend\pages.json'
with open(pages_json_path, 'r', encoding='utf-8') as f:
    pages_content = f.read()

# Simple string replace for selectedColor
if '"selectedColor": "#3cc51f"' in pages_content:
    pages_content = pages_content.replace('"selectedColor": "#3cc51f"', '"selectedColor": "#FF5000"')
    print("Updated pages.json tabBar color")
elif '"selectedColor": "#FF5000"' not in pages_content:
    # If it's something else, try to find the line
    import re
    pages_content = re.sub(r'"selectedColor":\s*"#[0-9a-fA-F]{6}"', '"selectedColor": "#FF5000"', pages_content)
    print("Updated pages.json tabBar color via regex")

with open(pages_json_path, 'w', encoding='utf-8') as f:
    f.write(pages_content)

# 3. Update App.vue (Global Styles)
app_vue_path = r'D:\spb-expert11\frontend\App.vue'
app_vue_content = """<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style lang="scss">
	/* Global CSS */
    @import '@/uni.scss';
    
    view, text, image, input, scroll-view {
        box-sizing: border-box;
    }
    
    page {
        background-color: #f5f5f5;
        font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
    }
    
    .container {
        width: 100%;
        min-height: 100vh;
        background-color: #f5f5f5;
    }
    
    /* Utility Classes */
    .text-primary { color: $uni-color-primary; }
    .bg-white { background-color: #fff; }
    .mt-10 { margin-top: 10rpx; }
    .mb-10 { margin-bottom: 10rpx; }
    .p-20 { padding: 20rpx; }
    
    /* Common Button */
    .btn-primary {
        background-color: $uni-color-primary;
        color: #fff;
        text-align: center;
        border-radius: 40rpx;
        font-size: 28rpx;
        padding: 10rpx 30rpx;
    }
</style>
"""
with open(app_vue_path, 'w', encoding='utf-8') as f:
    f.write(app_vue_content)
print("Updated App.vue")

# 4. Update index.vue (Home Page UI)
index_vue_path = r'D:\spb-expert11\frontend\pages\index\index.vue'
index_vue_content = """<template>
	<view class="container">
		<!-- Search Bar (Sticky) -->
		<view class="search-header">
			<view class="search-bar" @click="doSearch">
				<view class="search-icon">🔍</view>
				<text class="search-placeholder">Search ships, parts, services...</text>
			</view>
		</view>

		<!-- Banners -->
		<swiper class="swiper" circular indicator-dots autoplay indicator-active-color="#FF5000">
			<swiper-item v-for="(item, index) in banners" :key="index">
				<view class="swiper-item">
					<image v-if="item.image" :src="item.image" mode="aspectFill" class="banner-img"></image>
                    <view v-else class="banner-placeholder">Banner {{ index + 1 }}</view>
				</view>
			</swiper-item>
		</swiper>

		<!-- Categories -->
		<view class="category-grid">
			<view class="category-item" v-for="(item, index) in categories" :key="index">
				<view class="cat-icon-box">
                    <image v-if="item.icon" :src="item.icon" class="cat-img"></image>
                    <text v-else class="cat-emoji">📦</text>
                </view>
				<text class="cat-name">{{ item.name }}</text>
			</view>
		</view>

		<!-- Recommended Products (Waterfall/Grid) -->
		<view class="section-header">
            <text class="section-title">Recommended</text>
            <text class="section-more">See All ></text>
        </view>
        
		<view class="product-list">
			<view class="product-item" v-for="(item, index) in products" :key="index" @click="goToDetail(item)">
				<view class="product-img-box">
                    <image v-if="item.image" :src="item.image" mode="aspectFill" class="product-img"></image>
                    <view v-else class="product-img-placeholder">Product</view>
                </view>
				<view class="product-info">
					<text class="product-name">{{ item.name }}</text>
                    <view class="product-bottom">
                        <text class="product-price">¥<text class="price-num">{{ item.price }}</text></text>
                        <text class="product-sold" v-if="item.sales">Sold {{ item.sales }}</text>
                    </view>
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
				banners: [],
				categories: [],
				products: []
			}
		},
		onLoad() {
            this.loadData();
		},
		methods: {
            doSearch() {
                uni.navigateTo({
                    url: `/pages/search/search`
                });
            },
            goToDetail(item) {
                uni.navigateTo({
                    url: `/pages/product/detail?id=${item.id}`
                });
            },
            async loadData() {
                try {
                    const res = await request({ url: '/store/home/' });
                    this.banners = res.banners || [{id:1}, {id:2}];
                    this.categories = res.categories || [{name:'Ships'}, {name:'Parts'}, {name:'Crew'}, {name:'Fuel'}];
                    this.products = res.recommended_products || [];
                } catch (e) {
                    console.error(e);
                    // Fallback data for preview
                    this.banners = [{id:1}, {id:2}];
                    this.categories = [{name:'Ships'}, {name:'Parts'}, {name:'Crew'}, {name:'Fuel'}, {name:'Docs'}];
                }
            }
		}
	}
</script>

<style lang="scss">
    /* Header */
    .search-header {
        position: sticky;
        top: 0;
        z-index: 100;
        background-color: #FF5000; /* Theme Color */
        padding: 20rpx;
    }
    .search-bar {
        background-color: #fff;
        height: 64rpx;
        border-radius: 32rpx;
        display: flex;
        align-items: center;
        padding: 0 20rpx;
    }
    .search-icon { font-size: 28rpx; margin-right: 10rpx; }
    .search-placeholder { font-size: 26rpx; color: #999; }

    /* Banner */
    .swiper {
        height: 300rpx;
        margin: 20rpx;
        border-radius: 16rpx;
        overflow: hidden;
    }
    .swiper-item, .banner-img, .banner-placeholder {
        width: 100%;
        height: 100%;
        background-color: #eee;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #999;
    }

    /* Categories */
    .category-grid {
        display: flex;
        flex-wrap: wrap;
        padding: 20rpx;
        background-color: #fff;
        margin: 20rpx;
        border-radius: 16rpx;
    }
    .category-item {
        width: 20%;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20rpx;
    }
    .cat-icon-box {
        width: 80rpx;
        height: 80rpx;
        background-color: #f8f8f8;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10rpx;
    }
    .cat-emoji { font-size: 40rpx; }
    .cat-name { font-size: 24rpx; color: #333; }

    /* Section Header */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 30rpx;
        margin-bottom: 20rpx;
    }
    .section-title { font-size: 32rpx; font-weight: bold; color: #333; }
    .section-more { font-size: 24rpx; color: #999; }

    /* Product List (Grid) */
    .product-list {
        display: flex;
        flex-wrap: wrap;
        padding: 0 20rpx;
        justify-content: space-between;
    }
    .product-item {
        width: 48%; /* Two column */
        background-color: #fff;
        border-radius: 16rpx;
        margin-bottom: 20rpx;
        overflow: hidden;
        box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
    }
    .product-img-box {
        width: 100%;
        height: 340rpx;
        background-color: #f5f5f5;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .product-img { width: 100%; height: 100%; }
    .product-img-placeholder { color: #ccc; }
    
    .product-info { padding: 20rpx; }
    .product-name {
        font-size: 28rpx;
        color: #333;
        line-height: 1.4;
        height: 80rpx; /* 2 lines */
        overflow: hidden;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
    }
    .product-bottom {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-top: 10rpx;
    }
    .product-price { color: #FF5000; font-size: 24rpx; font-weight: bold; }
    .price-num { font-size: 36rpx; }
    .product-sold { font-size: 22rpx; color: #999; }
</style>
"""
with open(index_vue_path, 'w', encoding='utf-8') as f:
    f.write(index_vue_content)
print("Updated index.vue")
