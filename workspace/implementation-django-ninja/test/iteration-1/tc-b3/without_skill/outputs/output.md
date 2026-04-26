# Django Ninja Code Review: `create_order`

## 1. Critical Issues

### 1.1 Race Condition (재고 차감)

```python
if product.stock < payload.quantity:
    return {'error': 'Insufficient stock', 'code': 400}
# ... 중간에 다른 요청이 동일 product를 읽을 수 있음
product.stock -= payload.quantity
product.save()
```

`product.stock`을 읽고 나서 감소시키는 사이에 다른 요청이 동일 상품의 재고를 동시에 차감할 수 있다. Python 레벨의 `-=` 연산은 DB 수준의 원자적 연산이 아니므로 **재고가 음수**가 되거나 **초과 판매**가 발생할 수 있다.

**수정 방안:**
```python
from django.db.models import F

# select_for_update로 행 잠금
product = Product.objects.select_for_update().get(id=payload.product_id)

# 또는 F() expression으로 원자적 갱신
Product.objects.filter(id=product.id).update(stock=F('stock') - payload.quantity)
```

### 1.2 트랜잭션 미사용

결제 성공 후 `Order.objects.create()`와 `product.save()`가 별개의 DB 연산으로 실행된다. 둘 중 하나가 실패하면 데이터 정합성이 깨진다. 예를 들어 `Order`는 생성됐는데 `product.save()`에서 예외가 발생하면 재고는 줄지 않은 채 주문만 존재하게 된다.

**수정 방안:**
```python
from django.db import transaction

with transaction.atomic():
    product = Product.objects.select_for_update().get(id=payload.product_id)
    # ... 재고 확인, 주문 생성, 재고 차감을 하나의 트랜잭션 안에서 처리
```

### 1.3 결제 후 실패 시 보상 로직 부재

`requests.post()`로 외부 결제 API를 호출한 뒤, 이후 `Order.objects.create()` 또는 `product.save()`가 실패하면 **결제는 완료됐지만 주문은 생성되지 않는** 상태가 된다. 결제 취소(환불) 등의 보상 트랜잭션(compensating transaction)이 필요하다.

---

## 2. Major Issues

### 2.1 HTTP 응답 코드가 항상 200

에러 상황에서 `{'error': '...', 'code': 404}` 같은 dict를 반환하고 있지만, 실제 HTTP 상태 코드는 항상 **200 OK**이다. 클라이언트가 응답 본문을 파싱하지 않으면 에러를 감지할 수 없다.

**수정 방안:** Django Ninja의 `HttpError`를 사용하거나 tuple로 상태 코드를 반환한다.
```python
from ninja.errors import HttpError

raise HttpError(404, "Product not found")

# 또는 tuple 반환
return 400, {'error': 'Insufficient stock'}
```

### 2.2 동기 HTTP 호출로 인한 성능 문제

`requests.post()`는 동기 블로킹 호출이다. 외부 결제 서비스가 느리면 Django 워커 스레드가 점유되어 전체 서버 처리량이 크게 저하된다. 타임아웃도 설정되어 있지 않아 무한 대기 가능성이 있다.

**수정 방안:**
```python
resp = requests.post(
    'https://payment.example.com/charge',
    json={'amount': float(product.price * payload.quantity)},
    timeout=10,  # 최소한 타임아웃 설정
)
```

비동기 처리가 필요하다면 Celery 같은 태스크 큐를 고려하거나, Django Ninja의 async view를 활용할 수 있다.

### 2.3 Import 누락

`Product`와 `Order` 모델이 import되어 있지 않다. 실행 시 `NameError`가 발생한다.

```python
from myapp.models import Product, Order  # 필요
```

---

## 3. Minor Issues

### 3.1 출력 스키마 미정의

입력은 `OrderIn` 스키마로 정의했지만, 응답 스키마가 없다. 성공/실패 시 반환 구조가 다르고 타입 안전성이 보장되지 않는다. Django Ninja의 `response` 파라미터를 활용해야 API 문서 자동 생성과 응답 검증이 가능하다.

```python
class OrderOut(Schema):
    order_id: int
    total: float

class ErrorOut(Schema):
    error: str
    code: int

@api.post('/orders', response={200: OrderOut, 400: ErrorOut, 404: ErrorOut})
def create_order(request, payload: OrderIn):
    ...
```

### 3.2 `float()` 변환

`float(product.price * payload.quantity)` -- `product.price`가 `DecimalField`라면 `Decimal`을 `float`으로 변환하면서 정밀도 손실이 발생할 수 있다. JSON 직렬화가 목적이라면 `str()`로 변환하거나 응답 스키마에서 `Decimal` 직렬화를 처리하는 것이 더 안전하다.

### 3.3 URL 패턴 컨벤션

`'/orders'`는 Django/Ninja에서 일반적으로 trailing slash를 붙여 `'/orders/'`로 작성한다. Django의 `APPEND_SLASH` 설정과의 일관성을 위해 확인이 필요하다.

### 3.4 로깅 부재

결제 실패, 재고 부족 등의 상황에서 로깅이 없어 운영 환경에서 문제 추적이 어렵다.

---

## 4. 개선된 코드 예시

```python
import logging
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from django.db import transaction
from django.db.models import F
import requests

from myapp.models import Product, Order

logger = logging.getLogger(__name__)

api = NinjaAPI()

class OrderIn(Schema):
    product_id: int
    quantity: int

class OrderOut(Schema):
    order_id: int
    total: str  # Decimal 정밀도 보존

@api.post('/orders/', response={200: OrderOut})
def create_order(request, payload: OrderIn):
    with transaction.atomic():
        try:
            product = Product.objects.select_for_update().get(id=payload.product_id)
        except Product.DoesNotExist:
            raise HttpError(404, "Product not found")

        if product.stock < payload.quantity:
            raise HttpError(400, "Insufficient stock")

        total = product.price * payload.quantity

        try:
            resp = requests.post(
                'https://payment.example.com/charge',
                json={'amount': str(total)},
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException:
            logger.exception("Payment request failed for product %s", product.id)
            raise HttpError(502, "Payment failed")

        order = Order.objects.create(
            product=product,
            quantity=payload.quantity,
            total=total,
        )
        Product.objects.filter(id=product.id).update(stock=F('stock') - payload.quantity)

    return {'order_id': order.id, 'total': str(order.total)}
```

---

## 5. 요약

| 구분 | 항목 | 심각도 |
|------|------|--------|
| Race Condition | 재고 동시 차감 | Critical |
| 트랜잭션 미사용 | 주문/재고 정합성 | Critical |
| 보상 로직 부재 | 결제 성공 후 DB 실패 | Critical |
| HTTP 상태 코드 | 항상 200 반환 | Major |
| 동기 블로킹 + 타임아웃 미설정 | 서버 성능 저하 | Major |
| Import 누락 | Product, Order | Major |
| 응답 스키마 미정의 | 타입 안전성 부재 | Minor |
| float 변환 | Decimal 정밀도 손실 | Minor |
| URL trailing slash | 컨벤션 불일치 | Minor |
| 로깅 부재 | 운영 추적 불가 | Minor |
