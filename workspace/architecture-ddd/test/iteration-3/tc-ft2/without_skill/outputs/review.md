# Django DDD 프로젝트 구조 리뷰

## 현재 구조 요약

```
applications/
├── shared_kernel/
│   └── utils.py
├── inventory/
│   ├── models.py, services.py, repositories.py
│   ├── serializers.py, views.py, urls.py
│   ├── signals.py, admin.py, tests.py
└── order/
    ├── models.py, services.py, repositories.py
    ├── serializers.py, views.py, urls.py
    ├── events.py, admin.py, tests.py
```

---

## 문제 분석

### 문제 1. Bounded Context 간 직접 의존 (order -> inventory)

`order/services.py`에서 `inventory.models.Stock`을 직접 import하여 재고를 차감하고 있다.

**왜 문제인가:**

- DDD에서 Bounded Context는 독립적인 경계를 가져야 한다. order 컨텍스트가 inventory의 내부 모델을 직접 참조하면 두 컨텍스트가 강하게 결합된다.
- inventory의 Stock 모델 필드명이 바뀌거나, 재고 차감 정책이 변경되면 order 쪽 코드도 함께 수정해야 한다.
- 이 구조에서는 order를 독립적으로 테스트할 수 없다. 반드시 inventory의 실제 모델과 DB 테이블이 필요하다.
- 재고 차감이라는 inventory 도메인의 핵심 비즈니스 로직이 order 서비스 안에 흩어져 관리된다.

**개선 방향:**

(A) Anti-Corruption Layer + Domain Event 패턴 적용:

```python
# order/services.py -- 개선 후
class OrderService:
    def __init__(self, inventory_gateway: InventoryGateway):
        self._inventory = inventory_gateway

    def create_order(self, order_data):
        # inventory 내부 모델을 모르고, 인터페이스만 사용
        if not self._inventory.check_availability(sku, quantity):
            raise InsufficientStockError()
        order = Order.create(order_data)
        # 재고 차감은 이벤트로 위임
        order.add_event(OrderCreated(order_id=order.id, items=order.items))
        return order
```

```python
# order/acl.py (Anti-Corruption Layer)
from abc import ABC, abstractmethod

class InventoryGateway(ABC):
    @abstractmethod
    def check_availability(self, sku: str, quantity: int) -> bool: ...

    @abstractmethod
    def reserve_stock(self, sku: str, quantity: int) -> None: ...
```

```python
# inventory/acl_adapters.py
class DjangoInventoryGateway(InventoryGateway):
    def check_availability(self, sku, quantity):
        stock = Stock.objects.get(sku=sku)
        return stock.available >= quantity
```

(B) 또는 최소한 inventory 쪽에 public API(서비스 함수)를 두고, order에서는 그 API만 호출하도록 한다:

```python
# order/services.py
from inventory.services import InventoryService  # 모델이 아닌 서비스 계층만 참조

class OrderService:
    def create_order(self, order_data):
        InventoryService.deduct_stock(sku, quantity)  # 내부 구현은 모름
```

이 방식은 완전한 DDD가 아니지만, 현실적인 첫 단계로 적합하다.

---

### 문제 2. 도메인 모델이 Django ORM에 직접 의존

`models.py`의 모든 도메인 모델이 `django.db.models.Model`을 상속하고 있다. 즉 도메인 모델 = ORM 모델이다.

**왜 문제인가:**

- 도메인 모델에 비즈니스 규칙을 넣으려 해도, Django Model의 `save()`, `clean()`, `Meta` 등 ORM 관심사와 섞인다.
- 도메인 로직을 테스트하려면 반드시 DB가 필요하다. 순수한 단위 테스트가 불가능하다.
- 도메인 모델이 프레임워크에 종속되어, Django를 벗어난 컨텍스트(배치 처리, 메시지 컨슈머 등)에서 재사용이 어렵다.
- Value Object, Entity, Aggregate Root 같은 DDD 빌딩 블록을 명확하게 표현하기 어렵다.

**개선 방향:**

도메인 모델과 ORM 모델을 분리한다:

```python
# inventory/domain/models.py -- 순수 도메인 모델
from dataclasses import dataclass

@dataclass
class Stock:
    sku: str
    quantity: int
    warehouse_id: str

    def deduct(self, amount: int) -> None:
        if amount > self.quantity:
            raise InsufficientStockError(self.sku, self.quantity, amount)
        self.quantity -= amount

    def replenish(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Replenish amount must be positive")
        self.quantity += amount

    def is_low_stock(self, threshold: int = 10) -> bool:
        return self.quantity <= threshold
```

```python
# inventory/infra/orm_models.py -- Django ORM 모델 (persistence 전용)
from django.db import models

class StockORM(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    warehouse = models.ForeignKey(WarehouseORM, on_delete=models.CASCADE)

    class Meta:
        db_table = "inventory_stock"
```

```python
# inventory/infra/repositories.py -- 매핑 담당
class DjangoStockRepository(StockRepository):
    def find_by_sku(self, sku: str) -> Stock:
        orm_obj = StockORM.objects.get(sku=sku)
        return Stock(sku=orm_obj.sku, quantity=orm_obj.quantity, ...)

    def save(self, stock: Stock) -> None:
        StockORM.objects.update_or_create(
            sku=stock.sku,
            defaults={"quantity": stock.quantity, ...}
        )
```

**현실적 타협안:**

