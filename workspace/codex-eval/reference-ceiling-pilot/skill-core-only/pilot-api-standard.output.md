아래를 팀 컨벤션 문서에 그대로 넣을 수 있는 형태로 작성했습니다.

# Django Ninja API Pagination / Error Response Standard

## 1. 기본 원칙

- API 구현은 Django Ninja `Schema`, `Router`, `NinjaAPI`를 사용한다.
- DRF `Serializer`, `ViewSet`, `APIView`, `permission_classes`는 사용하지 않는다.
- 목록 응답은 항상 페이지네이션한다.
- 팀 표준 목록 응답은 `items/meta` envelope를 사용한다.
- 커스텀 envelope를 반환할 때는 `@paginate`와 섞지 않는다.
- 커스텀 envelope를 반환하면서 `response=list[Something]`로 선언하지 않는다.
- 모든 API 에러는 RFC 9457 Problem Details 형식으로 반환한다.
- Problem Details 응답의 `Content-Type`은 `application/problem+json`이다.
- 엔드포인트의 `response={...}`에는 성공과 실패 상태 코드를 모두 명시한다.

---

## 2. 페이지네이션 표준

### 2.1 목록 응답 Shape

```json
{
  "items": [
    {
      "id": 1,
      "name": "Keyboard"
    }
  ],
  "meta": {
    "limit": 20,
    "has_more": true,
    "next_cursor": "eyJpZCI6MTIzfQ"
  }
}
```

### 2.2 규칙

- 기본 페이지네이션은 cursor 기반으로 한다.
- cursor는 클라이언트가 해석하지 않는 opaque string으로 취급한다.
- cursor는 base64 URL-safe 인코딩 문자열을 사용한다.
- 응답에는 항상 `has_more`를 포함한다.
- 다음 페이지가 없으면 `next_cursor`는 `null`이다.
- `limit` 기본값은 `20`, 최댓값은 `100`이다.
- 정렬 기준은 안정적이어야 하며, 기본은 `id ASC` 또는 `created_at DESC, id DESC`처럼 tie-breaker를 포함한다.
- 사용자 입력을 `order_by()`에 직접 전달하지 않는다. 정렬 필드는 allow-list 또는 Enum으로 제한한다.
- offset pagination은 작은 관리 화면이나 내부 도구처럼 데이터 크기와 정렬 안정성이 통제되는 경우에만 사용한다.

---

## 3. 공통 Schema

```python
# common/api/schemas.py

from ninja import Schema


class ProblemInvalidParam(Schema):
    name: str
    reason: str


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str | None = None
    errors: list[ProblemInvalidParam] | None = None


class CursorPageMeta(Schema):
    limit: int
    has_more: bool
    next_cursor: str | None = None
```

목록 응답은 리소스별로 명시 Schema를 만든다. 제네릭처럼 숨기지 않고 OpenAPI에 드러나는 응답 이름을 유지한다.

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


class ProductCreateIn(Schema):
    name: str
    price: int


class ProductUpdateIn(Schema):
    name: str | None = None
    price: int | None = None


class ProductCreateOut(Schema):
    id: int
    name: str
    price: int
    created_at: datetime
```

---

## 4. Cursor Helper

```python
# common/api/pagination.py

import base64
import json
from dataclasses import dataclass


DEFAULT_LIMIT = 20
MAX_LIMIT = 100


@dataclass(frozen=True)
class CursorPage:
    limit: int
    cursor_id: int | None


def normalize_limit(limit: int | None) -> int:
    if limit is None:
        return DEFAULT_LIMIT
    return min(max(limit, 1), MAX_LIMIT)


def encode_cursor(payload: dict[str, int | str]) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(cursor: str | None) -> dict[str, int | str] | None:
    if not cursor:
        return None

    padding = "=" * (-len(cursor) % 4)
    raw = base64.urlsafe_b64decode(cursor + padding)

    data = json.loads(raw.decode())
    if not isinstance(data, dict):
        raise ValueError("Invalid cursor")

    return data


def parse_id_cursor(cursor: str | None, limit: int | None) -> CursorPage:
    data = decode_cursor(cursor)
    cursor_id = None

    if data is not None:
        value = data.get("id")
        if not isinstance(value, int):
            raise ValueError("Invalid cursor")
        cursor_id = value

    return CursorPage(
        limit=normalize_limit(limit),
        cursor_id=cursor_id,
    )
