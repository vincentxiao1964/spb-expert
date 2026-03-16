from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CompanyProfile, CrewProfile

User = get_user_model()

class CompanyProfileSerializer(serializers.ModelSerializer):
    verification_status_display = serializers.CharField(source='get_verification_status_display', read_only=True)
    company_name = serializers.CharField(source='user.company_name', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = CompanyProfile
        fields = [
            'id', 'user_id', 'company_name', 'business_license_no', 'business_license_img', 
            'address', 'contact_person', 'contact_phone', 
            'website', 'description', 
            'verification_status', 'verification_status_display', 'is_verified'
        ]
        read_only_fields = ['verification_status', 'verification_status_display', 'is_verified', 'company_name', 'user_id']

class CrewProfileSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)

    class Meta:
        model = CrewProfile
        fields = [
            'id', 'user_id', 'avatar', 'real_name', 'gender', 'gender_display', 'birth_date', 
            'position', 'years_of_experience', 'certificate_number', 
            'status', 'status_display', 'resume_file', 'bio'
        ]

class UserSerializer(serializers.ModelSerializer):
    company_profile = CompanyProfileSerializer(read_only=True)
    crew_profile = CrewProfileSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'mobile', 'avatar', 
            'role', 'role_display', 'company_name', 'date_joined',
            'company_profile', 'crew_profile'
        ]
        read_only_fields = ['id', 'username', 'email', 'date_joined', 'role_display']

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user basic info
    """
    class Meta:
        model = User
        fields = ['mobile', 'avatar', 'company_name']
