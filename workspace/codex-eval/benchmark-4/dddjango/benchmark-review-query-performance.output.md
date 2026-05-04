현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 `config.toml`도 없어 실제 파일/라인 기준 리뷰는 못 했습니다. 그래서 아래는 주문 목록 API에서 보고된 N+1과 느린 pagination 증상 기준의 구조 리뷰입니다.

**주요 발견**

[Convention: 관계 로딩 전략 혼합] -- 주문 목록 응답에서 `order.customer`, `order.payment`, `order.lines`, `line.product` 같은 관계를 직렬화하면서 `Order.objects.all()` 또는 필터만 적용한 QuerySet을 반환하면 Django Ninja serialization 단계에서 N+1이 발생합니다. `select_related`와 `prefetch_related`는 용도가 다릅니다.

```python
from django.db.models import Count, Prefetch

def list_orders_queryset():
    return (
        Order.objects
        .select_related("customer", "payment")  # FK / OneToOne
        .prefetch_related(                      # reverse FK / M2M
            Prefetch(
                "lines",
                queryset=OrderLine.objects.select_related("product")
                .only("id", "order_id", "product_id", "quantity", "unit_price",
                      "product__id", "product__name"),
                to_attr="prefetched_lines",
            )
        )
        .annotate(line_count=Count("lines"))
        .order_by("-created_at", "-id")
    )
```

[API Design: 목록 응답 schema 과중] -- 주문 목록에서 상세용 중첩 schema를 재사용하면 prefetch 범위가 계속 커지고 payload도 무거워집니다. 목록은 summary schema로 제한하고, 라인/배송지/결제 상세는 `GET /orders/{id}`로 분리하는 편이 맞습니다. `ModelSchema fields="__all__"` 또는 `create_schema(depth=1+)`는 피해야 합니다.

```python
from ninja import Schema
from datetime import datetime
from decimal import Decimal

class OrderListItemSchema(Schema):
    id: int
    number: str
    status: str
    customer_name: str
    total_amount: Decimal
    line_count: int
    created_at: datetime

    @staticmethod
    def resolve_customer_name(obj):
        return obj.customer.name
```

[Pagination: offset/page-number 한계] -- 주문이 많고 `?page=5000` 또는 큰 `offset`을 허용하면 DB는 앞의 행을 계속 스캔/버립니다. 관리자성 랜덤 접근이면 offset이 가능하지만, 고객 주문 목록/운영 피드처럼 최신순 탐색이면 cursor 또는 keyset이 더 적합합니다. 정렬은 반드시 안정적이어야 하므로 `("-created_at", "-id")`처럼 tie-breaker를 둬야 합니다.

```python
from ninja import Router
from ninja.pagination import paginate, CursorPagination

router = Router()

@router.get("/orders", response=list[OrderListItemSchema])
@paginate(CursorPagination, ordering=("-created_at", "-id"), page_size=50)
def list_orders(request):
    return list_orders_queryset()
```

[DB: 인덱스가 pagination 정렬과 필터를 따라가지 못할 가능성] -- 목록 필터가 `customer_id`, `status`, `created_at` 중심이면 복합 인덱스도 그 워크로드에 맞아야 합니다. 예: 고객별 최신 주문이면 `Index(fields=["customer", "-created_at", "-id"])`, 상태별 운영 목록이면 `Index(fields=["status", "-created_at", "-id"])` 후보를 `EXPLAIN ANALYZE`로 검증하세요.

**측정/테스트**

쿼리 수 회귀 테스트를 먼저 고정하세요.

```python
@pytest.mark.django_db
def test_order_list_query_count(client, django_assert_num_queries):
    OrderFactory.create_batch(30, lines__count=3)

    with django_assert_num_queries(4):  # session/user + orders + lines + products 정도로 조정
        response = client.get("/api/orders?cursor=")

    assert response.status_code == 200
```

성능 확인은 `django-debug-toolbar`/`django-silk`로 쿼리 수와 중복 SQL을 보고, 핵심 SQL은 `QuerySet.explain(analyze=True, buffers=True)` 또는 PostgreSQL `EXPLAIN ANALYZE`로 확인하면 됩니다. 목표는 “페이지 크기 N이 커져도 쿼리 수가 상수”이고, 큰 페이지 이동에서 offset scan이 사라지는지 확인하는 것입니다.

---
> **관련 스킬 참조:**
> - Django ORM 최적화 → **implementation-django** 스킬
> - Django Ninja Schema/Router/Pagination → **implementation-django-ninja** 스킬
> - 인덱스와 EXPLAIN 검증 → **architecture-db** 스킬