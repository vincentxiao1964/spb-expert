from django.contrib import admin
from .models import CargoRequest, MatchResult


@admin.register(CargoRequest)
class CargoRequestAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'id', 'user', 'cargo_type', 'weight', 'volume', 'max_draft', 'dwt_tolerance_percent', 'draft_tolerance_percent', 'status', 'created_at')
    list_filter = ('cargo_type', 'status', 'created_at')
    search_fields = ('unique_id', 'user__username', 'origin', 'destination')
    readonly_fields = ('unique_id',)
    ordering = ('-created_at',)


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'cargo_request', 'ship_listing', 'score', 'created_at', 'is_viewed')
    list_filter = ('created_at', 'is_viewed')
    search_fields = ('cargo_request__id', 'ship_listing__id')
    ordering = ('-score',)
