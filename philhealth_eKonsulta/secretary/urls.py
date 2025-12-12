from django.urls import path
from . import views

app_name = 'secretary'

urlpatterns = [
    path('patients/', views.patient_list, name="patient_list"),
    path('patient/create/', views.patient_create, name="patient_create"),
    path('patients/<int:pk>/edit/', views.patient_update, name="patient_update"),
    path('patients/<int:pk>/delete/', views.patient_delete, name="patient_delete"),  
]