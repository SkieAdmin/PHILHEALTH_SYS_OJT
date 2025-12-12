from django.db import models

#patient table
class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)        
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male','Male'),('Female','Female')])
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name} ,{self.first_name}"

