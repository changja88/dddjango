from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Now


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# patients app -- apps/patients/models.py
# ---------------------------------------------------------------------------


class Patient(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"


# ---------------------------------------------------------------------------
# doctors app -- apps/doctors/models.py
# ---------------------------------------------------------------------------


class Doctor(TimeStampedModel):
    class Department(models.TextChoices):
        INTERNAL_MEDICINE = "internal_medicine", "내과"
        SURGERY = "surgery", "외과"
        PEDIATRICS = "pediatrics", "소아과"
        ORTHOPEDICS = "orthopedics", "정형외과"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )
    department = models.CharField(
        max_length=20,
        choices=Department,
    )
    license_number = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["department", "user__last_name"]

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.get_department_display()})"


# ---------------------------------------------------------------------------
# appointments app -- apps/appointments/models.py
# ---------------------------------------------------------------------------


class AppointmentQuerySet(models.QuerySet):
    def for_patient(self, patient):
        return self.filter(patient=patient)

    def for_doctor(self, doctor):
        return self.filter(doctor=doctor)

    def pending(self):
        return self.filter(status=Appointment.Status.PENDING)

    def confirmed(self):
        return self.filter(status=Appointment.Status.CONFIRMED)

    def upcoming(self):
        from django.utils import timezone

        return self.filter(scheduled_at__gte=timezone.now())


class Appointment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "대기"
        CONFIRMED = "confirmed", "확정"
        COMPLETED = "completed", "완료"
        CANCELLED = "cancelled", "취소"

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    scheduled_at = models.DateTimeField()
    department = models.CharField(
        max_length=20,
        choices=Doctor.Department,
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
        db_default=Status.PENDING,
    )
    note = models.TextField(blank=True)

    objects = AppointmentQuerySet.as_manager()

    class Meta:
        ordering = ["-scheduled_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "scheduled_at"],
                condition=~Q(status="cancelled"),
                name="unique_doctor_schedule",
            ),
            models.CheckConstraint(
                check=Q(
                    department__in=[
                        "internal_medicine",
                        "surgery",
                        "pediatrics",
                        "orthopedics",
                    ]
                ),
                name="valid_department",
            ),
            models.CheckConstraint(
                check=Q(
                    status__in=["pending", "confirmed", "completed", "cancelled"]
                ),
                name="valid_status",
            ),
        ]

    def __str__(self):
        return (
            f"Appointment: {self.patient} -> {self.doctor} "
            f"at {self.scheduled_at:%Y-%m-%d %H:%M}"
        )

    def clean(self):
        self._validate_no_duplicate_schedule()

    def _validate_no_duplicate_schedule(self):
        conflicting = (
            Appointment.objects.filter(
                doctor=self.doctor,
                scheduled_at=self.scheduled_at,
            )
            .exclude(status=self.Status.CANCELLED)
            .exclude(pk=self.pk)
        )
        if conflicting.exists():
            raise ValidationError(
                {
                    "scheduled_at": "해당 의사는 이 시간에 이미 예약이 있습니다.",
                }
            )

    def confirm(self):
        if self.status != self.Status.PENDING:
            raise ValidationError("대기 상태의 예약만 확정할 수 있습니다.")
        self.status = self.Status.CONFIRMED
        self.save(update_fields=["status", "updated_at"])

    def complete(self):
        if self.status != self.Status.CONFIRMED:
            raise ValidationError("확정 상태의 예약만 완료 처리할 수 있습니다.")
        self.status = self.Status.COMPLETED
        self.save(update_fields=["status", "updated_at"])

    def cancel(self):
        if self.status in (self.Status.COMPLETED, self.Status.CANCELLED):
            raise ValidationError("완료되거나 이미 취소된 예약은 취소할 수 없습니다.")
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])
