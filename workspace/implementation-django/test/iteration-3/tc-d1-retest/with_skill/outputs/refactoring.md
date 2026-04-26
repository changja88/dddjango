# 주문 처리 코드 리팩토링

## 개별 변경 사항

---

### 1. Fat View -> Service Layer 추출

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
def order_create(*, user: User, items: list[dict], payment_method: str) -> Order:
    ...
```

[Reason] Service Layer / Fat Model, Thin View -- 주문 생성 로직이 뷰 안에 직접 구현되어 있어 `OrderCreateView`와 `OrderAPIView`에서 동일한 코드가 중복된다. 비즈니스 로직을 `order_create` 서비스 함수로 추출하면 두 뷰 모두 한 줄로 호출할 수 있고, 테스트도 뷰 없이 서비스 함수 단위로 가능해진다.

---

### 2. Python 레벨 재고 차감 -> F() 표현식으로 원자적 처리

[Before]
```python
product.stock -= item['quantity']
product.save()
```

[After]
```python
Product.objects.filter(pk=product.pk).update(
    stock=F("stock") - item["quantity"]
)
```

[Reason] Performance / F() 표현식 -- `product.stock -= quantity; product.save()`는 읽기-수정-쓰기(read-modify-write) 패턴으로, 동시 요청 시 재고가 잘못 계산될 수 있다. `F("stock") - quantity`는 DB 레벨에서 `UPDATE SET stock = stock - %s`로 실행되어 race condition을 방지한다.

---

### 3. 트랜잭션 없는 다중 DB 작업 -> transaction.atomic()

[Before]
```python
order = Order.objects.create(user=user, total_amount=0)
# ... OrderItem 생성, 재고 차감, Payment 생성 ...
order.total_amount = total
order.save()
```

[After]
```python
with transaction.atomic():
    order = Order.objects.create(user=user, total_amount=Decimal("0"))
    # ... 모든 DB 작업을 atomic 블록 안에서 수행
```

[Reason] Service Layer / 트랜잭션과 부수 효과 -- Order, OrderItem, Product(재고 차감), Payment 생성이 하나의 비즈니스 트랜잭션이다. 중간에 실패하면 부분적으로만 데이터가 생성되어 정합성이 깨진다. `transaction.atomic()`으로 묶으면 전부 성공하거나 전부 롤백된다.

---

### 4. 트랜잭션 내부 이메일 발송 -> transaction.on_commit()

[Before]
```python
# transaction.atomic() 블록 안에서 직접 호출
send_mail('주문 확인', f'주문 {order.id}가 생성되었습니다.',
          'noreply@shop.com', [user.email])
```

[After]
```python
transaction.on_commit(
    lambda: send_order_confirmation_email(order=order)
)
```

[Reason] Service Layer / transaction.on_commit -- 이메일은 되돌릴 수 없는 부수 효과다. 트랜잭션 안에서 이메일을 보낸 뒤 후속 DB 작업이 실패하여 롤백되면, 존재하지 않는 주문에 대한 확인 메일이 발송된다. `transaction.on_commit()`을 사용하면 트랜잭션이 성공적으로 커밋된 후에만 이메일이 발송된다.

---

### 5. 루프 안에서 동일 쿼리 중복 실행 -> 단일 조회 + select_for_update

[Before]
```python
# 재고 검증 루프에서 한 번
for item in data['items']:
    product = Product.objects.get(pk=item['product_id'])
    if product.stock < item['quantity']:
        ...

# 주문 아이템 생성 루프에서 또 한 번
for item in data['items']:
    product = Product.objects.get(pk=item['product_id'])
    ...
```

[After]
```python
product_ids = [item["product_id"] for item in items]
products = {
    p.pk: p
    for p in Product.objects.filter(pk__in=product_ids).select_for_update()
}
```

[Reason] QuerySet 최적화 / select_for_update -- 원본 코드는 같은 Product를 두 번 조회한다 (검증용 + 생성용). `filter(pk__in=...)` 한 번으로 필요한 모든 Product를 가져오고, `select_for_update()`로 재고 차감 시점까지 행을 잠가 동시성 문제를 방지한다.

---

### 6. 루프 안에서 개별 OrderItem.objects.create -> bulk_create

[Before]
```python
for item in data['items']:
    product = Product.objects.get(pk=item['product_id'])
    OrderItem.objects.create(
        order=order, product=product,
        quantity=item['quantity'], price=product.price
    )
