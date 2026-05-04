## [주요 내용]

이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 요청 검증용 “serializer 클래스”는 DRF `Serializer`가 아니라 Django Ninja `Schema`로 만들면 됩니다. `Schema`를 엔드포인트 인자로 선언하면 요청 body 검증이 자동으로 걸립니다.

```python
# apps/orders/schemas.py
from decimal import Decimal
from enum import StrEnum

from ninja import Schema
from pydantic import Field, field_validator, model_validator


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"


class OrderCreateRequest(Schema):
    """주문 생성 요청 값을 검증한다."""

    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)
    unit_price: Decimal = Field(gt=Decimal("0"))
    status: OrderStatus = OrderStatus.PENDING
    memo: str | None = Field(default=None, max_length=500)

    @field_validator("memo")
    @classmethod
    def normalize_memo(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_total_amount(self) -> "OrderCreateRequest":
        if self.quantity * self.unit_price > Decimal("1000000"):
            raise ValueError("주문 금액은 1,000,000을 초과할 수 없습니다.")
        return self


class OrderCreateResponse(Schema):
    """주문 생성 응답 값을 직렬화한다."""

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    status: OrderStatus
```

```python
# apps/orders/api.py
from ninja import Router

from apps.orders.models import Order
from apps.orders.schemas import OrderCreateRequest, OrderCreateResponse

router = Router(tags=["orders"])


@router.post("/", response={201: OrderCreateResponse})
def create_order(request, payload: OrderCreateRequest) -> tuple[int, Order]:
    """검증된 요청 값으로 주문을 생성한다."""

    order = Order.objects.create(
        product_id=payload.product_id,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        status=payload.status,
        memo=payload.memo,
    )
    return 201, order
```

```python
# config/api.py
from ninja import NinjaAPI

from apps.orders.api import router as orders_router

api = NinjaAPI()
api.add_router("/orders/", orders_router)
```

```python
# config/urls.py
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

핵심은 이겁니다:

`OrderCreateRequest`가 요청 검증 클래스입니다. DRF의 `Serializer.is_valid()`를 직접 호출하지 않고, Ninja가 `payload: OrderCreateRequest` 타입 힌트를 보고 JSON body를 자동 파싱하고 검증합니다. 검증 실패 시 422 응답이 자동으로 반환되고 OpenAPI 문서에도 스키마가 반영됩니다.

PEP 695 제네릭은 이 예시에서 제네릭 타입이 없어 사용하지 않았습니다.

## [관련 스킬 참조]

---
> **관련 스킬 참조:**
> - 요청/응답 Schema와 Router 구성 → **implementation-django-ninja** 스킬