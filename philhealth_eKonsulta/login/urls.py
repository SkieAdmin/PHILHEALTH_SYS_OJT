from django.urls import path
from .import views

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('superadmin-login/', views.superadmin_login_view, name="superadmin_login"),
    path('superadmin-dashboard/', views.superadmin_dashboard, name="superadmin_dashboard"),
    path('doctor-dashboard/', views.doctor_dashboard, name="doctor_dashboard"),
    path('secretary-dashboard/', views.secretary_dashboard, name="secretary_dashboard"),
    path('finance-dashboard/', views.finance_dashboard, name="finance_dashboard"),

    # CRUD
    path('create-user/', views.create_user_view, name="create_user"),
    path('list-users/', views.list_users_view, name="list_users"),
    path('update-user/<int:user_id>/', views.update_user_view, name="update_user"),
    path('delete-user/<int:user_id>/', views.delete_user_view, name="delete_user"),
]
