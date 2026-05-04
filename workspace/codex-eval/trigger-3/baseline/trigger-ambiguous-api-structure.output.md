**주요 내용**

현재 `/private/tmp/dddjango-codex-eval` 작업 디렉터리가 비어 있고 세션이 읽기 전용이라 파일을 만들거나 수정할 수는 없었습니다. 대신 이 프로젝트 설정에 맞춰 Django Ninja 기준의 깔끔한 API 구조를 잡으면 아래처럼 가는 게 좋습니다. DRF는 이 프로젝트 정책상 사용하지 않습니다.

```text
config/
  api.py          # NinjaAPI 생성, 공통 예외 핸들러, 라우터 합성
  urls.py         # path("api/", api.urls)

products/
  models.py
  schemas.py      # 요청/응답 Schema
  api.py          # Router + endpoint
  services.py     # use case 조율
```

핵심 규칙은 이렇게 잡습니다.

```python
# config/api.py
from django.http import JsonResponse
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError, ValidationError

from products.api import router as products_router


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""


api = NinjaAPI(version="1.0.0")

api.add_router("/products", products_router, tags=["products"])


@api.exception_handler(HttpError)
def handle_http_error(request, exc):
    return JsonResponse(
        ProblemDetail(
            title=str(exc),
            status=exc.status_code,
            detail=str(exc),
            instance=request.path,
        ).model_dump(),
        status=exc.status_code,
        content_type="application/problem+json",
    )


@api.exception_handler(ValidationError)
def handle_validation_error(request, exc):
    return JsonResponse(
        ProblemDetail(
            type="https://api.example.com/problems/validation-error",
            title="Validation Error",
            status=422,
            detail="Request validation failed.",
            instance=request.path,
        ).model_dump(),
        status=422,
        content_type="application/problem+json",
    )
```

```python
# products/schemas.py
from datetime import datetime
from ninja import ModelSchema, Schema

from .models import Product


class ProductCreateIn(Schema):
    name: str
    price: int


class ProductUpdateIn(Schema):
    name: str | None = None
    price: int | None = None


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "created_at", "updated_at"]
```

```python
# products/api.py
from ninja import Router
from ninja.pagination import CursorPagination, paginate

from .schemas import ProductCreateIn, ProductOut, ProductUpdateIn
from .services import ProductService

router = Router()


@router.get("", response=list[ProductOut])
@paginate(CursorPagination, page_size=50, max_page_size=100)
def list_products(request):
    return ProductService.list_products()


@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int) -> ProductOut:
    return ProductService.get_product(product_id)


@router.post("", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn) -> tuple[int, ProductOut]:
    return 201, ProductService.create_product(payload)


@router.patch("/{product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: ProductUpdateIn) -> ProductOut:
    return ProductService.update_product(product_id, payload)


@router.delete("/{product_id}", response={204: None})
def delete_product(request, product_id: int) -> tuple[int, None]:
    ProductService.delete_product(product_id)
    return 204, None
```

```python
# config/urls.py
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

API 설계 기준은 `/api/products`, `/api/products/{product_id}`처럼 명사 기반 복수 리소스로 두고, 목록은 항상 페이지네이션을 붙이는 방향이 좋습니다. 에러는 전부 RFC 9457 Problem Details 형식으로 통일하면 클라이언트 쪽 처리도 깔끔해집니다.

---
> **관련 스킬 참조:**
> - API 엔드포인트/상태 코드/에러 형식 → **architecture-api** 스킬
> - Django Ninja Router/Schema/페이지네이션 구현 → **implementation-django-ninja** 스킬