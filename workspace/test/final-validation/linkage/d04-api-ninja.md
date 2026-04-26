# D04: architecture-api → implementation-django-ninja 위임 테스트

## 프롬프트

> API 설계가 끝났어. 이제 실제로 Django Ninja로 구현하려는데, Router랑 Schema 구조는 어떻게 잡으면 돼?

## 스킬 판정

- **진입 스킬**: architecture-api (API 설계 완료 언급)
- **위임 대상**: implementation-django-ninja (Django Ninja 구현 요청)
- **최종 스킬**: implementation-django-ninja
- **모드**: Writing (구현 구조 안내)

architecture-api SKILL.md에 명시된 위임 규칙: "Django Ninja API 구현(Schema, Router, 스로틀링)에 대해서는 implementation-django-ninja에 위임한다."

---

## 응답

Django Ninja에서 Router와 Schema 구조를 잡는 핵심 패턴은 **앱별 Router 분리**와 **용도별 Schema 분리**다.

### 프로젝트 구조

```
myproject/
├── myproject/
│   ├── api.py          # NinjaAPI 인스턴스, 라우터 합성, 글로벌 예외 핸들러
│   ├── settings.py
│   └── urls.py         # path("api/", api.urls)
├── orders/
│   ├── api.py          # Router() + 엔드포인트
│   ├── schemas.py      # OrderIn, OrderOut, OrderPatch 등
│   └── models.py
├── products/
│   ├── api.py          # Router() + 엔드포인트
│   ├── schemas.py      # ProductOut, ProductFilter 등
│   └── models.py
└── users/
    ├── api.py
    ├── schemas.py
    └── models.py
```

각 앱에 `api.py`(Router와 엔드포인트)와 `schemas.py`(Schema 정의)를 분리한다. Schema가 적으면 `api.py` 안에 두어도 되지만, 앱이 성장하면 분리하는 것이 유지보수에 유리하다.

### Router 합성

```python
# myproject/api.py
from ninja import NinjaAPI
from orders.api import router as orders_router
from products.api import router as products_router

api = NinjaAPI(title="MyService API", version="1.0.0")

api.add_router("/orders/", orders_router, tags=["orders"])
api.add_router("/products/", products_router, tags=["products"])
api.add_router("/users/", "users.api.router", tags=["users"])
```

```python
# myproject/urls.py
from django.urls import path
from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

```python
# orders/api.py
from ninja import Router
from .schemas import OrderIn, OrderOut, OrderListOut
from .models import Order

router = Router()

@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderIn) -> Order:
    return Order.objects.create(**payload.dict())

@router.get("/", response=list[OrderListOut])
def list_orders(request):
    return Order.objects.select_related("customer").all()

@router.get("/{order_id}", response=OrderOut)
def get_order(request, order_id: int) -> Order:
    return Order.objects.get(id=order_id)
```

핵심 규칙:
- 앱별로 `Router()`를 생성하고, 프로젝트 루트의 `NinjaAPI`에서 `add_router()`로 합성한다
- `tags` 파라미터로 OpenAPI 문서에서 엔드포인트를 그룹화한다
- 문자열 경로(`"users.api.router"`)로 지연 임포트가 가능하다
- 하위 리소스 URL은 최대 3단계 깊이로 유지한다

### Schema 설계 패턴

```python
# orders/schemas.py
from ninja import Schema, ModelSchema, PatchDict, Field
from .models import Order

# 생성 요청용 -- 클라이언트가 보내는 필드만
class OrderIn(Schema):
    product_id: int
    quantity: int
    shipping_address: str

# 목록 응답용 -- 최소 필드
class OrderListOut(ModelSchema):
    class Meta:
        model = Order
        fields = ["id", "status", "total_amount", "created_at"]

# 상세 응답용 -- 더 많은 필드
class OrderOut(ModelSchema):
    customer_name: str = ""

    class Meta:
        model = Order
        fields = ["id", "status", "total_amount", "shipping_address", "created_at"]

    @staticmethod
    def resolve_customer_name(obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"

# PATCH 요청용 -- PatchDict로 제공된 필드만 업데이트
class OrderUpdate(Schema):
    status: str
    shipping_address: str

@router.patch("/{order_id}", response=OrderOut)
def update_order(request, order_id: int, payload: PatchDict[OrderUpdate]):
    order = Order.objects.get(id=order_id)
    for attr, value in payload.items():
        setattr(order, attr, value)
    order.save()
    return order
```

Schema 설계의 핵심 원칙:
- **용도별 Schema 분리**: `XxxIn`(생성), `XxxOut`(상세 응답), `XxxListOut`(목록 응답), `XxxUpdate`(수정)로 나눈다
- **ModelSchema는 응답용**: `Meta.fields`로 노출할 필드를 명시적으로 선택한다. `fields = '__all__'`은 민감 데이터 노출 위험이 있으므로 사용하지 않는다
- **Schema는 요청용**: 클라이언트가 보내는 데이터만 정의한다. 모델 구조를 그대로 노출하지 않는다
- **계산 필드는 resolver**: `resolve_<field>` 정적 메서드로 동적 값을 계산한다
- **PATCH에는 PatchDict**: 제공된 필드만 포함하는 dict를 반환하여 부분 업데이트를 처리한다
- **타입 힌트 필수**: 모든 엔드포인트 매개변수와 반환 타입에 타입 힌트를 작성한다

---

> **관련 스킬 참조:**
> - [REST 원칙, URL 설계, 상태 코드, 버저닝 전략] → **architecture-api** 스킬
> - [Django 모델, ORM QuerySet, 마이그레이션] → **implementation-django** 스킬
> - [인증/페이지네이션/에러 처리/FilterSchema 구현] → **implementation-django-ninja** 스킬 (본 스킬의 추가 참조)
> - [Python 타입 힌트, async 패턴] → **implementation-python** 스킬
> - [API 엔드포인트 테스트, TestClient] → **implementation-test** 스킬