```

---

## 5. Error Helper와 Exception Handler

```python
# common/api/errors.py

from django.http import HttpRequest
from ninja import NinjaAPI
from ninja.errors import ValidationError

from common.api.schemas import ProblemDetail, ProblemInvalidParam


class ApiProblem(Exception):
    def __init__(
        self,
        *,
        status: int,
        title: str,
        detail: str,
        type: str = "about:blank",
        errors: list[ProblemInvalidParam] | None = None,
    ) -> None:
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type
        self.errors = errors


def problem_payload(
    *,
    request: HttpRequest,
    status: int,
    title: str,
    detail: str,
    type: str = "about:blank",
    errors: list[ProblemInvalidParam] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "type": type,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
    }

    if errors:
        payload["errors"] = [error.dict() for error in errors]

    return payload


def problem_response(
    api: NinjaAPI,
    request: HttpRequest,
    *,
    status: int,
    title: str,
    detail: str,
    type: str = "about:blank",
    errors: list[ProblemInvalidParam] | None = None,
):
    response = api.create_response(
        request,
        problem_payload(
            request=request,
            status=status,
            title=title,
            detail=detail,
            type=type,
            errors=errors,
        ),
        status=status,
    )
    response["Content-Type"] = "application/problem+json"
    return response


def register_exception_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(ApiProblem)
    def handle_api_problem(request: HttpRequest, exc: ApiProblem):
        return problem_response(
            api,
            request,
            status=exc.status,
            title=exc.title,
            detail=exc.detail,
            type=exc.type,
            errors=exc.errors,
        )

    @api.exception_handler(ValidationError)
    def handle_validation_error(request: HttpRequest, exc: ValidationError):
        return problem_response(
            api,
            request,
            status=422,
            title="Validation Failed",
            detail="Request validation failed.",
            type="https://api.example.com/problems/validation-error",
        )

    @api.exception_handler(ValueError)
    def handle_value_error(request: HttpRequest, exc: ValueError):
        return problem_response(
            api,
            request,
            status=400,
            title="Bad Request",
            detail=str(exc),
            type="https://api.example.com/problems/bad-request",
        )
```

API 합성 위치에서 exception handler를 등록한다.

```python
# config/api.py

from ninja import NinjaAPI

from common.api.errors import register_exception_handlers
from products.api import router as products_router

api = NinjaAPI(title="Service API", version="1.0.0")

register_exception_handlers(api)

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

---

## 6. `response={...}` 표준 예시

### 6.1 목록 API

```python
# products/api.py

from django.http import HttpRequest
from ninja import Query, Router

from common.api.errors import ApiProblem
from common.api.pagination import encode_cursor, parse_id_cursor
from common.api.schemas import ProblemDetail
from products.models import Product
from products.schemas import ProductListOut

router = Router(tags=["products"])


@router.get(
    "",
    response={
        200: ProductListOut,
        400: ProblemDetail,
        422: ProblemDetail,
    },
)
def list_products(
    request: HttpRequest,
    cursor: str | None = Query(None),
    limit: int | None = Query(None),
) -> ProductListOut:
    page = parse_id_cursor(cursor, limit)

    queryset = Product.objects.order_by("id")
    if page.cursor_id is not None:
        queryset = queryset.filter(id__gt=page.cursor_id)

    rows = list(queryset[: page.limit + 1])
    items = rows[: page.limit]
    has_more = len(rows) > page.limit

    next_cursor = None
    if has_more and items:
        next_cursor = encode_cursor({"id": items[-1].id})

    return ProductListOut(
        items=items,
        meta={
            "limit": page.limit,
            "has_more": has_more,
            "next_cursor": next_cursor,
        },
    )
```

### 6.2 생성 API

```python
from django.db import IntegrityError
from django.http import HttpRequest

from common.api.errors import ApiProblem
from common.api.schemas import ProblemDetail
from products.models import Product
from products.schemas import ProductCreateIn, ProductCreateOut


@router.post(
    "",
    response={
        201: ProductCreateOut,
        409: ProblemDetail,
        422: ProblemDetail,
    },
)
def create_product(request: HttpRequest, payload: ProductCreateIn) -> tuple[int, Product]:
    try:
        product = Product.objects.create(
            name=payload.name,
            price=payload.price,
        )
    except IntegrityError as exc:
        raise ApiProblem(
            status=409,
            title="Conflict",
            detail="Product already exists.",
            type="https://api.example.com/problems/product-conflict",
        ) from exc

    return 201, product
```

