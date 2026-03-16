import os

# 1. common/api.js
api_js = """const BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const request = (options) => {
	return new Promise((resolve, reject) => {
		uni.request({
			url: BASE_URL + options.url,
			method: options.method || 'GET',
			data: options.data || {},
			header: options.header || {
                'Content-Type': 'application/json'
            },
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data);
				} else {
					console.error('API Error:', res);
					reject(res);
				}
			},
			fail: (err) => {
				console.error('Network Error:', err);
				reject(err);
			}
		});
	});
}
"""
with open(r'D:\spb-expert11\frontend\common\api.js', 'w', encoding='utf-8') as f:
    f.write(api_js)

# 2. pages/index/index.vue
index_vue = """<template>
	<view class="content">
        <!-- Search Bar (Placeholder) -->
        <view class="search-bar">
            <input placeholder="Search products..." />
        </view>

        <!-- Banners -->
		<swiper class="swiper" :indicator-dots="true" :autoplay="true" :interval="3000" :duration="1000">
			<swiper-item v-for="(item, index) in banners" :key="index">
				<view class="swiper-item">
                    <image :src="item.image || '/static/placeholder.png'" mode="aspectFill" style="width:100%; height:100%;"></image>
                    <text class="banner-title" v-if="!item.image">{{ item.title }}</text>
                </view>
			</swiper-item>
		</swiper>

        <!-- Categories Grid -->
        <view class="category-grid">
            <view class="category-item" v-for="(cat, index) in categories" :key="index">
                <text>{{ cat.name }}</text>
            </view>
        </view>

        <!-- Recommended Products -->
        <view class="section-title">Recommended</view>
        <view class="product-list">
            <view class="product-item" v-for="(prod, index) in products" :key="index">
                <image :src="prod.images && prod.images.length > 0 ? prod.images[0].image : '/static/product_placeholder.png'" mode="aspectFill" class="product-img"></image>
                <view class="product-info">
                    <text class="product-name">{{ prod.name }}</text>
                    <text class="product-price">¥{{ prod.price }}</text>
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
            async loadData() {
                try {
                    const res = await request({ url: '/store/home/' });
                    this.banners = res.banners;
                    this.categories = res.categories;
                    this.products = res.recommended_products;
                } catch (e) {
                    console.error(e);
                }
            }
		}
	}
</script>

<style>
	.content {
		display: flex;
		flex-direction: column;
        padding-bottom: 20px;
	}
    .swiper {
        height: 300rpx;
        background-color: #eee;
    }
    .swiper-item {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .category-grid {
        display: flex;
        flex-wrap: wrap;
        padding: 20rpx;
        background: #fff;
        margin-top: 20rpx;
    }
    .category-item {
        width: 25%;
        text-align: center;
        padding: 10rpx;
        font-size: 24rpx;
    }
    .section-title {
        font-size: 32rpx;
        font-weight: bold;
        padding: 20rpx;
        margin-top: 20rpx;
    }
    .product-list {
        display: flex;
        flex-wrap: wrap;
        padding: 10rpx;
    }
    .product-item {
        width: 48%;
        margin: 1%;
        background: #fff;
        border-radius: 10rpx;
        overflow: hidden;
    }
    .product-img {
        width: 100%;
        height: 300rpx;
        background: #f0f0f0;
    }
    .product-info {
        padding: 10rpx;
    }
    .product-name {
        font-size: 28rpx;
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .product-price {
        color: red;
        font-weight: bold;
        font-size: 30rpx;
    }
</style>
"""
with open(r'D:\spb-expert11\frontend\pages\index\index.vue', 'w', encoding='utf-8') as f:
    f.write(index_vue)

# 3. pages/category/category.vue (Placeholder)
cat_vue = """<template>
	<view>
		<text>Category Page</text>
	</view>
</template>
<script>
	export default {
		data() {
			return {}
		}
	}
</script>
"""
with open(r'D:\spb-expert11\frontend\pages\category\category.vue', 'w', encoding='utf-8') as f:
    f.write(cat_vue)

# 4. pages/cart/cart.vue (Placeholder)
cart_vue = """<template>
	<view>
		<text>Cart Page</text>
	</view>
</template>
<script>
	export default {
		data() {
			return {}
		}
	}
</script>
"""
with open(r'D:\spb-expert11\frontend\pages\cart\cart.vue', 'w', encoding='utf-8') as f:
    f.write(cart_vue)

# 5. pages/user/user.vue (Placeholder)
user_vue = """<template>
	<view>
		<text>User Center</text>
	</view>
</template>
<script>
	export default {
		data() {
			return {}
		}
	}
</script>
"""
with open(r'D:\spb-expert11\frontend\pages\user\user.vue', 'w', encoding='utf-8') as f:
    f.write(user_vue)

print("Created Vue Pages and API util")
