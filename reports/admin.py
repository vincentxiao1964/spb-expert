from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reason', 'reporter', 'content_object', 'status', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['description', 'reporter__username']
    readonly_fields = ['reporter', 'content_type', 'object_id', 'content_object', 'created_at']
    list_editable = ['status']
