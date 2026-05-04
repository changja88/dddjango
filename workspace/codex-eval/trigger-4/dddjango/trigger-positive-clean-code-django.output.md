작업 디렉터리 `/private/tmp/dddjango-codex-eval`가 비어 있고 `config.toml`도 없어서 실제 파일 수정은 적용하지 못했습니다. 대신 Django view 안의 주문 생성 로직을 얇은 view + application service 구조로 옮기는 최소 리팩터링안을 남깁니다. 실제 코드가 들어오면 이 형태로 바로 패치하면 됩니다.

**[주요 내용]**

[Before]

```python
# orders/views.py
def create_order(request):
    data = json.loads(request.body)
    items = data["items"]

    if not items:
        return JsonResponse({"error": "empty items"}, status=400)

    total_price = 0
    order = Order.objects.create(user=request.user, status="created")

    for item in items:
        product = Product.objects.get(id=item["product_id"])
        if product.stock < item["quantity"]:
            return JsonResponse({"error": "not enough stock"}, status=400)

        product.stock -= item["quantity"]
        product.save(update_fields=["stock"])

        OrderLine.objects.create(
            order=order,
            product=product,
            quantity=item["quantity"],
            price=product.price,
        )
        total_price += product.price * item["quantity"]

    order.total_price = total_price
    order.save(update_fields=["total_price"])

    return JsonResponse({"order_id": order.id}, status=201)
```

[After]

```python
# orders/application/create_order.py
from dataclasses import dataclass
from django.db import transaction

class EmptyOrderError(Exception):
    pass

class InsufficientStockError(Exception):
    pass

@dataclass(frozen=True)
class CreateOrderLineCommand:
    product_id: int
    quantity: int

@dataclass(frozen=True)
class CreateOrderCommand:
    user_id: int
    lines: list[CreateOrderLineCommand]

class CreateOrderService:
    @transaction.atomic
    def execute(self, command: CreateOrderCommand) -> int:
        if not command.lines:
            raise EmptyOrderError()

        order = Order.objects.create(user_id=command.user_id, status=Order.Status.CREATED)
        total_price = 0

        for line in command.lines:
            product = Product.objects.select_for_update().get(id=line.product_id)
            if product.stock < line.quantity:
                raise InsufficientStockError()

            product.decrease_stock(line.quantity)
            product.save(update_fields=["stock"])

            OrderLine.objects.create(
                order=order,
                product=product,
                quantity=line.quantity,
                price=product.price,
            )
            total_price += product.price * line.quantity

        order.total_price = total_price
        order.save(update_fields=["total_price"])
        return order.id
```

```python
# orders/views.py
from django.http import JsonResponse
from .application.create_order import (
    CreateOrderCommand,
    CreateOrderLineCommand,
    CreateOrderService,
    EmptyOrderError,
    InsufficientStockError,
)

def create_order(request):
    payload = json.loads(request.body)
    command = CreateOrderCommand(
        user_id=request.user.id,
        lines=[
            CreateOrderLineCommand(
                product_id=line["product_id"],
                quantity=line["quantity"],
            )
            for line in payload.get("items", [])
        ],
    )

    try:
        order_id = CreateOrderService().execute(command)
    except EmptyOrderError:
        return JsonResponse({"error": "empty items"}, status=400)
    except InsufficientStockError:
        return JsonResponse({"error": "not enough stock"}, status=400)

    return JsonResponse({"order_id": order_id}, status=201)
```

```python
# orders/models.py
class Product(models.Model):
    # ...

    def decrease_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.stock < quantity:
            raise InsufficientStockError()
        self.stock -= quantity
```

[Reason] Clean Code / Application Service  
view는 HTTP 입력 변환과 HTTP 응답 변환만 담당합니다. 주문 생성 유스케이스, 트랜잭션, 재고 차감, 총액 계산은 `CreateOrderService.execute()`로 이동합니다. 함수의 추상화 수준이 섞이지 않고 테스트 대상도 명확해집니다.

[Reason] DDD  
`Order`가 Aggregate Root 후보이고, `Product` 재고 차감은 도메인 행위입니다. 재고 차감 규칙을 view에 두지 않고 `product.decrease_stock()`로 이동하면 Tell-Don’t-Ask에 가까워집니다. 다만 실제 모델 구조를 보기 전에는 Repository/UoW까지 도입하지 않는 편이 낫습니다.

**작은 리팩터링 순서**

1. 기존 view 테스트를 먼저 고정합니다: 성공, 빈 장바구니, 재고 부족.
2. `CreateOrderCommand`와 `CreateOrderService`를 추가하고 view 로직을 그대로 이동합니다.
3. view는 command 생성, service 호출, 예외를 HTTP 응답으로 매핑하는 역할만 남깁니다.
4. `Product.decrease_stock()`처럼 도메인 규칙을 모델 메서드로 한 단계 더 이동합니다.
5. 동시 주문 위험이 있으면 `select_for_update()` 또는 낙관적 잠금을 별도 단계로 검증합니다.

**검증 단계**

```bash
python manage.py test orders
python manage.py test
```

추가해야 할 핵심 테스트:

```python
def test_create_order_returns_201(client, product):
    ...

def test_create_order_rejects_empty_items(client):
    ...

def test_create_order_rejects_insufficient_stock(client, product):
    ...
```

---
> **관련 스킬 참조:**
> - Django application service 분리 → **architecture-implementation-patterns** 스킬
> - 주문 Aggregate / 재고 불변식 정리 → **architecture-ddd** 스킬
> - view 함수 단순화와 예외 흐름 정리 → **implementation-cleancode** 스킬