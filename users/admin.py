from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, LoginLog, ChannelEvent

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone_number', 'company_name', 'membership_level', 'source_channel', 'is_staff', 'last_login', 'date_joined')
    list_filter = ('membership_level', 'source_channel', 'is_staff', 'is_active', 'groups', 'date_joined', 'last_login')
    search_fields = ('username', 'phone_number', 'company_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('phone_number', 'company_name', 'membership_level', 'approved_posts_count', 'source_channel', 'openid', 'unionid', 'oa_openid')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('phone_number', 'company_name', 'membership_level', 'approved_posts_count', 'source_channel')}),
    )
    readonly_fields = ('openid', 'unionid', 'oa_openid')

@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'login_time', 'user_agent')
    list_filter = ('login_time',)
    search_fields = ('user__username', 'ip_address', 'user__phone_number')
    readonly_fields = ('user', 'ip_address', 'user_agent', 'login_time')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(ChannelEvent)
class ChannelEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'source_channel', 'user', 'created_at')
    list_filter = ('event_type', 'source_channel', 'created_at')
    search_fields = ('user__username', 'user__phone_number', 'source_channel')
    readonly_fields = ('event_type', 'source_channel', 'user', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(CustomUser, CustomUserAdmin)
