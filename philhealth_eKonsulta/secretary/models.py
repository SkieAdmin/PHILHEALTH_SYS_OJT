from django.shortcuts import render, redirect, get_list_or_404

from django.db import models
from login.models import DoctorProfile

#   patient table
#----------------------------------

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male','Male'),('Female','Female')])
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    medical_history = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
#   Appointment table
#------------------------------------
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending','Pending'),
        ('Confirmed','Confirmed'),
        ('Cancelled','Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete = models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete = models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = 'pending')
    notes = models.TextField(blank = True)

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date} at {self.time}"