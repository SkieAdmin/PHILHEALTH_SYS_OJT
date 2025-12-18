from django.db import models
from django.conf import settings
from secretary.models import Appointment


# (12/18/2025 - Gocotano) - Medicine model to store available medicines with prices
class Medicine(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ₱{self.price}"

    class Meta:
        ordering = ['name']


class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete = models.CASCADE, related_name="consultation")
    diagnosis  = models.TextField()
    # (Old Code) - prescription = models.TextField(blank=True, null=True)
    reason_notes = models.TextField(blank=True, null=True)  # (12/18/2025 - Gocotano) - Added reason notes field
    notes = models.TextField(blank=True, null=True)
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consultation")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation for {self.appointment.patient} by {self.doctor}"


# (12/18/2025 - Gocotano) - Prescription model to store individual medicine prescriptions for a consultation
class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="prescriptions")
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    doctor_prescription = models.TextField(blank=True, null=True)  # Doctor's specific instructions for this medicine
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine.name} x{self.quantity} for {self.consultation}"

    # (12/18/2025 - Gocotano) - Calculate total price for this prescription item
    def get_total_price(self):
        return self.medicine.price * self.quantity