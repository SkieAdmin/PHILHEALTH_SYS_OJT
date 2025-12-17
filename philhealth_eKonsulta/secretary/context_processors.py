from .models import Appointment, Patient

#   global counts for the sectary
#-------------------------------------

def global_counts(request):
    return{
        'patients_count': Patient.objects.count(),
        'appointments_count': Appointment.objects.count(),
    }