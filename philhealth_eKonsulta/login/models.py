from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('SUPERADMIN', 'Super Admin'),
        ('SECRETARY', 'Secretary'),
        ('DOCTOR', 'Doctor'),
        ('FINANCE', 'Finance'),
    ]
    role = models.CharField(max_length = 20, choices = ROLE_CHOICES, default = 'PATIENT')

# Create your models here.
