from django.db import models
from django.conf import settings
from doctor.models import Consultation
from decimal import Decimal


# (Old Code) - Original Payment model
# class Payment(models.Model):
#     PAYMENT_STATUS = [
#         ('PAID','Paid'),
#         ('UNPAID','Unpaid'),
#         ('PHILHEALTH', 'PhilHealth-Coverd'),
#     ]
#
#     consultation = models.OneToOneField(
#         Consultation,
#         on_delete = models.CASCADE,
#         related_name = "payment"
#     )
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices = PAYMENT_STATUS, default="UNPAID")
#     processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
#     date_processed = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.consultation.appointment.patient} - {self.status}"


# (12-19-2025) Gocotano - Billing model to handle patient billing after consultation
class Billing(models.Model):
    BILLING_STATUS = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('PHILHEALTH', 'PhilHealth-Covered'),
    ]

    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name="billing"
    )
    # (12-19-2025) Gocotano - Total amount for the consultation (auto-calculated)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # (12-19-2025) Gocotano - Amount covered by PhilHealth
    philhealth_coverage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # (12-19-2025) Gocotano - Amount already paid
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=BILLING_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Billing for {self.consultation.appointment.patient} - {self.status}"

    # (12-19-2025) Gocotano - Calculate remaining balance
    def get_balance(self):
        return self.total_amount - self.philhealth_coverage - self.amount_paid

    # (12-19-2025) Gocotano - Calculate and update total amount from consultation prescriptions
    def calculate_total(self):
        self.total_amount = self.consultation.get_total_amount()
        self.save()
        return self.total_amount


# (12-19-2025) Gocotano - BillingItem model to track individual items in a bill
class BillingItem(models.Model):
    ITEM_TYPE = [
        ('CONSULTATION', 'Consultation Fee'),
        ('MEDICINE', 'Medicine'),
        ('OTHER', 'Other'),
    ]

    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE, default='MEDICINE')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - ₱{self.total_price}"

    # (12-19-2025) Gocotano - Calculate total price before saving
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


# (12-19-2025) Gocotano - Transaction model to track payment history
class Transaction(models.Model):
    PAYMENT_METHOD = [
        ('CASH', 'Cash'),
        ('PHILHEALTH', 'PhilHealth'),
    ]

    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='CASH')
    reference_number = models.CharField(max_length=100, blank=True, null=True)  # For PhilHealth claim number
    remarks = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction ₱{self.amount} for {self.billing.consultation.appointment.patient}"

    class Meta:
        ordering = ['-created_at']