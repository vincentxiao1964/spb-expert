from django.contrib import admin
from django.utils.html import mark_safe
from .models import ShipListing, ListingImage, MarketNews, CrawledShip, CrawledShipSOL, CrawledShipEship, CrawledShipHorizon, DailyBriefing
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.action(description=_('Convert selected crawled ships to Listings'))
def convert_to_listing(modeladmin, request, queryset):
    # Find a default admin user to assign listings to
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        modeladmin.message_user(request, "No admin user found to assign listings to.", level=messages.ERROR)
        return

    success_count = 0
    for crawled in queryset:
        # Check duplicates based on source_url or description similarity?
        # For now, we trust the user's selection.
        
        # Map fields
        # ShipCategory mapping
        cat_map = {
            'Deck Barge': ShipListing.ShipCategory.DECK_BARGE,
            'Spud Barge': ShipListing.ShipCategory.SPUD_BARGE,
            'Hopper Barge': ShipListing.ShipCategory.HOPPER_BARGE,
            'SELF_PROPELLED': ShipListing.ShipCategory.SELF_PROPELLED_BARGE,
            'NON_SELF_PROPELLED': ShipListing.ShipCategory.DECK_BARGE, # Default fallback
        }
        
        # Try to map category, default to DECK_BARGE if unknown
        ship_category = cat_map.get(crawled.ship_category, ShipListing.ShipCategory.DECK_BARGE)
        
        # Create Listing
        listing = ShipListing.objects.create(
            user=admin_user,
            listing_type=ShipListing.ListingType.SELL, # Default to SELL
            ship_category=ship_category,
            length=float(crawled.length) if crawled.length else None,
            width=float(crawled.width) if crawled.width else None,
            depth=float(crawled.depth) if crawled.depth else None,
            dwt=float(crawled.dwt) if crawled.dwt and crawled.dwt.replace('.', '', 1).isdigit() else None,
            build_year=crawled.build_year,
            description=crawled.full_description or '',
            contact_info=crawled.contact_info or "See original source",
            status=ShipListing.Status.PENDING, # Pending review before public
            extended_info={
                'source': crawled.source,
                'source_id': crawled.source_id,
                'source_url': crawled.source_url,
                'remark': crawled.remark
            }
        )
        
        # Add Images
        if crawled.images:
            for img_url in crawled.images:
                # Add image links to description for now.
                listing.description += f"\n\n![Image]({img_url})"
        
        listing.save()
        success_count += 1

    modeladmin.message_user(request, f"Successfully converted {success_count} ships to Listings (Status: Pending).", level=messages.SUCCESS)

class DailyBriefingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('content',)

admin.site.register(DailyBriefing, DailyBriefingAdmin)

class CrawledShipAdmin(admin.ModelAdmin):
    list_display = ('source_id', 'source', 'dwt', 'width', 'ship_category', 'crawled_at')
    search_fields = ('source_id', 'full_description', 'remark', 'contact_info')
    list_filter = ('source', 'ship_category')
    readonly_fields = ('source_id', 'source_url', 'crawled_at', 'display_images')
    fieldsets = (
        (None, {
            'fields': ('source_id', 'source', 'source_url', 'crawled_at')
        }),
        ('Ship Info', {
            'fields': ('ship_category', 'dwt', 'build_year', 'length', 'width', 'depth')
        }),
        ('Details', {
            'fields': ('remark', 'contact_info', 'display_images', 'full_description')
        }),
    )

    def display_images(self, obj):
        if not obj.images:
            return _("No images")
        html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
        for url in obj.images:
            html += f'<a href="{url}" target="_blank"><img src="{url}" style="height: 100px; border: 1px solid #ccc; object-fit: cover;" /></a>'
        html += '</div>'
        return mark_safe(html)
    display_images.short_description = _('Images Preview')

    actions = [convert_to_listing]

class CrawledShipSOLAdmin(CrawledShipAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(source='sol')

class CrawledShipEshipAdmin(CrawledShipAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(source='eship')

class CrawledShipHorizonAdmin(CrawledShipAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(source='horizon')

# admin.site.register(CrawledShip, CrawledShipAdmin) # Unregister original one to avoid confusion
admin.site.register(CrawledShipSOL, CrawledShipSOLAdmin)
admin.site.register(CrawledShipEship, CrawledShipEshipAdmin)
admin.site.register(CrawledShipHorizon, CrawledShipHorizonAdmin)

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1

@admin.action(description=_('Approve selected listings'))
def approve_listings(modeladmin, request, queryset):
    for listing in queryset:
        if listing.status != ShipListing.Status.APPROVED:
            listing.status = ShipListing.Status.APPROVED
            listing.save()
            # Update user stats
            listing.user.approved_posts_count += 1
            listing.user.update_level()
            listing.user.save()

class ShipListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing_type', 'ship_category', 'dwt', 'user', 'status', 'created_at')
    list_filter = ('listing_type', 'ship_category', 'status')
    search_fields = ('user__username', 'contact_info', 'class_society')
    inlines = [ListingImageInline]
    actions = [approve_listings]

admin.site.register(ShipListing, ShipListingAdmin)

@admin.action(description=_('Approve selected news'))
def approve_news(modeladmin, request, queryset):
    for news in queryset:
        if news.status != MarketNews.Status.APPROVED:
            news.status = MarketNews.Status.APPROVED
            news.save()
            # Update user stats
            news.user.approved_posts_count += 1
            news.user.update_level()
            news.user.save()

class MarketNewsAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'title', 'user', 'original_source', 'status', 'created_at')
    list_filter = ('status', 'original_source')
    search_fields = ('unique_id', 'title', 'content', 'user__username', 'original_source')
    readonly_fields = ('source_url', 'unique_id')
    actions = [approve_news]

admin.site.register(MarketNews, MarketNewsAdmin)
