# 전자상거래 주문 처리 아키텍처 설계

## 1. 복잡도 평가

주문 도메인은 단순 CRUD가 아니다. 다음 요소들이 복잡도를 높인다.

| 요소 | 복잡도 기여 |
|---|---|
| 외부 PG사(토스페이먼츠) 통합 | 결제 승인/취소/부분취소 등 다양한 시나리오 |
| 외부 배송 시스템(CJ대한통운) 통합 | 주문 확인 후 비동기 알림 필요 |
| 읽기/쓰기 비대칭 (10:1) | 조회 최적화 필요 |
| 향후 배송 마이크로서비스 분리 | 통합 경계가 명확해야 함 |

**결론**: 외부 통합이 2개 이상이고, 향후 서비스 분리를 고려해야 하므로 **Hexagonal Architecture**를 기본으로 채택한다. 단순 Layered로는 외부 시스템 교체와 서비스 분리 시 도메인 로직이 인프라에 결합되는 문제가 발생한다.

---

## 2. 아키텍처 패턴 선택

### 2.1 Hexagonal Architecture (기본 구조)

외부 통합이 다수(PG사, 배송 시스템)이고 진입점도 다양할 수 있으므로 Hexagonal이 적합하다. 도메인이 포트(인터페이스)를 정의하고, 인프라가 어댑터로 구현한다.

### 2.2 CQRS 수준 1 (동일 DB, 분리된 모델)

주문 조회가 주문 생성보다 10배 많으므로, 읽기/쓰기 모델을 분리하여 각각 최적화한다. 단, 현재 Django 모놀리스이므로 별도 DB까지 가지 않고 **동일 DB에서 모델만 분리**하는 수준 1로 시작한다.

- **Command 모델**: 주문 생성, 결제 처리, 상태 변경 등 비즈니스 로직과 불변식 보호에 집중
- **Query 모델**: 주문 목록, 주문 상세 등 프레젠테이션에 최적화된 비정규화 DTO

Event Sourcing은 도입하지 않는다. 현재 상황에서 완전한 이벤트 이력이나 시간 여행 쿼리가 필요하지 않고, Django ORM 기반 모놀리스에서 Event Sourcing은 과도한 복잡성을 추가한다.

### 2.3 Outbox Pattern (배송 시스템 알림)

주문 확인 후 배송 시스템에 알려야 하는 요구사항은 **Dual Write Problem**에 해당한다. DB에 주문 상태를 저장하고 동시에 배송 시스템에 알림을 보내야 하는데, 두 작업의 원자성을 보장할 수 없다.

Outbox Pattern으로 해결한다:
1. 주문 상태 변경과 Outbox 레코드 INSERT를 같은 DB 트랜잭션으로 처리
2. Polling Publisher가 Outbox를 읽어 배송 시스템에 전달
3. 향후 배송 서비스 분리 시, Polling Publisher를 메시지 브로커 발행으로 교체

### 2.4 패턴 미적용 판단

| 패턴 | 미적용 사유 |
|---|---|
| Event Sourcing | 주문 이력은 상태 변경 로그로 충분, append-only 스트림 불필요 |
| CQRS 수준 2/3 | 현재 모놀리스에서 별도 DB는 과도, 수준 1로 시작 |
| Snapshot/Projection | Event Sourcing 미적용이므로 불필요 |

---

## 3. 의존성 방향과 계층 구조

모든 소스 코드 의존성은 안쪽(도메인)을 향한다. 인터페이스(포트)는 도메인 계층이 정의하고 소유하며, 인프라 계층이 구현한다.

