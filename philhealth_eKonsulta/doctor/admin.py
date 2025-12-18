from django.contrib import admin
from .models import Medicine, Consultation, Prescription

# (12/18/2025 - Gocotano) - Register Medicine model for admin management
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('name',)


# (12/18/2025 - Gocotano) - Register Consultation model for admin management
@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'doctor', 'diagnosis', 'date')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name', 'diagnosis')
    list_filter = ('date', 'doctor')


# (12/18/2025 - Gocotano) - Register Prescription model for admin management
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'medicine', 'quantity', 'get_total_price', 'created_at')
    search_fields = ('consultation__appointment__patient__first_name', 'medicine__name')
    list_filter = ('created_at', 'medicine')
