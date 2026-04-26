# 진료 예약 시스템 리팩토링

## 개별 변경 사항

---

### 1. 설정(Settings) 분리 및 비밀 정보 환경 변수 처리

```
[Before]
# settings.py
SECRET_KEY = 'django-insecure-hospital-secret-key-12345'
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hospital_db',
        'USER': 'admin',
        'PASSWORD': 'admin123',
    }
}

[After]
# config/settings/base.py
import environ

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env()

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")
DATABASES = {
    "default": env.db("DATABASE_URL"),
}

# config/settings/local.py
from .base import *  # noqa: F401,F403

DEBUG = True
INSTALLED_APPS += ["debug_toolbar"]

# config/settings/production.py
from .base import *  # noqa: F401,F403

DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

[Reason] Project Structure [TSD] / Security [DDoc] -- 비밀 정보(SECRET_KEY, DB PASSWORD)를 코드에 하드코딩하면 소스 저장소 노출 시 보안 사고로 이어진다. django-environ으로 환경 변수에서 읽고, 설정을 base/local/production으로 분리하여 환경별 보안 수준을 다르게 적용한다.
```

---

### 2. Boolean 플래그 남발을 TextChoices로 대체

```
[Before]
class Appointment(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    date = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment {self.id}"

[After]
class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
        db_index=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

[Reason] Model Design [DDoc] -- is_confirmed, is_completed, is_cancelled 세 개의 BooleanField는 is_confirmed=True이면서 is_cancelled=True인 불가능한 상태 조합을 허용한다. TextChoices로 상태를 단일 필드에 표현하면 상태 전이가 명확해지고 불가능한 조합이 구조적으로 방지된다.
```

---

### 3. TimeStampedModel Abstract Base Class 추출

```
[Before]
class Appointment(models.Model):
    # ... 필드들 ...
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

[After]
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Appointment(TimeStampedModel):
    # created_at, updated_at 자동 상속
    ...

[Reason] Model Design [DDoc] [TSD] -- created_at, updated_at는 거의 모든 모델에서 반복되는 공통 필드다. Abstract Base Class로 추출하면 DRY 원칙을 지키고, 다른 모델(Patient, Doctor 등)에서도 재사용할 수 있다.
```

---

### 4. 모델 유효성 검증(clean + CheckConstraint) 추가

```
[Before]
# 유효성 검증 없음 -- 과거 날짜로 예약 생성 가능, DB 레벨 제약 없음

[After]
from django.core.exceptions import ValidationError
from django.utils import timezone


class Appointment(TimeStampedModel):
    # ... 필드들 ...

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(status="completed", date__gt=Now()),
                name="appointment_completed_not_future",
            ),
        ]
        indexes = [
            models.Index(
                fields=["doctor", "date"],
                name="idx_appointment_doctor_date",
            ),
            models.Index(
                fields=["status", "-date"],
                name="idx_appointment_status_date",
            ),
        ]

    def clean(self):
        if self.date and self.date < timezone.now():
            raise ValidationError(
                {"date": "예약 날짜는 현재 시각 이후여야 합니다."}
            )

[Reason] Model Validation [DDoc] -- clean()으로 Python 레벨 검증을 수행하고, CheckConstraint로 데이터베이스 레벨 제약을 함께 걸어 이중 방어한다. 인덱스는 doctor+date 복합 조회와 status+date 필터링에 대비한다.
```

---

### 5. Fat View의 비즈니스 로직을 모델 메서드로 추출

```
[Before]
class AppointmentConfirmView(View):
    def post(self, request, pk):
        apt = Appointment.objects.get(pk=pk)
        if apt.is_cancelled:
            return JsonResponse({'error': 'cancelled'}, status=400)
        if apt.is_completed:
            return JsonResponse({'error': 'already completed'}, status=400)
        apt.is_confirmed = True
        apt.save()
        return JsonResponse({'status': 'confirmed'})

[After]
# models.py
class Appointment(TimeStampedModel):
    # ... 필드들 ...

    def confirm(self):
        """예약을 확정한다."""
        if self.status == self.Status.CANCELLED:
            raise ValidationError("취소된 예약은 확정할 수 없습니다.")
        if self.status == self.Status.COMPLETED:
            raise ValidationError("이미 완료된 예약입니다.")
        self.status = self.Status.CONFIRMED
        self.save(update_fields=["status", "updated_at"])

    def complete(self):
        """예약을 완료 처리한다."""
        if self.status != self.Status.CONFIRMED:
            raise ValidationError("확정된 예약만 완료할 수 있습니다.")
        self.status = self.Status.COMPLETED
        self.save(update_fields=["status", "updated_at"])

    def cancel(self):
        """예약을 취소한다."""
        if self.status in (self.Status.COMPLETED, self.Status.CANCELLED):
            raise ValidationError("완료되었거나 이미 취소된 예약입니다.")
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])

# views.py
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class AppointmentConfirmView(APIView):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        try:
            appointment.confirm()
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "confirmed"})

[Reason] Fat Model, Thin View [TSD] / Performance [DDoc] -- 상태 전이 로직은 도메인 규칙이므로 모델에 캡슐화한다. 뷰는 HTTP 관심사(요청 파싱, 응답 생성)만 담당한다. save(update_fields=["status", "updated_at"])로 변경된 필드만 업데이트하여 동시성 환경에서 다른 필드 덮어쓰기를 방지하고 성능을 개선한다. get_object_or_404를 사용하여 존재하지 않는 예약에 대해 적절한 404 응답을 반환한다.
```

---

### 6. Serializer의 fields = '__all__'을 명시적 필드 목록으로 교체

