from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CompanyProfile, CrewProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'mobile', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'mobile', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Info', {'fields': ('mobile', 'avatar', 'role', 'company_name')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Info', {'fields': ('mobile', 'role', 'company_name')}),
    )

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_person', 'verification_status', 'is_verified', 'created_at')
    list_filter = ('verification_status', 'is_verified')
    search_fields = ('user__username', 'user__company_name', 'contact_person')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CrewProfile)
class CrewProfileAdmin(admin.ModelAdmin):
    list_display = ('real_name', 'position', 'status', 'years_of_experience', 'created_at')
    list_filter = ('status', 'gender', 'position')
    search_fields = ('real_name', 'position', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
