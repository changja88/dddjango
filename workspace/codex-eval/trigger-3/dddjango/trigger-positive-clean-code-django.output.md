**[주요 내용]**

현재 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있고, 세션도 읽기 전용이라 실제 파일 수정은 할 수 없었습니다. 적용 방향은 Django view의 “요청/응답 변환”만 남기고, 주문 생성 유스케이스를 application service로 이동하는 것입니다.

작은 단계로는 이렇게 나눕니다.

1. `views.py`에서 주문 생성 검증/계산/DB 저장 로직 식별
2. `application/services.py`에 `CreateOrderService` 생성
3. view는 serializer/form 검증 후 command DTO를 service에 전달
4. service 단위 테스트 추가
5. view 테스트는 “service 호출 + HTTP 응답”만 검증

핵심 구조는 아래처럼 가져가면 됩니다.

```python
# orders/application/commands.py
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderLineCommand:
    product_id: int
    quantity: int


@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: int
    lines: tuple[CreateOrderLineCommand, ...]
```

```python
# orders/application/services.py
from django.db import transaction

from orders.application.commands import CreateOrderCommand
from orders.models import Order, OrderLine, Product


class EmptyOrderError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class CreateOrderService:
    @transaction.atomic
    def create(self, command: CreateOrderCommand) -> Order:
        if not command.lines:
            raise EmptyOrderError("주문 항목은 최소 1개 이상이어야 합니다.")

        products = Product.objects.in_bulk(
            [line.product_id for line in command.lines]
        )

        missing_ids = {
            line.product_id
            for line in command.lines
            if line.product_id not in products
        }
        if missing_ids:
            raise ProductNotFoundError(f"존재하지 않는 상품입니다: {sorted(missing_ids)}")

        order = Order.objects.create(customer_id=command.customer_id)

        order_lines = [
            OrderLine(
                order=order,
                product=products[line.product_id],
                quantity=line.quantity,
                unit_price=products[line.product_id].price,
            )
            for line in command.lines
        ]
        OrderLine.objects.bulk_create(order_lines)

        return order
```

```python
# orders/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from orders.application.commands import CreateOrderCommand, CreateOrderLineCommand
from orders.application.services import (
    CreateOrderService,
    EmptyOrderError,
    ProductNotFoundError,
)


@require_POST
def create_order(request):
    payload = request.json

    command = CreateOrderCommand(
        customer_id=request.user.id,
        lines=tuple(
            CreateOrderLineCommand(
                product_id=item["product_id"],
                quantity=item["quantity"],
            )
            for item in payload.get("lines", [])
        ),
    )

    try:
        order = CreateOrderService().create(command)
    except EmptyOrderError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except ProductNotFoundError as exc:
        return JsonResponse({"error": str(exc)}, status=404)

    return JsonResponse({"order_id": order.id}, status=201)
```

리팩터링 이유는 명확합니다.

| 변경 | 이유 |
|---|---|
| view에서 주문 생성 로직 제거 | view/router는 HTTP 어댑터로 얇게 유지 |
| `CreateOrderCommand` 도입 | request 구조가 application 계층으로 새지 않게 함 |
| `CreateOrderService.create()` 도입 | 주문 생성 유스케이스와 트랜잭션 경계를 한 곳에 둠 |
| 도메인 예외 분리 | HTTP status 결정은 view, 비즈니스 실패 표현은 service가 담당 |

검증은 이 순서로 하면 됩니다.

```bash
python manage.py test orders.tests.test_create_order_service
python manage.py test orders.tests.test_create_order_view
python manage.py test orders
```

테스트는 먼저 service 중심으로 작성하세요. 예: 빈 주문이면 `EmptyOrderError`, 없는 상품이면 `ProductNotFoundError`, 정상 주문이면 `Order`와 `OrderLine`이 생성되는지 검증합니다. view 테스트는 payload를 보내고 status code와 응답 shape만 확인하면 충분합니다.

Ubiquitous Language는 최소한 이렇게 고정합니다.

| 도메인 용어 | 코드 표현 | 금지 동의어 |
|---|---|---|
| 주문 생성 | `CreateOrderService.create` | `post`, `save_request` |
| 주문 항목 | `CreateOrderLineCommand` | `item_dict`, `payload_item` |
| 단가 | `unit_price` | `price_snapshot`, `raw_price` |

---
> **관련 스킬 참조:**
> - Django service 계층 구체화 → **implementation-django** 스킬
> - 주문 애그리거트/값 객체 확장 → **architecture-ddd** 스킬