```
[Before]
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

[After]
class AppointmentListSerializer(serializers.ModelSerializer):
    """목록 조회용 -- 최소 필드."""
    patient_name = serializers.CharField(source="patient.get_full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient_name",
            "doctor_name",
            "date",
            "status",
            "status_display",
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """상세 조회용 -- 전체 필드."""

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
            "date",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """생성용 -- 쓰기 필드만."""

    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "date", "notes"]

[Reason] DRF Serializer [DRF] -- fields = "__all__"은 모델에 민감한 필드가 추가될 때 자동으로 API에 노출되는 보안 위험이 있다. 액션별로 Serializer를 분리하여 목록 조회에서는 최소 정보만, 상세 조회에서는 전체 정보를, 생성 시에는 쓰기 가능한 필드만 노출한다.
```

---

### 7. 모델 __str__ 개선 및 필드 순서 정리

```
[Before]
def __str__(self):
    return f"Appointment {self.id}"

[After]
def __str__(self):
    return f"{self.patient} - {self.doctor} ({self.date:%Y-%m-%d %H:%M})"

[Reason] Design Philosophy [DDP] -- __str__은 admin과 디버깅에서 객체를 식별하는 데 사용된다. "Appointment 42" 같은 ID 기반 표현보다 환자, 의사, 날짜를 포함하면 의미 있는 식별이 가능하다.
```

---

### 8. Custom QuerySet 추출

```
[Before]
# QuerySet 커스터마이징 없음 -- 뷰에서 직접 필터링

[After]
class AppointmentQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=Appointment.Status.PENDING)

    def confirmed(self):
        return self.filter(status=Appointment.Status.CONFIRMED)

    def for_doctor(self, doctor):
        return self.filter(doctor=doctor)

    def for_patient(self, patient):
        return self.filter(patient=patient)

    def upcoming(self):
        return self.filter(date__gte=timezone.now()).order_by("date")

[Reason] QuerySet Patterns [DDoc] [TSD] -- 뷰에서 직접 필터를 작성하면 동일한 필터 조건이 여러 뷰에서 중복된다. Custom QuerySet 메서드로 체이닝 가능한 필터를 만들면 Appointment.objects.for_doctor(doc).upcoming().confirmed()처럼 의도가 명확한 쿼리를 조합할 수 있다.
```

---

## 리팩토링 완성 코드

### config/settings/base.py

```python
import environ

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env()

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")
DATABASES = {
    "default": env.db("DATABASE_URL"),
}

# ... 기타 공통 설정 ...
```

### config/settings/local.py

```python
from .base import *  # noqa: F401,F403

DEBUG = True
INSTALLED_APPS += ["debug_toolbar"]
```

### config/settings/production.py

```python
from .base import *  # noqa: F401,F403

DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
```

### models.py

```python
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Now
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AppointmentQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=Appointment.Status.PENDING)

    def confirmed(self):
        return self.filter(status=Appointment.Status.CONFIRMED)

    def for_doctor(self, doctor):
        return self.filter(doctor=doctor)

    def for_patient(self, patient):
        return self.filter(patient=patient)

    def upcoming(self):
        return self.filter(date__gte=timezone.now()).order_by("date")


class Appointment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    # -- DB fields --
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
        db_index=True,
    )
    notes = models.TextField(blank=True)

    # -- Manager --
    objects = AppointmentQuerySet.as_manager()

    # -- Meta --
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(status="completed", date__gt=Now()),
                name="appointment_completed_not_future",
            ),
        ]
        indexes = [
            models.Index(
                fields=["doctor", "date"],
                name="idx_appointment_doctor_date",
            ),
            models.Index(
                fields=["status", "-date"],
                name="idx_appointment_status_date",
            ),
        ]
        ordering = ["-date"]

    # -- __str__ --
    def __str__(self):
        return f"{self.patient} - {self.doctor} ({self.date:%Y-%m-%d %H:%M})"

    # -- Custom methods --
    def clean(self):
        if self.date and self.date < timezone.now():
            raise ValidationError(
                {"date": "예약 날짜는 현재 시각 이후여야 합니다."}
            )

    def confirm(self):
        """예약을 확정한다."""
        if self.status == self.Status.CANCELLED:
            raise ValidationError("취소된 예약은 확정할 수 없습니다.")
        if self.status == self.Status.COMPLETED:
            raise ValidationError("이미 완료된 예약입니다.")
        self.status = self.Status.CONFIRMED
        self.save(update_fields=["status", "updated_at"])

    def complete(self):
        """예약을 완료 처리한다."""
        if self.status != self.Status.CONFIRMED:
            raise ValidationError("확정된 예약만 완료할 수 있습니다.")
        self.status = self.Status.COMPLETED
        self.save(update_fields=["status", "updated_at"])

    def cancel(self):
        """예약을 취소한다."""
        if self.status in (self.Status.COMPLETED, self.Status.CANCELLED):
            raise ValidationError("완료되었거나 이미 취소된 예약입니다.")
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])
```

### views.py

```python
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment


class AppointmentConfirmView(APIView):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        try:
            appointment.confirm()
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "confirmed"})
```

### serializers.py

```python
from rest_framework import serializers

from .models import Appointment


class AppointmentListSerializer(serializers.ModelSerializer):
    """목록 조회용 -- 최소 필드."""

    patient_name = serializers.CharField(
        source="patient.get_full_name", read_only=True
    )
    doctor_name = serializers.CharField(
        source="doctor.get_full_name", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient_name",
            "doctor_name",
            "date",
            "status",
            "status_display",
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """상세 조회용 -- 전체 필드."""

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
            "date",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """생성용 -- 쓰기 필드만."""

    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "date", "notes"]
```