```
orders/
  domain/                          # 핵심 비즈니스 로직 (의존성 없음)
    models.py                      # Order Aggregate, OrderLine, OrderStatus (순수 도메인)
    events.py                      # OrderConfirmed, OrderCancelled 등 도메인 이벤트
    exceptions.py                  # OrderAlreadyPaid, InsufficientStock 등

  ports/
    driving/                       # Primary Ports (Use Case 인터페이스)
      order_commands.py            # PlaceOrder, ConfirmOrder, CancelOrder
      order_queries.py             # GetOrderDetail, ListOrders
    driven/                        # Secondary Ports (외부 시스템 인터페이스)
      payment_gateway.py           # PaymentGateway ABC
      shipping_notifier.py         # ShippingNotifier ABC
      order_repository.py          # OrderRepository ABC
      order_read_model.py          # OrderReadModel ABC

  application/                     # Use Case 조율 (ports에만 의존)
    command_handlers.py            # PlaceOrderHandler, ConfirmOrderHandler
    query_handlers.py              # GetOrderDetailHandler, ListOrdersHandler
    event_handlers.py              # 도메인 이벤트 → Integration Event 변환

  adapters/
    driving/                       # Primary Adapters (진입점)
      api/
        views.py                   # DRF ViewSet (REST API)
        serializers.py             # 요청/응답 직렬화
    driven/                        # Secondary Adapters (외부 시스템 구현)
      toss_payment_gateway.py      # 토스페이먼츠 API 구현
      cj_shipping_notifier.py      # CJ대한통운 API 구현 (ACL 포함)
      django_order_repository.py   # Django ORM 기반 Repository
      django_order_read_model.py   # Django ORM 기반 Read Model (비정규화 쿼리)
      outbox.py                    # Outbox 테이블 및 Polling Publisher

  infrastructure/
    django_models.py               # Django ORM 모델 (DB 스키마)
    migrations/                    # Django 마이그레이션
```

### 의존성 규칙

```
adapters/driving (REST API)
    |
    v
application (Use Case 핸들러)
    |
    v
domain (순수 비즈니스 로직)  <--소유--  ports (인터페이스 정의)
    ^
    |
adapters/driven (토스, CJ, Django ORM) --- 구현 ---> ports
```

- `domain/`은 어떤 외부 패키지도 import하지 않는다
- `ports/`는 `domain/`만 import한다
- `application/`은 `domain/`과 `ports/`만 import한다
- `adapters/`는 모든 계층을 import할 수 있지만, 역방향은 불가하다
- `infrastructure/`의 Django 모델은 도메인 모델과 분리된다

---

## 4. 핵심 컴포넌트 설계

### 4.1 도메인 모델 (Command Side)

```python
# domain/models.py
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from uuid import UUID


class OrderStatus(Enum):
    PENDING = "pending"
    PAYMENT_REQUESTED = "payment_requested"
    CONFIRMED = "confirmed"
    SHIPPING_NOTIFIED = "shipping_notified"
    CANCELLED = "cancelled"


@dataclass
class OrderLine:
    product_id: UUID
    product_name: str
    unit_price: Decimal
    quantity: int

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    """주문 Aggregate Root"""
    id: UUID
    customer_id: UUID
    lines: list[OrderLine] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    total_amount: Decimal = Decimal("0")
    _events: list = field(default_factory=list, repr=False)

    def place(self) -> None:
        if not self.lines:
            raise OrderValidationError("주문 항목이 비어 있습니다")
        self.total_amount = sum(line.subtotal for line in self.lines)
        self.status = OrderStatus.PAYMENT_REQUESTED
        self._events.append(OrderPlaced(order_id=self.id, amount=self.total_amount))

    def confirm(self, payment_id: str) -> None:
        if self.status != OrderStatus.PAYMENT_REQUESTED:
            raise InvalidOrderStateError(
                f"결제 확인 불가 상태: {self.status.value}"
            )
        self.status = OrderStatus.CONFIRMED
        self._events.append(
            OrderConfirmed(order_id=self.id, payment_id=payment_id)
        )

    def mark_shipping_notified(self) -> None:
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderStateError(
                f"배송 알림 불가 상태: {self.status.value}"
            )
        self.status = OrderStatus.SHIPPING_NOTIFIED

    def cancel(self, reason: str) -> None:
        if self.status in (OrderStatus.SHIPPING_NOTIFIED,):
            raise InvalidOrderStateError("배송 알림 후에는 취소 불가")
        self.status = OrderStatus.CANCELLED
        self._events.append(OrderCancelled(order_id=self.id, reason=reason))

    def collect_events(self) -> list:
        events = self._events[:]
        self._events.clear()
        return events
```

