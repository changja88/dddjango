# 주문 서비스 헥사고날 아키텍처 설계

## 복잡도 평가

주문 서비스는 단순 CRUD가 아니다. 결제 시스템, 재고 시스템, 배송 시스템 등 다수의 외부 통합이 존재하고, 주문 생성/결제/취소 등 비즈니스 규칙이 복잡하다. 따라서 레이어드 아키텍처로는 부족하며, **헥사고날 아키텍처(포트 & 어댑터)**가 적합하다.

## 의존성 방향

모든 소스 코드 의존성은 안쪽을 향한다. 도메인이 포트(인터페이스)를 정의하고 소유하며, 인프라가 이를 구현한다(소유권 역전).

```
Adapters(외부) → Ports(경계) → Application/Domain(내부)
```

## 디렉터리 구조

```
order/
  application/
    ports/
      driving/             # 인바운드 포트 (외부 -> 애플리케이션)
        order_use_case.py
      driven/              # 아웃바운드 포트 (애플리케이션 -> 외부)
        order_repository.py
        payment_gateway.py
        inventory_checker.py
        notification_sender.py
    services/
      order_service.py     # 유스케이스 구현 (포트 조율)
  domain/
    order.py               # 애그리거트 루트
    order_item.py           # 엔티티
    order_status.py         # 값 객체
    money.py                # 값 객체
  adapters/
    driving/               # 인바운드 어댑터
      rest_controller.py
      grpc_handler.py
      cli_command.py
    driven/                # 아웃바운드 어댑터
      postgres_order_repository.py
      stripe_payment_gateway.py
      inventory_api_adapter.py
      email_notification_adapter.py
```

## 인바운드 포트 (Driving Port)

인바운드 포트는 외부 액터가 애플리케이션을 구동하기 위해 호출하는 인터페이스다. 유스케이스 단위로 정의한다.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: str
    items: list[OrderItemDto]
    shipping_address: str


@dataclass(frozen=True)
class OrderResult:
    order_id: str
    status: str
    total_amount: int


class OrderCommandUseCase(ABC):
    """주문 커맨드 유스케이스 — 인바운드 포트"""

    @abstractmethod
    def create_order(self, command: CreateOrderCommand) -> OrderResult: ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> None: ...

    @abstractmethod
    def confirm_payment(self, order_id: str, payment_ref: str) -> None: ...


class OrderQueryUseCase(ABC):
    """주문 조회 유스케이스 — 인바운드 포트"""

    @abstractmethod
    def get_order(self, order_id: str) -> OrderResult: ...

    @abstractmethod
    def list_orders_by_customer(self, customer_id: str) -> list[OrderResult]: ...
```

**설계 의도:** 커맨드와 쿼리 유스케이스를 별도 포트로 분리했다. CQS 원칙에 따라 커맨드 메서드(`cancel_order`, `confirm_payment`)는 쿼리 데이터를 반환하지 않는다. `create_order`만 생성 결과를 반환하는데, 이는 클라이언트가 생성된 주문의 식별자를 알아야 하는 실용적 이유에서이다.

## 아웃바운드 포트 (Driven Port)

아웃바운드 포트는 애플리케이션이 외부 시스템에 요청하기 위해 사용하는 인터페이스다. 도메인 계층이 정의하고 소유하며, 기술적 연산이 아닌 도메인 의도를 표현한다.

```python
from abc import ABC, abstractmethod


class OrderRepository(ABC):
    """주문 영속성 — 아웃바운드 포트
    애그리거트 단위로 정의한다 (테이블 단위가 아님).
    """

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> list[Order]: ...


class PaymentGateway(ABC):
    """결제 처리 — 아웃바운드 포트"""

    @abstractmethod
    def charge(self, amount: Money, method: PaymentMethod) -> PaymentResult: ...

    @abstractmethod
    def refund(self, payment_ref: str, amount: Money) -> RefundResult: ...


class InventoryChecker(ABC):
    """재고 확인 — 아웃바운드 포트"""

    @abstractmethod
    def check_availability(self, items: list[OrderItem]) -> AvailabilityResult: ...

    @abstractmethod
    def reserve(self, items: list[OrderItem]) -> ReservationToken: ...

    @abstractmethod
    def release(self, token: ReservationToken) -> None: ...


class NotificationSender(ABC):
    """알림 발송 — 아웃바운드 포트"""

    @abstractmethod
    def send_order_confirmation(self, order: Order) -> None: ...

    @abstractmethod
    def send_cancellation_notice(self, order: Order) -> None: ...
