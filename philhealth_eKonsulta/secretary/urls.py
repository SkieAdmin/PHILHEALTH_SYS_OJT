from django.urls import path
from . import views

urlpatterns = [


    path('patients/', views.patient_list, name='patient_list'),
    path('patients/new/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    # Add by Gocotano - as of 2025-12-13
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    # Add by Gocotano - as of 2025-12-13 - Document and Picture delete routes
    path('documents/<int:pk>/delete/', views.delete_patient_document, name='delete_patient_document'),
    path('pictures/<int:pk>/delete/', views.delete_patient_picture, name='delete_patient_picture'),
]