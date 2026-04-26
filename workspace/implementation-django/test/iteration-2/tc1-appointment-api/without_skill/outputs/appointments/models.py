from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Department(models.TextChoices):
    """진료과 선택지."""

    INTERNAL_MEDICINE = "internal_medicine", "내과"
    SURGERY = "surgery", "외과"
    PEDIATRICS = "pediatrics", "소아과"
    ORTHOPEDICS = "orthopedics", "정형외과"


class AppointmentStatus(models.TextChoices):
    """예약 상태 선택지."""

    PENDING = "pending", "대기"
    CONFIRMED = "confirmed", "확정"
    COMPLETED = "completed", "완료"
    CANCELLED = "cancelled", "취소"


# 허용되는 상태 전이 맵
VALID_STATUS_TRANSITIONS: dict[str, list[str]] = {
    AppointmentStatus.PENDING: [
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.CANCELLED,
    ],
    AppointmentStatus.CONFIRMED: [
        AppointmentStatus.COMPLETED,
        AppointmentStatus.CANCELLED,
    ],
    AppointmentStatus.COMPLETED: [],
    AppointmentStatus.CANCELLED: [],
}


class Patient(models.Model):
    """환자 모델."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profile",
        verbose_name="사용자 계정",
    )
    name = models.CharField("이름", max_length=100)
    date_of_birth = models.DateField("생년월일")
    phone = models.CharField("연락처", max_length=20)

    class Meta:
        verbose_name = "환자"
        verbose_name_plural = "환자 목록"

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"


class Doctor(models.Model):
    """의사 모델."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        verbose_name="사용자 계정",
    )
    name = models.CharField("이름", max_length=100)
    department = models.CharField(
        "진료과",
        max_length=30,
        choices=Department.choices,
    )
    license_number = models.CharField(
        "면허번호",
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = "의사"
        verbose_name_plural = "의사 목록"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_department_display()})"


class Appointment(models.Model):
    """진료 예약 모델."""

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name="환자",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name="의사",
    )
    datetime = models.DateTimeField("예약일시")
    department = models.CharField(
        "진료과",
        max_length=30,
        choices=Department.choices,
    )
    status = models.CharField(
        "상태",
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
    )
    created_at = models.DateTimeField("생성일시", auto_now_add=True)
    updated_at = models.DateTimeField("수정일시", auto_now=True)
    note = models.TextField("메모", blank=True, default="")

    class Meta:
        verbose_name = "예약"
        verbose_name_plural = "예약 목록"
        ordering = ["-datetime"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "datetime"],
                condition=~models.Q(status="cancelled"),
                name="unique_doctor_datetime_active",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.patient.name} -> {self.doctor.name} "
            f"({self.get_status_display()}, {self.datetime})"
        )

    def clean(self) -> None:
        """모델 수준 유효성 검사."""
        super().clean()
        if self.department and self.doctor_id:
            if self.department != self.doctor.department:
                raise ValidationError(
                    {
                        "department": (
                            f"선택한 진료과({self.get_department_display()})가 "
                            f"의사의 진료과({self.doctor.get_department_display()})와 "
                            f"일치하지 않습니다."
                        )
                    }
                )

    def transition_to(self, new_status: str) -> None:
        """
        상태를 전이한다. 유효하지 않은 전이는 ValidationError를 발생시킨다.

        허용 전이:
            대기 -> 확정, 취소
            확정 -> 완료, 취소
            완료 -> (불가)
            취소 -> (불가)
        """
        allowed = VALID_STATUS_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            current_display = self.get_status_display()
            new_display = dict(AppointmentStatus.choices).get(new_status, new_status)
            raise ValidationError(
                f"'{current_display}' 상태에서 '{new_display}' 상태로 변경할 수 없습니다."
            )
        self.status = new_status
