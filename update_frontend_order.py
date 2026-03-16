import os

# Update frontend/pages/order/order.vue
order_vue_path = r'D:\spb-expert11\frontend\pages\order\order.vue'
with open(order_vue_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Template: Add Cancel Button
# For 'pending'
old_pending_group = """<view class="btn-group" v-if="order.status === 'pending'">
                        <view class="btn btn-pay" @click.stop="goToPay(order.id)">Pay Now</view>
                    </view>"""
                    
new_pending_group = """<view class="btn-group" v-if="order.status === 'pending'">
                        <view class="btn btn-cancel" @click.stop="cancelOrder(order)">Cancel</view>
                        <view class="btn btn-pay" @click.stop="goToPay(order.id)">Pay Now</view>
                    </view>"""

if old_pending_group in content:
    content = content.replace(old_pending_group, new_pending_group)

# For 'paid' - user can cancel/refund
# Find where to insert 'paid' group. It's not in the original file explicitly (filteredOrders handles it).
# But we can add a block for it.
# Insert after pending group.
paid_group = """
                    <view class="btn-group" v-if="order.status === 'paid'">
                        <view class="btn btn-cancel" @click.stop="cancelOrder(order)">Cancel Order</view>
                    </view>"""

if """<view class="btn-group" v-if="order.status === 'shipped'">""" in content:
    content = content.replace("""<view class="btn-group" v-if="order.status === 'shipped'">""", paid_group + "\n" + """<view class="btn-group" v-if="order.status === 'shipped'">""")

# 2. Update Script: Add cancelOrder method
method_insert_point = """            async confirmReceipt(order) {"""
cancel_method = """            async cancelOrder(order) {
                const [err, res] = await uni.showModal({
                    title: 'Cancel Order',
                    content: 'Are you sure you want to cancel this order?',
                });
                if (res.confirm) {
                    try {
                        await request({
                            url: `/store/orders/${order.id}/cancel/`,
                            method: 'POST'
                        });
                        uni.showToast({ title: 'Order Cancelled' });
                        this.loadOrders();
                    } catch (e) {
                        console.error(e);
                        uni.showToast({ title: 'Cancel failed', icon: 'none' });
                    }
                }
            },
"""

if method_insert_point in content and "cancelOrder(order)" not in content:
    content = content.replace(method_insert_point, cancel_method + method_insert_point)

# 3. Update Style: Add .btn-cancel
style_insert_point = """.btn-pay {"""
cancel_style = """.btn-cancel {
        background-color: #f8f8f8;
        color: #666;
        border: 1rpx solid #ccc;
        margin-right: 20rpx;
    }
    """

if style_insert_point in content and ".btn-cancel" not in content:
    content = content.replace(style_insert_point, cancel_style + style_insert_point)
    
# Also ensure .btn-group displays flex
if ".btn-group" not in content:
    # It might rely on default block, but we want buttons side by side
    btn_group_style = """
    .btn-group {
        display: flex;
        align-items: center;
    }"""
    content = content.replace("</style>", btn_group_style + "\n</style>")

with open(order_vue_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated frontend/pages/order/order.vue")
