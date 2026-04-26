# API Command 실행 결과

## 요청

"상품 검색 API를 만들어줘. 카테고리별 필터링, 가격 범위 검색, 키워드 검색이 가능해야 해."

---

## 1단계: 스킬 로드

**기본 스킬 (항상 적용):**
1. `skills/implementation-cleancode/SKILL.md` -- 클린 코드 원칙 (네이밍, 함수, 추상화, SOLID)
2. `skills/implementation-python/SKILL.md` -- Python 3.10+ 컨벤션 (타입 힌트, dataclasses, Pydantic v2)
3. `skills/implementation-django/SKILL.md` -- Django 5.x 프레임워크 컨벤션 (모델, QuerySet, 서비스 레이어)

**커맨드 전용 스킬:**
4. `skills/architecture-api/SKILL.md` -- REST API 설계 원칙 (URL, HTTP 메서드, 상태 코드, 페이지네이션)
5. `skills/implementation-django-ninja/SKILL.md` -- Django Ninja 구현 패턴 (Schema, Router, FilterSchema, 에러 처리)

## 2단계: TDD 여부

TDD 없이 진행한다.

## 3단계: 모드 판단

요청: "만들어줘" --> **Design** (architecture-api) + **Writing** (implementation-django-ninja)

---

## 4단계: 실행

---

### Phase 1: Design 모드 (architecture-api 스킬)

> 참조 로드: `references/rest-principles.md`, `references/url-design.md`, `references/http-methods.md`, `references/status-codes-errors.md`, `references/pagination.md`

#### 1.1 리소스 식별

| 리소스 | 설명 |
|--------|------|
| `Product` | 상품. 카테고리, 가격, 이름 등의 속성을 가짐 |
| `Category` | 상품 카테고리. 상품 필터링의 기준 |

#### 1.2 URL 구조

| 메서드 | URL | 설명 | 상태 코드 |
|--------|-----|------|-----------|
| `GET` | `/api/v1/products` | 상품 목록 조회 (필터링, 검색, 페이지네이션) | 200 |
| `GET` | `/api/v1/products/{product_id}` | 상품 상세 조회 | 200, 404 |
| `GET` | `/api/v1/categories` | 카테고리 목록 조회 | 200 |

설계 근거:
- 명사 복수형 사용 (`/products`, `/categories`) -- URL 설계 규칙
- 동사 미사용 -- 검색은 `GET /products?q=keyword` 쿼리 파라미터로 처리
- 최대 2단계 깊이 유지

#### 1.3 필터링/검색 쿼리 파라미터

```
GET /api/v1/products?q=키보드                         # 키워드 검색
GET /api/v1/products?category_id=5                    # 카테고리 필터링
GET /api/v1/products?min_price=10000&max_price=50000  # 가격 범위
GET /api/v1/products?q=키보드&category_id=5&min_price=10000&max_price=50000  # 복합
GET /api/v1/products?q=키보드&page=2                  # 페이지네이션
```

#### 1.4 요청/응답 설계

**상품 목록 응답 (200 OK):**

```json
{
  "items": [
    {
      "id": 1,
      "name": "기계식 키보드",
      "description": "체리 MX 스위치",
      "price": "89000.00",
      "category": {
        "id": 5,
        "name": "키보드"
      },
      "created_at": "2026-04-01T09:00:00Z"
    }
  ],
  "count": 42
}
```

**상품 상세 응답 (200 OK):**

```json
{
  "id": 1,
  "name": "기계식 키보드",
  "description": "체리 MX 스위치, 풀사이즈, RGB 백라이트",
  "price": "89000.00",
  "category": {
    "id": 5,
    "name": "키보드"
  },
  "stock_quantity": 150,
  "is_active": true,
  "created_at": "2026-04-01T09:00:00Z",
  "updated_at": "2026-04-05T14:30:00Z"
}
```

#### 1.5 에러 응답 설계 (RFC 9457 Problem Details)

**404 Not Found:**

```json
{
  "type": "about:blank",
  "title": "Product Not Found",
  "status": 404,
  "detail": "Product with id 999 does not exist.",
  "instance": "/api/v1/products/999"
}
```

**422 Unprocessable Entity (가격 범위 오류):**

```json
{
  "type": "about:blank",
  "title": "Invalid Price Range",
  "status": 422,
  "detail": "min_price cannot be greater than max_price.",
  "instance": "/api/v1/products"
}
```

#### 1.6 페이지네이션 전략

PageNumberPagination 선택 -- 상품 목록은 관리자와 사용자 모두 사용하며, 페이지 번호 기반 탐색이 직관적이다. 대규모 데이터셋이 예상되면 CursorPagination으로 전환을 고려한다.

---

### Phase 2: Writing 모드 (implementation-django-ninja 스킬)

> 참조 로드: `references/schema-validation.md`, `references/routing.md`, `references/input-filtering.md`, `references/response-pagination.md`, `references/error-throttling.md`

#### 2.1 Django 모델

```python
# products/models.py
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "price"]),
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self) -> str:
        return self.name
```

#### 2.2 Schema 정의

