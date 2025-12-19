from django.shortcuts import render, get_object_or_404, redirect
from doctor.models import Consultation
from .models import Payment

def finance_dashboard(request):
    consultations = Consultation.objects.filter(status="COMPLETED")
    return render(request, "dashboard/payment.html", {"consultations": consultations})

def update_payment_status(request, consultation_id, status):
    consultation = get_object_or_404(Consultation, id=consultation_id)

    # PhilHealth = no payment
    if status == "PHILHEALTH":
        amount = 0
    else:
        amount = consultation.get_total_amount()

    payment, created = Payment.objects.get_or_create(
        consultation=consultation,
        defaults={
            "amount": amount,
            "status": status,
            "processed_by": request.user
        }
    )

    if not created:
        payment.status = status
        payment.processed_by = request.user
        payment.save()

    return redirect("payment_dashboard")
