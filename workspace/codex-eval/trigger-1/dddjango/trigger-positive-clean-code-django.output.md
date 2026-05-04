**[주요 내용]**

현재 `/private/tmp/dddjango-codex-eval`에는 프로젝트 파일이 없고 sandbox도 read-only라 실제 `views.py`를 수정하거나 pytest를 실행하지 못했습니다. 아래는 dddjango 기준으로 “주문 생성 로직이 view에 몰린 상태”를 서비스 레이어로 분리하는 적용 예시입니다.

[Before]

```python
# orders/views.py
class OrderCreateView(View):
    def post(self, request):
        order = Order.objects.create(customer=request.user, status="pending")
        total = Decimal("0")

        for item in request.POST.getlist("items"):
            product = Product.objects.get(pk=item["product_id"])
            quantity = int(item["quantity"])

            if product.stock < quantity:
                messages.error(request, "재고가 부족합니다.")
                return redirect("cart")

            product.stock -= quantity
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
            )
            total += product.price * quantity

        order.total_price = total
        order.save()
        send_order_created_email(order)
        return redirect("orders:detail", pk=order.pk)
```

[After]

```python
# orders/services.py
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.db.models import F

from products.models import Product

from .emails import send_order_created_email
from .models import Order, OrderItem


class EmptyOrderError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


@dataclass(frozen=True)
class OrderLineInput:
    product_id: int
    quantity: int


def order_create(*, customer, lines: list[OrderLineInput]) -> Order:
    if not lines:
        raise EmptyOrderError("주문 항목이 없습니다.")

    product_ids = [line.product_id for line in lines]
    quantity_by_product_id = {
        line.product_id: line.quantity
        for line in lines
    }

    with transaction.atomic():
        products = (
            Product.objects
            .select_for_update()
            .filter(id__in=product_ids)
        )
        products_by_id = {product.id: product for product in products}

        total_price = Decimal("0")
        order_items = []

        order = Order.objects.create(
            customer=customer,
            status=Order.Status.PENDING,
            total_price=Decimal("0"),
        )

        for product_id, quantity in quantity_by_product_id.items():
            product = products_by_id[product_id]

            if product.stock < quantity:
                raise InsufficientStockError(f"{product.name} 재고가 부족합니다.")

            total_price += product.price * quantity
            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                )
            )

        OrderItem.objects.bulk_create(order_items)

        for product_id, quantity in quantity_by_product_id.items():
            Product.objects.filter(pk=product_id).update(
                stock=F("stock") - quantity,
            )

        order.total_price = total_price
        order.save(update_fields=["total_price"])

    transaction.on_commit(lambda: send_order_created_email(order))
    return order
```

```python
# orders/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from .forms import OrderCreateForm
from .services import (
    EmptyOrderError,
    InsufficientStockError,
    OrderLineInput,
    order_create,
)


class OrderCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = OrderCreateForm(request.POST)

        if not form.is_valid():
            messages.error(request, "주문 정보를 다시 확인해주세요.")
            return redirect("cart:detail")

        lines = [
            OrderLineInput(
                product_id=item["product_id"],
                quantity=item["quantity"],
            )
            for item in form.cleaned_data["items"]
        ]

        try:
            order = order_create(customer=request.user, lines=lines)
        except EmptyOrderError:
            messages.error(request, "주문 항목이 없습니다.")
            return redirect("cart:detail")
        except InsufficientStockError as exc:
            messages.error(request, str(exc))
            return redirect("cart:detail")

        return redirect("orders:detail", pk=order.pk)
```

[Reason] Django Convention -- Fat View를 Thin View로 바꿨습니다. view는 HTTP 입력, 메시지, redirect만 담당하고, 주문 생성 규칙은 `order_create` 서비스 함수가 담당합니다.

[Reason] Clean Code Principle -- 주문 항목 입력을 `OrderLineInput` 값 객체로 묶어 인수 개수를 줄이고 의도를 드러냈습니다. dict나 tuple 반환 대신 도메인 예외를 사용해 실패 이유도 명확해집니다.

[Reason] Django Transaction Convention -- 주문, 주문 항목, 재고 차감은 `transaction.atomic()` 안에서 처리하고, 이메일 발송은 `transaction.on_commit()`으로 분리했습니다. 트랜잭션이 롤백됐는데 이메일만 발송되는 불일치를 막습니다.

[Reason] Django Performance Convention -- 루프 안의 `OrderItem.objects.create()`는 `bulk_create()`로 바꾸고, 재고 차감은 `F()` expression을 사용했습니다. 동시 주문에서 재고 값이 덮어써질 위험을 줄입니다.

[Reason] Django Security Convention -- 주문 생성 view에는 `LoginRequiredMixin`을 적용했습니다. API 엔드포인트라면 DRF가 아니라 Django Ninja `Router`/`Schema`와 `auth=django_auth`로 구현해야 합니다. 이 프로젝트 기준에서는 DRF를 사용하지 않습니다.

**RED 테스트 예시**

실행은 못 했지만, 먼저 이런 실패 테스트를 둔 뒤 리팩터링하는 흐름이 맞습니다.

```python
# tests/test_order_create.py
import pytest

from orders.services import InsufficientStockError, OrderLineInput, order_create


@pytest.mark.django_db
def test_order_create_when_stock_is_enough_creates_order_and_items(user, product):
    product.stock = 10
    product.price = 1000
    product.save(update_fields=["stock", "price"])

    order = order_create(
        customer=user,
        lines=[OrderLineInput(product_id=product.id, quantity=2)],
    )

    assert order.customer == user
    assert order.total_price == 2000
    assert order.items.count() == 1


@pytest.mark.django_db
def test_order_create_when_stock_is_not_enough_raises_error(user, product):
    product.stock = 1
    product.save(update_fields=["stock"])

    with pytest.raises(InsufficientStockError):
        order_create(
            customer=user,
            lines=[OrderLineInput(product_id=product.id, quantity=2)],
        )
```

예상 실패 이유: 아직 `orders.services.order_create`, `OrderLineInput`, `InsufficientStockError`가 없거나, 기존 view 내부에만 로직이 있어서 테스트에서 직접 호출할 수 없습니다.

실행 명령:

```bash
pytest tests/test_order_create.py
pytest
```

---
> **관련 스킬 참조:**
> - Django 서비스 레이어 / Thin View → **implementation-django** 스킬
> - 클린 코드 리팩터링 / 예외 설계 → **implementation-cleancode** 스킬
> - RED-GREEN-REFACTOR 테스트 흐름 → **implementation-tdd** 스킬