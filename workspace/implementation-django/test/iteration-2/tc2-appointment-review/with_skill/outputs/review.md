# Code Review: 진료 예약 시스템

## Findings

### 1. Boolean Flag Proliferation in Doctor Model

```
[Boolean flag proliferation] -- Doctor 모델의 is_internal, is_surgeon, is_pediatric, is_orthopedic 필드는
BooleanField 남발에 해당한다. 현재 구조에서는 동시에 is_surgeon=True, is_orthopedic=True 같은 모순된
상태 조합이 가능하며, 새 전문과목 추가 시마다 컬럼을 추가해야 한다. TextChoices로 단일 필드에 표현해야 한다.
```

```python
# 현재 코드
is_internal = models.BooleanField(default=False)
is_surgeon = models.BooleanField(default=False)
is_pediatric = models.BooleanField(default=False)
is_orthopedic = models.BooleanField(default=False)

# 권장
class Specialty(models.TextChoices):
    INTERNAL = "internal", "Internal Medicine"
    SURGEON = "surgeon", "Surgeon"
    PEDIATRIC = "pediatric", "Pediatric"
    ORTHOPEDIC = "orthopedic", "Orthopedic"

specialty = models.CharField(
    max_length=20,
    choices=Specialty,
)
```

### 2. Missing Abstract Base Class for Shared Fields

```
[Missing Abstract Base Class] -- Doctor, Patient, Appointment 세 모델 모두 created_at, updated_at 필드를
동일하게 정의하고 있다. DRY 원칙 위반이며, TimeStampedModel 추상 베이스 클래스로 추출해야 한다.
```

```python
# 권장
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

### 3. Missing `__str__` Methods on All Models

```
[Model field ordering convention] -- Django 코딩 스타일에 따르면 모델은 fields -> managers -> Meta ->
__str__ -> save()/delete() -> custom methods 순서를 따라야 하며, __str__은 필수적으로 정의해야 한다.
세 모델 모두 __str__이 없어 admin 및 디버깅 시 객체 식별이 불가능하다.
```

### 4. N+1 Query in AppointmentView.get

```
[N+1 queries in view] -- for 루프 내에서 apt.patient.name과 apt.doctor.name에 접근하므로, 예약 N건에 대해
2N번의 추가 쿼리가 발생한다. select_related("patient", "doctor")를 사용하여 단일 JOIN 쿼리로 해결해야 한다.
```

```python
# 현재 코드
appointments = Appointment.objects.all()
for apt in appointments:
    result.append({
        'patient': apt.patient.name,  # 추가 쿼리
        'doctor': apt.doctor.name,    # 추가 쿼리
        ...
    })

# 권장
appointments = Appointment.objects.select_related("patient", "doctor")
```

### 5. save() Without update_fields

```
[save() without update_fields] -- post 메서드에서 apt.status = 'confirmed' 후 apt.save()를 호출하면
모든 필드가 UPDATE SET 절에 포함된다. 변경된 status 필드만 지정해야 한다.
```

```python
# 현재 코드
apt.status = 'confirmed'
apt.save()

# 권장
apt.status = 'confirmed'
apt.save(update_fields=["status"])
```

### 6. Unnecessary Create-Then-Update Pattern

```
[Fat view with business logic] -- post 메서드에서 Appointment를 status='pending'으로 생성한 직후 즉시
'confirmed'로 변경하고 다시 save()하는 것은 불필요한 2회 DB 쓰기다. 처음부터 'confirmed'로 생성하거나,
이 로직이 비즈니스 규칙이라면 모델 메서드나 서비스 레이어로 추출해야 한다.
```

```python
# 현재 코드: 2번의 DB 쓰기
apt = Appointment.objects.create(
    patient_id=data['patient_id'],
    doctor_id=data['doctor_id'],
    datetime=data['datetime'],
    status='pending'
)
apt.status = 'confirmed'
apt.save()

# 권장 (단순 생성의 경우)
apt = Appointment.objects.create(
    patient_id=data['patient_id'],
    doctor_id=data['doctor_id'],
    datetime=data['datetime'],
    status='confirmed',
)
```

### 7. Signal Used for Same-App Logic

```
[Signal used for same-app logic] -- notify_doctor 시그널은 같은 모듈 내 Appointment 모델의 post_save에
연결되어 있다. 시그널은 서드파티 모델 후크 또는 순환 의존 방지 용도에만 사용해야 한다. 같은 앱 내 로직은
save() 오버라이드 또는 서비스 함수에서 직접 호출하는 것이 명시적이고 디버깅이 쉽다.
```

```python
# 현재 코드: 암묵적 결합
@receiver(post_save, sender=Appointment)
def notify_doctor(sender, instance, created, **kwargs):
    if created:
        send_notification(instance.doctor, f"새 예약: {instance.patient.name}")

