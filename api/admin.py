from django.contrib import admin

from .models import MediaCheckTask, ModerationRule


@admin.register(MediaCheckTask)
class MediaCheckTaskAdmin(admin.ModelAdmin):
    list_display = ('trace_id', 'status', 'object_type', 'object_id', 'label', 'suggest', 'created_at')
    list_filter = ('status', 'object_type')
    search_fields = ('trace_id', 'media_url')
    ordering = ('-created_at',)


@admin.register(ModerationRule)
class ModerationRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'enabled', 'scope', 'rule_type', 'action', 'pattern', 'created_at')
    list_filter = ('enabled', 'scope', 'rule_type')
    search_fields = ('pattern',)
    ordering = ('-created_at',)
