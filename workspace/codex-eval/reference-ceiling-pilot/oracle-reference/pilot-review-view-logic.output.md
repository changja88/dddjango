**Findings**

1. **[Critical: Thin Ninja Boundary]** -- 주문 생성 로직을 Django Ninja endpoint/view에 모두 넣는 것은 비권장입니다. 주문 생성은 보통 요청 검증, 가격 스냅샷, 재고 예약/차감, 쿠폰/포인트, 결제 준비, 이벤트/알림, 멱등성, 트랜잭션을 함께 다룹니다. 이 로직이 view에 있으면 API 입출력 변경과 도메인 규칙 변경이 같은 파일을 흔들고, 서비스 테스트 없이 HTTP 테스트만 남아 회귀 비용이 커집니다.
   예외는 “한 모델 create + 부수효과 없음 + 불변식 거의 없음” 수준의 단순 CRUD입니다. 주문 생성은 그 예외에 들어가기 어렵습니다.

2. **[Critical: Transaction Boundary]** -- view 안에서 `Order.objects.create()`, `OrderLine.objects.create()`, 재고 차감, 결제/알림 호출을 순서대로 실행하면 partial write와 롤백 누락 위험이 큽니다. 최소한 application service가 `transaction.atomic()` 경계를 잡고, 외부 부수효과는 `transaction.on_commit()` 뒤로 밀어야 합니다. 통합 이벤트가 유실되면 안 되는 경로라면 `on_commit()`만으로 부족하고 Outbox가 맞습니다.

3. **[High: Idempotency]** -- 주문 생성 `POST /orders/`는 사용자 더블 클릭, 모바일 재시도, 네트워크 타임아웃으로 중복 생성되기 쉽습니다. `Idempotency-Key`를 endpoint에서 받고, service에서 `(user_id, key)` unique record로 처리해야 합니다. 이미 성공한 키면 같은 응답을 반환하고, 처리 중인 키면 `409 Conflict` 또는 팀 표준 상태를 반환합니다.

4. **[High: DDD Boundary]** -- view가 “재고 가능 여부 판단”, “주문 가능 상태”, “총액 계산”, “배송지 변경 가능 여부” 같은 규칙을 직접 실행하면 애그리거트 불변식이 API 레이어로 샙니다. `Order`는 애그리거트 루트이고, 주문 라인/배송 정보/금액 스냅샷의 불변식은 모델/도메인 메서드 쪽에 두는 편이 맞습니다. service는 유스케이스 조율자여야 하고, 도메인 규칙의 본체가 되면 안 됩니다.

5. **[Medium: N+1 / Locking]** -- view에서 요청 line item을 돌며 `Product.objects.get()` 또는 `Inventory.objects.get()`을 반복하면 N+1과 동시성 버그가 같이 납니다. 상품/재고는 `id__in`으로 한 번에 읽고, 재고 차감이 있으면 `select_for_update()` 또는 DB 제약/F expression 기반 업데이트를 검토해야 합니다. 회귀 테스트에는 `assertNumQueries`를 넣는 게 좋습니다.

6. **[Medium: Error Contract]** -- Ninja 기본 validation error, `HttpError`, 도메인 예외 응답이 섞이면 클라이언트가 오류를 안정적으로 처리하기 어렵습니다. 주문 생성에서는 `422` validation, `409` idempotency/conflict, `400` business rule, `401/403` auth/authz를 RFC 9457 Problem Details 형식으로 통일하는 편이 낫습니다.

**최소 수정 방향**

파일 단위로는 이 정도가 적정합니다.

- `orders/api/schemas.py`: Ninja `Schema`로 요청/응답만 정의
- `orders/api/router.py`: 인증, idempotency header 수신, service 호출, 예외 매핑만 담당
- `orders/application/services.py`: `create_order()` 유스케이스, `transaction.atomic()`, idempotency, repository/query orchestration
- `orders/domain/models.py` 또는 Django model methods: 주문 불변식, 총액 계산, 상태 전이
- `orders/api/errors.py`: Problem Details 응답/exception handler
- `orders/tests/`: service 테스트, API error contract 테스트, idempotency/concurrency 테스트, query count 테스트

**Compact Sketch**

```python
# orders/api/schemas.py
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class OrderLineIn(Schema):
    product_id: UUID
    quantity: int


class CreateOrderIn(Schema):
    lines: list[OrderLineIn]
    shipping_address_id: UUID


class OrderOut(Schema):
    id: UUID
    status: str
    total_amount: Decimal
```

