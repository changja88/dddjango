**주요 내용**

커머스에서 `주문`, `결제`, `배송`, `정산`은 “테이블이 달라서”가 아니라 **유비쿼터스 언어, 불변식, 상태 전이, 트랜잭션 경계, 외부 시스템 책임**이 달라지는 지점에서 나누는 것이 좋습니다.

| Bounded Context | 핵심 질문 | 소유하는 모델 | 소유하지 않는 것 |
|---|---|---|---|
| Ordering | 고객이 무엇을 어떤 조건으로 구매했는가? | `Order`, `OrderLine`, `OrderStatus`, 주문 취소/확정 규칙 | 카드 승인, 송장, 판매자 지급액 |
| Payments | 돈을 받을 수 있는가, 받았는가, 돌려줬는가? | `Payment`, `PaymentAttempt`, `Refund`, `PaymentStatus` | 주문 상품 구성, 배송 완료 판정, 정산 계산 |
| Shipments | 상품을 어떻게 출고하고 배송 추적할 것인가? | `Shipment`, `TrackingNumber`, `Carrier`, `DeliveryStatus` | 결제 승인, 주문 금액 계산, 판매자 정산 |
| Settlements | 판매자/입점사에게 얼마를 언제 지급할 것인가? | `Settlement`, `SettlementLine`, `Fee`, `PayoutStatus` | 고객 주문 상태 전이, PG 승인, 택배사 상태 원본 |

가장 중요한 분리 기준은 다음입니다.

1. **같은 단어가 다른 의미를 가지면 분리합니다.**  
   `완료`는 주문에서는 “구매 프로세스 종료”, 결제에서는 “매입/캡처 완료”, 배송에서는 “고객 수령”, 정산에서는 “판매자 지급 완료”입니다. 같은 `completed`라도 의미가 다릅니다.

2. **강한 일관성이 필요한 범위만 하나의 애그리거트로 둡니다.**  
   주문 생성 시 “주문 라인이 최소 1개여야 한다”, “주문 총액은 주문 라인의 합과 같아야 한다”는 Ordering 내부 불변식입니다. 반면 “결제 성공 후 배송 요청 생성”은 다른 컨텍스트 간 결과적 일관성으로 처리해도 됩니다.

3. **상태 전이 주체가 다르면 분리합니다.**  
   주문은 고객/커머스 정책이 바꾸고, 결제는 PG 응답과 환불 정책이 바꾸고, 배송은 물류/택배 이벤트가 바꾸고, 정산은 회계 마감 정책이 바꿉니다.

4. **외부 시스템 모델이 강하게 섞이면 ACL을 둡니다.**  
   PG사의 `tid`, `auth_code`, 택배사의 `invoice_no`, ERP의 `vendor_code` 같은 언어가 주문 모델로 침투하지 않게 `payments.acl`, `shipments.acl`, `settlements.acl`에서 내부 모델로 번역합니다.

5. **트랜잭션 경계는 컨텍스트 내부로 제한합니다.**  
   주문 확정과 결제 승인, 배송 생성, 정산 예정 생성까지 한 DB 트랜잭션으로 묶으면 결합도가 급격히 커집니다. Ordering은 `OrderPlacedEvent`, Payments는 `PaymentCapturedEvent`를 발행하고 후속 컨텍스트가 구독하는 구조가 낫습니다.

권장 컨텍스트 맵은 이렇습니다.

```text
Ordering
  -> publishes OrderPlacedEvent
  -> Payments consumes

Payments
  -> publishes PaymentCapturedEvent, PaymentRefundedEvent
  -> Ordering consumes for order state
  -> Shipments consumes to prepare shipment
  -> Settlements consumes as payable/refundable fact

Shipments
  -> publishes ShipmentDispatchedEvent, ShipmentDeliveredEvent
  -> Ordering consumes for customer-visible order progress
  -> Settlements consumes delivery-completed settlement trigger

Settlements
  -> consumes PaymentCapturedEvent, PaymentRefundedEvent, ShipmentDeliveredEvent
  -> publishes SettlementCalculatedEvent, SettlementPaidEvent
```

예시 유비쿼터스 언어는 명시적으로 분리합니다.

