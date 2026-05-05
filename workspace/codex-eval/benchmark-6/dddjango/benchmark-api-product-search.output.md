`/Users/hyun/Desktop/dddjango/none`는 파일 목록이 비어 있어 읽을 fixture가 없었습니다. read-only sandbox라 아래는 적용용 unified diff 제안입니다.

```diff
diff --git a/products/api.py b/products/api.py
new file mode 100644
--- /dev/null
+++ b/products/api.py
@@
+from decimal import Decimal
+from enum import Enum
+from typing import Annotated
+
+from django.http import HttpRequest
+from ninja import FilterSchema, Query, Router, Schema
+from ninja.filter_schema import FilterLookup
+from pydantic import Field
+
+from products.models import Product
+
+router = Router(tags=["products"])
+
+
+class ProductSort(str, Enum):
+    NEWEST = "newest"
+    PRICE_ASC = "price_asc"
+    PRICE_DESC = "price_desc"
+    NAME_ASC = "name_asc"
+
+
+SORT_ORDERING = {
+    ProductSort.NEWEST: ("-created_at", "-id"),
+    ProductSort.PRICE_ASC: ("price", "id"),
+    ProductSort.PRICE_DESC: ("-price", "-id"),
+    ProductSort.NAME_ASC: ("name", "id"),
+}
+
+
+class ProductFilter(FilterSchema):
+    q: Annotated[str | None, FilterLookup(["name__icontains", "sku__icontains"])] = None
+    category_id: int | None = None
+    brand_id: int | None = None
+    min_price: Annotated[Decimal | None, FilterLookup("price__gte")] = None
+    max_price: Annotated[Decimal | None, FilterLookup("price__lte")] = None
+    is_available: bool | None = None
+
+
+class PageQuery(Schema):
+    limit: int = Field(20, ge=1, le=100)
+    offset: int = Field(0, ge=0)
+
+
+class PageMeta(Schema):
+    total: int
+    limit: int
+    offset: int
+    has_more: bool
+
+
+class ProductOut(Schema):
+    id: int
+    name: str
+    sku: str
+    price: Decimal
+    category_id: int
+    brand_id: int | None
+    is_available: bool
+
+
+class ProductSearchPage(Schema):
+    items: list[ProductOut]
+    meta: PageMeta
+
+
+@router.get("", response={200: ProductSearchPage})
+def search_products(
+    request: HttpRequest,
+    filters: Query[ProductFilter],
+    page: Query[PageQuery],
+    sort: ProductSort = ProductSort.NEWEST,
+) -> ProductSearchPage:
+    queryset = Product.objects.all().select_related("category", "brand")
+    queryset = filters.filter(queryset).order_by(*SORT_ORDERING[sort])
+
+    total = queryset.count()
+    items = list(queryset[page.offset : page.offset + page.limit])
+
+    return ProductSearchPage(
+        items=items,
+        meta=PageMeta(
+            total=total,
+            limit=page.limit,
+            offset=page.offset,
+            has_more=page.offset + page.limit < total,
+        ),
+    )
diff --git a/config/api.py b/config/api.py
new file mode 100644
--- /dev/null
+++ b/config/api.py
@@
+from django.http import HttpRequest, JsonResponse
+from ninja import NinjaAPI, Schema
+from ninja.errors import ValidationError
+
+from products.api import router as products_router
+
+api = NinjaAPI()
+api.add_router("/products", products_router)
+
+
+class FieldError(Schema):
+    loc: list[str | int]
+    message: str
+    type: str
+
+
+class ProblemDetail(Schema):
+    type: str = "about:blank"
+    title: str
+    status: int
+    detail: str
+    instance: str
+    errors: list[FieldError] = []
+
+
+@api.exception_handler(ValidationError)
+def validation_errors(request: HttpRequest, exc: ValidationError) -> JsonResponse:
+    return JsonResponse(
+        ProblemDetail(
+            type="https://api.example.com/problems/validation-error",
+            title="Validation Error",
+            status=422,
+            detail="Query parameters or request body are invalid.",
+            instance=request.path,
+            errors=[
+                FieldError(
+                    loc=error.get("loc", []),
+                    message=error.get("msg", ""),
+                    type=error.get("type", ""),
+                )
+                for error in exc.errors
+            ],
+        ).model_dump(),
+        status=422,
+        content_type="application/problem+json",
+    )
```

**팀 컨벤션**

- URL: `GET /api/products`만 사용한다. 검색, 필터, 정렬은 전부 query parameter로 둔다.
- 필터: `FilterSchema`와 `Query[...]`를 기준으로 한다. `q`, `category_id`, `brand_id`, `min_price`, `max_price`, `is_available`만 공개한다.
- 정렬: 클라이언트 입력을 `order_by()`에 직접 넣지 않는다. `ProductSort` enum과 `SORT_ORDERING` allow-list만 통과시킨다.
- 페이지네이션: 상품 검색은 `limit/offset` envelope를 표준으로 한다. `limit` 최대값은 100, 응답은 `{items, meta}`로 고정한다.
- 에러: 모든 API 에러는 RFC 9457 Problem Details 형식으로 통일한다. validation error는 `422`와 `application/problem+json`을 사용하고, 필드별 오류는 `errors` 확장 필드에 둔다.
- 응답 타입: 커스텀 envelope를 쓰므로 `response=list[ProductOut]`를 쓰지 않는다. plain list 응답일 때만 `list[Schema]`를 쓴다.
- sync endpoint는 항상 `request: HttpRequest`와 명시적 반환 타입을 둔다.

검증은 이 환경에서 실행하지 못했습니다. 적용 후 `python manage.py check`, `pytest products/tests/test_api.py`, 그리고 `curl -i "/api/products?limit=101"`에서 `422`와 `Content-Type: application/problem+json`을 확인하세요.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬
> - API 오류/페이지네이션 설계 → **architecture-api** 스킬