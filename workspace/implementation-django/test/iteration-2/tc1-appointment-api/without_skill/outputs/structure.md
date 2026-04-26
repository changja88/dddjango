# Appointment Management System - Project Structure

```
appointment_project/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── appointments/
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── permissions.py
    ├── admin.py
    └── apps.py
```

## Models

- **Patient**: 환자 (User FK, 이름, 생년월일, 연락처)
- **Doctor**: 의사 (User FK, 이름, 진료과, 면허번호)
- **Appointment**: 예약 (Patient FK, Doctor FK, 예약일시, 진료과, 상태)

## Status Flow

```
대기(PENDING) -> 확정(CONFIRMED) -> 완료(COMPLETED)
대기(PENDING) -> 취소(CANCELLED)
확정(CONFIRMED) -> 취소(CANCELLED)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/appointments/ | 예약 목록 (본인 것만) |
| POST | /api/appointments/ | 예약 생성 |
| GET | /api/appointments/{id}/ | 예약 상세 |
| PATCH | /api/appointments/{id}/ | 예약 수정 |
| POST | /api/appointments/{id}/confirm/ | 예약 확정 (의사 전용) |
| POST | /api/appointments/{id}/complete/ | 진료 완료 (의사 전용) |
| POST | /api/appointments/{id}/cancel/ | 예약 취소 |
| GET | /api/patients/ | 환자 목록 |
| GET | /api/doctors/ | 의사 목록 |

## Business Rules

1. 상태 전이: 대기 -> 확정 -> 완료 (순서 강제)
2. 취소는 대기/확정 상태에서만 가능
3. 같은 의사에게 같은 시간대 중복 예약 불가 (unique constraint)
4. 환자는 본인 예약만 조회 가능
5. 의사는 본인에게 배정된 예약만 조회 가능
6. 진료과: 내과/외과/소아과/정형외과
