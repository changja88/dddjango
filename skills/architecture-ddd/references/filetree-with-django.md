# DDD + Django 프로젝트 폴더 구조

Python/Django 프로젝트에서 DDD를 적용할 때의 권장 폴더 구조.

```
applications/
├── shared_kernel/                  # Shared Kernel (도메인 로직 포함 금지)
│   ├── value_object/               # 공통 값 객체 (Money, DateRange 등)
│   └── schema/                     # 공통 스키마 (ErrorOut 등)
│
└── <domain>/                       # Bounded Context 단위
    ├── domain_layer/               # 순수 도메인 모델 (Django ORM/signals 의존 금지)
    │   ├── <aggregate>/            # 애그리거트 단위 폴더 (트랜잭션 경계 = 폴더 경계)
    │   │   ├── <root>.py           # 애그리거트 루트 (불변식 보호, 비즈니스 메서드)
    │   │   ├── <entity>.py         # 내부 엔티티 (루트를 통해서만 접근)
    │   │   └── <value_object>.py   # 이 애그리거트 전용 값 객체 (frozen=True)
    │   ├── value_object/           # 여러 애그리거트에서 공유하는 값 객체
    │   ├── repository/             # 리포지토리 인터페이스 (ABC, 애그리거트 단위)
    │   │   └── <name>_repo.py      # class <Name>Repository(ABC): ...
    │   ├── event/                  # 도메인 이벤트 클래스 (프레임워크 무의존, 과거형 명명)
    │   │   └── <name>_events.py    # OrderConfirmedEvent, OrderCancelledEvent 등
    │   ├── service/                # 도메인 서비스 (무상태, 특정 엔티티에 속하지 않는 순수 도메인 로직)
    │   │   └── <purpose>/          # 목적별 하위 폴더
    │   └── specification/          # Specification 패턴 (선택, 복잡한 비즈니스 규칙 조합)
    │
    ├── application_layer/          # 유스케이스 조율 (비즈니스 로직 금지, 조율만)
    │   ├── *_service.py            # 응용 서비스 (네이밍: *_service.py)
    │   └── event_handlers.py       # 타 도메인 이벤트 구독 핸들러 (@receiver)
    │
    ├── infra_layer/                # 인프라 (프레임워크 의존, domain ABC 구현)
    │   ├── django_<domain>/        # Django 앱 (Django 자동 탐색이 필요한 것만)
    │   │   ├── apps.py
    │   │   ├── models/             # ORM 모델 (모델별 파일 분리)
    │   │   │   ├── __init__.py     # 모델 re-export
    │   │   │   └── <name>_model.py # ORM → domain entity 변환 책임
    │   │   ├── admin.py            # (선택) Django 자동 탐색
    │   │   └── management/         # (선택) Django 자동 탐색
    │   │       └── commands/
    │   ├── repository/             # 리포지토리 구현체 (domain ABC 구현, ORM → entity 변환)
    │   │   └── <name>_repo.py      # class Django<Name>Repository(<Name>Repository): ...
    │   ├── event_bus/              # 도메인 이벤트 → Django signals 변환
    │   │   └── signal_event_bus.py
    │   └── <adapter>/              # 기술적 관심사 (외부 API, 암호화, 파일 저장 등)
    │       └── *.py
    │
    ├── presentation_layer/         # API 인터페이스 (API + Schema만)
    │   ├── routers.py              # 도메인 라우터 등록
    │   ├── api/                    # 라우터/뷰 (*_api.py)
    │   └── schema/                 # 요청/응답 스키마 + 에러 코드 상수
    │
    └── tests/
        ├── conftest.py             # 테스트 픽스처
        ├── domain/                 # 순수 도메인 로직 (외부 의존 없음, 가장 빠름)
        ├── application/            # 서비스 로직 (mock repo, 이벤트 핸들러)
        ├── infra/                  # repository CRUD, 외부 서비스 연동
        └── api/                    # HTTP 요청/응답, 상태 코드, 인증
```

### Django 앱 규칙

- **위치**: `applications/<domain>/infra_layer/django_<domain>/` (네이밍: `django_` 접두사)
- **INSTALLED_APPS**: `applications.<domain>.infra_layer.django_<domain>` 형식으로 등록
- **모델 파일 분리**: `models.py` 대신 `models/` 폴더로 분리 (위 트리 참고)
  - 파일명: `<모델명>_model.py`
  - 클래스명: `<모델명>Model` — 반드시 `Model` 접미사
  - `models/__init__.py`에서 모든 모델을 re-export

### 도메인 간 읽기 import 규칙

- 타 도메인의 `application_layer` 서비스만 직접 import 허용
- `domain_layer`, `infra_layer` 직접 접근 금지
- 단방향만 허용 (순환 시 이벤트 패턴 또는 Shared Kernel로 해소)
