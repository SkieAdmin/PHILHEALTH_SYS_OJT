from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'gender', 'contact_number', 'email', 'address', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('gender','created_at')
# Register your models here.
