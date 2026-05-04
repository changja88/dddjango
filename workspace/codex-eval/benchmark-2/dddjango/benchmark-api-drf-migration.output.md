**마이그레이션 가이드**

이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 기존 상품 API의 책임은 다음처럼 옮깁니다.

| 기존 DRF 책임 | Django Ninja 전환 |
|---|---|
| `Serializer`, `ModelSerializer` | 요청/응답 `Schema` 또는 제한된 `ModelSchema` |
| `ViewSet` 액션 | 앱별 `Router()` + `@router.get/post/patch/delete` |
| `DefaultRouter`, `SimpleRouter` | `NinjaAPI.add_router()` |
| `permission_classes` | `auth=django_auth`, `HttpBearer`, `APIKeyHeader` 등 |
| `serializer.save()` 비즈니스 처리 | application service |
| `get_queryset()` 읽기 최적화 | selector 또는 QuerySet 함수 |
| DRF validation | Schema 검증 + 도메인/application service 검증 |

**권장 구조**

```text
products/
  schemas.py
  api.py
  selectors.py
  services.py
config/
  api.py
  urls.py
```

`Serializer`는 입출력 계약만 담당하도록 `Schema`로 나누고, 상품 생성/수정 규칙은 service로 이동합니다. 엔드포인트는 얇게 유지합니다.

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


class ProductPatchIn(Schema):
    name: str | None = None
    price: Decimal | None = None
```

```python
# products/selectors.py
from django.db.models import QuerySet

from products.models import Product


def product_list() -> QuerySet[Product]:
    return Product.objects.order_by("-created_at")


def product_detail(product_id: int) -> Product:
    return Product.objects.get(pk=product_id)
```

```python
# products/services.py
from django.db import transaction

from products.models import Product


@transaction.atomic
def product_create(*, name: str, price) -> Product:
    return Product.objects.create(name=name, price=price)


@transaction.atomic
def product_update(*, product: Product, data: dict) -> Product:
    for field, value in data.items():
        if value is not None:
            setattr(product, field, value)
    product.save(update_fields=[k for k, v in data.items() if v is not None])
    return product
```

```python
# products/api.py
from ninja import Router
from ninja.pagination import paginate
from ninja.security import django_auth

from products.schemas import ProductCreateIn, ProductOut, ProductPatchIn
from products.selectors import product_detail, product_list
from products.services import product_create, product_update

router = Router(auth=django_auth)


@router.get("/", response=list[ProductOut])
@paginate
def list_products(request):
    return product_list()


@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int):
    return product_detail(product_id)


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn):
    return 201, product_create(**payload.dict())


@router.patch("/{product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: ProductPatchIn):
    product = product_detail(product_id)
    return product_update(product=product, data=payload.dict(exclude_unset=True))
```

```python
# config/api.py
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(title="Product API", version="1.0.0")
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

**전환 순서**

1. 기존 상품 엔드포인트 목록을 고정합니다: list, detail, create, update, delete, 검색/필터.
2. DRF `Serializer` 필드를 `ProductOut`, `ProductCreateIn`, `ProductPatchIn`으로 분리합니다. 모든 모델 필드를 노출하지 않습니다.
3. `ViewSet`의 `get_queryset()`은 `selectors.py`로, `perform_create/update`는 `services.py`로 이동합니다.
4. `ViewSet` 액션을 `Router` 함수로 1:1 이전합니다.
5. 인증은 DRF permission이 아니라 Router 또는 endpoint의 `auth=`로 적용합니다.
6. 목록 API에는 `@paginate`를 먼저 붙이고, 기존 응답 형식과 다르면 v2 또는 호환 어댑터를 둡니다.
7. 오류 응답은 가능하면 RFC 9457 Problem Details 형태로 통일합니다.

**회귀 테스트 전략**

- 기존 DRF API의 golden response를 저장하고 Ninja 응답과 필드, 상태 코드, 정렬 순서를 비교합니다.
- `GET /api/products/`는 페이지네이션, 정렬, 필터 파라미터를 포함해 테스트합니다.
- `POST/PATCH`는 정상 케이스와 가격 음수, 필수값 누락, 권한 없음 케이스를 검증합니다.
- 읽기 API에는 `assertNumQueries`로 N+1 회귀를 잡습니다.
- OpenAPI 문서가 `/api/docs`에서 생성되는지 확인합니다.

검증 명령:

```bash
python manage.py test products
python manage.py check
```

---
> **관련 스킬 참조:**
> - API 설계/상태 코드/페이지네이션 → **architecture-api** 스킬
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