작업 디렉터리에 `config.toml`이나 Django 소스 파일이 없어 실제 파일 기준으로 저장소 문서는 만들 수 없었습니다. 대신 기존 DRF `Serializer/ViewSet` 상품 API를 Django Ninja `Schema/Router` 구조로 옮기는 마이그레이션 가이드를 바로 붙여 넣어 쓸 수 있는 형태로 정리했습니다.

**DRF → Django Ninja 상품 API 마이그레이션 가이드**

참고 문서: Django Ninja의 `Router`, `Schema`, `ModelSchema`는 공식 문서 기준으로 정리했습니다.  
Sources: [Django Ninja Routers](https://django-ninja.dev/guides/routers/), [Django Ninja ModelSchema](https://django-ninja.dev/guides/response/django-pydantic/), [Django Ninja Response Schema](https://django-ninja.dev/guides/response/), [DRF ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)

## 1. 목표 구조

기존 DRF 구조:

```python
products/
  serializers.py
  views.py
  urls.py
```

권장 Ninja 구조:

```python
products/
  schemas.py
  api.py
  services.py      # 선택: 비즈니스 로직 분리
  models.py

project/
  api.py
  urls.py
```

DRF의 역할을 다음처럼 옮긴다.

| DRF | Django Ninja |
|---|---|
| `ModelSerializer` | `ModelSchema` 또는 `Schema` |
| `ViewSet` / `ModelViewSet` | `Router` 함수 기반 endpoint |
| `DefaultRouter.register()` | `api.add_router()` |
| `serializer.is_valid()` | 함수 인자의 타입 검증 |
| `serializer.save()` | 명시적 ORM 생성/수정 |
| `Response(data, status=...)` | 객체/딕셔너리 반환 또는 `Status(...)` |
| `@action` | 별도 `@router.get/post(...)` endpoint |

## 2. Schema 작성

기존 DRF 예시:

```python
# products/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]
```

Ninja로 변경:

```python
# products/schemas.py
from ninja import ModelSchema, Schema
from .models import Product

class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "is_active", "created_at"]

class ProductCreateIn(ModelSchema):
    class Meta:
        model = Product
        fields = ["name", "price", "stock", "is_active"]

class ProductUpdateIn(ModelSchema):
    class Meta:
        model = Product
        fields = ["name", "price", "stock", "is_active"]
        fields_optional = "__all__"

class ErrorOut(Schema):
    detail: str
```

주의할 점:

- `ModelSchema`에서 `fields = "__all__"`는 피한다. 내부 필드나 민감한 필드가 노출될 수 있다.
- `PATCH`용 Schema는 `fields_optional = "__all__"`를 사용한다.
- 부분 수정 시 `payload.dict(exclude_unset=True)` 또는 Pydantic v2 환경에서는 `payload.model_dump(exclude_unset=True)`를 사용한다. 프로젝트의 Pydantic 버전에 맞춰 하나로 통일한다.

## 3. Router 작성

기존 DRF ViewSet:

```python
# products/views.py
from rest_framework.viewsets import ModelViewSet
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

Ninja Router:

```python
# products/api.py
from django.shortcuts import get_object_or_404
from ninja import Router, Status

from .models import Product
from .schemas import ProductOut, ProductCreateIn, ProductUpdateIn, ErrorOut

router = Router(tags=["products"])

@router.get("/", response=list[ProductOut])
def list_products(request):
    return Product.objects.all()

@router.get("/{product_id}", response={200: ProductOut, 404: ErrorOut})
def get_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product

@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn):
    product = Product.objects.create(**payload.dict())
    return Status(201, product)

@router.patch("/{product_id}", response={200: ProductOut, 404: ErrorOut})
def update_product(request, product_id: int, payload: ProductUpdateIn):
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)

    product.save()
    return product

@router.delete("/{product_id}", response={204: None, 404: ErrorOut})
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return Status(204, None)
```

## 4. 최상위 API 연결

```python
# project/api.py
from ninja import NinjaAPI
from products.api import router as products_router

api = NinjaAPI(title="Product API")

api.add_router("/products/", products_router)
```

```python
# project/urls.py
from django.contrib import admin
from django.urls import path
from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

결과 endpoint:

```text
GET     /api/products/
POST    /api/products/
GET     /api/products/{product_id}
PATCH   /api/products/{product_id}
DELETE  /api/products/{product_id}
```

## 5. Query Parameter, 검색, 필터링

DRF에서 `filter_backends`, `search_fields`, `ordering_fields`를 쓰던 경우 Ninja에서는 명시적으로 받는 편이 좋다.

```python
from ninja import Query, Schema

class ProductFilter(Schema):
    q: str | None = None
    is_active: bool | None = None
    min_price: int | None = None
    max_price: int | None = None

@router.get("/", response=list[ProductOut])
def list_products(request, filters: ProductFilter = Query(...)):
    qs = Product.objects.all()

    if filters.q:
        qs = qs.filter(name__icontains=filters.q)
    if filters.is_active is not None:
        qs = qs.filter(is_active=filters.is_active)
    if filters.min_price is not None:
        qs = qs.filter(price__gte=filters.min_price)
    if filters.max_price is not None:
        qs = qs.filter(price__lte=filters.max_price)

    return qs
```

## 6. DRF `@action` 변환

기존:

```python
@action(detail=True, methods=["post"])
def activate(self, request, pk=None):
    ...
```

Ninja:

```python
@router.post("/{product_id}/activate", response=ProductOut)
def activate_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = True
    product.save(update_fields=["is_active"])
    return product
```

## 7. 마이그레이션 순서

1. 기존 `ProductSerializer`의 `fields`, `read_only_fields`, `validate_*`, `create`, `update`를 목록화한다.
2. 응답용 `ProductOut`, 생성용 `ProductCreateIn`, 수정용 `ProductUpdateIn`을 분리한다.
3. `ProductViewSet`의 `list/retrieve/create/update/destroy` 동작을 `products/api.py` 함수로 옮긴다.
4. `@action` endpoint를 명시적 URL로 옮긴다.
5. 인증/권한 정책을 전역 `NinjaAPI`, router, 또는 개별 endpoint 단위로 다시 연결한다.
6. 기존 DRF URL과 Ninja URL을 일정 기간 병행 운영하거나, API 버전을 `/api/v2/products/`로 분리한다.
7. 기존 serializer 테스트를 Ninja endpoint 테스트로 교체한다.
8. OpenAPI 문서(`/api/docs`)에서 request/response schema가 의도대로 노출되는지 확인한다.

## 8. 테스트 체크리스트

- `GET /api/products/` 목록 응답 필드가 기존 API와 호환되는가
- `POST`에서 필수값 누락 시 422 validation error가 발생하는가
- `PATCH`에서 전달하지 않은 필드가 `None`으로 덮이지 않는가
- 삭제 후 204 응답이 정상인가
- 가격, 재고 같은 숫자 필드의 타입 검증이 되는가
- 기존 클라이언트가 trailing slash, 응답 status code, error format 차이를 감당할 수 있는가

핵심은 DRF의 암묵적 `ModelViewSet` 동작을 Ninja에서는 명시적인 함수 endpoint로 푸는 것입니다. 상품 API처럼 CRUD 중심인 경우에는 `Schema` 분리와 `PATCH`의 `exclude_unset=True` 처리만 제대로 잡으면 비교적 안정적으로 옮길 수 있습니다.