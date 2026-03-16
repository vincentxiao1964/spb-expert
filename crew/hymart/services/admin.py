from django.contrib import admin
from .models import ServiceCategory, ServiceListing

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'parent', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    ordering = ('order', 'id')

@admin.register(ServiceListing)
class ServiceListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'is_active', 'is_approved', 'approved_at', 'approved_by', 'created_at')
    list_filter = ('is_active', 'is_approved', 'category')
    search_fields = ('title', 'slug', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('approved_at', 'approved_by')
    raw_id_fields = ('owner',)
    actions = ['approve_selected', 'unapprove_selected']

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
    approve_selected.short_description = '审核通过所选服务'

    def unapprove_selected(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_selected.short_description = '撤销审核所选服务'
