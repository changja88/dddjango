# apps/appointments/services.py

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.doctors.models import Doctor
from apps.patients.models import Patient


def appointment_create(
    *,
    patient: Patient,
    doctor: Doctor,
    scheduled_at,
    department: str,
    note: str = "",
) -> Appointment:
    appointment = Appointment(
        patient=patient,
        doctor=doctor,
        scheduled_at=scheduled_at,
        department=department,
        note=note,
    )
    appointment.full_clean()
    appointment.save()
    return appointment


@transaction.atomic
def appointment_confirm(*, appointment: Appointment) -> Appointment:
    appointment = (
        Appointment.objects.select_for_update().get(pk=appointment.pk)
    )
    appointment.confirm()
    return appointment


@transaction.atomic
def appointment_complete(*, appointment: Appointment) -> Appointment:
    appointment = (
        Appointment.objects.select_for_update().get(pk=appointment.pk)
    )
    appointment.complete()
    return appointment


@transaction.atomic
def appointment_cancel(*, appointment: Appointment) -> Appointment:
    appointment = (
        Appointment.objects.select_for_update().get(pk=appointment.pk)
    )
    appointment.cancel()
    return appointment


def appointment_list_for_patient(*, patient: Patient):
    return (
        Appointment.objects.select_related("doctor__user")
        .for_patient(patient)
        .order_by("-scheduled_at")
    )


def appointment_list_for_doctor(*, doctor: Doctor):
    return (
        Appointment.objects.select_related("patient__user")
        .for_doctor(doctor)
        .order_by("-scheduled_at")
    )


def appointment_upcoming_for_doctor(*, doctor: Doctor):
    return (
        Appointment.objects.select_related("patient__user")
        .for_doctor(doctor)
        .upcoming()
        .exclude(status=Appointment.Status.CANCELLED)
        .order_by("scheduled_at")
    )