### 4.2 Driven Ports (도메인이 소유하는 인터페이스)

```python
# ports/driven/payment_gateway.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class PaymentResult:
    payment_id: str
    success: bool
    error_message: str | None = None


class PaymentGateway(ABC):
    """결제 처리 포트 — 도메인이 정의, 인프라가 구현"""

    @abstractmethod
    def request_payment(
        self, order_id: UUID, amount: Decimal, method: str
    ) -> PaymentResult: ...

    @abstractmethod
    def cancel_payment(self, payment_id: str) -> PaymentResult: ...
```

```python
# ports/driven/shipping_notifier.py
from abc import ABC, abstractmethod
from uuid import UUID


class ShippingNotifier(ABC):
    """배송 알림 포트 — 향후 마이크로서비스 분리 대비"""

    @abstractmethod
    def notify_order_confirmed(
        self, order_id: UUID, shipping_address: str, items: list[dict]
    ) -> None: ...
```

```python
# ports/driven/order_repository.py
from abc import ABC, abstractmethod
from uuid import UUID
from domain.models import Order


class OrderRepository(ABC):
    """Aggregate 단위 Repository — 주문 Aggregate 당 하나"""

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def get(self, order_id: UUID) -> Order: ...
```

```python
# ports/driven/order_read_model.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class OrderSummaryDTO:
    """조회에 최적화된 비정규화 DTO — 도메인 로직 없음"""
    order_id: UUID
    customer_name: str
    total_amount: Decimal
    status: str
    item_count: int
    created_at: str


@dataclass(frozen=True)
class OrderDetailDTO:
    order_id: UUID
    customer_name: str
    lines: list[dict]
    total_amount: Decimal
    status: str
    payment_id: str | None
    shipping_tracking_number: str | None
    created_at: str
    updated_at: str


class OrderReadModel(ABC):
    """Query Side 전용 — DB 직접 쿼리로 프레젠테이션 최적화"""

    @abstractmethod
    def get_detail(self, order_id: UUID) -> OrderDetailDTO: ...

    @abstractmethod
    def list_by_customer(
        self, customer_id: UUID, page: int = 1, size: int = 20
    ) -> list[OrderSummaryDTO]: ...

    @abstractmethod
    def list_recent(
        self, page: int = 1, size: int = 20
    ) -> list[OrderSummaryDTO]: ...
```

### 4.3 Application Layer (Command Handler)

```python
# application/command_handlers.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.models import Order, OrderLine
from ports.driven.payment_gateway import PaymentGateway
from ports.driven.order_repository import OrderRepository


@dataclass(frozen=True)
class PlaceOrder:
    """Command: 비즈니스 의도를 표현"""
    customer_id: UUID
    items: list[dict]  # [{product_id, product_name, unit_price, quantity}]
    payment_method: str


class PlaceOrderHandler:
    """Command를 받아 Aggregate를 통해 비즈니스 로직 실행"""

    def __init__(
        self,
        repository: OrderRepository,
        payment_gateway: PaymentGateway,
        outbox: "OutboxWriter",
    ):
        self._repository = repository
        self._payment = payment_gateway
        self._outbox = outbox

    def handle(self, command: PlaceOrder) -> UUID:
        # 1. Aggregate 생성 및 비즈니스 로직 실행
        order = Order(
            id=uuid4(),
            customer_id=command.customer_id,
            lines=[
                OrderLine(
                    product_id=item["product_id"],
                    product_name=item["product_name"],
                    unit_price=Decimal(str(item["unit_price"])),
                    quantity=item["quantity"],
                )
                for item in command.items
            ],
        )
        order.place()

        # 2. 결제 요청 (외부 PG사)
        result = self._payment.request_payment(
            order_id=order.id,
            amount=order.total_amount,
            method=command.payment_method,
        )

        if result.success:
            order.confirm(payment_id=result.payment_id)

        # 3. 같은 트랜잭션으로 저장 + Outbox 기록
        self._repository.save(order)

        for event in order.collect_events():
            self._outbox.write(event)  # 같은 DB 트랜잭션 내에서 Outbox INSERT

        return order.id
```

