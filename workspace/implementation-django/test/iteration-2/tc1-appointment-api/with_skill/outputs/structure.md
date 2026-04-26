# 진료 예약 관리 시스템 프로젝트 구조

```
appointment_system/
    .gitignore
    .env.example
    manage.py
    requirements/
        base.txt
        dev.txt
        prod.txt
    config/
        __init__.py
        settings/
            __init__.py
            base.py
            local.py
            production.py
            test.py
        urls.py
        wsgi.py
        asgi.py
    apps/
        __init__.py
        patients/
            __init__.py
            models.py
            admin.py
            apps.py
            migrations/
                __init__.py
        doctors/
            __init__.py
            models.py
            admin.py
            apps.py
            migrations/
                __init__.py
        appointments/
            __init__.py
            models.py
            serializers.py
            views.py
            urls.py
            permissions.py
            services.py
            admin.py
            apps.py
            migrations/
                __init__.py
            tests/
                __init__.py
                test_models.py
                test_views.py
                test_services.py
```

## 앱 분리 기준

- `patients/` -- 환자 도메인 (사용자 프로필, 환자 정보)
- `doctors/` -- 의사 도메인 (의사 프로필, 진료과 정보)
- `appointments/` -- 예약 도메인 (예약 CRUD, 상태 전이, 중복 방지)
