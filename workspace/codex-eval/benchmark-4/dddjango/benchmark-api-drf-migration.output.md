이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 전환합니다.

**[주요 내용]**

기존 상품 API의 책임은 다음처럼 나눕니다.

| 기존 DRF 책임 | Django Ninja 전환 위치 |
|---|---|
| `Serializer` 입력 검증 | `Schema` |
| `ModelSerializer` 응답 직렬화 | `ModelSchema` 또는 명시적 `Schema` |
| `ViewSet.list/retrieve/create/update/destroy` | `Router`의 `@router.get/post/patch/delete` |
| `DefaultRouter/SimpleRouter` | `NinjaAPI.add_router()` |
| `permission_classes` | `auth=` 또는 router/API 단위 인증 |
| `serializer.save()` 내부 처리 | application service |
| `get_queryset()` 필터/정렬 | selector + `FilterSchema` |

전환 목표 구조:

```text
products/
  schemas.py
  selectors.py
  services.py
  api.py
config/
  api.py
  urls.py
```

핵심 예시는 상품 모델이 `Product(id, name, price, status, created_at)`를 가진다고 가정합니다.

```python
# products/schemas.py
from decimal import Decimal

from ninja import ModelSchema, Schema

from products.models import Product


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "status", "created_at"]


class ProductCreateIn(Schema):
    name: str
    price: Decimal
    status: str = "draft"


class ProductUpdateIn(Schema):
    name: str | None = None
    price: Decimal | None = None
    status: str | None = None
```

```python
# products/selectors.py
from django.db.models import QuerySet

from products.models import Product


def product_list() -> QuerySet[Product]:
    return Product.objects.order_by("-created_at")


def product_get(product_id: int) -> Product:
    return Product.objects.get(id=product_id)
```

```python
# products/services.py
from products.models import Product
from products.schemas import ProductCreateIn, ProductUpdateIn


def product_create(data: ProductCreateIn) -> Product:
    return Product.objects.create(**data.dict())


def product_update(product: Product, data: ProductUpdateIn) -> Product:
    for field, value in data.dict(exclude_unset=True).items():
        setattr(product, field, value)
    product.save(update_fields=list(data.dict(exclude_unset=True).keys()))
    return product
```

```python
# products/api.py
from ninja import Router
from ninja.pagination import paginate

from products.schemas import ProductCreateIn, ProductOut, ProductUpdateIn
from products.selectors import product_get, product_list
from products.services import product_create, product_update

router = Router(tags=["products"])


@router.get("/", response=list[ProductOut])
@paginate
def list_products(request):
    return product_list()


@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int):
    return product_get(product_id)


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn):
    return 201, product_create(payload)


@router.patch("/{product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: ProductUpdateIn):
    return product_update(product_get(product_id), payload)


@router.delete("/{product_id}", response={204: None})
def delete_product(request, product_id: int):
    product_get(product_id).delete()
    return 204, None
```

```python
# config/api.py
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(title="Product API")
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

전환 순서:

1. 현재 DRF 엔드포인트별 동작을 고정합니다: URL, method, status code, request body, response body, pagination, auth, error case.
2. `Serializer`를 `Schema`로 옮기되, 모든 모델 필드를 노출하지 말고 공개 필드만 명시합니다.
3. `ViewSet` 액션을 `Router` 함수로 1:1 이동합니다.
4. `serializer.save()`나 뷰 내부 비즈니스 로직은 `services.py`로 이동합니다.
5. `get_queryset()`의 조회/필터/정렬은 `selectors.py`와 `FilterSchema`로 분리합니다.
6. `DefaultRouter/SimpleRouter` 등록은 `NinjaAPI.add_router()`로 바꿉니다.
7. 인증은 DRF permission이 아니라 Django Ninja의 `auth=` 정책으로 라우터 또는 엔드포인트에 적용합니다.
8. DRF URL을 바로 제거하지 말고, 회귀 테스트가 통과한 뒤 같은 API 버전에서 교체하거나 `/api/v2/products/`처럼 새 버전으로 병행합니다.

회귀 테스트 전략:

```python
# tests/test_products_api.py
import pytest
from ninja.testing import TestClient

from config.api import api
from products.models import Product

client = TestClient(api)


@pytest.mark.django_db
def test_list_products_returns_products():
    Product.objects.create(name="Keyboard", price="120.00", status="active")

    response = client.get("/products/")

    assert response.status_code == 200
    assert response.json()["items"][0]["name"] == "Keyboard"


@pytest.mark.django_db
def test_create_product_returns_201():
    response = client.post(
        "/products/",
        json={"name": "Mouse", "price": "45.00", "status": "active"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Mouse"
```

검증 명령:

```bash
pytest tests/test_products_api.py
pytest
python manage.py check
```

DRF 제거 전에는 기존 API와 Ninja API의 응답 스냅샷을 비교합니다. 특히 목록 pagination envelope, decimal/string 표현, 404/422 오류 형식, 인증 실패의 401/403 차이를 고정 테스트로 잡아야 합니다.

---
> **관련 스킬 참조:**
> - REST URL/status/error 설계 → **architecture-api** 스킬
> - Django 서비스/selector 분리 → **implementation-django** 스킬
> - Schema/Router/API 테스트 구현 → **implementation-django-ninja** 스킬