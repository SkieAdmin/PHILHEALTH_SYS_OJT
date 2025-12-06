from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required
from django.contrib.auth import get_user_model

User = get_user_model

def superadmin_login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if username == "admin" and password == "admin123":
            user = authenticate(request, username = username, password = password)
            if user and user.role == "SUPERADMIN":
                login(request, user)
                return redirect("superadmin_dashboard")
            else:
                return render(request, "superadmin_login.html", {"error":"Invalid SuperAdmin Credentails"})
        else:
            return render(request, "superadmin_login.html", {"error":"Only the Superadmin can login here"})
    return render(request, "superadmin_login.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.role == "DOCTOR":
                return redirect("docter_dashboard")
            elif user.role == "SECRETARY":
                return redirect("secretary_dashboard")
            elif user.role == "FINANCE":
                return redirect("finance_dashboard")
        else:
            return render(request, "login.html", {"error":"invalid credentials"})
    return render(request, "login.html")


@login_required
def create_user_view(request):
    if request.user.role != "SUPERADMIN":
        return render(request, "error.html",{"message":"only the superadmin can crete account"})
    
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        role = request.POST["role"]
        
        if role not in ["DOCTOR", "SECRETARY", "FINANCE"]:
            return render(request, "error.html", {"message":"superadmin can only create doctor, secretary and finance accounts"})
        
        User.objects.create_user(username=username, password=password, role=role)
        return redirect("superadmin_dashboard")
    
    return render(request, "create_user.html")


@login_required
def superadmin_dashboard(request):
    return render(request, 'superadmin.html')
@login_required
def doctor_dashboard(request):
    return render(request, 'doctor.html')
@login_required
def secretary_dashboard(request):
    return render(request, 'secretary.html')
@login_required
def finance_dashboard(request):
    return render(request, 'finace.html')
# Create your views here.   
