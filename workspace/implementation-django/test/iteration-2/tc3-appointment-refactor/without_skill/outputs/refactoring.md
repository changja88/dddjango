# Refactoring: 진료 예약 시스템

## 1. settings.py -- 환경변수 분리

**문제점:** SECRET_KEY, 데이터베이스 비밀번호 등 민감 정보가 코드에 하드코딩되어 있다.

```python
# settings.py
import os

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'change-me-in-production')

DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'hospital_db'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

**변경 이유:**
- 비밀번호, SECRET_KEY 같은 민감 정보를 환경변수로 분리하여 보안을 확보한다.
- DEBUG 기본값을 `False`로 변경하여 실수로 프로덕션에서 디버그 모드가 켜지는 것을 방지한다.
- HOST, PORT도 환경변수로 외부 설정 가능하게 했다.

---

## 2. models.py -- 상태 필드를 Enum 기반 단일 필드로 통합

**문제점:** `is_confirmed`, `is_completed`, `is_cancelled` 세 개의 boolean 필드가 상호 배타적인 상태를 표현하고 있다. 동시에 `is_confirmed=True`이면서 `is_cancelled=True`인 비정상 상태가 가능하다.

```python
# models.py
from django.db import models


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        CONFIRMED = 'confirmed', '확정'
        COMPLETED = 'completed', '완료'
        CANCELLED = 'cancelled', '취소'

    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE,
        related_name='appointments',
    )
    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE,
        related_name='appointments',
    )
    date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['doctor', 'date']),
            models.Index(fields=['patient', 'date']),
        ]

    def __str__(self):
        return f"{self.patient} - {self.doctor} ({self.get_status_display()}, {self.date:%Y-%m-%d %H:%M})"

    # 상태 전이 허용 규칙
    _ALLOWED_TRANSITIONS = {
        Status.PENDING: {Status.CONFIRMED, Status.CANCELLED},
        Status.CONFIRMED: {Status.COMPLETED, Status.CANCELLED},
        Status.COMPLETED: set(),
        Status.CANCELLED: set(),
    }

    def transition_to(self, new_status):
        """상태를 전이한다. 허용되지 않은 전이는 ValueError를 발생시킨다."""
        allowed = self._ALLOWED_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"'{self.get_status_display()}' 상태에서 "
                f"'{Appointment.Status(new_status).label}' 상태로 전이할 수 없습니다."
            )
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])

    def confirm(self):
        self.transition_to(self.Status.CONFIRMED)

    def complete(self):
        self.transition_to(self.Status.COMPLETED)

    def cancel(self):
        self.transition_to(self.Status.CANCELLED)
```

**변경 이유:**
- `TextChoices`를 사용한 단일 `status` 필드로 통합하여 모순된 상태 조합을 원천 차단한다.
- `_ALLOWED_TRANSITIONS` 딕셔너리로 상태 전이 규칙을 한곳에 명시하여, 비즈니스 규칙 파악과 수정이 쉽다.
- `transition_to` 메서드가 모든 전이를 검증하므로, 뷰나 서비스 계층에서 상태 검증 코드를 반복할 필요가 없다.
- `confirm()`, `complete()`, `cancel()` 편의 메서드로 호출부 가독성을 높였다.
- `save(update_fields=...)` 를 사용하여 불필요한 전체 UPDATE를 방지한다.
- `related_name`을 추가하여 역참조 쿼리(`patient.appointments.all()`)를 명확하게 했다.
- `__str__`에 환자, 의사, 상태, 날짜 정보를 포함하여 admin에서의 가독성을 높였다.
- 자주 쿼리되는 필드 조합에 복합 인덱스를 추가했다.

---

## 3. views.py -- 예외 처리 및 구조 개선

**문제점:**
- `objects.get()`이 404를 반환하지 않고 `DoesNotExist` 예외로 500 에러를 발생시킨다.
- 상태 검증 로직이 뷰에 직접 들어있어 모델의 비즈니스 규칙과 중복된다.
- `View`를 직접 사용하여 보일러플레이트가 많다.

```python
# views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from .models import Appointment


class AppointmentConfirmView(View):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        try:
            appointment.confirm()
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=409)
        return JsonResponse({'status': 'confirmed'})
```

**변경 이유:**
- `get_object_or_404`를 사용하여 존재하지 않는 예약에 대해 적절한 404 응답을 반환한다.
- 상태 전이 검증을 모델의 `confirm()` 메서드에 위임하여 뷰가 얇아졌다.
- HTTP 상태 코드를 400 대신 409(Conflict)로 변경했다. 요청 형식이 잘못된 것이 아니라 리소스의 현재 상태와 충돌하는 것이므로 409가 의미상 정확하다.

---

## 4. serializers.py -- 명시적 필드 선언 및 읽기 전용 구분

**문제점:** `fields = '__all__'`은 모델 필드가 추가될 때 의도치 않게 API에 노출될 수 있다.

```python
# serializers.py
from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
    )

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'doctor',
            'date',
            'status',
            'status_display',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
```

**변경 이유:**
- 필드를 명시적으로 나열하여 모델 변경 시 API 스펙이 예기치 않게 변하는 것을 방지한다.
- `status`를 `read_only`로 지정하여 시리얼라이저를 통한 직접 상태 변경을 막고, 상태 전이는 반드시 전용 엔드포인트(`confirm`, `complete`, `cancel`)를 거치도록 강제한다.
- `status_display` 필드를 추가하여 API 소비자가 한글 라벨을 바로 사용할 수 있게 했다.

---

## 변경 요약

| 영역 | 원본 문제 | 리팩토링 내용 |
|------|----------|-------------|
| settings | 민감 정보 하드코딩, DEBUG 기본 True | 환경변수 분리, DEBUG 기본 False |
| models | 3개 boolean으로 상태 표현, 모순 상태 가능 | TextChoices 단일 필드 + 상태 전이 메서드 |
| views | DoesNotExist 미처리, 뷰에 검증 로직 중복 | get_object_or_404 + 모델 메서드 위임 |
| serializers | `__all__` 사용, 필드 보호 없음 | 명시적 필드 나열 + read_only 구분 |
