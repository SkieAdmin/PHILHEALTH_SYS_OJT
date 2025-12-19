from django.urls import path
from . import views

# (Old Code) - Original URL patterns
# urlpatterns = [
#     path("dashboard/", views.finance_dashboard, name="payment_dashboard"),
#     path("payment/update/<int:consultation_id>/<str:status>/", views.update_payment_status, name="update_payment_status"),
# ]

# (12-19-2025) Gocotano - Updated URL patterns for finance module
urlpatterns = [
    path("dashboard/", views.finance_dashboard, name="finance_dashboard"),
    path("billing/<int:billing_id>/", views.billing_detail, name="billing_detail"),
    path("billing/<int:billing_id>/pay/", views.process_payment, name="process_payment"),
    path("billing/<int:billing_id>/philhealth/", views.apply_philhealth, name="apply_philhealth"),
]
