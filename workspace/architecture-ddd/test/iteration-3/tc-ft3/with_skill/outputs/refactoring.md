# Django 프로젝트 DDD 폴더 구조 리팩토링

## 1. 전략 설계: 바운디드 컨텍스트 정의

리팩토링에 앞서 전략 설계를 수행한다. 전술 패턴보다 전략 설계가 먼저다.

| 바운디드 컨텍스트 | 애그리거트 | 서브도메인 유형 |
|---|---|---|
| **catalog** (상품 카탈로그) | Product, Category | Core |
| **ordering** (주문) | Order (루트) + OrderItem (내부 엔티티) | Core |

- "Product"는 카탈로그 컨텍스트에서 상품 정보(이름, 가격, 카테고리)를 의미하고, 주문 컨텍스트에서는 `product_id`로만 참조한다.
- Order와 OrderItem은 하나의 애그리거트다. OrderItem은 Order 없이 존재할 수 없으며, 주문 금액 계산이라는 불변식을 함께 보호해야 한다.
- Product와 Category는 각각 별도 애그리거트다. Category는 Product에서 ID로만 참조한다.

### 컨텍스트 맵

```
[catalog] ──(도메인 이벤트)──> [ordering]
                                  │
                                  └── OrderPlacedEvent
                                        │
                              (이벤트 구독) ──> [catalog] 재고 차감
```

- ordering -> catalog: 주문 생성 시 상품 정보 조회는 application_layer에서 catalog의 application_layer 서비스를 호출한다.
- catalog -> ordering: 직접 의존 없음. OrderPlacedEvent를 catalog가 구독하여 재고를 차감한다 (결과적 일관성).

---

## 2. 변경 전 파일 트리

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

---

## 3. 변경 후 파일 트리

