**Django Ninja API 응답 표준**

아래 표준은 팀 컨벤션 문서에 그대로 넣는 것을 기준으로 한다. DRF는 사용하지 않고, 모든 요청/응답은 Django Ninja `Schema`, 앱별 `Router`, 상태 코드별 `response={...}` 계약으로 명시한다.

## 1. 목록 API 페이지네이션 표준

기본 목록 API는 `items/meta` envelope를 사용한다.

```json
{
  "items": [
    { "id": 1, "name": "A" }
  ],
  "meta": {
    "limit": 20,
    "has_more": true,
    "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wNS0wNVQxMDozMDowMFoiLCJpZCI6MX0="
  }
}
```

규칙:

- 공개/대용량 목록 API 기본값은 cursor pagination이다.
- cursor는 base64 등으로 인코딩한 opaque token으로 취급한다. 클라이언트가 내부 구조를 해석하면 안 된다.
- 기본 query parameter는 `limit`, `cursor`, `sort`, filter fields를 사용한다.
- `limit` 기본값은 `20`, 최대값은 `100`으로 둔다.
- cursor pagination 응답에는 기본적으로 `total`을 넣지 않는다. 비싸고 일관성이 흔들릴 수 있다.
- 관리자/소규모 목록처럼 랜덤 접근과 총 개수가 중요한 경우에만 offset 또는 page number pagination을 허용한다.
- 정렬 필드는 Enum allow-list로 제한한다. 사용자 입력을 `order_by()`에 직접 넣지 않는다.
- `@paginate`를 쓰면 Django Ninja paginator의 응답 형식을 따른다. 팀 표준 envelope를 반환할 때는 `@paginate`와 섞지 말고 직접 `items/meta`를 만든다.
- envelope 응답인데 `response=list[Schema]`로 선언하지 않는다. 반드시 `response=ListResponseSchema`를 선언한다.

## 2. 페이지네이션 Schema

```python
# common/api/schemas.py
from ninja import Schema


class CursorPageMeta(Schema):
    limit: int
    has_more: bool
    next_cursor: str | None = None


class OffsetPageMeta(Schema):
    limit: int
    offset: int
    total: int
    has_more: bool


class ErrorParam(Schema):
    name: str
    reason: str


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    code: str | None = None
    invalid_params: list[ErrorParam] | None = None
```

리소스별 목록 응답은 명시적으로 만든다.

```python
# products/schemas.py
from datetime import datetime
from ninja import Schema
from common.api.schemas import CursorPageMeta


class ProductOut(Schema):
    id: int
    name: str
    price: int
    created_at: datetime


class ProductListOut(Schema):
    items: list[ProductOut]
    meta: CursorPageMeta
```

## 3. 필터/정렬 Query Schema

```python
# products/schemas.py
from enum import StrEnum
from ninja import FilterSchema, Field, Schema


class ProductSort(StrEnum):
    CREATED_AT_DESC = "-created_at"
    CREATED_AT_ASC = "created_at"
    PRICE_DESC = "-price"
    PRICE_ASC = "price"


class ProductListQuery(FilterSchema):
    limit: int = Field(default=20, ge=1, le=100)
    cursor: str | None = None
    sort: ProductSort = ProductSort.CREATED_AT_DESC
    category_id: int | None = None
    q: str | None = Field(default=None, max_length=100)
```

## 4. Cursor 목록 Endpoint 예시

```python
# products/api.py
import base64
import json
from django.http import HttpRequest
from ninja import Query, Router

from common.api.schemas import ProblemDetail
from .models import Product
from .schemas import ProductListOut, ProductListQuery, ProductOut

router = Router(tags=["products"])


def encode_cursor(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
    return base64.urlsafe_b64encode(raw).decode()


def decode_cursor(cursor: str) -> dict:
    raw = base64.urlsafe_b64decode(cursor.encode())
    return json.loads(raw)


@router.get(
    "",
    response={
        200: ProductListOut,
        400: ProblemDetail,
        422: ProblemDetail,
    },
)
def list_products(request: HttpRequest, query: Query[ProductListQuery]) -> tuple[int, dict]:
    queryset = Product.objects.all()

    if query.category_id is not None:
        queryset = queryset.filter(category_id=query.category_id)

    if query.q:
        queryset = queryset.filter(name__icontains=query.q)

    ordering = query.sort.value
    queryset = queryset.order_by(ordering, "id")

    if query.cursor:
        cursor = decode_cursor(query.cursor)
        if ordering == "-created_at":
            queryset = queryset.filter(created_at__lt=cursor["created_at"])
        elif ordering == "created_at":
            queryset = queryset.filter(created_at__gt=cursor["created_at"])
        elif ordering == "-price":
            queryset = queryset.filter(price__lt=cursor["price"])
        elif ordering == "price":
            queryset = queryset.filter(price__gt=cursor["price"])

    rows = list(queryset[: query.limit + 1])
    page_items = rows[: query.limit]
    has_more = len(rows) > query.limit

    next_cursor = None
    if has_more and page_items:
        last = page_items[-1]
        next_cursor = encode_cursor(
            {
                "id": last.id,
                "created_at": last.created_at.isoformat(),
                "price": last.price,
            }
        )

    return 200, {
        "items": page_items,
        "meta": {
            "limit": query.limit,
            "has_more": has_more,
            "next_cursor": next_cursor,
        },
    }
```

