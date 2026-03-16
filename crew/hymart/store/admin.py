from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'parent', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    ordering = ('order', 'id')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'stock', 'is_active', 'is_approved', 'approved_at', 'approved_by', 'created_at')
    list_filter = ('is_active', 'is_approved', 'category')
    search_fields = ('title', 'slug', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('approved_at', 'approved_by')
    raw_id_fields = ('owner',)
    actions = ['approve_selected', 'unapprove_selected']

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
    approve_selected.short_description = '审核通过所选商品'

    def unapprove_selected(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_selected.short_description = '撤销审核所选商品'
