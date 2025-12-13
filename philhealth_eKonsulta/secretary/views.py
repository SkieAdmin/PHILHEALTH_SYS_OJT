from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Appointment, Patient, PatientDocument, PatientPicture
from .forms import AppointmentForm, PatientForm, SingleDocumentForm, SinglePictureForm
# Add by Gocotano - as of 2025-12-13
from django.db.models import Q



#       Patient CRUD
#-------------------------------------
# Update by Gocotano - as of 2025-12-13 - Added search filter
def patient_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        patients = Patient.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(contact_number__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    else:
        patients = Patient.objects.all()
    return render(request, 'patient/patient_list.html', {'patients': patients, 'search_query': search_query})

# Update by Gocotano - as of 2025-12-13 - Added file uploads
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        document_form = SingleDocumentForm(request.POST, request.FILES)
        picture_form = SinglePictureForm(request.POST, request.FILES)

        if form.is_valid():
            patient = form.save()

            # Handle single document upload
            if 'document' in request.FILES:
                doc = request.FILES['document']
                description = request.POST.get('description', '')
                PatientDocument.objects.create(
                    patient=patient,
                    document=doc,
                    original_filename=doc.name,
                    description=description
                )

            # Handle single picture upload
            if 'picture' in request.FILES:
                pic = request.FILES['picture']
                caption = request.POST.get('caption', '')
                PatientPicture.objects.create(
                    patient=patient,
                    picture=pic,
                    original_filename=pic.name,
                    caption=caption
                )

            return redirect('patient_list')
    else:
        form = PatientForm()
        document_form = SingleDocumentForm()
        picture_form = SinglePictureForm()

    return render(request, 'patient/patient_form.html', {
        'form': form,
        'document_form': document_form,
        'picture_form': picture_form
    })

# Update by Gocotano - as of 2025-12-13 - Added file uploads
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        document_form = SingleDocumentForm(request.POST, request.FILES)
        picture_form = SinglePictureForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            # Handle single document upload
            if 'document' in request.FILES:
                doc = request.FILES['document']
                description = request.POST.get('description', '')
                PatientDocument.objects.create(
                    patient=patient,
                    document=doc,
                    original_filename=doc.name,
                    description=description
                )

            # Handle single picture upload
            if 'picture' in request.FILES:
                pic = request.FILES['picture']
                caption = request.POST.get('caption', '')
                PatientPicture.objects.create(
                    patient=patient,
                    picture=pic,
                    original_filename=pic.name,
                    caption=caption
                )

            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
        document_form = SingleDocumentForm()
        picture_form = SinglePictureForm()

    return render(request, 'patient/patient_form.html', {
        'form': form,
        'document_form': document_form,
        'picture_form': picture_form,
        'patient': patient
    })

def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        return redirect('patient_list')
    return render(request, 'patient/patient_confirm_delete.html', {'patient': patient})

# Add by Gocotano - as of 2025-12-13
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'patient/patient_detail.html', {'patient': patient})

# Add by Gocotano - as of 2025-12-13
def delete_patient_document(request, pk):
    document = get_object_or_404(PatientDocument, pk=pk)
    patient_pk = document.patient.pk
    if request.method == 'POST':
        document.document.delete()
        document.delete()
    return redirect('patient_detail', pk=patient_pk)

# Add by Gocotano - as of 2025-12-13
def delete_patient_picture(request, pk):
    picture = get_object_or_404(PatientPicture, pk=pk)
    patient_pk = picture.patient.pk
    if request.method == 'POST':
        picture.picture.delete()
        picture.delete()
    return redirect('patient_detail', pk=patient_pk)


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