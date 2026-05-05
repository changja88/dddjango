**Django Ninja Pagination/Error Response 팀 표준**

아래 코드는 팀 컨벤션 문서에 그대로 넣는 기준 예시다. 이 프로젝트에서는 DRF를 사용하지 않고, Django Ninja `Schema`/`Router` 기준으로 작성한다.

## 1. 목록 응답 표준

목록 API는 항상 envelope를 사용한다.

```json
{
  "items": [],
  "meta": {
    "limit": 20,
    "offset": 0,
    "total": 125,
    "has_more": true
  }
}
```

규칙:

- 목록 응답은 `items`와 `meta`를 가진다.
- `items`는 현재 페이지 데이터만 담는다.
- `meta.total`은 필터 적용 후 전체 개수다.
- `meta.has_more`는 다음 페이지 존재 여부다.
- 기본 `limit`은 `20`, 최대 `limit`은 `100`으로 제한한다.
- `offset`은 `0` 이상이어야 한다.
- 커스텀 envelope를 쓰는 API에서는 Django Ninja `@paginate`와 섞지 않는다.
- `response=list[Schema]`는 envelope 없는 plain list 응답에만 사용한다.

```python
# schemas.py
from ninja import Schema


class PageMeta(Schema):
    limit: int
    offset: int
    total: int
    has_more: bool


class ProductOut(Schema):
    id: int
    name: str
    price: int


class ProductListOut(Schema):
    items: list[ProductOut]
    meta: PageMeta
```

```python
# api.py
from django.http import HttpRequest
from ninja import Query, Router

from .models import Product
from .schemas import PageMeta, ProductListOut, ProductOut

router = Router()

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


@router.get(
    "/products",
    response={200: ProductListOut},
)
def list_products(
    request: HttpRequest,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
) -> ProductListOut:
    queryset = Product.objects.order_by("id")

    total = queryset.count()
    rows = list(queryset[offset : offset + limit])

    return ProductListOut(
        items=[ProductOut(id=row.id, name=row.name, price=row.price) for row in rows],
        meta=PageMeta(
            limit=limit,
            offset=offset,
            total=total,
            has_more=offset + limit < total,
        ),
    )
```

plain list가 정말 필요한 내부성 API만 아래처럼 쓴다.

```python
from django.http import HttpRequest
from ninja import Router

from .models import Product
from .schemas import ProductOut

router = Router()


@router.get(
    "/products/all",
    response={200: list[ProductOut]},
)
def list_all_products(request: HttpRequest) -> list[ProductOut]:
    rows = Product.objects.order_by("id")
    return [ProductOut(id=row.id, name=row.name, price=row.price) for row in rows]
```

## 2. 오류 응답 표준

모든 API 오류는 RFC 9457 Problem Details 형식을 사용한다.

```json
{
  "type": "https://api.example.com/problems/not-found",
  "title": "Resource not found",
  "status": 404,
  "detail": "Product 123 does not exist.",
  "instance": "/api/products/123",
  "code": "product_not_found"
}
```

규칙:

- 모든 오류 응답은 `type`, `title`, `status`, `detail`, `instance`를 가진다.
- 팀 내부 식별자는 확장 필드 `code`에 둔다.
- 필드 검증 오류는 확장 필드 `invalid_params`에 담는다.
- 오류 응답의 `Content-Type`은 `application/problem+json`이다.
- 400, 401, 403, 404, 409, 422, 429, 500을 표준 상태 코드로 우선 사용한다.
- 인증 실패는 401, 권한 없음은 403으로 구분한다.
- 비즈니스 충돌은 409, 요청 값 검증 실패는 422를 사용한다.

```python
# schemas.py
from ninja import Schema


class InvalidParam(Schema):
    name: str
    reason: str


class ProblemDetails(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str | None = None
    invalid_params: list[InvalidParam] | None = None
```

```python
# errors.py
from dataclasses import dataclass


@dataclass(frozen=True)
class ApiProblem(Exception):
    status: int
    title: str
    detail: str
    code: str
    type: str = "about:blank"
```

