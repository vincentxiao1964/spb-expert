from rest_framework import serializers
from .models import Report
from django.contrib.contenttypes.models import ContentType

class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.ReadOnlyField(source='reporter.username')
    content_type_str = serializers.CharField(write_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'content_type_str', 'object_id', 
            'reason', 'description', 'status', 'created_at'
        ]
        read_only_fields = ['status', 'created_at']

    def create(self, validated_data):
        content_type_str = validated_data.pop('content_type_str')
        app_label, model = content_type_str.split('.')
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        
        return Report.objects.create(
            content_type=content_type,
            **validated_data
        )