# 권장: 서비스 함수에서 직접 호출
def appointment_create(*, patient_id, doctor_id, datetime_val):
    apt = Appointment.objects.create(
        patient_id=patient_id,
        doctor_id=doctor_id,
        datetime=datetime_val,
        status="confirmed",
    )
    send_notification(apt.doctor, f"새 예약: {apt.patient.name}")
    return apt
```

### 8. Missing Input Validation and Error Handling in View

```
[Fat view with business logic / Security] -- post 메서드에서 json.loads(request.body)가 실패할 경우의
예외 처리가 없고, data['patient_id'] 등 키가 없을 때의 처리도 없다. 또한 datetime 필드명이 Python
내장 모듈명과 충돌한다. 존재하지 않는 patient_id나 doctor_id에 대한 검증도 없다.
```

### 9. Missing Import Statements

```
[Coding style] -- View, JsonResponse, json 등이 import 없이 사용되고 있다. send_notification 함수도
정의나 import가 보이지 않는다.
```

### 10. STATUS_CHOICES Should Use TextChoices

```
[TextChoices not used] -- Appointment.STATUS_CHOICES가 리스트 튜플 방식으로 정의되어 있다.
Django 3.0+ 이후 권장하는 TextChoices 열거형을 사용해야 한다. TextChoices는 타입 안전성과
코드 자동완성 지원을 제공한다.
```

```python
# 현재 코드
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
]
status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

# 권장
class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"

status = models.CharField(max_length=20, choices=Status, default=Status.PENDING)
```

### 11. `datetime` Field Name Shadows Python Built-in

```
[Naming convention] -- Appointment 모델의 datetime 필드가 Python 표준 라이브러리의 datetime 모듈명과
동일하여 해당 모듈 스코프에서 datetime 임포트 사용 시 충돌이 발생한다. scheduled_at이나
appointment_datetime 등으로 변경해야 한다.
```

---

## Review Checklist

- [x] **Project structure**: settings split, apps isolated, no circular deps -- 단일 파일이므로 구조 판단 불가, 해당 없음
- [x] **Model field ordering**: fields -> managers -> Meta -> __str__ -> save -> custom methods -- `__str__` 메서드 누락 (Finding 3)
- [x] **Boolean flag proliferation**: should be TextChoices/IntegerChoices -- Doctor 모델에서 발견 (Finding 1)
- [x] **Missing select_related/prefetch_related on FK/M2M access in loops** -- AppointmentView.get에서 발견 (Finding 4)
- [x] **N+1 queries in views or templates** -- AppointmentView.get에서 발견 (Finding 4)
- [x] **save() without update_fields when only specific fields changed** -- AppointmentView.post에서 발견 (Finding 5)
- [x] **Signals used for same-app logic** -- notify_doctor 시그널에서 발견 (Finding 7)
- [x] **fields = "__all__" or exclude in ModelForm/Serializer** -- 해당 없음 (ModelForm/Serializer 미사용)
- [x] **Multi-table inheritance where Abstract Base Class suffices** -- 해당 없음 (상속 미사용, 단 ABC 미도입 문제는 Finding 2)
- [x] **Raw SQL with string interpolation** -- 해당 없음 (Raw SQL 미사용)
- [x] **Missing CSRF protection or @csrf_exempt without justification** -- View 기반 JSON API로 CSRF 미들웨어가 적용된다고 가정하면 해당 없음, 단 DRF 없이 JSON API를 구현하는 패턴 자체가 비관용적
- [x] **CBV with 4+ Mixins or deeply customized generic view** -- 해당 없음
- [x] **Fat views with business logic that belongs in model/service** -- AppointmentView.post에서 발견 (Finding 6, 7)
- [x] **Missing assertNumQueries in performance-critical test paths** -- 테스트 코드 없음, 테스트 작성 시 assertNumQueries 포함 필요
- [x] **Django 5.x features not used where applicable** -- STATUS_CHOICES에 TextChoices 미사용 (Finding 10), db_default 활용 가능 여부 검토 권장
