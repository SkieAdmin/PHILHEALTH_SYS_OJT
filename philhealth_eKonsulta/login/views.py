
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import IntegrityError

from .models import DoctorProfile, SecretaryProfile, FinanceProfile

User = get_user_model()





# -------------------------
#       LOGIN VIEWS
# -------------------------

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.role == "DOCTOR":
                return redirect("doctor_dashboard")
            elif user.role == "SECRETARY":
                return redirect("secretary_dashboard")
            elif user.role == "FINANCE":
                return redirect("finance_dashboard")
        else:
            return render(request, "login/login.html", {"error": "Invalid credentials"})

    return render(request, "login/login.html")


def superadmin_login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user and user.role == "SUPERADMIN":
            login(request, user)
            return redirect("superadmin_dashboard")
        else:
            return render(
                request,
                "login/superadmin_login.html",
                {"error": "Invalid SuperAdmin credentials"},
            )

    return render(request, "login/superadmin_login.html")


# -------------------------
#        USER CRUD
# -------------------------

@login_required
def create_user_view(request):
    if request.user.role != "SUPERADMIN":
        return render(request, "login/error.html", {"message": "Access denied."})

    if request.method == "POST":
        role = request.POST["role"]

        if role == "DOCTOR":
            return redirect("doctor_registration")
        elif role == "SECRETARY":
            return redirect("secretary_registration")
        elif role == "FINANCE":
            return redirect("finance_registration")

        return redirect("list_users")

    return render(request, "login/create_user.html")


@login_required
def list_users_view(request):
    if request.user.role != "SUPERADMIN":
        return render(request, "login/error.html", {"message": "Access denied."})

    users = User.objects.exclude(role="SUPERADMIN")
    return render(request, "login/list_users.html", {"users": users})


@login_required
def update_user_view(request, user_id):
    if request.user.role != "SUPERADMIN":
        return render(request, "login/error.html", {"message": "Access denied."})

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.username = request.POST["username"]
        user.role = request.POST["role"]
        user.save()
        return redirect("list_users")

    return render(request, "login/create_user.html", {"user": user})


@login_required
def delete_user_view(request, user_id):
    if request.user.role != "SUPERADMIN":
        return render(request, "login/error.html", {"message": "Access denied."})

    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect("list_users")


# -------------------------
#   REGISTRATION FUNCTIONS
# -------------------------

@login_required
def doctor_registration(request):
    if request.user.role != "SUPERADMIN":
        return render(request, "login/error.html", {"message": "Access denied."})

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        employee_id = request.POST.get("employee_id")
        specialization = request.POST.get("specialization")
        license_number = request.POST.get("license_number")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        # Prevent duplicate username/email
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("doctor_registration")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect("doctor_registration")

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                role="DOCTOR",
                email=email,
                is_staff=True,
                is_active=True
            )

            DoctorProfile.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                employee_id=employee_id,
                specialization=specialization,
                license_number=license_number,
                phone=phone,
                email=email
            )

            messages.success(request, "Doctor registered successfully!")
            return redirect("doctor_registration")

        except IntegrityError:
            messages.error(request, "Error creating doctor account.")
            return redirect("doctor_registration")

    return render(request, "user_registration/doctor_registration.html")


@login_required
def secretary_registration(request):
    if request.user.role != "SUPERADMIN":
        return render(request, "login/error.html", {"message": "Access denied."})

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        employee_id = request.POST["employee_id"]
        department = request.POST["department"]
        phone = request.POST["phone"]
        email = request.POST["email"]

        user = User.objects.create_user(
            username=username,
            password=password,
            role="SECRETARY",
            email=email,
            is_staff=True,
            is_active=True
        )

        SecretaryProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            employee_id=employee_id,
            department=department,
            phone=phone,
            email=email
        )

        messages.success(request, "Secretary registered successfully!")
        return redirect("secretary_registration")

    return render(request, "user_registration/secretary_registration.html")


@login_required
def finance_registration(request):
    if request.user.role != "SUPERADMIN":
        return render(request, "login/error.html", {"message": "Access denied."})

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        employee_id = request.POST["employee_id"]
        position = request.POST["position"]
        phone = request.POST["phone"]
        email = request.POST["email"]

        user = User.objects.create_user(
            username=username,
            password=password,
            role="FINANCE",
            email=email,
            is_staff=True,
            is_active=True
        )

        FinanceProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            employee_id=employee_id,
            position=position,
            phone=phone,
            email=email
        )

        messages.success(request, "Finance staff registered successfully!")
        return redirect("finance_registration")

    return render(request, "user_registration/finance_registration.html")


# -------------------------
#        DASHBOARDS
# -------------------------

@login_required
def superadmin_dashboard(request):
    return render(request, "landing_pages/superadmin.html")


@login_required
def doctor_dashboard(request):
    return render(request, "landing_pages/doctor.html")


@login_required
def secretary_dashboard(request):
    return render(request, "landing_pages/secretary.html")


@login_required
def finance_dashboard(request):
    return render(request, "landing_pages/finance.html")


# -------------------------
#        LOGOUT
# -------------------------

def user_logout(request):
    logout(request)
    return redirect("login")

#-------------------------------------
#     get inforamtion for the users
#-------------------------------------

def doctor_dashboard(request):
    if request.user.role != "DOCTOR":
        return render(request, "login/error.html", {"message": "Access denied."})
    doctor_profile = get_object_or_404(DoctorProfile, user = request.user)
    return render(request, "landing_pages/doctor.html",{"doctor": doctor_profile})

def secretary_dashboard(request):
    if request.user.role != "SECRETARY":
        return render(request, "login/error.html", {"message": "Access denied"})
    secretary_profile = get_object_or_404(SecretaryProfile, user = request.user)
    return render(request, "landing_pages/secretary.html",{"secretary": secretary_profile})

