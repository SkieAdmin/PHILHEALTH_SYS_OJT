from django.contrib import admin
from .models import Billing, BillingItem, Transaction

# (Old Code) - Original Payment admin registration
# from .models import Payment
# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('consultation', 'amount', 'status', 'processed_by', 'date_processed')
#     search_fields = ('status',)
#     list_filter = ('status', 'processed_by', 'date_processed')


# (12-19-2025) Gocotano - Register Billing model in admin
@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'total_amount', 'philhealth_coverage', 'amount_paid', 'status', 'created_at')
    search_fields = ('consultation__appointment__patient__first_name', 'consultation__appointment__patient__last_name')
    list_filter = ('status', 'created_at')


# (12-19-2025) Gocotano - Register BillingItem model in admin
@admin.register(BillingItem)
class BillingItemAdmin(admin.ModelAdmin):
    list_display = ('billing', 'item_type', 'description', 'quantity', 'unit_price', 'total_price')
    search_fields = ('description',)
    list_filter = ('item_type',)


# (12-19-2025) Gocotano - Register Transaction model in admin
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('billing', 'amount', 'payment_method', 'reference_number', 'processed_by', 'created_at')
    search_fields = ('reference_number', 'remarks')
    list_filter = ('payment_method', 'created_at')
