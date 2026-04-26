# 주문 처리 코드 리팩토링

## 문제 진단

1. **Fat View** -- 뷰가 재고 검증, 주문 생성, 결제 처리, 이메일 발송까지 모두 담당
2. **로직 중복** -- `OrderCreateView`와 `OrderAPIView`에서 동일한 비즈니스 로직 반복
3. **트랜잭션 미적용** -- 주문 생성 도중 실패 시 데이터 정합성 깨짐
4. **N+1 쿼리** -- 루프를 두 번 돌면서 같은 Product를 중복 조회

## 리팩토링 결과

### 1. Service Layer -- 비즈니스 로직 분리

```python
# services/order_service.py

from decimal import Decimal
from django.db import transaction
from django.core.mail import send_mail
from django.core.exceptions import ValidationError

from orders.models import Order, OrderItem, Payment
from products.models import Product


class OrderService:
    """주문 생성에 관한 모든 비즈니스 로직을 담당한다."""

    @staticmethod
    def create_order(user, items_data: list[dict], payment_method: str) -> Order:
        """
        주문을 생성한다.
        items_data: [{'product_id': int, 'quantity': int}, ...]
        """
        products_with_qty = OrderService._validate_stock(items_data)

        with transaction.atomic():
            order = OrderService._build_order(user, products_with_qty)
            OrderService._create_payment(order, payment_method)

        OrderService._send_confirmation_email(order, user)
        return order

    @staticmethod
    def _validate_stock(items_data: list[dict]) -> list[tuple]:
        """재고를 검증하고 (Product, quantity) 쌍을 반환한다."""
        product_ids = [item['product_id'] for item in items_data]
        products_by_id = {
            p.pk: p
            for p in Product.objects.filter(pk__in=product_ids).select_for_update()
        }

        results = []
        for item in items_data:
            product = products_by_id.get(item['product_id'])
            if product is None:
                raise ValidationError(f"상품(id={item['product_id']})을 찾을 수 없습니다.")

            quantity = item['quantity']
            if product.stock < quantity:
                raise ValidationError(f'{product.name} 재고 부족')

            results.append((product, quantity))
        return results

    @staticmethod
    def _build_order(user, products_with_qty: list[tuple]) -> Order:
        """Order와 OrderItem을 생성하고 재고를 차감한다."""
        order = Order.objects.create(user=user, total_amount=Decimal('0'))
        total = Decimal('0')

        order_items = []
        products_to_update = []

        for product, quantity in products_with_qty:
            order_items.append(OrderItem(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            ))
            total += product.price * quantity
            product.stock -= quantity
            products_to_update.append(product)

        OrderItem.objects.bulk_create(order_items)
        Product.objects.bulk_update(products_to_update, ['stock'])

        order.total_amount = total
        order.save(update_fields=['total_amount'])
        return order

    @staticmethod
    def _create_payment(order: Order, payment_method: str) -> Payment:
        return Payment.objects.create(
            order=order,
            amount=order.total_amount,
            method=payment_method,
        )

    @staticmethod
    def _send_confirmation_email(order: Order, user) -> None:
        send_mail(
            '주문 확인',
            f'주문 {order.id}가 생성되었습니다.',
            'noreply@shop.com',
            [user.email],
        )
```

### 2. Views -- 얇은 뷰로 변경

```python
# views.py

import json
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response

from services.order_service import OrderService


class OrderCreateView(View):
    """Django View 기반 주문 생성 엔드포인트."""

    def post(self, request):
        data = json.loads(request.body)
        try:
            order = OrderService.create_order(
                user=request.user,
                items_data=data['items'],
                payment_method=data['payment_method'],
            )
        except ValidationError as e:
            return JsonResponse({'error': str(e.message)}, status=400)

        return JsonResponse({'order_id': order.id})


class OrderAPIView(APIView):
    """DRF 기반 주문 생성 엔드포인트."""

    def post(self, request):
        data = request.data
        try:
            order = OrderService.create_order(
                user=request.user,
                items_data=data['items'],
                payment_method=data['payment_method'],
            )
        except ValidationError as e:
            return Response({'error': str(e.message)}, status=400)

        return Response({'order_id': order.id})
```

## 변경 요약

| 항목 | Before | After |
|---|---|---|
| 뷰 책임 | 검증 + 생성 + 결제 + 메일 | 요청 파싱, 서비스 호출, 응답 반환 |
| 로직 중복 | 2개 뷰에서 동일 로직 복붙 | `OrderService.create_order()` 단일 호출 |
| DB 쿼리 | Product를 루프마다 개별 조회 (N+1) | `filter(pk__in=...)` 한 번 + `bulk_create` / `bulk_update` |
| 트랜잭션 | 없음 (중간 실패 시 데이터 불일치) | `transaction.atomic()` 으로 원자성 보장 |
| 동시성 | 재고 경합 시 음수 가능 | `select_for_update()` 로 행 잠금 |
