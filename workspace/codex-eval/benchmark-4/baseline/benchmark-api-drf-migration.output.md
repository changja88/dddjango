`/private/tmp/dddjango-codex-eval`에는 현재 `config.toml`이나 Django 코드 파일이 없어 프로젝트 맞춤 파일로 작성하지는 못했습니다. 대신 기존 DRF `Serializer/ViewSet` 기반 상품 API를 Django Ninja `Schema/Router` 구조로 옮기는 실무형 마이그레이션 가이드를 아래처럼 정리하면 됩니다.

**DRF 상품 API → Django Ninja 마이그레이션 가이드**

## 1. 목표 구조

기존 구조가 보통 다음과 같다면:

```text
products/
  models.py
  serializers.py
  views.py
  urls.py
```

Django Ninja 전환 후에는 다음처럼 분리한다.

```text
products/
  models.py
  schemas.py
  api.py
  services.py        # 선택
```

프로젝트 루트 또는 API 앱에는 Ninja 엔트리포인트를 둔다.

```text
config/
  urls.py
  api.py
```

## 2. DRF Serializer를 Ninja Schema로 변환

기존 DRF 예시:

```python
# products/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "created_at"]
        read_only_fields = ["id", "created_at"]
```

Ninja Schema 예시:

```python
# products/schemas.py
from datetime import datetime
from ninja import Schema

class ProductOut(Schema):
    id: int
    name: str
    price: int
    stock: int
    created_at: datetime

class ProductCreateIn(Schema):
    name: str
    price: int
    stock: int

class ProductUpdateIn(Schema):
    name: str | None = None
    price: int | None = None
    stock: int | None = None
```

핵심 차이:

- DRF `Serializer`는 validation, representation, create/update를 함께 담당한다.
- Ninja `Schema`는 Pydantic 기반 입출력 타입 정의에 가깝다.
- 생성/수정 로직은 Router 함수나 service layer로 이동하는 편이 좋다.

## 3. ViewSet을 Router 함수로 변환

기존 DRF ViewSet 예시:

```python
# products/views.py
from rest_framework.viewsets import ModelViewSet
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

Ninja Router 예시:

```python
# products/api.py
from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Product
from .schemas import ProductOut, ProductCreateIn, ProductUpdateIn

router = Router(tags=["products"])

@router.get("/", response=list[ProductOut])
def list_products(request):
    return Product.objects.all()

@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int):
    return get_object_or_404(Product, id=product_id)

@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn):
    product = Product.objects.create(**payload.dict())
    return 201, product

@router.patch("/{product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: ProductUpdateIn):
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)

    product.save()
    return product

@router.delete("/{product_id}", response={204: None})
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

## 4. URL 연결

DRF 기존 방식:

```python
# products/urls.py
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet)

urlpatterns = router.urls
```

Ninja 방식:

```python
# config/api.py
from ninja import NinjaAPI
from products.api import router as products_router

api = NinjaAPI(title="Commerce API")
api.add_router("/products", products_router)
```

```python
# config/urls.py
from django.urls import path
from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

최종 엔드포인트는 다음처럼 된다.

```text
GET     /api/products/
POST    /api/products/
GET     /api/products/{product_id}
PATCH   /api/products/{product_id}
DELETE  /api/products/{product_id}
```

## 5. 인증/권한 마이그레이션

DRF:

```python
permission_classes = [IsAuthenticated]
```

Ninja에서는 API 또는 Router/Endpoint 단위로 인증을 붙인다.

```python
from ninja.security import django_auth

@router.get("/", response=list[ProductOut], auth=django_auth)
def list_products(request):
    return Product.objects.all()
```

전체 API에 적용하려면:

```python
api = NinjaAPI(auth=django_auth)
```

권한 조건이 복잡하면 endpoint 내부에서 명시적으로 검사한다.

```python
if not request.user.is_staff:
    return 403, {"detail": "Forbidden"}
```

## 6. Pagination 처리

DRF `PageNumberPagination`을 사용했다면 Ninja에서는 명시적으로 limit/offset 또는 page 파라미터를 받는 방식이 단순하다.

```python
@router.get("/", response=list[ProductOut])
def list_products(request, limit: int = 20, offset: int = 0):
    return Product.objects.all()[offset:offset + limit]
```

응답에 total이 필요하면 별도 응답 Schema를 둔다.

```python
class ProductListOut(Schema):
    total: int
    items: list[ProductOut]
```

## 7. Serializer의 validate/create/update 대체

DRF Serializer에 있던 로직:

```python
def validate_price(self, value):
    if value < 0:
        raise serializers.ValidationError("가격은 0 이상이어야 합니다.")
    return value
```

Ninja/Pydantic에서는 Schema validator나 service 함수로 옮긴다.

```python
from pydantic import field_validator

class ProductCreateIn(Schema):
    name: str
    price: int
    stock: int

    @field_validator("price")
    @classmethod
    def validate_price(cls, value):
        if value < 0:
            raise ValueError("가격은 0 이상이어야 합니다.")
        return value
```

비즈니스 규칙이 DB 조회나 여러 모델을 건드리면 `services.py`로 분리하는 편이 좋다.

```python
# products/services.py
from .models import Product

def create_product(payload):
    return Product.objects.create(**payload.dict())
```

## 8. 테스트 변경 방향

DRF `APIClient` 기반 테스트는 Django test client 또는 Ninja test client로 변경한다.

```python
def test_create_product(client):
    response = client.post(
        "/api/products/",
        data={"name": "Keyboard", "price": 10000, "stock": 5},
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Keyboard"
```

기존 테스트에서 확인해야 할 항목:

- 상태 코드가 동일한지
- 응답 JSON 필드명이 유지되는지
- validation error 형식 변경이 허용 가능한지
- 인증 실패 응답이 기존 클라이언트와 호환되는지
- pagination 응답 구조가 바뀌는지

## 9. 마이그레이션 순서

1. `django-ninja`를 의존성에 추가한다.
2. `config/api.py`에 `NinjaAPI` 엔트리포인트를 만든다.
3. `products/schemas.py`에 기존 Serializer 필드를 입출력 Schema로 분리한다.
4. `products/api.py`에 list/detail/create/update/delete endpoint를 만든다.
5. 기존 DRF URL과 Ninja URL을 임시로 병행 운영한다.
6. 테스트를 Ninja endpoint 기준으로 추가한다.
7. 클라이언트 호출 경로를 전환한다.
8. 사용하지 않는 DRF ViewSet/Serializer/Router를 제거한다.

## 10. 주의할 점

- DRF `ModelSerializer`처럼 자동 create/update가 되지 않으므로 저장 로직을 직접 작성해야 한다.
- `read_only_fields`, `write_only_fields`는 입출력 Schema 분리로 표현한다.
- DRF의 permission/filter/search/pagination은 Ninja에서 직접 구현하거나 별도 유틸로 옮겨야 한다.
- 기존 API 응답 형식을 유지해야 한다면 Schema 이름보다 JSON shape을 우선한다.
- OpenAPI 문서는 Ninja가 자동 제공하므로 `/api/docs`에서 확인한다.

요약하면, `Serializer`는 `schemas.py`의 명시적인 입출력 타입으로, `ViewSet`은 `api.py`의 endpoint 함수들로 옮기면 된다. DRF가 암묵적으로 처리하던 validation, permission, pagination, create/update 동작은 Ninja에서는 코드로 드러내는 방향으로 정리하는 것이 핵심이다.