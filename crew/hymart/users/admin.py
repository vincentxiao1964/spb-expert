from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_merchant', 'is_buyer', 'phone', 'created_at')
    list_filter = ('is_merchant', 'is_buyer')
    search_fields = ('user__username', 'phone')
