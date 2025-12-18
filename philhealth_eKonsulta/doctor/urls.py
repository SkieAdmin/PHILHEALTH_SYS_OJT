from django.urls import path
from . import views

urlpatterns = [
    path('appointments', views.doctor_appointments, name='doctor_appt_list'),
    path('appointment/<int:appointment_id>/<str:new_status>/', views.update_appointment_status, name='update_appointment_status'),
    path('patient/<int:appointment_id>/', views.patient_appt_detail, name='patient_appt_detail'),
    path('consultation/<int:appointment_id>/', views.add_consultation, name='add_consultation'),
    # (12/18/2025 - Gocotano) - My Patients URLs
    path('my-patients/', views.my_patients, name='my_patients'),
    path('my-patients/<int:patient_id>/', views.my_patient_detail, name='my_patient_detail'),
]