from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = ('transaction_id', 'user', 'payment_method', 'amount', 'status', 'created_at')

    list_filter = ('payment_method', 'status', 'created_at')

    search_fields = ('transaction_id', 'gateway_reference', 'user__email')
    
    readonly_fields = ('created_at', 'updated_at')
