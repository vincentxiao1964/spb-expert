from django.contrib import admin
from .models import PaymentIntent

@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'provider', 'status', 'created_at')
    list_filter = ('provider', 'status')
    search_fields = ('reference',)
