**리뷰 결과**

Fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않고, 현재 워크스페이스도 비어 있어 실제 파일/라인 기준 리뷰는 할 수 없었습니다. 아래는 주문 목록 API에서 N+1과 느린 pagination이 있다는 전제의 적용 가능한 review findings입니다.

1. **[Convention: QuerySet 최적화] -- `select_related`와 `prefetch_related` 책임이 섞이면 N+1이 남습니다.**  
   `Order -> customer`, `Order -> payment`, `Order -> shipping_address`처럼 FK/O2O 단일 객체는 `select_related()`로 JOIN해야 합니다. 반대로 `Order -> lines`, `lines -> product`처럼 reverse FK/M2M 컬렉션은 `prefetch_related()` 또는 `Prefetch()`가 맞습니다. `select_related`는 pagination을 빠르게 만들지 않고, `prefetch_related`도 큰 offset scan을 해결하지 않습니다. 둘은 N+1 제거용이고 pagination 전략과 별개입니다.

2. **[API Pagination] -- 대용량 주문 목록에 offset/page-number pagination은 뒤 페이지로 갈수록 느려집니다.**  
   주문 목록은 보통 `created_at desc, id desc` 정렬이 안정적이므로 cursor/keyset pagination을 우선 검토해야 합니다. offset은 관리자 소규모 목록에는 단순하지만, 운영 주문 테이블에서는 `OFFSET n`만큼 건너뛰는 비용과 삽입/삭제 중복 문제가 생깁니다.

3. **[Schema 설계] -- 목록 응답 schema가 주문 상세 수준으로 중첩되면 serializer 단계에서 다시 N+1이 발생합니다.**  
   목록에서는 `customer_name`, `line_count`, `total_amount`, `status`, `created_at` 정도의 평평한 `OrderListItemSchema`를 권장합니다. `customer.addresses`, `lines.product.options`, `payment.transactions` 같은 깊은 중첩은 상세 API로 분리해야 합니다.

**권장 형태**

```python
from django.http import HttpRequest
from django.db.models import Count, Prefetch, QuerySet
from ninja import Router, Schema
from ninja.pagination import CursorPagination, paginate

from orders.models import Order, OrderLine

router = Router()


class OrderLineSummarySchema(Schema):
    id: int
    product_name: str
    quantity: int


class OrderListItemSchema(Schema):
    id: int
    order_number: str
    customer_name: str
    status: str
    total_amount: int
    line_count: int
    created_at: str


def get_order_list_queryset() -> QuerySet[Order]:
    lines = OrderLine.objects.select_related("product").only(
        "id",
        "order_id",
        "product__name",
        "quantity",
    )

    return (
        Order.objects.select_related("customer")
        .prefetch_related(Prefetch("lines", queryset=lines))
        .annotate(line_count=Count("lines"))
        .only(
            "id",
            "order_number",
            "customer__name",
            "status",
            "total_amount",
            "created_at",
        )
        .order_by("-created_at", "-id")
    )


@router.get("/orders", response=list[OrderListItemSchema])
@paginate(CursorPagination, ordering=("-created_at", "-id"), page_size=50)
def list_orders(request: HttpRequest) -> QuerySet[Order]:
    return get_order_list_queryset()
```

DB 인덱스는 실제 `WHERE` 조건에 맞춰 정해야 하지만, 기본 목록이 최신순이면 최소한 다음 계열을 측정 후보로 봅니다.

```python
models.Index(fields=["-created_at", "-id"], name="idx_orders_created_id")
```

상태/고객 필터가 항상 같이 붙는다면 `status, -created_at, -id` 또는 `customer_id, -created_at, -id`처럼 등호 조건 컬럼을 앞에 둔 복합 인덱스를 `EXPLAIN ANALYZE`로 검증하세요.

**검증 방법**

```python
def test_order_list_query_count(django_assert_num_queries, client):
    with django_assert_num_queries(3):
        response = client.get("/api/orders?limit=50")
    assert response.status_code == 200
```

기준 쿼리 수는 보통 `orders + prefetched lines + count/extra pagination query` 수준으로 고정해야 합니다. 추가로 PostgreSQL에서 실제 목록 SQL에 `EXPLAIN (ANALYZE, BUFFERS)`를 실행해 `Seq Scan`, 큰 `Rows Removed`, 높은 buffer read가 사라졌는지 확인하세요.

---
> **관련 스킬 참조:**
> - Django ORM N+1 최적화 → **implementation-django** 스킬
> - Django Ninja Schema/Router/Pagination → **implementation-django-ninja** 스킬
> - cursor/keyset pagination과 인덱스 검증 → **architecture-api**, **architecture-db** 스킬