지정된 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 작업 디렉터리에도 읽을 프로젝트 파일이 없습니다. 그래서 특정 코드 스타일에 맞춘 패치는 만들 수 없고, 바로 붙여 넣어 적용할 수 있는 “팀 컨벤션 문서 추가” 형태의 unified diff로 제안합니다.

```diff
diff --git a/docs/api/product-search-convention.md b/docs/api/product-search-convention.md
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/docs/api/product-search-convention.md
@@ -0,0 +1,194 @@
+# 상품 검색 API 컨벤션
+
+이 문서는 Django Ninja 기반 상품 검색 API의 필터, 정렬, 페이지네이션, 에러 응답 표준을 정의한다.
+
+## 1. 기본 원칙
+
+- 검색 API는 `GET /api/products`를 사용한다.
+- Query parameter는 snake_case를 사용한다.
+- 응답 필드는 JSON camelCase로 변환하지 않고 snake_case를 유지한다.
+- 필터 조건은 명시적으로 전달된 값만 적용한다.
+- 알 수 없는 정렬 키, 잘못된 페이지 값, 유효하지 않은 필터 값은 `400 Bad Request`로 응답한다.
+- 빈 검색 결과는 에러가 아니라 `items: []`, `total: 0`으로 응답한다.
+
+## 2. Endpoint
+
+```http
+GET /api/products
+```
+
+### Query Parameters
+
+| 이름 | 타입 | 필수 | 기본값 | 설명 |
+| --- | --- | --- | --- | --- |
+| `q` | string | no | - | 상품명, 설명, SKU 검색어 |
+| `category_id` | int | no | - | 카테고리 ID |
+| `brand_id` | int | no | - | 브랜드 ID |
+| `min_price` | decimal | no | - | 최소 가격 |
+| `max_price` | decimal | no | - | 최대 가격 |
+| `is_available` | bool | no | - | 판매 가능 여부 |
+| `sort` | string | no | `-created_at` | 정렬 조건 |
+| `page` | int | no | `1` | 페이지 번호, 1부터 시작 |
+| `page_size` | int | no | `20` | 페이지 크기 |
+
+## 3. 필터 컨벤션
+
+### 검색어
+
+- `q`는 앞뒤 공백을 제거한다.
+- 빈 문자열은 필터를 적용하지 않은 것으로 본다.
+- 검색 대상은 기본적으로 `name`, `description`, `sku`다.
+- 검색은 `icontains` 기반으로 시작하고, 별도 검색 엔진 도입 전까지 DB 검색을 표준으로 한다.
+
+```python
+if params.q:
+    keyword = params.q.strip()
+    queryset = queryset.filter(
+        Q(name__icontains=keyword)
+        | Q(description__icontains=keyword)
+        | Q(sku__icontains=keyword)
+    )
+```
+
+### 가격
+
+- `min_price`와 `max_price`는 0 이상이어야 한다.
+- `min_price > max_price`는 `400 Bad Request`로 응답한다.
+- 가격 필드는 `Decimal`로 처리한다.
+
+### Boolean
+
+- Django Ninja의 bool 파싱을 사용한다.
+- 허용 입력은 `true`, `false`, `1`, `0` 수준으로 제한한다.
+- 의미가 모호한 값은 validation error로 처리한다.
+
+## 4. 정렬 컨벤션
+
+정렬은 `sort` query parameter 하나로 처리한다.
+
+- 오름차순: `price`
+- 내림차순: `-price`
+- 기본값: `-created_at`
+- 복수 정렬은 초기 버전에서 지원하지 않는다.
+
+허용 정렬 키:
+
+| API 값 | DB 필드 | 설명 |
+| --- | --- | --- |
+| `created_at` | `created_at` | 등록일 |
+| `price` | `price` | 가격 |
+| `name` | `name` | 상품명 |
+| `popularity` | `popularity_score` | 인기 점수 |
+
+알 수 없는 정렬 키는 다음 에러로 응답한다.
+
+```json
+{
+  "error": {
+    "code": "INVALID_SORT",
+    "message": "지원하지 않는 정렬 조건입니다.",
+    "details": {
+      "field": "sort",
+      "allowed": ["created_at", "-created_at", "price", "-price", "name", "-name", "popularity", "-popularity"]
+    }
+  }
+}
+```
+
+## 5. 페이지네이션 컨벤션
+
+페이지네이션은 page 기반으로 통일한다.
+
+- `page` 기본값: `1`
+- `page_size` 기본값: `20`
+- `page_size` 최댓값: `100`
+- `page < 1`은 validation error
+- `page_size < 1` 또는 `page_size > 100`은 validation error
+
+응답 형식:
+
+```json
+{
+  "items": [
+    {
+      "id": 1,
+      "name": "상품명",
+      "price": "12000.00",
+      "is_available": true,
+      "created_at": "2026-05-05T10:00:00+09:00"
+    }
+  ],
+  "pagination": {
+    "page": 1,
+    "page_size": 20,
+    "total": 132,
+    "total_pages": 7,
+    "has_next": true,
+    "has_previous": false
+  }
+}
+```
+
+## 6. 에러 응답 표준
+
+모든 API 에러는 다음 형식을 사용한다.
+
+```json
+{
+  "error": {
+    "code": "ERROR_CODE",
+    "message": "사용자 또는 클라이언트가 이해할 수 있는 메시지",
+    "details": {}
+  }
+}
+```
+
+### 공통 에러 코드
+
+| HTTP Status | code | 설명 |
+| --- | --- | --- |
+| 400 | `VALIDATION_ERROR` | query/body validation 실패 |
+| 400 | `INVALID_FILTER` | 필터 조합이 유효하지 않음 |
+| 400 | `INVALID_SORT` | 지원하지 않는 정렬 조건 |
+| 404 | `NOT_FOUND` | 리소스 없음 |
+| 500 | `INTERNAL_SERVER_ERROR` | 서버 내부 오류 |
+
+## 7. Django Ninja 예시 구현
+
+```python
+from decimal import Decimal
+from math import ceil
+from typing import Optional
+
+from django.db.models import Q
+from ninja import Query, Router, Schema
+from ninja.errors import HttpError
+
+from products.models import Product
+
+
+router = Router(tags=["Products"])
+
+
+class ErrorBody(Schema):
+    code: str
+    message: str
+    details: dict = {}
+
+
+class ErrorResponse(Schema):
+    error: ErrorBody
+
+
+class ProductSearchQuery(Schema):
+    q: Optional[str] = None
+    category_id: Optional[int] = None
+    brand_id: Optional[int] = None
+    min_price: Optional[Decimal] = None
+    max_price: Optional[Decimal] = None
+    is_available: Optional[bool] = None
+    sort: str = "-created_at"
+    page: int = 1
+    page_size: int = 20
+
+
+class ProductOut(Schema):
+    id: int
+    name: str
+    price: Decimal
+    is_available: bool
+    created_at: str
+
+
+class PaginationOut(Schema):
+    page: int
+    page_size: int
+    total: int
+    total_pages: int
+    has_next: bool
+    has_previous: bool
+
+
+class ProductSearchResponse(Schema):
+    items: list[ProductOut]
+    pagination: PaginationOut
+
+
+SORT_FIELDS = {
+    "created_at": "created_at",
+    "price": "price",
+    "name": "name",
+    "popularity": "popularity_score",
+}
+
+
+def build_error(code: str, message: str, details: dict | None = None) -> dict:
+    return {
+        "error": {
+            "code": code,
+            "message": message,
+            "details": details or {},
+        }
+    }
+
+
+def resolve_sort(sort: str) -> str:
+    descending = sort.startswith("-")
+    sort_key = sort[1:] if descending else sort
+
+    if sort_key not in SORT_FIELDS:
+        allowed = []
+        for key in SORT_FIELDS:
+            allowed.extend([key, f"-{key}"])
+        raise HttpError(
+            400,
+            build_error(
+                "INVALID_SORT",
+                "지원하지 않는 정렬 조건입니다.",
+                {"field": "sort", "allowed": allowed},
+            ),
+        )
+
+    field_name = SORT_FIELDS[sort_key]
+    return f"-{field_name}" if descending else field_name
+
+
+def validate_search_query(params: ProductSearchQuery) -> None:
+    if params.page < 1:
+        raise HttpError(400, build_error("VALIDATION_ERROR", "page는 1 이상이어야 합니다.", {"field": "page"}))
+
+    if params.page_size < 1 or params.page_size > 100:
+        raise HttpError(
+            400,
+            build_error("VALIDATION_ERROR", "page_size는 1 이상 100 이하여야 합니다.", {"field": "page_size"}),
+        )
+
+    if params.min_price is not None and params.min_price < 0:
+        raise HttpError(400, build_error("VALIDATION_ERROR", "min_price는 0 이상이어야 합니다.", {"field": "min_price"}))
+
+    if params.max_price is not None and params.max_price < 0:
+        raise HttpError(400, build_error("VALIDATION_ERROR", "max_price는 0 이상이어야 합니다.", {"field": "max_price"}))
+
+    if (
+        params.min_price is not None
+        and params.max_price is not None
+        and params.min_price > params.max_price
+    ):
+        raise HttpError(
+            400,
+            build_error(
+                "INVALID_FILTER",
+                "min_price는 max_price보다 클 수 없습니다.",
+                {"fields": ["min_price", "max_price"]},
+            ),
+        )
+
+
+@router.get(
+    "/products",
+    response={200: ProductSearchResponse, 400: ErrorResponse},
+)
+def search_products(request, params: ProductSearchQuery = Query(...)):
+    validate_search_query(params)
+
+    queryset = Product.objects.all()
+
+    if params.q:
+        keyword = params.q.strip()
+        if keyword:
+            queryset = queryset.filter(
+                Q(name__icontains=keyword)
+                | Q(description__icontains=keyword)
+                | Q(sku__icontains=keyword)
+            )
+
+    if params.category_id is not None:
+        queryset = queryset.filter(category_id=params.category_id)
+
+    if params.brand_id is not None:
+        queryset = queryset.filter(brand_id=params.brand_id)
+
+    if params.min_price is not None:
+        queryset = queryset.filter(price__gte=params.min_price)
+
+    if params.max_price is not None:
+        queryset = queryset.filter(price__lte=params.max_price)
+
+    if params.is_available is not None:
+        queryset = queryset.filter(is_available=params.is_available)
+
+    queryset = queryset.order_by(resolve_sort(params.sort), "id")
+
+    total = queryset.count()
+    offset = (params.page - 1) * params.page_size
+    limit = offset + params.page_size
+    items = list(queryset[offset:limit])
+    total_pages = ceil(total / params.page_size) if total else 0
+
+    return {
+        "items": items,
+        "pagination": {
+            "page": params.page,
+            "page_size": params.page_size,
+            "total": total,
+            "total_pages": total_pages,
+            "has_next": params.page < total_pages,
+            "has_previous": params.page > 1,
+        },
+    }
+```
+
+## 8. 구현 시 체크리스트
+
+- `Product.objects.all()`에는 필요한 경우 `select_related("category", "brand")`를 추가한다.
+- 리스트 응답에서는 상세 설명, 대용량 이미지, 내부 관리 필드를 제외한다.
+- 정렬에는 항상 보조 정렬값 `id`를 붙여 페이지 간 순서 흔들림을 줄인다.
+- `page_size` 최대값은 서비스 트래픽과 DB 부하를 보고 조정한다.
+- 검색 대상 필드에 DB index 또는 별도 검색 인프라가 필요한지는 데이터 규모 기준으로 별도 판단한다.
```

핵심 컨벤션은 `GET /api/products`, 단일 `sort` 파라미터, page 기반 pagination, 그리고 `{ "error": { "code", "message", "details" } }` 형태의 표준 에러 응답입니다. 실제 프로젝트 파일이 없어서 모델명, 앱 경로, 인증/권한 방식은 일반적인 Django Ninja 예시로 둔 상태입니다.