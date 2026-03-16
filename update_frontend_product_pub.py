import os
import json

# 1. Update apps/store/views.py (Add upload_image action)
# We'll create a separate script for this to keep things clean, or just do it here if we want.
# Let's write the updater script for backend first.

updater_script = r"""
import re
import os

file_path = r'D:\spb-expert11\apps\store\views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import for ProductImage
if "from .models import Category, Product" in content and "ProductImage" not in content:
    content = content.replace("from .models import Category, Product", "from .models import Category, Product, ProductImage")

# The method code to insert
upload_method = '''
    @action(detail=True, methods=['post'], parser_classes=[parsers.MultiPartParser])
    def upload_image(self, request, pk=None):
        product = self.get_object()
        # Check ownership
        if product.merchant.user != request.user:
            return Response({'error': 'Permission denied'}, status=403)
            
        image_file = request.FILES.get('image')
        if not image_file:
             return Response({'error': 'No image provided'}, status=400)
             
        # Create ProductImage
        # Check if it's the first image
        is_main = not product.images.exists()
        ProductImage.objects.create(product=product, image=image_file, is_main=is_main)
        
        return Response({'status': 'uploaded'})
'''

if "def upload_image" not in content:
    # Insert before "from apps.core.models import Banner" which follows ProductViewSet
    if "from apps.core.models import Banner" in content:
        content = content.replace("from apps.core.models import Banner", upload_method + "\nfrom apps.core.models import Banner")
    elif "class HomeViewSet" in content:
         # Fallback
         content = content.replace("class HomeViewSet", upload_method + "\nclass HomeViewSet")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Updated {file_path}")
"""

with open(r'D:\spb-expert9\update_product_viewset.py', 'w', encoding='utf-8') as f:
    f.write(updater_script)


# 2. Create pages/merchant/product_list.vue
product_list_path = r'D:\spb-expert11\frontend\pages\merchant\product_list.vue'
product_list_content = """<template>
	<view class="container">
        <view class="header">
            <view class="btn-add" @click="goToAdd">+ Add Product</view>
        </view>
        
        <view class="product-list">
            <view class="product-item" v-for="(item, index) in products" :key="index">
                <image :src="item.images && item.images.length > 0 ? item.images[0].image : ''" class="product-img" mode="aspectFill"></image>
                <view class="product-info">
                    <text class="product-name">{{ item.name }}</text>
                    <text class="product-price">¥{{ item.price }}</text>
                    <text class="product-stock">Stock: {{ item.stock }}</text>
                </view>
            </view>
            <view class="empty-state" v-if="products.length === 0">
                <text>No products yet.</text>
            </view>
        </view>
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
                    const res = await request({ url: '/store/products/?mode=mine' });
                    this.products = res;
                } catch (e) {
                    console.error(e);
                }
            },
            goToAdd() {
                uni.navigateTo({ url: '/pages/merchant/product_edit' });
            }
		}
	}
</script>

<style>
	.container {
		background-color: #f5f5f5;
        min-height: 100vh;
        padding: 20rpx;
	}
    .header {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 20rpx;
    }
    .btn-add {
        background-color: #ff5000;
        color: #fff;
        padding: 10rpx 30rpx;
        border-radius: 30rpx;
        font-size: 28rpx;
    }
    .product-item {
        background-color: #fff;
        border-radius: 10rpx;
        margin-bottom: 20rpx;
        padding: 20rpx;
        display: flex;
    }
    .product-img {
        width: 150rpx;
        height: 150rpx;
        background-color: #eee;
        margin-right: 20rpx;
        border-radius: 8rpx;
    }
    .product-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .product-name {
        font-size: 30rpx;
        font-weight: bold;
    }
    .product-price {
        color: #ff5000;
        font-size: 28rpx;
    }
    .product-stock {
        font-size: 24rpx;
        color: #999;
    }
    .empty-state {
        text-align: center;
        padding-top: 100rpx;
        color: #999;
    }
</style>
"""
with open(product_list_path, 'w', encoding='utf-8') as f:
    f.write(product_list_content)
