from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Patient, Appointment, PatientDocument, PatientPicture

#patient
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'gender', 'contact_number', 'email', 'address', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('gender','created_at')

#appointment
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status', 'notes')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name')
    list_filter = ('status', 'date')

#patient document
@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'original_filename', 'description', 'uploaded_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'original_filename', 'description')
    list_filter = ('uploaded_at',)

#patient picture
@admin.register(PatientPicture)
class PatientPictureAdmin(admin.ModelAdmin):
    list_display = ('patient', 'original_filename', 'caption', 'uploaded_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'original_filename', 'caption')
    list_filter = ('uploaded_at',)
