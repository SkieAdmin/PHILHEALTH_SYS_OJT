from django import forms
from .models import Consultation, Prescription, Medicine


# (Old Code) - Original ConsultationForm
# class ConsultationForm(forms.ModelForm):
#     class Meta:
#         model = Consultation
#         fields = ["diagnosis", "prescription", "notes"]


# (12/18/2025 - Gocotano) - Updated ConsultationForm with reason_notes field
class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ["diagnosis", "reason_notes", "notes"]
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reason_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter reason notes...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes...'}),
        }


# (12/18/2025 - Gocotano) - PrescriptionForm for individual medicine prescriptions
class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["medicine", "quantity", "doctor_prescription"]
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'value': 1}),
            'doctor_prescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Prescription instructions...'}),
        }
