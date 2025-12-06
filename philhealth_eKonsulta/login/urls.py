from django.urls import path
from .import views

urlpatterns = [
    path('login/', views.login_view, name = "login"),
    
    path('superuser-login/', views.superadmin_login_view, name = "superadmin_login"),
    
    path('create-user/', views.create_user_view, name = "create_user"),
    
    path('superadmin-dashboard/', views.superadmin_dashboard, name = "superadmin_dashboard"),
    path('doctor-dashbaord/', views.doctor_dashboard, name = "doctor_dashboard"),
    path('secretary-dashboard/', views.secretary_dashboard, name = "secretary_dashboard"),
    path('finance-dashbaord/', views.finance_dashboard, name ="finance_dashboard"),
]