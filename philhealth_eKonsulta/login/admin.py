from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DoctorProfile, SecretaryProfile, FinanceProfile

#admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields':('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields':('is_active', 'is_staff', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Role Info', {'fields':('role',)}),
    )
    search_fields = ('username', 'email')
    ordering = ('date_joined',)

#doctor profile
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'specialization', 'license_number', 'phone', 'email', 'created_at')
    search_fields = ('employee_id', 'license_number', 'user_name', 'user_email')
    list_filter = ('specialization',)

#secretary profile
@admin.register(SecretaryProfile)
class SecretarProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'phone', 'email', 'created_at')
    search_fields = ('employee_id', 'department', 'user_name', 'user_email')
    list_filter = ('department',)

@admin.register(FinanceProfile)
class FinanceProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'position', 'phone', 'email', 'created_at')
    search_fields = ('employee_id', 'position', 'user_name', 'user_email')
    list_filter = ('position',)


