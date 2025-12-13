from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient, PatientDocument, PatientPicture
# Update by Gocotano - as of 2025-12-13
from .forms import PatientForm, SingleDocumentForm, SinglePictureForm
# Add by Gocotano - as of 2025-12-13
from django.db.models import Q

# Old patient_list - commented out by Gocotano - as of 2025-12-13
# def patient_list(request):
#     patients = Patient.objects.all()
#     return render(request, 'secretary/patient_list.html', {'patients': patients})

# Update by Gocotano - as of 2025-12-13
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
    return render(request, 'secretary/patient_list.html', {'patients': patients, 'search_query': search_query})

# Old patient_create - commented out by Gocotano - as of 2025-12-13
# def patient_create(request):
#     if request.method == 'POST':
#         form = PatientForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('patient_list')
#     else:
#         form = PatientForm()
#     return render(request, 'secretary/patient_form.html', {'form': form})

# Update by Gocotano - as of 2025-12-13
# Updated to handle file uploads (documents and pictures) - one at a time
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
                    original_filename=doc.name,  # Add by Gocotano - as of 2025-12-13
                    description=description
                )

            # Handle single picture upload
            if 'picture' in request.FILES:
                pic = request.FILES['picture']
                caption = request.POST.get('caption', '')
                PatientPicture.objects.create(
                    patient=patient,
                    picture=pic,
                    original_filename=pic.name,  # Add by Gocotano - as of 2025-12-13
                    caption=caption
                )

            return redirect('patient_list')
    else:
        form = PatientForm()
        document_form = SingleDocumentForm()
        picture_form = SinglePictureForm()

    return render(request, 'secretary/patient_form.html', {
        'form': form,
        'document_form': document_form,
        'picture_form': picture_form
    })

# Old patient_update - commented out by Gocotano - as of 2025-12-13
# def patient_update(request, pk):
#     patient = get_object_or_404(Patient, pk=pk)
#     if request.method == 'POST':
#         form = PatientForm(request.POST, instance=patient)
#         if form.is_valid():
#             form.save()
#             return redirect('patient_list')
#     else:
#         form = PatientForm(instance=patient)
#     return render(request, 'secretary/patient_form.html', {'form': form})

# Update by Gocotano - as of 2025-12-13
# Updated to handle file uploads (documents and pictures) - one at a time
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
                    original_filename=doc.name,  # Add by Gocotano - as of 2025-12-13
                    description=description
                )

            # Handle single picture upload
            if 'picture' in request.FILES:
                pic = request.FILES['picture']
                caption = request.POST.get('caption', '')
                PatientPicture.objects.create(
                    patient=patient,
                    picture=pic,
                    original_filename=pic.name,  # Add by Gocotano - as of 2025-12-13
                    caption=caption
                )

            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
        document_form = SingleDocumentForm()
        picture_form = SinglePictureForm()

    return render(request, 'secretary/patient_form.html', {
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
    return render(request, 'secretary/patient_confirm_delete.html', {'patient': patient})

# Add by Gocotano - as of 2025-12-13
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'secretary/patient_detail.html', {'patient': patient})

# Add by Gocotano - as of 2025-12-13
# View to delete a patient document
def delete_patient_document(request, pk):
    document = get_object_or_404(PatientDocument, pk=pk)
    patient_pk = document.patient.pk
    if request.method == 'POST':
        document.document.delete()  # Delete the file from storage
        document.delete()
    return redirect('patient_detail', pk=patient_pk)

# Add by Gocotano - as of 2025-12-13
# View to delete a patient picture
def delete_patient_picture(request, pk):
    picture = get_object_or_404(PatientPicture, pk=pk)
    patient_pk = picture.patient.pk
    if request.method == 'POST':
        picture.picture.delete()  # Delete the file from storage
        picture.delete()
    return redirect('patient_detail', pk=patient_pk)