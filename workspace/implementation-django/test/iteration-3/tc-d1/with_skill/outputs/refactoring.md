# 주문 처리 코드 리팩토링

## 변경 1: Fat View의 비즈니스 로직을 서비스 레이어로 추출

[Before]
```python
class OrderCreateView(View):
    def post(self, request):
        data = json.loads(request.body)
        user = request.user
        for item in data['items']:
            product = Product.objects.get(pk=item['product_id'])
            if product.stock < item['quantity']:
                return JsonResponse({'error': f'{product.name} 재고 부족'}, status=400)
        order = Order.objects.create(user=user, total_amount=0)
        total = Decimal('0')
        for item in data['items']:
            product = Product.objects.get(pk=item['product_id'])
            OrderItem.objects.create(
                order=order, product=product,
                quantity=item['quantity'], price=product.price
            )
            total += product.price * item['quantity']
            product.stock -= item['quantity']
            product.save()
        order.total_amount = total
        order.save()
        payment = Payment.objects.create(
            order=order, amount=total, method=data['payment_method']
        )
        send_mail('주문 확인', f'주문 {order.id}가 생성되었습니다.',
                  'noreply@shop.com', [user.email])
        return JsonResponse({'order_id': order.id})
```

[After]
```python
# services.py
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction

from .models import Order, OrderItem, Payment, Product


def order_create(*, user, items: list[dict], payment_method: str) -> Order:
    """주문을 생성하고 결제 및 확인 이메일을 처리한다."""
    products = _order_validate_stock(items=items)
    with transaction.atomic():
        order = _order_build(user=user, items=items, products=products)
        _order_deduct_stock(items=items, products=products)
        _payment_create(order=order, payment_method=payment_method)
    _order_send_confirmation(order=order, email=user.email)
    return order


def _order_validate_stock(*, items: list[dict]) -> dict[int, Product]:
    """재고를 검증하고 Product 객체를 한 번에 조회하여 반환한다."""
    product_ids = [item["product_id"] for item in items]
    products = Product.objects.filter(pk__in=product_ids).select_for_update()
    products_by_id = {p.pk: p for p in products}

    for item in items:
        product = products_by_id.get(item["product_id"])
        if product is None:
            raise ValidationError(f"상품 {item['product_id']}을(를) 찾을 수 없습니다.")
        if product.stock < item["quantity"]:
            raise ValidationError(f"{product.name} 재고 부족")
    return products_by_id


def _order_build(*, user, items: list[dict], products: dict[int, Product]) -> Order:
    """Order와 OrderItem을 생성하고 총액을 계산한다."""
    order = Order.objects.create(user=user, total_amount=Decimal("0"))
    order_items = []
    total = Decimal("0")

    for item in items:
        product = products[item["product_id"]]
        order_items.append(
            OrderItem(
                order=order,
                product=product,
                quantity=item["quantity"],
                price=product.price,
            )
        )
        total += product.price * item["quantity"]

    OrderItem.objects.bulk_create(order_items)
    order.total_amount = total
    order.save(update_fields=["total_amount"])
    return order


def _order_deduct_stock(*, items: list[dict], products: dict[int, Product]) -> None:
    """재고를 차감하고 일괄 업데이트한다."""
    for item in items:
        products[item["product_id"]].stock -= item["quantity"]
    Product.objects.bulk_update(products.values(), ["stock"])


def _payment_create(*, order: Order, payment_method: str) -> Payment:
    """결제 레코드를 생성한다."""
    return Payment.objects.create(
        order=order,
        amount=order.total_amount,
        method=payment_method,
    )


def _order_send_confirmation(*, order: Order, email: str) -> None:
    """주문 확인 이메일을 발송한다."""
    send_mail(
        "주문 확인",
        f"주문 {order.id}가 생성되었습니다.",
        "noreply@shop.com",
        [email],
    )
```

[Reason] Service Layer / Fat View -> EXTRACT to service -- 동일한 주문 생성 로직이 `OrderCreateView`와 `OrderAPIView` 두 곳에서 반복된다. 비즈니스 로직을 `order_create` 서비스 함수로 추출하면 DRY 원칙을 충족하고, 두 뷰 모두 같은 서비스를 호출하여 일관된 동작을 보장한다. 네이밍은 HackSoft의 `<entity>_<action>` 규칙을 따른다.

