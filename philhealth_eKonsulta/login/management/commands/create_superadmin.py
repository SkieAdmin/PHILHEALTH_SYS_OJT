from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "create fixed superadmin"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        Config_User = input("[+] Enter the username for the superadmin: ")
        Config_Pass = input("[+] Enter the password for the superadmin: ")
        Config_Email = input("[+] Enter the email for the superadmin: ")
        if not User.objects.filter(username = Config_User).exists():
            User.objects.create_superuser(
                username = Config_User,
                password = Config_Pass,
                role = "SUPERADMIN",
                email = Config_Email
            )
            self.stdout.write(self.style.SUCCESS("SuperAdmin Successfully"))
        else:
            self.stdout.write(self.style.SUCCESS("SuperAdmin already exists"))