```python
# config/api.py
from django.http import HttpRequest, JsonResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError

from common.api.errors import ApiProblem

api = NinjaAPI()


@api.exception_handler(ApiProblem)
def api_problem_handler(request: HttpRequest, exc: ApiProblem) -> JsonResponse:
    return JsonResponse(
        {
            "type": exc.type,
            "title": exc.title,
            "status": exc.status,
            "detail": exc.detail,
            "instance": request.path,
            "code": exc.code,
        },
        status=exc.status,
        content_type="application/problem+json",
    )


@api.exception_handler(ValidationError)
def validation_error_handler(request: HttpRequest, exc: ValidationError) -> JsonResponse:
    return JsonResponse(
        {
            "type": "https://api.example.com/problems/validation-error",
            "title": "Validation error",
            "status": 422,
            "detail": "Request validation failed.",
            "instance": request.path,
            "code": "validation_error",
            "invalid_params": [
                {
                    "name": ".".join(str(part) for part in error.get("loc", [])),
                    "reason": error.get("msg", "Invalid value."),
                }
                for error in exc.errors
            ],
        },
        status=422,
        content_type="application/problem+json",
    )
```

## 3. Endpoint response 예시

성공과 오류 응답을 데코레이터에 명시한다.

```python
from django.http import HttpRequest
from ninja import Router

from common.api.errors import ApiProblem
from common.api.schemas import ProblemDetails
from .models import Product
from .schemas import ProductOut

router = Router()


@router.get(
    "/products/{product_id}",
    response={
        200: ProductOut,
        404: ProblemDetails,
    },
)
def get_product(request: HttpRequest, product_id: int) -> ProductOut:
    product = Product.objects.filter(id=product_id).first()

    if product is None:
        raise ApiProblem(
            status=404,
            title="Resource not found",
            detail=f"Product {product_id} does not exist.",
            code="product_not_found",
            type="https://api.example.com/problems/not-found",
        )

    return ProductOut(
        id=product.id,
        name=product.name,
        price=product.price,
    )
```

생성 API는 `201`을 명시한다.

```python
from django.http import HttpRequest
from ninja import Router

from common.api.schemas import ProblemDetails
from .models import Product
from .schemas import ProductCreateIn, ProductOut

router = Router()


@router.post(
    "/products",
    response={
        201: ProductOut,
        409: ProblemDetails,
        422: ProblemDetails,
    },
)
def create_product(request: HttpRequest, payload: ProductCreateIn) -> tuple[int, ProductOut]:
    product = Product.objects.create(
        name=payload.name,
        price=payload.price,
    )

    return 201, ProductOut(
        id=product.id,
        name=product.name,
        price=product.price,
    )
```

## 4. 팀 규칙 요약

- 모든 sync endpoint 첫 인자는 `request: HttpRequest`로 작성한다.
- 모든 endpoint는 명시적 반환 타입을 가진다.
- 요청/응답은 Django Ninja `Schema`를 사용한다.
- 목록 API는 기본적으로 `items/meta` envelope를 사용한다.
- plain list 응답일 때만 `response={200: list[Schema]}`를 사용한다.
- `from typing import list`는 사용하지 않는다.
- 오류는 `ProblemDetails` 하나로 통일한다.
- `exception_handler`에서 `application/problem+json`을 명시한다.
- `response={...}`에 성공/오류 상태 코드를 함께 문서화한다.
- 사용자 입력 정렬값은 allow-list나 Enum으로 제한하고 `order_by()`에 직접 넣지 않는다.

## 5. Edge-case 체크리스트

- `limit`이 1 미만이면 422가 나는가?
- `limit`이 최대값을 넘으면 422가 나는가?
- `offset`이 음수이면 422가 나는가?
- 빈 목록이 `items: []`와 올바른 `meta.total: 0`을 반환하는가?
- 마지막 페이지에서 `has_more: false`인가?
- 필터 적용 후 `total`이 필터링된 전체 개수인가?
- 삭제되었거나 없는 리소스가 404 Problem Details를 반환하는가?
- 중복 생성, 상태 충돌, 재고 부족 같은 비즈니스 충돌이 409를 반환하는가?
- 인증 누락은 401, 권한 부족은 403으로 구분되는가?
- 모든 오류 응답의 `Content-Type`이 `application/problem+json`인가?
- validation error가 `invalid_params`를 포함하는가?
- endpoint 데코레이터의 `response={...}`에 실제 가능한 오류 코드가 빠지지 않았는가?
- 목록 API가 envelope를 반환하면서 `response=list[...]`로 잘못 선언되어 있지 않은가?

---
> **관련 스킬 참조:**
> - API 설계 원칙과 오류/페이지네이션 정책 → **architecture-api** 스킬
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