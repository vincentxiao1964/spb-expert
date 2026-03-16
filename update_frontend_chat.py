import os

chat_vue_path = r'D:\spb-expert11\frontend\pages\chat\chat.vue'
with open(chat_vue_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Template
# Add Plus Button
if '<view class="btn-plus"' not in content:
    content = content.replace(
        '<input class="input" v-model="content" placeholder="Type a message..." confirm-type="send" @confirm="sendMsg" />',
        '<view class="btn-plus" @click="chooseImage">+</view>\n            <input class="input" v-model="content" placeholder="Type a message..." confirm-type="send" @confirm="sendMsg" />'
    )

# Update Bubble to show Image
if '<image v-if="msg.image"' not in content:
    target_bubble = '<text>{{ msg.content }}</text>'
    new_bubble = """<image v-if="msg.image" :src="msg.image" mode="widthFix" class="msg-image" @click="previewImage(msg.image)"></image>
                        <text v-if="msg.content">{{ msg.content }}</text>"""
    content = content.replace(target_bubble, new_bubble)

# 2. Update Script
# Add Methods
if 'chooseImage() {' not in content:
    methods_start = 'methods: {'
    new_methods = """methods: {
            chooseImage() {
                uni.chooseImage({
                    count: 1,
                    success: (res) => {
                        const tempFilePaths = res.tempFilePaths;
                        this.uploadImage(tempFilePaths[0]);
                    }
                });
            },
            uploadImage(filePath) {
                const token = uni.getStorageSync('token');
                uni.uploadFile({
                    url: 'http://127.0.0.1:8000/api/v1/users/messages/',
                    filePath: filePath,
                    name: 'image',
                    header: {
                        'Authorization': 'Bearer ' + token
                    },
                    formData: {
                        'receiver': this.targetId,
                        'content': '' // Optional: allow caption later
                    },
                    success: (uploadFileRes) => {
                        const data = JSON.parse(uploadFileRes.data);
                        this.messages.push(data);
                        this.scrollToBottom();
                    },
                    fail: (err) => {
                        console.error(err);
                        uni.showToast({ title: 'Image send failed', icon: 'none' });
                    }
                });
            },
            previewImage(url) {
                uni.previewImage({
                    urls: [url]
                });
            },
"""
    content = content.replace(methods_start, new_methods)

# 3. Update Styles
if '.btn-plus' not in content:
    style_end = '</style>'
    # Note: assuming style tag exists, but file read didn't show it. 
    # Let's check if style tag exists, usually at the end.
    # If not, append it.
    if '</style>' in content:
        new_styles = """
    .btn-plus {
        font-size: 60rpx;
        margin-right: 20rpx;
        color: #666;
        line-height: 60rpx;
    }
    .msg-image {
        max-width: 300rpx;
        border-radius: 10rpx;
        display: block;
        margin-bottom: 10rpx;
    }
"""
        content = content.replace('</style>', new_styles + '</style>')
    else:
        # Add style tag
        content += """
<style>
    .container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        background-color: #f5f5f5;
    }
    .chat-area {
        flex: 1;
        overflow: hidden;
    }
    .msg-list {
        padding: 20rpx;
        padding-bottom: 120rpx;
    }
    .msg-item {
        display: flex;
        margin-bottom: 30rpx;
    }
    .msg-self {
        flex-direction: row-reverse;
    }
    .avatar {
        width: 80rpx;
        height: 80rpx;
        border-radius: 10rpx;
        margin: 0 20rpx;
    }
    .bubble {
        background-color: #fff;
        padding: 20rpx;
        border-radius: 10rpx;
        max-width: 60%;
        word-break: break-all;
    }
    .msg-self .bubble {
        background-color: #95ec69;
    }
    .input-area {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f7f7fa;
        padding: 20rpx;
        display: flex;
        align-items: center;
        border-top: 1rpx solid #e5e5e5;
        box-sizing: border-box;
    }
    .input {
        flex: 1;
        background-color: #fff;
        height: 70rpx;
        border-radius: 10rpx;
        padding: 0 20rpx;
        margin-right: 20rpx;
    }
    .btn-send {
        background-color: #007aff;
        color: #fff;
        padding: 10rpx 30rpx;
        border-radius: 10rpx;
        font-size: 28rpx;
    }
    .btn-plus {
        font-size: 60rpx;
        margin-right: 20rpx;
        color: #666;
        line-height: 60rpx;
    }
    .msg-image {
        max-width: 300rpx;
        border-radius: 10rpx;
        display: block;
        margin-bottom: 10rpx;
    }
</style>
"""

with open(chat_vue_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated chat.vue")