---

## 변경 2: 루프 내 개별 Product.objects.get() 호출 제거 (N+1 쿼리 해결)

[Before]
```python
for item in data['items']:
    product = Product.objects.get(pk=item['product_id'])
    if product.stock < item['quantity']:
        return JsonResponse({'error': f'{product.name} 재고 부족'}, status=400)
# ... 두 번째 루프에서 또 개별 조회
for item in data['items']:
    product = Product.objects.get(pk=item['product_id'])
```

[After]
```python
product_ids = [item["product_id"] for item in items]
products = Product.objects.filter(pk__in=product_ids).select_for_update()
products_by_id = {p.pk: p for p in products}
```

[Reason] QuerySet 최적화 / Missing select_related -> ADD based on access patterns -- 원래 코드는 아이템 수 N에 대해 검증 루프에서 N번, 생성 루프에서 N번, 총 2N번의 개별 쿼리를 실행한다. `filter(pk__in=...)` 으로 단 1번의 쿼리로 모든 상품을 조회하고, `select_for_update()`로 동시성 환경에서의 재고 차감 레이스 컨디션도 방지한다.

---

## 변경 3: 루프 내 개별 save()를 bulk 연산으로 교체

[Before]
```python
for item in data['items']:
    product = Product.objects.get(pk=item['product_id'])
    OrderItem.objects.create(
        order=order, product=product,
        quantity=item['quantity'], price=product.price
    )
    total += product.price * item['quantity']
    product.stock -= item['quantity']
    product.save()  # 루프마다 UPDATE 쿼리
```

[After]
```python
# OrderItem 일괄 생성
order_items = []
for item in items:
    product = products[item["product_id"]]
    order_items.append(
        OrderItem(
            order=order, product=product,
            quantity=item["quantity"], price=product.price,
        )
    )
OrderItem.objects.bulk_create(order_items)

# 재고 일괄 차감
for item in items:
    products[item["product_id"]].stock -= item["quantity"]
Product.objects.bulk_update(products.values(), ["stock"])
```

[Reason] Individual save() in loop -> REPLACE with bulk_update/bulk_create -- 루프 내 개별 `create()`와 `save()`는 아이템 수만큼 INSERT/UPDATE 쿼리를 발생시킨다. `bulk_create`와 `bulk_update`를 사용하면 각각 1번의 쿼리로 처리되어 DB 왕복 횟수가 대폭 감소한다.

---

## 변경 4: save() 호출에 update_fields 추가

[Before]
```python
order.total_amount = total
order.save()  # 모든 컬럼이 SET 절에 포함
```

[After]
```python
order.total_amount = total
order.save(update_fields=["total_amount"])
```

[Reason] Performance / save(update_fields=...) -- total_amount 필드만 변경되었으므로, `update_fields`를 지정하여 변경된 컬럼만 UPDATE한다. 동시성 환경에서 다른 필드의 변경을 덮어쓰는 것을 방지하고, 업데이트 데이터량도 줄인다.

---

## 변경 5: transaction.atomic()으로 원자성 보장

[Before]
```python
# 트랜잭션 없이 순차 실행 -- 중간에 실패하면 부분 생성 상태
order = Order.objects.create(user=user, total_amount=0)
# ... OrderItem 생성, 재고 차감, Payment 생성이 각각 별도 트랜잭션
```

[After]
```python
with transaction.atomic():
    order = _order_build(user=user, items=items, products=products)
    _order_deduct_stock(items=items, products=products)
    _payment_create(order=order, payment_method=payment_method)
```

[Reason] DRY / Explicit > Implicit -- 주문 생성, 재고 차감, 결제 생성은 하나의 비즈니스 트랜잭션이다. 중간에 실패하면 전부 롤백되어야 한다. `transaction.atomic()`으로 감싸 데이터 정합성을 보장한다.

---

## 변경 6: 뷰를 얇게 유지 -- 서비스 함수 호출만 담당

[Before]
```python
class OrderCreateView(View):
    def post(self, request):
        data = json.loads(request.body)
        user = request.user
        # ... 30줄 이상의 비즈니스 로직

class OrderAPIView(APIView):
    def post(self, request):
        data = request.data
        user = request.user
        # ... 위와 동일한 로직 반복
```

