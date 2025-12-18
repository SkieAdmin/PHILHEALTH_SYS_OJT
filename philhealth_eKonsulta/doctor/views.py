from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from secretary.models import Appointment, DoctorProfile, Patient, PatientDocument, PatientPicture  #[12-17-2025 - Gocotano] - Added PatientDocument, PatientPicture imports
from .models import models
from .forms import ConsultationForm
from django.db.models import Q  #[12-17-2025 - Gocotano] - Added Q for search filtering

@login_required
def doctor_appointments(request):
    doctor = get_object_or_404(DoctorProfile, user = request.user)
    #(Old Code) - appointments = Appointment.objects.filter(doctor = doctor).order_by('date')

    #[12-17-2025 - Gocotano] - Search and Filter logic
    appointments = Appointment.objects.filter(doctor=doctor)

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query)
        )

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    appointments = appointments.order_by('date')

    return render(request, 'doctor/doctor_appt_list.html', {
        'appointments': appointments,
        'search_query': search_query,
        'status_filter': status_filter
    })

@login_required
def update_appointment_status(request, appointment_id, new_status):
    doctor = get_object_or_404(DoctorProfile, user = request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    if new_status in ['APPROVE','CANCELLED','COMPLETED']:
        appointment.status = new_status
        appointment.save()
    #(Old Code) - return redirect('doctor_dashboard')
    #[12-17-2025 - Gocotano] - Redirect to appointment list instead of dashboard
    return redirect('doctor_appt_list')

@login_required
def patient_appt_detail(request, appointment_id):
    doctor = get_object_or_404(DoctorProfile, user = request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    patient = appointment.patient

    #[12-17-2025 - Gocotano] - Get patient documents and pictures
    documents = PatientDocument.objects.filter(patient=patient)
    pictures = PatientPicture.objects.filter(patient=patient)

    return render(request, 'doctor/patient_appt_detail.html', {
        'patient': patient,
        'appointment': appointment,
        'documents': documents,
        'pictures': pictures
    })

# @login_required
# def add_consultation(request, appointment_id):
#     appointment = get_object_or_404(Appointment, id=appointment_id, status="APPROVED")

#     if request.method == "POST":
#         form = ConsultationForm(request.POST)
#         if form.is_valid():
#             consultation = form.save(commit=False)
#             consultation.appointment = appointment
#             consultation.doctor = request.user
#             consultation.save()
#             return redirect('doctor_appt_list')
#     else:
#         form = ConsultationForm()

#     return render(request, "consultation/add_consultation.html", {"form": form, "appointment": appointment})


@login_required
def add_consultation(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        status="APPROVE"
    )

    # Prevent duplicate consultation
    if hasattr(appointment, "consultation"):
        return redirect("doctor_appt_list")

    if request.method == "POST":
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.appointment = appointment
            consultation.doctor = request.user
            consultation.save()

            appointment.status = "COMPLETED"
            appointment.save()

            return redirect("doctor_appt_list")
    else:
        form = ConsultationForm()

    return render(
        request,
        "consultation/add_consultation.html",
        {"form": form, "appointment": appointment}
    )
