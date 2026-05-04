**[주요 내용]**

현재 `/private/tmp/dddjango-codex-eval` 디렉터리는 비어 있고 세션도 읽기 전용이라 실제 파일 수정은 적용하지 못했습니다. `config.toml`도 해당 위치에 없습니다. 주문 생성 로직은 아래 방향으로 리팩터링하면 됩니다: view/router는 HTTP 입출력만 맡고, 유스케이스는 application service로 이동합니다.

[Before]

```python
# orders/views.py
def create_order(request):
    data = json.loads(request.body)
    product = Product.objects.get(id=data["product_id"])
    if product.stock < data["quantity"]:
        return JsonResponse({"error": "out_of_stock"}, status=400)

    order = Order.objects.create(user=request.user)
    OrderLine.objects.create(
        order=order,
        product=product,
        quantity=data["quantity"],
        price=product.price,
    )
    product.stock -= data["quantity"]
    product.save()

    return JsonResponse({"order_id": order.id}, status=201)
```

[After]

```python
# orders/application/create_order.py
from dataclasses import dataclass
from django.db import transaction

class OutOfStockError(Exception):
    pass

@dataclass(frozen=True)
class CreateOrderCommand:
    user_id: int
    product_id: int
    quantity: int

class CreateOrderService:
    def __init__(self, product_model, order_model, order_line_model):
        self.product_model = product_model
        self.order_model = order_model
        self.order_line_model = order_line_model

    @transaction.atomic
    def execute(self, command: CreateOrderCommand) -> int:
        product = self.product_model.objects.select_for_update().get(
            id=command.product_id
        )

        if product.stock < command.quantity:
            raise OutOfStockError

        order = self.order_model.objects.create(user_id=command.user_id)
        self.order_line_model.objects.create(
            order=order,
            product=product,
            quantity=command.quantity,
            price=product.price,
        )

        product.stock -= command.quantity
        product.save(update_fields=["stock"])

        return order.id
```

```python
# orders/views.py
from django.http import JsonResponse
from .application.create_order import (
    CreateOrderCommand,
    CreateOrderService,
    OutOfStockError,
)
from .models import Order, OrderLine, Product

def create_order(request):
    payload = json.loads(request.body)

    service = CreateOrderService(Product, Order, OrderLine)

    try:
        order_id = service.execute(
            CreateOrderCommand(
                user_id=request.user.id,
                product_id=payload["product_id"],
                quantity=payload["quantity"],
            )
        )
    except OutOfStockError:
        return JsonResponse({"error": "out_of_stock"}, status=400)

    return JsonResponse({"order_id": order_id}, status=201)
```

[Reason] Clean Code / Application Service  
view는 JSON 파싱, command 생성, HTTP 응답 변환만 담당합니다. 재고 확인, 주문 생성, 주문 라인 생성, 재고 차감, 트랜잭션 경계는 하나의 유스케이스이므로 `CreateOrderService.execute()`에 모읍니다. 이렇게 하면 view 테스트 없이도 주문 생성 규칙을 단위 테스트할 수 있고, view가 Django HTTP 어댑터 역할로 얇아집니다.

작은 리팩터링 순서:

1. 기존 view의 주문 생성 블록을 그대로 `CreateOrderService.execute()`로 이동합니다.
2. request/payload 의존을 `CreateOrderCommand`로 끊습니다.
3. `return JsonResponse({"error": ...})` 같은 흐름 제어를 도메인/application 예외로 바꿉니다.
4. 트랜잭션은 view가 아니라 service 메서드에 둡니다.
5. 이후 필요하면 `ProductRepository`, `OrderRepository` 포트로 ORM 의존을 더 분리합니다.

검증 단계:

```bash
python manage.py test orders
```

추가해야 할 핵심 테스트:

```python
def test_create_order_decreases_stock(db, user, product):
    service = CreateOrderService(Product, Order, OrderLine)

    order_id = service.execute(
        CreateOrderCommand(
            user_id=user.id,
            product_id=product.id,
            quantity=2,
        )
    )

    product.refresh_from_db()
    assert Order.objects.filter(id=order_id, user=user).exists()
    assert product.stock == 8
```

```python
def test_create_order_fails_when_stock_is_not_enough(db, user, product):
    service = CreateOrderService(Product, Order, OrderLine)

    with pytest.raises(OutOfStockError):
        service.execute(
            CreateOrderCommand(
                user_id=user.id,
                product_id=product.id,
                quantity=999,
            )
        )
```

---
> **관련 스킬 참조:**
> - Django application service 리팩터링 → **architecture-implementation-patterns** 스킬