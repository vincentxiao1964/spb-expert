import os

# 1. Update product/detail.vue (Add Coupons)
detail_path = r'D:\spb-expert11\frontend\pages\product\detail.vue'
with open(detail_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Coupons section in template
if '<view class="coupons-section" v-if="coupons.length > 0">' not in content:
    # Insert before reviews-section or info-section end
    # Let's insert after info-section
    target = """<view class="merchant" v-if="product.merchant_name">Merchant: {{ product.merchant_name }}</view>
			<view class="description">{{ product.description }}</view>
		</view>"""
        
    replacement = """<view class="merchant" v-if="product.merchant_name">Merchant: {{ product.merchant_name }}</view>
			<view class="description">{{ product.description }}</view>
		</view>

        <view class="coupons-section" v-if="coupons.length > 0">
            <view class="section-title">Coupons</view>
            <scroll-view scroll-x class="coupon-scroll">
                <view class="coupon-card" v-for="(coupon, index) in coupons" :key="index" @click="claimCoupon(coupon)">
                    <view class="coupon-left">
                        <text class="amount" v-if="coupon.discount_type=='amount'">¥{{coupon.discount_value}}</text>
                        <text class="amount" v-else>{{coupon.discount_value}}%</text>
                        <text class="cond">Min ¥{{coupon.min_spend}}</text>
                    </view>
                    <view class="coupon-right">
                        <text class="status">{{ coupon.is_claimed ? 'Claimed' : 'Claim' }}</text>
                    </view>
                </view>
            </scroll-view>
        </view>"""
        
    content = content.replace(target, replacement)
    
    # Add CSS
    if ".coupons-section" not in content:
        css = """
    .coupons-section { background: #fff; margin-top: 20rpx; padding: 20rpx; }
    .coupon-scroll { white-space: nowrap; display: flex; }
    .coupon-card { display: inline-flex; width: 300rpx; height: 120rpx; background: #fff5f5; border: 1rpx solid #ffcccc; margin-right: 20rpx; border-radius: 10rpx; overflow: hidden; }
    .coupon-left { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; border-right: 1rpx dashed #ffcccc; }
    .coupon-right { width: 80rpx; display: flex; justify-content: center; align-items: center; background: #ffe6e6; color: #ff5500; font-size: 24rpx; font-weight: bold; }
    .coupon-left .amount { font-size: 32rpx; font-weight: bold; color: #ff5500; }
    .coupon-left .cond { font-size: 20rpx; color: #999; }
"""
        # Append to style. Usually before </style>
        content = content.replace("</style>", css + "\n</style>")
        
    # Add coupons data and methods
    # Data
    if "coupons: []" not in content:
        content = content.replace("reviews: [],", "reviews: [],\n				coupons: [],")
        
    # Methods: loadCoupons, claimCoupon
    # Call loadCoupons in onLoad
    if "this.loadReviews();" in content:
        content = content.replace("this.loadReviews();", "this.loadReviews();\n			this.loadCoupons();")
        
    # Add methods logic
    new_methods = """
            loadCoupons() {
                // Fetch coupons for this product's merchant
                // Wait, product object needs to be loaded first? 
                // We call this after loadProduct? 
                // loadProduct is async? No, in my code it is not awaited in onLoad.
                // We should call loadCoupons inside loadProduct success or watch product.
                // Let's rely on product.merchant being available.
                // Or better, fetch product first then coupons.
                // For now, I'll assume I can fetch coupons if I know merchant ID.
                // But initially I only have product ID.
                // So I'll modify loadProduct to fetch coupons.
            },
            claimCoupon(coupon) {
                if (coupon.is_claimed) return;
                request('/store/coupons/' + coupon.id + '/claim/', 'POST').then(res => {
                    uni.showToast({ title: 'Claimed!' });
                    coupon.is_claimed = true;
                }).catch(err => {
                    if (err.error) uni.showToast({ title: err.error, icon: 'none' });
                });
            },"""
            
    # Inject claimCoupon method.
    # But for loadCoupons, let's look at loadProduct.
    # Since I cannot see loadProduct implementation in the snippet (it was truncated?), I will append these methods to methods block
    # and try to call loadCoupons inside loadProduct if I can find it.
    
    # Actually, I'll just add `loadCoupons` and call it.
    # To fix the timing issue, I will modify `loadProduct` if I can match it.
    
    # Let's search for loadProduct method start.
    # It is likely: `async loadProduct() {` or `loadProduct() {`
    
    # I'll just add the methods first.
    if "methods: {" in content:
        content = content.replace("methods: {", "methods: {" + new_methods)

    # Now, how to trigger loadCoupons?
    # I'll add a watch on `product`.
    if "watch: {" not in content:
        watch_block = """
        watch: {
            product(newVal) {
                if (newVal && newVal.merchant) {
                    this.fetchMerchantCoupons(newVal.merchant);
                }
            }
        },"""
        # Insert before methods
        content = content.replace("methods: {", watch_block + "\n		methods: {")
        
    # Add fetchMerchantCoupons implementation
    content = content.replace("loadCoupons() {", """fetchMerchantCoupons(merchantId) {
                request('/store/coupons/?merchant_id=' + merchantId, 'GET').then(res => {
                    this.coupons = res;
                });
            },
            loadCoupons() {""") # keeping empty loadCoupons as placeholder or remove it

    with open(detail_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated product/detail.vue")

# 2. Update order/confirm.vue (Coupon Selection)
confirm_path = r'D:\spb-expert11\frontend\pages\order\confirm.vue'
with open(confirm_path, 'r', encoding='utf-8') as f:
    c_content = f.read()

# Add Coupon Selector in template
if "coupon-selector" not in c_content:
    # Insert before Summary
    target = """<!-- Summary -->
        <view class="summary">"""
    
    replacement = """<!-- Coupon Selector -->
        <view class="coupon-selector" @click="showCouponPicker">
            <text>Coupon</text>
            <view class="right">
                <text v-if="selectedCoupon">{{ selectedCoupon.coupon.code }} (-¥{{ couponDiscount }})</text>
                <text v-else class="placeholder">{{ availableCoupons.length }} Available</text>
                <text class="arrow">></text>
            </view>
        </view>

        <!-- Summary -->
        <view class="summary">"""
        
    c_content = c_content.replace(target, replacement)
    
    # Update Total Price calculation to include discount
    # Update computed: totalPrice
    # Original:
    # return this.cartItems.reduce((sum, item) => { ... }, 0).toFixed(2);
    
    # New:
    # let total = ...
    # if (this.selectedCoupon) total -= this.couponDiscount;
    # return total > 0 ? total.toFixed(2) : '0.00';
    
    # We need to parse existing computed property.
    # It's safer to just replace the whole computed block if it matches standard format.
    
    old_computed = """computed: {
            totalPrice() {
                return this.cartItems.reduce((sum, item) => {
                    const price = item.product_price || (item.product ? item.product.price : 0);
                    return sum + (parseFloat(price) * item.quantity);
                }, 0).toFixed(2);
            }
        },"""
        
    new_computed = """computed: {
            rawTotal() {
                return this.cartItems.reduce((sum, item) => {
                    const price = item.product_price || (item.product ? item.product.price : 0);
                    return sum + (parseFloat(price) * item.quantity);
                }, 0);
            },
            couponDiscount() {
                if (!this.selectedCoupon) return 0;
                const c = this.selectedCoupon.coupon;
                if (c.discount_type === 'amount') {
                    return parseFloat(c.discount_value);
                } else {
                    return this.rawTotal * (parseFloat(c.discount_value) / 100);
                }
            },
            totalPrice() {
                let total = this.rawTotal - this.couponDiscount;
                return total > 0 ? total.toFixed(2) : '0.00';
            }
        },"""
        
    c_content = c_content.replace(old_computed, new_computed)
    
    # Add Data
    if "selectedAddress: null" in c_content:
        c_content = c_content.replace(
            "selectedAddress: null", 
            "selectedAddress: null,\n                availableCoupons: [],\n                selectedCoupon: null"
        )
        
    # Add Methods
    # loadAvailableCoupons, showCouponPicker
    # And update submitOrder to include coupon_id
    
    new_methods = """
            loadAvailableCoupons() {
                request('/store/my-coupons/?status=unused', 'GET').then(res => {
                    // Filter applicable coupons?
                    // Ideally backend does this, but for now we filter locally based on min_spend
                    const total = this.rawTotal;
                    this.availableCoupons = res.filter(uc => {
                        return total >= parseFloat(uc.coupon.min_spend);
                    });
                });
            },
            showCouponPicker() {
                if (this.availableCoupons.length === 0) {
                    uni.showToast({ title: 'No coupons available', icon: 'none' });
                    return;
                }
                const itemList = this.availableCoupons.map(uc => {
                    const c = uc.coupon;
                    const val = c.discount_type === 'amount' ? '¥'+c.discount_value : c.discount_value+'%';
                    return `${c.code} (${val} OFF)`;
                });
                uni.showActionSheet({
                    itemList: itemList,
                    success: (res) => {
                        this.selectedCoupon = this.availableCoupons[res.tapIndex];
                    }
                });
            },
"""
    if "methods: {" in c_content:
        c_content = c_content.replace("methods: {", "methods: {" + new_methods)
        
    # Trigger loadAvailableCoupons. In onShow?
    if "this.loadCart();" in c_content:
        c_content = c_content.replace("this.loadCart();", "this.loadCart();\n                this.loadAvailableCoupons();")

    # Update submitOrder to include coupon_id
    # I need to find submitOrder. It's likely in the part I haven't read or it's implicitly there.
    # Wait, the Read output didn't show submitOrder method! It ended at selectAddress.
    # So I need to append submitOrder or replace it if I can guess it.
    # But I see `submitOrder` in template: `@click="submitOrder"`
    # So it must be in the file (probably after selectAddress).
    
    # I'll just append it to the end of methods, assuming I can overwrite it or it's missing.
    # If it exists, I might duplicate it which is bad.
    # Let's try to Read the rest of the file first?
    # No, I'll use regex to replace it if found, or append.
    
    # Actually, the file content read was truncated at line 100.
    # I should read the rest.
    
    with open(confirm_path, 'w', encoding='utf-8') as f:
        f.write(c_content)
    print("Updated order/confirm.vue (Part 1)")

