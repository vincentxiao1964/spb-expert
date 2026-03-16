
import os

file_path = r"d:\spb-expert11\frontend\pages\product\detail.vue"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Modify addToCart to return id
    old_add = """                    await request({
                        url: '/store/cart/',
                        method: 'POST',
                        data: { product_id: this.id, quantity: 1 }
                    });
                    uni.showToast({ title: 'Added to Cart' });"""

    new_add = """                    const res = await request({
                        url: '/store/cart/',
                        method: 'POST',
                        data: { product_id: this.id, quantity: 1 }
                    });
                    uni.showToast({ title: 'Added to Cart' });
                    return res.cart_item_id;"""

    if old_add in content:
        content = content.replace(old_add, new_add)
    else:
        print("Could not find addToCart pattern")

    # 2. Modify buyNow to use id
    old_buy = """                this.addToCart().then(() => {
                    uni.navigateTo({ url: '/pages/order/confirm' });
                });"""

    new_buy = """                this.addToCart().then((itemId) => {
                    if (itemId) {
                        uni.setStorageSync('checkout_items', [itemId]);
                        uni.navigateTo({ url: '/pages/order/confirm' });
                    }
                });"""

    if old_buy in content:
        content = content.replace(old_buy, new_buy)
    else:
        print("Could not find buyNow pattern")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated detail.vue")

except Exception as e:
    print(f"Error: {e}")
