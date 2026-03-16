import os

# 1. Update merchant/product_list.vue (Card Style)
list_vue_path = r'D:\spb-expert11\frontend\pages\merchant\product_list.vue'
list_vue_content = """<template>
	<view class="container">
        <view class="header-actions">
            <view class="btn-add" @click="goToAdd">
                <text class="plus">+</text> Add New Product
            </view>
        </view>
        
		<scroll-view scroll-y class="product-list">
			<view class="product-card" v-for="(item, index) in products" :key="item.id">
				<image :src="item.image || '/static/logo.png'" mode="aspectFill" class="p-img"></image>
				<view class="p-info">
					<text class="p-name">{{ item.name }}</text>
                    <view class="p-meta">
                        <text class="p-price">¥{{ item.price }}</text>
                        <text class="p-stock">Stock: {{ item.stock }}</text>
                    </view>
                    <view class="p-status">
                        <text class="status-tag" :class="{active: item.is_active}">{{ item.is_active ? 'Active' : 'Draft' }}</text>
                    </view>
				</view>
                <view class="p-actions">
                    <view class="action-btn edit" @click="editProduct(item)">Edit</view>
                    <view class="action-btn delete" @click="deleteProduct(item)">Del</view>
                </view>
			</view>
            <view class="empty-tip" v-if="products.length === 0">
                <text>No products yet</text>
            </view>
		</scroll-view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				products: []
			}
		},
		onShow() {
            this.loadProducts();
		},
		methods: {
            async loadProducts() {
                try {
                    const res = await request({ url: '/store/merchant/products/' });
                    this.products = res.results || res;
                } catch (e) {
                    console.error(e);
                }
            },
            goToAdd() {
                uni.navigateTo({ url: '/pages/merchant/product_edit' });
            },
            editProduct(item) {
                uni.navigateTo({ url: `/pages/merchant/product_edit?id=${item.id}` });
            },
            async deleteProduct(item) {
                uni.showModal({
                    title: 'Confirm Delete',
                    content: 'Are you sure you want to delete this product?',
                    success: async (res) => {
                        if (res.confirm) {
                            try {
                                await request({ url: `/store/products/${item.id}/`, method: 'DELETE' });
                                uni.showToast({ title: 'Deleted' });
                                this.loadProducts();
                            } catch (e) {
                                uni.showToast({ title: 'Failed', icon: 'none' });
                            }
                        }
                    }
                });
            }
		}
	}
</script>

<style lang="scss">
	.container {
		padding: 20rpx;
        background-color: #f5f5f5;
        min-height: 100vh;
	}
    
    .header-actions {
        margin-bottom: 20rpx;
    }
    .btn-add {
        background-color: #FF5000;
        color: #fff;
        text-align: center;
        padding: 20rpx;
        border-radius: 10rpx;
        font-size: 30rpx;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .plus { font-size: 40rpx; margin-right: 10rpx; line-height: 1; }
    
    .product-card {
        background-color: #fff;
        border-radius: 16rpx;
        padding: 20rpx;
        margin-bottom: 20rpx;
        display: flex;
        align-items: center;
        box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
    }
    .p-img {
        width: 140rpx;
        height: 140rpx;
        border-radius: 8rpx;
        background-color: #eee;
        margin-right: 20rpx;
    }
    .p-info {
        flex: 1;
        height: 140rpx;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .p-name { font-size: 28rpx; font-weight: bold; color: #333; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
    .p-meta { display: flex; align-items: center; justify-content: space-between; }
    .p-price { font-size: 30rpx; color: #FF5000; font-weight: bold; }
    .p-stock { font-size: 24rpx; color: #999; }
    
    .status-tag {
        font-size: 20rpx;
        padding: 2rpx 8rpx;
        background-color: #eee;
        color: #999;
        border-radius: 4rpx;
    }
    .status-tag.active {
        background-color: #e8f5e9;
        color: #4caf50;
    }
    
    .p-actions {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 140rpx;
        padding-left: 20rpx;
        border-left: 1rpx solid #f0f0f0;
    }
    .action-btn {
        font-size: 24rpx;
        padding: 10rpx 20rpx;
        border-radius: 30rpx;
        text-align: center;
    }
    .edit { background-color: #e3f2fd; color: #2196f3; margin-bottom: 10rpx; }
    .delete { background-color: #ffebee; color: #f44336; }
    
    .empty-tip { text-align: center; color: #999; margin-top: 100rpx; }
</style>
"""