```
myproject/
├── manage.py
├── config/
│   ├── settings.py        # INSTALLED_APPS에 django_catalog, django_ordering 등록
│   ├── urls.py
│   └── wsgi.py
│
├── applications/
│   ├── shared_kernel/
│   │   └── value_object/
│   │       └── money.py                    # Money 값 객체 (frozen=True)
│   │
│   ├── catalog/                            # Bounded Context: 상품 카탈로그
│   │   ├── domain_layer/
│   │   │   ├── product/                    # Product 애그리거트
│   │   │   │   ├── product.py              # Product 엔티티 (애그리거트 루트, 순수 Python)
│   │   │   │   └── product_status.py       # ProductStatus 값 객체
│   │   │   ├── category/                   # Category 애그리거트
│   │   │   │   └── category.py             # Category 엔티티 (애그리거트 루트, 순수 Python)
│   │   │   ├── repository/
│   │   │   │   ├── product_repo.py         # ProductRepository(ABC)
│   │   │   │   └── category_repo.py        # CategoryRepository(ABC)
│   │   │   └── event/
│   │   │       └── catalog_events.py       # StockDecreasedEvent 등
│   │   │
│   │   ├── application_layer/
│   │   │   ├── catalog_service.py          # 상품 조회/등록 유스케이스 조율
│   │   │   └── event_handlers.py           # OrderPlacedEvent 구독 -> 재고 차감
│   │   │
│   │   ├── infra_layer/
│   │   │   ├── django_catalog/             # Django 앱
│   │   │   │   ├── apps.py
│   │   │   │   ├── models/
│   │   │   │   │   ├── __init__.py         # ProductModel, CategoryModel re-export
│   │   │   │   │   ├── product_model.py    # ProductModel(models.Model)
│   │   │   │   │   └── category_model.py   # CategoryModel(models.Model)
│   │   │   │   └── admin.py
│   │   │   ├── repository/
│   │   │   │   ├── product_repo.py         # DjangoProductRepository(ProductRepository)
│   │   │   │   └── category_repo.py        # DjangoCategoryRepository(CategoryRepository)
│   │   │   └── event_bus/
│   │   │       └── signal_event_bus.py     # Django signals 기반 이벤트 디스패치
│   │   │
│   │   ├── presentation_layer/
│   │   │   ├── routers.py                  # URL 라우터 등록
│   │   │   ├── api/
│   │   │   │   └── product_api.py          # ProductViewSet
│   │   │   └── schema/
│   │   │       └── product_schema.py       # ProductSerializer (요청/응답 스키마)
│   │   │
│   │   └── tests/
│   │       ├── conftest.py
│   │       ├── domain/                     # 순수 도메인 로직 테스트
│   │       ├── application/                # 서비스 로직 테스트
│   │       ├── infra/                      # 리포지토리 CRUD 테스트
│   │       └── api/                        # HTTP 요청/응답 테스트
│   │
│   └── ordering/                           # Bounded Context: 주문
│       ├── domain_layer/
│       │   ├── order/                      # Order 애그리거트
│       │   │   ├── order.py                # Order 엔티티 (애그리거트 루트, 순수 Python)
│       │   │   ├── order_item.py           # OrderItem 엔티티 (Order 내부 엔티티)
│       │   │   └── order_status.py         # OrderStatus 값 객체 (Enum)
│       │   ├── value_object/
│       │   │   └── shipping_info.py        # ShippingInfo 값 객체 (frozen=True)
│       │   ├── repository/
│       │   │   └── order_repo.py           # OrderRepository(ABC)
│       │   └── event/
│       │       └── order_events.py         # OrderPlacedEvent, OrderCancelledEvent
│       │
│       ├── application_layer/
│       │   └── order_service.py            # 주문 생성/취소 유스케이스 조율
│       │
│       ├── infra_layer/
│       │   ├── django_ordering/            # Django 앱
│       │   │   ├── apps.py
│       │   │   ├── models/
│       │   │   │   ├── __init__.py         # OrderModel, OrderItemModel re-export
│       │   │   │   ├── order_model.py      # OrderModel(models.Model)
│       │   │   │   └── order_item_model.py # OrderItemModel(models.Model)
│       │   │   └── admin.py
│       │   ├── repository/
│       │   │   └── order_repo.py           # DjangoOrderRepository(OrderRepository)
│       │   └── event_bus/
│       │       └── signal_event_bus.py     # Django signals 기반 이벤트 디스패치
│       │
│       ├── presentation_layer/
│       │   ├── routers.py                  # URL 라우터 등록
│       │   ├── api/
│       │   │   └── order_api.py            # OrderViewSet
│       │   └── schema/
│       │       └── order_schema.py         # OrderSerializer (요청/응답 스키마)
│       │
│       └── tests/
│           ├── conftest.py
│           ├── domain/
│           ├── application/
│           ├── infra/
│           └── api/
```

---

## 4. 파일 이동 매핑

### 4.1 products/ 앱 해체

| 변경 전 | 변경 후 | 비고 |
|---|---|---|
| `products/models.py` (Product) | `applications/catalog/infra_layer/django_catalog/models/product_model.py` | ORM 모델은 infra로 이동. 비즈니스 로직은 `domain_layer/product/product.py`로 분리 |
| `products/models.py` (Category) | `applications/catalog/infra_layer/django_catalog/models/category_model.py` | ORM 모델은 infra로 이동. 도메인 모델은 `domain_layer/category/category.py`로 분리 |
| `products/views.py` | `applications/catalog/presentation_layer/api/product_api.py` | ViewSet은 presentation_layer로 이동 |
| `products/serializers.py` | `applications/catalog/presentation_layer/schema/product_schema.py` | Serializer는 스키마로 이동 |
| `products/urls.py` | `applications/catalog/presentation_layer/routers.py` | URL 설정은 라우터로 이동 |
| `products/admin.py` | `applications/catalog/infra_layer/django_catalog/admin.py` | Django 자동 탐색이 필요하므로 Django 앱 안에 유지 |
| `products/tests.py` | `applications/catalog/tests/` 하위 분리 | 도메인/application/infra/api 4계층으로 분리 |

### 4.2 orders/ 앱 해체

| 변경 전 | 변경 후 | 비고 |
|---|---|---|
| `orders/models.py` (Order) | `applications/ordering/infra_layer/django_ordering/models/order_model.py` | ORM 모델은 infra로 이동. 비즈니스 로직은 `domain_layer/order/order.py`로 분리 |
| `orders/models.py` (OrderItem) | `applications/ordering/infra_layer/django_ordering/models/order_item_model.py` | ORM 모델은 infra로 이동. 도메인 모델은 `domain_layer/order/order_item.py`로 분리 |
| `orders/views.py` | `applications/ordering/presentation_layer/api/order_api.py` | ViewSet은 presentation_layer로 이동 |
| `orders/serializers.py` | `applications/ordering/presentation_layer/schema/order_schema.py` | Serializer는 스키마로 이동 |
| `orders/services.py` | `applications/ordering/application_layer/order_service.py` | 비즈니스 로직은 도메인 모델로 이동, 조율 로직만 application_layer에 잔류 |
| `orders/signals.py` | **삭제** | Django signals 기반 재고 차감은 도메인 이벤트로 대체 |
| `orders/urls.py` | `applications/ordering/presentation_layer/routers.py` | URL 설정은 라우터로 이동 |
| `orders/admin.py` | `applications/ordering/infra_layer/django_ordering/admin.py` | Django 자동 탐색이 필요하므로 Django 앱 안에 유지 |
| `orders/tests.py` | `applications/ordering/tests/` 하위 분리 | 도메인/application/infra/api 4계층으로 분리 |

### 4.3 신규 파일

| 파일 | 용도 |
|---|---|
| `applications/shared_kernel/value_object/money.py` | 공통 Money 값 객체 |
| `applications/catalog/domain_layer/product/product.py` | Product 도메인 모델 (순수 Python, ORM 무의존) |
| `applications/catalog/domain_layer/category/category.py` | Category 도메인 모델 (순수 Python, ORM 무의존) |
| `applications/catalog/domain_layer/repository/product_repo.py` | ProductRepository 인터페이스 (ABC) |
| `applications/catalog/domain_layer/repository/category_repo.py` | CategoryRepository 인터페이스 (ABC) |
| `applications/catalog/domain_layer/event/catalog_events.py` | StockDecreasedEvent 등 |
| `applications/catalog/application_layer/catalog_service.py` | 상품 조회/등록 유스케이스 |
| `applications/catalog/application_layer/event_handlers.py` | OrderPlacedEvent 구독 핸들러 |
| `applications/catalog/infra_layer/repository/product_repo.py` | DjangoProductRepository 구현체 |
| `applications/catalog/infra_layer/repository/category_repo.py` | DjangoCategoryRepository 구현체 |
| `applications/catalog/infra_layer/event_bus/signal_event_bus.py` | 이벤트 버스 구현 |
| `applications/ordering/domain_layer/order/order.py` | Order 도메인 모델 (애그리거트 루트, 순수 Python) |
| `applications/ordering/domain_layer/order/order_item.py` | OrderItem 도메인 모델 (내부 엔티티) |
| `applications/ordering/domain_layer/order/order_status.py` | OrderStatus Enum 값 객체 |
| `applications/ordering/domain_layer/value_object/shipping_info.py` | ShippingInfo 값 객체 |
| `applications/ordering/domain_layer/repository/order_repo.py` | OrderRepository 인터페이스 (ABC) |
| `applications/ordering/domain_layer/event/order_events.py` | OrderPlacedEvent, OrderCancelledEvent |
| `applications/ordering/application_layer/order_service.py` | 주문 생성/취소 유스케이스 |
| `applications/ordering/infra_layer/repository/order_repo.py` | DjangoOrderRepository 구현체 |
| `applications/ordering/infra_layer/event_bus/signal_event_bus.py` | 이벤트 버스 구현 |

---

## 5. 주요 리팩토링 상세

### 5.1 빈혈 도메인 모델 -> 풍부한 도메인 모델

[Before]
```python
# orders/models.py -- Django ORM에 종속된 빈혈 모델
class Order(models.Model):
    customer = models.ForeignKey(...)
    status = models.CharField(...)
    created_at = models.DateTimeField(...)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, ...)
    product = models.ForeignKey('products.Product', ...)  # 직접 참조
    quantity = models.IntegerField(...)
    price = models.DecimalField(...)

# orders/services.py -- 비즈니스 로직이 서비스에 집중
def create_order(customer_id, items):
    order = Order.objects.create(customer_id=customer_id, status='pending')
    for item in items:
        product = Product.objects.get(id=item['product_id'])  # 타 애그리거트 직접 호출
        OrderItem.objects.create(order=order, product=product, ...)
    return order

def cancel_order(order_id):
    order = Order.objects.get(id=order_id)
    order.status = 'cancelled'
    order.save()
```

[After]
```python
# applications/ordering/domain_layer/order/order.py -- 순수 Python 도메인 모델
from dataclasses import dataclass, field
from typing import List
from uuid import uuid4

from applications.ordering.domain_layer.order.order_item import OrderItem
from applications.ordering.domain_layer.order.order_status import OrderStatus
from applications.ordering.domain_layer.event.order_events import (
    OrderPlacedEvent,
    OrderCancelledEvent,
)


@dataclass
class Order:
    """주문 애그리거트 루트

    - OrderItem은 내부 엔티티로, Order를 통해서만 접근한다
    - 다른 애그리거트(Product)는 product_id로만 참조한다
    - 모든 상태 변경은 비즈니스 메서드를 통해 수행한다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    customer_id: str = ""
    _items: List[OrderItem] = field(default_factory=list)
    _status: OrderStatus = field(default=OrderStatus.PENDING)
    _events: List = field(default_factory=list)

    def __post_init__(self):
        if self._items:
            self._verify_at_least_one_item()

    def add_item(self, product_id: str, product_name: str, price: int, quantity: int) -> None:
        """주문 항목 추가 -- product_id로만 참조 (Vernon 규칙 3)"""
        item = OrderItem(
            product_id=product_id,
            product_name=product_name,
            price=price,
            quantity=quantity,
        )
        self._items.append(item)

    def place(self) -> None:
        """주문 확정 -- 불변식 검증 후 도메인 이벤트 발행"""
        self._verify_at_least_one_item()
        if self._status != OrderStatus.PENDING:
            raise ValueError("대기 상태에서만 주문을 확정할 수 있습니다")
        self._status = OrderStatus.CONFIRMED
        self._events.append(
            OrderPlacedEvent(
                order_id=self.id,
                customer_id=self.customer_id,
                items=[
                    {"product_id": item.product_id, "quantity": item.quantity}
                    for item in self._items
                ],
                total_amount=self.total_amount,
            )
        )

    def cancel(self) -> None:
        """주문 취소 -- 비즈니스 규칙이 엔티티 안에 위치"""
        if self._status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            raise ValueError(f"{self._status.value} 상태에서는 취소할 수 없습니다")
        self._status = OrderStatus.CANCELLED
        self._events.append(
            OrderCancelledEvent(
                order_id=self.id,
                items=[
                    {"product_id": item.product_id, "quantity": item.quantity}
                    for item in self._items
                ],
            )
        )

    @property
    def total_amount(self) -> int:
        return sum(item.subtotal for item in self._items)

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def items(self) -> List[OrderItem]:
        return list(self._items)

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events

    def _verify_at_least_one_item(self) -> None:
        if not self._items:
            raise ValueError("최소 한 개의 상품을 주문해야 합니다")
```

[Reason] **빈혈 도메인 모델 -> 풍부한 도메인 모델** -- `create_order()`, `cancel_order()` 등 서비스에 흩어져 있던 비즈니스 로직(`status` 전이 규칙, 항목 검증)을 Order 애그리거트 루트 안으로 이동했다. 엔티티가 자신의 불변식을 스스로 보호한다.

---

### 5.2 직접 객체 참조 -> ID 참조

[Before]
```python
# orders/models.py
class OrderItem(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)  # 직접 참조

# orders/services.py
def create_order(customer_id, items):
    product = Product.objects.get(id=item['product_id'])  # 타 애그리거트 ORM 직접 호출
```

[After]
```python
# applications/ordering/domain_layer/order/order_item.py
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderItem:
    """주문 항목 -- Order 애그리거트 내부 엔티티

    Product를 ID로만 참조한다 (Vernon 규칙 3).
    """
    product_id: str       # Product 애그리거트를 ID로만 참조
    product_name: str     # 주문 시점의 상품명 스냅샷
    price: int            # 주문 시점의 가격 스냅샷
    quantity: int

    @property
    def subtotal(self) -> int:
        return self.price * self.quantity
```

[Reason] **직접 참조 -> ID 참조 (Vernon 규칙 3)** -- `ForeignKey('products.Product')`로 타 애그리거트를 직접 참조하면 두 애그리거트가 강하게 결합되고, 로딩 시 불필요한 JOIN이 발생한다. `product_id: str`로 변경하여 결합도를 낮추고, 주문 시점의 상품명과 가격을 스냅샷으로 보관한다.

---

### 5.3 Django signals -> 도메인 이벤트

[Before]
```python
# orders/signals.py -- 인프라 관심사(signals)에 비즈니스 로직이 숨어있음
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Order)
def decrease_stock_on_order(sender, instance, created, **kwargs):
    if created:
        for item in instance.orderitem_set.all():
            product = item.product
            product.stock -= item.quantity
            product.save()
```

[After]
```python
# applications/ordering/domain_layer/event/order_events.py -- 도메인 이벤트 정의
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class OrderPlacedEvent:
    """주문 확정 이벤트 -- 과거형 명명"""
    order_id: str = ""
    customer_id: str = ""
    items: List[dict] = field(default_factory=list)  # [{"product_id": ..., "quantity": ...}]
    total_amount: int = 0
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderCancelledEvent:
    """주문 취소 이벤트"""
    order_id: str = ""
    items: List[dict] = field(default_factory=list)
    occurred_at: datetime = field(default_factory=datetime.now)


# applications/catalog/application_layer/event_handlers.py -- 이벤트 구독 핸들러
class StockEventHandler:
    """재고 이벤트 핸들러 -- catalog 컨텍스트에서 ordering 이벤트를 구독"""

    def __init__(self, product_repo: "ProductRepository"):
        self._product_repo = product_repo

    def handle_order_placed(self, event: "OrderPlacedEvent") -> None:
        """OrderPlacedEvent 구독 -> 재고 차감 (결과적 일관성)"""
        for item in event.items:
            product = self._product_repo.find_by_id(item["product_id"])
            if product is None:
                raise ValueError(f"상품을 찾을 수 없습니다: {item['product_id']}")
            product.decrease_stock(item["quantity"])
            self._product_repo.save(product)

    def handle_order_cancelled(self, event: "OrderCancelledEvent") -> None:
        """OrderCancelledEvent 구독 -> 재고 복원"""
        for item in event.items:
            product = self._product_repo.find_by_id(item["product_id"])
            if product is None:
                raise ValueError(f"상품을 찾을 수 없습니다: {item['product_id']}")
            product.increase_stock(item["quantity"])
            self._product_repo.save(product)
```

[Reason] **동기 호출 -> 도메인 이벤트 + 결과적 일관성 (Vernon 규칙 4)** -- Django `post_save` signal에 숨어 있던 재고 차감 로직은 (1) 비즈니스 의도가 코드에 드러나지 않고, (2) 주문과 재고가 같은 트랜잭션에서 강결합된다. Order 애그리거트가 `OrderPlacedEvent`를 발행하고, catalog 컨텍스트의 `StockEventHandler`가 이를 구독하여 별도로 재고를 차감하는 구조로 변경했다. 크로스 애그리거트 일관성은 결과적 일관성으로 달성한다.

---

### 5.4 서비스의 비즈니스 로직 -> 응용 서비스 (조율만)

[Before]
```python
# orders/services.py -- 비즈니스 로직과 조율 로직이 혼재
def create_order(customer_id, items):
    order = Order.objects.create(customer_id=customer_id, status='pending')
    for item in items:
        product = Product.objects.get(id=item['product_id'])  # ORM 직접 호출
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
            price=product.price,
        )
    return order

def cancel_order(order_id):
    order = Order.objects.get(id=order_id)
    order.status = 'cancelled'  # 비즈니스 규칙 검증 없이 직접 변경
    order.save()
```

[After]
```python
# applications/ordering/application_layer/order_service.py
from applications.ordering.domain_layer.order.order import Order
from applications.ordering.domain_layer.repository.order_repo import OrderRepository


class OrderApplicationService:
    """주문 응용 서비스 -- 비즈니스 로직 없이 조율만 담당

    - 리포지토리에서 애그리거트를 조회한다
    - 애그리거트의 도메인 메서드를 호출한다
    - 도메인 이벤트를 수집하여 디스패치한다
    - 결과를 반환한다
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        catalog_service: "CatalogApplicationService",
        event_bus: "EventBus",
    ):
        self._order_repo = order_repo
        self._catalog_service = catalog_service
        self._event_bus = event_bus

    def create_order(self, customer_id: str, items: list[dict]) -> str:
        """주문 생성 유스케이스"""
        order = Order(customer_id=customer_id)

        # 상품 정보는 catalog 컨텍스트의 application_layer를 통해 조회
        for item in items:
            product_info = self._catalog_service.get_product_info(item["product_id"])
            order.add_item(
                product_id=product_info["id"],
                product_name=product_info["name"],
                price=product_info["price"],
                quantity=item["quantity"],
            )

        order.place()
        self._order_repo.save(order)

        # 도메인 이벤트 수집 후 디스패치
        for event in order.collect_domain_events():
            self._event_bus.publish(event)

        return order.id

    def cancel_order(self, order_id: str) -> None:
        """주문 취소 유스케이스"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")

        order.cancel()  # 비즈니스 규칙은 애그리거트에 위임
        self._order_repo.save(order)

        for event in order.collect_domain_events():
            self._event_bus.publish(event)
```

[Reason] **비즈니스 로직을 서비스에서 엔티티로 이동** -- 기존 `services.py`의 `create_order()`는 주문 상태 설정, 주문 항목 생성, 상품 조회를 모두 직접 수행하는 빈혈 모델 안티패턴이었다. 비즈니스 로직(`place()`, `cancel()`, 불변식 검증)은 Order 애그리거트로 이동하고, 응용 서비스는 리포지토리 조회, 도메인 메서드 호출, 이벤트 디스패치만 담당한다. 상품 정보 조회도 `Product.objects.get()` 직접 호출 대신 catalog 컨텍스트의 `application_layer` 서비스를 통해 수행한다 (도메인 간 읽기 import 규칙 준수).

---

### 5.5 ORM 모델에서 도메인 모델 분리

[Before]
```python
# products/models.py -- 도메인 모델 == ORM 모델 (Django 프레임워크에 종속)
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(...)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
```

