import os

# Update frontend/pages/chat/chat.vue
chat_path = r'D:\spb-expert11\frontend\pages\chat\chat.vue'
with open(chat_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add connectWebSocket method
new_connect = """            connectWebSocket() {
                if (this.socketTask) return;
                
                const token = uni.getStorageSync('token');
                if (!token) return;
                
                // Use WS protocol. Replace with wss:// for production
                // Assuming backend is at 127.0.0.1:8000
                const url = 'ws://127.0.0.1:8000/ws/chat/' + this.currentUserId + '/?token=' + token;
                
                this.socketTask = uni.connectSocket({
                    url: url,
                    success: () => {
                        console.log('WebSocket connect success');
                    }
                });
                
                this.socketTask.onOpen((res) => {
                    console.log('WebSocket opened');
                    // Maybe ping?
                });
                
                this.socketTask.onMessage((res) => {
                    const data = JSON.parse(res.data);
                    if (data.type === 'chat_message') {
                        // Check if this message belongs to current conversation
                        // data.sender_id is the sender.
                        // If I am chatting with User A, and User B sends me a message, 
                        // I should probably not show it in User A's chat window, or show a notification?
                        // Current logic: this.targetId is the person I'm chatting with.
                        
                        // Case 1: Message from the person I'm chatting with
                        if (String(data.sender_id) === String(this.targetId)) {
                             this.messages.push({
                                 sender: data.sender_id,
                                 sender_avatar: data.sender_avatar,
                                 content: data.message,
                                 image: data.image,
                                 created_at: new Date().toISOString()
                             });
                             this.scrollToBottom();
                        }
                        // Case 2: Message I sent (echo from another device or confirmation)
                        // If backend sends back my own messages (it does in perform_create broadcast logic if I was the sender? No, group_send is to receiver group)
                        // Wait, perform_create sends to receiver's group.
                        // If I am the sender, I don't receive it via WebSocket unless I am subscribed to my own channel?
                        // ChatConsumer joins "chat_{my_id}".
                        // perform_create sends to "chat_{receiver_id}".
                        // So I (sender) do NOT receive the WebSocket message.
                        // I only receive messages sent TO me.
                        // So I don't need to handle "my own message" here, because I push it locally in sendMsg.
                        
                        // Case 3: Message from someone else
                        else {
                            // Show toast or badge?
                            uni.showToast({ title: 'New message from ' + data.sender_name, icon: 'none' });
                        }
                    }
                });
                
                this.socketTask.onError((err) => {
                    console.log('WebSocket error', err);
                });
                
                this.socketTask.onClose(() => {
                    console.log('WebSocket closed');
                    this.socketTask = null;
                    // Reconnect?
                    // setTimeout(this.connectWebSocket, 3000);
                });
            },"""

if "connectWebSocket() {" not in content:
    # Insert before loadHistory
    content = content.replace("async loadHistory() {", new_connect + "\n\n            async loadHistory() {")
    
# 2. Update sendMsg to use WebSocket for text
# Currently sendMsg uses API. 
# We can keep API for persistence and consistency (especially since perform_create now broadcasts).
# Using API is safer because it guarantees DB save before UI update.
# WebSocket send is faster but we need to handle "ack".
# Given the "perform_create" modification, if we use API, the receiver gets WS message.
# The sender pushes locally.
# This is a perfect hybrid. I don't need to change sendMsg to use WebSocket for transport, 
# UNLESS we want to avoid HTTP overhead.
# For now, keeping HTTP for sending is fine and simpler.
# But I should remove polling if I trust WS.
# The `startPolling` method was in the file.
# I should remove calls to `startPolling` if any. 
# The file had `this.pollTimer` but I don't see `this.startPolling()` called in `onLoad` in the previous Read output.
# Ah, `startPolling` method definition was there.
# Let's ensure we don't use it.

with open(chat_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated frontend/pages/chat/chat.vue")
