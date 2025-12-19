from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.finance_dashboard, name="payment_dashboard"),
    path("payment/update/<int:consultation_id>/<str:status>/", views.update_payment_status, name="update_payment_status"),
]