### 4.4 ACL: 외부 시스템 어댑터

토스페이먼츠와 CJ대한통운은 각각 자체 도메인 모델과 API 규격을 가진다. ACL로 감싸서 내부 도메인 모델 오염을 방지한다.

```python
# adapters/driven/toss_payment_gateway.py
import requests
from decimal import Decimal
from uuid import UUID

from ports.driven.payment_gateway import PaymentGateway, PaymentResult


class TossPaymentGateway(PaymentGateway):
    """ACL: 토스페이먼츠 API를 내부 PaymentGateway 인터페이스로 변환

    Facade: 토스 API의 복잡한 인증/요청 형식을 단순화
    Adapter: 토스 응답을 PaymentResult로 변환
    Translator: 토스 도메인 용어를 내부 도메인 용어로 매핑
    """

    def __init__(self, secret_key: str, base_url: str):
        self._secret_key = secret_key
        self._base_url = base_url

    def request_payment(
        self, order_id: UUID, amount: Decimal, method: str
    ) -> PaymentResult:
        # Facade: 토스 API 호출 단순화
        response = requests.post(
            f"{self._base_url}/v1/payments/confirm",
            json={
                "orderId": str(order_id),        # Translator: UUID -> string
                "amount": int(amount),            # Translator: Decimal -> int (원 단위)
                "paymentKey": method,
            },
            headers=self._auth_headers(),
        )

        # Adapter: 토스 응답 -> 내부 PaymentResult
        if response.status_code == 200:
            data = response.json()
            return PaymentResult(
                payment_id=data["paymentKey"],    # Translator: 토스 용어 -> 내부 용어
                success=True,
            )
        else:
            error = response.json()
            return PaymentResult(
                payment_id="",
                success=False,
                error_message=error.get("message", "결제 실패"),
            )

    def cancel_payment(self, payment_id: str) -> PaymentResult:
        response = requests.post(
            f"{self._base_url}/v1/payments/{payment_id}/cancel",
            json={"cancelReason": "주문 취소"},
            headers=self._auth_headers(),
        )
        return PaymentResult(
            payment_id=payment_id,
            success=response.status_code == 200,
        )

    def _auth_headers(self) -> dict:
        import base64
        encoded = base64.b64encode(f"{self._secret_key}:".encode()).decode()
        return {"Authorization": f"Basic {encoded}"}
```

```python
# adapters/driven/cj_shipping_notifier.py
import requests
from uuid import UUID

from ports.driven.shipping_notifier import ShippingNotifier


class CJShippingNotifier(ShippingNotifier):
    """ACL: CJ대한통운 API를 내부 ShippingNotifier 인터페이스로 변환

    향후 배송 마이크로서비스로 분리 시, 이 어댑터만 교체하면 된다.
    예: CJShippingNotifier -> ShippingServiceClient (gRPC/HTTP)
    """

    def __init__(self, api_key: str, base_url: str):
        self._api_key = api_key
        self._base_url = base_url

    def notify_order_confirmed(
        self, order_id: UUID, shipping_address: str, items: list[dict]
    ) -> None:
        # Translator: 내부 도메인 -> CJ API 규격
        cj_payload = {
            "sndNm": "우리쇼핑몰",
            "rcvNm": "",                           # 별도 조회 필요
            "rcvAddr": shipping_address,
            "ordNo": str(order_id),
            "itemList": [
                {
                    "itemNm": item["product_name"],
                    "itemQty": item["quantity"],
                }
                for item in items
            ],
        }

        requests.post(
            f"{self._base_url}/api/v1/order/register",
            json=cj_payload,
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
```

### 4.5 Outbox Pattern (배송 알림의 신뢰성 보장)

