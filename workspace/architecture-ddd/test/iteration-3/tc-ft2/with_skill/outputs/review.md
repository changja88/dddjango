# DDD Review: Django DDD 프로젝트 폴더 구조

## 리뷰 대상

```
applications/
├── shared_kernel/
│   └── utils.py
├── inventory/
│   ├── models.py        # Product, Warehouse, Stock (Django ORM)
│   ├── services.py      # 입고/출고 비즈니스 로직
│   ├── repositories.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── signals.py
│   ├── admin.py
│   └── tests.py
└── order/
    ├── models.py        # Order, OrderItem (Django ORM)
    ├── services.py      # 주문 생성 로직 (inventory.models 직접 import)
    ├── repositories.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── events.py
    ├── admin.py
    └── tests.py
```

---

## 심각도 범례

| 기호 | 의미 |
|------|------|
| CRITICAL | 구조적 원칙 위반 -- DDD 적용 의도 자체가 무효화됨 |
| MAJOR | 확장/유지보수 시 반드시 문제가 되는 설계 결함 |
| MINOR | 개선하면 좋지만 당장 장애를 일으키지는 않는 사항 |

---

## Findings

### CRITICAL-1. 바운디드 컨텍스트 간 직접 의존 -- 경계 침범

```
[Bounded Context Integrity] -- order/services.py에서 inventory.models.Stock을 직접 import하여
재고를 차감하는 것은 바운디드 컨텍스트 경계를 완전히 무시한 설계이다.
```

`order`와 `inventory`는 서로 다른 바운디드 컨텍스트다. "주문"과 "재고"는 각각 고유한 유비쿼터스 언어와 모델을 가진다. order 컨텍스트가 inventory의 도메인 모델을 직접 import하면 두 컨텍스트가 물리적으로 결합되어, inventory 모델 변경이 order를 깨뜨린다.

DDD 권장 폴더 구조의 도메인 간 읽기 import 규칙에 따르면:
- 타 도메인의 `application_layer` 서비스만 직접 import 허용
- `domain_layer`, `infra_layer` 직접 접근 금지
- 단방향만 허용 (순환 시 이벤트 패턴 또는 Shared Kernel로 해소)

**해결 방향**: 주문이 생성되면 `OrderPlacedEvent` 도메인 이벤트를 발행하고, inventory 컨텍스트의 이벤트 핸들러가 이를 구독하여 별도 트랜잭션에서 재고를 차감한다 (Vernon 규칙 4: 일관성 경계 밖에서는 결과적 일관성 사용). 동기적 호출이 반드시 필요하다면 최소한 ACL(충돌 방지 계층)을 두어 inventory 모델이 order 도메인으로 오염되지 않도록 방어해야 한다.

---

### CRITICAL-2. 계층 분리 없음 -- domain/application/infra 혼재

```
[DDD + Django 프로젝트 구조] -- domain_layer, application_layer, infra_layer, presentation_layer가
하나의 Django 앱 폴더에 혼재되어 있어 의존성 방향을 제어할 수 없다.
```

현재 구조에서 `models.py`, `services.py`, `repositories.py`, `serializers.py`, `views.py`가 모두 같은 폴더에 있다. 이 구조에서는 도메인 모델이 인프라(Django ORM)에 의존하는 것을 구조적으로 방지할 수 없다. 어떤 코드가 도메인 로직이고 어떤 코드가 응용 로직인지 파일 위치만으로는 판별이 불가능하다.

DDD + Django 권장 폴더 구조는 다음과 같이 계층을 명시적으로 분리한다:

