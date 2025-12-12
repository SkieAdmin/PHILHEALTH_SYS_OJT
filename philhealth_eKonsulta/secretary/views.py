from django.shortcuts import render, redirect , get_object_or_404

from .models import Patient
from .forms import PatientForm


#          Patient CRUD
#--------------------------------

def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'Patients/patient_list.html',{'patients': patients})

def patient_create(request):
    form = PatientForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('patient_list')
    return render(request, 'Patients/patient_form.html', {'form': form})

def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None , instance = patient)
    if form.is_valid():
        form.save()
        return redirect('patient_list')
    return render(request, 'Patients/patient_form/html', {'form': form})

def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        return redirect('patient_list')
    return render(request,'Patients/patient_form.html', {'patient': patient})

