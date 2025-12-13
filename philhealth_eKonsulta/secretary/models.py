from django.db import models
# Add by Gocotano - as of 2025-12-13
import uuid
import os

from django.db import models

# _________________________________________________________________________
# Add by Gocotano - as of 2025-12-13
# Function to generate random filename for documents & ID
def document_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # Get file extension like (.txt and etc)
    random_filename = f"{uuid.uuid4()}{ext}" #combine random UUID to become like bwfiwfwj.txt
    return f"patient_documents/{random_filename}"

def picture_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # Get file extension
    random_filename = f"{uuid.uuid4()}{ext}"
    return f"patient_pictures/{random_filename}"
# _________________________________________________________________________

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

# _________________________________________________________________________
# Add by Gocotano - as of 2025-12-13
# Model for Medical Record Documents (optional, multiple uploads allowed)
class PatientDocument(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    # Update by Gocotano - as of 2025-12-13 - Use random filename
    document = models.FileField(upload_to=document_upload_path)
    original_filename = models.CharField(max_length=255, blank=True, null=True)  # Store original filename
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.patient} - {self.description or 'No description'}"

# Add by Gocotano - as of 2025-12-13
# Model for Patient Pictures (optional, multiple uploads allowed, no limit)
class PatientPicture(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='pictures')
    # Update by Gocotano - as of 2025-12-13 - Use random filename
    picture = models.ImageField(upload_to=picture_upload_path)
    original_filename = models.CharField(max_length=255, blank=True, null=True)  # Store original filename
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

# _________________________________________________________________________

    def __str__(self):
        return f"Picture for {self.patient} - {self.caption or 'No caption'}"