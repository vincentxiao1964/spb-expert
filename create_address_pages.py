
import os
import json

# Define paths
BASE_DIR = r"D:\spb-expert11\frontend"
PAGES_JSON_PATH = os.path.join(BASE_DIR, "pages.json")
ADDRESS_DIR = os.path.join(BASE_DIR, "pages", "address")
ORDER_DIR = os.path.join(BASE_DIR, "pages", "order")
CART_VUE_PATH = os.path.join(BASE_DIR, "pages", "cart", "cart.vue")

# Ensure directories exist
os.makedirs(ADDRESS_DIR, exist_ok=True)
os.makedirs(ORDER_DIR, exist_ok=True)

# 1. Create Address List Page
address_list_content = """<template>
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
                <view class="edit-icon" @click.stop="editAddress(item)">
                    <text>Edit</text>
                </view>
            </view>
        </view>
        <view class="empty" v-if="list.length === 0">
            <text>No addresses found</text>
        </view>
        
        <view class="btn-add" @click="addAddress">
            <text>+ Add New Address</text>
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
                const prevPage = pages[pages.length - 2];
                // Check if prevPage has a callback or setData
                // In Uni-app/Vue, we can use event bus or global store, but simple way:
                if (prevPage.$vm) {
                    prevPage.$vm.selectedAddress = item;
                }
                uni.navigateBack();
            }
        }
    }
</script>

<style>
    .container { padding: 20rpx; padding-bottom: 100rpx; }
    .address-item {
        background: #fff;
        padding: 30rpx;
        margin-bottom: 20rpx;
        border-radius: 10rpx;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .info { flex: 1; }
    .user-row { margin-bottom: 10rpx; font-weight: bold; }
    .name { margin-right: 20rpx; }
    .tag-default { 
        font-size: 20rpx; color: #ff0000; border: 1px solid #ff0000; 
        padding: 2rpx 8rpx; border-radius: 4rpx; margin-left: 20rpx; 
    }
    .address-row { font-size: 26rpx; color: #666; }
    .edit-icon { 
        padding-left: 20rpx; border-left: 1px solid #eee; color: #999; font-size: 24rpx; 
    }
    .btn-add {
        position: fixed; bottom: 0; left: 0; right: 0;
        height: 100rpx; line-height: 100rpx; text-align: center;
        background: #3cc51f; color: #fff; font-size: 32rpx;
    }
    .empty { text-align: center; margin-top: 100rpx; color: #999; }
</style>
"""

with open(os.path.join(ADDRESS_DIR, "list.vue"), "w", encoding="utf-8") as f:
    f.write(address_list_content)
print("Created list.vue")

