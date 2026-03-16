from django.contrib import admin
from .models import Section, Thread, Post

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active']
    list_editable = ['order', 'is_active']

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'author', 'status', 'reply_count', 'view_count', 'is_pinned', 'created_at']
    list_filter = ['status', 'section', 'is_pinned', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    date_hierarchy = 'created_at'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['thread', 'author', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['content', 'author__username', 'thread__title']
