# Product CRUD API 설계 및 구현

## 1. API 설계 (architecture-api)

### 리소스 및 URL 구조

| 엔드포인트 | 메서드 | 설명 | 상태 코드 |
|-----------|--------|------|----------|
| `/api/v1/products` | GET | 상품 목록 조회 (필터링 + 페이지네이션) | 200 |
| `/api/v1/products` | POST | 상품 생성 | 201 |
| `/api/v1/products/{product_id}` | GET | 상품 상세 조회 | 200, 404 |
| `/api/v1/products/{product_id}` | PUT | 상품 전체 수정 | 200, 404 |
| `/api/v1/products/{product_id}` | PATCH | 상품 부분 수정 | 200, 404 |
| `/api/v1/products/{product_id}` | DELETE | 상품 삭제 | 204, 404 |

### 필터링 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `category` | string | 카테고리 정확히 일치 |
| `search` | string | 상품명/설명 부분 일치 검색 |
| `min_price` | decimal | 최소 가격 |
| `max_price` | decimal | 최대 가격 |

### 페이지네이션

Offset 방식 사용 (관리자 대시보드/일반 목록에 적합).

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `limit` | int | 20 | 페이지당 항목 수 |
| `offset` | int | 0 | 시작 위치 |

### 에러 형식

모든 에러는 RFC 9457 Problem Details 형식을 따른다.

```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Product with id 999 does not exist.",
  "instance": "/api/v1/products/999"
}
```

---

## 2. Django Model (implementation-django)

```python
# products/models.py

from decimal import Decimal

from django.db import models


class TimeStampedModel(models.Model):
    """공통 타임스탬프 필드를 제공하는 추상 베이스 클래스."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(models.Model):
    """상품 카테고리."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    """판매 상품 정보."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.DRAFT,
    )
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=Decimal("0")),
                name="product_price_non_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["category", "status"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.name
```

---

## 3. Django Ninja API 구현 (implementation-django-ninja)

### 3-1. Schema 정의

```python
# products/schemas.py

from decimal import Decimal
from typing import Annotated

from ninja import FilterLookup, FilterSchema, ModelSchema, PatchDict, Schema

from .models import Category, Product


# --- Category Schemas ---

class CategoryOut(ModelSchema):
    """카테고리 응답 스키마."""

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


# --- Product Schemas ---

class ProductIn(Schema):
    """상품 생성 요청 스키마."""

    name: str
    slug: str
    description: str = ""
    price: Decimal
    category_id: int
    status: str = Product.Status.DRAFT
    stock: int = 0


class ProductOut(Schema):
    """상품 응답 스키마."""

    id: int
    name: str
    slug: str
    description: str
    price: Decimal
    category: CategoryOut
    status: str
    stock: int
    created_at: str
    updated_at: str

    @staticmethod
    def resolve_created_at(obj) -> str:
        return obj.created_at.isoformat()

    @staticmethod
    def resolve_updated_at(obj) -> str:
        return obj.updated_at.isoformat()


class ProductUpdate(Schema):
    """상품 전체 수정 요청 스키마."""

    name: str
    slug: str
    description: str
    price: Decimal
    category_id: int
    status: str
    stock: int


class ProductPatch(Schema):
    """상품 부분 수정 요청 스키마 (PatchDict와 함께 사용)."""

    name: str
    slug: str
    description: str
    price: Decimal
    category_id: int
    status: str
    stock: int


# --- Filter Schema ---

class ProductFilterSchema(FilterSchema):
    """상품 목록 필터링 스키마."""

    category: Annotated[
        str | None,
        FilterLookup("category__slug"),
    ] = None
    search: Annotated[
        str | None,
        FilterLookup(["name__icontains", "description__icontains"]),
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

### 3-2. Router 및 엔드포인트

```python
# products/api.py

from django.shortcuts import get_object_or_404
from ninja import PatchDict, Query, Router
from ninja.pagination import LimitOffsetPagination, paginate

from .models import Product
from .schemas import (
    ProductFilterSchema,
    ProductIn,
    ProductOut,
    ProductPatch,
    ProductUpdate,
)

router = Router(tags=["products"])


@router.get("/", response=list[ProductOut])
@paginate(LimitOffsetPagination, page_size=20)
def list_products(request, filters: Query[ProductFilterSchema]):
    """상품 목록을 필터링하여 페이지네이션된 결과를 반환한다."""
    queryset = Product.objects.select_related("category").all()
    return filters.filter(queryset)


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductIn):
    """새 상품을 생성한다."""
    product = Product.objects.create(**payload.dict())
    product = Product.objects.select_related("category").get(pk=product.pk)
    return 201, product


@router.get("/{int:product_id}", response=ProductOut)
def get_product(request, product_id: int):
    """상품 상세 정보를 반환한다."""
    return get_object_or_404(
        Product.objects.select_related("category"),
        pk=product_id,
    )