```python
# adapters/driven/outbox.py
from django.db import models
import json
from uuid import uuid4


class OutboxMessage(models.Model):
    """Outbox 테이블 — 비즈니스 데이터와 같은 DB 트랜잭션으로 저장"""
    id = models.UUIDField(primary_key=True, default=uuid4)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)

    class Meta:
        db_table = "order_outbox"
        indexes = [
            models.Index(fields=["published", "created_at"]),
        ]


class OutboxWriter:
    """같은 DB 트랜잭션 내에서 Outbox에 이벤트 기록"""

    def write(self, event) -> None:
        OutboxMessage.objects.create(
            event_type=type(event).__name__,
            payload=event.__dict__,
        )


class OutboxPollingPublisher:
    """Polling Publisher: 주기적으로 Outbox 조회 후 처리

    Django management command 또는 Celery beat로 실행.
    향후 배송 서비스 분리 시, 여기서 메시지 브로커(Kafka 등)로 발행하도록 교체.
    """

    def __init__(self, shipping_notifier: "ShippingNotifier"):
        self._shipping = shipping_notifier

    def publish_pending(self, batch_size: int = 100) -> int:
        messages = OutboxMessage.objects.filter(
            published=False
        ).order_by("created_at")[:batch_size]

        published_count = 0
        for msg in messages:
            if msg.event_type == "OrderConfirmed":
                self._shipping.notify_order_confirmed(
                    order_id=msg.payload["order_id"],
                    shipping_address=msg.payload.get("shipping_address", ""),
                    items=msg.payload.get("items", []),
                )
            msg.published = True
            msg.save(update_fields=["published"])
            published_count += 1

        return published_count
```

### 4.6 Query Side (Read Model)

```python
# adapters/driven/django_order_read_model.py
from uuid import UUID
from django.db import connection

from ports.driven.order_read_model import (
    OrderReadModel, OrderSummaryDTO, OrderDetailDTO,
)


class DjangoOrderReadModel(OrderReadModel):
    """DB 직접 쿼리로 조회 성능 최적화 — 도메인 로직 없음

    Django ORM의 values(), annotate() 또는 raw SQL을 사용하여
    Command 모델(Aggregate)을 거치지 않고 비정규화된 DTO를 직접 반환한다.
    """

    def get_detail(self, order_id: UUID) -> OrderDetailDTO:
        # ORM annotate 또는 raw SQL로 JOIN + 비정규화 조회
        # Aggregate를 로드하지 않으므로 불필요한 비즈니스 로직 초기화 없음
        from infrastructure.django_models import DjangoOrder
        row = (
            DjangoOrder.objects
            .select_related("customer")
            .prefetch_related("lines")
            .get(id=order_id)
        )
        return OrderDetailDTO(
            order_id=row.id,
            customer_name=row.customer.name,
            lines=[
                {
                    "product_name": line.product_name,
                    "unit_price": str(line.unit_price),
                    "quantity": line.quantity,
                    "subtotal": str(line.subtotal),
                }
                for line in row.lines.all()
            ],
            total_amount=row.total_amount,
            status=row.status,
            payment_id=row.payment_id,
            shipping_tracking_number=row.tracking_number,
            created_at=row.created_at.isoformat(),
            updated_at=row.updated_at.isoformat(),
        )

    def list_by_customer(
        self, customer_id: UUID, page: int = 1, size: int = 20
    ) -> list[OrderSummaryDTO]:
        from infrastructure.django_models import DjangoOrder
        offset = (page - 1) * size
        rows = (
            DjangoOrder.objects
            .filter(customer_id=customer_id)
            .annotate(item_count=models.Count("lines"))
            .values(
                "id", "customer__name", "total_amount",
                "status", "item_count", "created_at",
            )
            .order_by("-created_at")[offset:offset + size]
        )
        return [
            OrderSummaryDTO(
                order_id=row["id"],
                customer_name=row["customer__name"],
                total_amount=row["total_amount"],
                status=row["status"],
                item_count=row["item_count"],
                created_at=row["created_at"].isoformat(),
            )
            for row in rows
        ]

    def list_recent(
        self, page: int = 1, size: int = 20
    ) -> list[OrderSummaryDTO]:
        from infrastructure.django_models import DjangoOrder
        offset = (page - 1) * size
        rows = (
            DjangoOrder.objects
            .annotate(item_count=models.Count("lines"))
            .values(
                "id", "customer__name", "total_amount",
                "status", "item_count", "created_at",
            )
            .order_by("-created_at")[offset:offset + size]
        )
        return [
            OrderSummaryDTO(
                order_id=row["id"],
                customer_name=row["customer__name"],
                total_amount=row["total_amount"],
                status=row["status"],
                item_count=row["item_count"],
                created_at=row["created_at"].isoformat(),
            )
            for row in rows
        ]
```

---

## 5. 통합 경계 설계

### 5.1 외부 시스템 격리 (ACL)

| 외부 시스템 | 포트 (도메인 소유) | 어댑터 (인프라 구현) | ACL 역할 |
|---|---|---|---|
| 토스페이먼츠 | `PaymentGateway` | `TossPaymentGateway` | 토스 API 규격/용어를 내부 도메인으로 변환 |
| CJ대한통운 | `ShippingNotifier` | `CJShippingNotifier` | CJ API 필드명/형식을 내부 도메인으로 변환 |

외부 시스템 변경(PG사 교체, 배송사 변경) 시 어댑터만 교체하면 되고, 도메인과 애플리케이션 계층은 영향을 받지 않는다.

### 5.2 향후 배송 마이크로서비스 분리 경로

현재 아키텍처는 배송 서비스 분리를 다음과 같이 지원한다.

```
현재 (모놀리스):
  OrderConfirmed 이벤트 → Outbox → Polling Publisher → CJShippingNotifier (직접 호출)

분리 후 (마이크로서비스):
  OrderConfirmed 이벤트 → Outbox → Polling Publisher → Message Broker (Kafka)
                                                            |
                                                            v
                                              [배송 서비스] → CJ대한통운 API
```

변경 범위:
1. `OutboxPollingPublisher`가 `ShippingNotifier` 직접 호출 대신 메시지 브로커에 발행
2. `CJShippingNotifier`를 배송 서비스로 이동
3. 주문 도메인과 애플리케이션 계층은 변경 없음

이 분리가 가능한 이유:
- 도메인 이벤트(`OrderConfirmed`)가 이미 정의되어 있다
- Outbox Pattern이 이미 비동기 메시징 인프라를 추상화하고 있다
- `ShippingNotifier` 포트가 도메인으로부터 배송 알림의 구현 방식을 격리하고 있다

### 5.3 도메인 이벤트와 Integration Event 분리

주문 도메인 내부 이벤트(`OrderConfirmed`)를 그대로 외부에 노출하지 않는다. Outbox에 기록할 때 Integration Event로 변환한다.

```python
# application/event_handlers.py

class OrderEventHandler:
    """도메인 이벤트를 Integration Event로 변환하여 Outbox에 기록"""

    def __init__(self, outbox: OutboxWriter):
        self._outbox = outbox

    def handle_order_confirmed(self, event: OrderConfirmed) -> None:
        # 내부 도메인 이벤트 -> Published Language로 변환
        integration_event = {
            "event_type": "order.confirmed",
            "version": "1.0",
            "order_id": str(event.order_id),
            "payment_id": event.payment_id,
            "timestamp": datetime.utcnow().isoformat(),
            # 내부 구현 세부사항은 포함하지 않음
        }
        self._outbox.write_raw(
            event_type="order.confirmed",
            payload=integration_event,
        )
```

---

## 6. Django 실용적 고려사항

Django ORM은 Active Record 패턴이므로, 순수 Data Mapper를 구현하면 Django의 장점(admin, forms, migrations)을 잃는다. 다음과 같은 실용적 타협을 적용한다.

### 6.1 Django 모델과 도메인 모델의 관계

```python
# infrastructure/django_models.py — DB 스키마 전용
class DjangoOrder(models.Model):
    id = models.UUIDField(primary_key=True)
    customer = models.ForeignKey("Customer", on_delete=models.PROTECT)
    status = models.CharField(max_length=30)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_id = models.CharField(max_length=100, null=True)
    tracking_number = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"


class DjangoOrderLine(models.Model):
    order = models.ForeignKey(DjangoOrder, related_name="lines", on_delete=models.CASCADE)
    product_id = models.UUIDField()
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_lines"
```

### 6.2 Repository에서 수동 변환

