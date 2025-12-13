from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Appointment, Patient
from .forms import AppointmentForm, PatientForm



#       Patient CRUD
#-------------------------------------
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patient/patient_list.html', {'patients': patients})

def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'patient/patient_form.html', {'form': form})

def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patient/patient_form.html', {'form': form})

def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        return redirect('patient_list')
    return render(request, 'patient/patient_confirm_delete.html', {'patient': patient})


#       Appointment
#-------------------------------

def appointment_list(request):
    appointments =  Appointment.objects.all().order_by('date','time')
    return render(request, 'appointment/appointment_list.html', {'appointments': appointments})

def appointment_create(request):
    form = AppointmentForm(request.POST or None)
    if form.is_valid():
        existing = Appointment.objects.filter(
            doctor = form.cleaned_data['doctor'],
            date = form.cleaned_data['date'],
            time = form.cleaned_data['time'],
        )
        if existing.exists():
            form.add_error(None, "This time slot is already booked.")
        else:
            form.save()
            return redirect('appointment_list')
    return render(request, 'appointment/appointment_form.html', {'form':form})

def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if form.is_valid():
        form.save()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_form.html', {'form':form})

def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_delete_confirm.html', {'appointment': appointment})

def secretary_dashboard(request):
    today = timezone.now().date()
    upcoming = Appointment.objects.filter(date=today).order_by('time')
    total_patients = Patient.objects.count()
    return render(request, 'appointment/dashboard.html',{
        'upcoming':upcoming,
        'total_patients' : total_patients
    })