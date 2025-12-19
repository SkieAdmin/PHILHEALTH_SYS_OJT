from django.db import models
from django.conf import settings
from doctor.models import Consultation

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('PAID','Paid'),
        ('UNPAID','Unpaid'),
        ('PHILHEALTH', 'PhilHealth-Coverd'),
    ]

    consultation = models.OneToOneField(
        Consultation,
        on_delete = models.CASCADE,
        related_name = "payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices = PAYMENT_STATUS, default="UNPAID")
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    date_processed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.consultation.appointment.patient} - {self.status}"