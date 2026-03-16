from django.contrib import admin
from .models import AdminMessage, MemberMessage

class AdminMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'phone_number', 'created_at')
    readonly_fields = ('name', 'company_name', 'phone_number', 'message', 'created_at')

class MemberMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

admin.site.register(AdminMessage, AdminMessageAdmin)
admin.site.register(MemberMessage, MemberMessageAdmin)
