from django import forms
from .models import Patient, Appointment

# Update by Gocotano - as of 2025-12-13
# Added calendar widget for birth_date
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

# Add by Gocotano - as of 2025-12-13
# Form for single document upload
class SingleDocumentForm(forms.Form):
    document = forms.FileField(required=False)
    description = forms.CharField(max_length=255, required=False)

# Add by Gocotano - as of 2025-12-13
# Form for single picture upload
class SinglePictureForm(forms.Form):
    picture = forms.ImageField(required=False)
    caption = forms.CharField(max_length=255, required=False)


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'date', 'time', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }