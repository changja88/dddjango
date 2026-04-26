# Django DDD Refactoring Plan

## 1. 변경 전 구조 (AS-IS)

```
myproject/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/
│   ├── models.py          # Product(models.Model), Category(models.Model)
│   ├── views.py           # ProductViewSet
│   ├── serializers.py     # ProductSerializer
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
└── orders/
    ├── models.py          # Order(models.Model), OrderItem(models.Model)
    ├── views.py           # OrderViewSet
    ├── serializers.py     # OrderSerializer
    ├── services.py        # create_order(), cancel_order() — Product.objects.get() 직접 호출
    ├── signals.py         # post_save로 재고 차감
    ├── urls.py
    ├── admin.py
    └── tests.py
```

### 현재 구조의 문제점

| 문제 | 설명 |
|------|------|
| 도메인 모델이 ORM에 직접 의존 | `Product(models.Model)` 등 도메인 로직과 영속성이 결합 |
| 서비스에서 타 바운디드 컨텍스트 직접 참조 | `orders/services.py`에서 `Product.objects.get()` 직접 호출 |
| 재고 차감이 Django signal로 처리 | 도메인 이벤트가 아닌 프레임워크 메커니즘에 의존 |
| 애그리거트 경계 불명확 | Order-OrderItem 관계가 ORM 레벨에서만 표현 |
| 레이어 구분 없음 | 도메인, 애플리케이션, 인프라, 프레젠테이션이 혼재 |

---

## 2. 변경 후 구조 (TO-BE)

```
myproject/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── shared_kernel/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entity.py              # Entity, AggregateRoot 베이스 클래스
│   │   ├── value_object.py        # ValueObject 베이스 클래스
│   │   └── domain_event.py        # DomainEvent 베이스 클래스, EventBus
│   └── infra/
│       ├── __init__.py
│       └── event_dispatcher.py    # 인메모리 이벤트 디스패처 구현
│
├── products/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities.py            # Product (순수 파이썬), Category (순수 파이썬)
│   │   ├── value_objects.py       # Money, SKU 등
│   │   ├── repositories.py        # ProductRepository(ABC), CategoryRepository(ABC)
│   │   ├── events.py              # StockDeducted, StockRestored
│   │   └── exceptions.py          # InsufficientStockError 등
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services.py            # ProductApplicationService
│   │   ├── dtos.py                # ProductDTO
│   │   └── event_handlers.py      # OrderCreated 이벤트 핸들러 (재고 차감)
│   ├── infra/
│   │   ├── __init__.py
│   │   ├── django_models.py       # ProductORM(models.Model), CategoryORM(models.Model)
│   │   ├── repositories.py        # DjangoProductRepository, DjangoCategoryRepository
│   │   ├── mappers.py             # ORM <-> 도메인 엔티티 매핑
│   │   └── admin.py
│   ├── presentation/
│   │   ├── __init__.py
│   │   ├── views.py               # ProductViewSet
│   │   ├── serializers.py         # ProductSerializer
│   │   └── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_domain.py
│       ├── test_application.py
│       └── test_infra.py
│
└── orders/
    ├── __init__.py
    ├── domain/
    │   ├── __init__.py
    │   ├── entities.py            # Order (AggregateRoot, 순수 파이썬), OrderItem (Entity)
    │   ├── value_objects.py       # OrderStatus, Address 등
    │   ├── repositories.py        # OrderRepository(ABC)
    │   ├── events.py              # OrderCreated, OrderCancelled
    │   ├── exceptions.py          # InvalidOrderStateError 등
    │   └── services.py            # OrderDomainService (도메인 서비스)
    ├── application/
    │   ├── __init__.py
    │   ├── services.py            # OrderApplicationService (create_order, cancel_order)
    │   ├── dtos.py                # CreateOrderDTO, OrderResponseDTO
    │   └── commands.py            # CreateOrderCommand, CancelOrderCommand
    ├── infra/
    │   ├── __init__.py
    │   ├── django_models.py       # OrderORM(models.Model), OrderItemORM(models.Model)
    │   ├── repositories.py        # DjangoOrderRepository
    │   ├── mappers.py             # ORM <-> 도메인 엔티티 매핑
    │   └── admin.py
    ├── presentation/
    │   ├── __init__.py
    │   ├── views.py               # OrderViewSet
    │   ├── serializers.py         # OrderSerializer
    │   └── urls.py
    └── tests/
        ├── __init__.py
        ├── test_domain.py
        ├── test_application.py
        └── test_infra.py
```

---

## 3. 파일 이동 매핑

### 3.1 products 바운디드 컨텍스트

| AS-IS | TO-BE | 변경 내용 |
|-------|-------|-----------|
| `products/models.py` (Product) | `products/domain/entities.py` | ORM 의존 제거, 순수 파이썬 도메인 엔티티로 재작성 |
| `products/models.py` (Category) | `products/domain/entities.py` | ORM 의존 제거, 순수 파이썬 도메인 엔티티로 재작성 |
| `products/models.py` (ORM 정의) | `products/infra/django_models.py` | ORM 모델은 인프라 계층의 영속성 모델로 분리 |
| `products/views.py` | `products/presentation/views.py` | 이동 (Application Service를 주입받도록 수정) |
| `products/serializers.py` | `products/presentation/serializers.py` | 이동 |
| `products/urls.py` | `products/presentation/urls.py` | 이동 |
| `products/admin.py` | `products/infra/admin.py` | 이동 |
| `products/tests.py` | `products/tests/test_domain.py` | 분할 (도메인/애플리케이션/인프라 테스트 분리) |
| `products/tests.py` | `products/tests/test_application.py` | 분할 |
| `products/tests.py` | `products/tests/test_infra.py` | 분할 |
| (신규) | `products/domain/value_objects.py` | Money, SKU 등 값 객체 신규 작성 |
| (신규) | `products/domain/repositories.py` | 리포지토리 인터페이스(ABC) 신규 작성 |
| (신규) | `products/domain/events.py` | StockDeducted 등 도메인 이벤트 신규 작성 |
| (신규) | `products/domain/exceptions.py` | 도메인 예외 신규 작성 |
| (신규) | `products/application/services.py` | 애플리케이션 서비스 신규 작성 |
| (신규) | `products/application/dtos.py` | DTO 신규 작성 |
| (신규) | `products/application/event_handlers.py` | OrderCreated 이벤트 핸들러 (재고 차감 로직) |
| (신규) | `products/infra/repositories.py` | 리포지토리 구현체 신규 작성 |
| (신규) | `products/infra/mappers.py` | ORM-도메인 매퍼 신규 작성 |

### 3.2 orders 바운디드 컨텍스트

| AS-IS | TO-BE | 변경 내용 |
|-------|-------|-----------|
| `orders/models.py` (Order) | `orders/domain/entities.py` | ORM 의존 제거, AggregateRoot 상속, 순수 파이썬으로 재작성 |
| `orders/models.py` (OrderItem) | `orders/domain/entities.py` | ORM 의존 제거, Entity 상속, Order 애그리거트의 구성원 |
| `orders/models.py` (ORM 정의) | `orders/infra/django_models.py` | ORM 모델은 인프라 계층의 영속성 모델로 분리 |
| `orders/services.py` | `orders/application/services.py` | Product.objects.get() 직접 호출 제거, 도메인 이벤트 발행 방식으로 전환 |
| `orders/signals.py` | **삭제** | Django signal 제거, 도메인 이벤트(OrderCreated)로 대체 |
| `orders/views.py` | `orders/presentation/views.py` | 이동 (Application Service를 주입받도록 수정) |
| `orders/serializers.py` | `orders/presentation/serializers.py` | 이동 |
| `orders/urls.py` | `orders/presentation/urls.py` | 이동 |
| `orders/admin.py` | `orders/infra/admin.py` | 이동 |
| `orders/tests.py` | `orders/tests/test_domain.py` | 분할 (도메인/애플리케이션/인프라 테스트 분리) |
| `orders/tests.py` | `orders/tests/test_application.py` | 분할 |
| `orders/tests.py` | `orders/tests/test_infra.py` | 분할 |
| (신규) | `orders/domain/value_objects.py` | OrderStatus, Address 등 값 객체 신규 작성 |
| (신규) | `orders/domain/repositories.py` | 리포지토리 인터페이스(ABC) 신규 작성 |
| (신규) | `orders/domain/events.py` | OrderCreated, OrderCancelled 도메인 이벤트 신규 작성 |
| (신규) | `orders/domain/exceptions.py` | 도메인 예외 신규 작성 |
| (신규) | `orders/domain/services.py` | 도메인 서비스 (도메인 규칙 검증) 신규 작성 |
| (신규) | `orders/application/dtos.py` | DTO 신규 작성 |
| (신규) | `orders/application/commands.py` | 커맨드 객체 신규 작성 |
| (신규) | `orders/infra/repositories.py` | 리포지토리 구현체 신규 작성 |
| (신규) | `orders/infra/mappers.py` | ORM-도메인 매퍼 신규 작성 |

### 3.3 shared_kernel (신규)

| AS-IS | TO-BE | 변경 내용 |
|-------|-------|-----------|
| (신규) | `shared_kernel/domain/entity.py` | Entity, AggregateRoot 베이스 클래스 |
| (신규) | `shared_kernel/domain/value_object.py` | ValueObject 베이스 클래스 |
| (신규) | `shared_kernel/domain/domain_event.py` | DomainEvent 베이스 클래스, EventBus 인터페이스 |
| (신규) | `shared_kernel/infra/event_dispatcher.py` | 인메모리 이벤트 디스패처 구현 |

### 3.4 config (변경 없음)

| AS-IS | TO-BE | 변경 내용 |
|-------|-------|-----------|
| `config/settings.py` | `config/settings.py` | 유지 (INSTALLED_APPS 경로 업데이트 필요) |
| `config/urls.py` | `config/urls.py` | 유지 (include 경로 업데이트 필요) |
| `config/wsgi.py` | `config/wsgi.py` | 유지 |

---

## 4. 핵심 설계 결정

### 4.1 애그리거트 경계

```
[Product 애그리거트]          [Order 애그리거트]
┌──────────────────┐        ┌──────────────────────┐
│ Product (Root)   │        │ Order (Root)          │
│   - name         │        │   - status            │
│   - price        │        │   - total_amount      │
│   - stock        │        │   - ordered_at        │
│   - deduct()     │        │   - add_item()        │
│   - restore()    │        │   - cancel()          │
└──────────────────┘        │   - domain_events[]   │
                            │                      │
[Category 애그리거트]        │ OrderItem (Entity)    │
┌──────────────────┐        │   - product_id (ID)   │
│ Category (Root)  │        │   - quantity           │
│   - name         │        │   - unit_price         │
└──────────────────┘        └──────────────────────┘
```

- **Order 애그리거트**: Order가 Root, OrderItem은 Order 내부 Entity. 외부에서 OrderItem을 직접 조회/수정 불가.
- **Product 애그리거트**: Product가 Root. 재고(stock)는 Product가 직접 관리.
- **Category 애그리거트**: 별도 Root. Product는 category_id(ID 참조)만 보유.
- **컨텍스트 간 참조**: OrderItem은 `product_id`(ID 값)만 보유하며, Product 엔티티를 직접 참조하지 않음.

### 4.2 도메인 이벤트를 통한 재고 차감 흐름

기존의 Django signal(`post_save`) 방식을 제거하고, 도메인 이벤트 기반으로 전환한다.

```
주문 생성 흐름:

1. Client -> OrderViewSet.create()
2. OrderViewSet -> OrderApplicationService.create_order(command)
3. OrderApplicationService:
   a. Order.create(items) 호출 -> Order 애그리거트 생성
   b. Order 내부에서 OrderCreated 도메인 이벤트 등록
   c. OrderRepository.save(order) -> DB 저장
   d. EventBus.publish(order.domain_events) -> 이벤트 발행
4. EventBus -> ProductEventHandler.handle_order_created(event)
5. ProductEventHandler:
   a. ProductRepository.get(product_id) -> Product 도메인 엔티티 조회
   b. Product.deduct_stock(quantity) 호출
   c. ProductRepository.save(product) -> DB 저장
```

```
주문 취소 흐름:

1. Client -> OrderViewSet.cancel()
2. OrderViewSet -> OrderApplicationService.cancel_order(command)
3. OrderApplicationService:
   a. OrderRepository.get(order_id) -> Order 조회
   b. Order.cancel() 호출 -> OrderCancelled 이벤트 등록
   c. OrderRepository.save(order)
   d. EventBus.publish(order.domain_events)
4. EventBus -> ProductEventHandler.handle_order_cancelled(event)
5. ProductEventHandler:
   a. 각 item에 대해 Product.restore_stock(quantity) 호출
```

### 4.3 도메인 모델의 ORM 독립성

도메인 엔티티는 `django.db.models.Model`을 상속하지 않는 순수 파이썬 클래스로 작성한다.

```python
# orders/domain/entities.py (TO-BE)
class Order:
    """순수 파이썬 도메인 엔티티 - Django ORM에 의존하지 않음"""

    def __init__(self, id, items, status, ordered_at):
        self.id = id
        self._items = list(items)
        self._status = status
        self._ordered_at = ordered_at
        self._domain_events = []

    def add_item(self, product_id, quantity, unit_price):
        item = OrderItem(product_id=product_id, quantity=quantity, unit_price=unit_price)
        self._items.append(item)

    def cancel(self):
        if self._status != OrderStatus.CONFIRMED:
            raise InvalidOrderStateError("Only confirmed orders can be cancelled")
        self._status = OrderStatus.CANCELLED
        self._domain_events.append(
            OrderCancelled(order_id=self.id, items=self._items)
        )

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self._items)

    def collect_events(self):
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
```

영속성은 인프라 계층의 매퍼가 담당한다.

```python
# orders/infra/mappers.py
class OrderMapper:
    @staticmethod
    def to_domain(orm_model: OrderORM) -> Order:
        items = [OrderItemMapper.to_domain(item) for item in orm_model.items.all()]
        return Order(
            id=orm_model.id,
            items=items,
            status=OrderStatus(orm_model.status),
            ordered_at=orm_model.ordered_at,
        )

    @staticmethod
    def to_orm(domain_entity: Order) -> OrderORM:
        # 도메인 엔티티 -> ORM 모델 변환
        ...
```

### 4.4 바운디드 컨텍스트 간 통신

orders 컨텍스트에서 products 컨텍스트를 직접 호출하지 않는다. 도메인 이벤트를 통해 간접적으로 통신한다.

```python
# AS-IS: orders/services.py (직접 참조 - 위반)
from products.models import Product

def create_order(data):
    product = Product.objects.get(id=data['product_id'])  # 직접 호출
    product.stock -= data['quantity']                      # 직접 수정
    product.save()

# TO-BE: orders/application/services.py (이벤트 기반 - 분리)
class OrderApplicationService:
    def __init__(self, order_repo, event_bus):
        self._order_repo = order_repo
        self._event_bus = event_bus

    def create_order(self, command):
        order = Order.create(items=command.items)  # Product 참조 없음
        self._order_repo.save(order)
        self._event_bus.publish(order.collect_events())  # OrderCreated 이벤트 발행
```

---

## 5. config 변경 사항

### settings.py

```python
INSTALLED_APPS = [
    # ...
    'products.infra',   # django_models.py가 있는 위치 (AppConfig에서 label 지정)
    'orders.infra',     # django_models.py가 있는 위치
]
```

또는 각 바운디드 컨텍스트 루트에 `AppConfig`를 두고 `default_auto_field`와 `label`을 설정한다.

```python
# products/__init__.py
default_app_config = 'products.apps.ProductsConfig'

# products/apps.py
from django.apps import AppConfig

class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    label = 'products'

    def ready(self):
        from products.application.event_handlers import register_handlers
        register_handlers()
```

### urls.py

```python
# config/urls.py
urlpatterns = [
    path('api/products/', include('products.presentation.urls')),
    path('api/orders/', include('orders.presentation.urls')),
]
```

---

## 6. 리팩토링 실행 순서

| 단계 | 작업 | 이유 |
|------|------|------|
| 1 | `shared_kernel` 생성 | 베이스 클래스가 다른 모든 도메인 엔티티의 기반 |
| 2 | `products/domain` 작성 | Order가 Product에 의존(ID 참조)하므로 먼저 정의 |
| 3 | `products/infra` 작성 | ORM 모델 분리 및 리포지토리 구현 |
| 4 | `orders/domain` 작성 | 도메인 엔티티 + 이벤트 정의 |
| 5 | `orders/infra` 작성 | ORM 모델 분리 및 리포지토리 구현 |
| 6 | `orders/application` 작성 | 기존 services.py를 애플리케이션 서비스로 재작성, 이벤트 발행 추가 |
| 7 | `products/application` 작성 | 이벤트 핸들러(재고 차감) 구현 |
| 8 | `presentation` 계층 이동 | views, serializers, urls 이동 |
| 9 | `orders/signals.py` 삭제 | 도메인 이벤트로 대체 완료 후 제거 |
| 10 | config 업데이트 및 테스트 | settings.py, urls.py 경로 수정, 전체 테스트 실행 |
