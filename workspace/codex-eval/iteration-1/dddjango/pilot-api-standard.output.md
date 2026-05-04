**Django Ninja API Standard: Pagination & Errors**

아래 표준을 팀 컨벤션 문서에 그대로 넣어도 됩니다. 이 프로젝트 정책은 DRF가 아니라 Django Ninja `Schema`, `Router`, `NinjaAPI.exception_handler()`를 기준으로 합니다.

## 1. Pagination 표준

목록 API는 반드시 페이지네이션을 적용한다. 기본은 cursor pagination이며, 작은 관리자성 목록만 예외적으로 limit/offset을 허용한다.

**응답 shape**

```json
{
  "items": [],
  "page": {
    "next_cursor": "opaque-base64-cursor-or-null",
    "has_more": true,
    "limit": 50
  }
}
```

**규칙**

- `items`: 현재 페이지 데이터 배열.
- `page.next_cursor`: 다음 페이지가 없으면 `null`.
- `page.has_more`: 다음 페이지 존재 여부.
- `page.limit`: 실제 적용된 limit.
- 기본 `limit=50`, 최대 `limit=100`.
- cursor는 클라이언트가 해석하지 않는 opaque string으로 둔다.
- 정렬 기준은 안정적이어야 한다. 예: `created_at DESC, id DESC`.
- `total_count`는 기본 응답에 넣지 않는다. 비용이 싼 화면에서만 별도 필드로 허용한다.

```python
# schemas.py
from typing import Generic, TypeVar

from ninja import Schema
from pydantic import Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class CursorPageSchema(Schema):
    next_cursor: str | None = None
    has_more: bool
    limit: int


class CursorListResponse(GenericModel, Generic[T]):
    items: list[T]
    page: CursorPageSchema


class CursorPaginationInput(Schema):
    cursor: str | None = None
    limit: int = Field(default=50, ge=1, le=100)
```

```python
# products/schemas.py
from datetime import datetime

from ninja import ModelSchema

from .models import Product


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "created_at"]
```

```python
# products/api.py
from ninja import Router, Query

from common.schemas import CursorListResponse, CursorPaginationInput
from .models import Product
from .schemas import ProductOut
from .pagination import decode_cursor, encode_cursor

router = Router(tags=["products"])


@router.get("", response={200: CursorListResponse[ProductOut]})
def list_products(
    request,
    pagination: Query[CursorPaginationInput],
) -> CursorListResponse[ProductOut]:
    limit = pagination.limit
    queryset = Product.objects.order_by("-created_at", "-id")

    if pagination.cursor:
        created_at, product_id = decode_cursor(pagination.cursor)
        queryset = queryset.filter(
            created_at__lt=created_at,
        ) | queryset.filter(
            created_at=created_at,
            id__lt=product_id,
        )

    rows = list(queryset[: limit + 1])
    items = rows[:limit]
    has_more = len(rows) > limit

    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor(created_at=last.created_at, object_id=last.id)

    return CursorListResponse[ProductOut](
        items=items,
        page={
            "next_cursor": next_cursor,
            "has_more": has_more,
            "limit": limit,
        },
    )
```

## 2. Error Response 표준

모든 API 오류는 RFC 9457 Problem Details 형식을 따른다. 커스텀 `{error: ...}` 또는 `{message: ...}` 단독 응답은 사용하지 않는다.

**응답 shape**

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed.",
  "instance": "/api/products",
  "errors": [
    {
      "code": "invalid",
      "field": "price",
      "message": "Input should be greater than 0"
    }
  ]
}
```

```python
# common/errors.py
from typing import Any

from ninja import Schema


class FieldErrorSchema(Schema):
    code: str
    message: str
    field: str | None = None


