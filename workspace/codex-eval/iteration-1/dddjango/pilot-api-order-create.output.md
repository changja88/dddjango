**주요 내용**

전략적 경계는 이렇게 나눕니다.

| Context | 책임 | 금지 동의어 |
|---|---|---|
| Ordering | 주문 생성, 주문 금액 계산, 주문 상태 | `cart`, `purchase` |
| Inventory | 판매 가능 재고 확인/예약 | `stock_count` 직접 수정 |
| Payment | 결제 준비, payment intent 생성 | `charge`, 즉시 승인 |

주문 생성은 `POST /v1/orders`입니다. 결제 준비는 주문 생성 유스케이스의 일부지만, 결제 승인/capture는 별도 API로 분리합니다. `POST`이므로 `Idempotency-Key` 헤더를 필수로 받아 중복 주문/중복 결제 준비를 막습니다.

핵심 흐름:

1. `Idempotency-Key`로 기존 성공 응답 확인
2. DB 트랜잭션 시작
3. 상품 row를 `select_for_update()`로 잠금
4. 재고 확인 및 예약
5. 주문 금액 계산
6. `PENDING_PAYMENT` 주문 저장
7. idempotency record 저장
8. 커밋 후 `PaymentPort.prepare()` 호출
9. payment intent 정보를 주문에 연결하고 응답

외부 결제 호출은 DB 트랜잭션 안에서 하지 않습니다. 트랜잭션은 로컬 불변식, 즉 “재고는 음수가 될 수 없다”, “주문 금액은 주문 항목 가격 합계와 일치한다”까지만 보호합니다.

```python
# apps/orders/domain/repositories.py
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: "Order") -> None: ...
```

```python
# apps/orders/domain/values.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidOrderAmount("amount must be non-negative")
```

```python
# apps/orders/domain/order.py
class Order:
    """Aggregate Root.
    Invariants:
    - total_amount equals sum(line.unit_price * line.quantity)
    - order starts as PENDING_PAYMENT after stock reservation
    - payment preparation does not mark the order as paid
    """

    @classmethod
    def create(cls, *, customer_id, lines) -> "Order":
        total = Money(sum(line.unit_price.amount * line.quantity for line in lines))
        return cls(customer_id=customer_id, lines=lines, total_amount=total)
```

```python
# apps/payments/ports.py
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class PaymentPreparation:
    provider_payment_id: str
    client_secret: str

class PaymentPort(Protocol):
    def prepare(
        self,
        *,
        order_id: str,
        amount: int,
        currency: str,
        idempotency_key: str,
    ) -> PaymentPreparation: ...
```

```python
# apps/orders/api/schemas.py
from ninja import Schema

class OrderLineIn(Schema):
    product_id: int
    quantity: int

class CreateOrderIn(Schema):
    lines: list[OrderLineIn]

class PaymentOut(Schema):
    provider_payment_id: str
    client_secret: str

class OrderCreatedOut(Schema):
    order_id: str
    status: str
    total_amount: int
    currency: str
    payment: PaymentOut
```

```python
# apps/orders/application/services.py
from django.db import transaction

class CreateOrderService:
    def __init__(self, payment_port: PaymentPort):
        self.payment_port = payment_port

    def create(self, *, customer_id: int, data: CreateOrderIn, idem_key: str):
        cached = IdempotencyRecord.objects.find_response(idem_key)
        if cached:
            return cached

        with transaction.atomic():
            products = (
                Product.objects
                .select_for_update()
                .filter(id__in=[line.product_id for line in data.lines])
            )
            product_map = {p.id: p for p in products}

            order_lines = []
            for line in data.lines:
                product = product_map.get(line.product_id)
                if product is None:
                    raise ProductNotFound()
                if product.available_quantity < line.quantity:
                    raise InsufficientStock()

                product.available_quantity -= line.quantity
                product.save(update_fields=["available_quantity"])

                order_lines.append(
                    OrderLineDraft(
                        product_id=product.id,
                        quantity=line.quantity,
                        unit_price=Money(product.price),
                    )
                )

            order = Order.create(customer_id=customer_id, lines=order_lines)
            order_model = OrderModel.objects.create_from_domain(order)

            IdempotencyRecord.objects.create_pending(
                key=idem_key,
                resource_id=order_model.id,
            )

        payment = self.payment_port.prepare(
            order_id=str(order_model.id),
            amount=order.total_amount.amount,
            currency=order.total_amount.currency,
            idempotency_key=f"order:{order_model.id}:{idem_key}",
        )

        OrderModel.objects.filter(id=order_model.id).update(
            provider_payment_id=payment.provider_payment_id,
        )

        response = OrderCreatedOut(
            order_id=str(order_model.id),
            status="PENDING_PAYMENT",
            total_amount=order.total_amount.amount,
            currency=order.total_amount.currency,
            payment=payment,
        )
        IdempotencyRecord.objects.save_response(idem_key, response)
        return response
```

```python
# apps/orders/api/router.py
from ninja import Header, Router
from ninja.security import django_auth

router = Router(tags=["orders"], auth=django_auth)

@router.post("", response={201: OrderCreatedOut})
def create_order(
    request,
    payload: CreateOrderIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    service = CreateOrderService(payment_port=payment_gateway())
    return 201, service.create(
        customer_id=request.user.id,
        data=payload,
        idem_key=idempotency_key,
    )
```

오류는 RFC 9457 Problem Details로 통일합니다.

| 상황 | HTTP |
|---|---:|
| 재고 부족 | `409 Conflict` |
| 상품 없음 | `404 Not Found` |
| 잘못된 수량/빈 주문 | `422 Unprocessable Content` |
| idempotency key 누락 | `400 Bad Request` |
| 결제 준비 실패 | `502 Bad Gateway` 또는 재시도 가능한 `202 Accepted` |

---
> **관련 스킬 참조:**
> - 트랜잭션/인덱스/락 상세 설계 → **architecture-db** 스킬
> - 실제 Django Ninja 구현/테스트 작성 → **implementation-django-ninja** 스킬