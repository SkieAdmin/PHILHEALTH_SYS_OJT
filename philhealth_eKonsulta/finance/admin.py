from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'amount', 'status', 'processed_by', 'date_processed')
    search_fields = ('status',)
    list_filter = ('status', 'processed_by', 'date_processed')