class ProblemDetailSchema(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    errors: list[FieldErrorSchema] | None = None


class ProblemError(Exception):
    def __init__(
        self,
        *,
        status: int,
        title: str,
        detail: str,
        type: str,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type
        self.errors = errors
```

```python
# config/api.py
from django.core.exceptions import PermissionDenied
from django.http import Http404
from ninja import NinjaAPI
from ninja.errors import ValidationError

from common.errors import ProblemDetailSchema, ProblemError
from products.api import router as products_router

api = NinjaAPI(title="Service API", version="1.0.0")


def problem_response(request, *, status: int, title: str, detail: str, type: str, errors=None):
    return api.create_response(
        request,
        {
            "type": type,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": request.path,
            "errors": errors,
        },
        status=status,
    )


@api.exception_handler(ValidationError)
def validation_error_handler(request, exc: ValidationError):
    errors = [
        {
            "code": "invalid",
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
        }
        for error in exc.errors
    ]
    return problem_response(
        request,
        status=422,
        title="Validation Error",
        detail="Request validation failed.",
        type="https://api.example.com/problems/validation-error",
        errors=errors,
    )


@api.exception_handler(ProblemError)
def problem_error_handler(request, exc: ProblemError):
    return problem_response(
        request,
        status=exc.status,
        title=exc.title,
        detail=exc.detail,
        type=exc.type,
        errors=exc.errors,
    )


@api.exception_handler(Http404)
def not_found_handler(request, exc: Http404):
    return problem_response(
        request,
        status=404,
        title="Not Found",
        detail="The requested resource was not found.",
        type="https://api.example.com/problems/not-found",
    )


@api.exception_handler(PermissionDenied)
def permission_denied_handler(request, exc: PermissionDenied):
    return problem_response(
        request,
        status=403,
        title="Forbidden",
        detail="You do not have permission to access this resource.",
        type="https://api.example.com/problems/forbidden",
    )


api.add_router("/products", products_router)
```

## 3. `response={...}` 예시

상태 코드별 응답 스키마를 명시한다. 성공과 실패 스키마를 함께 선언한다.

```python
from ninja import Router

from common.errors import ProblemDetailSchema, ProblemError
from common.schemas import CursorListResponse
from .schemas import ProductCreateIn, ProductOut

router = Router(tags=["products"])


@router.get(
    "",
    response={
        200: CursorListResponse[ProductOut],
        422: ProblemDetailSchema,
    },
)
def list_products(request) -> CursorListResponse[ProductOut]:
    ...


@router.get(
    "/{product_id}",
    response={
        200: ProductOut,
        404: ProblemDetailSchema,
    },
)
def get_product(request, product_id: int) -> ProductOut:
    ...


@router.post(
    "",
    response={
        201: ProductOut,
        409: ProblemDetailSchema,
        422: ProblemDetailSchema,
    },
)
def create_product(request, payload: ProductCreateIn) -> tuple[int, ProductOut]:
    ...


@router.delete(
    "/{product_id}",
    response={
        204: None,
        404: ProblemDetailSchema,
        409: ProblemDetailSchema,
    },
)
def delete_product(request, product_id: int) -> tuple[int, None]:
    return 204, None
```

비즈니스 오류는 `ProblemError`로 올린다.

```python
raise ProblemError(
    status=409,
    title="Conflict",
    detail="A product with this SKU already exists.",
    type="https://api.example.com/problems/duplicate-sku",
    errors=[
        {
            "code": "duplicate",
            "field": "sku",
            "message": "SKU must be unique.",
        }
    ],
)
```

## 4. 상태 코드 규칙

- `200`: 조회, 수정 성공.
- `201`: 생성 성공.
- `204`: 삭제 성공 또는 응답 본문 없는 성공.
- `400`: 요청 형식은 맞지만 의미가 잘못된 일반 클라이언트 오류.
- `401`: 인증 필요.
- `403`: 인증은 됐지만 권한 없음.
- `404`: 리소스 없음.
- `409`: 중복, 상태 충돌, 삭제 불가 같은 비즈니스 충돌.
- `422`: Schema validation 실패.
- `429`: rate limit 초과.
- `500`: 예상하지 못한 서버 오류. 상세 내부 정보 노출 금지.

## 5. Edge-Case Checklist

- [ ] 모든 목록 API가 pagination shape `{items, page}`를 반환하는가?
- [ ] `limit` 기본값과 최대값이 Schema에서 강제되는가?
- [ ] cursor가 opaque string이며 클라이언트가 내부 값을 의존하지 않는가?
- [ ] cursor 정렬 기준이 unique tie-breaker를 포함하는가? 예: `created_at`, `id`.
- [ ] 페이지 조회 중 데이터가 추가/삭제되어도 중복/누락 위험이 낮은가?
- [ ] 빈 목록은 `items=[]`, `has_more=false`, `next_cursor=null`인가?
- [ ] 모든 오류가 `ProblemDetailSchema` shape를 따르는가?
- [ ] validation error는 `422`, auth failure는 `401`, forbidden은 `403`, conflict는 `409`인가?
- [ ] 예외 응답에 stack trace, SQL, 내부 모델명, secret 값이 노출되지 않는가?
- [ ] 각 라우터 데코레이터에 `response={...}`가 선언되어 OpenAPI가 정확한가?
- [ ] 삭제 성공은 본문 없이 `204: None`을 반환하는가?
- [ ] DRF `Serializer`, `ViewSet`, `APIView`, `permission_classes`를 사용하지 않는가?

---
> **관련 스킬 참조:**
> - API 설계 원칙과 상태 코드/페이지네이션 전략 → **architecture-api** 스킬
> - Django Ninja Schema/Router/exception_handler 구현 → **implementation-django-ninja** 스킬