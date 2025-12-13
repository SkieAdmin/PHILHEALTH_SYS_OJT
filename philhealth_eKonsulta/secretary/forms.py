from django import forms
from .models import Patient, PatientDocument, PatientPicture

# Old PatientForm - commented out by Gocotano - as of 2025-12-13
# class PatientForm(forms.ModelForm):
#     class Meta:
#         model = Patient
#         fields = '__all__'

# Add by Gocotano - as of 2025-12-13
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

# Add by Gocotano - as of 2025-12-13
# Form for uploading medical record documents
class PatientDocumentForm(forms.ModelForm):
    class Meta:
        model = PatientDocument
        fields = ['document', 'description']

# Add by Gocotano - as of 2025-12-13
# Form for uploading patient pictures
class PatientPictureForm(forms.ModelForm):
    class Meta:
        model = PatientPicture
        fields = ['picture', 'caption']

# Add by Gocotano - as of 2025-12-13
# Form for single document upload (can add multiple documents one at a time)
class SingleDocumentForm(forms.Form):
    document = forms.FileField(required=False)
    description = forms.CharField(max_length=255, required=False)

# Add by Gocotano - as of 2025-12-13
# Form for single picture upload (can add multiple pictures one at a time)
class SinglePictureForm(forms.Form):
    picture = forms.ImageField(required=False)
    caption = forms.CharField(max_length=255, required=False)