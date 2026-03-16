from rest_framework import serializers
from .models import JobPosition, JobListing
from django.contrib.auth import get_user_model

User = get_user_model()

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'company_name', 'avatar']

class JobPositionSerializer(serializers.ModelSerializer):
    positions = serializers.SerializerMethodField()

    class Meta:
        model = JobPosition
        fields = ['id', 'name', 'slug', 'parent', 'description', 'is_active', 'order', 'positions']

    def get_positions(self, obj):
        # Using 'positions' related_name as defined in model
        if obj.positions.exists():
            return JobPositionSerializer(obj.positions.all(), many=True).data
        return []

class JobListingSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(read_only=True)
    position = JobPositionSerializer(read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=JobPosition.objects.all(), source='position', write_only=True
    )
    ship_type_display = serializers.CharField(source='get_ship_type_display', read_only=True)

    class Meta:
        model = JobListing
        fields = [
            'id', 'employer', 'position', 'position_id', 'title', 
            'ship_type', 'ship_type_display', 'salary_range', 'contract_duration',
            'requirements', 'description', 'is_active', 'view_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['employer', 'view_count', 'created_at', 'updated_at']
