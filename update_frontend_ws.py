import os

chat_vue_path = r'D:\spb-expert11\frontend\pages\chat\chat.vue'
with open(chat_vue_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add socketTask to data
if 'socketTask: null' not in content:
    content = content.replace(
        'pollTimer: null',
        'pollTimer: null,\n                socketTask: null'
    )

# 2. Replace startPolling with connectWebSocket
if 'startPolling()' in content:
    content = content.replace('this.startPolling();', 'this.connectWebSocket();')
    
    # Remove startPolling method
    # It's easier to just rename it and change content
    if 'startPolling() {' in content:
        # This is tricky with simple replace. Let's just append connectWebSocket and remove startPolling call.
        pass

# Let's completely rewrite the script section to be safe and clean
# We will inject the connectWebSocket method
new_methods = """
            connectWebSocket() {
                const token = uni.getStorageSync('token');
                // Use current user ID for room name, or we can use a generic endpoint and auth via headers/ticket
                // For simplicity in this demo, we assume the backend validates the user from the connection
                // But standard WebSocket API in browser doesn't support custom headers easily.
                // However, uni.connectSocket supports header.
                
                // Note: In development, we use ws://127.0.0.1:8000/ws/chat/ROOM/
                // Our backend expects room_name. We are using user_id as room.
                // Actually, the consumer uses user_id from scope.
                // But we defined url as /ws/chat/(?P<room_name>\w+)/
                // Let's use 'global' or 'user_{id}' as room name, but the Consumer logic I wrote 
                // ignores the URL param and uses self.scope['user'].id for group name.
                // So the URL param is dummy but required.
                
                this.socketTask = uni.connectSocket({
                    url: 'ws://127.0.0.1:8000/ws/chat/1/', // '1' is dummy
                    header: {
                        'Authorization': 'Bearer ' + token
                    },
                    success: () => {
                        console.log('WebSocket connected');
                    }
                });

                this.socketTask.onMessage((res) => {
                    const data = JSON.parse(res.data);
                    if (data.type === 'chat_message') {
                        // Check if this message belongs to current conversation
                        if (data.sender_id == this.targetId || data.sender_id == this.currentUserId) {
                            // Only add if not already present (avoid duplicates if we push optimistically)
                            // But for simplicity, we rely on the list.
                            // If sender is me, I might have already pushed it.
                            if (data.sender_id == this.currentUserId) {
                                // Ignore echo if I already pushed it? 
                                // My sendMsg pushes it.
                                return;
                            }
                            this.messages.push({
                                sender: data.sender_id,
                                sender_avatar: data.sender_avatar,
                                content: data.message,
                                image: null // Images are sent via HTTP and received via HTTP response first
                            });
                            this.scrollToBottom();
                        }
                    }
                });
                
                this.socketTask.onOpen(() => {
                    console.log('WebSocket Open');
                });
                
                this.socketTask.onError((err) => {
                    console.error('WebSocket Error', err);
                    // Fallback to polling if WS fails
                    this.startPolling();
                });
                
                this.socketTask.onClose(() => {
                    console.log('WebSocket Closed');
                });
            },
            
            // Keep polling as backup or for history sync
            startPolling() {
                if (this.pollTimer) return;
                this.pollTimer = setInterval(() => {
                    // Only poll if WS is not active? Or just poll less frequently?
                    // Let's just reload history to sync
                    // this.loadHistory(); 
                }, 10000);
            },
"""

if 'startPolling() {' in content:
    # Replace startPolling block with new methods
    # We need to find the exact block. 
    # Instead, let's just append connectWebSocket and change the call in onLoad
    pass

# Update sendMsg to use WebSocket?
# No, we kept HTTP POST for saving to DB, and Backend triggers WebSocket.
# This is a common pattern (REST + WS for notification).
# So sendMsg doesn't need to change, except removing the manual push if we want to rely on echo.
# But relying on echo feels slow. Optimistic update is better.
# In my Consumer, I sent back 'message_sent' confirmation but also 'chat_message' to group?
# No, I sent 'chat_message' to receiver's group.
# I did NOT send to sender's group.
# So sender relies on HTTP response.
# Receiver gets WS message.

# So I just need to add connectWebSocket and call it.

if 'connectWebSocket' not in content:
    methods_start = 'methods: {'
    content = content.replace(methods_start, methods_start + new_methods)

# Update onUnload to close socket
if 'onUnload() {' in content:
    content = content.replace(
        'onUnload() {',
        'onUnload() {\n            if (this.socketTask) this.socketTask.close();'
    )

with open(chat_vue_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated chat.vue with WebSocket")