print(f"Created {product_list_path}")


# 3. Create pages/merchant/product_edit.vue
product_edit_path = r'D:\spb-expert11\frontend\pages\merchant\product_edit.vue'
product_edit_content = """<template>
	<view class="container">
        <form @submit="formSubmit">
            <view class="form-group">
                <text class="label">Product Name</text>
                <input class="input" name="name" v-model="form.name" placeholder="Enter product name" />
            </view>
            
            <view class="form-group">
                <text class="label">Price</text>
                <input class="input" name="price" type="digit" v-model="form.price" placeholder="0.00" />
            </view>
            
            <view class="form-group">
                <text class="label">Stock</text>
                <input class="input" name="stock" type="number" v-model="form.stock" placeholder="0" />
            </view>
            
            <view class="form-group">
                <text class="label">Category</text>
                <picker @change="bindPickerChange" :value="catIndex" :range="categories" range-key="name">
                    <view class="picker">
                        {{ catIndex > -1 ? categories[catIndex].name : 'Select Category' }}
                    </view>
                </picker>
            </view>
            
            <view class="form-group">
                <text class="label">Description</text>
                <textarea class="textarea" v-model="form.description" placeholder="Product details..." />
            </view>
            
            <view class="form-group">
                <text class="label">Images</text>
                <view class="image-list">
                    <view class="img-item" v-for="(img, idx) in tempImages" :key="idx">
                        <image :src="img" mode="aspectFill"></image>
                    </view>
                    <view class="img-add" @click="chooseImage">+</view>
                </view>
            </view>
            
            <button form-type="submit" class="btn-submit" :disabled="submitting">Publish Product</button>
        </form>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';
    const BASE_URL = 'http://127.0.0.1:8000/api/v1'; // Need explicit for upload

	export default {
		data() {
			return {
                form: {
                    name: '',
                    price: '',
                    stock: '',
                    description: '',
                    category: ''
                },
                categories: [],
                catIndex: -1,
                tempImages: [],
                submitting: false
			}
		},
		onLoad() {
            this.loadCategories();
		},
		methods: {
            async loadCategories() {
                try {
                    const res = await request({ url: '/store/categories/' });
                    this.categories = res;
                } catch (e) {
                    console.error(e);
                }
            },
            bindPickerChange(e) {
                this.catIndex = e.detail.value;
                this.form.category = this.categories[this.catIndex].id;
            },
            chooseImage() {
                uni.chooseImage({
                    count: 3,
                    success: (res) => {
                        this.tempImages = [...this.tempImages, ...res.tempFilePaths];
                    }
                });
            },
            async formSubmit() {
                if (!this.form.name || !this.form.price || !this.form.category) {
                    uni.showToast({ title: 'Please fill required fields', icon: 'none' });
                    return;
                }
                
                this.submitting = true;
                uni.showLoading({ title: 'Publishing...' });
                
                try {
                    // 1. Create Product
                    const product = await request({
                        url: '/store/products/',
                        method: 'POST',
                        data: this.form
                    });
                    
                    // 2. Upload Images
                    if (this.tempImages.length > 0) {
                        for (let path of this.tempImages) {
                            await this.uploadImage(product.id, path);
                        }
                    }
                    
                    uni.hideLoading();
                    uni.showToast({ title: 'Success!' });
                    setTimeout(() => {
                        uni.navigateBack();
                    }, 1500);
                    
                } catch (e) {
                    uni.hideLoading();
                    uni.showToast({ title: 'Failed', icon: 'none' });
                    console.error(e);
                } finally {
                    this.submitting = false;
                }
            },
            uploadImage(productId, filePath) {
                return new Promise((resolve, reject) => {
                    uni.uploadFile({
                        url: `${BASE_URL}/store/products/${productId}/upload_image/`,
                        filePath: filePath,
                        name: 'image',
                        header: {
                            'Authorization': 'Bearer ' + uni.getStorageSync('token')
                        },
                        success: (res) => {
                             if (res.statusCode >= 200 && res.statusCode < 300) {
                                 resolve(res.data);
                             } else {
                                 reject(res);
                             }
                        },
                        fail: (err) => reject(err)
                    });
                });
            }
		}
	}
</script>

<style>
	.container {
		padding: 30rpx;
	}
    .form-group {
        margin-bottom: 30rpx;
    }
    .label {
        font-size: 28rpx;
        color: #666;
        margin-bottom: 10rpx;
        display: block;
    }
    .input {
        border: 1rpx solid #eee;
        padding: 20rpx;
        border-radius: 8rpx;
        font-size: 28rpx;
    }
    .picker {
        border: 1rpx solid #eee;
        padding: 20rpx;
        border-radius: 8rpx;
        font-size: 28rpx;
    }
    .textarea {
        border: 1rpx solid #eee;
        padding: 20rpx;
        border-radius: 8rpx;
        width: 100%;
        height: 200rpx;
        font-size: 28rpx;
    }
    .image-list {
        display: flex;
        flex-wrap: wrap;
    }
    .img-item {
        width: 150rpx;
        height: 150rpx;
        margin-right: 20rpx;
        margin-bottom: 20rpx;
        border-radius: 8rpx;
        overflow: hidden;
    }
    .img-item image {
        width: 100%;
        height: 100%;
    }
    .img-add {
        width: 150rpx;
        height: 150rpx;
        background-color: #f5f5f5;
        border: 1rpx dashed #ccc;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 60rpx;
        color: #ccc;
        border-radius: 8rpx;
    }
    .btn-submit {
        background-color: #ff5000;
        color: #fff;
        margin-top: 50rpx;
        border-radius: 50rpx;
    }
</style>
"""
with open(product_edit_path, 'w', encoding='utf-8') as f:
    f.write(product_edit_content)
