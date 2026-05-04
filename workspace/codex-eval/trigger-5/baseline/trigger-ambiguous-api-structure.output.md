`/private/tmp/dddjango-codex-eval`은 현재 비어 있고, 세션이 read-only라 파일을 직접 만들 수는 없습니다. 대신 이 프로젝트 정책에 맞춰 Django Ninja 기준으로 API 구조를 이렇게 잡는 게 깔끔합니다.

**권장 구조**
```text
config/
  api.py          # NinjaAPI 생성, 앱 router 합성
  urls.py         # /api/ 진입점 연결

apps/
  products/
    models.py
    schemas.py   # 요청/응답 Schema
    filters.py   # FilterSchema, 정렬 allow-list
    services.py  # 비즈니스 로직
    selectors.py # 읽기 전용 QuerySet 조립
    api.py       # Router + endpoint
    tests/
      test_api.py
```

**URL 규칙**
```text
GET    /api/v1/products
POST   /api/v1/products
GET    /api/v1/products/{product_id}
PATCH  /api/v1/products/{product_id}
DELETE /api/v1/products/{product_id}

GET    /api/v1/products?status=active&q=keyboard&sort=-created_at&limit=50&cursor=...
```

핵심 원칙은 다음으로 고정하면 됩니다.

- 리소스는 복수 명사: `/products`, `/orders`
- URL에 동사 금지: `/create-product` 대신 `POST /products`
- 버전은 우선 `/api/v1/...`
- 목록 API는 항상 페이지네이션
- 정렬 필드는 allow-list로 제한
- 에러 응답은 RFC 9457 Problem Details
- 생성성 `POST` 중 중복이 위험한 API는 `Idempotency-Key` 지원

**Django Ninja 합성 예시**
```python
# config/api.py
from ninja import NinjaAPI

from apps.products.api import router as products_router

api = NinjaAPI(
    title="Service API",
    version="1.0.0",
)

api.add_router("/v1/products", products_router)
```

```python
# config/urls.py
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

```python
# apps/products/api.py
from ninja import Router, Query
from django.shortcuts import get_object_or_404

from .models import Product
from .schemas import ProductIn, ProductOut, ProductPatch
from .filters import ProductFilter
from .selectors import list_products
from .services import create_product, update_product

router = Router(tags=["products"])


@router.get("", response=list[ProductOut])
def product_list(request, filters: Query[ProductFilter]) -> list[Product]:
    return list_products(filters)


@router.post("", response={201: ProductOut})
def product_create(request, payload: ProductIn) -> tuple[int, Product]:
    return 201, create_product(payload)


@router.get("/{product_id}", response=ProductOut)
def product_detail(request, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.patch("/{product_id}", response=ProductOut)
def product_update(request, product_id: int, payload: ProductPatch) -> Product:
    product = get_object_or_404(Product, id=product_id)
    return update_product(product, payload)


@router.delete("/{product_id}", response={204: None})
def product_delete(request, product_id: int) -> tuple[int, None]:
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

**에러 포맷 표준**
```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation error",
  "status": 422,
  "detail": "Request body is invalid.",
  "instance": "/api/v1/products"
}
```

직접 적용하려면 먼저 실제 Django 프로젝트 파일이 있어야 합니다. 현재 워크스페이스가 비어 있어서 구현/테스트 실행은 하지 못했습니다.

---
> **관련 스킬 참조:**
> - Django Ninja 구현 → **implementation-django-ninja** 스킬
> - 도메인/서비스 레이어 분리 → **architecture-ddd** 스킬
> - 테스트 작성 → **implementation-test** 스킬