[After]
```python
# applications/catalog/domain_layer/product/product.py -- 순수 도메인 모델
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Product:
    """상품 애그리거트 루트 -- Django ORM에 의존하지 않는 순수 Python 모델

    Category는 category_id로만 참조한다 (Vernon 규칙 3).
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    price: int = 0
    stock: int = 0
    category_id: str = ""  # Category 애그리거트를 ID로만 참조

    def decrease_stock(self, quantity: int) -> None:
        """재고 차감 -- 비즈니스 규칙이 엔티티 안에 위치"""
        if quantity <= 0:
            raise ValueError("차감 수량은 0보다 커야 합니다")
        if self.stock < quantity:
            raise ValueError(f"재고가 부족합니다 (현재: {self.stock}, 요청: {quantity})")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """재고 증가"""
        if quantity <= 0:
            raise ValueError("증가 수량은 0보다 커야 합니다")
        self.stock += quantity


# applications/catalog/infra_layer/django_catalog/models/product_model.py -- ORM 모델
from django.db import models


class ProductModel(models.Model):
    """ORM 모델 -- domain entity와의 변환 책임을 진다"""
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    stock = models.IntegerField(default=0)
    category_id = models.UUIDField()  # FK 대신 ID만 저장

    class Meta:
        app_label = "django_catalog"
        db_table = "catalog_product"


# applications/catalog/infra_layer/repository/product_repo.py -- 리포지토리 구현체
from applications.catalog.domain_layer.product.product import Product
from applications.catalog.domain_layer.repository.product_repo import ProductRepository
from applications.catalog.infra_layer.django_catalog.models.product_model import ProductModel


class DjangoProductRepository(ProductRepository):
    """Django ORM 기반 리포지토리 구현체 -- ORM <-> domain 변환"""

    def find_by_id(self, product_id: str) -> Product | None:
        try:
            orm_obj = ProductModel.objects.get(id=product_id)
            return self._to_domain(orm_obj)
        except ProductModel.DoesNotExist:
            return None

    def save(self, product: Product) -> None:
        orm_obj = self._to_orm(product)
        orm_obj.save()

    def _to_domain(self, orm_obj: ProductModel) -> Product:
        return Product(
            id=str(orm_obj.id),
            name=orm_obj.name,
            price=orm_obj.price,
            stock=orm_obj.stock,
            category_id=str(orm_obj.category_id),
        )

    def _to_orm(self, domain_obj: Product) -> ProductModel:
        return ProductModel(
            id=domain_obj.id,
            name=domain_obj.name,
            price=domain_obj.price,
            stock=domain_obj.stock,
            category_id=domain_obj.category_id,
        )
```

[Reason] **도메인 모델의 프레임워크 독립성 확보 (DIP)** -- 기존에는 `Product(models.Model)`로 도메인 모델이 Django ORM에 직접 종속되어 있었다. 순수 Python `@dataclass`로 도메인 모델을 분리하고, ORM 모델(`ProductModel`)은 infra_layer에 배치했다. 리포지토리 구현체가 ORM <-> domain 변환을 담당한다. "ORM이 도메인 모델을 임포트하게 하라. 도메인 모델이 ORM을 임포트하면 안 된다."

---

### 5.6 바운디드 컨텍스트 경계 명확화

[Before]
```python
# orders/services.py -- 주문 컨텍스트에서 상품 컨텍스트 ORM 직접 접근
from products.models import Product

def create_order(customer_id, items):
    product = Product.objects.get(id=item['product_id'])  # products 도메인의 infra에 직접 접근
```

[After]
```python
# applications/ordering/application_layer/order_service.py
# 타 컨텍스트의 application_layer 서비스만 import
from applications.catalog.application_layer.catalog_service import CatalogApplicationService

class OrderApplicationService:
    def __init__(self, ..., catalog_service: CatalogApplicationService, ...):
        self._catalog_service = catalog_service

    def create_order(self, customer_id, items):
        # catalog 컨텍스트의 application_layer를 통해서만 접근
        product_info = self._catalog_service.get_product_info(item["product_id"])
```

[Reason] **바운디드 컨텍스트 경계 보호** -- 기존에는 `orders/services.py`에서 `products.models.Product`를 직접 import하여 다른 바운디드 컨텍스트의 infra_layer에 직접 접근했다. DDD 도메인 간 읽기 규칙에 따라, 타 도메인의 `application_layer` 서비스만 직접 import하고, `domain_layer`와 `infra_layer`는 직접 접근을 금지한다.

---

## 6. config/settings.py 변경

```python
INSTALLED_APPS = [
    # ...
    "applications.catalog.infra_layer.django_catalog",
    "applications.ordering.infra_layer.django_ordering",
]
```

---

## 7. 리팩토링 체크리스트 검증

- [x] 빈혈 도메인 모델 -> 비즈니스 로직을 엔티티/값 객체 안으로 이동
- [x] 큰 애그리거트 -> Product와 Category를 별도 애그리거트로 분리
- [x] 직접 참조 -> ID 참조로 교체 (Product-Category, Order-Product)
- [x] 비즈니스 로직이 서비스에 -> 엔티티/값 객체 메서드로 이동
- [x] 동기 호출 (Django signals) -> 도메인 이벤트 + 결과적 일관성으로 교체
- [x] 모호한 경계 -> catalog / ordering 바운디드 컨텍스트로 분리