```python
# orders/api/router.py
from django.http import HttpRequest
from ninja import Header, Router

from orders.api.schemas import CreateOrderIn, OrderOut
from orders.application.services import CreateOrderCommand, OrderApplicationService
from orders.domain.exceptions import InsufficientStock, IdempotencyConflict

router = Router(tags=["orders"])


@router.post("/", response={201: OrderOut}, by_alias=True)
def create_order(
    request: HttpRequest,
    payload: CreateOrderIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> tuple[int, OrderOut]:
    command = CreateOrderCommand(
        user_id=request.user.id,
        idempotency_key=idempotency_key,
        lines=payload.lines,
        shipping_address_id=payload.shipping_address_id,
    )
    order = OrderApplicationService().create_order(command)
    return 201, order
```

```python
# orders/application/services.py
from dataclasses import dataclass
from uuid import UUID

from django.db import IntegrityError, transaction

from orders.models import IdempotencyRecord, InventoryItem, Order, Product


@dataclass(frozen=True)
class CreateOrderCommand:
    user_id: int
    idempotency_key: str
    lines: list
    shipping_address_id: UUID


class OrderApplicationService:
    @transaction.atomic
    def create_order(self, command: CreateOrderCommand) -> Order:
        record, created = IdempotencyRecord.objects.get_or_create(
            user_id=command.user_id,
            key=command.idempotency_key,
            defaults={"status": IdempotencyRecord.Status.PROCESSING},
        )
        if not created:
            return record.replay_or_raise_conflict()

        product_ids = [line.product_id for line in command.lines]
        products = Product.objects.in_bulk(product_ids)

        inventory_by_product_id = {
            item.product_id: item
            for item in InventoryItem.objects.select_for_update().filter(
                product_id__in=product_ids
            )
        }

        order = Order.place(
            user_id=command.user_id,
            lines=command.lines,
            products=products,
            inventory_by_product_id=inventory_by_product_id,
            shipping_address_id=command.shipping_address_id,
        )
        order.save_with_lines()

        record.mark_succeeded(order_id=order.id, response_snapshot=OrderOut.from_orm(order).dict())
        record.save(update_fields=["status", "order_id", "response_snapshot", "updated_at"])

        transaction.on_commit(lambda: send_order_created_notification.delay(order.id))
        return order
```

```python
# orders/api/errors.py
from django.http import HttpRequest
from ninja import NinjaAPI

api = NinjaAPI()


def problem(status: int, title: str, detail: str, type_: str, instance: str):
    return api.create_response(
        None,
        {
            "type": type_,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": instance,
        },
        status=status,
        content_type="application/problem+json",
    )


@api.exception_handler(InsufficientStock)
def insufficient_stock_handler(request: HttpRequest, exc: InsufficientStock):
    return problem(
        409,
        "Insufficient stock",
        str(exc),
        "https://api.example.com/problems/insufficient-stock",
        request.path,
    )


@api.exception_handler(IdempotencyConflict)
def idempotency_conflict_handler(request: HttpRequest, exc: IdempotencyConflict):
    return problem(
        409,
        "Idempotency conflict",
        str(exc),
        "https://api.example.com/problems/idempotency-conflict",
        request.path,
    )
```

**Ubiquitous Language**

| 도메인 용어 | 코드 표현 | 금지할 표현 |
|---|---|---|
| 주문 생성 | `Order.place()` / `create_order()` | `make_order`, `insert_order` |
| 재고 예약 | `InventoryItem.reserve()` | `minus_stock` |
| 주문 생성됨 | `OrderPlaced` | `OrderCreatedSignal` |

**테스트 누락 체크**

서비스 레이어 없이 view만 테스트하면 핵심 경로가 과하게 HTTP에 묶입니다. 최소 테스트는 다음이 필요합니다: 정상 주문 생성, 재고 부족 `409 problem+json`, 같은 `Idempotency-Key` 재시도 시 같은 응답, 다른 payload로 같은 키 재사용 시 conflict, 상품/재고 조회 query count, 동시 재고 차감 race 방지.

결론은 “절대 안 된다”가 아니라 “주문 생성처럼 불변식과 부수효과가 있는 use case는 view에 넣지 않는 쪽이 맞다”입니다. Ninja endpoint는 얇게 두고, application service가 트랜잭션과 멱등성을 조율하며, 도메인 규칙은 `Order`/`InventoryItem` 쪽으로 내리는 구성이 최소한의 분리입니다.

---
> **관련 스킬 참조:**
> - API error/idempotency 설계 → **architecture-api** 스킬
> - 주문 Aggregate/도메인 이벤트 → **architecture-ddd** 스킬
> - Django transaction/query 최적화 → **implementation-django** 스킬
> - Django Ninja endpoint/schema/error handler → **implementation-django-ninja** 스킬