현재 `/private/tmp/dddjango-codex-eval`에는 Django 프로젝트 파일이 없고 읽기 전용 환경이라 실제 패치는 적용하지 못했습니다. 대신 기존 view의 주문 생성 로직을 아래 구조로 옮기면 됩니다.

**[Before]**
```python
# orders/views.py

@login_required
def create_order(request):
    if request.method == "POST":
        data = request.POST
        order = Order.objects.create(user=request.user)

        for item in data.getlist("items"):
            product = Product.objects.get(id=item["product_id"])
            if product.stock < item["quantity"]:
                messages.error(request, "재고가 부족합니다.")
                return redirect("orders:create")

            product.stock -= item["quantity"]
            product.save()

            OrderLine.objects.create(
                order=order,
                product=product,
                quantity=item["quantity"],
                price=product.price,
            )

        send_order_email(order.id)
        return redirect("orders:detail", pk=order.id)

    return render(request, "orders/create.html")
```

**[After]**
```python
# orders/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CreateOrderForm
from .services import OrderCreationError, place_order


@login_required
@require_POST
def create_order(request):
    form = CreateOrderForm(request.POST)

    if not form.is_valid():
        return render(request, "orders/create.html", {"form": form})

    try:
        result = place_order(form.to_command(user=request.user))
    except OrderCreationError as exc:
        form.add_error(None, str(exc))
        return render(request, "orders/create.html", {"form": form})

    return redirect("orders:detail", pk=result.order_id)
```

```python
# orders/services.py

from dataclasses import dataclass

from django.db import transaction

from .models import Order, OrderLine, Product
from .tasks import send_order_confirmation


class OrderCreationError(Exception):
    pass


class EmptyOrder(OrderCreationError):
    pass


class ProductUnavailable(OrderCreationError):
    pass


@dataclass(frozen=True)
class OrderLineInput:
    product_id: int
    quantity: int


@dataclass(frozen=True)
class CreateOrderCommand:
    user_id: int
    lines: tuple[OrderLineInput, ...]


@dataclass(frozen=True)
class PlacedOrder:
    order_id: int


def place_order(command: CreateOrderCommand) -> PlacedOrder:
    if not command.lines:
        raise EmptyOrder("주문 항목이 없습니다.")

    with transaction.atomic():
        products = _get_locked_products(command.lines)
        order = Order.objects.create(user_id=command.user_id)

        order_lines = [
            _build_order_line(order, products[line.product_id], line)
            for line in command.lines
        ]

        OrderLine.objects.bulk_create(order_lines)
        _decrease_stock(products, command.lines)

        transaction.on_commit(
            lambda: send_order_confirmation.delay(order.id)
        )

    return PlacedOrder(order_id=order.id)


def _get_locked_products(lines: tuple[OrderLineInput, ...]) -> dict[int, Product]:
    product_ids = {line.product_id for line in lines}

    products = Product.objects.select_for_update().in_bulk(product_ids)

    if len(products) != len(product_ids):
        raise ProductUnavailable("구매할 수 없는 상품이 포함되어 있습니다.")

    return products


def _build_order_line(
    order: Order,
    product: Product,
    line: OrderLineInput,
) -> OrderLine:
    if product.stock < line.quantity:
        raise ProductUnavailable(f"{product.name} 재고가 부족합니다.")

    return OrderLine(
        order=order,
        product=product,
        quantity=line.quantity,
        unit_price=product.price,
    )


def _decrease_stock(
    products: dict[int, Product],
    lines: tuple[OrderLineInput, ...],
) -> None:
    for line in lines:
        product = products[line.product_id]
        product.stock -= line.quantity

    Product.objects.bulk_update(products.values(), ["stock"])
```

**[Reason] Clean Code / Django**
View는 HTTP 입력 검증, service 호출, 응답 선택만 담당합니다. 주문 생성, 재고 차감, 라인 생성, 알림 예약은 application service로 이동해 테스트 가능한 유스케이스가 됩니다. 재고는 `select_for_update()`와 `transaction.atomic()`으로 보호하고, 이메일/알림은 `transaction.on_commit()` 뒤에 실행해 롤백된 주문에 알림이 나가지 않게 합니다.

추가 테스트는 최소한 다음을 두면 됩니다.

```python
# tests/isolated/orders/test_place_order.py

import pytest

from orders.services import EmptyOrder, ProductUnavailable, place_order


def test_place_order_creates_order_lines_and_decreases_stock(user, product):
    command = create_order_command(user=user, product=product, quantity=2)

    result = place_order(command)

    product.refresh_from_db()
    assert result.order_id is not None
    assert product.stock == 8


def test_place_order_rejects_empty_lines(user):
    command = create_order_command(user=user, lines=())

    with pytest.raises(EmptyOrder):
        place_order(command)


def test_place_order_rejects_insufficient_stock(user, product):
    command = create_order_command(user=user, product=product, quantity=999)

    with pytest.raises(ProductUnavailable):
        place_order(command)
```

실제 프로젝트에 적용 후 실행할 명령은 `pytest tests/isolated/orders -q`입니다.

---
> **관련 스킬 참조:**
> - Django service layer / thin view → **implementation-django** 스킬