실무에서는 cursor 조건을 정렬 필드와 `id` 조합으로 더 엄밀하게 맞춘다. 예를 들어 `created_at`이 같은 행이 많으면 `(created_at, id)` 기준으로 다음 페이지를 계산해야 누락/중복이 줄어든다.

## 5. Error Response 표준

모든 API 에러는 RFC 9457 Problem Details 형식을 사용한다.

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed.",
  "instance": "/api/v1/products",
  "code": "VALIDATION_ERROR",
  "invalid_params": [
    {
      "name": "limit",
      "reason": "Input should be less than or equal to 100"
    }
  ]
}
```

규칙:

- `Content-Type`은 `application/problem+json`으로 내려간다.
- `status`는 실제 HTTP status code와 반드시 일치한다.
- `type`은 문제 유형별 안정적인 URI다.
- `title`은 문제 유형의 짧은 이름이다. 발생마다 바꾸지 않는다.
- `detail`은 이번 발생에 대한 설명이다.
- `code`는 프론트엔드/클라이언트 분기용 안정 코드다.
- 필드 검증 오류는 `invalid_params` 확장 필드에 넣는다.
- 인증 실패는 `401`, 권한 부족은 `403`, 리소스 없음은 `404`, 중복/상태 충돌은 `409`, 의미 검증 실패는 `422`, rate limit은 `429`를 사용한다.

## 6. Exception Handler 표준

```python
# config/api.py
from dataclasses import dataclass, field
from typing import Any

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest
from ninja import NinjaAPI
from ninja.errors import ValidationError

from common.api.schemas import ProblemDetail
from products.api import router as products_router


@dataclass
class APIException(Exception):
    status: int
    type: str
    title: str
    detail: str
    code: str
    extra: dict[str, Any] = field(default_factory=dict)


api = NinjaAPI(
    title="Example API",
    version="1.0.0",
)


def problem_response(
    request: HttpRequest,
    status: int,
    type: str,
    title: str,
    detail: str,
    code: str,
    **extra: Any,
):
    payload = {
        "type": type,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
        "code": code,
        **extra,
    }
    response = api.create_response(request, payload, status=status)
    response["Content-Type"] = "application/problem+json"
    return response


@api.exception_handler(APIException)
def handle_api_exception(request: HttpRequest, exc: APIException):
    return problem_response(
        request,
        status=exc.status,
        type=exc.type,
        title=exc.title,
        detail=exc.detail,
        code=exc.code,
        **exc.extra,
    )


@api.exception_handler(ValidationError)
def handle_validation_error(request: HttpRequest, exc: ValidationError):
    invalid_params = [
        {
            "name": ".".join(str(part) for part in error.get("loc", [])),
            "reason": error.get("msg", "Invalid value."),
        }
        for error in exc.errors
    ]

    return problem_response(
        request,
        status=422,
        type="https://api.example.com/problems/validation-error",
        title="Validation Error",
        detail="Request validation failed.",
        code="VALIDATION_ERROR",
        invalid_params=invalid_params,
    )


@api.exception_handler(Http404)
def handle_not_found(request: HttpRequest, exc: Http404):
    return problem_response(
        request,
        status=404,
        type="https://api.example.com/problems/not-found",
        title="Not Found",
        detail="The requested resource was not found.",
        code="NOT_FOUND",
    )


@api.exception_handler(PermissionDenied)
def handle_permission_denied(request: HttpRequest, exc: PermissionDenied):
    return problem_response(
        request,
        status=403,
        type="https://api.example.com/problems/forbidden",
        title="Forbidden",
        detail="You do not have permission to access this resource.",
        code="FORBIDDEN",
    )


api.add_router("/products/", products_router)
```

```python
# config/urls.py
from django.urls import path
from .api import api

urlpatterns = [
    path("api/v1/", api.urls),
]
```

## 7. Endpoint `response={...}` 예시

생성 API:

```python
# products/api.py
from django.db import IntegrityError
from django.http import HttpRequest
from ninja import Router

from common.api.schemas import ProblemDetail
from config.api import APIException
from .models import Product
from .schemas import ProductCreateIn, ProductOut

router = Router(tags=["products"])


@router.post(
    "",
    response={
        201: ProductOut,
        409: ProblemDetail,
        422: ProblemDetail,
    },
)
def create_product(request: HttpRequest, payload: ProductCreateIn) -> tuple[int, Product]:
    try:
        product = Product.objects.create(
            name=payload.name,
            price=payload.price,
            category_id=payload.category_id,
        )
    except IntegrityError as exc:
        raise APIException(
            status=409,
            type="https://api.example.com/problems/product-conflict",
            title="Product Conflict",
            detail="A product with the same unique key already exists.",
            code="PRODUCT_CONFLICT",
        ) from exc

    return 201, product