```

**설계 의도:**
- `OrderRepository`는 테이블이 아닌 애그리거트 단위로 정의했다. `save`는 주문과 주문 항목을 포함한 전체 애그리거트를 저장한다.
- `PaymentGateway`, `InventoryChecker`, `NotificationSender`는 각각 외부 시스템과의 대화를 도메인 언어로 표현한다. `http_post`나 `send_request`가 아니라 `charge`, `check_availability`, `send_order_confirmation`처럼 비즈니스 의도를 드러낸다.

## 어댑터 구현 예시

### 인바운드 어댑터 (Driving Adapter)

```python
class OrderRestController:
    """REST API — 인바운드 어댑터
    비즈니스 로직을 포함하지 않는다. 포트를 호출할 뿐이다.
    """

    def __init__(self, command_use_case: OrderCommandUseCase,
                 query_use_case: OrderQueryUseCase) -> None:
        self._command = command_use_case
        self._query = query_use_case

    def post_order(self, request: HttpRequest) -> HttpResponse:
        command = CreateOrderCommand(
            customer_id=request.body["customer_id"],
            items=request.body["items"],
            shipping_address=request.body["shipping_address"],
        )
        result = self._command.create_order(command)
        return HttpResponse(status=201, body=result)

    def get_order(self, order_id: str) -> HttpResponse:
        result = self._query.get_order(order_id)
        return HttpResponse(status=200, body=result)
```

### 아웃바운드 어댑터 (Driven Adapter)

```python
class PostgresOrderRepository(OrderRepository):
    """PostgreSQL — 아웃바운드 어댑터
    도메인이 정의한 OrderRepository 포트를 구현한다.
    """

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def save(self, order: Order) -> None:
        with self._session_factory() as session:
            row = self._to_row(order)
            session.merge(row)
            session.commit()

    def find_by_id(self, order_id: str) -> Order | None:
        with self._session_factory() as session:
            row = session.get(OrderRow, order_id)
            return self._to_domain(row) if row else None

    def find_by_customer(self, customer_id: str) -> list[Order]:
        with self._session_factory() as session:
            rows = session.query(OrderRow).filter_by(
                customer_id=customer_id
            ).all()
            return [self._to_domain(row) for row in rows]


class StripePaymentGateway(PaymentGateway):
    """Stripe API — 아웃바운드 어댑터"""

    def charge(self, amount: Money, method: PaymentMethod) -> PaymentResult:
        response = stripe.PaymentIntent.create(
            amount=amount.cents,
            currency=amount.currency,
            payment_method=method.stripe_token,
        )
        return PaymentResult(
            success=response.status == "succeeded",
            reference=response.id,
        )

    def refund(self, payment_ref: str, amount: Money) -> RefundResult:
        response = stripe.Refund.create(
            payment_intent=payment_ref,
            amount=amount.cents,
        )
        return RefundResult(success=response.status == "succeeded")
```

## 의존성 주입 조합

```python
# 컴포지션 루트 — 애플리케이션 진입점에서 조립
session_factory = create_session_factory(DATABASE_URL)

order_repository = PostgresOrderRepository(session_factory)
payment_gateway = StripePaymentGateway()
inventory_checker = InventoryApiAdapter(INVENTORY_SERVICE_URL)
notification_sender = EmailNotificationAdapter(SMTP_CONFIG)

order_service = OrderService(
    repository=order_repository,
    payment=payment_gateway,
    inventory=inventory_checker,
    notification=notification_sender,
)

controller = OrderRestController(
    command_use_case=order_service,
    query_use_case=order_service,
)
```

## 포트/어댑터 전체 매핑

| 포트 (인터페이스) | 방향 | 어댑터 (구현) | 교체 가능 대안 |
|---|---|---|---|
| `OrderCommandUseCase` | 인바운드 | `OrderRestController`, `OrderGrpcHandler` | CLI, 테스트 하네스 |
| `OrderQueryUseCase` | 인바운드 | `OrderRestController` | GraphQL 어댑터 |
| `OrderRepository` | 아웃바운드 | `PostgresOrderRepository` | InMemoryOrderRepository (테스트) |
| `PaymentGateway` | 아웃바운드 | `StripePaymentGateway` | TossPaymentGateway, MockPayment |
| `InventoryChecker` | 아웃바운드 | `InventoryApiAdapter` | MockInventoryChecker (테스트) |
| `NotificationSender` | 아웃바운드 | `EmailNotificationAdapter` | SmsAdapter, MockNotification |

인바운드 어댑터는 포트를 **호출**하고, 아웃바운드 어댑터는 포트를 **구현**한다. 이 비대칭이 헥사고날 아키텍처의 핵심 구조이다.

---
> **관련 스킬 참조:**
> - 주문 애그리거트, 엔티티, 값 객체 설계 -> **architecture-ddd** 스킬
> - 주문 테이블 스키마, 인덱스 설계 -> **architecture-db** 스킬
> - 주문 REST API 엔드포인트 설계 -> **architecture-api** 스킬
> - Django ORM 기반 리포지토리 구현 -> **implementation-django** 스킬
> - Python 타입 힌트, 데이터클래스 컨벤션 -> **implementation-python** 스킬