```

[After]
```python
order_items = [
    OrderItem(
        order=order,
        product=product,
        quantity=item["quantity"],
        price=product.price,
    )
    for item in items
    for product in [products[item["product_id"]]]
]
OrderItem.objects.bulk_create(order_items)
```

[Reason] QuerySet / bulk 연산 -- 루프 안에서 `create()`를 N번 호출하면 N개의 INSERT 쿼리가 발생한다. `bulk_create()`로 한 번의 쿼리로 모든 OrderItem을 생성하여 DB 왕복 횟수를 줄인다.

---

### 7. 전체 모델 save() -> save(update_fields=...)

[Before]
```python
order.total_amount = total
order.save()
```

[After]
```python
order.total_amount = total
order.save(update_fields=["total_amount"])
```

[Reason] Performance / save(update_fields) -- `save()` 호출 시 모든 컬럼이 UPDATE 대상이 된다. `update_fields`를 지정하면 변경된 필드만 UPDATE하여 불필요한 데이터 전송을 줄이고, 동시 수정 시 다른 필드를 덮어쓰는 문제를 방지한다.

---

### 8. 뷰에서 직접 JSON 파싱/검증 -> DRF Serializer 활용

[Before]
```python
class OrderCreateView(View):
    def post(self, request):
        data = json.loads(request.body)
```

[After]
```python
class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True, allow_empty=False)
    payment_method = serializers.CharField()
```

[Reason] DRF / Serializer 설계 -- 수동 `json.loads()`는 잘못된 JSON에 대한 에러 처리가 없고, 필드 타입 검증도 없다. DRF Serializer를 사용하면 입력 검증이 선언적이고 일관되며, 에러 메시지도 자동으로 구조화된다.

---

## 리팩토링된 전체 코드

### serializers.py

```python
from rest_framework import serializers


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True, allow_empty=False)
    payment_method = serializers.CharField()


class OrderCreateResponseSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
```

### services.py

```python
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F

from .models import Order, OrderItem, Payment, Product


def order_create(*, user, items: list[dict], payment_method: str) -> Order:
    """주문을 생성하고 결제를 처리한다."""
    with transaction.atomic():
        product_ids = [item["product_id"] for item in items]
        products = {
            p.pk: p
            for p in Product.objects.filter(pk__in=product_ids).select_for_update()
        }

        # 존재하지 않는 상품 검증
        missing = set(product_ids) - set(products.keys())
        if missing:
            raise ValidationError(f"존재하지 않는 상품: {missing}")

        # 재고 검증
        for item in items:
            product = products[item["product_id"]]
            if product.stock < item["quantity"]:
                raise ValidationError(f"{product.name} 재고 부족")

        # 주문 생성
        order = Order.objects.create(user=user, total_amount=Decimal("0"))

        # 주문 아이템 일괄 생성
        total = Decimal("0")
        order_items = []
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

        # F() 표현식으로 재고 원자적 차감
        for item in items:
            Product.objects.filter(pk=item["product_id"]).update(
                stock=F("stock") - item["quantity"]
            )

        # 주문 총액 업데이트
        order.total_amount = total
        order.save(update_fields=["total_amount"])

        # 결제 생성
        Payment.objects.create(
            order=order,
            amount=total,
            method=payment_method,
        )

    # 트랜잭션 커밋 후에만 이메일 발송
    transaction.on_commit(
        lambda: _send_order_confirmation_email(order=order, user=user)
    )

    return order


def _send_order_confirmation_email(*, order: Order, user) -> None:
    """주문 확인 이메일을 발송한다."""
    send_mail(
        "주문 확인",
        f"주문 {order.id}가 생성되었습니다.",
        "noreply@shop.com",
        [user.email],
    )
```

### views.py

```python
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OrderCreateSerializer
from .services import order_create


class OrderCreateView(View):
    """Django View 기반 주문 생성."""

    def post(self, request):
        serializer = OrderCreateSerializer(data=json.loads(request.body))
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            order = order_create(
                user=request.user,
                items=data["items"],
                payment_method=data["payment_method"],
            )
        except ValidationError as e:
            return JsonResponse({"error": str(e.message)}, status=400)

        return JsonResponse({"order_id": order.id})


class OrderAPIView(APIView):
    """DRF APIView 기반 주문 생성."""

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            order = order_create(
                user=request.user,
                items=data["items"],
                payment_method=data["payment_method"],
            )
        except ValidationError as e:
            return Response(
                {"error": str(e.message)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"order_id": order.id}, status=status.HTTP_201_CREATED)
```
