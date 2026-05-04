이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja `Schema`/`Router`로 작성합니다. 아래는 기존 상품 API를 `Serializer`/`ViewSet` 구조에서 Ninja 구조로 옮길 때의 마이그레이션 가이드입니다.

**마이그레이션 목표**
DRF 기준 구조:

```text
products/
  serializers.py
  views.py
  urls.py
```

Ninja 기준 구조:

```text
products/
  schemas.py
  api.py
config/
  api.py
  urls.py
```

핵심 변환은 다음과 같습니다.

| DRF | Django Ninja |
|---|---|
| `ModelSerializer` | `Schema` 또는 `ModelSchema` |
| `ViewSet` | `Router` + `@router.get/post/patch/delete` |
| `DefaultRouter`, `SimpleRouter` | `NinjaAPI.add_router()` |
| `permission_classes` | `auth=` |
| `Response(...)` | 일반 객체 반환 또는 `(status, data)` 반환 |
| `serializer.is_valid()` | 요청 `Schema` 자동 검증 |
| `serializer.save()` | 서비스 함수 또는 ORM 직접 호출 |

**1. Serializer를 Schema로 변환**

Before:

```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "is_active"]
```

After:

```python
# products/schemas.py
from decimal import Decimal

from ninja import ModelSchema, Schema

from products.models import Product


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "is_active"]


class ProductCreateIn(Schema):
    name: str
    price: Decimal
    stock: int = 0
    is_active: bool = True


class ProductUpdateIn(Schema):
    name: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    is_active: bool | None = None
```

`fields = "__all__"`은 사용하지 않습니다. 상품 모델에 내부 원가, 공급사 메모, 삭제 플래그 같은 필드가 생기면 API로 그대로 노출될 수 있습니다.

**2. ViewSet을 Router 엔드포인트로 변환**

Before:

```python
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

After:

```python
# products/api.py
from typing import Any

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate

from products.models import Product
from products.schemas import ProductCreateIn, ProductOut, ProductUpdateIn

router = Router(tags=["products"])


@router.get("/", response=list[ProductOut])
@paginate(LimitOffsetPagination)
def list_products(request: Any) -> Product.objects.none().__class__:
    return Product.objects.filter(is_active=True).order_by("-id")


@router.get("/{product_id}", response=ProductOut)
def get_product(request: Any, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.post("/", response={201: ProductOut})
def create_product(request: Any, payload: ProductCreateIn) -> tuple[int, Product]:
    product = Product.objects.create(**payload.model_dump())
    return 201, product


@router.patch("/{product_id}", response=ProductOut)
def update_product(
    request: Any,
    product_id: int,
    payload: ProductUpdateIn,
) -> Product:
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    product.save(update_fields=list(payload.model_dump(exclude_unset=True).keys()))
    return product


@router.delete("/{product_id}", response={204: None})
def delete_product(request: Any, product_id: int) -> tuple[int, None]:
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

실무에서는 `create_product`, `update_product`, `delete_product` 안의 비즈니스 로직을 `products/services.py`로 빼는 편이 좋습니다. API 함수는 입력 검증, 인증, 상태 코드, 서비스 호출만 담당하게 둡니다.

**3. Router 등록**

DRF의 `DefaultRouter` 대신 최상위 `NinjaAPI`에 앱 라우터를 직접 연결합니다.

```python
# config/api.py
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(title="Shop API", version="1.0.0")
api.add_router("/products/", products_router)
```

```python
# config/urls.py
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

**4. 인증 변환**

Before:

```python
permission_classes = [IsAuthenticated]
```

After:

```python
from ninja.security import django_auth

router = Router(auth=django_auth, tags=["products"])
```

공개 목록 API만 예외로 열어야 하면 엔드포인트에 `auth=None`을 둡니다.

```python
@router.get("/", response=list[ProductOut], auth=None)
def list_products(request: Any):
    ...
```

**5. 필터링과 페이지네이션**

목록 API는 기본적으로 페이지네이션을 붙입니다. 필터가 늘어나면 개별 쿼리 파라미터보다 `Schema`로 묶습니다.

```python
from decimal import Decimal

from ninja import Query, Schema


class ProductFilter(Schema):
    q: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None


@router.get("/", response=list[ProductOut])
@paginate(LimitOffsetPagination)
def list_products(request: Any, filters: Query[ProductFilter]):
    qs = Product.objects.filter(is_active=True)

    if filters.q:
        qs = qs.filter(name__icontains=filters.q)
    if filters.min_price is not None:
        qs = qs.filter(price__gte=filters.min_price)
    if filters.max_price is not None:
        qs = qs.filter(price__lte=filters.max_price)

    return qs.order_by("-id")
```

**6. 에러 응답 표준화**

단순 404는 `get_object_or_404`로 충분합니다. 도메인 에러가 있으면 `HttpError` 또는 `@api.exception_handler()`를 사용하고, 가능하면 RFC 9457 Problem Details 형식으로 통일합니다.

```python
# config/api.py
from django.http import JsonResponse
from ninja.errors import HttpError


@api.exception_handler(HttpError)
def handle_http_error(request, exc):
    return JsonResponse(
        {
            "type": "about:blank",
            "title": str(exc),
            "status": exc.status_code,
            "detail": str(exc),
            "instance": request.path,
        },
        status=exc.status_code,
        content_type="application/problem+json",
    )
```

**마이그레이션 체크리스트**
- `rest_framework` import 제거
- `serializers.py`를 `schemas.py`로 대체
- `ViewSet` 메서드를 `@router.get/post/patch/delete` 함수로 분리
- `DefaultRouter` 등록을 `api.add_router()`로 교체
- 목록 API에 `@paginate` 적용
- 요청 본문은 전부 `Schema`로 받기
- 응답 스키마는 명시적 필드만 노출
- 인증은 `auth=`로 적용
- 삭제는 `204, None` 반환
- 테스트는 DRF `APIClient` 대신 Ninja `TestClient` 또는 Django client 기준으로 갱신

---
> **관련 스킬 참조:**
> - Django Ninja API 마이그레이션 → **implementation-django-ninja** 스킬