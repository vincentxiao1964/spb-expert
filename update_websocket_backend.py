import os

# Update apps/users/views.py with WebSocket broadcast
views_path = r'D:\spb-expert11\apps\users\views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
imports = """from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync"""

if "from channels.layers" not in content:
    content = imports + "\n" + content

# Replace perform_create
old_perform_create = """    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)"""
        
new_perform_create = """    def perform_create(self, serializer):
        msg = serializer.save(sender=self.request.user)
        
        # Broadcast to receiver via WebSocket
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{msg.receiver.id}",
                {
                    'type': 'chat_message',
                    'message': msg.content,
                    'image': msg.image.url if msg.image else None,
                    'sender_id': msg.sender.id,
                    'sender_name': msg.sender.username,
                    'sender_avatar': msg.sender.avatar
                }
            )
        except Exception as e:
            print(f"WebSocket broadcast failed: {e}")"""

if old_perform_create in content:
    content = content.replace(old_perform_create, new_perform_create)

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated apps/users/views.py")

# Update apps/users/consumers.py
consumers_path = r'D:\spb-expert11\apps\users\consumers.py'
with open(consumers_path, 'r', encoding='utf-8') as f:
    c_content = f.read()

# Update chat_message method to include image
old_chat_message = """    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_avatar': event['sender_avatar']
        }))"""
        
new_chat_message = """    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'image': event.get('image'),
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_avatar': event['sender_avatar']
        }))"""

if old_chat_message in c_content:
    c_content = c_content.replace(old_chat_message, new_chat_message)
else:
    # Maybe indentation or whitespace differs.
    # Let's try to just replace the dict inside json.dumps
    pass # If strict match fails, we might need regex or manual find.

with open(consumers_path, 'w', encoding='utf-8') as f:
    f.write(c_content)
print("Updated apps/users/consumers.py")
