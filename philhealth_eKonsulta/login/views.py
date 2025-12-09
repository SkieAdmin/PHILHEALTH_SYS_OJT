from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

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
            return render(request, "login/superadmin_login.html", {"error": "Invalid SuperAdmin credentials"})
    return render(request, "login/superadmin_login.html")

# CRUD
@login_required
def create_user_view(request):
    if request.user.role != "SUPERADMIN":
        return render(request, "login/error.html", {"message": "Access denied."})
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        role = request.POST["role"]
        User.objects.create_user(username=username, password=password, role=role)
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




@login_required
def superadmin_dashboard(request):
    return render(request, "login/superadmin.html")
@login_required
def doctor_dashboard(request):
    return render(request, "login/doctor.html")
@login_required
def secretary_dashboard(request):
    return render(request, "login/secretary.html")
@login_required
def finance_dashboard(request):
    return render(request, "login/finance.html")


def user_logout(request):
    logout(request)
    return redirect("login")