[After]
```python
# views.py
import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views import View

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import order_create


class OrderCreateView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            order = order_create(
                user=request.user,
                items=data["items"],
                payment_method=data["payment_method"],
            )
        except ValidationError as e:
            return JsonResponse({"error": str(e.message)}, status=400)
        return JsonResponse({"order_id": order.id}, status=201)


class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            order = order_create(
                user=request.user,
                items=request.data["items"],
                payment_method=request.data["payment_method"],
            )
        except ValidationError as e:
            return Response({"error": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"order_id": order.id}, status=status.HTTP_201_CREATED)
```

[Reason] Fat view with business logic -> EXTRACT to model method or service / DRY -- 두 뷰 모두 동일한 `order_create` 서비스를 호출하므로 로직 중복이 완전히 제거된다. 각 뷰는 자신의 프레임워크에 맞는 요청 파싱과 응답 포맷팅만 담당하며, 비즈니스 로직은 서비스 레이어에 격리된다. `OrderAPIView`에는 `permission_classes`와 적절한 HTTP 상태 코드도 추가했다.

---

## 전체 리팩토링 결과

### services.py

```python
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction

from .models import Order, OrderItem, Payment, Product


def order_create(*, user, items: list[dict], payment_method: str) -> Order:
    """주문을 생성하고 결제 및 확인 이메일을 처리한다."""
    products = _order_validate_stock(items=items)
    with transaction.atomic():
        order = _order_build(user=user, items=items, products=products)
        _order_deduct_stock(items=items, products=products)
        _payment_create(order=order, payment_method=payment_method)
    _order_send_confirmation(order=order, email=user.email)
    return order


def _order_validate_stock(*, items: list[dict]) -> dict[int, Product]:
    """재고를 검증하고 Product 객체를 한 번에 조회하여 반환한다."""
    product_ids = [item["product_id"] for item in items]
    products = Product.objects.filter(pk__in=product_ids).select_for_update()
    products_by_id = {p.pk: p for p in products}

    for item in items:
        product = products_by_id.get(item["product_id"])
        if product is None:
            raise ValidationError(f"상품 {item['product_id']}을(를) 찾을 수 없습니다.")
        if product.stock < item["quantity"]:
            raise ValidationError(f"{product.name} 재고 부족")
    return products_by_id


def _order_build(*, user, items: list[dict], products: dict[int, Product]) -> Order:
    """Order와 OrderItem을 생성하고 총액을 계산한다."""
    order = Order.objects.create(user=user, total_amount=Decimal("0"))
    order_items = []
    total = Decimal("0")

    for item in items:
        product = products[item["product_id"]]
        order_items.append(
            OrderItem(
                order=order,
                product=product,
                quantity=item["quantity"],
                price=product.price,
            )
        )
        total += product.price * item["quantity"]

    OrderItem.objects.bulk_create(order_items)
    order.total_amount = total
    order.save(update_fields=["total_amount"])
    return order


def _order_deduct_stock(*, items: list[dict], products: dict[int, Product]) -> None:
    """재고를 차감하고 일괄 업데이트한다."""
    for item in items:
        products[item["product_id"]].stock -= item["quantity"]
    Product.objects.bulk_update(products.values(), ["stock"])


def _payment_create(*, order: Order, payment_method: str) -> Payment:
    """결제 레코드를 생성한다."""
    return Payment.objects.create(
        order=order,
        amount=order.total_amount,
        method=payment_method,
    )


def _order_send_confirmation(*, order: Order, email: str) -> None:
    """주문 확인 이메일을 발송한다."""
    send_mail(
        "주문 확인",
        f"주문 {order.id}가 생성되었습니다.",
        "noreply@shop.com",
        [email],
    )
```

### views.py

```python
import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views import View

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import order_create


class OrderCreateView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            order = order_create(
                user=request.user,
                items=data["items"],
                payment_method=data["payment_method"],
            )
        except ValidationError as e:
            return JsonResponse({"error": str(e.message)}, status=400)
        return JsonResponse({"order_id": order.id}, status=201)


class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            order = order_create(
                user=request.user,
                items=request.data["items"],
                payment_method=request.data["payment_method"],
            )
        except ValidationError as e:
            return Response({"error": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"order_id": order.id}, status=status.HTTP_201_CREATED)
```
