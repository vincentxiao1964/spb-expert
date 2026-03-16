from django.contrib import admin
from .models import Inquiry, InquiryMessage

class InquiryMessageInline(admin.TabularInline):
    model = InquiryMessage
    extra = 0
    readonly_fields = ('sender', 'created_at')

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'seller', 'content_object', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'seller__username', 'subject')
    inlines = [InquiryMessageInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(InquiryMessage)
class InquiryMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'inquiry', 'sender', 'is_quote', 'price', 'created_at')
    list_filter = ('is_quote', 'created_at')