### 6.3 단건 조회 API

```python
@router.get(
    "/{product_id}",
    response={
        200: ProductCreateOut,
        404: ProblemDetail,
    },
)
def get_product(request: HttpRequest, product_id: int) -> Product:
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist as exc:
        raise ApiProblem(
            status=404,
            title="Not Found",
            detail="Product was not found.",
            type="https://api.example.com/problems/product-not-found",
        ) from exc
```

### 6.4 삭제 API

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
        raise ApiProblem(
            status=404,
            title="Not Found",
            detail="Product was not found.",
            type="https://api.example.com/problems/product-not-found",
        )

    return 204, None
```

---

## 7. 상태 코드 표준

- `200 OK`: 조회, 목록, 수정 성공
- `201 Created`: 생성 성공
- `204 No Content`: 삭제 성공 또는 응답 본문 없는 성공
- `400 Bad Request`: cursor 파싱 실패, 잘못된 쿼리 조합
- `401 Unauthorized`: 인증 필요
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스 없음
- `409 Conflict`: unique 충돌, 상태 충돌, 멱등성 충돌
- `422 Unprocessable Entity`: 요청 validation 실패
- `429 Too Many Requests`: rate limit 초과
- `500 Internal Server Error`: 예상하지 못한 서버 오류

---

## 8. Edge-case Checklist

### 페이지네이션

- [ ] 목록 API에 페이지네이션이 없는가?
- [ ] 커스텀 `items/meta` envelope와 `@paginate`를 섞었는가?
- [ ] 커스텀 envelope인데 `response=list[Schema]`로 선언했는가?
- [ ] `limit` 최댓값이 없는가?
- [ ] `limit=0`, 음수, 과도한 값이 들어왔을 때 동작이 정의되어 있는가?
- [ ] cursor가 깨졌거나 base64 decode에 실패할 때 `400 ProblemDetail`을 반환하는가?
- [ ] cursor가 클라이언트에 내부 DB 구조를 과하게 노출하지 않는가?
- [ ] 정렬 기준이 불안정해서 중복/누락이 발생할 수 있는가?
- [ ] `has_more` 계산을 위해 `limit + 1`개를 조회하는가?
- [ ] 마지막 페이지에서 `next_cursor`가 `null`인가?
- [ ] 사용자 입력 정렬값을 `order_by()`에 직접 전달하지 않는가?
- [ ] 대량 목록에서 N+1이 발생하지 않도록 `select_related`/`prefetch_related`를 검토했는가?

### 에러 응답

- [ ] 모든 에러가 RFC 9457 `type/title/status/detail/instance`를 포함하는가?
- [ ] `Content-Type`이 `application/problem+json`인가?
- [ ] `response={...}`에 실패 상태 코드와 `ProblemDetail`이 명시되어 있는가?
- [ ] validation 실패가 `422 ProblemDetail`로 통일되어 있는가?
- [ ] 인증 실패 `401`과 인가 실패 `403`을 구분하는가?
- [ ] unique 충돌, 상태 충돌, 중복 요청을 `409`로 반환하는가?
- [ ] rate limit 실패에 `429`를 사용하는가?
- [ ] 내부 예외 메시지, SQL, stack trace를 `detail`에 노출하지 않는가?
- [ ] 필드별 validation 에러가 필요하면 `errors` extension에 넣는가?
- [ ] 테스트에서 `application/problem+json`을 검증하는가?

### 쓰기 API

- [ ] `POST` 생성 응답은 `201`인가?
- [ ] 삭제 성공은 본문 없이 `204`인가?
- [ ] 비멱등 `POST`에 `Idempotency-Key` 또는 DB unique 제약과 `IntegrityError` 처리가 있는가?
- [ ] `transaction.atomic()` 안에서 실패 상태를 저장한 뒤 예외를 다시 raise해 rollback으로 사라지지 않는가?
- [ ] 응답 Schema가 민감 필드(`password`, hash, personal id, token 등)를 노출하지 않는가?

---

> **관련 스킬 참조:**
> - API 설계 원칙과 오류/페이지네이션 정책 → **architecture-api** 스킬
> - Django Ninja Schema/Router/response/exception_handler 구현 → **implementation-django-ninja** 스킬