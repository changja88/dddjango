이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. Fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 파일이 없었고, 읽기 전용 환경이므로 변경 diff 대신 마이그레이션 가이드를 제공합니다.

**마이그레이션 목표**

기존 상품 API의 책임을 다음처럼 옮깁니다.

| 기존 책임 | Django Ninja 전환 위치 |
|---|---|
| 입력/출력 검증 | `Schema` / `ModelSchema` |
| 목록/상세/생성/수정/삭제 액션 | 앱별 `Router()` + `@router.get/post/patch/delete` |
| 비즈니스 규칙, 트랜잭션 | application service |
| 읽기 전용 조회 최적화 | selector |
| 인증/권한 | `auth=` 또는 라우터/API 수준 인증 |
| URL 등록 | `NinjaAPI.add_router()` |

**권장 파일 구조**

```text
products/
  api.py
  schemas.py
  selectors.py
  services.py
config/
  api.py
  urls.py
```

**Schema**

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

**Selector / Service**

```python
# products/selectors.py
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from products.models import Product


def product_list() -> QuerySet[Product]:
    return Product.objects.order_by("-created_at")


def product_get(product_id: int) -> Product:
    return get_object_or_404(Product, pk=product_id)
```

```python
# products/services.py
from django.db import transaction

from products.models import Product
from products.schemas import ProductCreateIn, ProductPatchIn


@transaction.atomic
def product_create(payload: ProductCreateIn) -> Product:
    return Product.objects.create(**payload.dict())


@transaction.atomic
def product_patch(product: Product, payload: ProductPatchIn) -> Product:
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)
    product.full_clean()
    product.save(update_fields=list(payload.dict(exclude_unset=True).keys()))
    return product
```

**Router**

```python
# products/api.py
from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate

from products.schemas import ProductCreateIn, ProductOut, ProductPatchIn
from products.selectors import product_get, product_list
from products.services import product_create, product_patch

router = Router(tags=["products"])


@router.get("/", response=list[ProductOut])
@paginate
def list_products(request: HttpRequest) -> list[ProductOut]:
    return list(product_list())


@router.get("/{product_id}", response=ProductOut)
def get_product(request: HttpRequest, product_id: int) -> ProductOut:
    return product_get(product_id)


@router.post("/", response={201: ProductOut})
def create_product(request: HttpRequest, payload: ProductCreateIn) -> tuple[int, ProductOut]:
    return 201, product_create(payload)


@router.patch("/{product_id}", response=ProductOut)
def patch_product(
    request: HttpRequest,
    product_id: int,
    payload: ProductPatchIn,
) -> ProductOut:
    product = product_get(product_id)
    return product_patch(product, payload)
```

**API 합성**

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

**전환 순서**

1. 기존 상품 API의 URL, 응답 필드, 상태 코드, 인증 요구사항을 테스트로 고정합니다.
2. 응답 전용 `ProductOut`부터 만들고 목록/상세 GET을 Router로 옮깁니다.
3. 생성/수정 입력 Schema를 분리합니다. 모든 모델 필드를 자동 노출하지 않습니다.
4. 저장 로직은 endpoint 안에 두지 말고 `services.py`로 이동합니다.
5. 조회 최적화와 404 처리는 `selectors.py`에 둡니다.
6. 기존 라우팅과 새 Ninja 라우팅을 짧게 병행한 뒤 클라이언트 전환이 끝나면 기존 API를 제거합니다.
7. 에러 응답은 가능하면 RFC 9457 Problem Details 형식으로 통일합니다.

**회귀 테스트 전략**

```bash
python manage.py check
pytest
```

추가로 다음을 고정하세요.

- 목록/상세 응답 필드와 타입 스냅샷
- 생성 성공 시 `201`
- 존재하지 않는 상품 조회 시 `404`
- PATCH가 전달된 필드만 변경하는지
- 목록 API 페이지네이션 응답
- 인증이 필요한 쓰기 API의 미인증 요청 차단
- 목록 API의 쿼리 수 회귀 방지: `assertNumQueries`

---
> **관련 스킬 참조:**
> - API 구현 전환 → **implementation-django-ninja** 스킬
> - REST 응답/상태 코드 검토 → **architecture-api** 스킬