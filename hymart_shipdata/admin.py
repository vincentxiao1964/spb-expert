from django.contrib import admin
from .models import ShipExtendedInfo, VoyageHistory
from market.models import ShipListing

class ShipExtendedInfoInline(admin.StackedInline):
    model = ShipExtendedInfo
    can_delete = False
    verbose_name_plural = 'Hymart Extended Info'

# Ideally we would attach this to ShipListingAdmin, but we can't easily modify it from here without monkey patching.
# So we just register ShipExtendedInfo as a standalone admin for now.

@admin.register(ShipExtendedInfo)
class ShipExtendedInfoAdmin(admin.ModelAdmin):
    list_display = ('ship_listing', 'draft_laden', 'grain_capacity', 'imo_number')
    search_fields = ('ship_listing__description', 'imo_number')
    list_filter = ('hatch_count',)
    raw_id_fields = ('ship_listing',)

@admin.register(VoyageHistory)
class VoyageHistoryAdmin(admin.ModelAdmin):
    list_display = ('ship_listing', 'departure_port', 'arrival_port', 'departure_date')
    list_filter = ('departure_port', 'arrival_port')
    search_fields = ('ship_listing__description', 'cargo_description')
    raw_id_fields = ('ship_listing',)
