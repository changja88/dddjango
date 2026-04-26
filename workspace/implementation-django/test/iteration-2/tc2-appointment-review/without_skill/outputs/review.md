# Code Review: 진료 예약 시스템

## 1. N+1 Query 문제 (심각도: 높음)

`AppointmentView.get`에서 모든 예약을 순회하며 `apt.patient.name`, `apt.doctor.name`에 접근한다. `select_related`가 없으므로 예약 건수만큼 추가 쿼리가 발생한다.

```python
# 문제
appointments = Appointment.objects.all()

# 수정
appointments = Appointment.objects.select_related('patient', 'doctor').all()
```

## 2. 불필요한 이중 저장 (심각도: 높음)

`post` 메서드에서 `create(status='pending')` 직후 `status = 'confirmed'`로 변경하고 `save()`를 다시 호출한다. DB 쓰기가 2회 발생하며, 첫 번째 `create` 시 `post_save` 시그널이 `created=True`로 트리거되어 아직 `pending` 상태인 예약에 대해 알림이 발송된다.

```python
# 문제
apt = Appointment.objects.create(..., status='pending')
apt.status = 'confirmed'
apt.save()

# 수정 — 처음부터 confirmed로 생성하거나, 비즈니스 로직상 pending이 필요하면 시그널 로직을 재검토
apt = Appointment.objects.create(..., status='confirmed')
```

## 3. 누락된 import (심각도: 높음)

`View`, `JsonResponse`, `json`, `send_notification`이 import되지 않았다. 실행 시 `NameError`가 발생한다.

```python
import json
from django.http import JsonResponse
from django.views import View
```

`send_notification`도 정의나 import이 없다.

## 4. 입력 유효성 검증 부재 (심각도: 높음)

`post` 메서드에서 `request.body`를 파싱한 후 `data['patient_id']`, `data['doctor_id']`, `data['datetime']` 키를 검증 없이 직접 참조한다.

- 키가 없으면 `KeyError` 발생
- 존재하지 않는 `patient_id`/`doctor_id`는 `IntegrityError` 발생
- `datetime` 문자열 포맷 검증 없음

Django Form이나 DRF Serializer를 사용하여 유효성 검증을 추가해야 한다.

## 5. Doctor 모델의 Boolean 필드 남용 (심각도: 중간)

`is_internal`, `is_surgeon`, `is_pediatric`, `is_orthopedic` 4개의 Boolean 필드로 전문과목을 표현하고 있다. 새로운 과목이 추가될 때마다 마이그레이션이 필요하고, 조합 관리가 어렵다.

```python
# 수정 — 별도 모델로 분리
class Specialty(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialties = models.ManyToManyField(Specialty)
```

## 6. Signal에서의 외래키 접근 (심각도: 중간)

`notify_doctor` 시그널 내부에서 `instance.patient.name`에 접근한다. `post_save` 시점에 `patient`가 prefetch되어 있지 않으면 추가 쿼리가 발생하며, `send_notification`이 실패할 경우 예외가 전파되어 트랜잭션에 영향을 줄 수 있다.

```python
@receiver(post_save, sender=Appointment)
def notify_doctor(sender, instance, created, **kwargs):
    if created:
        try:
            patient_name = instance.patient.name
            send_notification(instance.doctor, f"새 예약: {patient_name}")
        except Exception:
            logger.exception("알림 발송 실패")
```

## 7. CSRF 보호 미비 (심각도: 중간)

`View` 기반 클래스에서 POST 요청을 처리하지만, `csrf_exempt` 데코레이터도 없고 CSRF 토큰 처리 로직도 없다. API 전용이라면 DRF의 `APIView`를 사용하거나, 명시적으로 `csrf_exempt`를 적용해야 한다.

## 8. 예약 중복 방지 로직 부재 (심각도: 중간)

같은 의사에게 같은 시간에 여러 예약이 생성되는 것을 방지하는 로직이 없다.

```python
class Appointment(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'datetime'],
                name='unique_doctor_datetime'
            )
        ]
```

## 9. datetime 필드명 충돌 (심각도: 낮음)

`Appointment.datetime`은 Python 표준 라이브러리 `datetime` 모듈과 이름이 충돌한다. `scheduled_at`, `appointment_time` 등으로 변경하는 것이 좋다.

## 10. 문자열 변환 방식 (심각도: 낮음)

`str(apt.datetime)`은 ISO 포맷을 보장하지 않는다. `apt.datetime.isoformat()`을 사용하거나 DRF Serializer의 `DateTimeField`를 활용하는 것이 일관성 있다.

## 요약

| 구분 | 항목 수 |
|------|---------|
| 높음 | 4건 (N+1 쿼리, 이중 저장, import 누락, 입력 검증 부재) |
| 중간 | 4건 (Boolean 필드 남용, Signal 예외 처리, CSRF, 중복 예약) |
| 낮음 | 2건 (필드명 충돌, 문자열 변환) |
