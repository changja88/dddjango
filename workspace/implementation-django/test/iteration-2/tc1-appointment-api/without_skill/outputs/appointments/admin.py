from django.contrib import admin

from .models import Appointment, Doctor, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["name", "date_of_birth", "phone", "user"]
    search_fields = ["name", "phone"]


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "license_number", "user"]
    list_filter = ["department"]
    search_fields = ["name", "license_number"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "patient",
        "doctor",
        "datetime",
        "department",
        "status",
        "created_at",
    ]
    list_filter = ["status", "department", "datetime"]
    search_fields = ["patient__name", "doctor__name"]
    raw_id_fields = ["patient", "doctor"]
    readonly_fields = ["created_at", "updated_at"]
