from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "create fixed superadmin"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        if not User.objects.filter(username = "admin").exists():
            User.objects.create_superuser(
                username = "admin",
                password = "admin123",
                role = "SUPERADMIN",
                email = "admin@example.com"
            )
            self.stdout.write(self.style.SUCCESS("SuperAdmin created: U = admin, P = admin123"))
        else:
            self.stdout.write(self.style.SUCCESS("SuperAdmin already exists"))