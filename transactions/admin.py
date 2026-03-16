from django.contrib import admin
from .models import Transaction, TransactionDocument, TransactionLog

class TransactionDocumentInline(admin.TabularInline):
    model = TransactionDocument
    extra = 0

class TransactionLogInline(admin.TabularInline):
    model = TransactionLog
    extra = 0
    readonly_fields = ('actor', 'action', 'timestamp')
    can_delete = False

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'buyer', 'seller', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('listing__title', 'buyer__username', 'seller__username')
    inlines = [TransactionDocumentInline, TransactionLogInline]
    
    fieldsets = (
        (None, {
            'fields': ('listing', 'buyer', 'seller', 'status')
        }),
        ('Financials', {
            'fields': ('price_agreed', 'deposit_amount', 'needs_financing')
        }),
        ('Signatures', {
            'fields': ('buyer_signed', 'buyer_signed_at', 'seller_signed', 'seller_signed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TransactionDocument)
class TransactionDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'doc_type', 'is_verified', 'uploaded_at')
    list_filter = ('doc_type', 'is_verified')