```
applications/<domain>/
├── domain_layer/          # 순수 도메인 모델 (Django ORM/signals 의존 금지)
│   ├── <aggregate>/       # 애그리거트 단위 폴더
│   ├── repository/        # 리포지토리 인터페이스 (ABC)
│   ├── event/             # 도메인 이벤트 클래스
│   └── service/           # 도메인 서비스
├── application_layer/     # 유스케이스 조율 (비즈니스 로직 금지)
├── infra_layer/           # Django 앱, 리포지토리 구현체, 이벤트 버스
│   └── django_<domain>/   # Django 자동 탐색이 필요한 것만
└── presentation_layer/    # API 인터페이스
```

핵심은 `domain_layer`가 어떤 프레임워크에도 의존하지 않는 순수 Python으로 유지되어야 한다는 점이다. Django 앱(`models.py`, `admin.py` 등)은 `infra_layer/django_<domain>/` 안에 격리한다.

---

### CRITICAL-3. 도메인 모델이 Django ORM에 직접 의존

```
[Domain Model Independence] -- 도메인 모델이 models.Model을 상속하여
프레임워크와 결합되어 있다. 도메인 로직의 단독 테스트와 프레임워크 교체가 불가능하다.
```

Cosmic Python의 핵심 원칙: "ORM이 도메인 모델을 import하게 하라. 도메인 모델이 ORM을 import하면 안 된다."

현재 `models.py`에서 `models.Model`을 상속받아 도메인 엔티티를 정의하면, 도메인 로직을 테스트하기 위해 반드시 데이터베이스가 필요하다. 도메인 모델은 순수 Python 클래스(`@dataclass`)로 정의하고, ORM 모델은 infra_layer에 별도 배치하여 domain entity와 ORM model 간의 변환 책임을 리포지토리 구현체에 맡겨야 한다.

**권장 구조**:
- `domain_layer/<aggregate>/<root>.py` -- 순수 Python `@dataclass` 도메인 엔티티
- `infra_layer/django_<domain>/models/<name>_model.py` -- ORM 모델 (`Model` 접미사 필수)
- `infra_layer/repository/<name>_repo.py` -- ORM 모델과 도메인 엔티티 간 변환

---

### MAJOR-1. 빈혈 도메인 모델 가능성 (Anemic Domain Model)

```
[Rich Domain Model] -- models.py에 ORM 모델만, services.py에 비즈니스 로직 전부라는 구조는
전형적인 빈혈 도메인 모델 안티패턴이다.
```

`models.py`에는 데이터(필드)만 있고 `services.py`에 모든 비즈니스 로직(입고/출고, 주문 생성)이 몰려 있다면, 이는 Martin Fowler가 안티패턴으로 명명한 빈혈 도메인 모델이다. 절차적 프로그래밍과 본질적으로 동일하며, DDD를 적용하는 의미가 사라진다.

비즈니스 로직은 엔티티와 값 객체 안에 위치해야 한다. services.py의 로직 중 특정 애그리거트의 상태를 변경하거나 계산하는 로직은 해당 애그리거트 루트의 메서드로 이동하고, services.py는 조율(orchestration)만 담당하는 응용 서비스로 축소해야 한다.

---

### MAJOR-2. 애그리거트 경계 불명확

```
[Aggregate Design] -- models.py에 Product, Warehouse, Stock이 함께 있어
어디가 애그리거트 루트이고 어디가 내부 엔티티인지 경계가 보이지 않는다.
```

Vernon의 규칙 2(작은 애그리거트 설계)에 따르면, 애그리거트 단위로 폴더를 분리하여 트랜잭션 경계를 물리적으로 표현해야 한다. 권장 구조에서는 `domain_layer/<aggregate>/` 폴더 하나가 하나의 애그리거트를 나타내며, `<root>.py`가 애그리거트 루트, `<entity>.py`가 내부 엔티티, `<value_object>.py`가 전용 값 객체다.

Product, Warehouse, Stock이 각각 별도 애그리거트인지, Stock이 Warehouse 애그리거트의 내부 엔티티인지를 명확히 결정하고 폴더로 표현해야 한다.

---

### MAJOR-3. 리포지토리 인터페이스와 구현체 미분리

