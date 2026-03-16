from django.contrib import admin
from .models import ServiceCategory, ServiceListing

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'is_active', 'order')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')

@admin.register(ServiceListing)
class ServiceListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'category', 'service_area', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('title', 'description', 'service_area')
