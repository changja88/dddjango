# 상품 목록 API (Django Ninja - FilterSchema + CursorPagination)

## models.py

```python
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    class Meta:
        ordering = ["-created_at"]

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categories = models.ManyToManyField(Category, related_name="products", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
```

## schemas.py

```python
from typing import Annotated, List, Optional

from ninja import FilterLookup, FilterSchema, ModelSchema, Schema

from .models import Product


class CategorySchema(Schema):
    id: int
    name: str


class ProductSchema(ModelSchema):
    categories: List[CategorySchema]

    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "created_at"]


class ProductFilterSchema(FilterSchema):
    search: Annotated[
        Optional[str],
        FilterLookup("name__icontains"),
    ] = None
    category_ids: Optional[List[int]] = None
    min_price: Annotated[
        Optional[float],
        FilterLookup("price__gte"),
    ] = None
    max_price: Annotated[
        Optional[float],
        FilterLookup("price__lte"),
    ] = None
    in_stock: Optional[bool] = None

    def filter_category_ids(self, value: List[int]) -> Q:
        return Q(categories__id__in=value)

    def filter_in_stock(self, value: bool) -> Q:
        if value:
            return Q(stock__gt=0)
        return Q(stock=0)
```

## api.py

```python
from typing import List

from django.db.models import Q
from ninja import Query, Router
from ninja.pagination import CursorPagination, paginate

from .models import Product
from .schemas import ProductFilterSchema, ProductSchema

router = Router(tags=["products"])

ORDERING_FIELDS: dict[str, tuple[str, ...]] = {
    "price_asc": ("price", "pk"),
    "price_desc": ("-price", "-pk"),
    "name_asc": ("name", "pk"),
    "name_desc": ("-name", "-pk"),
    "latest": ("-created_at", "-pk"),
    "oldest": ("created_at", "pk"),
}
DEFAULT_ORDERING = "latest"


@router.get("/", response=List[ProductSchema])
@paginate(CursorPagination, page_size=20, max_page_size=100)
def list_products(
    request,
    filters: Query[ProductFilterSchema],
    ordering: str = DEFAULT_ORDERING,
) -> List[Product]:
    qs = Product.objects.prefetch_related("categories").all()
    qs = filters.filter(qs)

    order_fields = ORDERING_FIELDS.get(ordering, ORDERING_FIELDS[DEFAULT_ORDERING])
    qs = qs.order_by(*order_fields)

    return qs
```

## urls.py (앱 레벨)

```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI()
api.add_router("/products", products_router)
```

---

## 설계 요약

| 요구사항 | 구현 |
|---------|------|
| 카테고리 필터 (다중 선택) | `category_ids: Optional[List[int]]` + `filter_category_ids` 커스텀 메서드 (`categories__id__in`) |
| 가격 범위 필터 | `min_price` / `max_price` + `FilterLookup("price__gte")`, `FilterLookup("price__lte")` |
| 이름 검색 (부분 일치) | `search` + `FilterLookup("name__icontains")` |
| 재고 유무 필터 | `in_stock: Optional[bool]` + `filter_in_stock` 커스텀 메서드 (`stock__gt=0` / `stock=0`) |
| 정렬 | `ordering` 쿼리 파라미터 + `ORDERING_FIELDS` 화이트리스트 매핑 |
| 커서 기반 페이지네이션 | `@paginate(CursorPagination, page_size=20, max_page_size=100)` |

## 요청 예시

```
GET /api/products/?category_ids=1&category_ids=3&min_price=10000&max_price=50000&search=셔츠&in_stock=true&ordering=price_asc
```

## 응답 형식

```json
{
  "next": "http://api.example.com/api/products/?cursor=eyJwIjpbMTAwMDAsNV0sInIiOmZhbHNlLCJvIjowfQ==",
  "previous": null,
  "results": [
    {
      "id": 5,
      "name": "린넨 셔츠",
      "price": 29000.00,
      "stock": 42,
      "created_at": "2026-03-15T09:30:00Z",
      "categories": [
        {"id": 1, "name": "상의"},
        {"id": 3, "name": "여름"}
      ]
    }
  ]
}
```

## 주요 설계 결정

**FilterSchema 사용**: `FilterSchema`를 사용해 필터 파라미터를 선언적으로 정의했다. `None` 값의 필터는 기본 동작(`ignore_none=True`)에 의해 자동 무시되므로, 클라이언트는 필요한 필터만 전달하면 된다.

**커스텀 필터 메서드**: `category_ids`와 `in_stock`은 단순한 `FilterLookup`으로 표현할 수 없으므로 `filter_<field>` 메서드를 사용했다. `category_ids`는 `__in` 조회, `in_stock`은 `stock > 0` 여부로 분기하는 로직이 필요하다.

**정렬 화이트리스트**: 임의의 필드명을 `order_by`에 직접 전달하면 보안 위험이 있다. `ORDERING_FIELDS` 딕셔너리로 허용된 정렬 옵션만 매핑하고, 각 옵션에 보조 정렬 키(`pk`)를 추가하여 커서 페이지네이션의 안정성을 보장했다.

**CursorPagination**: 커서 페이지네이션은 정렬 필드의 일관성이 필요하다. `ordering` 파라미터에 따라 `order_by`가 동적으로 바뀌므로, 각 정렬 옵션에 `pk`를 보조 키로 포함하여 동일 값 행에서도 커서가 안정적으로 동작하도록 했다.