완전 분리가 부담스러우면, Django Model을 유지하되 비즈니스 로직을 메서드로 집중시키고, ORM 쿼리 로직은 Repository/Manager로 분리하는 것도 유효하다. 다만 이 경우에도 "도메인 모델이 Django에 의존한다"는 한계는 남는다.

---

### 문제 3. 계층 분리 부재 (domain/application/infrastructure 혼재)

한 Django 앱 폴더 안에 도메인 로직(`models.py`, `services.py`), 인프라(`repositories.py`, `signals.py`), 표현 계층(`views.py`, `serializers.py`, `urls.py`)이 모두 섞여 있다.

**왜 문제인가:**

- 어떤 코드가 비즈니스 규칙이고, 어떤 코드가 기술적 구현인지 파일 구조만으로 구분할 수 없다.
- `services.py` 안에서 Django ORM 쿼리를 직접 수행하면, 서비스 로직이 인프라에 의존하는 것인지 도메인 로직인지 모호해진다.
- 새로운 개발자가 코드를 읽을 때, 의존성 방향을 파악하기 어렵다.
- 계층별 테스트 전략을 세우기 어렵다 (도메인 단위 테스트 vs 통합 테스트 구분 불가).

**개선 방향:**

각 Bounded Context를 계층별로 하위 패키지로 분리한다:

```
applications/
├── shared_kernel/
│   ├── domain/
│   │   └── value_objects.py        # 공통 Value Object (Money, Quantity 등)
│   └── utils.py
│
├── inventory/
│   ├── domain/
│   │   ├── models.py               # Entity, Aggregate Root (순수 Python)
│   │   ├── value_objects.py         # SKU, Quantity 등
│   │   ├── events.py               # 도메인 이벤트 정의
│   │   ├── repositories.py         # Repository 인터페이스 (ABC)
│   │   └── exceptions.py           # 도메인 예외
│   │
│   ├── application/
│   │   ├── services.py             # 유스케이스 오케스트레이션
│   │   ├── commands.py             # Command 객체 (입고, 출고)
│   │   ├── queries.py              # Query 객체 (재고 조회)
│   │   └── event_handlers.py       # 도메인 이벤트 핸들러
│   │
│   ├── infra/
│   │   ├── orm_models.py           # Django ORM 모델
│   │   ├── repositories.py         # Repository 구현체
│   │   ├── signals.py              # Django signal 연결
│   │   └── admin.py
│   │
│   ├── presentation/
│   │   ├── serializers.py          # DRF Serializer
│   │   ├── views.py                # DRF ViewSet/APIView
│   │   └── urls.py
│   │
│   └── tests/
│       ├── test_domain.py          # 순수 단위 테스트 (DB 불필요)
│       ├── test_application.py     # 서비스 계층 테스트
│       └── test_integration.py     # API 통합 테스트
│
└── order/
    ├── domain/
    │   ├── models.py               # Order (Aggregate Root), OrderItem (Entity)
    │   ├── value_objects.py         # OrderStatus, OrderNumber 등
    │   ├── events.py               # OrderCreated, OrderCancelled 등
    │   ├── repositories.py         # Repository 인터페이스
    │   └── exceptions.py
    │
    ├── application/
    │   ├── services.py             # 주문 생성 유스케이스
    │   └── event_handlers.py       # inventory 이벤트 구독
    │
    ├── acl/
    │   └── inventory_gateway.py    # inventory 컨텍스트 접근 인터페이스
    │
    ├── infra/
    │   ├── orm_models.py
    │   ├── repositories.py
    │   ├── inventory_adapter.py    # InventoryGateway 구현체
    │   └── admin.py
    │
    ├── presentation/
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    │
    └── tests/
        ├── test_domain.py
        ├── test_application.py
        └── test_integration.py
```

**핵심 의존성 규칙:**

```
presentation -> application -> domain
                    |
               infra (구현체)
```

- `domain` 패키지는 외부 의존성이 없다 (순수 Python).
- `application`은 `domain`의 인터페이스에만 의존한다.
- `infra`는 `domain`의 인터페이스를 구현하고, Django ORM 등 기술적 세부사항을 담당한다.
- `presentation`은 `application` 서비스를 호출한다.
- 의존성은 항상 바깥에서 안쪽으로만 향한다 (Dependency Inversion).

---

## 종합 평가

| 항목 | 현재 상태 | 심각도 |
|------|----------|--------|
| BC 간 직접 참조 | order가 inventory.models를 직접 import | 높음 |
| 도메인-ORM 결합 | models.Model 직접 상속, 분리 없음 | 중간 |
| 계층 혼재 | domain/app/infra/presentation이 한 폴더 | 중간 |

**우선순위 권장:**

1. **BC 간 의존성 정리** (가장 시급) -- 컨텍스트 간 결합은 시스템이 커질수록 변경 비용이 급격히 증가한다. Anti-Corruption Layer 또는 최소한 서비스 계층 간 호출로 전환한다.
2. **계층 분리** -- 폴더 구조를 domain/application/infra/presentation으로 나누면 의존성 방향이 명시적이 되어, 코드 리뷰와 신규 개발자 온보딩이 수월해진다.
3. **도메인 모델 분리** -- 비용이 가장 크다. 기존 Django 앱에서 ORM 모델과 도메인 모델을 분리하면 매핑 코드가 필요하고, Django Admin 등과의 통합도 재설계해야 한다. 프로젝트 규모와 복잡도에 따라 판단한다.
