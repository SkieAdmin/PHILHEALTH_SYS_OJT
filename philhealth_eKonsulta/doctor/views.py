from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from secretary.models import Appointment, DoctorProfile, Patient
from .models import models

@login_required
def doctor_appointments(request):
    doctor = get_object_or_404(DoctorProfile, user = request.user)
    appointments = Appointment.objects.filter(doctor = doctor).order_by('date')
    return render(request, 'doctor/doctor_appt_list.html', {'appointments':appointments})

@login_required
def update_appointment_status(request, appointment_id, new_status):
    doctor = get_object_or_404(DoctorProfile, user = request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    if new_status in ['APPROVE','CANCELLED','COMPLETED']:
        appointment.status = new_status
        appointment.save()
    return redirect('doctor_dashboard')

@login_required
def patient_appt_detail(request, appointment_id):
    doctor = get_object_or_404(DoctorProfile, user = request.user)
    appointment =   get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    patient = appointment.patient
    return render(request, 'doctor/patient_appt_detail.html', {'patient': patient, 'appointment':appointment})

