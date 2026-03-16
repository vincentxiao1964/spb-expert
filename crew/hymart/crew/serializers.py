from rest_framework import serializers
from django.contrib.auth.models import User
from .models import JobPosition, JobListing


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class JobPositionSerializer(serializers.ModelSerializer):
    positions = serializers.SerializerMethodField()

    class Meta:
        model = JobPosition
        fields = ['id', 'name', 'slug', 'parent', 'description', 'is_active', 'order', 'positions']

    def get_positions(self, obj):
        children = obj.positions.all()
        if children.exists():
            return JobPositionSerializer(children, many=True).data
        return []


class JobListingSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(read_only=True)
    position = JobPositionSerializer(read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=JobPosition.objects.all(),
        source='position',
        write_only=True,
    )
    ship_type_display = serializers.CharField(source='get_ship_type_display', read_only=True)

    class Meta:
        model = JobListing
        fields = [
            'id',
            'employer',
            'position',
            'position_id',
            'title',
            'ship_type',
            'ship_type_display',
            'salary_range',
            'contract_duration',
            'requirements',
            'description',
            'is_active',
            'view_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['employer', 'view_count', 'created_at', 'updated_at']