```

상세 조회 API:

```python
@router.get(
    "/{product_id}",
    response={
        200: ProductOut,
        404: ProblemDetail,
    },
)
def get_product(request: HttpRequest, product_id: int) -> Product:
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist as exc:
        raise APIException(
            status=404,
            type="https://api.example.com/problems/product-not-found",
            title="Product Not Found",
            detail="The requested product does not exist.",
            code="PRODUCT_NOT_FOUND",
        ) from exc
```

삭제 API:

```python
@router.delete(
    "/{product_id}",
    response={
        204: None,
        404: ProblemDetail,
    },
)
def delete_product(request: HttpRequest, product_id: int) -> tuple[int, None]:
    deleted_count, _ = Product.objects.filter(id=product_id).delete()

    if deleted_count == 0:
        raise APIException(
            status=404,
            type="https://api.example.com/problems/product-not-found",
            title="Product Not Found",
            detail="The requested product does not exist.",
            code="PRODUCT_NOT_FOUND",
        )

    return 204, None
```

PATCH API:

```python
from ninja import PatchDict

from .schemas import ProductPatchIn


@router.patch(
    "/{product_id}",
    response={
        200: ProductOut,
        404: ProblemDetail,
        409: ProblemDetail,
        422: ProblemDetail,
    },
)
def update_product(
    request: HttpRequest,
    product_id: int,
    payload: PatchDict[ProductPatchIn],
) -> Product:
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist as exc:
        raise APIException(
            status=404,
            type="https://api.example.com/problems/product-not-found",
            title="Product Not Found",
            detail="The requested product does not exist.",
            code="PRODUCT_NOT_FOUND",
        ) from exc

    for field, value in payload.items():
        setattr(product, field, value)

    try:
        product.save(update_fields=list(payload.keys()))
    except IntegrityError as exc:
        raise APIException(
            status=409,
            type="https://api.example.com/problems/product-conflict",
            title="Product Conflict",
            detail="The update conflicts with an existing product.",
            code="PRODUCT_CONFLICT",
        ) from exc

    return product
```

## 8. 상태 코드 규칙

- `200 OK`: 조회, 전체 수정, 부분 수정 성공
- `201 Created`: 생성 성공. 가능하면 `Location` 헤더 포함
- `202 Accepted`: 비동기 작업 접수
- `204 No Content`: 삭제 성공, 본문 없음
- `400 Bad Request`: JSON 형식 오류, 잘못된 cursor 등 요청 형식 문제
- `401 Unauthorized`: 인증 필요
- `403 Forbidden`: 인증은 되었지만 권한 부족
- `404 Not Found`: 리소스 없음 또는 존재 숨김
- `409 Conflict`: 중복 생성, 낙관적 잠금 실패, 상태 충돌
- `422 Unprocessable Entity`: 형식은 맞지만 도메인 규칙상 처리 불가
- `429 Too Many Requests`: rate limit 초과
- `500 Internal Server Error`: 예상하지 못한 서버 오류
- `503 Service Unavailable`: 일시 장애 또는 점검, 가능하면 `Retry-After` 포함

## 9. Edge-case Checklist

- 목록 API에 pagination이 없는가?
- envelope 응답인데 `response=list[...]`로 선언했는가?
- `@paginate`와 커스텀 `items/meta` envelope를 섞었는가?
- `limit` 최대값이 없는가?
- cursor가 내부 DB 필드 그대로 노출되는가?
- cursor decode 실패가 `400 ProblemDetail`로 변환되는가?
- 정렬 필드가 allow-list 없이 `order_by()`에 직접 들어가는가?
- 정렬 기준이 non-unique인데 tie-breaker `id`가 없는가?
- cursor pagination에서 삽입/삭제 시 누락 또는 중복 가능성을 테스트했는가?
- 대용량 cursor 목록에 `total`을 매번 계산하는가?
- 요청 Schema와 응답 Schema가 분리되어 있는가?
- 입력 Schema에 서버 생성 필드가 포함되어 있는가?
- 응답 Schema가 민감 필드를 노출하는가?
- `ModelSchema`에서 `fields = "__all__"`을 사용했는가?
- 모든 에러가 `ProblemDetail` 형식인가?
- 에러 응답의 `status` 값과 실제 HTTP status가 일치하는가?
- 에러 `Content-Type`이 `application/problem+json`인가?
- 401과 403을 구분했는가?
- 중복/동시성 충돌을 400이 아니라 409로 처리했는가?
- 도메인 의미 검증 실패를 422로 처리했는가?
- 삭제 성공 응답이 `204`이면서 본문을 반환하지 않는가?
- `response={...}`에 성공/실패 status별 Schema가 모두 선언되어 있는가?
- 테스트에서 status code, response schema, problem content type을 함께 검증하는가?

---
> **관련 스킬 참조:**
> - API 설계/상태 코드/페이지네이션 → **architecture-api** 스킬
> - Django Ninja Router/Schema/exception handler 구현 → **implementation-django-ninja** 스킬