# 2. Create Address Edit Page
address_edit_content = """<template>
    <view class="container">
        <form @submit="formSubmit">
            <view class="form-item">
                <text class="label">Recipient</text>
                <input class="input" name="recipient_name" v-model="form.recipient_name" placeholder="Name" />
            </view>
            <view class="form-item">
                <text class="label">Phone</text>
                <input class="input" name="phone" v-model="form.phone" placeholder="Mobile Number" />
            </view>
            <view class="form-item">
                <text class="label">Region</text>
                <!-- Simplified for MVP: Text inputs or simple picker -->
                <view class="region-inputs">
                    <input class="input-sm" v-model="form.province" placeholder="Province" />
                    <input class="input-sm" v-model="form.city" placeholder="City" />
                    <input class="input-sm" v-model="form.district" placeholder="District" />
                </view>
            </view>
            <view class="form-item">
                <text class="label">Detail</text>
                <input class="input" name="detail_address" v-model="form.detail_address" placeholder="Street, Building, Room" />
            </view>
            <view class="form-item row-between">
                <text class="label">Set as Default</text>
                <switch :checked="form.is_default" @change="switchChange" />
            </view>
            
            <button form-type="submit" class="btn-submit">Save</button>
            <button v-if="form.id" @click="deleteAddress" class="btn-delete">Delete</button>
        </form>
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
                }
            }
        },
        onLoad(options) {
            if (options.id) {
                this.loadAddress(options.id);
            }
        },
        methods: {
            async loadAddress(id) {
                try {
                    const res = await request({ url: `/users/addresses/${id}/` });
                    this.form = res;
                } catch (e) {
                    console.error(e);
                }
            },
            switchChange(e) {
                this.form.is_default = e.detail.value;
            },
            async formSubmit() {
                if (!this.form.recipient_name || !this.form.phone || !this.form.detail_address) {
                    uni.showToast({ title: 'Please fill required fields', icon: 'none' });
                    return;
                }
                
                try {
                    let url = '/users/addresses/';
                    let method = 'POST';
                    if (this.form.id) {
                        url += `${this.form.id}/`;
                        method = 'PUT';
                    }
                    
                    await request({
                        url: url,
                        method: method,
                        data: this.form
                    });
                    
                    uni.showToast({ title: 'Saved' });
                    setTimeout(() => uni.navigateBack(), 1000);
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Save failed', icon: 'none' });
                }
            },
            async deleteAddress() {
                try {
                    await request({
                        url: `/users/addresses/${this.form.id}/`,
                        method: 'DELETE'
                    });
                    uni.showToast({ title: 'Deleted' });
                    setTimeout(() => uni.navigateBack(), 1000);
                } catch (e) {
                    console.error(e);
                }
            }
        }
    }
</script>

<style>
    .container { padding: 30rpx; }
    .form-item {
        margin-bottom: 30rpx; border-bottom: 1px solid #eee; padding-bottom: 20rpx;
    }
    .label { width: 160rpx; display: inline-block; font-size: 28rpx; color: #333; }
    .input { display: inline-block; width: 500rpx; vertical-align: middle; }
    .region-inputs { display: flex; gap: 10rpx; }
    .input-sm { flex: 1; border: 1px solid #eee; padding: 10rpx; font-size: 24rpx; }
    .row-between { display: flex; justify-content: space-between; align-items: center; }
    .btn-submit { background: #3cc51f; color: #fff; margin-top: 50rpx; }
    .btn-delete { background: #f5f5f5; color: #ff0000; margin-top: 20rpx; }
</style>
"""

with open(os.path.join(ADDRESS_DIR, "edit.vue"), "w", encoding="utf-8") as f:
    f.write(address_edit_content)
print("Created edit.vue")

