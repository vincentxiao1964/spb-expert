from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.DateTimeField(source='created_at', format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'type', 'title', 'message', 'is_read', 
            'content_type', 'object_id', 'created_at', 'created_at_formatted'
        ]
        read_only_fields = ['recipient', 'created_at']
