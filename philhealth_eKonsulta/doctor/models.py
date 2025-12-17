from django.db import models
from django.conf import settings
from secretary.models import Appointment

class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete = models.CASCADE, related_name="consultation")
    diagnosis  = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consultation")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation for {self.appointment.patient} by {self.doctor}"