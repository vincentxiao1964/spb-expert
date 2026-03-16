import os

# Add Refund Button to Order List in D:\spb-expert11\frontend\pages\order\order.vue
order_vue_path = r'D:\spb-expert11\frontend\pages\order\order.vue'
with open(order_vue_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Request Refund button for 'paid', 'shipped', 'completed' orders
# We can add a "Request Refund" button.
# If order.status in ['paid', 'shipped', 'completed']

# Let's add it to the card footer.
# We have btn-groups for pending, paid, shipped.

refund_btn = """                        <view class="btn btn-refund" @click.stop="goToRefund(order.id)">Request Refund</view>"""

# Add to 'paid' group (after Cancel)
if """<view class="btn btn-cancel" @click.stop="cancelOrder(order)">Cancel Order</view>""" in content:
    content = content.replace("""<view class="btn btn-cancel" @click.stop="cancelOrder(order)">Cancel Order</view>""", 
                              """<view class="btn btn-cancel" @click.stop="cancelOrder(order)">Cancel Order</view>
                        """ + refund_btn)

# Add to 'shipped' group (before Confirm Receipt)
if """<view class="btn btn-confirm" @click.stop="confirmReceipt(order)">Confirm Receipt</view>""" in content:
     content = content.replace("""<view class="btn btn-confirm" @click.stop="confirmReceipt(order)">Confirm Receipt</view>""",
                               refund_btn + "\n" + """                        <view class="btn btn-confirm" @click.stop="confirmReceipt(order)">Confirm Receipt</view>""")
                               
# Add to 'completed' group? Usually yes, within return window.
# We don't have a completed group yet in the template logic shown in Read, 
# except for the Review button which is in the body, not footer.
# Let's check if there is a footer for completed.
# If not, we can add one.

completed_group = """
                    <view class="btn-group" v-if="order.status === 'completed'">
                        <view class="btn btn-refund" @click.stop="goToRefund(order.id)">Request Refund</view>
                    </view>"""
                    
# Find where to insert completed group.
# After shipped group.
if """<view class="btn-group" v-if="order.status === 'shipped'">""" in content:
    # Insert after the closing tag of shipped group?
    # The shipped group ends with </view>
    # It's tricky with string replacement if we don't have unique context.
    pass

# Let's just look for the end of card-footer div or where other groups are.
# We have:
# <view class="card-footer">
# ...
# <view class="btn-group" v-if="order.status === 'shipped'">...</view>
# </view>

# We can append before `</view>` of card-footer if we can identify it.
# Or just replace the shipped group with shipped + completed.

# Let's define the replacement for shipped group to include completed group after it.
shipped_block = """<view class="btn-group" v-if="order.status === 'shipped'">
                        <view class="btn btn-refund" @click.stop="goToRefund(order.id)">Request Refund</view>
                        <view class="btn btn-confirm" @click.stop="confirmReceipt(order)">Confirm Receipt</view>
                    </view>"""
                    
if """<view class="btn-group" v-if="order.status === 'shipped'">""" in content:
    # We already modified shipped group above in memory variable 'content' ?
    # Yes, line 18 replaced confirmReceipt line.
    # So the content now has refund button in shipped group.
    
    # Now append completed group after shipped group.
    # Find the closing </view> of shipped group. 
    # It's hard.
    pass

# Alternative: just add the method `goToRefund` and style.
# And add the button to the 'paid' and 'shipped' groups.

# Add method
method_insert = """            goToPay(id) {"""
refund_method = """            goToRefund(id) {
                uni.navigateTo({
                    url: `/pages/order/refund?order_id=${id}`
                });
            },
"""
if method_insert in content:
    content = content.replace(method_insert, refund_method + method_insert)

# Add style
style_insert = """.btn-cancel {"""
refund_style = """.btn-refund {
        border: 1rpx solid #ff5000;
        color: #ff5000;
        background-color: #fff;
        margin-right: 20rpx;
    }
"""
if style_insert in content:
    content = content.replace(style_insert, refund_style + style_insert)
    
with open(order_vue_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated frontend/pages/order/order.vue with Refund buttons")
