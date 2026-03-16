from django.contrib import admin
from .models import Advertisement

@admin.action(description='Activate selected ads')
def activate_ads(modeladmin, request, queryset):
    # Check limit
    active_count = Advertisement.objects.filter(is_active=True).count()
    for ad in queryset:
        if active_count >= 4:
            modeladmin.message_user(request, "Cannot activate more than 4 ads.", level='error')
            break
        if not ad.is_active:
            ad.is_active = True
            ad.save()
            active_count += 1

class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'activated_at')
    list_filter = ('is_active',)
    actions = [activate_ads]

admin.site.register(Advertisement, AdvertisementAdmin)