print(f"Created {product_edit_path}")


# 4. Update pages/merchant/dashboard.vue (Link to Product List)
dashboard_path = r'D:\spb-expert11\frontend\pages\merchant\dashboard.vue'
with open(dashboard_path, 'r', encoding='utf-8') as f:
    dashboard_content = f.read()

# Replace empty action for product management
if '<view class="menu-item">' in dashboard_content:
    dashboard_content = dashboard_content.replace(
        '<view class="menu-item">',
        '<view class="menu-item" @click="goToProducts">'
    )

# Add method
if "goToProducts" not in dashboard_content and "goToOrders() {" in dashboard_content:
    dashboard_content = dashboard_content.replace(
        "goToOrders() {",
        "goToProducts() { uni.navigateTo({ url: '/pages/merchant/product_list' }); },\n            goToOrders() {"
    )

with open(dashboard_path, 'w', encoding='utf-8') as f:
    f.write(dashboard_content)
print(f"Updated {dashboard_path}")


# 5. Update pages.json
pages_json_path = r'D:\spb-expert11\frontend\pages.json'
with open(pages_json_path, 'r', encoding='utf-8') as f:
    pages_config = json.load(f)

new_pages = [
    {
        "path": "pages/merchant/product_list",
        "style": {
            "navigationBarTitleText": "My Products"
        }
    },
    {
        "path": "pages/merchant/product_edit",
        "style": {
            "navigationBarTitleText": "Edit Product"
        }
    }
]

for new_page in new_pages:
    if not any(p['path'] == new_page['path'] for p in pages_config['pages']):
        pages_config['pages'].append(new_page)
    
with open(pages_json_path, 'w', encoding='utf-8') as f:
    json.dump(pages_config, f, indent=4)
print(f"Updated {pages_json_path}")
