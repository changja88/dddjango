이 프로젝트 정책상 DRF 코드는 새로 만들지 않고 Django Ninja로 전환합니다. 지정 fixture path `/Users/hyun/Desktop/dddjango/none`와 현재 작업 디렉터리에는 읽을 fixture 파일이 없어서, 아래는 `products` 앱의 `Product` 모델이 이미 있다는 가정의 마이그레이션 가이드입니다.

**책임 매핑**

| 기존 책임 | Django Ninja 전환 위치 |
|---|---|
| Serializer 출력 필드 | `products/schemas.py`의 `Schema` 또는 `ModelSchema` |
| Serializer 입력 검증 | `ProductCreateIn`, `ProductUpdateIn` |
| ViewSet action | `products/api.py`의 `Router` 엔드포인트 |
| queryset 구성 | `products/selectors.py` |
| create/update/delete 유스케이스 | `products/services.py` |
| router 등록 | `config/api.py`의 `api.add_router()` |

**전환 순서**

1. `schemas.py`를 먼저 추가한다. 응답 필드는 명시적으로 제한하고, `fields = "__all__"`은 쓰지 않는다.
2. 목록/상세 조회를 `selectors.py`로 옮긴다. 목록은 페이지네이션을 고려해 `QuerySet`을 반환한다.
3. 생성/수정/삭제 로직을 `services.py`로 분리한다. 트랜잭션, 재고/가격 같은 도메인 규칙은 endpoint 안에 두지 않는다.
4. `api.py`에 `Router()`를 만들고 `@router.get/post/patch/delete`로 기존 action을 1:1 매핑한다.
5. `config/api.py`에서 앱 라우터를 `NinjaAPI.add_router()`로 합성한다.
6. 기존 API와 응답 shape가 맞는지 회귀 테스트를 통과시킨 뒤, 기존 Serializer/ViewSet 라우팅을 제거한다.

**핵심 코드 예시**

```python
# products/schemas.py
from decimal import Decimal

from ninja import ModelSchema, Schema

from products.models import Product


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "is_active", "created_at"]


class ProductCreateIn(Schema):
    name: str
    price: Decimal


class ProductUpdateIn(Schema):
    name: str | None = None
    price: Decimal | None = None
    is_active: bool | None = None
```

```python
# products/selectors.py
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from products.models import Product


def product_list() -> QuerySet[Product]:
    return Product.objects.filter(is_active=True).order_by("-created_at")


def product_get(product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)
```

```python
# products/services.py
from django.db import transaction

from products.models import Product
from products.schemas import ProductCreateIn, ProductUpdateIn


@transaction.atomic
def product_create(payload: ProductCreateIn) -> Product:
    return Product.objects.create(**payload.model_dump())


@transaction.atomic
def product_update(product: Product, payload: ProductUpdateIn) -> Product:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    product.save(update_fields=[*payload.model_dump(exclude_unset=True), "updated_at"])
    return product


@transaction.atomic
def product_delete(product: Product) -> None:
    product.delete()
```

```python
# products/api.py
from django.http import HttpRequest
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate
from ninja.security import SessionAuth

from products.schemas import ProductCreateIn, ProductOut, ProductUpdateIn
from products.selectors import product_get, product_list
from products.services import product_create, product_delete, product_update

router = Router(auth=SessionAuth(), tags=["products"])


@router.get("/", response=list[ProductOut])
@paginate(LimitOffsetPagination)
def list_products(request: HttpRequest) -> list[ProductOut]:
    return product_list()


@router.get("/{product_id}", response=ProductOut)
def get_product(request: HttpRequest, product_id: int) -> ProductOut:
    return product_get(product_id)


@router.post("/", response={201: ProductOut})
def create_product(request: HttpRequest, payload: ProductCreateIn) -> tuple[int, ProductOut]:
    return 201, product_create(payload)


@router.patch("/{product_id}", response=ProductOut)
def update_product(
    request: HttpRequest,
    product_id: int,
    payload: ProductUpdateIn,
) -> ProductOut:
    product = product_get(product_id)
    return product_update(product, payload)


@router.delete("/{product_id}", response={204: None})
def delete_product(request: HttpRequest, product_id: int) -> tuple[int, None]:
    product_delete(product_get(product_id))
    return 204, None
```

```python
# config/api.py
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI()
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

**회귀 테스트 전략**

- 기존 목록/상세/생성/수정/삭제 endpoint별 status code와 JSON 필드를 비교한다.
- 목록 API는 페이지네이션 파라미터 `limit`, `offset` 동작을 검증한다.
- 인증 필요 API는 익명 요청 `401`, 인증 요청 `200/201/204`를 분리해 검증한다.
- 상세/수정/삭제의 없는 상품 ID는 `404`를 검증한다.
- 목록 조회는 `assertNumQueries`로 N+1 회귀를 막는다.
- 실행 명령: `python manage.py check`, `pytest` 또는 `python manage.py test`.

---
> **관련 스킬 참조:**
> - API endpoint 설계와 오류 형식 → **architecture-api** 스킬
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