| 용어 | Ordering | Payments | Shipments | Settlements | 금지 동의어 |
|---|---|---|---|---|---|
| 완료 | 주문 종료 | 결제 캡처/환불 완료 | 배송 완료 | 지급 완료 | `done`, `complete` 단독 사용 |
| 금액 | 주문 총액 | 승인/매입/환불 금액 | 배송비 | 지급 대상 금액 | `price`, `amount` 혼용 |
| 취소 | 주문 취소 | 승인 취소/환불 | 배송 취소 | 정산 제외/차감 | `delete`, `rollback` |
| 상태 | 주문 상태 | 결제 상태 | 배송 상태 | 지급 상태 | 공통 `status` 의미 공유 |

전술 설계는 작게 가져갑니다.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("금액은 음수일 수 없습니다")
        if not self.currency:
            raise ValueError("통화는 필수입니다")


@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: str
    customer_id: str
    total: Money


@dataclass
class Order:
    """Aggregate Root: Order

    불변식:
    - 주문 라인은 최소 1개 이상이어야 한다.
    - 주문 총액은 주문 라인 금액 합계와 일치해야 한다.
    - 결제 완료 전에는 출고 요청 상태로 넘어갈 수 없다.
    """

    id: str
    customer_id: str
    total: Money
    status: str

    def confirm(self) -> OrderPlacedEvent:
        if self.status != "draft":
            raise ValueError("draft 상태의 주문만 확정할 수 있습니다")
        self.status = "placed"
        return OrderPlacedEvent(
            order_id=self.id,
            customer_id=self.customer_id,
            total=self.total,
        )


class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...


class OrderApplicationService:
    def __init__(self, orders: OrderRepository) -> None:
        self.orders = orders

    def place_order(self, order_id: str) -> OrderPlacedEvent:
        order = self.orders.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        event = order.confirm()
        self.orders.save(order)
        return event
```

Django 프로젝트 구조는 bounded context를 앱으로 나누되, Django 앱 내부에서 `domain`, `application`, `infra`, `api`를 분리하는 식이 실용적입니다. API는 이 프로젝트 기준상 DRF가 아니라 **Django Ninja Schema/Router**를 사용합니다.

```text
repository_root/
    manage.py
    config/
        settings/
            base.py
            local.py
            production.py
            test.py
        urls.py
        asgi.py
        wsgi.py

    apps/
        orders/
            domain/
                models.py
                events.py
                value_objects.py
                repositories.py
            application/
                services.py
                handlers.py
            infra/
                django_models.py
                repositories.py
            api/
                schemas.py
                router.py
            admin.py
            apps.py

        payments/
            domain/
                models.py
                events.py
                value_objects.py
                repositories.py
            application/
                services.py
                handlers.py
            infra/
                django_models.py
                repositories.py
                pg_client.py
                acl.py
            api/
                schemas.py
                router.py

        shipments/
            domain/
                models.py
                events.py
                value_objects.py
                repositories.py
            application/
                services.py
                handlers.py
            infra/
                django_models.py
                repositories.py
                carrier_client.py
                acl.py
            api/
                schemas.py
                router.py

        settlements/
            domain/
                models.py
                events.py
                value_objects.py
                repositories.py
            application/
                services.py
                handlers.py
            infra/
                django_models.py
                repositories.py
                erp_client.py
                acl.py
            api/
                schemas.py
                router.py

        shared/
            domain/
                money.py
                ids.py
            events/
                bus.py
```

주의할 점은 `shared`를 크게 만들지 않는 것입니다. `Money`, `CustomerId`, `OrderId` 같은 안정적인 값 객체나 이벤트 버스 추상화 정도만 두고, 주문/결제/배송/정산의 상태와 정책을 `shared`로 올리면 다시 큰 진흙공이 됩니다.

초기 MVP라면 네 컨텍스트를 물리적으로 한 Django 프로젝트 안에 두되, **앱 간 직접 모델 import를 금지하고 ID와 이벤트로만 연결**하는 방식을 추천합니다. 이후 결제나 배송처럼 외부 장애 전파가 큰 컨텍스트부터 별도 서비스로 분리할 수 있습니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 설계 → **implementation-django-ninja** 스킬
> - DB 테이블/인덱스/트랜잭션 설계 → **architecture-db** 스킬
> - 이벤트 기반 연동/헥사고날 구조 → **architecture-implementation-patterns** 스킬