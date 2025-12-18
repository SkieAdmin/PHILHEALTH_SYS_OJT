from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from secretary.models import Appointment, DoctorProfile, Patient, PatientDocument, PatientPicture  #[12-17-2025 - Gocotano] - Added PatientDocument, PatientPicture imports
from .models import Consultation, Medicine, Prescription  # (12/18/2025 - Gocotano) - Updated imports for new models
from .forms import ConsultationForm
from django.db.models import Q  #[12-17-2025 - Gocotano] - Added Q for search filtering
from django.db.models import Exists, OuterRef  # (12/18/2025 - Gocotano) - Added for my_patients query
import json  # (12/18/2025 - Gocotano) - Added for parsing prescription JSON data

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


# (Old Code) - Original add_consultation view
# @login_required
# def add_consultation(request, appointment_id):
#     appointment = get_object_or_404(
#         Appointment,
#         id=appointment_id,
#         status="APPROVE"
#     )
#
#     # Prevent duplicate consultation
#     if hasattr(appointment, "consultation"):
#         return redirect("doctor_appt_list")
#
#     if request.method == "POST":
#         form = ConsultationForm(request.POST)
#         if form.is_valid():
#             consultation = form.save(commit=False)
#             consultation.appointment = appointment
#             consultation.doctor = request.user
#             consultation.save()
#
#             appointment.status = "COMPLETED"
#             appointment.save()
#
#             return redirect("doctor_appt_list")
#     else:
#         form = ConsultationForm()
#
#     return render(
#         request,
#         "consultation/add_consultation.html",
#         {"form": form, "appointment": appointment}
#     )


# (12/18/2025 - Gocotano) - Updated add_consultation view to handle multiple prescriptions
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

    # (12/18/2025 - Gocotano) - Get all active medicines for the dropdown
    medicines = Medicine.objects.filter(is_active=True)

    if request.method == "POST":
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.appointment = appointment
            consultation.doctor = request.user
            consultation.save()

            # (12/18/2025 - Gocotano) - Process prescription data from form
            prescriptions_json = request.POST.get('prescriptions_data', '[]')
            try:
                prescriptions_list = json.loads(prescriptions_json)
                for item in prescriptions_list:
                    medicine_id = item.get('medicine_id')
                    quantity = item.get('quantity', 1)
                    doctor_prescription = item.get('doctor_prescription', '')

                    if medicine_id:
                        medicine = Medicine.objects.filter(id=medicine_id).first()
                        if medicine:
                            Prescription.objects.create(
                                consultation=consultation,
                                medicine=medicine,
                                quantity=int(quantity),
                                doctor_prescription=doctor_prescription
                            )
            except json.JSONDecodeError:
                pass  # Handle invalid JSON gracefully

            appointment.status = "COMPLETED"
            appointment.save()

            return redirect("doctor_appt_list")
    else:
        form = ConsultationForm()

    return render(
        request,
        "consultation/add_consultation.html",
        {
            "form": form,
            "appointment": appointment,
            "medicines": medicines  # (12/18/2025 - Gocotano) - Pass medicines to template
        }
    )


# (12/18/2025 - Gocotano) - My Patients view - shows patients with APPROVED or COMPLETED appointments
@login_required
def my_patients(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)

    # (12/18/2025 - Gocotano) - Get unique patients with APPROVE or COMPLETED appointments for this doctor
    patients = Patient.objects.filter(
        appointment__doctor=doctor,
        appointment__status__in=['APPROVE', 'COMPLETED']
    ).distinct()

    # (12/18/2025 - Gocotano) - Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    patients = patients.order_by('last_name', 'first_name')

    return render(request, 'doctor/my_patients.html', {
        'patients': patients,
        'search_query': search_query
    })


# (12/18/2025 - Gocotano) - My Patient Detail view - shows patient details and consultation list
@login_required
def my_patient_detail(request, patient_id):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)

    # (12/18/2025 - Gocotano) - Verify this patient has appointments with this doctor
    has_appointment = Appointment.objects.filter(
        patient=patient,
        doctor=doctor,
        status__in=['APPROVE', 'COMPLETED']
    ).exists()

    if not has_appointment:
        return redirect('my_patients')

    # (12/18/2025 - Gocotano) - Get patient's documents and pictures
    documents = PatientDocument.objects.filter(patient=patient)
    pictures = PatientPicture.objects.filter(patient=patient)

    # (12/18/2025 - Gocotano) - Get all consultations for this patient with this doctor
    consultations = Consultation.objects.filter(
        appointment__patient=patient,
        doctor=request.user
    ).order_by('-date')

    # (12/18/2025 - Gocotano) - Get appointments for this patient
    appointments = Appointment.objects.filter(
        patient=patient,
        doctor=doctor
    ).order_by('-date')

    return render(request, 'doctor/my_patient_detail.html', {
        'patient': patient,
        'documents': documents,
        'pictures': pictures,
        'consultations': consultations,
        'appointments': appointments
    })
