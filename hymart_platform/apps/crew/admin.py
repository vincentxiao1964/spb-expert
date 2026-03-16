from django.contrib import admin
from .models import JobPosition, JobListing

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'is_active', 'order')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'position', 'ship_type', 'salary_range', 'is_active', 'created_at')
    list_filter = ('is_active', 'ship_type', 'created_at')
    search_fields = ('title', 'employer__company_name', 'description')
    readonly_fields = ('view_count',)