@router.put("/{int:product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: ProductUpdate):
    """상품 정보를 전체 교체한다."""
    product = get_object_or_404(Product, pk=product_id)
    for attr, value in payload.dict().items():
        setattr(product, attr, value)
    product.save()
    product = Product.objects.select_related("category").get(pk=product.pk)
    return product


@router.patch("/{int:product_id}", response=ProductOut)
def patch_product(request, product_id: int, payload: PatchDict[ProductPatch]):
    """상품 정보를 부분 수정한다."""
    product = get_object_or_404(Product, pk=product_id)
    for attr, value in payload.items():
        setattr(product, attr, value)
    product.save(update_fields=list(payload.keys()))
    product = Product.objects.select_related("category").get(pk=product.pk)
    return product


@router.delete("/{int:product_id}", response={204: None})
def delete_product(request, product_id: int):
    """상품을 삭제한다."""
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return 204, None
```

### 3-3. 메인 API 설정 및 에러 처리

```python
# config/api.py

from django.http import JsonResponse
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError, ValidationError

from products.api import router as products_router


api = NinjaAPI(
    title="Product API",
    version="1.0.0",
)

api.add_router("/v1/products", products_router)


# --- RFC 9457 Problem Details 에러 처리 ---

class ProblemDetail(Schema):
    """RFC 9457 Problem Details 응답 스키마."""

    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""


@api.exception_handler(HttpError)
def handle_http_error(request, exc: HttpError):
    """HttpError를 RFC 9457 형식으로 반환한다."""
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
def handle_validation_error(request, exc: ValidationError):
    """검증 에러를 RFC 9457 형식으로 반환한다."""
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
def handle_unexpected_error(request, exc: Exception):
    """예상치 못한 에러를 RFC 9457 형식으로 반환한다."""
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

### 3-4. URL 설정

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

---

## 4. 프로젝트 구조

```
config/
    __init__.py
    settings/
        base.py
        local.py
        production.py
        test.py
    api.py              # NinjaAPI 인스턴스, 라우터 연결, 에러 핸들러
    urls.py
products/
    __init__.py
    models.py           # Category, Product 모델
    schemas.py          # Schema, FilterSchema 정의
    api.py              # Router, 엔드포인트 정의
    admin.py
    migrations/
```

---

## 5. API 사용 예시

### 상품 목록 조회 (필터링 + 페이지네이션)

```
GET /api/v1/products?category=electronics&min_price=100&limit=20&offset=0
```

```json
{
  "items": [
    {
      "id": 1,
      "name": "Wireless Keyboard",
      "slug": "wireless-keyboard",
      "description": "Bluetooth wireless keyboard",
      "price": "49.99",
      "category": {
        "id": 1,
        "name": "Electronics",
        "slug": "electronics"
      },
      "status": "active",
      "stock": 150,
      "created_at": "2026-04-05T10:00:00+00:00",
      "updated_at": "2026-04-05T10:00:00+00:00"
    }
  ],
  "count": 45
}
```

### 상품 검색

```
GET /api/v1/products?search=keyboard&max_price=100
```

### 상품 생성

```
POST /api/v1/products
Content-Type: application/json

{
  "name": "Wireless Mouse",
  "slug": "wireless-mouse",
  "description": "Ergonomic wireless mouse",
  "price": "29.99",
  "category_id": 1,
  "status": "active",
  "stock": 200
}
```

### 상품 부분 수정

```
PATCH /api/v1/products/1
Content-Type: application/json

{
  "price": "39.99",
  "stock": 100
}
```

### 상품 삭제

```
DELETE /api/v1/products/1
```

응답: `204 No Content`

---

## 6. 설계 결정 요약

| 결정 | 근거 |
|------|------|
| URL에 복수 명사 `/products` 사용 | REST URL 설계 규칙: 컬렉션은 복수 명사 |
| POST 201, DELETE 204 | HTTP 상태 코드 표준: 생성은 201, 삭제는 204 |
| RFC 9457 에러 형식 | 모든 API 에러에 일관된 Problem Details 형식 적용 |
| LimitOffsetPagination | 일반 목록/관리 대시보드에 적합한 단순한 페이지네이션 |
| FilterSchema + FilterLookup | 타입 안전한 필터링, Django Q 표현식 자동 변환 |
| PatchDict 사용 | PATCH 작업에서 전달된 필드만 수정, 명확한 의도 전달 |
| select_related("category") | FK 조회 시 N+1 쿼리 방지 |
| save(update_fields=...) | PATCH에서 변경된 필드만 업데이트하여 성능 최적화 |
| PROTECT on_delete | 카테고리 삭제 시 연결된 상품이 있으면 삭제 방지 |
| CheckConstraint for price | DB 레벨에서 가격이 음수가 되지 않도록 이중 방어 |
| TextChoices for status | 불리언 플래그 대신 열거형으로 상태를 명확하게 표현 |

---

> **관련 스킬 참조:**
> - [모델 테스트, API 테스트] --> **implementation-tdd** 스킬
> - [데이터베이스 인덱스 최적화, 정규화] --> **architecture-db** 스킬
> - [인증/인가 추가] --> **implementation-django-ninja** 스킬 (authentication 참조)
> - [서비스 레이어 분리] --> **implementation-django** 스킬 (service-layer 참조)
> - [헥사고날 아키텍처, CQRS] --> **architecture-implementation-patterns** 스킬
