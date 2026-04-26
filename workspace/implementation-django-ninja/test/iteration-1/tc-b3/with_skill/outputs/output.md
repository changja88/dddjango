# Django Ninja Code Review: `create_order` Endpoint

## Review Findings

### 1. Missing Response Type Hints

```
[Convention] -- Type hints are mandatory on all endpoint parameters and return types. 엔드포인트의 return type과 response schema가 지정되지 않았다. Django Ninja는 response= 파라미터로 응답 스키마를 명시하고, 상태 코드별 다중 응답 스키마를 지원한다. 이를 통해 OpenAPI 문서 자동 생성과 응답 데이터 검증이 가능해진다.
```

현재 코드는 `dict`를 직접 반환하며, 성공과 에러 응답의 구조가 문서화되지 않는다. `response={200: OrderOut, ...}` 형식으로 상태 코드별 스키마를 정의해야 한다.

---

### 2. Non-Standard Error Format (RFC 9457 위반)

```
[Convention] -- 모든 API 에러 응답은 RFC 9457 Problem Details 형식을 따라야 한다. 현재 코드는 {'error': ..., 'code': ...} 형태의 비표준 에러 형식을 사용하며, HTTP 상태 코드를 응답 본문에 넣고 있다. HTTP 상태 코드는 HTTP 응답 자체에 설정해야 하고, 에러 본문은 Problem Details(type, title, status, detail, instance) 형식을 따라야 한다.
```

`return {'error': 'Product not found', 'code': 404}`는 실제 HTTP 상태 코드 200으로 반환되면서 본문에 404를 담는 안티패턴이다. `HttpError`를 raise하거나, `@api.exception_handler()`로 등록한 핸들러를 통해 RFC 9457 형식으로 응답해야 한다.

---

### 3. Missing Authentication

```
[Convention] -- 인증이 필요한 엔드포인트에 auth가 설정되어 있지 않다. 주문 생성은 인증된 사용자만 접근할 수 있어야 한다. Django Ninja의 내장 인증 클래스(HttpBearer, APIKeyHeader, SessionAuth 등)를 사용하거나, 글로벌/라우터 수준에서 auth를 설정해야 한다.
```

---

### 4. Sync View with External I/O -- Should Be Async

```
[Convention] -- 외부 API 호출이 포함된 엔드포인트는 async로 작성해야 한다. 현재 requests.post()로 동기 HTTP 호출을 하고 있어 결제 API 응답을 기다리는 동안 워커 스레드가 블로킹된다. httpx.AsyncClient 또는 aiohttp 등을 사용한 async 뷰로 전환하면 동시 요청 처리 성능이 크게 향상된다.
```

비동기 지원 레퍼런스의 선택 가이드에 따르면, 외부 API 호출이 많은 엔드포인트는 async가 권장된다. ORM 호출은 Django 4.1+의 `aget()`, `acreate()`, `asave()` 등 네이티브 async 메서드를 사용한다.

---

### 5. Endpoint Doing Too Much (Fat Endpoint)

```
[Convention] -- 엔드포인트가 너무 많은 책임을 가지고 있다. 상품 조회, 재고 검증, 외부 결제 API 호출, 주문 생성, 재고 차감이 하나의 함수에 모두 들어 있다. 비즈니스 로직은 서비스 레이어로 분리하고, 엔드포인트는 요청 파싱과 응답 반환만 담당해야 한다.
```

---

### 6. Missing Input Validation on Schema

```
[Convention] -- Schema에 필드 수준 유효성 검증이 없다. quantity에 0이나 음수가 들어올 수 있다. Pydantic의 Field(gt=0) 또는 @field_validator를 사용하여 입력 값에 대한 제약 조건을 스키마 수준에서 정의해야 한다.
```

---

### 7. No Atomicity -- Race Condition on Stock

```
[Convention] -- 재고 확인과 차감이 원자적으로 수행되지 않는다. product.stock 확인 후 product.save()까지 사이에 동시 요청이 들어오면 재고 초과 판매가 발생할 수 있다. Django의 transaction.atomic()과 select_for_update() 또는 F() expression을 사용해야 한다.
```

이 부분은 Django ORM 영역(implementation-django)이지만, API 엔드포인트에서 직접 ORM 조작을 하고 있기 때문에 언급한다.

---

### 8. Routing: NinjaAPI Direct vs Router Pattern

```
[Convention] -- NinjaAPI 인스턴스에 직접 엔드포인트를 등록하고 있다. 권장 패턴은 앱별로 Router()를 사용하고, 메인에서 api.add_router()로 조합하는 것이다. 프로젝트가 커질수록 라우터 기반 구조가 유지보수에 유리하다.
```

---

## Review Checklist

| Item | Status |
|------|--------|
| DRF 패턴 사용 여부 | OK -- DRF 패턴 없음 |
| 엔드포인트 파라미터/반환 타입 힌트 | FAIL -- return type, response schema 미지정 |
| Schema 필드 노출 범위 | OK -- 명시적 필드 선언 |
| 인증 설정 | FAIL -- auth 미설정 |
| 리스트 엔드포인트 페이지네이션 | N/A -- 단일 리소스 생성 엔드포인트 |
| 에러 처리 / 표준 에러 형식 | FAIL -- 비표준 에러 형식, HTTP 상태 코드 미사용 |
| Sync에서 async 전환 필요 여부 | FAIL -- 외부 API 호출을 동기로 수행 |
| FilterSchema 사용 여부 | N/A -- 필터링 로직 없음 |
| 입력 유효성 검증 | FAIL -- Schema에 필드 제약 조건 없음 |
| 엔드포인트 책임 분리 | FAIL -- 비즈니스 로직이 엔드포인트에 집중 |

---

## Suggested Revision

아래는 위 리뷰 항목을 모두 반영한 개선 코드이다.

```python
import httpx
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from ninja import Router, Schema
from ninja.errors import HttpError
from pydantic import Field

from .models import Order, Product


router = Router(tags=["orders"])


# -- Schemas --

class OrderIn(Schema):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderOut(Schema):
    order_id: int
    total: Decimal


# -- Service Layer --

async def charge_payment(amount: Decimal) -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://payment.example.com/charge",
            json={"amount": float(amount)},
        )
    if resp.status_code != 200:
        raise HttpError(502, "Payment gateway rejected the charge.")


async def create_order_service(product_id: int, quantity: int) -> Order:
    product = await Product.objects.filter(id=product_id).select_for_update().afirst()
    if product is None:
        raise HttpError(404, "Product not found.")

    if product.stock < quantity:
        raise HttpError(409, "Insufficient stock.")

    total = product.price * quantity
    await charge_payment(total)

    order = await Order.objects.acreate(
        product=product,
        quantity=quantity,
        total=total,
    )
    await Product.objects.filter(id=product_id).aupdate(stock=F("stock") - quantity)
    return order


# -- Endpoint --

@router.post("/orders", response={201: OrderOut})
async def create_order(request, payload: OrderIn) -> tuple[int, OrderOut]:
    async with transaction.atomic():
        order = await create_order_service(payload.product_id, payload.quantity)
    return 201, OrderOut(order_id=order.id, total=order.total)
```

- `HttpError`를 raise하면 Django Ninja가 적절한 HTTP 상태 코드로 에러를 반환하며, `@api.exception_handler()`를 통해 RFC 9457 형식으로 일괄 변환할 수 있다.
- 인증은 `router = Router(auth=AuthBearer())` 또는 `api.add_router("/", orders_router, auth=AuthBearer())` 수준에서 적용한다.
