# login/urls.py
from django.urls import path
from .import views

urlpatterns = [
    # path('', views.index, name="index"),

    path('login/', views.login_view, name="login"),
    path(' ', views.user_logout, name="logout"),
    path('superadmin-login/', views.superadmin_login_view, name="superadmin_login"),
    path('superadmin-login/', views.admin_logout, name="superadmin_logout"),

    path('superadmin-dashboard/', views.superadmin_dashboard, name="superadmin_dashboard"),
    path('doctor-dashboard/', views.doctor_dashboard, name="doctor_dashboard"),
    path('secretary-dashboard/', views.secretary_dashboard, name="secretary_dashboard"),
    path('finance-dashboard/', views.finance_dashboard, name="finance_dashboard"),

    # CRUD
    path('create-user/', views.create_user_view, name="create_user"),
    path('list-users/', views.list_users_view, name="list_users"),
    #(Added by Gocotano) - View User brub
    path('view-user/<int:user_id>/', views.view_user_view, name="view_user"),
    path('update-user/<int:user_id>/', views.update_user_view, name="update_user"),
    path('delete-user/<int:user_id>/', views.delete_user_view, name="delete_user"),
    
    # Registration URLs #new
    path('doctor-registration/', views.doctor_registration, name='doctor_registration'),
    path('secretary-registration/', views.secretary_registration, name='secretary_registration'),
    path('finance-registration/', views.finance_registration, name='finance_registration'),
]