```
[Repository / DIP] -- repositories.py가 한 파일에 인터페이스와 구현을 함께 두고 있어
의존성 역전 원칙(DIP)이 적용되지 않았다.
```

리포지토리는 도메인 영역에 인터페이스(ABC)를 정의하고, 인프라 영역에서 구현해야 한다. 이렇게 해야 도메인 계층이 인프라에 의존하지 않으며, 테스트 시 인메모리 구현체로 교체할 수 있다.

**권장 구조**:
- `domain_layer/repository/<name>_repo.py` -- `class <Name>Repository(ABC)` 인터페이스
- `infra_layer/repository/<name>_repo.py` -- `class Django<Name>Repository(<Name>Repository)` 구현체

---

### MAJOR-4. 도메인 이벤트가 Django signals에 직접 의존

```
[Domain Events] -- events.py가 Django signals 기반이므로 도메인 이벤트가
프레임워크 메커니즘에 결합되어 있다.
```

도메인 이벤트 클래스는 프레임워크 무의존 순수 Python 클래스여야 한다. Django signals는 이벤트의 전달 메커니즘(인프라 관심사)이므로 `infra_layer/event_bus/signal_event_bus.py`에 위치해야 한다. 도메인 이벤트 클래스 자체는 `domain_layer/event/<name>_events.py`에 `@dataclass(frozen=True)`로 정의하고, 과거형으로 명명한다 (예: `OrderPlacedEvent`, `StockDepletedEvent`).

---

### MINOR-1. shared_kernel에 utils.py만 존재

```
[Shared Kernel] -- shared_kernel/utils.py는 DDD의 Shared Kernel 패턴에 부합하지 않는다.
```

DDD의 Shared Kernel은 두 바운디드 컨텍스트가 공유하는 최소한의 도메인 모델이다. 권장 구조에 따르면 `shared_kernel/`에는 공통 값 객체(`value_object/`)와 공통 스키마(`schema/`)가 위치해야 하며, 도메인 로직은 포함하지 않는다. `utils.py`라는 이름은 도메인 의미가 없으므로, 실제 공유되는 개념(Money, DateRange 등)을 값 객체로 정의하여 `shared_kernel/value_object/`에 배치해야 한다.

---

### MINOR-2. 테스트 계층별 분리 없음

```
[Test Organization] -- tests.py 단일 파일은 도메인/응용/인프라/API 테스트를 구분하지 못한다.
```

권장 구조에서는 테스트를 계층별로 분리한다:
- `tests/domain/` -- 순수 도메인 로직 (외부 의존 없음, 가장 빠름)
- `tests/application/` -- 서비스 로직 (mock repo, 이벤트 핸들러)
- `tests/infra/` -- repository CRUD, 외부 서비스 연동
- `tests/api/` -- HTTP 요청/응답, 상태 코드, 인증

도메인 테스트가 데이터베이스 없이 실행 가능해야 DDD의 이점을 체감할 수 있다.

---

## Review Checklist

| 점검 항목 | 결과 | 관련 Finding |
|-----------|------|-------------|
| 바운디드 컨텍스트 경계가 명확한가 | FAIL | CRITICAL-1 |
| 애그리거트가 과도하게 크지 않은가 | UNCLEAR | MAJOR-2 |
| 애그리거트 간 ID 참조를 사용하는가 | FAIL | CRITICAL-1 (직접 import) |
| 빈혈 도메인 모델이 아닌가 | FAIL | MAJOR-1 |
| 값 객체로 모델링할 개념이 엔티티로 되어 있지 않은가 | UNCLEAR | (코드 미확인) |
| 크로스 애그리거트 통신이 도메인 이벤트를 사용하는가 | FAIL | CRITICAL-1, MAJOR-4 |
| 유비쿼터스 언어가 코드에 반영되어 있는가 | UNCLEAR | (코드 미확인) |
| 서브도메인 유형에 맞는 복잡도인가 | PASS | (inventory=Supporting, order=Core로 추정) |

