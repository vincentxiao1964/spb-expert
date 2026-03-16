from django.contrib import admin
from .models import Port, BunkerPrice, ContractTemplate

@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'scope', 'sub_type', 'updated_at')
    list_filter = ('category', 'scope', 'sub_type')
    search_fields = ('title', 'description')
    readonly_fields = ('updated_at',)

@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_zh', 'country_en', 'country_zh', 'latitude', 'longitude')
    search_fields = ('name_en', 'name_zh', 'country_en')
    list_filter = ('country_en',)

@admin.register(BunkerPrice)
class BunkerPriceAdmin(admin.ModelAdmin):
    list_display = ('port', 'date', 'fuel_type', 'price', 'currency', 'change')
    list_filter = ('date', 'fuel_type', 'currency', 'port__country_en')
    search_fields = ('port__name_en', 'port__name_zh')
    date_hierarchy = 'date'