with open(list_vue_path, 'w', encoding='utf-8') as f:
    f.write(list_vue_content)
print("Updated merchant/product_list.vue")

# 2. Update merchant/product_edit.vue (Clean Form)
edit_vue_path = r'D:\spb-expert11\frontend\pages\merchant\product_edit.vue'
edit_vue_content = """<template>
	<view class="container">
		<view class="form-group">
            <view class="label">Product Name</view>
            <input class="input" v-model="form.name" placeholder="Enter product name" />
        </view>
        
        <view class="form-group">
            <view class="label">Price (¥)</view>
            <input class="input" type="number" v-model="form.price" placeholder="0.00" />
        </view>
        
        <view class="form-group">
            <view class="label">Stock</view>
            <input class="input" type="number" v-model="form.stock" placeholder="0" />
        </view>
        
        <view class="form-group">
            <view class="label">Category</view>
            <!-- Simplified: Input ID or Select if we had list -->
            <input class="input" type="number" v-model="form.category" placeholder="Category ID" />
        </view>
        
        <view class="form-group">
            <view class="label">Description</view>
            <textarea class="textarea" v-model="form.description" placeholder="Product details..."></textarea>
        </view>
        
        <view class="form-group">
            <view class="label">Main Image</view>
            <view class="image-uploader" @click="chooseImage">
                <image v-if="tempImage" :src="tempImage" mode="aspectFill" class="uploaded-img"></image>
                <view v-else class="upload-placeholder">
                    <text class="plus">+</text>
                    <text>Upload</text>
                </view>
            </view>
        </view>
        
        <view class="btn-submit" @click="submit">Save Product</view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				id: null,
                form: {
                    name: '',
                    price: '',
                    stock: '',
                    category: '',
                    description: ''
                },
                tempImage: ''
			}
		},
		onLoad(options) {
            if (options.id) {
                this.id = options.id;
                this.loadProduct();
            }
		},
		methods: {
            async loadProduct() {
                try {
                    const res = await request({ url: `/store/products/${this.id}/` });
                    this.form = {
                        name: res.name,
                        price: res.price,
                        stock: res.stock,
                        category: res.category,
                        description: res.description
                    };
                    // Handle image display if needed
                } catch (e) {
                    console.error(e);
                }
            },
            chooseImage() {
                uni.chooseImage({
                    count: 1,
                    success: (res) => {
                        this.tempImage = res.tempFilePaths[0];
                    }
                });
            },
            async submit() {
                if (!this.form.name || !this.form.price) {
                    uni.showToast({ title: 'Name and Price required', icon: 'none' });
                    return;
                }
                
                try {
                    let url = '/store/products/';
                    let method = 'POST';
                    if (this.id) {
                        url += `${this.id}/`;
                        method = 'PUT'; // or PATCH
                    }
                    
                    // Simple JSON submit first (excluding image for simplicity in this demo)
                    // For image upload, we'd need uni.uploadFile as implemented before
                    const res = await request({
                        url: url,
                        method: method,
                        data: this.form
                    });
                    
                    // If image exists, upload it separately or handle multipart
                    if (this.tempImage) {
                         const uploadRes = await uni.uploadFile({
                            url: 'http://127.0.0.1:8000/api/v1' + url + 'upload_image/', // Custom action needed or standard multipart
                            filePath: this.tempImage,
                            name: 'image',
                            header: {
                                'Authorization': 'Bearer ' + uni.getStorageSync('token')
                            }
                        });
                    }
                    
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
        box-shadow: 0 4rpx 12rpx rgba(255, 80, 0, 0.3);
    }
</style>
"""

with open(edit_vue_path, 'w', encoding='utf-8') as f:
    f.write(edit_vue_content)
print("Updated merchant/product_edit.vue")
