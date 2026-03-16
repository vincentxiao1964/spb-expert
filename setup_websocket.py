import os

# 1. Update settings.py
settings_path = r'D:\spb-expert11\config\settings.py'
with open(settings_path, 'r', encoding='utf-8') as f:
    s_content = f.read()

# Add 'daphne' to INSTALLED_APPS (must be top)
if "'daphne'" not in s_content:
    s_content = s_content.replace(
        "INSTALLED_APPS = [",
        "INSTALLED_APPS = [\n    'daphne',  # Must be at the top"
    )

# Add 'channels' to INSTALLED_APPS (can be anywhere, but usually with others)
if "'channels'" not in s_content:
    s_content = s_content.replace(
        "'django.contrib.staticfiles',",
        "'django.contrib.staticfiles',\n\n    # Channels\n    'channels',"
    )

# Set ASGI_APPLICATION
if "ASGI_APPLICATION" not in s_content:
    s_content = s_content.replace(
        "WSGI_APPLICATION = 'config.wsgi.application'",
        "WSGI_APPLICATION = 'config.wsgi.application'\nASGI_APPLICATION = 'config.asgi.application'"
    )

# Add CHANNEL_LAYERS (In-Memory for dev)
if "CHANNEL_LAYERS" not in s_content:
    s_content += """

# Channels Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
"""

with open(settings_path, 'w', encoding='utf-8') as f:
    f.write(s_content)
print("Updated settings.py")

# 2. Create routing.py in apps/users/
routing_path = r'D:\spb-expert11\apps\users\routing.py'
routing_content = """from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
"""
with open(routing_path, 'w', encoding='utf-8') as f:
    f.write(routing_content)
print("Created apps/users/routing.py")

# 3. Create consumers.py in apps/users/
consumers_path = r'D:\spb-expert11\apps\users\consumers.py'
consumers_content = """import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return

        # Use user ID as room name for personal notifications
        self.room_group_name = f"chat_{self.user.id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'chat_message':
            receiver_id = text_data_json['receiver_id']
            content = text_data_json.get('content', '')
            # Note: Images are handled via HTTP POST, which then triggers WebSocket notification
            
            # Save message
            await self.save_message(receiver_id, content)
            
            # Send to receiver's group
            await self.channel_layer.group_send(
                f"chat_{receiver_id}",
                {
                    'type': 'chat_message',
                    'message': content,
                    'sender_id': self.user.id,
                    'sender_name': self.user.username,
                    'sender_avatar': self.user.avatar
                }
            )
            
            # Send back to sender (for confirmation/echo)
            # Actually, frontend usually adds immediately, but this confirms receipt
            await self.send(text_data=json.dumps({
                'type': 'message_sent',
                'status': 'ok'
            }))

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_avatar': event['sender_avatar']
        }))

    @database_sync_to_async
    def save_message(self, receiver_id, content):
        receiver = User.objects.get(id=receiver_id)
        Message.objects.create(
            sender=self.user,
            receiver=receiver,
            content=content
        )
"""
with open(consumers_path, 'w', encoding='utf-8') as f:
    f.write(consumers_content)
print("Created apps/users/consumers.py")

# 4. Update config/asgi.py
asgi_path = r'D:\spb-expert11\config\asgi.py'
asgi_content = """
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import apps.users.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                apps.users.routing.websocket_urlpatterns
            )
        )
    ),
})
"""
with open(asgi_path, 'w', encoding='utf-8') as f:
    f.write(asgi_content)
print("Updated config/asgi.py")
