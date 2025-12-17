from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from login.models import DoctorProfile
# Add by Gocotano - as of 2025-12-13
import uuid
import os

# Add by Gocotano - as of 2025-12-13
# Function to generate random filename for documents
def document_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    random_filename = f"{uuid.uuid4()}{ext}"
    return f"patient_documents/{random_filename}"

# Add by Gocotano - as of 2025-12-13
# Function to generate random filename for pictures
def picture_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    random_filename = f"{uuid.uuid4()}{ext}"
    return f"patient_pictures/{random_filename}"

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



#   Appointment table old
#------------------------------------
# class Appointment(models.Model):
#     STATUS_CHOICES = [
#         ('Pending','Pending'),
#         ('Confirmed','Confirmed'),
#         ('Cancelled','Cancelled'),
#     ]

#     patient = models.ForeignKey(Patient, on_delete = models.CASCADE)
#     doctor = models.ForeignKey(DoctorProfile, on_delete = models.CASCADE)
#     date = models.DateField()
#     time = models.TimeField()
#     status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = 'pending')
#     notes = models.TextField(blank = True)

#     def __str__(self):
#         return f"{self.patient} with {self.doctor} on {self.date} at {self.time}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING','Pending'),
        ('APPROVE','Approve'),
        ('CANCELLED','Cancelled'),
        ('COMPLETED','Completed'),
    ]

    patient = models.ForeignKey('Patient', on_delete = models.CASCADE)
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE
    )
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    time = models.TimeField()
    notes = models.TextField (blank = True)
    def __str__(self):
        return f"{self.patient} -  {self.date} ({self.status})"






# Add by Gocotano - as of 2025-12-13
# Model for Medical Record Documents (optional, multiple uploads allowed)
class PatientDocument(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to=document_upload_path)
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.patient} - {self.description or 'No description'}"

# Add by Gocotano - as of 2025-12-13
# Model for Patient Pictures (optional, multiple uploads allowed, no limit)
class PatientPicture(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='pictures')
    picture = models.ImageField(upload_to=picture_upload_path)
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Picture for {self.patient} - {self.caption or 'No caption'}"