```python
# products/schemas.py
from decimal import Decimal
from datetime import datetime
from typing import Annotated

from ninja import FilterLookup, FilterSchema, Schema


class CategoryOut(Schema):
    id: int
    name: str


class ProductListOut(Schema):
    id: int
    name: str
    description: str
    price: Decimal
    category: CategoryOut
    created_at: datetime


class ProductDetailOut(Schema):
    id: int
    name: str
    description: str
    price: Decimal
    category: CategoryOut
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductFilterSchema(FilterSchema):
    q: Annotated[
        str | None,
        FilterLookup(["name__icontains", "description__icontains"]),
    ] = None
    category_id: Annotated[
        int | None,
        FilterLookup("category_id"),
    ] = None
    min_price: Annotated[
        Decimal | None,
        FilterLookup("price__gte"),
    ] = None
    max_price: Annotated[
        Decimal | None,
        FilterLookup("price__lte"),
    ] = None
```

설계 결정:
- `ProductListOut`과 `ProductDetailOut`을 분리하여 목록에서는 불필요한 필드(`stock_quantity`, `is_active`, `updated_at`)를 제외한다.
- `FilterSchema`와 `FilterLookup`을 사용하여 수동 Q 표현식 대신 타입 안전한 선언적 필터링을 구현한다.
- `q` 필드는 `name`과 `description` 두 필드를 OR 조건으로 검색한다 (FilterLookup의 리스트는 기본적으로 OR 결합).

#### 2.3 Router 및 엔드포인트

```python
# products/api.py
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.pagination import PageNumberPagination, paginate

from .models import Category, Product
from .schemas import (
    CategoryOut,
    ProductDetailOut,
    ProductFilterSchema,
    ProductListOut,
)

router = Router(tags=["products"])


@router.get("/", response=list[ProductListOut])
@paginate(PageNumberPagination, page_size=20)
def list_products(
    request,
    filters: Query[ProductFilterSchema],
) -> list[ProductListOut]:
    """상품 목록을 조회한다. 키워드 검색, 카테고리 필터링, 가격 범위 필터링을 지원한다."""
    queryset = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
    )
    return filters.filter(queryset)


@router.get("/{product_id}", response={200: ProductDetailOut, 404: None})
def get_product(request, product_id: int):
    """상품 상세 정보를 조회한다."""
    product = get_object_or_404(
        Product.objects.select_related("category"),
        id=product_id,
        is_active=True,
    )
    return product
```

설계 결정:
- `select_related("category")`로 N+1 쿼리를 방지한다.
- `is_active=True` 필터를 기본 적용하여 비활성 상품을 노출하지 않는다.
- `@paginate(PageNumberPagination, page_size=20)`으로 목록 엔드포인트에 페이지네이션을 적용한다.
- `get_object_or_404`를 사용하여 존재하지 않는 상품에 대해 404를 반환한다.

#### 2.4 카테고리 엔드포인트

```python
# products/api.py (categories 라우터 추가)

category_router = Router(tags=["categories"])


@category_router.get("/", response=list[CategoryOut])
def list_categories(request) -> list[CategoryOut]:
    """카테고리 목록을 조회한다."""
    return Category.objects.all()
```

#### 2.5 에러 처리 (RFC 9457 Problem Details)

```python
# config/api.py
from django.http import JsonResponse
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError, ValidationError

from products.api import category_router, router as products_router


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""


api = NinjaAPI(title="Product Search API", version="1.0.0")
api.add_router("/v1/products/", products_router)
api.add_router("/v1/categories/", category_router)


@api.exception_handler(HttpError)
def handle_http_error(request, exc: HttpError) -> JsonResponse:
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
def handle_validation_error(request, exc: ValidationError) -> JsonResponse:
    return JsonResponse(
        {
            "type": "about:blank",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed.",
            "instance": request.path,
            "errors": exc.errors,
        },
        status=422,
        content_type="application/problem+json",
    )


@api.exception_handler(Exception)
def handle_unexpected_error(request, exc: Exception) -> JsonResponse:
    return JsonResponse(
        ProblemDetail(
            title="Internal Server Error",
            status=500,
            detail="An unexpected error occurred.",
            instance=request.path,
        ).model_dump(),
        status=500,
        content_type="application/problem+json",
    )
```

#### 2.6 URL 설정

```python
# config/urls.py
from django.contrib import admin
from django.urls import path

from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

#### 2.7 프로젝트 구조

```
config/
    api.py            # NinjaAPI 인스턴스, 라우터 연결, 에러 핸들러
    urls.py           # api.urls 등록
    settings/
        base.py
        local.py
        production.py
products/
    __init__.py
    models.py         # Category, Product 모델
    schemas.py        # Schema, FilterSchema 정의
    api.py            # Router, 엔드포인트 정의
    admin.py
```

#### 2.8 사용 예시

```
# 키워드 검색
GET /api/v1/products/?q=키보드

# 카테고리 필터링
GET /api/v1/products/?category_id=5

# 가격 범위 검색
GET /api/v1/products/?min_price=10000&max_price=50000

# 복합 필터 + 페이지네이션
GET /api/v1/products/?q=키보드&category_id=5&min_price=10000&max_price=50000&page=2

# 상품 상세
GET /api/v1/products/1

# 카테고리 목록
GET /api/v1/categories/
```

---

> **관련 스킬 참조:**
> - 모델에 인덱스 전략이나 정규화가 필요하면 --> **architecture-db** 스킬
> - 인증/인가(JWT, API Key)를 추가하려면 --> **implementation-django-ninja** 스킬 (인증 섹션)
> - 상품 CRUD(생성/수정/삭제)를 추가하려면 --> **architecture-api** + **implementation-django-ninja** 스킬
> - 비즈니스 로직이 복잡해지면 서비스 레이어 도입 --> **implementation-django** 스킬 (서비스 레이어 섹션)
> - 테스트 작성이 필요하면 --> **implementation-tdd** 스킬
