import os
import json

# File paths
BASE_DIR = r"D:\spb-expert11\frontend"
PAGES_JSON_PATH = os.path.join(BASE_DIR, "pages.json")
CART_VUE_PATH = os.path.join(BASE_DIR, "pages", "cart", "cart.vue")
ADDR_LIST_VUE_PATH = os.path.join(BASE_DIR, "pages", "address", "list.vue")
ADDR_EDIT_VUE_PATH = os.path.join(BASE_DIR, "pages", "address", "edit.vue")
CONFIRM_VUE_PATH = os.path.join(BASE_DIR, "pages", "order", "confirm.vue")

# 1. Fix pages.json
def fix_pages_json():
    try:
        with open(PAGES_JSON_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # The broken block to find
        broken_block = '''            "path": "pages/user/user",
            "style": {
                "navigationBarTitleText": "Me"
            },
		{"path": "pages/user/favorites", "style": {"navigationBarTitleText": "My Favorites"},
		{"path": "pages/chat/list", "style": {"navigationBarTitleText": "Messages"}},
		{"path": "pages/chat/chat", "style": {"navigationBarTitleText": "Chat"}}}
        },'''
        
        # The fixed block
        fixed_block = '''            "path": "pages/user/user",
            "style": {
                "navigationBarTitleText": "Me"
            }
        },
        {
            "path": "pages/user/favorites",
            "style": {
                "navigationBarTitleText": "My Favorites"
            }
        },
        {
            "path": "pages/chat/list",
            "style": {
                "navigationBarTitleText": "Messages"
            }
        },
        {
            "path": "pages/chat/chat",
            "style": {
                "navigationBarTitleText": "Chat"
            }
        },'''
        
        if broken_block in content:
            new_content = content.replace(broken_block, fixed_block)
            with open(PAGES_JSON_PATH, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Successfully fixed pages.json")
        else:
            # Fallback: try to fix by parsing if simple replace failed (due to whitespace diffs)
            # But since I read it directly from previous tool output, whitespace should match.
            # If not, let's try a regex or just manual check.
            # Actually, let's try to normalize spaces if needed, but strict replace is safer if exact.
            print("Could not find exact broken block in pages.json. Checking for variants...")
            # Variant with different indentation?
            pass
            
    except Exception as e:
        print(f"Error fixing pages.json: {e}")

# 2. Update Cart Vue
cart_vue_content = r'''<template>
	<view class="container">
		<view class="cart-list" v-if="cartItems.length > 0">
			<view class="cart-item" v-for="(item, index) in cartItems" :key="index">
				<view class="item-selector" @click="toggleSelect(item)">
                    <view class="radio" :class="{checked: item.selected}"></view>
                </view>
				<view class="item-img" @click="goDetail(item.product.id)">
                    <image :src="item.product.images[0].image" v-if="item.product.images && item.product.images.length > 0" mode="aspectFill"></image>
                    <image src="/static/default-product.png" v-else mode="aspectFill"></image>
                </view>
				<view class="item-info">
					<text class="item-name" @click="goDetail(item.product.id)">{{ item.product.name }}</text>
                    <text class="item-sku" v-if="item.product.sku">SKU: {{ item.product.sku }}</text>
					<view class="price-qty">
                        <text class="item-price">¥{{ item.product.price }}</text>
                        <view class="quantity-ctrl">
                            <text class="btn-qty" @click.stop="updateQty(item, -1)">-</text>
                            <text class="qty">{{ item.quantity }}</text>
                            <text class="btn-qty" @click.stop="updateQty(item, 1)">+</text>
                        </view>
                    </view>
				</view>
                <view class="btn-delete" @click.stop="removeItem(item)">
                    <text class="icon-delete">×</text>
                </view>
			</view>
		</view>
		
        <!-- Empty State -->
		<view class="empty-cart" v-else>
            <image src="/static/empty-cart.png" mode="widthFix" class="empty-img"></image>
			<text class="empty-text">Your cart is empty</text>
			<button class="btn-go-shop" @click="goShop">Go Shopping</button>
		</view>

		<!-- Bottom Bar -->
		<view class="bottom-bar" v-if="cartItems.length > 0">
            <view class="select-all" @click="toggleSelectAll">
                <view class="radio" :class="{checked: isAllSelected}"></view>
                <text>Select All</text>
            </view>
			<view class="total-info">
				<text>Total:</text>
				<text class="total-price">¥{{ totalPrice }}</text>
			</view>
			<view class="btn-checkout" :class="{disabled: selectedCount === 0}" @click="checkout">
                Checkout ({{ selectedCount }})
            </view>
		</view>
        
        <!-- Tabbar Placeholder -->
        <view style="height: 100rpx;"></view>
	</view>
</template>

<script>
    import { request } from '../../common/api.js';

	export default {
		data() {
			return {
				cartItems: [],
                isAllSelected: false
			}
		},
		onShow() {
            this.loadCart();
		},
        computed: {
            selectedItems() {
                return this.cartItems.filter(item => item.selected);
            },
            selectedCount() {
                return this.selectedItems.length;
            },
            totalPrice() {
                return this.selectedItems.reduce((sum, item) => {
                    return sum + (parseFloat(item.product.price) * item.quantity);
                }, 0).toFixed(2);
            }
        },
		methods: {
            async loadCart() {
                if (!uni.getStorageSync('token')) return;
                try {
                    const res = await request({ url: '/store/cart/' });
                    // Add 'selected' property to each item locally
                    this.cartItems = (res.items || []).map(item => ({
                        ...item,
                        selected: true // Default select all
                    }));
                    this.checkAllSelected();
                } catch (e) {
                    console.error(e);
                }
            },
            goDetail(id) {
                uni.navigateTo({ url: `/pages/product/detail?id=${id}` });
            },
            goShop() {
                uni.switchTab({ url: '/pages/index/index' });
            },
            toggleSelect(item) {
                item.selected = !item.selected;
                this.checkAllSelected();
            },
            toggleSelectAll() {
                this.isAllSelected = !this.isAllSelected;
                this.cartItems.forEach(item => {
                    item.selected = this.isAllSelected;
                });
            },
            checkAllSelected() {
                this.isAllSelected = this.cartItems.length > 0 && this.cartItems.every(item => item.selected);
            },
            async updateQty(item, change) {
                const newQty = item.quantity + change;
                if (newQty < 1) return;

                try {
                    // Optimistic update
                    item.quantity = newQty;
                    
                    await request({
                        url: '/store/cart/update_item/',
                        method: 'POST',
                        data: { item_id: item.id, quantity: newQty }
                    });
                } catch (e) {
                    console.error(e);
                    item.quantity -= change; // Revert on error
                    uni.showToast({ title: 'Update failed', icon: 'none' });
                }
            },
            async removeItem(item) {
                uni.showModal({
                    title: 'Remove Item',
                    content: 'Are you sure you want to remove this item?',
                    success: async (res) => {
                        if (res.confirm) {
                            try {
                                await request({
                                    url: '/store/cart/remove/',
                                    method: 'POST',
                                    data: { item_id: item.id }
                                });
                                this.cartItems = this.cartItems.filter(i => i.id !== item.id);
                                this.checkAllSelected();
                            } catch (e) {
                                console.error(e);
                            }
                        }
                    }
                });
            },
            checkout() {
                if (this.selectedCount === 0) return;
                const selectedIds = this.selectedItems.map(item => item.id);
                uni.setStorageSync('checkout_items', selectedIds);
                uni.navigateTo({ url: '/pages/order/confirm' });
            }
		}
	}
</script>

<style lang="scss">
    .container {
        min-height: 100vh;
        background-color: #f5f5f5;
        padding-bottom: 120rpx;
    }
    .cart-list { padding: 20rpx; }
    .cart-item {
        display: flex;
        align-items: center;
        background-color: #fff;
        border-radius: 16rpx;
        padding: 20rpx;
        margin-bottom: 20rpx;
        position: relative;
        box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.02);
    }
    .item-selector {
        padding-right: 20rpx;
        display: flex;
        align-items: center;
    }
    .radio {
        width: 36rpx;
        height: 36rpx;
        border: 2rpx solid #ccc;
        border-radius: 50%;
        &.checked {
            background-color: #FF5000;
            border-color: #FF5000;
            position: relative;
            &::after {
                content: '';
                position: absolute;
                left: 10rpx;
                top: 6rpx;
                width: 10rpx;
                height: 16rpx;
                border: solid #fff;
                border-width: 0 4rpx 4rpx 0;
                transform: rotate(45deg);
            }
        }
    }
    .item-img {
        width: 160rpx;
        height: 160rpx;
        border-radius: 12rpx;
        overflow: hidden;
        background-color: #f0f0f0;
        margin-right: 20rpx;
        image { width: 100%; height: 100%; }
    }
    .item-info {
        flex: 1;
        height: 160rpx;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .item-name {
        font-size: 28rpx;
        color: #333;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        overflow: hidden;
    }
    .item-sku { font-size: 24rpx; color: #999; }
    .price-qty { display: flex; justify-content: space-between; align-items: center; }
    .item-price { font-size: 32rpx; color: #FF5000; font-weight: bold; }
    .quantity-ctrl {
        display: flex;
        align-items: center;
        border: 1rpx solid #eee;
        border-radius: 8rpx;
    }
    .btn-qty {
        width: 50rpx;
        height: 50rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32rpx;
        color: #666;
        background-color: #f9f9f9;
    }
    .qty { width: 70rpx; text-align: center; font-size: 28rpx; color: #333; }
    .btn-delete {
        position: absolute;
        top: 20rpx;
        right: 20rpx;
        width: 40rpx;
        height: 40rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        .icon-delete { font-size: 40rpx; color: #ccc; line-height: 1; }
    }
    .empty-cart {
        padding-top: 200rpx;
        display: flex;
        flex-direction: column;
        align-items: center;
        .empty-img { width: 200rpx; height: 200rpx; margin-bottom: 30rpx; opacity: 0.5; }
        .empty-text { font-size: 28rpx; color: #999; margin-bottom: 50rpx; }
        .btn-go-shop {
            width: 240rpx;
            height: 70rpx;
            line-height: 70rpx;
            background: linear-gradient(90deg, #FF7A00, #FF5000);
            color: #fff;
            font-size: 28rpx;
            border-radius: 35rpx;
            &::after { border: none; }
        }
    }
    .bottom-bar {
        position: fixed;
        bottom: 0;
        /* #ifdef H5 */
        bottom: 50px;
        /* #endif */
        left: 0; right: 0;
        height: 100rpx;
        background-color: #fff;
        display: flex;
        align-items: center;
        padding: 0 30rpx;
        box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
        z-index: 100;
        .select-all {
            display: flex; align-items: center; font-size: 26rpx; color: #666; margin-right: auto;
            .radio { margin-right: 10rpx; }
        }
        .total-info {
            display: flex; align-items: center; margin-right: 30rpx; font-size: 28rpx; color: #333;
            .total-price { font-size: 34rpx; color: #FF5000; font-weight: bold; margin-left: 10rpx; }
        }
        .btn-checkout {
            width: 200rpx; height: 70rpx;
            background: linear-gradient(90deg, #FF7A00, #FF5000);
            color: #fff; text-align: center; line-height: 70rpx;
            border-radius: 35rpx; font-size: 28rpx; font-weight: bold;
            &.disabled { background: #ccc; }
        }
    }
</style>'''

# 3. Update Address List Vue
addr_list_vue_content = r'''<template>
    <view class="container">
        <view class="address-list">
            <view class="address-item" v-for="(item, index) in list" :key="index" @click="selectAddress(item)">
                <view class="info">
                    <view class="user-row">
                        <text class="name">{{ item.recipient_name }}</text>
                        <text class="phone">{{ item.phone }}</text>
                        <text v-if="item.is_default" class="tag-default">Default</text>
                    </view>
                    <view class="address-row">
                        {{ item.province }} {{ item.city }} {{ item.district }} {{ item.detail_address }}
                    </view>
                </view>
                <view class="actions">
                    <view class="edit-icon" @click.stop="editAddress(item)">
                        <text>Edit</text>
                    </view>
                </view>
            </view>
        </view>
        <view class="empty" v-if="list.length === 0">
            <image src="/static/empty-address.png" mode="aspectFit" class="empty-img"></image>
            <text>No addresses found</text>
        </view>
        
        <view class="footer-btn">
            <view class="btn-add" @click="addAddress">
                <text>+ Add New Address</text>
            </view>
        </view>
    </view>
</template>

<script>
    import { request } from '../../common/api.js';

    export default {
        data() {
            return {
                list: [],
                isSelectMode: false
            }
        },
        onLoad(options) {
            if (options.mode === 'select') {
                this.isSelectMode = true;
                uni.setNavigationBarTitle({ title: 'Select Address' });
            }
        },
        onShow() {
            this.loadData();
        },
        methods: {
            async loadData() {
                try {
                    const res = await request({ url: '/users/addresses/' });
                    this.list = res;
                } catch (e) {
                    console.error(e);
                }
            },
            addAddress() {
                uni.navigateTo({ url: '/pages/address/edit' });
            },
            editAddress(item) {
                uni.navigateTo({ url: `/pages/address/edit?id=${item.id}` });
            },
            selectAddress(item) {
                if (!this.isSelectMode) return;
                
                // Return selected address to previous page
                const pages = getCurrentPages();
                if (pages.length > 1) {
                    const prevPage = pages[pages.length - 2];
                    // Update data on previous page
                    // #ifdef H5
                    if (prevPage.selectedAddress !== undefined) prevPage.selectedAddress = item;
                    // #endif
                    // #ifdef MP-WEIXIN
                    if (prevPage.$vm) prevPage.$vm.selectedAddress = item;
                    // #endif
                    
                    // Also store in global/storage as backup
                    uni.setStorageSync('selected_address', item);
                }
                uni.navigateBack();
            }
        }
    }
</script>

<style lang="scss">
    .container { 
        min-height: 100vh;
        background-color: #f5f5f5;
        padding: 20rpx; 
        padding-bottom: 140rpx; 
    }
    .address-item {
        background: #fff;
        padding: 30rpx;
        margin-bottom: 20rpx;
        border-radius: 16rpx;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.02);
    }
    .info { flex: 1; }
    .user-row { 
        margin-bottom: 12rpx; 
        display: flex; 
        align-items: center;
    }
    .name { font-size: 30rpx; font-weight: bold; color: #333; margin-right: 20rpx; }
    .phone { font-size: 28rpx; color: #666; }
    .tag-default { 
        font-size: 20rpx; color: #FF5000; border: 1px solid #FF5000; 
        padding: 2rpx 8rpx; border-radius: 4rpx; margin-left: 20rpx; 
    }
    .address-row { font-size: 26rpx; color: #999; line-height: 1.4; }
    .actions { padding-left: 30rpx; border-left: 1rpx solid #eee; }
    .edit-icon { 
        color: #999; font-size: 26rpx; 
    }
    .empty {
        padding-top: 200rpx;
        display: flex;
        flex-direction: column;
        align-items: center;
        .empty-img { width: 200rpx; height: 200rpx; margin-bottom: 20rpx; opacity: 0.5; }
        text { color: #999; font-size: 28rpx; }
    }
    .footer-btn {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        padding: 20rpx 30rpx;
        background: #fff;
        box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
        z-index: 10;
        
        .btn-add {
            height: 80rpx;
            background: linear-gradient(90deg, #FF7A00, #FF5000);
            border-radius: 40rpx;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30rpx;
            font-weight: bold;
        }
    }
</style>'''

# 4. Update Address Edit Vue
addr_edit_vue_content = r'''<template>
    <view class="container">
        <view class="form-card">
            <view class="form-item">
                <text class="label">Recipient</text>
                <input class="input" v-model="form.recipient_name" placeholder="Full Name" />
            </view>
            <view class="form-item">
                <text class="label">Phone</text>
                <input class="input" v-model="form.phone" type="number" placeholder="Phone Number" />
            </view>
            <view class="form-item">
                <text class="label">Region</text>
                <picker mode="region" @change="onRegionChange" :value="region">
                    <view class="picker-view">
                        <text v-if="region.length">{{ region[0] }} {{ region[1] }} {{ region[2] }}</text>
                        <text v-else class="placeholder">Select Province/City/District</text>
                    </view>
                </picker>
            </view>
            <view class="form-item">
                <text class="label">Address</text>
                <input class="input" v-model="form.detail_address" placeholder="Street, Apt, etc." />
            </view>
            <view class="form-item switch-item">
                <text class="label">Set as Default</text>
                <switch :checked="form.is_default" @change="onDefaultChange" color="#FF5000" style="transform:scale(0.8)" />
            </view>
        </view>
        
        <view class="footer-btn">
            <view class="btn-save" @click="submit">Save Address</view>
            <view class="btn-delete" v-if="form.id" @click="deleteAddr">Delete</view>
        </view>
    </view>
</template>

<script>
    import { request } from '../../common/api.js';

    export default {
        data() {
            return {
                form: {
                    recipient_name: '',
                    phone: '',
                    province: '',
                    city: '',
                    district: '',
                    detail_address: '',
                    is_default: false
                },
                region: []
            }
        },
        onLoad(options) {
            if (options.id) {
                this.loadData(options.id);
                uni.setNavigationBarTitle({ title: 'Edit Address' });
            } else {
                uni.setNavigationBarTitle({ title: 'New Address' });
            }
        },
        methods: {
            async loadData(id) {
                try {
                    const res = await request({ url: `/users/addresses/${id}/` });
                    this.form = res;
                    this.region = [res.province, res.city, res.district];
                } catch (e) {
                    console.error(e);
                }
            },
            onRegionChange(e) {
                this.region = e.detail.value;
                this.form.province = this.region[0];
                this.form.city = this.region[1];
                this.form.district = this.region[2];
            },
            onDefaultChange(e) {
                this.form.is_default = e.detail.value;
            },
            async submit() {
                if (!this.form.recipient_name || !this.form.phone || !this.form.province || !this.form.detail_address) {
                    uni.showToast({ title: 'Please fill all fields', icon: 'none' });
                    return;
                }
                
                try {
                    const url = this.form.id ? `/users/addresses/${this.form.id}/` : '/users/addresses/';
                    const method = this.form.id ? 'PUT' : 'POST';
                    
                    await request({
                        url: url,
                        method: method,
                        data: this.form
                    });
                    
                    uni.showToast({ title: 'Saved' });
                    setTimeout(() => {
                        uni.navigateBack();
                    }, 1500);
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Save failed', icon: 'none' });
                }
            },
            async deleteAddr() {
                uni.showModal({
                    title: 'Delete Address',
                    content: 'Are you sure?',
                    success: async (res) => {
                        if (res.confirm) {
                            try {
                                await request({
                                    url: `/users/addresses/${this.form.id}/`,
                                    method: 'DELETE'
                                });
                                uni.navigateBack();
                            } catch (e) {
                                console.error(e);
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
        min-height: 100vh;
        background-color: #f5f5f5;
        padding: 20rpx;
    }
    .form-card {
        background: #fff;
        border-radius: 16rpx;
        padding: 0 30rpx;
    }
    .form-item {
        display: flex;
        align-items: center;
        padding: 30rpx 0;
        border-bottom: 1rpx solid #eee;
        &:last-child { border-bottom: none; }
        
        &.switch-item {
            justify-content: space-between;
        }
    }
    .label {
        width: 180rpx;
        font-size: 28rpx;
        color: #333;
    }
    .input {
        flex: 1;
        font-size: 28rpx;
        color: #333;
    }
    .picker-view {
        flex: 1;
        font-size: 28rpx;
        color: #333;
        .placeholder { color: #999; }
    }
    .footer-btn {
        margin-top: 60rpx;
        
        .btn-save {
            height: 88rpx;
            background: linear-gradient(90deg, #FF7A00, #FF5000);
            color: #fff;
            border-radius: 44rpx;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32rpx;
            font-weight: bold;
            margin-bottom: 30rpx;
        }
        
        .btn-delete {
            height: 88rpx;
            background: #fff;
            color: #666;
            border-radius: 44rpx;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32rpx;
        }
    }
</style>'''

# 5. Update Order Confirm Vue
confirm_vue_content = r'''<template>
    <view class="container">
        <!-- Address Section -->
        <view class="address-section" @click="selectAddress">
            <view class="bg-line"></view>
            <view v-if="selectedAddress" class="addr-content">
                <view class="addr-icon">
                    <text class="icon-loc">📍</text>
                </view>
                <view class="addr-info">
                    <view class="user-row">
                        <text class="name">{{ selectedAddress.recipient_name }}</text>
                        <text class="phone">{{ selectedAddress.phone }}</text>
                    </view>
                    <view class="detail">
                        {{ selectedAddress.province }} {{ selectedAddress.city }} {{ selectedAddress.district }} {{ selectedAddress.detail_address }}
                    </view>
                </view>
                <view class="arrow">></view>
            </view>
            <view v-else class="no-address">
                <view class="add-btn">
                    <text class="plus">+</text>
                    <text>Add Shipping Address</text>
                </view>
            </view>
        </view>

        <!-- Order Items -->
        <view class="order-card">
            <view class="card-header">
                <text class="shop-name">SPB Expert Shop</text>
            </view>
            <view class="item" v-for="(item, index) in cartItems" :key="index">
                <image :src="item.product.images[0].image" mode="aspectFill" class="thumb"></image>
                <view class="item-right">
                    <text class="title">{{ item.product.name }}</text>
                    <view class="sku-line">
                        <text class="sku">Default</text>
                        <text class="qty">x{{ item.quantity }}</text>
                    </view>
                    <view class="price-line">
                        <text class="price">¥{{ item.product.price }}</text>
                    </view>
                </view>
            </view>
            
            <view class="cell-row">
                <text class="label">Delivery</text>
                <text class="value">Free Shipping</text>
            </view>
            
            <view class="cell-row">
                <text class="label">Remark</text>
                <input class="input" v-model="remark" placeholder="Optional" />
            </view>
        </view>

        <!-- Summary -->
        <view class="summary-card">
            <view class="row">
                <text>Subtotal</text>
                <text class="price">¥{{ rawTotal }}</text>
            </view>
            <view class="row">
                <text>Shipping</text>
                <text class="price">¥0.00</text>
            </view>
            <view class="row total-row">
                <text>Total</text>
                <text class="total-price">¥{{ totalPrice }}</text>
            </view>
        </view>

        <!-- Footer -->
        <view class="footer-bar">
            <view class="total-info">
                <text>Total:</text>
                <text class="amount">¥{{ totalPrice }}</text>
            </view>
            <view class="btn-submit" @click="submitOrder">Submit Order</view>
        </view>
    </view>
</template>

<script>
    import { request } from '../../common/api.js';

    export default {
        data() {
            return {
                cartItems: [],
                selectedAddress: null,
                remark: ''
            }
        },
        onShow() {
            this.loadCartItems();
            
            // Check if address was selected from address list
            const pages = getCurrentPages();
            const currPage = pages[pages.length - 1];
            // #ifdef H5
            if (currPage.selectedAddress) {
                this.selectedAddress = currPage.selectedAddress;
            }
            // #endif
            
            // Or check storage
            const storedAddr = uni.getStorageSync('selected_address');
            if (storedAddr && !this.selectedAddress) {
                this.selectedAddress = storedAddr;
            }
            
            // If still no address, load default
            if (!this.selectedAddress) {
                this.loadDefaultAddress();
            }
        },
        computed: {
            rawTotal() {
                return this.cartItems.reduce((sum, item) => {
                    return sum + (parseFloat(item.product.price) * item.quantity);
                }, 0).toFixed(2);
            },
            totalPrice() {
                return this.rawTotal; // Add shipping/coupon logic here
            }
        },
        methods: {
            async loadCartItems() {
                // Get selected IDs from storage
                const selectedIds = uni.getStorageSync('checkout_items');
                if (!selectedIds || selectedIds.length === 0) {
                    // Fallback to loading all cart items if none specific
                    // Or redirect back
                    return;
                }
                
                try {
                    const res = await request({ url: '/store/cart/' });
                    // Filter by selectedIds
                    this.cartItems = (res.items || []).filter(item => selectedIds.includes(item.id));
                } catch (e) {
                    console.error(e);
                }
            },
            async loadDefaultAddress() {
                try {
                    const res = await request({ url: '/users/addresses/' });
                    const defaultAddr = res.find(a => a.is_default);
                    if (defaultAddr) {
                        this.selectedAddress = defaultAddr;
                    } else if (res.length > 0) {
                        this.selectedAddress = res[0];
                    }
                } catch (e) {
                    console.error(e);
                }
            },
            selectAddress() {
                uni.navigateTo({ url: '/pages/address/list?mode=select' });
            },
            async submitOrder() {
                if (!this.selectedAddress) {
                    uni.showToast({ title: 'Please select an address', icon: 'none' });
                    return;
                }
                
                try {
                    uni.showLoading({ title: 'Processing...' });
                    
                    // Prepare data
                    const orderData = {
                        address_id: this.selectedAddress.id,
                        remark: this.remark,
                        items: this.cartItems.map(item => item.id) // Pass cart item IDs
                    };
                    
                    // We assume backend has an endpoint to create order from cart items
                    // Standard: POST /store/orders/
                    const res = await request({
                        url: '/store/orders/',
                        method: 'POST',
                        data: orderData
                    });
                    
                    uni.hideLoading();
                    uni.showToast({ title: 'Order Created' });
                    
                    // Clear checkout items
                    uni.removeStorageSync('checkout_items');
                    
                    // Navigate to Pay
                    setTimeout(() => {
                        uni.redirectTo({ url: `/pages/order/pay?order_id=${res.id}&amount=${res.total_amount}` });
                    }, 1000);
                    
                } catch (e) {
                    uni.hideLoading();
                    console.error(e);
                    uni.showToast({ title: 'Order failed', icon: 'none' });
                }
            }
        }
    }
</script>

<style lang="scss">
    .container {
        min-height: 100vh;
        background-color: #f5f5f5;
        padding-bottom: 120rpx;
    }
    
    .address-section {
        background: #fff;
        position: relative;
        margin-bottom: 20rpx;
        
        .bg-line {
            height: 6rpx;
            background: repeating-linear-gradient(-45deg, #ff6c6c 0, #ff6c6c 20%, transparent 0, transparent 25%, #1989fa 0, #1989fa 45%, transparent 0, transparent 50%);
            background-size: 80rpx;
        }
        
        .addr-content {
            padding: 30rpx;
            display: flex;
            align-items: center;
        }
        
        .addr-icon { margin-right: 20rpx; font-size: 40rpx; }
        .addr-info { flex: 1; }
        .user-row { font-size: 30rpx; font-weight: bold; margin-bottom: 10rpx; }
        .phone { margin-left: 20rpx; font-weight: normal; font-size: 28rpx; }
        .detail { font-size: 26rpx; color: #666; line-height: 1.4; }
        .arrow { color: #999; }
        
        .no-address {
            padding: 40rpx;
            display: flex;
            justify-content: center;
            .add-btn {
                display: flex; align-items: center; color: #FF5000; font-size: 30rpx;
                .plus { font-size: 40rpx; margin-right: 10rpx; }
            }
        }
    }
    
    .order-card, .summary-card {
        background: #fff;
        margin: 20rpx;
        border-radius: 16rpx;
        overflow: hidden;
        padding: 20rpx;
    }
    
    .card-header {
        padding-bottom: 20rpx;
        border-bottom: 1rpx solid #f5f5f5;
        margin-bottom: 20rpx;
        .shop-name { font-weight: bold; font-size: 28rpx; }
    }
    
    .item {
        display: flex;
        margin-bottom: 20rpx;
        .thumb { width: 140rpx; height: 140rpx; border-radius: 8rpx; margin-right: 20rpx; background: #f0f0f0; }
        .item-right { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .title { font-size: 26rpx; color: #333; line-height: 1.4; }
        .sku-line { display: flex; justify-content: space-between; color: #999; font-size: 24rpx; }
        .price-line { display: flex; justify-content: flex-end; }
        .price { color: #333; font-weight: bold; font-size: 28rpx; }
    }
    
    .cell-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20rpx 0;
        border-top: 1rpx solid #f9f9f9;
        font-size: 28rpx;
        .label { color: #333; }
        .value { color: #666; }
        .input { text-align: right; color: #333; flex: 1; margin-left: 20rpx; }
    }
    
    .summary-card {
        .row {
            display: flex; justify-content: space-between; margin-bottom: 10rpx; font-size: 26rpx; color: #666;
            &.total-row { margin-top: 20rpx; font-size: 30rpx; color: #333; font-weight: bold; }
        }
    }
    
    .footer-bar {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        height: 100rpx;
        background: #fff;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding: 0 30rpx;
        box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
        z-index: 100;
        
        .total-info {
            display: flex; align-items: center; margin-right: 30rpx; font-size: 28rpx;
            .amount { color: #FF5000; font-size: 36rpx; font-weight: bold; margin-left: 10rpx; }
        }
        
        .btn-submit {
            width: 220rpx; height: 72rpx;
            background: linear-gradient(90deg, #FF7A00, #FF5000);
            color: #fff;
            border-radius: 36rpx;
            text-align: center;
            line-height: 72rpx;
            font-size: 28rpx;
            font-weight: bold;
        }
    }
</style>'''

def update_file(path, content):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")
    except Exception as e:
        print(f"Error updating {path}: {e}")

if __name__ == "__main__":
    fix_pages_json()
    update_file(CART_VUE_PATH, cart_vue_content)
    update_file(ADDR_LIST_VUE_PATH, addr_list_vue_content)
    update_file(ADDR_EDIT_VUE_PATH, addr_edit_vue_content)
    update_file(CONFIRM_VUE_PATH, confirm_vue_content)
    print("All updates complete.")
