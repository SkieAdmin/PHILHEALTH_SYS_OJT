from django.urls import path
from . import views

urlpatterns = [

    # patient
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/new/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    # Add by Gocotano - as of 2025-12-13
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('documents/<int:pk>/delete/', views.delete_patient_document, name='delete_patient_document'),
    path('pictures/<int:pk>/delete/', views.delete_patient_picture, name='delete_patient_picture'),

    # appointment
    # path('dashboard/', views.secretary_dashboard, name='secretary_dashboard'),
    path('appointment/', views.appointment_list, name='appointment_list'),
    path('appointment/create/', views.appointment_create, name='appointment_create'),
    path('appointment/<int:pk>/edit/', views.appointment_update, name='appointment_update'),
    path('appointment/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
]