from django.contrib import admin
from .models import CrewListing

@admin.register(CrewListing)
class CrewListingAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'nationality_type', 'nationality', 'total_sea_experience', 'status', 'updated_at')
    list_filter = ('nationality_type', 'status', 'gender')
    search_fields = ('name', 'position', 'nationality', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')