```python
# adapters/driven/django_order_repository.py
from domain.models import Order, OrderLine, OrderStatus
from infrastructure.django_models import DjangoOrder, DjangoOrderLine
from ports.driven.order_repository import OrderRepository


class DjangoOrderRepository(OrderRepository):
    """Django ORM 기반 Repository — to_domain/from_domain 변환 레이어 포함"""

    def save(self, order: Order) -> None:
        django_order, _ = DjangoOrder.objects.update_or_create(
            id=order.id,
            defaults={
                "customer_id": order.customer_id,
                "status": order.status.value,
                "total_amount": order.total_amount,
            },
        )
        # OrderLine 동기화
        DjangoOrderLine.objects.filter(order=django_order).delete()
        DjangoOrderLine.objects.bulk_create([
            DjangoOrderLine(
                order=django_order,
                product_id=line.product_id,
                product_name=line.product_name,
                unit_price=line.unit_price,
                quantity=line.quantity,
                subtotal=line.subtotal,
            )
            for line in order.lines
        ])

    def get(self, order_id) -> Order:
        row = DjangoOrder.objects.prefetch_related("lines").get(id=order_id)
        return Order(
            id=row.id,
            customer_id=row.customer_id,
            status=OrderStatus(row.status),
            total_amount=row.total_amount,
            lines=[
                OrderLine(
                    product_id=line.product_id,
                    product_name=line.product_name,
                    unit_price=line.unit_price,
                    quantity=line.quantity,
                )
                for line in row.lines.all()
            ],
        )
```

### 6.3 트랜잭션 관리

Django의 `transaction.atomic()`을 Unit of Work 대신 사용한다. Django ORM에서 별도 UoW를 구현하면 `set_autocommit(False)` 등 비표준적 관리가 필요해 boilerplate가 과도해진다.

```python
# application/command_handlers.py 내 트랜잭션 경계
from django.db import transaction


class PlaceOrderHandler:
    def handle(self, command: PlaceOrder) -> UUID:
        with transaction.atomic():
            # 1. 도메인 로직
            order = self._build_order(command)
            order.place()

            # 2. 결제 (외부 호출은 트랜잭션 밖이 이상적이나,
            #          결제 결과에 따라 상태가 달라지므로 내부에서 처리)
            result = self._payment.request_payment(...)
            if result.success:
                order.confirm(result.payment_id)

            # 3. 같은 트랜잭션으로 주문 저장 + Outbox 기록
            self._repository.save(order)
            for event in order.collect_events():
                self._outbox.write(event)

        return order.id
```

---

## 7. 패턴 적용 요약

| 패턴 | 적용 위치 | 근거 |
|---|---|---|
| **Hexagonal Architecture** | 주문 도메인 전체 | 외부 통합 2개(PG, 배송), 향후 서비스 분리 대비 |
| **CQRS 수준 1** | 주문 읽기/쓰기 분리 | 읽기:쓰기 = 10:1 비대칭 부하 |
| **Outbox Pattern** | 배송 알림 | DB+외부시스템 Dual Write 원자성 보장 |
| **ACL** | 토스페이먼츠, CJ대한통운 | 외부 도메인 모델 오염 방지, 어댑터 교체 용이 |
| **Repository** | 주문 Aggregate | Aggregate 단위 영속화, 도메인-인프라 분리 |
| **DIP (Ownership Inversion)** | 모든 포트 | 도메인이 인터페이스를 정의하고 소유, 인프라가 구현 |
| **도메인 이벤트 -> Integration Event 변환** | Outbox 기록 시 | 내부 구현을 외부에 노출하지 않음 |

| 패턴 | 미적용 | 사유 |
|---|---|---|
| Event Sourcing | 전체 | 이벤트 이력 불필요, Django 모놀리스에 과도한 복잡성 |
| CQRS 수준 2/3 | 별도 DB | 현재 모놀리스에서 불필요, 수준 1로 충분 |
| 별도 Unit of Work | 전체 | Django `transaction.atomic()`으로 대체 |
| Data Mapper (순수) | 전체 | Django ORM에 해당 메커니즘 부재, 수동 변환으로 타협 |
