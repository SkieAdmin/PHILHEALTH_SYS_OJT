from django.urls import path
from . import views

urlpatterns = [
    path('appointments', views.doctor_appointments, name='doctor_appt_list'),
    path('appointment/<int:appointment_id>/<str:new_status>/', views.update_appointment_status, name='update_appointment_status'),
    path('patient/<int:appointment_id>/', views.patient_appt_detail, name='patient_appt_detail')
]