---

## 권장 개선 구조

Section 14(DDD + Django 프로젝트 구조)에 따라 재구성하면 다음과 같다:

```
applications/
├── shared_kernel/
│   ├── value_object/
│   │   └── money.py                        # Money 값 객체 등
│   └── schema/
│       └── error_out.py
│
├── inventory/
│   ├── domain_layer/
│   │   ├── product/
│   │   │   └── product.py                  # Product 애그리거트 루트 (순수 dataclass)
│   │   ├── stock/
│   │   │   └── stock.py                    # Stock 애그리거트 루트
│   │   ├── repository/
│   │   │   ├── product_repo.py             # class ProductRepository(ABC)
│   │   │   └── stock_repo.py               # class StockRepository(ABC)
│   │   ├── event/
│   │   │   └── inventory_events.py         # StockDepletedEvent 등 (frozen dataclass)
│   │   └── service/
│   │       └── stock_allocation_service.py # 입고/출고 도메인 서비스
│   │
│   ├── application_layer/
│   │   ├── inventory_service.py            # 유스케이스 조율
│   │   └── event_handlers.py              # OrderPlacedEvent 구독 -> 재고 차감
│   │
│   ├── infra_layer/
│   │   ├── django_inventory/
│   │   │   ├── apps.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── product_model.py        # ORM 모델 (ProductModel)
│   │   │   │   └── stock_model.py          # ORM 모델 (StockModel)
│   │   │   └── admin.py
│   │   ├── repository/
│   │   │   ├── django_product_repo.py      # DjangoProductRepository
│   │   │   └── django_stock_repo.py        # DjangoStockRepository
│   │   └── event_bus/
│   │       └── signal_event_bus.py         # Django signals 변환
│   │
│   ├── presentation_layer/
│   │   ├── api/
│   │   │   └── inventory_api.py
│   │   └── schema/
│   │       └── inventory_schema.py
│   │
│   └── tests/
│       ├── domain/
│       ├── application/
│       ├── infra/
│       └── api/
│
└── order/
    ├── domain_layer/
    │   ├── order/
    │   │   ├── order.py                    # Order 애그리거트 루트 (place(), cancel() 등)
    │   │   └── order_line_item.py          # OrderLineItem 값 객체 (frozen)
    │   ├── repository/
    │   │   └── order_repo.py               # class OrderRepository(ABC)
    │   ├── event/
    │   │   └── order_events.py             # OrderPlacedEvent, OrderCancelledEvent
    │   └── service/
    │
    ├── application_layer/
    │   └── order_service.py                # 유스케이스 조율 (inventory 직접 접근 금지)
    │
    ├── infra_layer/
    │   ├── django_order/
    │   │   ├── apps.py
    │   │   ├── models/
    │   │   │   ├── __init__.py
    │   │   │   └── order_model.py          # ORM 모델 (OrderModel)
    │   │   └── admin.py
    │   ├── repository/
    │   │   └── django_order_repo.py        # DjangoOrderRepository
    │   └── event_bus/
    │       └── signal_event_bus.py
    │
    ├── presentation_layer/
    │   ├── api/
    │   │   └── order_api.py
    │   └── schema/
    │       └── order_schema.py
    │
    └── tests/
        ├── domain/
        ├── application/
        ├── infra/
        └── api/
```

이 구조에서 핵심은:
- `domain_layer/`는 Django import가 전혀 없는 순수 Python이다
- order가 inventory의 재고를 차감할 때, `OrderPlacedEvent`를 발행하고 inventory의 `event_handlers.py`가 구독한다
- ORM 모델(`*Model`)과 도메인 엔티티(`@dataclass`)가 물리적으로 분리되어 있다
- 리포지토리 구현체가 ORM 모델과 도메인 엔티티 간의 변환을 담당한다
