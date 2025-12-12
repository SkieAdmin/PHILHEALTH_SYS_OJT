# (Gocotano Changes) - Custom management command to create dummy accounts
# Usage: py manage.py create_dummy_acc

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from login.models import DoctorProfile, SecretaryProfile, FinanceProfile
import random

class Command(BaseCommand):
    help = "Create dummy accounts for Doctor, Secretary, and Finance roles (10-20 accounts)"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # (Gocotano Changes) - Dummy data lists for generating realistic mock data
        first_names = [
            "Juan", "Maria", "Jose", "Ana", "Pedro", "Rosa", "Carlos", "Elena",
            "Miguel", "Sofia", "Antonio", "Carmen", "Francisco", "Teresa", "Manuel",
            "Lucia", "Rafael", "Patricia", "Fernando", "Gloria"
        ]

        last_names = [
            "Dela Cruz", "Santos", "Reyes", "Garcia", "Mendoza", "Torres", "Flores",
            "Gonzales", "Ramos", "Cruz", "Bautista", "Aquino", "Villanueva", "Fernandez",
            "Castro", "Rivera", "Lopez", "Martinez", "Perez", "Hernandez"
        ]

        specializations = [
            "General Medicine", "Pediatrics", "Cardiology", "Dermatology",
            "Orthopedics", "Neurology", "Ophthalmology", "Gynecology",
            "Internal Medicine", "Surgery"
        ]

        departments = [
            "Outpatient Department", "Admissions", "Medical Records",
            "Billing", "Emergency", "Laboratory", "Radiology", "Pharmacy"
        ]

        positions = [
            "Finance Officer", "Accountant", "Billing Clerk", "Cashier",
            "Budget Analyst", "Financial Analyst", "Payroll Officer", "Auditor"
        ]

        created_count = {"DOCTOR": 0, "SECRETARY": 0, "FINANCE": 0}

        # (Gocotano Changes) - Create 5-7 doctors
        self.stdout.write(self.style.WARNING("Creating Doctor accounts..."))
        for i in range(random.randint(5, 7)):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"doctor_{first_name.lower()}_{i+1}"
            email = f"{username}@philhealth.com"
            employee_id = f"DOC-{1000 + i}"
            license_number = f"LIC-{random.randint(100000, 999999)}"

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password="password123",
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
                    specialization=random.choice(specializations),
                    license_number=license_number,
                    phone=f"09{random.randint(100000000, 999999999)}",
                    email=email
                )
                created_count["DOCTOR"] += 1
                self.stdout.write(f"  Created: {username}")

        # (Gocotano Changes) - Create 5-7 secretaries
        self.stdout.write(self.style.WARNING("Creating Secretary accounts..."))
        for i in range(random.randint(5, 7)):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"secretary_{first_name.lower()}_{i+1}"
            email = f"{username}@philhealth.com"
            employee_id = f"SEC-{2000 + i}"

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password="password123",
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
                    department=random.choice(departments),
                    phone=f"09{random.randint(100000000, 999999999)}",
                    email=email
                )
                created_count["SECRETARY"] += 1
                self.stdout.write(f"  Created: {username}")

        # (Gocotano Changes) - Create 5-7 finance staff
        self.stdout.write(self.style.WARNING("Creating Finance accounts..."))
        for i in range(random.randint(5, 7)):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"finance_{first_name.lower()}_{i+1}"
            email = f"{username}@philhealth.com"
            employee_id = f"FIN-{3000 + i}"

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password="password123",
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
                    position=random.choice(positions),
                    phone=f"09{random.randint(100000000, 999999999)}",
                    email=email
                )
                created_count["FINANCE"] += 1
                self.stdout.write(f"  Created: {username}")

        # (Gocotano Changes) - Summary
        total = sum(created_count.values())
        self.stdout.write(self.style.SUCCESS(f"\n=== SUMMARY ==="))
        self.stdout.write(self.style.SUCCESS(f"Doctors created: {created_count['DOCTOR']}"))
        self.stdout.write(self.style.SUCCESS(f"Secretaries created: {created_count['SECRETARY']}"))
        self.stdout.write(self.style.SUCCESS(f"Finance staff created: {created_count['FINANCE']}"))
        self.stdout.write(self.style.SUCCESS(f"Total accounts created: {total}"))
        self.stdout.write(self.style.WARNING(f"\nDefault password for all accounts: password123"))
# (End Gocotano Changes)