# 3. Create Order Confirmation Page
confirm_content = """<template>
    <view class="container">
        <!-- Address Section -->
        <view class="address-section" @click="selectAddress">
            <view v-if="selectedAddress" class="has-address">
                <view class="user-info">
                    <text class="name">{{ selectedAddress.recipient_name }}</text>
                    <text class="phone">{{ selectedAddress.phone }}</text>
                </view>
                <view class="addr-info">
                    {{ selectedAddress.province }} {{ selectedAddress.city }} {{ selectedAddress.district }} {{ selectedAddress.detail_address }}
                </view>
            </view>
            <view v-else class="no-address">
                <text>+ Select Shipping Address</text>
            </view>
            <view class="arrow">></view>
        </view>

        <!-- Order Items -->
        <view class="order-items">
            <view class="item" v-for="(item, index) in cartItems" :key="index">
                <view class="item-name">{{ item.product_name || item.product.name }}</view>
                <view class="item-meta">
                    <text class="price">¥{{ item.product_price || item.product.price }}</text>
                    <text class="qty">x{{ item.quantity }}</text>
                </view>
            </view>
        </view>

        <!-- Summary -->
        <view class="summary">
            <view class="row">
                <text>Total Amount</text>
                <text class="price">¥{{ totalPrice }}</text>
            </view>
        </view>

        <!-- Footer -->
        <view class="footer">
            <view class="total">Total: ¥{{ totalPrice }}</view>
            <view class="btn-pay" @click="submitOrder">Place Order</view>
        </view>
    </view>
</template>

<script>
    import { request } from '../../common/api.js';

    export default {
        data() {
            return {
                cartItems: [],
                selectedAddress: null
            }
        },
        onShow() {
            // Re-fetch cart items or load from storage
            // If we came back from Address Select, this.selectedAddress might be set by page stack manipulation
            // But let's check if we need to load cart
            if (this.cartItems.length === 0) {
                this.loadCart();
            }
            // If no address selected, try to load default
            if (!this.selectedAddress) {
                this.loadDefaultAddress();
            }
        },
        computed: {
            totalPrice() {
                return this.cartItems.reduce((sum, item) => {
                    const price = item.product_price || (item.product ? item.product.price : 0);
                    return sum + (parseFloat(price) * item.quantity);
                }, 0).toFixed(2);
            }
        },
        methods: {
            async loadCart() {
                try {
                    // For now, assuming we are checking out the WHOLE cart
                    // Real world: pass selected item IDs
                    const res = await request({ url: '/store/cart/' });
                    this.cartItems = res.items || res; // Handle if serializer returns object or list
                } catch (e) {
                    console.error(e);
                }
            },
            async loadDefaultAddress() {
                try {
                    const res = await request({ url: '/users/addresses/' });
                    if (res && res.length > 0) {
                        const defaultAddr = res.find(a => a.is_default);
                        this.selectedAddress = defaultAddr || res[0];
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
                    const res = await request({
                        url: '/store/orders/create_order/',
                        method: 'POST',
                        data: {
                            address_id: this.selectedAddress.id
                        }
                    });
                    
                    uni.showToast({ title: 'Order Placed!' });
                    // Navigate to Order List or Payment
                    setTimeout(() => {
                        uni.redirectTo({ url: '/pages/order/order' });
                    }, 1500);
                    
                } catch (e) {
                    console.error(e);
                    uni.showToast({ title: 'Order Failed', icon: 'none' });
                }
            }
        }
    }
</script>

<style>
    .container { padding-bottom: 120rpx; background: #f5f5f5; min-height: 100vh; }
    .address-section {
        background: #fff; padding: 30rpx; display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20rpx;
    }
    .user-info { font-weight: bold; margin-bottom: 10rpx; }
    .addr-info { color: #666; font-size: 26rpx; }
    .no-address { color: #f00; }
    .order-items { background: #fff; padding: 20rpx; margin-bottom: 20rpx; }
    .item { display: flex; justify-content: space-between; padding: 20rpx 0; border-bottom: 1px solid #eee; }
    .footer {
        position: fixed; bottom: 0; width: 100%; height: 100rpx; background: #fff;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
    }
    .total { padding-left: 30rpx; font-weight: bold; color: #f00; }
    .btn-pay {
        background: #f00; color: #fff; height: 100%; width: 250rpx;
        display: flex; align-items: center; justify-content: center;
    }
</style>
"""

with open(os.path.join(ORDER_DIR, "confirm.vue"), "w", encoding="utf-8") as f:
    f.write(confirm_content)
print("Created confirm.vue")

# 4. Update pages.json
with open(PAGES_JSON_PATH, 'r', encoding='utf-8') as f:
    pages_config = json.load(f)

new_pages = [
    {
        "path": "pages/address/list",
        "style": {
            "navigationBarTitleText": "My Addresses"
        }
    },
    {
        "path": "pages/address/edit",
        "style": {
            "navigationBarTitleText": "Edit Address"
        }
    },
    {
        "path": "pages/order/confirm",
        "style": {
            "navigationBarTitleText": "Confirm Order"
        }
    }
]

# Check if pages already exist
existing_paths = [p['path'] for p in pages_config['pages']]
for page in new_pages:
    if page['path'] not in existing_paths:
        pages_config['pages'].append(page)

with open(PAGES_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(pages_config, f, indent=4, ensure_ascii=False)
print("Updated pages.json")

# 5. Update Cart Vue to redirect to confirm
with open(CART_VUE_PATH, 'r', encoding='utf-8') as f:
    cart_content = f.read()

# Replace the checkout method body
if "async checkout() {" in cart_content:
    # A simple regex or string replace might be tricky if content varies, 
    # but based on previous read, we know the structure.
    # We will replace the whole method block if we can find a unique enough string.
    # Or just replace the inside.
    
    target_str = """async checkout() {
                // 1. Get Address (Mocking: fetch list and pick first)
                let addressId = null;"""
    
    new_str = """async checkout() {
                uni.navigateTo({ url: '/pages/order/confirm' });"""
    
    if target_str in cart_content:
        cart_content = cart_content.replace(target_str, new_str)
        with open(CART_VUE_PATH, 'w', encoding='utf-8') as f:
            f.write(cart_content)
        print("Updated cart.vue")
    else:
        print("Could not match checkout method in cart.vue exactly, manual check needed.")
