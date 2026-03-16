from django.contrib import admin
from .models import Order, OrderItem, OrderLog, OrderRefund

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderLogInline(admin.TabularInline):
    model = OrderLog
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_name', 'status', 'total_amount', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline, OrderLogInline]

@admin.register(OrderRefund)
class OrderRefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'status', 'created_at')
    list_filter = ('status',)
