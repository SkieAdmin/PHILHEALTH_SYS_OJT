from django.contrib import admin
from .models import CustomUser,DoctorProfile,SecretaryProfile,FinanceProfile

admin.site.register(CustomUser)
admin.site.register(DoctorProfile)
admin.site.register(SecretaryProfile)
admin.site.register(FinanceProfile)
# Register your models here.
