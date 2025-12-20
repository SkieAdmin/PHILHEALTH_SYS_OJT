from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal
from doctor.models import Consultation, Prescription
from .models import Billing, BillingItem, Transaction


# (Old Code) - Original finance_dashboard view
# def finance_dashboard(request):
#     consultations = Consultation.objects.filter(status="COMPLETED")
#     return render(request, "dashboard/payment.html", {"consultations": consultations})

# (Old Code) - Original update_payment_status view
# def update_payment_status(request, consultation_id, status):
#     consultation = get_object_or_404(Consultation, id=consultation_id)
#     if status == "PHILHEALTH":
#         amount = 0
#     else:
#         amount = consultation.get_total_amount()
#     payment, created = Payment.objects.get_or_create(
#         consultation=consultation,
#         defaults={
#             "amount": amount,
#             "status": status,
#             "processed_by": request.user
#         }
#     )
#     if not created:
#         payment.status = status
#         payment.processed_by = request.user
#         payment.save()
#     return redirect("payment_dashboard")


# (12-19-2025) Gocotano - Finance dashboard view showing summary cards
@login_required
def finance_dashboard(request):
    # (12-20-2025) Gocotano - Get counts for summary cards
    total_billings = Billing.objects.count()
    pending_count = Billing.objects.filter(status='PENDING').count()
    partial_count = Billing.objects.filter(status='PARTIAL').count()
    paid_count = Billing.objects.filter(status='PAID').count()
    philhealth_count = Billing.objects.filter(status='PHILHEALTH').count()

    return render(request, 'finance/finance_dashboard.html', {
        'total_billings': total_billings,
        'pending_count': pending_count,
        'partial_count': partial_count,
        'paid_count': paid_count,
        'philhealth_count': philhealth_count
    })


# (12-20-2025) Gocotano - Billing list view showing all billing records with filters
@login_required
def billing_list(request):
    # (12-19-2025) Gocotano - Get all consultations where appointment is COMPLETED (not consultation status)
    consultations = Consultation.objects.filter(appointment__status="COMPLETED").select_related(
        'appointment__patient',
        'appointment__doctor',
        'appointment__doctor__user',
        'doctor'
    ).order_by('-date')

    # (12-19-2025) Gocotano - Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        consultations = consultations.filter(
            Q(appointment__patient__first_name__icontains=search_query) |
            Q(appointment__patient__last_name__icontains=search_query)
        )

    # (12-19-2025) Gocotano - Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        if status_filter == 'NO_BILLING':
            consultations = consultations.filter(billing__isnull=True)
        else:
            consultations = consultations.filter(billing__status=status_filter)

    # (12-19-2025) Gocotano - Create billing records for consultations that don't have one
    billing_list = []
    for consultation in consultations:
        if not hasattr(consultation, 'billing'):
            billing = Billing.objects.create(
                consultation=consultation,
                total_amount=consultation.get_total_amount()
            )
            for prescription in consultation.prescriptions.all():
                BillingItem.objects.create(
                    billing=billing,
                    item_type='MEDICINE',
                    description=prescription.medicine.name,
                    quantity=prescription.quantity,
                    unit_price=prescription.medicine.price,
                    total_price=prescription.get_total_price()
                )
        else:
            billing = consultation.billing

        assigned_doctor = consultation.appointment.doctor
        billing_list.append({
            'consultation': consultation,
            'billing': billing,
            'patient': consultation.appointment.patient,
            'doctor': consultation.doctor,
            'assigned_doctor': assigned_doctor,
            'amount': billing.total_amount,
            'balance': billing.get_balance(),
            'status': billing.status
        })

    return render(request, 'finance/billing_list.html', {
        'billing_list': billing_list,
        'search_query': search_query,
        'status_filter': status_filter
    })


# (12-19-2025) Gocotano - Billing detail view showing patient info, diagnosis, and bill items
@login_required
def billing_detail(request, billing_id):
    billing = get_object_or_404(Billing, id=billing_id)
    consultation = billing.consultation
    patient = consultation.appointment.patient
    doctor = consultation.doctor
    # (12-19-2025) Gocotano - Get assigned doctor from appointment (DoctorProfile)
    assigned_doctor = consultation.appointment.doctor

    # (12-19-2025) Gocotano - Get all prescriptions/medicines for this consultation
    prescriptions = consultation.prescriptions.all()

    # (12-19-2025) Gocotano - Get billing items
    billing_items = billing.items.all()

    # (12-19-2025) Gocotano - Get transaction history
    transactions = billing.transactions.all()

    return render(request, 'finance/billing_detail.html', {
        'billing': billing,
        'consultation': consultation,
        'patient': patient,
        'doctor': doctor,
        'assigned_doctor': assigned_doctor,  # (12-19-2025) Gocotano - Pass assigned doctor
        'prescriptions': prescriptions,
        'billing_items': billing_items,
        'transactions': transactions,
        'balance': billing.get_balance()
    })


# (12-19-2025) Gocotano - Process payment (Cash or PhilHealth)
@login_required
def process_payment(request, billing_id):
    billing = get_object_or_404(Billing, id=billing_id)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'CASH')
        amount = Decimal(request.POST.get('amount', '0'))
        reference_number = request.POST.get('reference_number', '')
        remarks = request.POST.get('remarks', '')

        # (12-19-2025) Gocotano - Create transaction record
        transaction = Transaction.objects.create(
            billing=billing,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            remarks=remarks,
            processed_by=request.user
        )

        # (12-19-2025) Gocotano - Update billing based on payment method
        if payment_method == 'PHILHEALTH':
            billing.philhealth_coverage += amount
        else:
            billing.amount_paid += amount

        # (12-19-2025) Gocotano - Update billing status
        balance = billing.get_balance()
        if balance <= 0:
            billing.status = 'PAID'
        elif billing.amount_paid > 0 or billing.philhealth_coverage > 0:
            billing.status = 'PARTIAL'

        billing.save()

        messages.success(request, f'Payment of ₱{amount} processed successfully!')
        return redirect('billing_detail', billing_id=billing.id)

    return redirect('billing_detail', billing_id=billing.id)


# (12-19-2025) Gocotano - Apply full PhilHealth coverage
@login_required
def apply_philhealth(request, billing_id):
    billing = get_object_or_404(Billing, id=billing_id)

    if request.method == 'POST':
        # (12-19-2025) Gocotano - Apply full PhilHealth coverage to remaining balance
        balance = billing.get_balance()
        reference_number = request.POST.get('reference_number', '')
        remarks = request.POST.get('remarks', 'PhilHealth Full Coverage')

        # (12-19-2025) Gocotano - Create transaction for PhilHealth
        Transaction.objects.create(
            billing=billing,
            amount=balance,
            payment_method='PHILHEALTH',
            reference_number=reference_number,
            remarks=remarks,
            processed_by=request.user
        )

        billing.philhealth_coverage = billing.total_amount
        billing.status = 'PHILHEALTH'
        billing.save()

        messages.success(request, 'PhilHealth coverage applied successfully!')

    return redirect('billing_detail', billing_id=billing.id)
